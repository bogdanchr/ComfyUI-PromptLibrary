from prompt_library.simulation.structure import (
    DEFAULT_PROMPT_FILES,
    CategoryStructureCheck,
    check_category_structure,
)


def test_category_structure_is_complete():
    result = check_category_structure(
        list(DEFAULT_PROMPT_FILES)
    )

    assert result.is_complete is True
    assert result.present_files == DEFAULT_PROMPT_FILES
    assert result.missing_files == ()


def test_category_structure_reports_missing_files():
    result = check_category_structure(
        [
            "01_character.txt",
            "02_typ_postaci.txt",
            "03_temat.txt",
        ]
    )

    assert result.is_complete is False
    assert result.missing_files == (
        "04_stroj.txt",
        "05_poza.txt",
        "06_akcja.txt",
        "07_rekwizyt.txt",
        "08_emocja.txt",
        "09_kompozycja.txt",
        "10_perspektywa.txt",
        "11_tlo.txt",
    )


def test_category_structure_is_case_insensitive():
    result = check_category_structure(
        [name.upper() for name in DEFAULT_PROMPT_FILES]
    )

    assert result.is_complete is True


def test_category_structure_for_empty_category():
    result = check_category_structure([])

    assert result == CategoryStructureCheck(
        missing_files=DEFAULT_PROMPT_FILES,
    )
