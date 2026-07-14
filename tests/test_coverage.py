from src.simulation.coverage import (
    FileCoverage,
    calculate_file_coverage,
    CategoryCoverage,
    calculate_category_coverage,
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
def test_calculate_category_coverage():
    available_by_file = {
        "01_character.txt": [
            "cute",
            "brave",
        ],
        "02_typ_postaci.txt": [
            "little boy",
            "little girl",
        ],
    }

    used_by_file = {
        "01_character.txt": [
            "cute",
        ],
        "02_typ_postaci.txt": [
            "little boy",
            "little girl",
        ],
    }

    result = calculate_category_coverage(
        available_by_file=available_by_file,
        used_by_file=used_by_file,
    )

    assert result.total_entries == 4
    assert result.used_entries == 3
    assert result.coverage_percent == 75.0

    assert result.files["01_character.txt"].coverage_percent == 50.0
    assert result.files["02_typ_postaci.txt"].coverage_percent == 100.0

    assert result.unused_entries == {
        "01_character.txt": ("brave",),
    }


def test_category_coverage_handles_missing_used_file():
    result = calculate_category_coverage(
        available_by_file={
            "01_character.txt": ["cute", "brave"],
        },
        used_by_file={},
    )

    assert result.total_entries == 2
    assert result.used_entries == 0
    assert result.coverage_percent == 0.0
    assert result.unused_entries == {
        "01_character.txt": ("cute", "brave"),
    }


def test_category_coverage_for_empty_category():
    result = calculate_category_coverage({}, {})

    assert result == CategoryCoverage()