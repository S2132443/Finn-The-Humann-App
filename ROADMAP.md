# ROADMAP

Single source of truth for planned work on Finn-The-Humann. Read this with the
rules in [CLAUDE.md](CLAUDE.md): the execution-order table below is the order of
work, not the inventory. Before claiming "X is all that remains in a phase", skim
that phase's whole section for Pending headings, including phases marked done.

Each substantive slice should get a spec in `docs/superpowers/specs/` (use
[TEMPLATE.md](docs/superpowers/specs/TEMPLATE.md)) before implementation, ending
in a verification checklist. Research findings, when requested, go in
`docs/superpowers/research/YYYY-MM-DD-topic.md` and are linked from the relevant
slice here.

## Execution Order

The order of work, not the inventory. Status: Pending, In Progress, Done.

| # | Phase | Next slice | Status |
|---|-------|------------|--------|
| 1 | A. Workflow and Hygiene Foundation | A1 Tooling config | Done |
| 2 | A. Workflow and Hygiene Foundation | A2 Remove dead code | Done |
| 3 | A. Workflow and Hygiene Foundation | A3 Config drift cleanup | Pending |
| 4 | A. Workflow and Hygiene Foundation | A4 Test harness | Pending |
| 5 | B. Automation | B1 Scheduled price updates | Pending |
| 6 | B. Automation | B2 Automated monthly snapshots | Pending |
| 7 | C. Data Ingestion | C1 CSV/Excel statement upload | Pending |
| 8 | D. Multi-User and Security | D1 Authentication | Pending |
| 9 | E. Advanced Analytics | E1 Performance attribution | Pending |

## Delivered Baseline (pre-roadmap)

State of the repo before this roadmap existed, captured so future sessions know
the starting point. Not work tracked here, just context.

- Single FastAPI service serving JSON API (`api/v1/`) and Jinja2 web UI (`web/`),
  sharing business logic in `services/`.
- Net worth, asset allocation vs SAA, TWRR, Modified Dietz (portfolio and
  per-asset-class), income tracking, yield, daily return series.
- Price refresh from LUNO and Yahoo Finance, exchange-rate updates, market and
  watchlist page, LUNO broker sync via an extensible provider pattern.
- Monthly snapshots, multi-currency conversion to MYR, PWA support.
- PostgreSQL schema in `database/init.sql` plus migrations 001 to 003.

## Phase A. Workflow and Hygiene Foundation

Groundwork that makes every later phase verifiable and keeps the repo aligned
with the rules in CLAUDE.md. Sourced from the gap analysis of 2026-06-16.

### A1 Tooling config (Done 2026-06-16)

Added `backend/pyproject.toml` configuring black (formatter) and ruff (lint-only)
at line length 88, target py311. Applied a one-time black baseline sweep over
`backend/app` in an isolated commit, recorded in `.git-blame-ignore-revs` so git
blame skips it. ruff cleanup of the 87 existing findings is incremental as files
are touched, not part of this slice. Spec:
[docs/superpowers/specs/2026-06-16-a1-tooling-config-design.md](docs/superpowers/specs/2026-06-16-a1-tooling-config-design.md).
Plan: [docs/superpowers/plans/2026-06-16-a1-tooling-config.md](docs/superpowers/plans/2026-06-16-a1-tooling-config.md).

### A2 Remove dead code (Done 2026-06-16)

Investigation showed the original premise was already handled by git: the
`frontend/` Python source had already been removed from the tracked tree (only
untracked `.pyc` bytecode lingered on disk), and no `__pycache__` or `.pyc` was
tracked anywhere (`.gitignore` already covers them). The only action was deleting
the untracked local bytecode, which has zero repository impact and needs no
commit. No spec or plan was warranted (Simplicity First).

Note for future architecture work: a separate, real JS frontend exists on the
`origin/gemini-frontend-test` branch (package.json, index.html, public assets).
It is unrelated to the dead Python bytecode removed here and must not be confused
with it. If a frontend direction is pursued, capture it as its own pending arc.

### A3 Config drift cleanup

Remove Flask leftovers from `.env.example` (`FLASK_ENV`, `API_BASE_URL`), correct
`CORS_ORIGINS` from the old port 5000 to 8000, and reconcile the exchange-rate
comment that claims rates are manual while the README says they auto-update.

### A4 Test harness

`pytest` and `pytest-asyncio` are already dependencies but no tests exist. Stand
up a `backend/tests/` layout with fixtures for a test database, then cover the
financial calculations in `services/calculations.py` first (TWRR, Modified Dietz,
net worth, exchange-rate conversion) since those are correctness-critical.

### Phase A Pending

- Decide whether to wire black and ruff into a pre-commit hook or CI once a CI
  pipeline exists. No CI is configured today.
- Restore or remove the missing `docs/images/dashboard-preview.png` referenced by
  the README.

## Phase B. Automation

### B1 Scheduled price updates

Automatic periodic price refresh (README roadmap notes APScheduler). Spec must
weigh APScheduler in-process against an external scheduler before deciding.

### B2 Automated monthly snapshots

Generate the monthly snapshot on a schedule rather than only via the manual
"Generate Snapshot" button.

### Phase B Pending

- No work captured beyond B1 and B2 yet.

## Phase C. Data Ingestion

### C1 CSV/Excel statement upload

Upload and parse brokerage or bank statements to reduce manual entry. Scope the
supported formats in the spec before building.

### Phase C Pending

- No work captured beyond C1 yet.

## Phase D. Multi-User and Security

### D1 Authentication

The app currently has no authentication; all financial data is open, and CORS
uses wildcard methods and headers with credentials allowed. Introduce auth and
tighten CORS. Multi-user data isolation follows once auth lands.

### Phase D Pending

- Multi-user data partitioning (account and asset ownership) once D1 lands.
- CORS hardening can ship with D1 or as its own slice if D1 slips.

## Phase E. Advanced Analytics

### E1 Performance attribution

Attribution analysis showing which holdings and asset classes drive returns
(README roadmap item).

### Phase E Pending

- No work captured beyond E1 yet.
