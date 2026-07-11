# Rules + Dependency Engine 0.9

Place one `rules.yaml` inside a category folder.

Supported levels, from lowest to highest priority:

1. `category`
2. `files`
3. `entries`

Supported actions:

- `requires` — always adds a phrase.
- `optional` — adds a phrase with a probability from 0 to 100.
- `replace` — replaces an exact prompt fragment.
- `exclude` — removes an exact prompt fragment.

Execution order: `requires` → `optional` → `replace` → `exclude`.
PromptLibrary never guesses; only exact configured rules are executed.
