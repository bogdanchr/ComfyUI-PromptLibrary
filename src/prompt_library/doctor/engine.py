from collections.abc import Iterable

from prompt_library.simulation import SimulationResult

from .result import DoctorResult
from .rules import DoctorRule


class DoctorEngine:
    """Uruchamia reguły diagnostyczne Prompt Doctora."""

    def __init__(self, rules: Iterable[DoctorRule] | None = None) -> None:
        self._rules = list(rules or [])

    @property
    def rules(self) -> tuple[DoctorRule, ...]:
        return tuple(self._rules)

    def add_rule(self, rule: DoctorRule) -> None:
        self._rules.append(rule)

    def diagnose(self, simulation_result: SimulationResult) -> DoctorResult:
        result = DoctorResult()

        for rule in self._rules:
            findings = rule.evaluate(simulation_result)
            result.extend(findings)

        return result
