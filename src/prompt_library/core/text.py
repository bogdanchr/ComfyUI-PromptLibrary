import re
from typing import Tuple

_WEIGHT_PATTERN = re.compile(r"^(.*?)(?:\s*(?:\||::)\s*)([^|:]+)$")

def parse_weighted_line(line: str) -> Tuple[str, float]:
    for separator in ("|", "::"):
        if separator in line:
            text, weight = line.rsplit(separator, 1)
            try:
                return text.strip(), max(float(weight.strip()), 0.0)
            except ValueError:
                return line.strip(), 1.0
    return line.strip(), 1.0

def has_invalid_weight(line: str) -> bool:
    match = _WEIGHT_PATTERN.match(line.strip())
    if not match:
        return False
    try:
        return float(match.group(2).strip()) < 0
    except ValueError:
        return True

def parse_separator(separator: str) -> str:
    return separator.replace("\\n", "\n").replace("\\t", "\t")

def clean_prompt(text: str, separator: str = ",\n") -> str:
    if not text:
        return ""
    separator = parse_separator(separator)
    parts = text.split(separator)
    cleaned = []
    for part in parts:
        part = part.strip().strip(" ,\n\t")
        part = re.sub(r"\s+,", ",", part)
        part = re.sub(r",\s*,+", ",", part)
        part = re.sub(r"[ \t]{2,}", " ", part)
        if part:
            cleaned.append(part)
    return separator.join(cleaned)

def section_label(filename: str) -> str:
    name = filename.rsplit(".", 1)[0]
    first, separator, rest = name.partition("_")
    if separator and first.isdigit():
        name = rest
    return name.replace("_", " ").strip().title()
