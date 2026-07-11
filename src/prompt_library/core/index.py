from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import re

from ..storage import read_raw_lines
from .constants import NEGATIVE_FILENAMES, RESERVED_FILENAMES, STYLE_FILENAMES
from .text import has_invalid_weight, parse_weighted_line


@dataclass(frozen=True)
class IndexedCategory:
    name: str
    entries: int
    files: int
    has_style: bool
    has_negative: bool
    issues: int

    @property
    def healthy(self) -> bool:
        return self.issues == 0 and self.files > 0

    @property
    def display_name(self) -> str:
        mark = "✓" if self.healthy else "⚠"
        return f"{self.name} ({self.entries}) {mark}"


class LibraryIndex:
    """A lightweight shared index used by Smart Library widgets.

    The index intentionally stores only stable facts needed by the UI. It does
    not modify files and can safely be rebuilt at any time.
    """

    def __init__(self, root_folder):
        self.root = Path(root_folder).expanduser().resolve()
        self.categories: List[IndexedCategory] = []
        self._display_to_name: Dict[str, str] = {}
        self._name_to_item: Dict[str, IndexedCategory] = {}
        self._scan()

    def _scan(self) -> None:
        if not self.root.is_dir():
            return

        folders = sorted(
            (p for p in self.root.rglob("*") if p.is_dir() and p.name != ".promptlibrary_backups"),
            key=lambda p: str(p.relative_to(self.root)).casefold(),
        )

        for folder in folders:
            prompt_files = sorted(
                (
                    p for p in folder.iterdir()
                    if p.is_file()
                    and p.suffix.casefold() == ".txt"
                    and p.name.casefold() not in RESERVED_FILENAMES
                ),
                key=lambda p: p.name.casefold(),
            )
            if not prompt_files:
                continue

            entries = 0
            issues = 0
            for path in prompt_files:
                try:
                    raw_lines = read_raw_lines(path, reload_cache=False)
                except OSError:
                    issues += 1
                    continue

                seen: set[str] = set()
                active_in_file = 0
                for raw in raw_lines:
                    stripped = raw.strip()
                    if not stripped:
                        issues += 1
                        continue
                    if stripped.startswith("#"):
                        continue
                    text, _weight = parse_weighted_line(stripped)
                    if not text:
                        continue
                    active_in_file += 1
                    entries += 1
                    key = text.casefold().strip()
                    if key in seen:
                        issues += 1
                    else:
                        seen.add(key)
                    if has_invalid_weight(stripped):
                        issues += 1
                if active_in_file == 0:
                    issues += 1

            existing = {p.name.casefold() for p in folder.iterdir() if p.is_file()}
            has_style = any(name.casefold() in existing for name in STYLE_FILENAMES)
            has_negative = any(name.casefold() in existing for name in NEGATIVE_FILENAMES)
            if not has_style:
                issues += 1
            if not has_negative:
                issues += 1

            name = folder.relative_to(self.root).as_posix()
            item = IndexedCategory(
                name=name,
                entries=entries,
                files=len(prompt_files),
                has_style=has_style,
                has_negative=has_negative,
                issues=issues,
            )
            self.categories.append(item)
            self._display_to_name[item.display_name] = item.name
            self._name_to_item[item.name] = item

    def choices(self) -> List[str]:
        return [item.display_name for item in self.categories]

    def resolve(self, value: str) -> str:
        """Resolve raw names and legacy decorated Smart Library labels.

        Legacy workflows may contain labels such as ``PIRACI (79) ✓``. The
        current entry count may be different, so exact lookup alone is not
        enough. Strip only the known trailing decoration and preserve folder
        names that legitimately contain parentheses.
        """
        value = (value or "").strip()
        exact = self._display_to_name.get(value)
        if exact is not None:
            return exact
        legacy = re.match(r"^(.*) \(\d+\) [✓⚠]$", value)
        if legacy:
            candidate = legacy.group(1).strip()
            if candidate in self._name_to_item:
                return candidate
        return value

    def get(self, name_or_label: str) -> IndexedCategory | None:
        return self._name_to_item.get(self.resolve(name_or_label))
