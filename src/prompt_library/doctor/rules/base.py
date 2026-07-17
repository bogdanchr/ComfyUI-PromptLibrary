from abc import ABC, abstractmethod

from prompt_library.simulation import SimulationResult

from ..finding import DoctorFinding


class DoctorRule(ABC):
	"""Wspólny interfejs wszystkich reguł Prompt Doctora."""

	@property
	@abstractmethod
	def name(self) -> str:
		"""Czytelna nazwa reguły."""

	@abstractmethod
	def evaluate(
		self,
		simulation_result: SimulationResult,
	) -> list[DoctorFinding]:
		"""Analizuje wynik symulacji i zwraca diagnozy."""

