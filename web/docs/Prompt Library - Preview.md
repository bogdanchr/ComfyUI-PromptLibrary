# Prompt Library / Preview

Własny, czytelny podgląd tekstu generowanego przez PromptLibrary.

## Podłączenie

- `positive` — podłącz wyjście `positive` z Prompt Library lub Buildera,
- `negative` — opcjonalnie wyjście `negative`,
- `debug` — opcjonalnie wyjście `debug`.

Po uruchomieniu workflow node pokazuje trzy oddzielne sekcje oraz podstawową statystykę długości tekstu.

Wyjścia `positive`, `negative` i `debug` są przekazywane bez zmian, więc Preview może stać również pomiędzy Prompt Library a kolejnymi node’ami.
