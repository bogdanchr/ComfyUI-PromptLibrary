from collections import Counter
from pathlib import Path

from ..models import ValidationSummary
from ..storage import read_raw_lines
from .library import PromptLibraryRepository
from .text import has_invalid_weight, parse_weighted_line, section_label

class LibraryValidator:
    def __init__(self, root_folder):
        self.repository = PromptLibraryRepository(root_folder)

    @staticmethod
    def _analyse(path):
        try:
            raw_lines = read_raw_lines(path, reload_cache=True)
        except OSError as exc:
            return {"active": 0, "blank": 0, "comments": 0, "duplicates": 0, "invalid_weights": 0, "empty": True, "read_error": str(exc)}
        active, blank, comments, invalid = [], 0, 0, 0
        for raw in raw_lines:
            stripped = raw.strip()
            if not stripped:
                blank += 1
            elif stripped.startswith("#"):
                comments += 1
            else:
                active.append(stripped)
                invalid += int(has_invalid_weight(stripped))
        normalized = [parse_weighted_line(line)[0].casefold().strip() for line in active]
        counts = Counter(normalized)
        duplicates = sum(value - 1 for value in counts.values() if value > 1)
        return {"active": len(active), "blank": blank, "comments": comments, "duplicates": duplicates, "invalid_weights": invalid, "empty": not active, "read_error": None}

    def validate(self, category="ALL"):
        category = (category or "ALL").strip() or "ALL"
        root = self.repository.root
        if not root.is_dir():
            return ValidationSummary(f"ERROR: root folder not found:\n{root}", "ERROR", 0, 0, 1)
        categories = self.repository.categories() if category == "ALL" else [category]
        lines = ["PROMPT LIBRARY VALIDATOR 0.1", "════════════════════════", f"Root: {root}", f"Scope: {category}", ""]
        entries = warnings = errors = 0
        if not categories:
            return ValidationSummary("\n".join(lines + ["ERROR: no category folders found."]), "ERROR", 0, 0, 1)
        for name in categories:
            info = self.repository.category(name)
            lines.extend([f"[{name}]", "────────────────────────"])
            if not info.path.is_dir():
                lines.extend(["✗ Category folder not found.", ""]); errors += 1; continue
            lines.append(f"{'✓' if info.prompt_files else '✗'} Prompt files: {len(info.prompt_files)}")
            lines.append(f"{'✓' if info.style_file else '⚠'} style.txt: {'present' if info.style_file else 'missing'}")
            lines.append(f"{'✓' if info.negative_file else '⚠'} negative.txt: {'present' if info.negative_file else 'missing'}")
            errors += int(not info.prompt_files)
            warnings += int(not info.style_file) + int(not info.negative_file)
            stats_total = {"active": 0, "duplicates": 0, "blank": 0, "invalid_weights": 0, "empty": 0}
            for path in info.prompt_files:
                stats = self._analyse(path)
                if stats["read_error"]:
                    lines.append(f"  {section_label(path.name)}: ✗ {stats['read_error']}"); errors += 1; continue
                for key in ("active", "duplicates", "blank", "invalid_weights"):
                    stats_total[key] += stats[key]
                stats_total["empty"] += int(stats["empty"])
                marks = []
                if stats["duplicates"]: marks.append(f"{stats['duplicates']} duplicates")
                if stats["blank"]: marks.append(f"{stats['blank']} blank")
                if stats["invalid_weights"]: marks.append(f"{stats['invalid_weights']} invalid weights")
                if stats["empty"]: marks.append("EMPTY FILE")
                suffix = f" — ⚠ {', '.join(marks)}" if marks else ""
                lines.append(f"  {section_label(path.name)}: {stats['active']} entries{suffix}")
            entries += stats_total["active"]
            category_warnings = stats_total["duplicates"] + stats_total["blank"] + stats_total["invalid_weights"] + stats_total["empty"]
            warnings += category_warnings
            lines.extend(["", f"Entries: {stats_total['active']}", f"Duplicates: {stats_total['duplicates']}", f"Blank lines: {stats_total['blank']}", f"Invalid weights: {stats_total['invalid_weights']}", f"Empty files: {stats_total['empty']}", ""])
        status = "ERROR" if errors else "WARNING" if warnings else "OK"
        lines.extend(["SUMMARY", "════════════════════════", f"Status: {status}", f"Total entries: {entries}", f"Warnings: {warnings}", f"Errors: {errors}"])
        return ValidationSummary("\n".join(lines), status, entries, warnings, errors)
