from prompt_library.simulation.fingerprint import (
    LibraryFingerprint,
    calculate_library_fingerprint,
)


def test_calculate_library_fingerprint():
    entries_by_file = {
        "01_character.txt": [
            "cute",
            "brave",
        ],
        "02_typ_postaci.txt": [
            "little boy",
            "little girl",
            "young boy",
        ],
        "03_temat.txt": [
            "explorer",
            "paleontologist",
        ],
    }

    result = calculate_library_fingerprint(entries_by_file)

    assert result.files_count == 3
    assert result.total_entries == 7
    assert result.possible_combinations == 12
    assert result.average_entries_per_file == 2.33
    assert result.smallest_file_size == 2
    assert result.largest_file_size == 3

    assert result.entries_by_file == {
        "01_character.txt": 2,
        "02_typ_postaci.txt": 3,
        "03_temat.txt": 2,
    }


def test_fingerprint_ignores_duplicate_entries():
    result = calculate_library_fingerprint(
        {
            "01_character.txt": [
                "cute",
                "cute",
                "brave",
            ],
        }
    )

    assert result.files_count == 1
    assert result.total_entries == 2
    assert result.possible_combinations == 2
    assert result.entries_by_file == {
        "01_character.txt": 2,
    }


def test_fingerprint_ignores_empty_files():
    result = calculate_library_fingerprint(
        {
            "01_character.txt": [],
            "02_typ_postaci.txt": [
                "little boy",
                "little girl",
            ],
        }
    )

    assert result.files_count == 1
    assert result.total_entries == 2
    assert result.possible_combinations == 2


def test_fingerprint_for_empty_library():
    result = calculate_library_fingerprint({})

    assert result == LibraryFingerprint()
