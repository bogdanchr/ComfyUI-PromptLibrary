from pathlib import Path

from prompt_library.simulation import Simulation


LIBRARY_ROOT = Path(r"D:\PromptLibrary\Kolorowanki")
CATEGORY = "MALI ODKRYWCY DINOZAURÓW"


def main() -> None:
    if not LIBRARY_ROOT.exists():
        raise FileNotFoundError(
            f"Library folder does not exist: {LIBRARY_ROOT}"
        )

    simulation = Simulation(LIBRARY_ROOT)

    result = simulation.run(
        category=CATEGORY,
        count=1000,
        mode="random",
        seed=1000,
    )

    report = simulation.report(result)

    print(report)

    output_path = simulation.save_report(
        result,
        Path("simulation_report.txt"),
    )

    print()
    print(f"Report saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()