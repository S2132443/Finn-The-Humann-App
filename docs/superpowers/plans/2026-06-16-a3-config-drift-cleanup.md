# A3 Config Drift Cleanup and Railway Removal Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove dead/stale config from the env templates and `config.py`, make LUNO keys reach the Docker backend, and delete all Railway artifacts and mentions.

**Architecture:** A set of surgical edits and file deletions. No application logic changes. Verification is by import check, repo-wide `railway` grep, file-absence checks, and `docker compose config` parsing.

**Tech Stack:** Python 3.11 (deploy target), Docker Compose, git.

Spec: [docs/superpowers/specs/2026-06-16-a3-config-drift-cleanup-design.md](../specs/2026-06-16-a3-config-drift-cleanup-design.md)

**Conventions:** Repo root is `C:\Projects\Finn-The-Humann-App`. Run `python` commands from `backend/`. Branch is `dev`. No AI-attribution trailer in commit messages. No em-dashes in any file.

---

## Task 1: Config cleanup

**Files:**
- Modify: `.env.example` (repo root)
- Modify: `backend/app/config.py` (line 25)
- Modify: `docker-compose.yml` (backend service `environment:` block)

- [ ] **Step 1: Rewrite `.env.example`**

Replace the ENTIRE contents of `.env.example` with exactly this (drops the API, Flask, and Exchange Rates sections; keeps database, application, and LUNO):
```
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=finn_db

# Application Configuration
SECRET_KEY=your-secret-key-change-in-production
BASE_CURRENCY=MYR
DEBUG=false

# LUNO API (optional - for auto-importing crypto balances)
# Generate read-only API keys at: https://www.luno.com/wallet/security/api_keys
LUNO_API_KEY_ID=
LUNO_API_KEY_SECRET=
```

- [ ] **Step 2: Fix the CORS_ORIGINS default in `backend/app/config.py`**

Find this line (line 25):
```python
    CORS_ORIGINS: list = ["http://localhost:5000", "http://127.0.0.1:5000"]
```
Replace it with:
```python
    CORS_ORIGINS: list = ["http://localhost:8000", "http://127.0.0.1:8000"]
```

- [ ] **Step 3: Pass LUNO keys to the backend container in `docker-compose.yml`**

In the `backend` service `environment:` block, which currently reads:
```yaml
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-password}@db:5432/${POSTGRES_DB:-finn_db}
      SECRET_KEY: ${SECRET_KEY:-your-secret-key-change-in-production}
      BASE_CURRENCY: ${BASE_CURRENCY:-MYR}
      DEBUG: ${DEBUG:-false}
```
add the two LUNO lines so it becomes:
```yaml
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD:-password}@db:5432/${POSTGRES_DB:-finn_db}
      SECRET_KEY: ${SECRET_KEY:-your-secret-key-change-in-production}
      BASE_CURRENCY: ${BASE_CURRENCY:-MYR}
      DEBUG: ${DEBUG:-false}
      LUNO_API_KEY_ID: ${LUNO_API_KEY_ID:-}
      LUNO_API_KEY_SECRET: ${LUNO_API_KEY_SECRET:-}
```

- [ ] **Step 4: Verify config still imports with the new CORS value**

Run from `backend/`:
```
python -c "from app.config import settings; print(settings.CORS_ORIGINS)"
```
Expected: prints `['http://localhost:8000', 'http://127.0.0.1:8000']` with no import error. If `pydantic_settings` is not installed in this environment, fall back to a syntax check: `python -m py_compile app/config.py` (expect exit 0).

- [ ] **Step 5: Verify `.env.example` is clean**

Run from repo root:
```
grep -E "API_BASE_URL|FLASK_ENV|_TO_MYR" .env.example || echo "CLEAN"
```
Expected: `CLEAN` (no matches).

- [ ] **Step 6: Verify docker-compose still parses (if docker is available)**

Run from repo root:
```
docker compose config >/dev/null && echo "COMPOSE OK"
```
Expected: `COMPOSE OK`. If the `docker` CLI is not available in this environment, skip this step and note it was skipped.

- [ ] **Step 7: Commit**

Run from repo root:
```
git add .env.example backend/app/config.py docker-compose.yml
git commit -m "Clean dead config and pass LUNO keys to docker backend (A3)"
```

---

## Task 2: Remove all Railway artifacts and mentions

**Files:**
- Delete: `.env.railway.example` (repo root)
- Delete: `.railwayignore` (repo root)
- Delete: `backend/railway.toml`
- Modify: `backend/Dockerfile` (lines 18 and 22 comments)

- [ ] **Step 1: Delete the three Railway files**

Run from repo root:
```
git rm .env.railway.example .railwayignore backend/railway.toml
```
Expected: git reports the three files removed.

- [ ] **Step 2: Strip the Railway comments from `backend/Dockerfile`**

The file currently ends with:
```dockerfile
# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Run the application
# Railway sets PORT environment variable, default to 8000 for local dev
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```
Replace that block with (neutral comments, behavior unchanged):
```dockerfile
# Expose the application port
EXPOSE 8000

# Run the application (honors PORT if set, defaults to 8000)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

- [ ] **Step 3: Verify no Railway mentions remain anywhere**

Run from repo root:
```
grep -ri railway . --exclude-dir=.git || echo "NO RAILWAY"
```
Expected: `NO RAILWAY` (no matches).

- [ ] **Step 4: Verify the three files are gone**

Run from repo root:
```
ls .env.railway.example .railwayignore backend/railway.toml 2>&1 | grep -c "No such" 
```
Expected: `3` (all three report "No such file").

- [ ] **Step 5: Commit**

Run from repo root:
```
git add backend/Dockerfile
git commit -m "Remove all Railway artifacts and mentions (A3)"
```
Note: the `git rm` from Step 1 is already staged; this commit includes both the deletions and the Dockerfile edit.

---

## Task 3: Final verification and mark done

- [ ] **Step 1: Re-run all success-criteria checks**

From repo root:
```
grep -E "API_BASE_URL|FLASK_ENV|_TO_MYR" .env.example || echo "ENV CLEAN"
grep -ri railway . --exclude-dir=.git || echo "NO RAILWAY"
ls .env.railway.example .railwayignore backend/railway.toml 2>&1 | grep -c "No such"
```
From `backend/`:
```
python -c "from app.config import settings; print(settings.CORS_ORIGINS)"
```
Expected: `ENV CLEAN`, `NO RAILWAY`, `3`, and the CORS list on port 8000 (or `py_compile` clean if pydantic_settings is missing).

- [ ] **Step 2: Tick the spec verification checklist and mark A3 done**

In `docs/superpowers/specs/2026-06-16-a3-config-drift-cleanup-design.md`, change every `- [ ]` to `- [x]` and set `Status: Implemented`.

In `ROADMAP.md`, set the A3 row in the execution-order table to `Done`, and update the `### A3 Config drift cleanup` section to a "Done 2026-06-16" note summarizing what changed (dead config removed, CORS fixed to 8000, LUNO passed to Docker, all Railway removed), linking the spec and this plan.

- [ ] **Step 3: Commit**

Run from repo root:
```
git add ROADMAP.md docs/superpowers/specs/2026-06-16-a3-config-drift-cleanup-design.md
git commit -m "Mark A3 config drift cleanup done"
```
