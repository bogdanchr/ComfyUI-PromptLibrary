from __future__ import annotations

from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from statistics import median
import re
from typing import Iterable

from ..storage import read_raw_lines
from .constants import NEGATIVE_FILENAMES, STYLE_FILENAMES
from .library import PromptLibraryRepository
from .text import parse_weighted_line, section_label


@dataclass(frozen=True)
class QualityIssue:
    kind: str
    severity: str
    message: str
    path: Path | None = None
    line: int | None = None
    suggestion: str | None = None


@dataclass
class QualityResult:
    report: str
    score: int
    status: str
    issues: list[QualityIssue] = field(default_factory=list)
    suggestions_count: int = 0

    @property
    def is_healthy(self) -> bool:
        return self.score >= 80 and not any(i.severity == "ERROR" for i in self.issues)

    @property
    def issues_count(self) -> int:
        return len(self.issues)


class PromptQualityDoctor:
    """Conservative, local quality checks. Never modifies user files."""

    ROLE_HINTS = {
        "character": {"max_words": 2, "forbidden_prefixes": ("wearing ", "holding ", "standing ", "walking ", "running ")},
        "typ_postaci": {"forbidden_prefixes": ("wearing ", "holding ", "standing ", "walking ")},
        "stroj": {"preferred_prefixes": ("wearing ",)},
        "rekwizyt": {"preferred_prefixes": ("holding ", "standing next to ", "standing beside ", "wearing ")},
        "tlo": {"forbidden_prefixes": ("holding ", "wearing ", "standing next to ", "standing beside ")},
    }

    THEME_RULES = {
        "pirat": {
            "foreign": ("dinosaur", "fossil", "prehistoric", "paleontologist", "volcano", "castle courtyard", "nature reserve"),
        },
        "dino": {
            "foreign": ("pirate", "treasure island", "pirate ship", "castle courtyard"),
        },
        "odkryw": {
            "foreign": ("pirate island", "pirate ship", "pirate captain", "castle courtyard"),
        },
    }

    RULE_SUGGESTIONS = (
        (("looking through binoculars",), "holding binoculars"),
        (("using a magnifying glass", "examining a fossil"), "holding a magnifying glass"),
        (("reading a treasure map", "following a treasure map", "following a map"), "holding a treasure map"),
        (("digging for treasure", "digging for fossils", "digging in the ground"), "holding a shovel"),
        (("pirate captain",), "wearing a pirate captain hat"),
        (("finding a dinosaur egg", "discovering a dinosaur egg"), "standing next to a dinosaur egg"),
        (("looking at flowers",), "holding a flower"),
        (("collecting leaves",), "holding a leaf"),
    )

    def __init__(self, root_folder):
        self.repository = PromptLibraryRepository(root_folder)

    @staticmethod
    def _clean(line: str) -> str | None:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            return None
        text, _ = parse_weighted_line(stripped)
        return re.sub(r"\s+", " ", text.strip()) if text else None

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[a-z0-9]+", text.casefold()))

    @classmethod
    def _similarity(cls, left: str, right: str) -> float:
        a, b = left.casefold(), right.casefold()
        seq = SequenceMatcher(None, a, b).ratio()
        ta, tb = cls._tokens(a), cls._tokens(b)
        jac = len(ta & tb) / len(ta | tb) if ta | tb else 0.0
        return max(seq, jac)

    @staticmethod
    def _role(path: Path) -> str:
        stem = re.sub(r"^\d+[_\- ]*", "", path.stem.casefold())
        stem = stem.replace("ó", "o").replace("ł", "l").replace("ś", "s").replace("ż", "z").replace("ź", "z").replace("ą", "a").replace("ę", "e").replace("ć", "c").replace("ń", "n")
        aliases = {
            "typ_postaci": "typ_postaci", "character": "character", "stroj": "stroj",
            "poza": "poza", "akcja": "akcja", "rekwizyt": "rekwizyt",
            "emocja": "emocja", "kompozycja": "kompozycja", "perspektywa": "perspektywa", "tlo": "tlo", "temat": "temat",
        }
        return aliases.get(stem, stem)

    def _entries(self, category: str):
        info = self.repository.category(category)
        by_file: dict[Path, list[tuple[int, str]]] = {}
        for path in info.prompt_files:
            values = []
            for no, raw in enumerate(read_raw_lines(path, reload_cache=True), 1):
                text = self._clean(raw)
                if text:
                    values.append((no, text))
            by_file[path] = values
        return info, by_file

    def analyze(self, category: str = "ALL") -> QualityResult:
        root = self.repository.root
        scope = (category or "ALL").strip() or "ALL"
        categories = self.repository.categories() if scope == "ALL" else [scope]
        issues: list[QualityIssue] = []
        suggestions = 0
        lines = [
            "PROMPT DOCTOR QUALITY 0.10",
            "════════════════════════════",
            f"Library: {root}",
            f"Scope: {scope}",
            "",
        ]
        if not root.is_dir() or not categories:
            issue = QualityIssue("missing_library", "ERROR", "Library or category not found.", root)
            return QualityResult("\n".join(lines + ["✗ Library or category not found."]), 0, "CRITICAL", [issue])

        for category_name in categories:
            info, by_file = self._entries(category_name)
            if not info.path.is_dir():
                issues.append(QualityIssue("missing_category", "ERROR", "Category folder not found.", info.path))
                continue
            lines.extend([f"[{category_name}]", "────────────────────────"])
            category_start = len(issues)

            # Similar or semantic duplicates inside a file.
            for path, entries in by_file.items():
                for idx, (line_a, text_a) in enumerate(entries):
                    for line_b, text_b in entries[idx + 1:]:
                        score = self._similarity(text_a, text_b)
                        if score >= 0.84 and text_a.casefold() != text_b.casefold():
                            issues.append(QualityIssue(
                                "similar_entries", "WARNING",
                                f"Similar entries ({score:.0%}): '{text_a}' ↔ '{text_b}'.",
                                path, line_b, "Consider keeping one or making their meanings more distinct.",
                            ))

            # Exact entries duplicated between files.
            seen_global: dict[str, tuple[Path, int, str]] = {}
            for path, entries in by_file.items():
                for line_no, text in entries:
                    key = text.casefold()
                    if key in seen_global and seen_global[key][0] != path:
                        first_path, first_line, _ = seen_global[key]
                        issues.append(QualityIssue(
                            "cross_file_duplicate", "WARNING",
                            f"Entry appears in two files: '{text}' ({section_label(first_path.name)}:{first_line}).",
                            path, line_no, "Keep the entry in the file matching its role.",
                        ))
                    else:
                        seen_global[key] = (path, line_no, text)

            # Role consistency checks.
            character_words: set[str] = set()
            for path, entries in by_file.items():
                if self._role(path) == "character":
                    character_words = {text.casefold() for _, text in entries}
                    break
            for path, entries in by_file.items():
                role = self._role(path)
                hints = self.ROLE_HINTS.get(role, {})
                for line_no, text in entries:
                    low = text.casefold()
                    if role == "typ_postaci":
                        duplicated = [word for word in character_words if re.search(rf"\b{re.escape(word)}\b", low)]
                        if duplicated:
                            issues.append(QualityIssue(
                                "role_overlap", "WARNING",
                                f"'{text}' repeats Character adjective: {', '.join(duplicated)}.",
                                path, line_no, "Remove the adjective from Typ Postaci.",
                            ))
                    max_words = hints.get("max_words")
                    if max_words and len(text.split()) > max_words:
                        issues.append(QualityIssue("role_length", "INFO", f"'{text}' is long for {section_label(path.name)}.", path, line_no))
                    forbidden = hints.get("forbidden_prefixes", ())
                    if forbidden and low.startswith(forbidden):
                        issues.append(QualityIssue("wrong_category", "WARNING", f"'{text}' may be in the wrong file ({section_label(path.name)}).", path, line_no))
                    preferred = hints.get("preferred_prefixes", ())
                    if preferred and not low.startswith(preferred):
                        issues.append(QualityIssue("category_style", "INFO", f"'{text}' uses a different pattern than most {section_label(path.name)} entries.", path, line_no))

            # Theme-specific, deliberately conservative conflict hints.
            cat_low = category_name.casefold()
            foreign_terms: tuple[str, ...] = ()
            for marker, config in self.THEME_RULES.items():
                if marker in cat_low:
                    foreign_terms = config["foreign"]
                    break
            if foreign_terms:
                for path, entries in by_file.items():
                    for line_no, text in entries:
                        hits = [term for term in foreign_terms if term in text.casefold()]
                        if hits:
                            issues.append(QualityIssue(
                                "thematic_conflict", "WARNING",
                                f"Possible thematic conflict: '{text}' does not clearly fit '{category_name}'.",
                                path, line_no, "Move it to another library or add an explicit rule if intentional.",
                            ))

            # Balance: compare active file sizes against median.
            counts = {path: len(values) for path, values in by_file.items() if values}
            if counts:
                med = median(counts.values())
                if med >= 4:
                    for path, count in counts.items():
                        if count < max(2, med * 0.4):
                            issues.append(QualityIssue(
                                "low_balance", "INFO",
                                f"{section_label(path.name)} has only {count} entries; category median is {med:g}.",
                                path, suggestion="Consider expanding this file if it limits variety.",
                            ))

            # Rule suggestions from pairs already present in this category.
            all_text = {text.casefold(): (path, line) for path, vals in by_file.items() for line, text in vals}
            for triggers, required in self.RULE_SUGGESTIONS:
                present_trigger = next((t for t in triggers if t in all_text), None)
                if present_trigger and required.casefold() in all_text:
                    path, line_no = all_text[present_trigger]
                    issues.append(QualityIssue(
                        "rule_suggestion", "SUGGESTION",
                        f"Suggested rule: '{present_trigger}' → requires '{required}'.",
                        path, line_no, "Add it to rules.yaml if generated prompts confirm the relationship.",
                    ))
                    suggestions += 1

            category_issues = issues[category_start:]
            warnings = sum(i.severity == "WARNING" for i in category_issues)
            infos = sum(i.severity == "INFO" for i in category_issues)
            sugg = sum(i.severity == "SUGGESTION" for i in category_issues)
            lines.extend([
                f"Files checked: {len(by_file)}",
                f"Entries checked: {sum(len(v) for v in by_file.values())}",
                f"Warnings: {warnings}",
                f"Notes: {infos}",
                f"Rule suggestions: {sugg}",
                "",
            ])

        errors = sum(i.severity == "ERROR" for i in issues)
        warnings = sum(i.severity == "WARNING" for i in issues)
        infos = sum(i.severity == "INFO" for i in issues)
        score = max(0, 100 - errors * 30 - warnings * 6 - infos * 1)
        status = "EXCELLENT" if score >= 95 else "GOOD" if score >= 80 else "NEEDS ATTENTION" if score >= 60 else "POOR"
        lines.extend([
            "QUALITY SUMMARY",
            "════════════════════════════",
            f"Health score: {score}%",
            f"Status: {status}",
            f"Warnings: {warnings}",
            f"Notes: {infos}",
            f"Suggested rules: {suggestions}",
            "",
        ])
        if issues:
            lines.extend(["FINDINGS", "────────────────────────"])
            icon = {"ERROR": "✗", "WARNING": "⚠", "INFO": "ℹ", "SUGGESTION": "💡"}
            for issue in issues:
                where = ""
                if issue.path:
                    try:
                        where = str(issue.path.relative_to(root))
                    except ValueError:
                        where = str(issue.path)
                    if issue.line:
                        where += f":{issue.line}"
                    where = f" [{where}]"
                lines.append(f"{icon.get(issue.severity, '•')} {issue.message}{where}")
                if issue.suggestion:
                    lines.append(f"   Suggestion: {issue.suggestion}")
        else:
            lines.append("✓ No quality concerns detected by local rules.")

        return QualityResult("\n".join(lines), score, status, issues, suggestions)
