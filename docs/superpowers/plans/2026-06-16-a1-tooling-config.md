# A1 Tooling Config Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the mandatory format-and-lint workflow enforceable by adding black and ruff config, applying a one-time black baseline, and keeping git blame clean.

**Architecture:** Add pinned dev dependencies and a single `backend/pyproject.toml` configuring black (formatter) and ruff (lint-only) at line length 88. Reformat `backend/app/` once with black in an isolated commit, then record that commit in `.git-blame-ignore-revs` so blame skips the reformat.

**Tech Stack:** Python 3.11, black 24.10.0, ruff 0.8.4, git.

Spec: [docs/superpowers/specs/2026-06-16-a1-tooling-config-design.md](../specs/2026-06-16-a1-tooling-config-design.md)

**Conventions for every command below:** run from the `backend/` directory unless stated otherwise. The repo root is the parent of `backend/`. On Windows PowerShell, `python -m <tool>` form is used so it works regardless of Scripts on PATH.

---

## Task 1: Add dependencies and tooling config

**Files:**
- Modify: `backend/requirements.txt` (the `# Development` block near the end)
- Create: `backend/pyproject.toml`

- [ ] **Step 1: Install the two tools into the active environment**

Run (from `backend/`):
```
python -m pip install black==24.10.0 ruff==0.8.4
```
Expected: both install successfully. Confirm with:
```
python -m black --version
python -m ruff --version
```
Expected: `black, 24.10.0` and `ruff 0.8.4`.

- [ ] **Step 2: Add the tools to requirements.txt**

In `backend/requirements.txt`, the `# Development` block currently reads:
```
# Development
pytest==7.4.3
pytest-asyncio==0.21.1
```
Change it to:
```
# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==24.10.0
ruff==0.8.4
```

- [ ] **Step 3: Create `backend/pyproject.toml`**

Create the file with exactly this content:
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

- [ ] **Step 4: Verify ruff loads the config and runs**

Run (from `backend/`):
```
python -m ruff check app
```
Expected: ruff runs without a configuration error. It may print lint findings or "All checks passed!"; either is acceptable. A TOML parse error or "unknown rule" message means the config is wrong and must be fixed before continuing.

- [ ] **Step 5: Verify black sees the config and reports the baseline**

Run (from `backend/`):
```
python -m black --check app
```
Expected: exit code 1 with a list of files that "would be reformatted". This is expected at this stage (the sweep happens in Task 2). Confirm the reported count is in the same ballpark as the known baseline (about 30 files). If black reports "All done" with 0 files, the config or path is wrong.

- [ ] **Step 6: Commit**

Run (from repo root):
```
git add backend/requirements.txt backend/pyproject.toml
git commit -m "Add black and ruff tooling config (A1)"
```
Note: do not add an AI-attribution trailer (per the repo "Match the Repo" rule).

---

## Task 2: Apply the black baseline sweep

**Files:**
- Modify: `backend/app/**/*.py` (reformatted by black, no behavior change)

- [ ] **Step 1: Capture a pre-sweep smoke check**

Run (from `backend/`):
```
python -c "import app.main"
```
Expected: it imports without error (this is the behavior baseline we must preserve). If it fails here due to a missing DATABASE_URL or similar, instead use a syntax-only baseline:
```
python -m compileall -q app
```
Expected: exit code 0 (all files compile). Record which check you used; the same check is repeated in Step 3.

- [ ] **Step 2: Run the black sweep**

Run (from `backend/`):
```
python -m black app
```
Expected: black prints "reformatted ..." lines and a summary like "N files reformatted, M files left unchanged".

- [ ] **Step 3: Verify no behavior change via the same smoke check**

Run the identical check chosen in Step 1 (from `backend/`):
```
python -c "import app.main"
```
or
```
python -m compileall -q app
```
Expected: same successful result as Step 1. black is formatting-only, so this must still pass.

- [ ] **Step 4: Verify black-clean**

Run (from `backend/`):
```
python -m black --check app
```
Expected: exit code 0, "All done!" with 0 files that would be reformatted.

- [ ] **Step 5: Commit the reformat in isolation**

Run (from repo root):
```
git add backend/app
git commit -m "Apply black formatting baseline (no behavior change)"
```
This commit must contain only formatting changes. Do not bundle any other edit into it, because its SHA is recorded for blame-skipping in Task 3.

---

## Task 3: Keep git blame clean

**Files:**
- Create: `.git-blame-ignore-revs` (repo root)

- [ ] **Step 1: Capture the formatting commit SHA**

Run (from repo root):
```
git rev-parse HEAD
```
Expected: the full 40-character SHA of the "Apply black formatting baseline" commit from Task 2 Step 5. Copy it.

- [ ] **Step 2: Create `.git-blame-ignore-revs` at the repo root**

Create the file with this content, replacing the placeholder with the SHA from Step 1:
```
# Formatting-only commits to skip in git blame.
# Activate locally: git config blame.ignoreRevsFile .git-blame-ignore-revs
# Apply black formatting baseline (A1)
<PASTE_FULL_SHA_HERE>
```

- [ ] **Step 3: Activate it locally**

Run (from repo root):
```
git config blame.ignoreRevsFile .git-blame-ignore-revs
```
Expected: no output, exit code 0.

- [ ] **Step 4: Verify blame skips the formatting commit**

Pick a file that was reformatted (for example `backend/app/main.py`). Run (from repo root):
```
git blame backend/app/main.py
```
Expected: the leftmost commit SHAs are the real authoring commits, not the formatting commit SHA from Step 1. If lines still attribute to the formatting commit, the ignore file or the `git config` setting is wrong.

- [ ] **Step 5: Commit**

Run (from repo root):
```
git add .git-blame-ignore-revs
git commit -m "Add git blame ignore for formatting baseline"
```

---

## Task 4: Final verification against the spec success criteria

- [ ] **Step 1: black-clean**

Run (from `backend/`): `python -m black --check app`
Expected: exit code 0.

- [ ] **Step 2: ruff runs against E/F/W/I**

Run (from `backend/`): `python -m ruff check app`
Expected: runs without config error (findings allowed).

- [ ] **Step 3: deps install cleanly**

Run (from `backend/`): `python -m pip install -r requirements.txt`
Expected: black 24.10.0 and ruff 0.8.4 are present (already satisfied).

- [ ] **Step 4: blame attributes real authors**

Run (from repo root): `git blame backend/app/main.py | head`
Expected: real authoring commits shown, not the formatting commit.

- [ ] **Step 5: Tick the spec verification checklist**

Open the spec and confirm every box in its Verification Checklist is satisfied by the work above. Update ROADMAP.md to mark slice A1 Done (move its status in the execution-order table and note completion in the Phase A section, per the ROADMAP rules). Commit:
```
git add ROADMAP.md docs/superpowers/specs/2026-06-16-a1-tooling-config-design.md
git commit -m "Mark A1 tooling config done"
```
