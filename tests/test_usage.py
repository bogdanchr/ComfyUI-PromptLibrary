from prompt_library.simulation.usage import (
    EntryUsageStatistics,
    calculate_entry_usage,
)


def test_calculate_entry_usage():
    used_by_file = {
        "01_character.txt": [
            "cute",
            "brave",
            "cute",
            "cute",
        ],
        "02_typ_postaci.txt": [
            "little boy",
            "little girl",
            "little boy",
        ],
    }

    result = calculate_entry_usage(used_by_file)

    assert result.total_selections == 7

    assert result.usage_by_file["01_character.txt"] == {
        "cute": 3,
        "brave": 1,
    }

    assert result.usage_by_file["02_typ_postaci.txt"] == {
        "little boy": 2,
        "little girl": 1,
    }


def test_entry_usage_sorts_equal_counts_alphabetically():
    result = calculate_entry_usage(
        {
            "01_character.txt": [
                "cute",
                "brave",
            ],
        }
    )

    assert list(
        result.usage_by_file["01_character.txt"]
    ) == [
        "brave",
        "cute",
    ]


def test_entry_usage_for_empty_data():
    result = calculate_entry_usage({})

    assert result == EntryUsageStatistics()
