from pathlib import Path
from typing import List, Optional

from ..models import CategoryInfo, PromptEntry, PromptFile
from ..storage import read_raw_lines
from .constants import NEGATIVE_FILENAMES, RESERVED_FILENAMES, STYLE_FILENAMES
from .text import parse_weighted_line, section_label

class PromptLibraryRepository:
    def __init__(self, root_folder):
        self.root = Path(root_folder).expanduser().resolve()

    def categories(self) -> List[str]:
        if not self.root.is_dir():
            return []
        return sorted((p.name for p in self.root.iterdir() if p.is_dir()), key=str.casefold)

    def category(self, name: str) -> CategoryInfo:
        path = (self.root / name).resolve()
        prompt_files = self.prompt_files(path)
        return CategoryInfo(
            name=name,
            path=path,
            prompt_files=prompt_files,
            style_file=self.find_optional(path, STYLE_FILENAMES),
            negative_file=self.find_optional(path, NEGATIVE_FILENAMES),
        )

    @staticmethod
    def prompt_files(category_path)     -> List[Path]:
        path = Path(category_path)
        if not path.is_dir():
            return []
        files = [p for p in path.iterdir() if p.is_file() and p.suffix.casefold() == ".txt" and p.name.casefold() not in RESERVED_FILENAMES]
        return sorted(files, key=lambda p: p.name.casefold())

    @staticmethod
    def find_optional(folder, filenames) -> Optional[Path]:
        folder = Path(folder)
        existing = {p.name.casefold(): p for p in folder.iterdir()} if folder.is_dir() else {}
        for filename in filenames:
            if filename.casefold() in existing and existing[filename.casefold()].is_file():
                return existing[filename.casefold()]
        return None

    @staticmethod
    def load_prompt_file(file_path, reload_cache=False) -> PromptFile:
        path = Path(file_path).expanduser().resolve()
        try:
            raw_lines = read_raw_lines(path, reload_cache)
        except OSError as exc:
            return PromptFile(path=path, label=section_label(path.name), error=str(exc))
        entries = []
        for line_number, raw in enumerate(raw_lines, start=1):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            text, weight = parse_weighted_line(stripped)
            if text:
                entries.append(PromptEntry(text=text, weight=weight, source_line=line_number, raw=raw))
        error = None if entries else "File contains no active prompt entries"
        return PromptFile(path=path, label=section_label(path.name), entries=entries, error=error)
