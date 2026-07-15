from dataclasses import dataclass, field
from .statistics import PromptLengthStatistics
from .coverage import CategoryCoverage
from .fingerprint import LibraryFingerprint

@dataclass(slots=True)
class SimulationResult:
    """Wynik jednej symulacji biblioteki promptów."""

    total_prompts: int = 0
    unique_prompts: int = 0
    duplicate_prompts: int = 0

    prompts: list[str] = field(default_factory=list)
    duplicate_items: dict[str, int] = field(default_factory=dict)
    
    length_statistics: PromptLengthStatistics = field(
    default_factory=PromptLengthStatistics
    )

    category_coverage: CategoryCoverage = field(
    default_factory=CategoryCoverage
    )

    library_fingerprint: LibraryFingerprint = field(
    default_factory=LibraryFingerprint
    )

    coverage: dict[str, float] = field(default_factory=dict)
    unused_entries: dict[str, list[str]] = field(default_factory=dict)

    rule_hits: dict[str, int] = field(
        default_factory=lambda: {
            "requires": 0,
            "optional": 0,
            "exclude": 0,
            "replace": 0,
        }
    )

    conflicts: list[str] = field(default_factory=list)

    @property
    def duplicate_rate(self) -> float:
        """Procent wygenerowanych promptów będących powtórzeniami."""
        if self.total_prompts == 0:
            return 0.0

        return round(
            self.duplicate_prompts / self.total_prompts * 100,
            2,
        )
    @property
    def search_space_coverage_percent(self) -> float:
        """Procent całej przestrzeni kombinacji pokryty przez symulację."""

        possible = self.library_fingerprint.possible_combinations

        if possible <= 0:
            return 0.0

        return round(
        self.unique_prompts / possible * 100,
        6,
    )