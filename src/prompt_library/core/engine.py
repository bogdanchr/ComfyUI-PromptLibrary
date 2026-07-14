from .library import PromptLibraryRepository
from .composer import PromptPart, compose_prompt_parts
from .rules import apply_rules, load_rules
from .selector import PromptSelector
from .text import clean_prompt, parse_separator


class LibraryEngine:
    def __init__(self, root_folder):
        self.repository = PromptLibraryRepository(root_folder)

    def build(
        self,
        category,
        mode,
        seed,
        index,
        separator,
        selected_parts_out=None,
    ):
        info = self.repository.category(category)
        sep = parse_separator(separator)
        debug = [
            "PROMPT LIBRARY 0.9",
            "────────────────────────",
            f"Category: {category}",
            f"Path: {info.path}",
            f"Files detected: {len(info.prompt_files)}",
            f"Mode: {mode}",
            "",
            "SELECTED PARTS",
            "────────────────────────",
        ]
        if not info.path.is_dir():
            message = f"[ERROR: category folder not found: {info.path}]"
            return message, "", "\n".join(debug + [message]), category, 0
        if not info.prompt_files:
            message = f"[ERROR: no prompt txt files found in {info.path}]"
            return message, "", "\n".join(debug + [message]), category, 0

        selected_parts = []
        errors = []

        for position, path in enumerate(info.prompt_files):
            prompt_file = self.repository.load_prompt_file(path, False)
            try:
                result = PromptSelector.select(
                    prompt_file,
                    mode,
                    seed,
                    index,
                    position * 10007,
                )
                selected_parts.append(
                    PromptPart(
                        prompt_file.label,
                        result.text,
                        path.name,
                    )
                )
                debug.append(
                    f"{prompt_file.label}: "
                    f"{result.text} "
                    f"[{result.index + 1}/{result.count}]"
                )
            except ValueError as exc:
                error = f"{prompt_file.label}: ERROR — {exc}"
                errors.append(error)
                debug.append(error)

        if selected_parts_out is not None:
            selected_parts_out.extend(selected_parts)

        def optional_text(path):
            if not path:
                return ""
            loaded = self.repository.load_prompt_file(path, False)
            return sep.join(entry.text for entry in loaded.entries) if not loaded.error else ""

        style = optional_text(info.style_file)
        negative = optional_text(info.negative_file)

        # Composer first, then deterministic rules.
        composed = compose_prompt_parts(selected_parts)
        rule_parts = [PromptPart("composed", text, "") for text in composed]
        # Preserve original selected parts for file and entry rule matching while
        # using composed output as the initial prompt body.
        rules = load_rules(info.path)
        application = apply_rules(selected_parts, rules, seed)
        selected_texts = {part.text.strip() for part in selected_parts}
        dependencies = [item for item in application.parts if item not in selected_texts]
        parts = list(composed)
        for item in dependencies:
            if item not in parts:
                parts.append(item)

        # Apply replacement/exclusion to composed fragments too.
        for removed in application.removed:
            parts = [item for item in parts if item.casefold().strip() != removed.casefold().strip()]
        for change in application.replaced:
            source, target = [value.strip() for value in change.split("→", 1)]
            parts = [target if item.casefold().strip() == source.casefold() else item for item in parts]

        if style:
            parts.append(style)
        positive = clean_prompt(sep.join(parts), sep)
        negative = clean_prompt(negative, sep)
        if not positive and errors:
            positive = "[ERROR: no valid prompt entries found]"

        debug.extend(["", "RULES / DEPENDENCIES", "────────────────────────"])
        if rules.error:
            debug.append(f"ERROR: {rules.error}")
        elif not (application.added or application.optional_added or application.removed or application.replaced):
            debug.append("No matching rules.")
        else:
            debug.extend(f"+ required: {item}" for item in application.added)
            debug.extend(f"+ optional: {item}" for item in application.optional_added)
            debug.extend(f"↔ replaced: {item}" for item in application.replaced)
            debug.extend(f"− excluded: {item}" for item in application.removed)

        debug.extend([
            "",
            "POSITIVE PROMPT",
            "────────────────────────",
            positive,
            "",
            "NEGATIVE PROMPT",
            "────────────────────────",
            negative,
        ])
        return positive, negative, "\n".join(debug), category, len(info.prompt_files)
