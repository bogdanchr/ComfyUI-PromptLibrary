from prompt_library.simulation import Simulation


def test_simulation_api_runs_and_builds_report(tmp_path):
    category = tmp_path / "TEST"
    category.mkdir()

    (category / "01_character.txt").write_text(
        "cute\nbrave\n",
        encoding="utf-8",
    )
    (category / "02_typ_postaci.txt").write_text(
        "little boy\nlittle girl\n",
        encoding="utf-8",
    )

    simulation = Simulation(tmp_path)

    result = simulation.run(
        category="TEST",
        count=10,
        mode="random",
        seed=100,
    )

    report = simulation.report(result)

    assert result.total_prompts == 10
    assert "Generated prompts: 10" in report
    assert "LIBRARY FINGERPRINT" in report


def test_simulation_api_saves_report(tmp_path):
    category = tmp_path / "TEST"
    category.mkdir()

    (category / "01_character.txt").write_text(
        "cute\n",
        encoding="utf-8",
    )

    simulation = Simulation(tmp_path)

    result = simulation.run(
        category="TEST",
        count=3,
        mode="random",
        seed=0,
    )

    output_path = tmp_path / "reports" / "simulation.txt"

    saved_path = simulation.save_report(
        result,
        output_path,
    )

    assert saved_path == output_path
    assert output_path.exists()
    assert "Generated prompts: 3" in output_path.read_text(
        encoding="utf-8"
    )