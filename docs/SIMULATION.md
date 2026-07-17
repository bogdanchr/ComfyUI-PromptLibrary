# Prompt Simulation

Moduł Prompt Simulation testuje bibliotekę promptów przez wielokrotne
generowanie kombinacji i zbieranie statystyk.

## Główne możliwości

- liczba wygenerowanych promptów,
- liczba unikalnych promptów,
- wykrywanie duplikatów,
- statystyki długości promptów,
- pokrycie wpisów w plikach,
- pokrycie całej przestrzeni wyszukiwania,
- statystyki użycia wpisów,
- fingerprint biblioteki,
- sprawdzanie struktury kategorii,
- raport tekstowy.

## Przykład użycia

```python
from pathlib import Path

from prompt_library.simulation import Simulation


library_root = Path("ścieżka/do/biblioteki")

simulation = Simulation(library_root)

result = simulation.run(
    category="MAŁE DINOZAURY",
    iterations=10_000,
    seed=1234,
)

print(simulation.report(result))
```