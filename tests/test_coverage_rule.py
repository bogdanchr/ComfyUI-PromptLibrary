from prompt_library.doctor import CoverageRule, Severity
from prompt_library.simulation import SimulationResult
from prompt_library.simulation.coverage import (
    CategoryCoverage,
    FileCoverage,
)


def test_coverage_rule_contains_metadata() -> None:
    rule = CoverageRule()

    assert rule.rule_id == "coverage"
    assert rule.name == "Category coverage"
    assert rule.description


def test_coverage_rule_returns_no_findings_for_full_coverage() -> None:
    simulation_result = SimulationResult(
        category_coverage=CategoryCoverage(
            files={
                "01_character.txt": FileCoverage(
                    total_entries=3,
                    used_entries=3,
                    coverage_percent=100.0,
                    unused_entries=(),
                )
            },
            total_entries=3,
            used_entries=3,
            coverage_percent=100.0,
            unused_entries={},
        )
    )

    findings = CoverageRule().evaluate(simulation_result)

    assert findings == []


def test_coverage_rule_reports_incomplete_category_coverage() -> None:
    simulation_result = SimulationResult(
        category_coverage=CategoryCoverage(
            total_entries=10,
            used_entries=8,
            coverage_percent=80.0,
        )
    )

    findings = CoverageRule().evaluate(simulation_result)

    assert len(findings) == 1

    finding = findings[0]

    assert finding.code == "incomplete_category_coverage"
    assert finding.severity is Severity.WARNING
    assert "80.0%" in finding.message
    assert finding.suggestion


def test_coverage_rule_reports_unused_entries_for_file() -> None:
    simulation_result = SimulationResult(
        category_coverage=CategoryCoverage(
            files={
                "02_action.txt": FileCoverage(
                    total_entries=4,
                    used_entries=2,
                    coverage_percent=50.0,
                    unused_entries=(
                        "biegnie",
                        "skacze",
                    ),
                )
            },
            total_entries=4,
            used_entries=2,
            coverage_percent=50.0,
            unused_entries={
                "02_action.txt": (
                    "biegnie",
                    "skacze",
                )
            },
        )
    )

    findings = CoverageRule().evaluate(simulation_result)

    assert len(findings) == 2

    file_finding = findings[1]

    assert file_finding.code == "unused_file_entries"
    assert file_finding.severity is Severity.WARNING
    assert file_finding.filename == "02_action.txt"
    assert "2" in file_finding.message
    assert "biegnie" in file_finding.suggestion
    assert "skacze" in file_finding.suggestion


def test_coverage_rule_reports_each_file_with_unused_entries() -> None:
    simulation_result = SimulationResult(
        category_coverage=CategoryCoverage(
            files={
                "01_character.txt": FileCoverage(
                    total_entries=2,
                    used_entries=1,
                    coverage_percent=50.0,
                    unused_entries=("pirat",),
                ),
                "02_action.txt": FileCoverage(
                    total_entries=2,
                    used_entries=1,
                    coverage_percent=50.0,
                    unused_entries=("biegnie",),
                ),
            },
            total_entries=4,
            used_entries=2,
            coverage_percent=50.0,
            unused_entries={
                "01_character.txt": ("pirat",),
                "02_action.txt": ("biegnie",),
            },
        )
    )

    findings = CoverageRule().evaluate(simulation_result)

    assert len(findings) == 3
    assert [finding.filename for finding in findings[1:]] == [
        "01_character.txt",
        "02_action.txt",
    ]
