from ..core.preview import format_prompt_preview


class PromptPreviewNode:
    """Display positive, negative and debug text in one readable node."""

    DESCRIPTION = (
        "Czytelny podgląd promptu bez zewnętrznego Preview as Text. "
        "Positive jest wymagany, Negative i Debug są opcjonalne."
    )

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "positive": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Podłącz wyjście positive z Prompt Library lub Buildera.",
                    },
                ),
            },
            "optional": {
                "negative": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Opcjonalnie podłącz negative z Prompt Library.",
                    },
                ),
                "debug": (
                    "STRING",
                    {
                        "forceInput": True,
                        "tooltip": "Opcjonalnie podłącz debug z Prompt Library.",
                    },
                ),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("positive", "negative", "debug", "report")
    FUNCTION = "show_preview"
    CATEGORY = "PromptLibrary/Preview"
    OUTPUT_NODE = True

    def show_preview(self, positive, negative="", debug=""):
        report = format_prompt_preview(positive, negative, debug)
        return {
            "ui": {"text": [report]},
            "result": (positive or "", negative or "", debug or "", report),
        }
