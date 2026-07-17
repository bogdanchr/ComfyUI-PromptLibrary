from pathlib import Path

from .engine import SimulationEngine
from .report import build_simulation_report
from .result import SimulationResult


class Simulation:
    """Publiczne API modułu symulacji PromptLibrary."""

    def __init__(self, root_folder: str | Path):
        self.root_folder = Path(root_folder)
        self.engine = SimulationEngine(str(self.root_folder))

    def run(
        self,
        category: str,
        count: int,
        mode: str = "random",
        seed: int = 0,
        index: int = 0,
        separator: str = ",\n",
    ) -> SimulationResult:
        """Uruchamia symulację i zwraca pełny wynik."""

        return self.engine.simulate(
            category=category,
            count=count,
            mode=mode,
            seed=seed,
            index=index,
            separator=separator,
        )

    @staticmethod
    def report(result: SimulationResult) -> str:
        """Buduje raport tekstowy z wyniku symulacji."""

        return build_simulation_report(result)

    @staticmethod
    def save_report(
        result: SimulationResult,
        output_path: str | Path,
    ) -> Path:
        """Zapisuje raport tekstowy do pliku UTF-8."""

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            build_simulation_report(result),
            encoding="utf-8",
        )

        return path
    