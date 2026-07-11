# PromptLibrary V2 Roadmap

## Vision

PromptLibrary V2 turns the project from a prompt generator into a complete environment for designing, testing, analysing, and improving prompt libraries.

V2 should remain:
- local-first,
- predictable,
- safe,
- modular,
- optional where AI is involved.

PromptLibrary must never change user files without explicit confirmation.

---

## V2 Goals

### 2.1 — Prompt Simulation

Generate hundreds or thousands of prompts without running an image model.

Planned features:
- choose category,
- choose simulation size,
- use the current selection mode,
- apply Rules and Dependency Engine,
- detect repeated prompts,
- detect conflicts,
- measure entry usage,
- measure rule usage,
- report unused entries,
- export results to TXT, CSV, or JSON.

Example report:

```text
Simulation: 1000 prompts

Unique prompts: 998
Duplicates: 2
Conflicts: 6
Unused entries: 4
Rules triggered: 317
Coverage: 96%
```

---

### 2.2 — Rule Builder

Create and edit `rules.yaml` visually.

Planned features:
- select an entry from the library,
- add `requires`,
- add `optional`,
- add `exclude`,
- add `replace`,
- preview the resulting YAML,
- validate before saving,
- create a backup before every change.

The user should not need to edit YAML manually.

---

### 2.3 — Safe Auto Fix

Apply selected fixes proposed by Prompt Doctor.

Planned fixes:
- remove exact duplicates,
- remove blank lines,
- normalize spaces and punctuation,
- create missing files,
- merge selected similar entries,
- add approved rules,
- move selected entries to a better category.

Rules:
- no silent changes,
- every fix must be selected by the user,
- every changed file must be backed up,
- a preview must be shown before saving.

---

### 2.4 — AI Doctor

Optional AI-assisted analysis for users who choose to enable it.

Possible providers:
- OpenAI API,
- OpenRouter,
- Ollama,
- other local LLM endpoints.

Planned tasks:
- suggest cleaner wording,
- detect thematic conflicts,
- suggest missing categories,
- suggest rules,
- suggest better balance,
- explain why a combination may be weak.

Safety and privacy:
- disabled by default,
- clearly show what data will be sent,
- allow local-only operation with Ollama,
- never modify files automatically,
- API keys must never be stored in workflow files.

---

### 2.5 — Statistics and Analytics

Provide a clear overview of the library.

Planned metrics:
- entries per file,
- category balance,
- most and least used entries,
- unused entries,
- rule activation frequency,
- prompt length distribution,
- duplicate rate,
- semantic similarity groups,
- simulation coverage.

---

### 2.6 — Prompt Optimizer

Improve prompt readability without changing meaning.

Planned features:
- remove repeated adjectives,
- detect redundant phrases,
- improve ordering,
- merge compatible fragments,
- suggest shorter alternatives,
- preserve original prompt as a comparison.

---

### 2.7 — Library Manager

Manage Prompt Packages from one place.

Planned features:
- import ZIP,
- export ZIP,
- create a new Prompt Package,
- clone a category,
- rename safely,
- validate package structure,
- show package metadata,
- support `library.yaml`,
- preserve compatibility with plain TXT libraries.

---

## Suggested Development Order

### Phase 1 — Analysis

1. Prompt Simulation
2. Statistics
3. Coverage and unused-entry reporting

### Phase 2 — Editing

4. Rule Builder
5. Safe Auto Fix
6. Library Manager

### Phase 3 — Intelligence

7. Prompt Optimizer
8. AI Doctor
9. Optional local LLM support

---

## Out of Scope for V2

The following are deliberately excluded:

- image generation,
- model downloading,
- LoRA management,
- sampler management,
- workflow editing,
- cloud marketplace,
- automatic background services,
- mandatory online accounts.

These may be considered for later versions only if they support the core purpose of PromptLibrary.

---

## V2 Design Rules

1. V1 workflows must remain compatible.
2. AI must always be optional.
3. No file may be changed without confirmation.
4. Every write operation must create a backup.
5. Reports must distinguish errors, warnings, and suggestions.
6. Local analysis should be preferred whenever possible.
7. One release should focus on one major feature.
8. New features must simplify real work, not only add options.

---

## Proposed Version Plan

```text
2.0.0-alpha.1  Prompt Simulation foundation
2.0.0-alpha.2  Statistics and coverage
2.0.0-alpha.3  Rule Builder
2.0.0-beta.1   Safe Auto Fix
2.0.0-beta.2   Library Manager
2.0.0-beta.3   Prompt Optimizer
2.0.0-rc.1     AI Doctor and local LLM integration
2.0.0          Stable V2 release
```

---

## Definition of Done for V2

PromptLibrary V2 is complete when a user can:

1. build a prompt library,
2. validate it,
3. simulate thousands of prompts,
4. find unused or conflicting entries,
5. create rules without editing YAML,
6. apply selected fixes safely,
7. optionally ask an AI for suggestions,
8. export the complete library as a portable package.
