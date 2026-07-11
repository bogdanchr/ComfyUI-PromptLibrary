from .library import PromptLibraryNode
from .builder import PromptBuilderNode
from .validator import PromptValidatorNode
from .utilities import PromptUtilitiesNode
from .preview import PromptPreviewNode

NODE_CLASS_MAPPINGS = {
    "PromptLibrary": PromptLibraryNode,
    "PL_PromptBuilder": PromptBuilderNode,
    "PromptValidator": PromptValidatorNode,
    "PromptLibraryUtilities": PromptUtilitiesNode,
    "PL_PromptPreview": PromptPreviewNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PromptLibrary": "Prompt Library",
    "PL_PromptBuilder": "Prompt Library / Builder",
    "PromptValidator": "Prompt Library / Doctor",
    "PromptLibraryUtilities": "Prompt Library / Utilities",
    "PL_PromptPreview": "Prompt Library / Preview",
}
