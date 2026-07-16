from dataclasses import dataclass, field


DEFAULT_PROMPT_FILES = (
    "01_character.txt",
    "02_typ_postaci.txt",
    "03_temat.txt",
    "04_stroj.txt",
    "05_poza.txt",
    "06_akcja.txt",
    "07_rekwizyt.txt",
    "08_emocja.txt",
    "09_kompozycja.txt",
    "10_perspektywa.txt",
    "11_tlo.txt",
)


@dataclass(slots=True, frozen=True)
class CategoryStructureCheck:
    """Wynik kontroli kompletności struktury kategorii."""

    expected_files: tuple[str, ...] = DEFAULT_PROMPT_FILES
    present_files: tuple[str, ...] = field(default_factory=tuple)
    missing_files: tuple[str, ...] = field(default_factory=tuple)

    @property
    def is_complete(self) -> bool:
        return not self.missing_files


def check_category_structure(
    filenames: list[str],
    expected_files: tuple[str, ...] = DEFAULT_PROMPT_FILES,
) -> CategoryStructureCheck:
    """Sprawdza, czy kategoria zawiera oczekiwane pliki promptów."""

    present_set = {name.casefold() for name in filenames}

    present = tuple(
        filename
        for filename in expected_files
        if filename.casefold() in present_set
    )

    missing = tuple(
        filename
        for filename in expected_files
        if filename.casefold() not in present_set
    )

    return CategoryStructureCheck(
        expected_files=expected_files,
        present_files=present,
        missing_files=missing,
    )
