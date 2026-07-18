from prompt_library.doctor import Severity, StructureRule
from prompt_library.simulation import (
    CategoryStructureCheck,
    SimulationResult,
)


def test_structure_rule_contains_metadata() -> None:
    rule = StructureRule()

    assert rule.rule_id == "structure"
    assert rule.name == "Category structure"
    assert rule.description


def test_structure_rule_returns_no_findings_for_complete_structure() -> None:
    simulation_result = SimulationResult(
        category_structure=CategoryStructureCheck(
            expected_files=(
                "01_character.txt",
                "02_action.txt",
            ),
            present_files=(
                "01_character.txt",
                "02_action.txt",
            ),
            missing_files=(),
        )
    )

    findings = StructureRule().evaluate(simulation_result)

    assert findings == []


def test_structure_rule_reports_one_missing_file() -> None:
    simulation_result = SimulationResult(
        category_structure=CategoryStructureCheck(
            expected_files=(
                "01_character.txt",
                "02_action.txt",
            ),
            present_files=("01_character.txt",),
            missing_files=("02_action.txt",),
        )
    )

    findings = StructureRule().evaluate(simulation_result)

    assert len(findings) == 1

    finding = findings[0]

    assert finding.code == "missing_category_file"
    assert finding.severity is Severity.ERROR
    assert finding.title == "Brak wymaganego pliku"
    assert finding.filename == "02_action.txt"
    assert "02_action.txt" in finding.message
    assert finding.suggestion == ("Dodaj plik 02_action.txt do katalogu kategorii.")


def test_structure_rule_reports_every_missing_file() -> None:
    simulation_result = SimulationResult(
        category_structure=CategoryStructureCheck(
            expected_files=(
                "01_character.txt",
                "02_action.txt",
                "03_style.txt",
            ),
            present_files=("01_character.txt",),
            missing_files=(
                "02_action.txt",
                "03_style.txt",
            ),
        )
    )

    findings = StructureRule().evaluate(simulation_result)

    assert len(findings) == 2
    assert [finding.filename for finding in findings] == [
        "02_action.txt",
        "03_style.txt",
    ]


def test_structure_rule_can_be_used_by_doctor_engine() -> None:
    from prompt_library.doctor import DoctorEngine

    simulation_result = SimulationResult(
        category_structure=CategoryStructureCheck(
            expected_files=("01_character.txt",),
            present_files=(),
            missing_files=("01_character.txt",),
        )
    )

    result = DoctorEngine([StructureRule()]).diagnose(simulation_result)

    assert result.total_findings == 1
    assert result.error_count == 1
