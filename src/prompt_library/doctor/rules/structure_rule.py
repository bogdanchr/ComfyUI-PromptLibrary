from prompt_library.simulation import SimulationResult

from ..finding import DoctorFinding, Severity
from .base import DoctorRule


class StructureRule(DoctorRule):
    """Sprawdza kompletność plików kategorii promptów."""

    rule_id = "structure"
    name = "Category structure"
    description = "Sprawdza, czy kategoria zawiera wszystkie wymagane pliki."

    def evaluate(
        self,
        simulation_result: SimulationResult,
    ) -> list[DoctorFinding]:
        structure = simulation_result.category_structure

        return [
            DoctorFinding(
                code="missing_category_file",
                severity=Severity.ERROR,
                title="Brak wymaganego pliku",
                message=f"W kategorii brakuje pliku: {filename}",
                filename=filename,
                suggestion=f"Dodaj plik {filename} do katalogu kategorii.",
            )
            for filename in structure.missing_files
        ]
