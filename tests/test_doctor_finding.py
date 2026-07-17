import pytest

from prompt_library.doctor import DoctorFinding, Severity


def test_severity_values() -> None:
    assert Severity.INFO.value == "info"
    assert Severity.WARNING.value == "warning"
    assert Severity.ERROR.value == "error"


def test_doctor_finding_contains_diagnostic_information() -> None:
    finding = DoctorFinding(
        code="missing_file",
        severity=Severity.ERROR,
        title="Brak wymaganego pliku",
        message="Brakuje pliku 09_kompozycja.txt.",
        category="MAŁE DINOZAURY",
        filename="09_kompozycja.txt",
        suggestion="Dodaj brakujący plik do kategorii.",
    )

    assert finding.code == "missing_file"
    assert finding.severity is Severity.ERROR
    assert finding.title == "Brak wymaganego pliku"
    assert finding.message == "Brakuje pliku 09_kompozycja.txt."
    assert finding.category == "MAŁE DINOZAURY"
    assert finding.filename == "09_kompozycja.txt"
    assert finding.suggestion == "Dodaj brakujący plik do kategorii."


def test_doctor_finding_allows_optional_location_and_suggestion() -> None:
    finding = DoctorFinding(
        code="high_duplicate_rate",
        severity=Severity.WARNING,
        title="Wysoki poziom duplikatów",
        message="Biblioteka zawiera dużo powtarzających się promptów.",
    )

    assert finding.category is None
    assert finding.filename is None
    assert finding.suggestion is None


def test_doctor_finding_is_immutable() -> None:
    finding = DoctorFinding(
        code="example",
        severity=Severity.INFO,
        title="Informacja",
        message="Przykładowa diagnoza.",
    )

    with pytest.raises(AttributeError):
        finding.message = "Zmieniona wiadomość."
