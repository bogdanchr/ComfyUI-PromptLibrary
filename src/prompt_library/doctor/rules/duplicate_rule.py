from prompt_library.simulation import SimulationResult

from ..finding import DoctorFinding, Severity
from .base import DoctorRule


class DuplicateRule(DoctorRule):
    """Wykrywa powtarzające się prompty wygenerowane podczas symulacji."""

    rule_id = "duplicates"
    name = "Prompt duplicates"
    description = (
        "Sprawdza, czy symulacja wygenerowała identyczne prompty, "
        "i wskazuje najczęściej powtarzające się wyniki."
    )

    def evaluate(
        self,
        simulation_result: SimulationResult,
    ) -> list[DoctorFinding]:
        if simulation_result.duplicate_prompts <= 0:
            return []

        findings = [
            DoctorFinding(
                code="duplicate_prompts_detected",
                severity=Severity.WARNING,
                title="Wykryto powtarzające się prompty",
                message=(
                    "Symulacja wygenerowała "
                    f"{simulation_result.duplicate_prompts} duplikatów "
                    f"na {simulation_result.total_prompts} promptów."
                ),
                suggestion=(
                    "Zwiększ różnorodność wpisów albo sprawdź reguły, "
                    "które mogą zbyt mocno ograniczać możliwe kombinacje."
                ),
            )
        ]

        for prompt, occurrences in simulation_result.duplicate_items.items():
            if occurrences <= 1:
                continue

            findings.append(
                DoctorFinding(
                    code="duplicate_prompt",
                    severity=Severity.WARNING,
                    title="Prompt wystąpił wielokrotnie",
                    message=(
                        f"Prompt „{prompt}” został wygenerowany "
                        f"{occurrences} razy."
                    ),
                    suggestion=(
                        "Sprawdź wpisy i zależności tworzące ten prompt. "
                        "Możliwe, że biblioteka zawiera zbyt podobne warianty."
                    ),
                )
            )

        return findings
