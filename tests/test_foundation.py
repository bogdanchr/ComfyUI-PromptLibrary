from pathlib import Path
import tempfile

from src.prompt_library.nodes import NODE_CLASS_MAPPINGS
from src.prompt_library.core.engine import LibraryEngine


def test_public_nodes():
    assert set(NODE_CLASS_MAPPINGS) == {
        "PromptLibrary",
        "PromptLibraryUtilities",
        "PromptValidator",
        "PL_PromptBuilder",
        "PL_PromptPreview",
    }


def test_engine_builds_prompt():
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        category = root / "PIRACI"
        category.mkdir()
        (category / "subject.txt").write_text("pirate boy\npirate girl\n", encoding="utf-8")
        (category / "style.txt").write_text("clean coloring page\n", encoding="utf-8")
        (category / "negative.txt").write_text("color\n", encoding="utf-8")

        positive, negative, debug, name, count = LibraryEngine(root).build(
            "PIRACI", "sequential", 0, 0, ",\\n"
        )

        assert "pirate boy" in positive
        assert "clean coloring page" in positive
        assert negative == "color"
        assert name == "PIRACI"
        assert count == 1
        assert "PROMPT LIBRARY" in debug


def test_validator_node_executes(tmp_path):
    category = tmp_path / "PIRACI"
    category.mkdir()
    (category / "subjects.txt").write_text("pirate ship\npirate captain\n", encoding="utf-8")

    from prompt_library.nodes.validator import PromptValidatorNode

    report, is_valid = PromptValidatorNode().validate_library(str(tmp_path), "PIRACI", True)
    assert "Total entries: 2" in report
    assert is_valid is True


def test_prompt_doctor_diagnoses_and_repairs(tmp_path):
    category = tmp_path / "PIRACI"
    category.mkdir()
    prompts = category / "subjects.txt"
    prompts.write_text("pirate ship\n\npirate ship\npirate captain\n", encoding="utf-8")

    from prompt_library.core.doctor import PromptDoctor

    doctor = PromptDoctor(tmp_path)
    before = doctor.diagnose("PIRACI")
    assert before.issues_count >= 4  # duplicate, blank, missing style and negative

    after = doctor.repair("PIRACI", "fix_all_safe")
    assert after.fixed_files == 3
    assert (category / "style.txt").exists()
    assert (category / "negative.txt").exists()
    assert prompts.read_text(encoding="utf-8") == "pirate ship\npirate captain\n"
    backups = list((tmp_path / ".promptlibrary_backups").glob("*/PIRACI/subjects.txt"))
    assert len(backups) == 1


def test_doctor_node_keeps_first_two_legacy_outputs(tmp_path):
    category = tmp_path / "PIRACI"
    category.mkdir()
    (category / "subjects.txt").write_text("pirate ship\n", encoding="utf-8")

    from prompt_library.nodes.validator import PromptValidatorNode

    report, healthy, issues, fixed = PromptValidatorNode().run_doctor(
        str(tmp_path), "PIRACI", True, "diagnose"
    )
    assert "PROMPT DOCTOR" in report
    assert healthy is True
    assert issues == 2  # missing style and negative are warnings
    assert fixed == 0


def test_smart_library_index(tmp_path):
    from src.prompt_library.core.index import LibraryIndex

    category = tmp_path / "PIRACI"
    category.mkdir()
    (category / "postac.txt").write_text("pirate boy\npirate girl\n", encoding="utf-8")
    (category / "style.txt").write_text("line art\n", encoding="utf-8")
    (category / "negative.txt").write_text("no shading\n", encoding="utf-8")

    index = LibraryIndex(tmp_path)
    assert index.choices() == ["PIRACI (2) ✓"]
    assert index.resolve("PIRACI (2) ✓") == "PIRACI"
    assert index.resolve("PIRACI") == "PIRACI"


def test_smart_library_warns_about_duplicate(tmp_path):
    from src.prompt_library.core.index import LibraryIndex

    category = tmp_path / "PIRACI"
    category.mkdir()
    (category / "postac.txt").write_text("pirate boy\npirate boy\n", encoding="utf-8")
    (category / "style.txt").write_text("line art\n", encoding="utf-8")
    (category / "negative.txt").write_text("no shading\n", encoding="utf-8")

    index = LibraryIndex(tmp_path)
    assert index.choices() == ["PIRACI (2) ⚠"]


def test_prompt_preview_formats_and_passes_through():
    from src.prompt_library.nodes.preview import PromptPreviewNode

    result = PromptPreviewNode().show_preview("cute dinosaur", "no shading", "Category: DINO")
    assert result["result"][:3] == ("cute dinosaur", "no shading", "Category: DINO")
    report = result["result"][3]
    assert "PROMPT PREVIEW" in report
    assert "POSITIVE" in report
    assert "cute dinosaur" in report
    assert "NEGATIVE" in report
    assert result["ui"]["text"] == [report]


def test_library_node_uses_stable_category_values(tmp_path, monkeypatch):
    from src.prompt_library.nodes import library as library_module

    category = tmp_path / "PIRACI"
    category.mkdir()
    (category / "postac.txt").write_text("pirate boy\npirate girl\n", encoding="utf-8")
    (category / "style.txt").write_text("line art\n", encoding="utf-8")
    (category / "negative.txt").write_text("no shading\n", encoding="utf-8")

    monkeypatch.setattr(library_module, "DEFAULT_ROOT", str(tmp_path))
    category_spec = library_module.PromptLibraryNode.INPUT_TYPES()["required"]["category"]
    assert category_spec[0] == ["PIRACI"]


def test_resolve_legacy_label_after_entry_count_changes(tmp_path):
    from src.prompt_library.core.index import LibraryIndex

    category = tmp_path / "MALI ODKRYWCY DINOZAURÓW"
    category.mkdir()
    (category / "postac.txt").write_text("one\ntwo\nthree\n", encoding="utf-8")
    (category / "style.txt").write_text("line art\n", encoding="utf-8")
    (category / "negative.txt").write_text("no shading\n", encoding="utf-8")

    index = LibraryIndex(tmp_path)
    assert index.resolve("MALI ODKRYWCY DINOZAURÓW (66) ✓") == "MALI ODKRYWCY DINOZAURÓW"


def test_reload_library_bumps_revision_and_reports_entries(tmp_path):
    from prompt_library.nodes.utilities import PromptUtilitiesNode
    from prompt_library.storage import get_library_revision

    category = tmp_path / "TEST"
    category.mkdir()
    (category / "01_subject.txt").write_text("first\nsecond\n", encoding="utf-8")
    (category / "style.txt").write_text("clean style\n", encoding="utf-8")
    (category / "negative.txt").write_text("noise\n", encoding="utf-8")

    before = get_library_revision()
    status, details, affected = PromptUtilitiesNode().run_action(
        str(tmp_path), "ALL", "reload_library", True
    )
    after = get_library_revision()

    assert status == "SUCCESS"
    assert affected == 2
    assert after == before + 1
    assert "Aktywne wpisy: 2" in details


def test_prompt_library_is_changed_contains_runtime_revision():
    from prompt_library.nodes.library import PromptLibraryNode
    from prompt_library.storage import bump_library_revision

    first = PromptLibraryNode.IS_CHANGED("root", "cat", "random", 1, 0, ", ")
    bump_library_revision()
    second = PromptLibraryNode.IS_CHANGED("root", "cat", "random", 1, 0, ", ")

    assert first != second


def test_prompt_composer_merges_character_with_character_type():
    from prompt_library.core.composer import PromptPart, compose_prompt_parts

    parts = [
        PromptPart("Character", "cute"),
        PromptPart("Typ Postaci", "preschool girl"),
        PromptPart("Temat", "young explorer"),
    ]
    assert compose_prompt_parts(parts) == ["cute preschool girl", "young explorer"]


def test_prompt_composer_removes_adjacent_duplicate_word():
    from prompt_library.core.composer import PromptPart, compose_prompt_parts

    parts = [
        PromptPart("Character", "cute"),
        PromptPart("Typ Postaci", "cute preschool girl"),
    ]
    assert compose_prompt_parts(parts) == ["cute preschool girl"]


def test_engine_uses_prompt_composer(tmp_path):
    category = tmp_path / "DINO"
    category.mkdir()
    (category / "01_character.txt").write_text("cute\n", encoding="utf-8")
    (category / "02_typ_postaci.txt").write_text("preschool girl\n", encoding="utf-8")
    (category / "03_temat.txt").write_text("young explorer\n", encoding="utf-8")

    positive, *_ = LibraryEngine(tmp_path).build("DINO", "sequential", 0, 0, ",\\n")
    assert positive == "cute preschool girl,\nyoung explorer"


def test_rules_engine_requires_optional_replace_exclude(tmp_path):
    from prompt_library.core.composer import PromptPart
    from prompt_library.core.rules import apply_rules, load_rules

    category = tmp_path / "PIRACI"
    category.mkdir()
    (category / "rules.yaml").write_text(
        """
entries:
  pirate ship:
    requires:
      - ocean
      - waves
    optional:
      - seagulls: 100
    exclude:
      - spaceship
    replace:
      boat: pirate ship
""",
        encoding="utf-8",
    )
    rules = load_rules(category)
    result = apply_rules(
        [
            PromptPart("Temat", "pirate ship", "03_temat.txt"),
            PromptPart("Rekwizyt", "spaceship", "07_rekwizyt.txt"),
            PromptPart("Inny", "boat", "08_inny.txt"),
        ],
        rules,
        seed=1,
    )
    assert "ocean" in result.parts
    assert "waves" in result.parts
    assert "seagulls" in result.parts
    assert "spaceship" not in result.parts
    assert "pirate ship" in result.parts
    assert result.error is None


def test_engine_applies_rules_yaml(tmp_path):
    from prompt_library.core.engine import LibraryEngine

    category = tmp_path / "DINO"
    category.mkdir()
    (category / "01_character.txt").write_text("cute\n", encoding="utf-8")
    (category / "02_typ_postaci.txt").write_text("preschool girl\n", encoding="utf-8")
    (category / "03_temat.txt").write_text("young explorer\n", encoding="utf-8")
    (category / "rules.yaml").write_text(
        """
entries:
  young explorer:
    requires:
      - fossil excavation site
""",
        encoding="utf-8",
    )
    positive, _, debug, _, _ = LibraryEngine(tmp_path).build(
        "DINO", "random", 0, 0, ",\n"
    )
    assert "cute preschool girl" in positive
    assert "fossil excavation site" in positive
    assert "+ required: fossil excavation site" in debug


def test_quality_doctor_detects_similarity_and_theme_conflict(tmp_path):
    from src.prompt_library.core.quality import PromptQualityDoctor
    category = tmp_path / "MALI ODKRYWCY"
    category.mkdir()
    (category / "01_character.txt").write_text("cute\nadorable\n", encoding="utf-8")
    (category / "02_typ_postaci.txt").write_text("cute little boy\nlittle girl\n", encoding="utf-8")
    (category / "08_emocja.txt").write_text("happy smile\nsmiling happily\n", encoding="utf-8")
    (category / "11_tlo.txt").write_text("pirate island\nforest trail\n", encoding="utf-8")
    result = PromptQualityDoctor(tmp_path).analyze("MALI ODKRYWCY")
    kinds = {i.kind for i in result.issues}
    assert "role_overlap" in kinds
    assert "thematic_conflict" in kinds
    assert result.score < 100


def test_doctor_quality_action(tmp_path):
    from src.prompt_library.core.doctor import PromptDoctor
    category = tmp_path / "PIRACI"
    category.mkdir()
    (category / "01_character.txt").write_text("cute\n", encoding="utf-8")
    (category / "02_typ_postaci.txt").write_text("cute little boy\n", encoding="utf-8")
    result = PromptDoctor(tmp_path).repair("PIRACI", "quality_check")
    assert "PROMPT DOCTOR QUALITY" in result.report
