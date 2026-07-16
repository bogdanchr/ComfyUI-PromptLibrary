from prompt_library.simulation.coverage import (
    CategoryCoverage,
    FileCoverage,
)
from prompt_library.simulation.fingerprint import LibraryFingerprint
from prompt_library.simulation.report import build_simulation_report
from prompt_library.simulation.result import SimulationResult
from prompt_library.simulation.statistics import PromptLengthStatistics
from prompt_library.simulation.structure import CategoryStructureCheck
from prompt_library.simulation.usage import EntryUsageStatistics


def test_build_simulation_report():
    result = SimulationResult(
        total_prompts=10,
        unique_prompts=8,
        duplicate_prompts=2,
        duplicate_items={
            "cute dinosaur": 3,
        },
        length_statistics=PromptLengthStatistics(
            average_characters=120.5,
            shortest_characters=90,
            longest_characters=150,
        ),
        category_structure=CategoryStructureCheck(
            present_files=(
                "01_character.txt",
                "02_typ_postaci.txt",
            ),
            missing_files=(
                "03_temat.txt",
            ),
        ),
        category_coverage=CategoryCoverage(
            files={
                "01_character.txt": FileCoverage(
                    total_entries=4,
                    used_entries=3,
                    coverage_percent=75.0,
                    unused_entries=("brave",),
                ),
            },
            total_entries=4,
            used_entries=3,
            coverage_percent=75.0,
            unused_entries={
                "01_character.txt": ("brave",),
            },
        ),
        library_fingerprint=LibraryFingerprint(
            files_count=2,
            total_entries=7,
            possible_combinations=12,
            average_entries_per_file=3.5,
            smallest_file_size=3,
            largest_file_size=4,
        ),
        entry_usage=EntryUsageStatistics(
            usage_by_file={
                "01_character.txt": {
                    "cute": 6,
                    "brave": 3,
                    "playful": 1,
                },
            },
            total_selections=10,
        ),
    )

    report = build_simulation_report(result)

    assert "Generated prompts: 10" in report
    assert "Unique prompts: 8" in report
    assert "Duplicate prompts: 2" in report
    assert "Duplicate rate: 20.00%" in report

    assert "Average characters: 120.5" in report

    assert "CATEGORY STRUCTURE" in report
    assert "Status: INCOMPLETE" in report
    assert "03_temat.txt" in report

    assert "Coverage: 75.00%" in report
    assert "01_character.txt: 3/4 (75.00%)" in report
    assert "  - brave" in report

    assert "Prompt files: 2" in report
    assert "Total entries: 7" in report
    assert "Possible combinations: 12" in report
    assert "Search space covered: 66.666667%" in report
    assert "Average entries per file: 3.5" in report

    assert "MOST USED ENTRIES" in report
    assert "cute: 6" in report
    assert "brave: 3" in report
    assert "playful: 1" in report