from ..prompt_library.core.engine import LibraryEngine

from .result import SimulationResult


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

        prompts: list[str] = []

        for offset in range(count):
            positive, _, _, _, _ = self.library_engine.build(
                category=category,
                mode=mode,
                seed=seed + offset,
                index=index + offset,
                separator=separator,
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

        return result
