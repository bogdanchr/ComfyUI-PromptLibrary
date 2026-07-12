from src.simulation.coverage import (
    FileCoverage,
    calculate_file_coverage,
)


def test_calculate_file_coverage():
    available = [
        "cute",
        "brave",
        "playful",
        "curious",
    ]
    used = [
        "cute",
        "playful",
        "cute",
    ]

    result = calculate_file_coverage(available, used)

    assert result.total_entries == 4
    assert result.used_entries == 2
    assert result.coverage_percent == 50.0
    assert result.unused_entries == (
        "brave",
        "curious",
    )


def test_file_coverage_removes_duplicate_available_entries():
    result = calculate_file_coverage(
        available_entries=["cute", "cute", "brave"],
        used_entries=["cute"],
    )

    assert result.total_entries == 2
    assert result.used_entries == 1
    assert result.coverage_percent == 50.0
    assert result.unused_entries == ("brave",)


def test_file_coverage_for_empty_file():
    result = calculate_file_coverage([], [])

    assert result == FileCoverage()
