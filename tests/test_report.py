from src.simulation.coverage import (
    CategoryCoverage,
    FileCoverage,
)
from src.simulation.report import build_simulation_report
from src.simulation.result import SimulationResult
from src.simulation.statistics import PromptLengthStatistics


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
    )

    report = build_simulation_report(result)

    assert "Generated prompts: 10" in report
    assert "Unique prompts: 8" in report
    assert "Duplicate prompts: 2" in report
    assert "Duplicate rate: 20.00%" in report
    assert "Average characters: 120.5" in report
    assert "Coverage: 75.00%" in report
    assert "01_character.txt: 3/4 (75.00%)" in report
    assert "  - brave" in report
