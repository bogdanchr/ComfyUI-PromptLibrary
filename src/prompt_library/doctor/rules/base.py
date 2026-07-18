from abc import ABC, abstractmethod

from prompt_library.simulation import SimulationResult

from ..finding import DoctorFinding


class DoctorRule(ABC):
    """Wspólny interfejs wszystkich reguł Prompt Doctora."""

    rule_id: str
    name: str
    description: str

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    @abstractmethod
    def evaluate(
        self,
        simulation_result: SimulationResult,
    ) -> list[DoctorFinding]:
        """Analizuje wynik symulacji i zwraca diagnozy."""
