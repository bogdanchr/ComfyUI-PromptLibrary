# ComfyUI-PromptLibrary

Prompt library, Composer, Doctor, Preview, utilities and deterministic dependency rules for ComfyUI.

## Nodes

- **Prompt Library** — builds positive and negative prompts from a text library.
- **Prompt Library / Preview** — displays positive, negative and debug data.
- **Prompt Library / Doctor** — diagnoses and safely repairs library files.
- **Prompt Library / Builder** — optionally combines external prompt fragments.
- **Prompt Library / Utilities** — reloads the library and resets Unique history.

## Installation

Copy this repository to `ComfyUI/custom_nodes/ComfyUI-PromptLibrary`, install requirements, and restart ComfyUI.

```bash
pip install -r requirements.txt
```

Current version: **0.10.0 — Rules + Dependency Engine**.

## Rules quick start

Place one `rules.yaml` in a category folder, next to the prompt TXT files.

```yaml
entries:
  young explorer:
    requires:
      - fossil excavation site
    optional:
      - friendly dinosaur: 30
    exclude:
      - modern city

files:
  03_temat.txt:
    requires:
      - simple background

category:
  exclude:
    - photorealistic
```

Supported actions:

- `requires` — always adds a phrase,
- `optional` — adds it with a probability from 0 to 100,
- `replace` — replaces an exact fragment,
- `exclude` — removes an exact fragment.

Rules are exact and deterministic. PromptLibrary never guesses. Details are shown in the `debug` output and Prompt Preview.

## Reload Library

After editing TXT or YAML files, run:

`Prompt Library / Utilities → reload_library → execute = true`

Run the queue once, then return `execute` to `false`.
