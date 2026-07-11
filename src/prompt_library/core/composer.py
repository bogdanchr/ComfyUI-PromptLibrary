"""Prompt composition rules for readable, model-friendly prompt fragments."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence

_PREFIX_ROLE_WORDS = {
    "character",
    "charakter",
    "modifier",
    "prefix",
    "cecha",
    "cechy",
}
_SUBJECT_ROLE_WORDS = {
    "typ postaci",
    "character type",
    "subject",
    "postac",
    "postać",
}


@dataclass(frozen=True)
class PromptPart:
    label: str
    text: str
    filename: str = ""


def _normalise_label(label: str) -> str:
    return re.sub(r"\s+", " ", label.casefold().replace("_", " ")).strip()


def _is_prefix(label: str) -> bool:
    value = _normalise_label(label)
    return value in _PREFIX_ROLE_WORDS or any(word in value for word in ("character", "charakter", "prefix"))


def _is_subject(label: str) -> bool:
    value = _normalise_label(label)
    return value in _SUBJECT_ROLE_WORDS or "typ postaci" in value or "character type" in value


def _merge_prefix_subject(prefix: str, subject: str) -> str:
    """Merge adjacent character modifier and subject without repeating words.

    Examples:
        cute + preschool girl -> cute preschool girl
        cute + cute preschool girl -> cute preschool girl
        very cute + cute little boy -> very cute little boy
    """
    prefix_words = prefix.strip().split()
    subject_words = subject.strip().split()
    if not prefix_words:
        return subject.strip()
    if not subject_words:
        return prefix.strip()

    prefix_folded = [word.casefold().strip(" ,.;:") for word in prefix_words]
    subject_folded = [word.casefold().strip(" ,.;:") for word in subject_words]

    # Remove the longest overlap between the end of the prefix and the beginning
    # of the subject. This avoids "cute cute preschool girl" while preserving
    # phrases such as "very cute".
    max_overlap = min(len(prefix_words), len(subject_words))
    overlap = 0
    for size in range(max_overlap, 0, -1):
        if prefix_folded[-size:] == subject_folded[:size]:
            overlap = size
            break

    merged = prefix_words + subject_words[overlap:]
    return " ".join(merged).strip()


def compose_prompt_parts(parts: Sequence[PromptPart]) -> list[str]:
    """Compose selected file fragments while preserving their original order.

    Version 0.8 has one intentionally small rule: a character modifier file
    (for example ``01_character.txt``) immediately followed by a character type
    file (for example ``02_typ_postaci.txt``) is merged into one phrase.
    Every other part remains a separate prompt fragment.
    """
    result: list[str] = []
    index = 0
    while index < len(parts):
        current = parts[index]
        if (
            index + 1 < len(parts)
            and _is_prefix(current.label)
            and _is_subject(parts[index + 1].label)
        ):
            result.append(_merge_prefix_subject(current.text, parts[index + 1].text))
            index += 2
            continue
        if current.text.strip():
            result.append(current.text.strip())
        index += 1
    return result
