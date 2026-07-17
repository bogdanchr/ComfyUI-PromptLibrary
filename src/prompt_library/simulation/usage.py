from collections import Counter
from dataclasses import dataclass, field


@dataclass(slots=True, frozen=True)
class EntryUsageStatistics:
    """Liczba użyć wpisów podczas symulacji."""

    usage_by_file: dict[str, dict[str, int]] = field(default_factory=dict)
    total_selections: int = 0


def calculate_entry_usage(
    used_by_file: dict[str, list[str]],
) -> EntryUsageStatistics:
    """Zlicza użycia każdego wpisu osobno dla każdego pliku."""

    usage_by_file: dict[str, dict[str, int]] = {}
    total_selections = 0

    for filename, entries in used_by_file.items():
        counts = Counter(entries)

        usage_by_file[filename] = dict(
            sorted(
                counts.items(),
                key=lambda item: (-item[1], item[0]),
            )
        )

        total_selections += sum(counts.values())

    return EntryUsageStatistics(
        usage_by_file=usage_by_file,
        total_selections=total_selections,
    )
