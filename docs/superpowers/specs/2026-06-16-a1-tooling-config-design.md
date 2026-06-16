# Spec: A1 Tooling Config (black + ruff)

Roadmap slice: [ROADMAP.md](../../../ROADMAP.md) Phase A / A1
Status: Approved
Research: none

## Assumptions and Tradeoffs

Assumptions, stated before any code:

- The Python project lives entirely under `backend/`, with all source in
  `backend/app/`. There are no `.py` files elsewhere in `backend/`, so tooling
  scope is `backend/app/`.
- The runtime is Python 3.11 (confirmed by `.cpython-311` bytecode and the
  `python:3.11` Docker base), so both tools target py311.
- There are no tests yet (slice A4), so any auto-fix that can change behavior is
  unsafe right now. black is formatting-only and safe; ruff `--fix` is not.
- The project `CLAUDE.md` does not specify a line length, and the updated global
  guideline delegates line length to the project. 88 is chosen deliberately.

Decisions and why:

- **Line length 88, not 79.** 88 is black's native default and the dominant
  modern Python convention, so the formatter is never fought. Only 62 lines
  currently exceed 88 versus 148 over 79, so the baseline reformat stays small.
- **One-time black sweep, ruff incremental.** Introducing a formatter is the one
  moment a baseline reformat pays off: it keeps formatting noise out of every
  future feature diff. black is deterministic and changes no behavior. ruff
  findings are surfaced as warnings and cleaned up as files are touched, which
  avoids risky bulk auto-fixes before any tests exist.
- **Ruff rule set E, F, W, I.** pycodestyle errors and warnings, pyflakes (real
  bugs such as unused or undefined names), and isort (import ordering). Strong
  signal, low noise on existing code, trivially expandable later.
- **Single `pyproject.toml`, dev deps in `requirements.txt`.** Matches the
  existing convention where `pytest` already lives under a `# Development` block.
  One config file, one deps file, no new install step.

## Success Criteria

- [ ] `python -m black --check app` exits 0 from `backend/` (codebase is
  black-clean at line length 88).
- [ ] `python -m ruff check app` runs from `backend/` against the E/F/W/I rule
  set without a configuration error (findings are allowed at this stage).
- [ ] `pip install -r requirements.txt` installs black and ruff at the pinned
  versions.
- [ ] With the ignore-revs file active, `git blame` on a swept file attributes
  lines to their real authoring commit, not the formatting commit.

## Design

Minimum change to make the mandatory format-and-lint workflow enforceable.

### Files touched

- `backend/requirements.txt` : add `black` and `ruff` (pinned) under the existing
  `# Development` block, beside `pytest`.
- `backend/pyproject.toml` : new file, black and ruff configuration.
- `backend/app/**/*.py` : reformatted by the one-time black sweep, no behavior
  change.
- `.git-blame-ignore-revs` : new file at the repo root listing the formatting
  commit SHA so `git blame` skips it.

### Dependencies (`backend/requirements.txt`)

```
# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==24.10.0
ruff==0.8.4
```

### Config (`backend/pyproject.toml`)

```toml
[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # re-exports; unused-import is expected here
```

ruff is lint-only. No `[tool.ruff.format]` section, so black remains the sole
formatter and the two tools never fight. The `__init__.py` ignore covers the
deliberate re-exports in package inits.

### Execution sequence

Three small commits keep config and reformat separable and keep blame clean:

1. Add deps and `pyproject.toml`. No code reformatted.
   Message: `Add black and ruff tooling config (A1)`.
2. Run `python -m black app` from `backend/`, reformatting `backend/app/` only.
   Message: `Apply black formatting baseline (no behavior change)`.
3. Create `.git-blame-ignore-revs` at the repo root with commit 2's SHA.
   Message: `Add git blame ignore for formatting baseline`. Activate locally
   with `git config blame.ignoreRevsFile .git-blame-ignore-revs`; GitHub detects
   the file automatically.

## Out of Scope

- ruff `--fix` and clearing existing lint findings (incremental as files are
  touched in later work).
- mypy, bandit, and pylint static analysis (possible future slice).
- pre-commit hooks and CI enforcement; no CI exists yet, tracked under Phase A
  Pending in ROADMAP.md.
- Any line still over 88 after black (black leaves long strings and comments
  alone); these are handled when the surrounding code is next touched.

## Verification Checklist

- [ ] **KISS:** One config file and two pinned deps; no scripts, wrappers, or
  abstractions added.
- [ ] **DRY:** Line length and target version are the single source for each
  tool; dev deps live in the one existing `# Development` block, not duplicated.
- [ ] **Modular:** Tooling config is self-contained in `pyproject.toml` and can
  be removed without touching application code.
- [ ] **Scalable:** Rule set and tool list expand by editing one file; nothing
  hard-codes per-file behavior beyond the documented `__init__.py` ignore.
- [ ] **Architecture invariants:** No application code logic changes; the single
  FastAPI service, `services/` reuse, and API/web split are untouched.
- [ ] **Standards:** black and ruff configured for modified-file workflow going
  forward; line length 88; no em-dashes in added files.
- [ ] **Tests:** No behavior change to test; `black --check` and `ruff check`
  serve as the objective verification for this slice.
- [ ] **Success criteria above are all met and were verified, not assumed.**
