DEFAULT_ROOT = r"D:\PromptLibrary\Kolorowanki"
STYLE_FILENAMES = ("style.txt", "styl.txt", "positive_style.txt")
NEGATIVE_FILENAMES = ("negative.txt", "negatywny.txt", "negative_prompt.txt")
RESERVED_FILENAMES = {name.casefold() for name in STYLE_FILENAMES + NEGATIVE_FILENAMES}
