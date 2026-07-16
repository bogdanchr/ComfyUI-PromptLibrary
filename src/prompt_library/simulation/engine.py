from ..core.engine import LibraryEngine
from .result import SimulationResult
from .statistics import calculate_prompt_length_statistics
from .coverage import calculate_category_coverage
from .fingerprint import calculate_library_fingerprint
from .usage import calculate_entry_usage
from .structure import check_category_structure
class SimulationEngine:
    """Generuje wiele promptów przy użyciu tego samego silnika co Prompt Library."""

    def __init__(self, root_folder: str):
        self.library_engine = LibraryEngine(root_folder)

    def simulate(
        self,
        category: str,
        count: int,
        mode: str = "random",
        seed: int = 0,
        index: int = 0,
        separator: str = ",\n",
    ) -> SimulationResult:
        result = SimulationResult()

        if count <= 0:
            return result

        category_info = self.library_engine.repository.category(category)

        available_by_file: dict[str, list[str]] = {}
        used_by_file: dict[str, list[str]] = {}

        for path in category_info.prompt_files:
            prompt_file = self.library_engine.repository.load_prompt_file(
                path,
                False,
            )

            if prompt_file.error:
                continue

            available_by_file[path.name] = [
                entry.text for entry in prompt_file.entries
            ]
            used_by_file[path.name] = []

        result.category_structure = check_category_structure(
        list(available_by_file)
    )
        
        prompts: list[str] = []

        for offset in range(count):
            selected_parts = []

            positive, _, _, _, _ = self.library_engine.build(
                category=category,
                mode=mode,
                seed=seed + offset,
                index=index + offset,
                separator=separator,
                selected_parts_out=selected_parts,
            )

            for part in selected_parts:
                if part.filename:
                    used_by_file.setdefault(part.filename, []).append(
                        part.text
                    )
            prompts.append(positive)

        counts: dict[str, int] = {}

        for prompt in prompts:
            counts[prompt] = counts.get(prompt, 0) + 1

        duplicate_items = {
            prompt: occurrences
            for prompt, occurrences in counts.items()
            if occurrences > 1
        }

        result.total_prompts = len(prompts)
        result.unique_prompts = len(counts)
        result.duplicate_prompts = result.total_prompts - result.unique_prompts
        result.prompts = prompts
        result.duplicate_items = duplicate_items
        result.length_statistics = calculate_prompt_length_statistics(prompts)
        result.category_coverage = calculate_category_coverage(
            available_by_file=available_by_file,
            used_by_file=used_by_file,
        )
        
        result.library_fingerprint = calculate_library_fingerprint(
            entries_by_file=available_by_file
        )

        result.entry_usage = calculate_entry_usage(used_by_file)

        return result
