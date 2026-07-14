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


@dataclass(slots=True, frozen=True)
class CategoryCoverage:
    """Pokrycie wszystkich plików jednej kategorii."""

    files: dict[str, FileCoverage] = field(default_factory=dict)
    total_entries: int = 0
    used_entries: int = 0
    coverage_percent: float = 0.0
    unused_entries: dict[str, tuple[str, ...]] = field(default_factory=dict)


def calculate_category_coverage(
    available_by_file: dict[str, list[str]],
    used_by_file: dict[str, list[str]],
) -> CategoryCoverage:
    """Oblicza pokrycie całej kategorii, osobno dla każdego pliku."""

    file_results: dict[str, FileCoverage] = {}
    unused_by_file: dict[str, tuple[str, ...]] = {}

    total_entries = 0
    used_entries = 0

    for filename, available_entries in available_by_file.items():
        file_coverage = calculate_file_coverage(
            available_entries=available_entries,
            used_entries=used_by_file.get(filename, []),
        )

        file_results[filename] = file_coverage
        total_entries += file_coverage.total_entries
        used_entries += file_coverage.used_entries

        if file_coverage.unused_entries:
            unused_by_file[filename] = file_coverage.unused_entries

    coverage_percent = (
        round(used_entries / total_entries * 100, 2)
        if total_entries
        else 0.0
    )

    return CategoryCoverage(
        files=file_results,
        total_entries=total_entries,
        used_entries=used_entries,
        coverage_percent=coverage_percent,
        unused_entries=unused_by_file,
    )
