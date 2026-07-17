from dataclasses import dataclass, field

from .finding import DoctorFinding, Severity


@dataclass(slots=True)
class DoctorResult:
	"""Zbiorczy wynik analizy Prompt Doctora."""

	findings: list[DoctorFinding] = field(default_factory=list)

	@property
	def total_findings(self) -> int:
		return len(self.findings)

	@property
	def errors(self) -> list[DoctorFinding]:
		return [
			finding
			for finding in self.findings
			if finding.severity is Severity.ERROR
		]

	@property
	def warnings(self) -> list[DoctorFinding]:
		return [
			finding
			for finding in self.findings
			if finding.severity is Severity.WARNING
		]

	@property
	def infos(self) -> list[DoctorFinding]:
		return [
			finding
			for finding in self.findings
			if finding.severity is Severity.INFO
		]

	@property
	def error_count(self) -> int:
		return len(self.errors)

	@property
	def warning_count(self) -> int:
		return len(self.warnings)

	@property
	def info_count(self) -> int:
		return len(self.infos)

	def add(self, finding: DoctorFinding) -> None:
		self.findings.append(finding)

	def extend(self, findings: list[DoctorFinding]) -> None:
		self.findings.extend(findings)

