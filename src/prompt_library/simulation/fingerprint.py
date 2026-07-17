from dataclasses import dataclass, field
from math import prod


@dataclass(slots=True, frozen=True)
class LibraryFingerprint:
    """Podstawowy odcisk struktury biblioteki promptów."""

    files_count: int = 0
    total_entries: int = 0
    possible_combinations: int = 0

    average_entries_per_file: float = 0.0
    smallest_file_size: int = 0
    largest_file_size: int = 0

    entries_by_file: dict[str, int] = field(default_factory=dict)


def calculate_library_fingerprint(
    entries_by_file: dict[str, list[str]],
) -> LibraryFingerprint:
    """Oblicza teoretyczną liczbę kombinacji i balans plików."""

    normalized_counts: dict[str, int] = {}

    for filename, entries in entries_by_file.items():
        unique_entries = tuple(dict.fromkeys(entries))

        if unique_entries:
            normalized_counts[filename] = len(unique_entries)

    if not normalized_counts:
        return LibraryFingerprint()

    sizes = list(normalized_counts.values())
    total_entries = sum(sizes)

    return LibraryFingerprint(
        files_count=len(normalized_counts),
        total_entries=total_entries,
        possible_combinations=prod(sizes),
        average_entries_per_file=round(
            total_entries / len(normalized_counts),
            2,
        ),
        smallest_file_size=min(sizes),
        largest_file_size=max(sizes),
        entries_by_file=normalized_counts,
    )
