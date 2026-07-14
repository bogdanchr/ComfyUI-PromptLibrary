from .result import SimulationResult


def build_simulation_report(result: SimulationResult) -> str:
    """Buduje czytelny raport tekstowy z wyniku symulacji."""

    lines = [
        "PROMPT SIMULATION",
        "════════════════════════════",
        "",
        f"Generated prompts: {result.total_prompts}",
        f"Unique prompts: {result.unique_prompts}",
        f"Duplicate prompts: {result.duplicate_prompts}",
        f"Duplicate rate: {result.duplicate_rate:.2f}%",
        "",
        "PROMPT LENGTH",
        "────────────────────────────",
        f"Average characters: "
        f"{result.length_statistics.average_characters}",
        f"Shortest prompt: "
        f"{result.length_statistics.shortest_characters}",
        f"Longest prompt: "
        f"{result.length_statistics.longest_characters}",
        "",
        "CATEGORY COVERAGE",
        "────────────────────────────",
        f"Entries used: "
        f"{result.category_coverage.used_entries}"
        f"/{result.category_coverage.total_entries}",
        f"Coverage: "
        f"{result.category_coverage.coverage_percent:.2f}%",
    ]

    if result.category_coverage.files:
        lines.extend(
            [
                "",
                "FILES",
                "────────────────────────────",
            ]
        )

        for filename, file_coverage in (
            result.category_coverage.files.items()
        ):
            lines.append(
                f"{filename}: "
                f"{file_coverage.used_entries}"
                f"/{file_coverage.total_entries} "
                f"({file_coverage.coverage_percent:.2f}%)"
            )

    if result.category_coverage.unused_entries:
        lines.extend(
            [
                "",
                "UNUSED ENTRIES",
                "────────────────────────────",
            ]
        )

        for filename, entries in (
            result.category_coverage.unused_entries.items()
        ):
            lines.append(filename)

            for entry in entries:
                lines.append(f"  - {entry}")

    return "\n".join(lines)
