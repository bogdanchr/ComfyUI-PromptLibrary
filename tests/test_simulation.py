from unittest import result
from src.prompt_library.simulation.engine import SimulationEngine
from src.prompt_library.simulation.result import SimulationResult
from prompt_library.simulation.fingerprint import LibraryFingerprint

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

    assert result.length_statistics.average_characters > 0
    assert result.length_statistics.shortest_characters > 0
    assert result.length_statistics.longest_characters >= (
    result.length_statistics.shortest_characters
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
    assert result.length_statistics.average_characters == 20.0
    assert result.length_statistics.shortest_characters == 20
    assert result.length_statistics.longest_characters == 20
    assert result.duplicate_items == {
        "cute little dinosaur": 5,
    }

def test_simulation_result_has_empty_category_coverage_by_default():
    engine_result = SimulationResult()

    assert engine_result.category_coverage.total_entries == 0
    assert engine_result.category_coverage.used_entries == 0
    assert engine_result.category_coverage.coverage_percent == 0.0
    assert engine_result.category_coverage.files == {}
def test_simulation_calculates_category_coverage(tmp_path):
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
        count=2,
        mode="sequential",
        seed=0,
        index=0,
    )

    assert result.category_coverage.total_entries == 4
    assert result.category_coverage.used_entries == 4
    assert result.category_coverage.coverage_percent == 100.0
    assert result.category_coverage.unused_entries == {}

    assert (
        result.category_coverage.files[
            "01_character.txt"
        ].coverage_percent
        == 100.0
    )
    assert (
        result.category_coverage.files[
            "02_typ_postaci.txt"
        ].coverage_percent
        == 100.0
    )
def test_search_space_coverage_percent():
    result = SimulationResult(
        total_prompts=10,
        unique_prompts=8,
        library_fingerprint=LibraryFingerprint(
            possible_combinations=100,
        ),
    )

    assert result.search_space_coverage_percent == 8.0
def test_search_space_coverage_percent_for_empty_space():
    result = SimulationResult()

    assert result.search_space_coverage_percent == 0.0