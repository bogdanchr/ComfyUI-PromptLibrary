from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class FileCoverage:
    """Pokrycie wpisów jednego pliku biblioteki."""

    total_entries: int = 0
    used_entries: int = 0
    coverage_percent: float = 0.0
    unused_entries: tuple[str, ...] = field(default_factory=tuple)


def calculate_file_coverage(
    available_entries: list[str],
    used_entries: list[str],
) -> FileCoverage:
    """Oblicza, ile dostępnych wpisów zostało użytych w symulacji."""

    available = tuple(dict.fromkeys(available_entries))
    used = set(used_entries)

    if not available:
        return FileCoverage()

    used_count = sum(entry in used for entry in available)
    unused = tuple(entry for entry in available if entry not in used)

    return FileCoverage(
        total_entries=len(available),
        used_entries=used_count,
        coverage_percent=round(used_count / len(available) * 100, 2),
        unused_entries=unused,
    )
