from dataclasses import dataclass, field


@dataclass(slots=True)
class SimulationResult:
    """Wynik jednej symulacji biblioteki promptów."""

    total_prompts: int = 0
    unique_prompts: int = 0
    duplicate_prompts: int = 0

    prompts: list[str] = field(default_factory=list)
    duplicate_items: dict[str, int] = field(default_factory=dict)

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
