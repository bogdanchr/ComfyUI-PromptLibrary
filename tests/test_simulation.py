from src.simulation.engine import SimulationEngine


def test_simulation_generates_requested_number_of_prompts(tmp_path):
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

    engine = SimulationEngine(str(tmp_path))

    result = engine.simulate(
        category="TEST",
        count=10,
        mode="random",
        seed=100,
    )

    assert result.total_prompts == 10
    assert len(result.prompts) == 10
    assert result.unique_prompts > 0
    assert result.duplicate_prompts == (
        result.total_prompts - result.unique_prompts
    )


def test_simulation_detects_duplicates(tmp_path):
    category = tmp_path / "TEST"
    category.mkdir()

    (category / "01_character.txt").write_text(
        "cute\n",
        encoding="utf-8",
    )
    (category / "02_typ_postaci.txt").write_text(
        "little dinosaur\n",
        encoding="utf-8",
    )

    engine = SimulationEngine(str(tmp_path))

    result = engine.simulate(
        category="TEST",
        count=5,
        mode="random",
        seed=0,
    )

    assert result.total_prompts == 5
    assert result.unique_prompts == 1
    assert result.duplicate_prompts == 4
    assert result.duplicate_rate == 80.0
    assert result.duplicate_items == {
        "cute little dinosaur": 5,
    }
