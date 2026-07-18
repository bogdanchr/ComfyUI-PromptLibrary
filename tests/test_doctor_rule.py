import pytest

from prompt_library.doctor import DoctorFinding, DoctorRule
from prompt_library.simulation import SimulationResult


class ExampleRule(DoctorRule):
    rule_id = "example"
    name = "Example rule"
    description = "Przykładowa reguła używana w testach."

    def evaluate(
        self,
        simulation_result: SimulationResult,
    ) -> list[DoctorFinding]:
        return []


def test_doctor_rule_cannot_be_created_directly() -> None:
    with pytest.raises(TypeError):
        DoctorRule()


def test_doctor_rule_contains_metadata() -> None:
    rule = ExampleRule()

    assert rule.rule_id == "example"
    assert rule.name == "Example rule"
    assert rule.description == "Przykładowa reguła używana w testach."


def test_doctor_rule_is_enabled_by_default() -> None:
    rule = ExampleRule()

    assert rule.enabled is True


def test_doctor_rule_can_be_disabled() -> None:
    rule = ExampleRule(enabled=False)

    assert rule.enabled is False


def test_complete_rule_returns_findings_list() -> None:
    rule = ExampleRule()

    findings = rule.evaluate(SimulationResult())

    assert findings == []
