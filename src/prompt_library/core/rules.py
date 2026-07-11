"""Deterministic rules and dependency engine for PromptLibrary 0.9."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError:  # pragma: no cover - handled at runtime in ComfyUI
    yaml = None

from .composer import PromptPart


@dataclass(frozen=True)
class RuleBlock:
    requires: tuple[str, ...] = ()
    optional: tuple[tuple[str, float], ...] = ()
    exclude: tuple[str, ...] = ()
    replace: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class RuleSet:
    entries: dict[str, RuleBlock] = field(default_factory=dict)
    files: dict[str, RuleBlock] = field(default_factory=dict)
    category: RuleBlock = RuleBlock()
    error: str | None = None


@dataclass(frozen=True)
class RuleApplication:
    parts: list[str]
    added: list[str]
    removed: list[str]
    replaced: list[str]
    optional_added: list[str]
    error: str | None = None


def _normalise_key(value: str) -> str:
    return " ".join(str(value).casefold().strip().split())


def _as_strings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return ()
    return tuple(str(item).strip() for item in value if str(item).strip())


def _optional_items(value: Any) -> tuple[tuple[str, float], ...]:
    if value is None:
        return ()
    if isinstance(value, (str, dict)):
        value = [value]
    if not isinstance(value, list):
        return ()
    result: list[tuple[str, float]] = []
    for item in value:
        if isinstance(item, str):
            result.append((item.strip(), 50.0))
        elif isinstance(item, dict):
            for text, chance in item.items():
                try:
                    probability = max(0.0, min(100.0, float(chance)))
                except (TypeError, ValueError):
                    probability = 50.0
                text = str(text).strip()
                if text:
                    result.append((text, probability))
    return tuple(result)


def _replace_items(value: Any) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, dict):
        return ()
    return tuple(
        (str(source).strip(), str(target).strip())
        for source, target in value.items()
        if str(source).strip() and str(target).strip()
    )


def _block(value: Any) -> RuleBlock:
    if not isinstance(value, dict):
        return RuleBlock()
    return RuleBlock(
        requires=_as_strings(value.get("requires")),
        optional=_optional_items(value.get("optional")),
        exclude=_as_strings(value.get("exclude")),
        replace=_replace_items(value.get("replace")),
    )


def load_rules(category_path: str | Path) -> RuleSet:
    path = Path(category_path) / "rules.yaml"
    if not path.is_file():
        return RuleSet()
    if yaml is None:
        return RuleSet(error="PyYAML is not installed. Run: pip install PyYAML")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        return RuleSet(error=f"Cannot read rules.yaml: {exc}")
    if not isinstance(data, dict):
        return RuleSet(error="rules.yaml must contain a YAML mapping")

    entries = {
        _normalise_key(name): _block(block)
        for name, block in (data.get("entries") or {}).items()
    } if isinstance(data.get("entries") or {}, dict) else {}
    files = {
        _normalise_key(name): _block(block)
        for name, block in (data.get("files") or {}).items()
    } if isinstance(data.get("files") or {}, dict) else {}
    return RuleSet(entries=entries, files=files, category=_block(data.get("category")))


def _matching_blocks(parts: Iterable[PromptPart], rules: RuleSet) -> list[RuleBlock]:
    """Return blocks in priority order: category, file, entry.

    Lower-priority rules are applied first, so higher-priority entry rules can
    replace or exclude their results later.
    """
    blocks: list[RuleBlock] = [rules.category]
    for part in parts:
        file_keys = {
            _normalise_key(part.filename),
            _normalise_key(Path(part.filename).stem),
            _normalise_key(part.label),
        }
        for key in file_keys:
            if key in rules.files:
                blocks.append(rules.files[key])
                break
    for part in parts:
        block = rules.entries.get(_normalise_key(part.text))
        if block:
            blocks.append(block)
    return blocks


def apply_rules(parts: list[PromptPart], rules: RuleSet, seed: int) -> RuleApplication:
    output = [part.text.strip() for part in parts if part.text.strip()]
    if rules.error:
        return RuleApplication(output, [], [], [], [], rules.error)

    added: list[str] = []
    removed: list[str] = []
    replaced: list[str] = []
    optional_added: list[str] = []
    rng = random.Random(int(seed) ^ 0x50A7B1)

    blocks = _matching_blocks(parts, rules)

    # requires / optional first
    for block in blocks:
        for text in block.requires:
            if _normalise_key(text) not in {_normalise_key(item) for item in output}:
                output.append(text)
                added.append(text)
        for text, chance in block.optional:
            if rng.random() * 100.0 < chance and _normalise_key(text) not in {_normalise_key(item) for item in output}:
                output.append(text)
                optional_added.append(text)

    # replace next
    for block in blocks:
        for source, target in block.replace:
            source_key = _normalise_key(source)
            for index, current in enumerate(list(output)):
                if _normalise_key(current) == source_key:
                    output[index] = target
                    replaced.append(f"{source} → {target}")

    # exclude last; higher-priority blocks run later and therefore win
    for block in blocks:
        excluded = {_normalise_key(text) for text in block.exclude}
        kept: list[str] = []
        for current in output:
            if _normalise_key(current) in excluded:
                removed.append(current)
            else:
                kept.append(current)
        output = kept

    # Final stable de-duplication.
    seen: set[str] = set()
    unique: list[str] = []
    for item in output:
        key = _normalise_key(item)
        if key and key not in seen:
            seen.add(key)
            unique.append(item)

    return RuleApplication(unique, added, removed, replaced, optional_added)
