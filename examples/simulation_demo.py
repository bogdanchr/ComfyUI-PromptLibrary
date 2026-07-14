from pathlib import Path

from src.prompt_library.simulation.engine import SimulationEngine
from src.prompt_library.simulation.report import build_simulation_report


LIBRARY_ROOT = Path(r"D:\PromptLibrary\Kolorowanki")
CATEGORY = "MALI ODKRYWCY DINOZAURÓW"


def main() -> None:
    if not LIBRARY_ROOT.exists():
        raise FileNotFoundError(
            f"Library folder does not exist: {LIBRARY_ROOT}"
        )

    engine = SimulationEngine(str(LIBRARY_ROOT))

    result = engine.simulate(
        category=CATEGORY,
        count=1000,
        mode="random",
        seed=1000,
    )

    report = build_simulation_report(result)

    print(report)

    output_path = Path("simulation_report.txt")
    output_path.write_text(report, encoding="utf-8")

    print()
    print(f"Report saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
