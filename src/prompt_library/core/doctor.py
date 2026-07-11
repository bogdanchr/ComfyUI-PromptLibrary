from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from shutil import copy2
from typing import Iterable, List

from ..storage import clear_prompt_cache, read_raw_lines
from .constants import NEGATIVE_FILENAMES, STYLE_FILENAMES
from .library import PromptLibraryRepository
from .quality import PromptQualityDoctor
from .text import has_invalid_weight, parse_weighted_line, section_label


@dataclass(frozen=True)
class DoctorIssue:
    kind: str
    severity: str
    message: str
    path: Path | None = None
    line: int | None = None
    fixable: bool = False


@dataclass
class DoctorResult:
    report: str
    status: str
    total_entries: int
    issues: List[DoctorIssue] = field(default_factory=list)
    fixed_files: int = 0
    backup_folder: Path | None = None

    @property
    def is_healthy(self) -> bool:
        return not any(issue.severity == "ERROR" for issue in self.issues)

    @property
    def issues_count(self) -> int:
        return len(self.issues)


class PromptDoctor:
    """Diagnose a prompt library and perform conservative, reversible fixes."""

    SAFE_ACTIONS = {
        "diagnose",
        "fix_duplicates_blank_lines",
        "create_missing_files",
        "fix_all_safe",
        "quality_check",
        "full_diagnosis",
    }

    def __init__(self, root_folder):
        self.repository = PromptLibraryRepository(root_folder)

    def _categories(self, category: str) -> list[str]:
        category = (category or "ALL").strip() or "ALL"
        return self.repository.categories() if category == "ALL" else [category]

    @staticmethod
    def _active_key(line: str) -> str | None:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            return None
        text, _weight = parse_weighted_line(stripped)
        return text.casefold().strip() if text else None

    def diagnose(self, category: str = "ALL") -> DoctorResult:
        root = self.repository.root
        scope = (category or "ALL").strip() or "ALL"
        issues: list[DoctorIssue] = []
        total_entries = 0
        lines = [
            "PROMPT DOCTOR 0.4",
            "════════════════════════",
            f"Library: {root}",
            f"Scope: {scope}",
            "",
        ]

        if not root.is_dir():
            issue = DoctorIssue("missing_root", "ERROR", f"Root folder not found: {root}")
            return DoctorResult("\n".join(lines + [f"✗ {issue.message}"]), "ERROR", 0, [issue])

        categories = self._categories(scope)
        if not categories:
            issue = DoctorIssue("no_categories", "ERROR", "No category folders found.")
            return DoctorResult("\n".join(lines + [f"✗ {issue.message}"]), "ERROR", 0, [issue])

        for name in categories:
            info = self.repository.category(name)
            lines.extend([f"[{name}]", "────────────────────────"])
            if not info.path.is_dir():
                issue = DoctorIssue("missing_category", "ERROR", "Category folder not found.", info.path)
                issues.append(issue)
                lines.extend([f"✗ {issue.message}", ""])
                continue

            lines.append(f"{'✓' if info.prompt_files else '✗'} Prompt files: {len(info.prompt_files)}")
            if not info.prompt_files:
                issues.append(DoctorIssue("no_prompt_files", "ERROR", "No prompt TXT files.", info.path))

            if info.style_file:
                lines.append("✓ style.txt")
            else:
                issues.append(DoctorIssue("missing_style", "WARNING", "Missing style.txt.", info.path / "style.txt", fixable=True))
                lines.append("⚠ style.txt missing")

            if info.negative_file:
                lines.append("✓ negative.txt")
            else:
                issues.append(DoctorIssue("missing_negative", "WARNING", "Missing negative.txt.", info.path / "negative.txt", fixable=True))
                lines.append("⚠ negative.txt missing")

            category_entries = 0
            for path in info.prompt_files:
                try:
                    raw_lines = read_raw_lines(path, reload_cache=True)
                except OSError as exc:
                    issues.append(DoctorIssue("read_error", "ERROR", str(exc), path))
                    lines.append(f"  {section_label(path.name)}: ✗ {exc}")
                    continue

                seen: set[str] = set()
                entries = duplicates = blanks = invalid_weights = 0
                for line_no, raw in enumerate(raw_lines, start=1):
                    stripped = raw.strip()
                    if not stripped:
                        blanks += 1
                        issues.append(DoctorIssue("blank_line", "WARNING", "Blank line.", path, line_no, True))
                        continue
                    if stripped.startswith("#"):
                        continue
                    entries += 1
                    key = self._active_key(raw)
                    if key in seen:
                        duplicates += 1
                        issues.append(DoctorIssue("duplicate", "WARNING", "Duplicate prompt entry.", path, line_no, True))
                    elif key:
                        seen.add(key)
                    if has_invalid_weight(stripped):
                        invalid_weights += 1
                        issues.append(DoctorIssue("invalid_weight", "WARNING", "Invalid weight syntax; manual review required.", path, line_no, False))

                category_entries += entries
                marks = []
                if duplicates:
                    marks.append(f"{duplicates} duplicate(s)")
                if blanks:
                    marks.append(f"{blanks} blank line(s)")
                if invalid_weights:
                    marks.append(f"{invalid_weights} invalid weight(s)")
                if not entries:
                    issues.append(DoctorIssue("empty_file", "ERROR", "File has no active prompt entries.", path))
                    marks.append("EMPTY FILE")
                suffix = f" — ⚠ {', '.join(marks)}" if marks else " — ✓"
                lines.append(f"  {section_label(path.name)}: {entries} entries{suffix}")

            total_entries += category_entries
            lines.extend([f"Entries: {category_entries}", ""])

        errors = sum(issue.severity == "ERROR" for issue in issues)
        warnings = sum(issue.severity == "WARNING" for issue in issues)
        fixable = sum(issue.fixable for issue in issues)
        status = "ERROR" if errors else "WARNING" if warnings else "OK"
        lines.extend([
            "DIAGNOSIS",
            "════════════════════════",
            f"Status: {status}",
            f"Total entries: {total_entries}",
            f"Issues: {len(issues)}",
            f"Safe fixes available: {fixable}",
            "",
        ])
        if issues:
            lines.append("SUGGESTED ACTION")
            lines.append("────────────────────────")
            if any(i.kind in {"duplicate", "blank_line"} for i in issues):
                lines.append("• fix_duplicates_blank_lines")
            if any(i.kind in {"missing_style", "missing_negative"} for i in issues):
                lines.append("• create_missing_files")
            if any(i.kind == "invalid_weight" for i in issues):
                lines.append("• Invalid weights are not changed automatically.")
        else:
            lines.append("✓ Library is healthy. No action required.")

        return DoctorResult("\n".join(lines), status, total_entries, issues)

    def _backup(self, paths: Iterable[Path]) -> Path | None:
        unique_paths = sorted({p.resolve() for p in paths if p.exists() and p.is_file()})
        if not unique_paths:
            return None
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_root = self.repository.root / ".promptlibrary_backups" / stamp
        for source in unique_paths:
            try:
                relative = source.relative_to(self.repository.root)
            except ValueError:
                relative = Path(source.name)
            target = backup_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            copy2(source, target)
        return backup_root

    @staticmethod
    def _clean_file(path: Path) -> bool:
        raw_lines = read_raw_lines(path, reload_cache=True)
        output: list[str] = []
        seen: set[str] = set()
        changed = False
        for raw in raw_lines:
            stripped = raw.strip()
            if not stripped:
                changed = True
                continue
            if stripped.startswith("#"):
                output.append(raw)
                continue
            key = PromptDoctor._active_key(raw)
            if key and key in seen:
                changed = True
                continue
            if key:
                seen.add(key)
            output.append(raw)
        if changed:
            path.write_text("\n".join(output).rstrip() + "\n", encoding="utf-8")
            clear_prompt_cache(path)
        return changed

    def repair(self, category: str, action: str) -> DoctorResult:
        action = action if action in self.SAFE_ACTIONS else "diagnose"
        if action == "quality_check":
            quality = PromptQualityDoctor(self.repository.root).analyze(category)
            return DoctorResult(quality.report, quality.status, 0, [
                DoctorIssue(i.kind, i.severity, i.message, i.path, i.line, False) for i in quality.issues
            ])
        if action == "full_diagnosis":
            technical = self.diagnose(category)
            quality = PromptQualityDoctor(self.repository.root).analyze(category)
            combined = technical.report + "\n\n" + quality.report
            combined_issues = technical.issues + [
                DoctorIssue(i.kind, i.severity, i.message, i.path, i.line, False) for i in quality.issues
            ]
            status = "ERROR" if any(i.severity == "ERROR" for i in combined_issues) else quality.status
            return DoctorResult(combined, status, technical.total_entries, combined_issues)
        before = self.diagnose(category)
        if action == "diagnose":
            return before

        clean_paths = {
            issue.path for issue in before.issues
            if issue.path and issue.kind in {"duplicate", "blank_line"}
        }
        create_paths = {
            issue.path for issue in before.issues
            if issue.path and issue.kind in {"missing_style", "missing_negative"}
        }
        touched_existing = clean_paths if action in {"fix_duplicates_blank_lines", "fix_all_safe"} else set()
        backup = self._backup(touched_existing)
        fixed_files = 0

        if action in {"fix_duplicates_blank_lines", "fix_all_safe"}:
            for path in sorted(clean_paths):
                fixed_files += int(self._clean_file(path))

        if action in {"create_missing_files", "fix_all_safe"}:
            for path in sorted(create_paths):
                if path.exists():
                    continue
                path.parent.mkdir(parents=True, exist_ok=True)
                label = "style" if path.name.casefold() in STYLE_FILENAMES else "negative"
                path.write_text(
                    f"# PromptLibrary {label} file\n"
                    "# Add one active entry per line below this comment.\n",
                    encoding="utf-8",
                )
                fixed_files += 1
                clear_prompt_cache(path)

        after = self.diagnose(category)
        header = [
            "PROMPT DOCTOR — REPAIR COMPLETE",
            "════════════════════════",
            f"Action: {action}",
            f"Changed/created files: {fixed_files}",
            f"Backup: {backup if backup else 'not required'}",
            "",
        ]
        after.report = "\n".join(header) + after.report
        after.fixed_files = fixed_files
        after.backup_folder = backup
        return after
