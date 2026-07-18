from prompt_library.doctor import DuplicateRule, Severity
from prompt_library.simulation import SimulationResult


def test_duplicate_rule_contains_metadata() -> None:
    rule = DuplicateRule()

    assert rule.rule_id == "duplicates"
    assert rule.name == "Prompt duplicates"
    assert rule.description


def test_duplicate_rule_returns_no_findings_without_duplicates() -> None:
    simulation_result = SimulationResult(
        total_prompts=10,
        unique_prompts=10,
        duplicate_prompts=0,
        duplicate_items={},
    )

    findings = DuplicateRule().evaluate(simulation_result)

    assert findings == []


def test_duplicate_rule_reports_duplicate_summary() -> None:
    simulation_result = SimulationResult(
        total_prompts=10,
        unique_prompts=8,
        duplicate_prompts=2,
        duplicate_items={
            "pirate with a sword": 2,
            "pirate on a ship": 2,
        },
    )

    findings = DuplicateRule().evaluate(simulation_result)

    summary = findings[0]

    assert summary.code == "duplicate_prompts_detected"
    assert summary.severity is Severity.WARNING
    assert summary.title == "Wykryto powtarzające się prompty"
    assert "2" in summary.message
    assert "10" in summary.message
    assert summary.suggestion


def test_duplicate_rule_reports_each_duplicate_prompt() -> None:
    simulation_result = SimulationResult(
        total_prompts=6,
        unique_prompts=4,
        duplicate_prompts=2,
        duplicate_items={
            "pirate with a sword": 3,
            "pirate on a ship": 2,
        },
    )

    findings = DuplicateRule().evaluate(simulation_result)

    assert len(findings) == 3

    duplicate_findings = findings[1:]

    assert [finding.code for finding in duplicate_findings] == [
        "duplicate_prompt",
        "duplicate_prompt",
    ]

    assert "pirate with a sword" in duplicate_findings[0].message
    assert "3" in duplicate_findings[0].message

    assert "pirate on a ship" in duplicate_findings[1].message
    assert "2" in duplicate_findings[1].message


def test_duplicate_rule_ignores_items_with_single_occurrence() -> None:
    simulation_result = SimulationResult(
        total_prompts=4,
        unique_prompts=3,
        duplicate_prompts=1,
        duplicate_items={
            "pirate with a sword": 2,
            "pirate on a ship": 1,
        },
    )

    findings = DuplicateRule().evaluate(simulation_result)

    assert len(findings) == 2
    assert "pirate with a sword" in findings[1].message
