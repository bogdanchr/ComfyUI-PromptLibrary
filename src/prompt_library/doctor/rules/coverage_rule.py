from prompt_library.simulation import SimulationResult

from ..finding import DoctorFinding, Severity
from .base import DoctorRule


class CoverageRule(DoctorRule):
    """Sprawdza wykorzystanie wpisów biblioteki podczas symulacji."""

    rule_id = "coverage"
    name = "Category coverage"
    description = (
        "Sprawdza ogólne pokrycie kategorii oraz wskazuje "
        "niewykorzystane wpisy w poszczególnych plikach."
    )

    def evaluate(
        self,
        simulation_result: SimulationResult,
    ) -> list[DoctorFinding]:
        coverage = simulation_result.category_coverage
        findings: list[DoctorFinding] = []

        if coverage.total_entries and coverage.coverage_percent < 100.0:
            findings.append(
                DoctorFinding(
                    code="incomplete_category_coverage",
                    severity=Severity.WARNING,
                    title="Niepełne pokrycie kategorii",
                    message=(
                        "Symulacja wykorzystała "
                        f"{coverage.coverage_percent}% wpisów kategorii "
                        f"({coverage.used_entries} z {coverage.total_entries})."
                    ),
                    suggestion=(
                        "Uruchom większą liczbę symulacji albo sprawdź, "
                        "czy reguły nie blokują części wpisów."
                    ),
                )
            )

        for filename, unused_entries in coverage.unused_entries.items():
            entries_text = ", ".join(unused_entries)

            findings.append(
                DoctorFinding(
                    code="unused_file_entries",
                    severity=Severity.WARNING,
                    title="Niewykorzystane wpisy w pliku",
                    message=(
                        f"Plik {filename} zawiera "
                        f"{len(unused_entries)} niewykorzystanych wpisów."
                    ),
                    filename=filename,
                    suggestion=(
                        "Sprawdź następujące wpisy: "
                        f"{entries_text}"
                    ),
                )
            )

        return findings
