from src.prompt_library.simulation.statistics import (
    PromptLengthStatistics,
    calculate_prompt_length_statistics,
)


def test_prompt_length_statistics():
    prompts = [
        "cute dinosaur",
        "brave little dinosaur",
        "happy",
    ]

    result = calculate_prompt_length_statistics(prompts)

    assert result.average_characters == 13.0
    assert result.shortest_characters == 5
    assert result.longest_characters == 21


def test_prompt_length_statistics_for_empty_list():
    result = calculate_prompt_length_statistics([])

    assert result == PromptLengthStatistics()
