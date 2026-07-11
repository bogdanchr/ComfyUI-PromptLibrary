from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

@dataclass(frozen=True)
class PromptEntry:
    text: str
    weight: float = 1.0
    source_line: int = 0
    raw: str = ""

@dataclass(frozen=True)
class PromptFile:
    path: Path
    label: str
    entries: List[PromptEntry] = field(default_factory=list)
    error: Optional[str] = None

@dataclass(frozen=True)
class CategoryInfo:
    name: str
    path: Path
    prompt_files: List[Path] = field(default_factory=list)
    style_file: Optional[Path] = None
    negative_file: Optional[Path] = None

@dataclass(frozen=True)
class SelectionResult:
    text: str
    index: int
    count: int

@dataclass(frozen=True)
class ValidationSummary:
    report: str
    status: str
    total_entries: int
    warnings: int
    errors: int

    def to_text(self) -> str:
        """Return the complete human-readable validation report."""
        return self.report

    @property
    def is_valid(self) -> bool:
        """True when validation found no errors. Warnings are allowed."""
        return self.errors == 0
