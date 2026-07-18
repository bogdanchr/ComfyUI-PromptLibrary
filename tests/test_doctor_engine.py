from prompt_library.doctor import (
    DoctorEngine,
    DoctorFinding,
    DoctorRule,
    Severity,
)
from prompt_library.simulation import SimulationResult


class EmptyRule(DoctorRule):
    rule_id = "empty"
    name = "Empty rule"
    description = "Nie zwraca żadnych diagnoz."

    def evaluate(
        self,
        simulation_result: SimulationResult,
    ) -> list[DoctorFinding]:
        return []


class WarningRule(DoctorRule):
    rule_id = "warning"
    name = "Warning rule"
    description = "Zwraca przykładowe ostrzeżenie."

    def evaluate(
        self,
        simulation_result: SimulationResult,
    ) -> list[DoctorFinding]:
        return [
            DoctorFinding(
                code="example_warning",
                severity=Severity.WARNING,
                title="Przykładowe ostrzeżenie",
                message="Reguła wykryła przykładowy problem.",
            )
        ]


class ErrorRule(DoctorRule):
    rule_id = "error"
    name = "Error rule"
    description = "Zwraca przykładowy błąd."

    def evaluate(
        self,
        simulation_result: SimulationResult,
    ) -> list[DoctorFinding]:
        return [
            DoctorFinding(
                code="example_error",
                severity=Severity.ERROR,
                title="Przykładowy błąd",
                message="Reguła wykryła poważny problem.",
            )
        ]


def test_doctor_engine_starts_without_rules() -> None:
    engine = DoctorEngine()

    assert engine.rules == ()


def test_doctor_engine_accepts_initial_rules() -> None:
    rule = EmptyRule()
    engine = DoctorEngine([rule])

    assert engine.rules == (rule,)


def test_doctor_engine_adds_rule() -> None:
    engine = DoctorEngine()
    rule = EmptyRule()

    engine.add_rule(rule)

    assert engine.rules == (rule,)


def test_doctor_engine_returns_empty_result_without_findings() -> None:
    engine = DoctorEngine([EmptyRule()])

    result = engine.diagnose(SimulationResult())

    assert result.total_findings == 0


def test_doctor_engine_combines_findings_from_multiple_rules() -> None:
    engine = DoctorEngine(
        [
            WarningRule(),
            ErrorRule(),
        ]
    )

    result = engine.diagnose(SimulationResult())

    assert result.total_findings == 2
    assert result.warning_count == 1
    assert result.error_count == 1
    assert result.findings[0].code == "example_warning"
    assert result.findings[1].code == "example_error"


def test_doctor_engine_keeps_rule_order() -> None:
    warning_rule = WarningRule()
    error_rule = ErrorRule()

    engine = DoctorEngine(
        [
            warning_rule,
            error_rule,
        ]
    )

    assert engine.rules == (
        warning_rule,
        error_rule,
    )


def test_doctor_engine_skips_disabled_rules() -> None:
    enabled_rule = WarningRule()
    disabled_rule = ErrorRule(enabled=False)

    engine = DoctorEngine(
        [
            enabled_rule,
            disabled_rule,
        ]
    )

    result = engine.diagnose(SimulationResult())

    assert result.total_findings == 1
    assert result.warning_count == 1
    assert result.error_count == 0
    assert result.findings[0].code == "example_warning"
