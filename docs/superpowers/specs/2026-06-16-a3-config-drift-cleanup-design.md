# Spec: A3 Config Drift Cleanup and Railway Removal

Roadmap slice: [ROADMAP.md](../../../ROADMAP.md) Phase A / A3
Status: Approved
Research: none

## Assumptions and Tradeoffs

Assumptions, verified against actual consumption before writing:

- `API_BASE_URL` and `FLASK_ENV` are not read by any code or by
  `docker-compose.yml`. They are Flask two-service leftovers.
- The `USD_TO_MYR/SGD/EUR/GBP` env vars in the env templates are not read by any
  code. Exchange rates live in the `Currency` DB table and are refreshed by the
  live API in `app/services/price_fetcher.py`. The accompanying comment that
  promises a "future" API integration is wrong; that integration already exists.
- `CORS_ORIGINS` in `config.py` defaults to port 5000 (Flask), but the app runs
  on 8000. The web UI is served same-origin so the value is currently inert, but
  it is drifted and should reflect reality.
- `docker-compose.yml` does not pass `LUNO_API_KEY_ID/SECRET` to the backend
  container, so the documented LUNO sync cannot work under Docker even when the
  keys are set in `.env`.
- Railway is being abandoned. All Railway artifacts and textual mentions are
  removed. The `${PORT:-8000}` default in the Dockerfile is kept because it is
  generic and behaves identically (defaults to 8000) when no PORT is set.

Decisions and why:

- **Fix `CORS_ORIGINS` value only, defer hardening to D1.** Correcting the stale
  port is drift cleanup. Changing wildcard methods/headers, `allow_credentials`,
  or making origins env-configurable is a security concern owned by D1.
- **Delete, do not rewrite, the Railway files.** The user is not using Railway,
  so a single-service rewrite of `.env.railway.example` would be dead
  documentation. Deletion is simpler (KISS).
- **Add LUNO vars to compose with empty defaults.** `${LUNO_API_KEY_ID:-}` keeps
  the app working without keys (the feature is optional) while making the
  documented Docker path functional when keys are provided.

## Success Criteria

- [ ] `.env.example` contains no `API_BASE_URL`, no `FLASK_ENV`, and no
  `*_TO_MYR` exchange-rate vars or the related "MVP/future" comment.
- [ ] `app/config.py` `CORS_ORIGINS` default uses port 8000, not 5000.
- [ ] `docker-compose.yml` backend service passes `LUNO_API_KEY_ID` and
  `LUNO_API_KEY_SECRET` with empty defaults.
- [ ] `grep -ri railway` over the repository (excluding `.git`) returns nothing.
- [ ] `.env.railway.example`, `.railwayignore`, and `backend/railway.toml` no
  longer exist.
- [ ] `python -c "import app.config"` loads without error.

## Design

A set of surgical edits and file deletions. No application logic changes.

### Files touched

- `.env.example` : remove dead `API_BASE_URL`, `FLASK_ENV`, and the exchange-rate
  block with its comment. Keep `POSTGRES_*`, `SECRET_KEY`, `BASE_CURRENCY`,
  `DEBUG`, and the `LUNO_*` block.
- `backend/app/config.py` : change the `CORS_ORIGINS` default from
  `["http://localhost:5000", "http://127.0.0.1:5000"]` to
  `["http://localhost:8000", "http://127.0.0.1:8000"]`.
- `docker-compose.yml` : add to the `backend` service `environment:` block:
  `LUNO_API_KEY_ID: ${LUNO_API_KEY_ID:-}` and
  `LUNO_API_KEY_SECRET: ${LUNO_API_KEY_SECRET:-}`.
- `backend/Dockerfile` : remove the two Railway-referencing comments (the
  `EXPOSE` comment and the `CMD` comment); keep `EXPOSE 8000` and
  `CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` with neutral
  comments.
- Delete: `.env.railway.example`, `.railwayignore`, `backend/railway.toml`.

## Out of Scope

- CORS security hardening (wildcard methods/headers, `allow_credentials`,
  env-configurable origins). Owned by D1.
- The `DATABASE_URL` vs `POSTGRES_*` split. This is intentional: compose builds
  `DATABASE_URL` from the `POSTGRES_*` values. Not drift.
- Passing LUNO keys to any non-Docker deployment path.

## Verification Checklist

- [ ] **KISS:** Only edits and deletions; no new abstraction or rewrite of
  Railway docs.
- [ ] **DRY:** The two env templates no longer carry duplicated, contradictory
  exchange-rate and Flask config; one clear `.env.example` remains.
- [ ] **Modular:** Each change is independent; removing Railway files does not
  affect the app, and the LUNO compose change is isolated to one service block.
- [ ] **Scalable:** No change that constrains growth; CORS hardening path remains
  open for D1.
- [ ] **Architecture invariants:** Single FastAPI service unchanged; no API/web
  logic or `services/` change.
- [ ] **Standards:** No em-dashes; edits stay surgical; `.env.example` keeps only
  variables the code or compose actually consumes.
- [ ] **Tests:** No behavior change to unit-test; verification is the import
  check, the `grep -ri railway` check, and `docker compose config` parsing.
- [ ] **Success criteria above are all met and were verified, not assumed.**
