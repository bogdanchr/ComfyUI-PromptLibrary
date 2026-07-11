# Changelog

## 0.10.0 — Rules + Dependency Engine

- Added `rules.yaml` support per category.
- Added entry, file and category rule scopes.
- Added `requires`, `optional`, `replace` and `exclude` actions.
- Added deterministic optional selection based on the Prompt Library seed.
- Added rule activity to the debug output and Prompt Preview.
- Added `examples/rules.yaml` and `docs/RULES.md`.
- Added PyYAML as the only external dependency.
- Added end-to-end tests for rule parsing and execution.

## 0.8.0 — Prompt Composer

- Added natural joining of `01_character.txt` and `02_typ_postaci.txt`.
- Removed direct word overlap such as `cute` + `cute preschool girl`.

## 0.7.0 — Reload Library

- Added full `reload_library` action in Utilities.


## 0.10.0 — Prompt Doctor Quality

- Added local quality analysis without AI or internet access.
- Detects similar entries, cross-file duplicates, likely wrong categories, thematic conflicts and library imbalance.
- Provides conservative rules.yaml suggestions.
- Added `quality_check` and `full_diagnosis` Doctor actions.
