from ..core.text import clean_prompt, parse_separator


class PromptBuilderNode:
    """Combine optional prompt fragments into one clean string."""

    DESCRIPTION = "Opcjonalnie łączy kilka tekstów w jeden uporządkowany prompt."

    @classmethod
    def INPUT_TYPES(cls):
        tip = "Fragment promptu. Puste wejścia są pomijane."
        return {
            "required": {
                "base": ("STRING", {"multiline": True, "default": "", "tooltip": "Główny fragment promptu."}),
                "separator": ("STRING", {"default": ",\\n", "tooltip": "Separator między niepustymi fragmentami."}),
            },
            "optional": {
                "part_1": ("STRING", {"forceInput": True, "tooltip": tip}),
                "part_2": ("STRING", {"forceInput": True, "tooltip": tip}),
                "part_3": ("STRING", {"forceInput": True, "tooltip": tip}),
                "part_4": ("STRING", {"forceInput": True, "tooltip": tip}),
            },
        }

    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("prompt", "parts_count")
    FUNCTION = "build_prompt"
    CATEGORY = "PromptLibrary/Builder"

    def build_prompt(self, base, separator, part_1="", part_2="", part_3="", part_4=""):
        sep = parse_separator(separator)
        parts = [
            part.strip(" ,\n\t")
            for part in (base, part_1, part_2, part_3, part_4)
            if part and part.strip(" ,\n\t")
        ]
        return clean_prompt(sep.join(parts), sep), len(parts)
