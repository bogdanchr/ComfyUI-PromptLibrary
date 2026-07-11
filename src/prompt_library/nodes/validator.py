from ..core.constants import DEFAULT_ROOT
from ..core.doctor import PromptDoctor


class PromptValidatorNode:
    """Prompt Doctor: diagnose and safely repair a prompt library."""

    DESCRIPTION = (
        "Prompt Doctor sprawdza bibliotekę, wskazuje konkretne problemy i może "
        "bezpiecznie usunąć duplikaty/puste linie lub utworzyć brakujące pliki pomocnicze."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "root_folder": ("STRING", {"default": DEFAULT_ROOT, "tooltip": "Folder biblioteki do zdiagnozowania."}),
                "category": ("STRING", {"default": "", "tooltip": "Puste pole = cała biblioteka. Możesz podać jedną kategorię."}),
                "validate": ("BOOLEAN", {"default": True, "tooltip": "Uruchom Prompt Doctor podczas kolejki."}),
                "action": ([
                    "diagnose",
                    "quality_check",
                    "full_diagnosis",
                    "fix_duplicates_blank_lines",
                    "create_missing_files",
                    "fix_all_safe",
                ], {"default": "diagnose", "tooltip": "quality_check analizuje treść bez zmian plików; full_diagnosis łączy kontrolę techniczną i jakościową. Akcje naprawcze tworzą kopię zmienianych plików."}),
            }
        }

    RETURN_TYPES = ("STRING", "BOOLEAN", "INT", "INT")
    RETURN_NAMES = ("report", "is_healthy", "issues_count", "fixed_files")
    FUNCTION = "run_doctor"
    CATEGORY = "PromptLibrary/Doctor"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, root_folder, category, validate, action="diagnose"):
        return float("nan") if validate else (root_folder, category, validate, action)

    def run_doctor(self, root_folder, category, validate, action="diagnose"):
        if not validate:
            return ("Prompt Doctor wyłączony.", True, 0, 0)
        doctor = PromptDoctor(root_folder)
        scope = (category or "ALL").strip() or "ALL"
        result = doctor.repair(scope, action)
        return (result.report, result.is_healthy, result.issues_count, result.fixed_files)

    # Compatibility with workflows/tests that still call the old function name.
    def validate_library(self, root_folder, category, validate, action="diagnose"):
        return self.run_doctor(root_folder, category, validate, action)[:2]
