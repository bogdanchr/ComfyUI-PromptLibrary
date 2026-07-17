from prompt_library.doctor import DoctorFinding, DoctorResult, Severity


def make_finding(
    code: str,
    severity: Severity,
) -> DoctorFinding:
    return DoctorFinding(
        code=code,
        severity=severity,
        title=f"Finding {code}",
        message=f"Message for {code}",
    )


def test_doctor_result_starts_empty() -> None:
    result = DoctorResult()

    assert result.findings == []
    assert result.total_findings == 0
    assert result.error_count == 0
    assert result.warning_count == 0
    assert result.info_count == 0


def test_doctor_result_groups_findings_by_severity() -> None:
    error = make_finding("error_1", Severity.ERROR)
    warning = make_finding("warning_1", Severity.WARNING)
    info = make_finding("info_1", Severity.INFO)

    result = DoctorResult(
        findings=[
            error,
            warning,
            info,
        ]
    )

    assert result.errors == [error]
    assert result.warnings == [warning]
    assert result.infos == [info]


def test_doctor_result_counts_findings() -> None:
    result = DoctorResult(
        findings=[
            make_finding("error_1", Severity.ERROR),
            make_finding("error_2", Severity.ERROR),
            make_finding("warning_1", Severity.WARNING),
            make_finding("info_1", Severity.INFO),
        ]
    )

    assert result.total_findings == 4
    assert result.error_count == 2
    assert result.warning_count == 1
    assert result.info_count == 1


def test_doctor_result_adds_single_finding() -> None:
    result = DoctorResult()
    finding = make_finding("warning_1", Severity.WARNING)

    result.add(finding)

    assert result.findings == [finding]


def test_doctor_result_extends_multiple_findings() -> None:
    result = DoctorResult()

    findings = [
        make_finding("error_1", Severity.ERROR),
        make_finding("info_1", Severity.INFO),
    ]

    result.extend(findings)

    assert result.findings == findings
