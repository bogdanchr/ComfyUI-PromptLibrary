# Prompt Library

Główny node do codziennego generowania promptów z biblioteki tekstowej.

## Szybki start

1. Wskaż `root_folder`.
2. Wybierz `category`.
3. Wybierz `mode`.
4. Podłącz `positive` i `negative` do odpowiednich wejść enkodera tekstu.

## Tryby

- **random** — losowy wpis.
- **sequential** — kolejne wpisy.
- **weighted** — losowanie według wag zapisanych w bibliotece.
- **unique** — bez powtórek, dopóki nie zresetujesz historii w Utilities.

## Wyjścia

- **positive** — gotowy prompt pozytywny.
- **negative** — treść `negative.txt`.
- **debug** — informacje o wybranych plikach i wpisach.
- **category** — użyta kategoria.
- **files_count** — liczba użytych plików.
