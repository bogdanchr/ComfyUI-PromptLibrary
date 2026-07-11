from ..core.constants import DEFAULT_ROOT
from ..core.engine import LibraryEngine
from ..core.index import LibraryIndex
from ..storage import get_library_revision


class PromptLibraryNode:
    """Main everyday node: select a category and build positive/negative prompts."""

    DESCRIPTION = (
        "Codzienny node PromptLibrary. Lista kategorii używa stabilnych nazw folderów, "
        "dzięki czemu dodanie wpisów lub nowych plików TXT nie unieważnia zapisanych workflow."
    )

    @classmethod
    def INPUT_TYPES(cls):
        index = LibraryIndex(DEFAULT_ROOT)
        # IMPORTANT: combo values must remain stable. Counts/status are metadata and
        # must not be part of the persisted category value, otherwise every library
        # edit invalidates saved workflows in ComfyUI.
        categories = [item.name for item in index.categories] or ["PIRACI"]
        return {
            "required": {
                "root_folder": (
                    "STRING",
                    {
                        "default": DEFAULT_ROOT,
                        "tooltip": (
                            "Główny folder biblioteki. Po zmianie folderu użyj Utilities → "
                            "reload_text_cache i odśwież definicje node'ów lub uruchom ComfyUI ponownie."
                        ),
                    },
                ),
                "category": (
                    categories,
                    {
                        "default": categories[0],
                        "tooltip": (
                            "Stabilna nazwa folderu kategorii. Liczbę wpisów i stan biblioteki "
                            "sprawdzisz w Prompt Doctorze; nie są już częścią wartości pola."
                        ),
                    },
                ),
                "mode": (
                    ["random", "sequential", "weighted", "unique"],
                    {
                        "default": "random",
                        "tooltip": (
                            "random: losowy wpis; sequential: kolejne wpisy; "
                            "weighted: losowanie według wag; unique: bez powtórek do resetu historii."
                        ),
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "tooltip": "Steruje losowaniem w trybach random i weighted.",
                    },
                ),
                "index": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 999999,
                        "tooltip": "Numer startowy używany przez tryb sequential.",
                    },
                ),
                "separator": (
                    "STRING",
                    {
                        "default": ",\\n",
                        "tooltip": "Separator łączący fragmenty promptu. Najczęściej: ,\\n albo , ",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("positive", "negative", "debug", "category", "files_count")
    FUNCTION = "build"
    CATEGORY = "PromptLibrary/Library"

    @classmethod
    def IS_CHANGED(cls, root_folder, category, mode, seed, index, separator):
        if mode == "unique":
            return float("nan")
        return root_folder, category, mode, seed, index, separator, get_library_revision()

    def build(self, root_folder, category, mode, seed, index, separator):
        raw_category = LibraryIndex(root_folder).resolve(category)
        return LibraryEngine(root_folder).build(
            category=raw_category,
            mode=mode,
            seed=seed,
            index=index,
            separator=separator,
        )
