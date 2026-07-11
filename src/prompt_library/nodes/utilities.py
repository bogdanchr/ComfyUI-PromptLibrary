from pathlib import Path

from ..core.constants import DEFAULT_ROOT
from ..core.index import LibraryIndex
from ..core.library import PromptLibraryRepository
from ..storage import bump_library_revision, clear_prompt_cache, reset_unique_state


class PromptUtilitiesNode:
    """Administrative actions for reloading a library and Unique history."""

    DESCRIPTION = (
        "Narzędzia administracyjne. Reload Library czyści cache TXT i wymusza "
        "ponowne wykonanie node'ów Prompt Library przy następnym uruchomieniu kolejki."
    )

    @classmethod
    def INPUT_TYPES(cls):
        categories = ["ALL"] + PromptLibraryRepository(DEFAULT_ROOT).categories()
        return {
            "required": {
                "root_folder": (
                    "STRING",
                    {
                        "default": DEFAULT_ROOT,
                        "tooltip": "Główny folder biblioteki, której dotyczy operacja.",
                    },
                ),
                "category": (
                    categories,
                    {
                        "default": "ALL",
                        "tooltip": "ALL obejmuje całą bibliotekę; inna wartość ogranicza reset Unique.",
                    },
                ),
                "action": (
                    ["reload_library", "reload_text_cache", "reset_unique_history"],
                    {
                        "default": "reload_library",
                        "tooltip": (
                            "reload_library: pełne odświeżenie po edycji plików TXT; "
                            "reload_text_cache: samo czyszczenie cache; "
                            "reset_unique_history: pozwala ponownie losować użyte wpisy."
                        ),
                    },
                ),
                "execute": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "Ustaw True, uruchom kolejkę jeden raz, potem wróć na False.",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("status", "details", "affected_entries")
    FUNCTION = "run_action"
    CATEGORY = "PromptLibrary/Utilities"
    OUTPUT_NODE = True

    @classmethod
    def IS_CHANGED(cls, root_folder, category, action, execute):
        return float("nan") if execute else (root_folder, category, action, execute)

    @staticmethod
    def _library_stats(root_folder: str) -> tuple[int, int, int]:
        index = LibraryIndex(root_folder)
        categories = len(index.categories)
        files = sum(item.files for item in index.categories)
        entries = sum(item.entries for item in index.categories)
        return categories, files, entries

    def run_action(self, root_folder, category, action, execute):
        if not execute:
            return "READY", "Ustaw execute = true i uruchom kolejkę jeden raz.", 0

        if action == "reload_library":
            cached_files = clear_prompt_cache()
            revision = bump_library_revision()
            categories, files, entries = self._library_stats(root_folder)
            details = (
                "Biblioteka przeładowana.\n"
                f"Kategorie: {categories}\n"
                f"Pliki promptów: {files}\n"
                f"Aktywne wpisy: {entries}\n"
                f"Wyczyszczone wpisy cache: {cached_files}\n"
                f"Revision: {revision}\n\n"
                "Teraz ustaw execute = false i uruchom generowanie."
            )
            return "SUCCESS", details, entries

        if action == "reload_text_cache":
            affected = clear_prompt_cache()
            revision = bump_library_revision()
            return (
                "SUCCESS",
                f"Cache plików wyczyszczony ({affected}). Revision: {revision}. "
                "Przy następnym uruchomieniu Prompt Library odczyta pliki ponownie.",
                affected,
            )

        if action == "reset_unique_history":
            path = (Path(root_folder).expanduser() / category).resolve()
            affected = reset_unique_state() if category == "ALL" else reset_unique_state(folder_path=path)
            revision = bump_library_revision()
            return "SUCCESS", f"Historia Unique wyzerowana dla: {category}. Revision: {revision}.", affected

        return "ERROR", f"Nieznana operacja: {action}", 0
