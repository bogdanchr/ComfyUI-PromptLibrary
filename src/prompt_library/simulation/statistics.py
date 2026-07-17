from dataclasses import dataclass
from statistics import mean


@dataclass(slots=True, frozen=True)
class PromptLengthStatistics:
    """Podstawowe statystyki długości wygenerowanych promptów."""

    average_characters: float = 0.0
    shortest_characters: int = 0
    longest_characters: int = 0


def calculate_prompt_length_statistics(
    prompts: list[str],
) -> PromptLengthStatistics:
    """Oblicza długość średnią, minimalną i maksymalną."""

    lengths = [len(prompt) for prompt in prompts]

    if not lengths:
        return PromptLengthStatistics()

    return PromptLengthStatistics(
        average_characters=round(mean(lengths), 2),
        shortest_characters=min(lengths),
        longest_characters=max(lengths),
    )
