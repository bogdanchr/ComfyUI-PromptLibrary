
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
	"""Poziom ważności diagnozy Prompt Doctora."""

	INFO = "info"
	WARNING = "warning"
	ERROR = "error"


@dataclass(frozen=True, slots=True)
class DoctorFinding:
	"""Pojedynczy problem lub informacja wykryta przez Prompt Doctora."""

	code: str
	severity: Severity
	title: str
	message: str
	category: str | None = None
	filename: str | None = None
	suggestion: str | None = None

