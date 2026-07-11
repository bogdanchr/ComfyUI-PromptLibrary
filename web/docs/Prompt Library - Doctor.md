# Prompt Library / Doctor

Prompt Doctor diagnozuje bibliotekę i pokazuje dokładnie, gdzie znajduje się problem.

## Bezpieczny start

1. Ustaw `action` na `diagnose`.
2. Ustaw `validate` na `true`.
3. Uruchom kolejkę i przeczytaj wyjście `report`.

## Akcje

- `diagnose` — tylko raport, bez zmian.
- `fix_duplicates_blank_lines` — usuwa powtórzone aktywne wpisy i puste linie.
- `create_missing_files` — tworzy brakujące `style.txt` i `negative.txt` z komentarzem, bez aktywnych promptów.
- `fix_all_safe` — wykonuje obie bezpieczne naprawy.

Przed zmianą istniejących plików Doctor tworzy kopię w:

```text
.promptlibrary_backups/RRRRMMDD-GGMMSS/
```

Nieprawidłowe wagi nie są poprawiane automatycznie, ponieważ wymagają decyzji użytkownika.


## Quality actions

- `quality_check` — checks wording, similarity, thematic consistency, balance and rule opportunities. It never changes files.
- `full_diagnosis` — combines technical diagnosis with the quality report.

Quality findings are suggestions, not automatic fixes.
