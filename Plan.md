# Plan: Migrate from Flask Proxy to FastAPI Unified Server

## Why Migrate?

### The Current Problem

Today, the Flask frontend is a **pass-through proxy** with zero business logic. Every route follows the same pattern:

```python
# Flask route — ALL routes look like this
resp = client.get(f"{api_url}/api/v1/something")
data = resp.json()
return render_template('page.html', data=data)
```

This creates measurable costs:

| Problem | Evidence from Codebase |
|---------|----------------------|
| **Double-hop latency** | Dashboard alone makes 6 sequential `httpx.Client` calls (`dashboard.py:19-34`). Each request: Browser → Flask → FastAPI → DB → FastAPI → Flask → Browser |
| **Duplicated routing** | 6 Flask blueprint files (`accounts.py`, `assets.py`, `transactions.py`, `income.py`, `settings.py`, `dashboard.py`) that mirror the 7 FastAPI router files — 12 route files total for one app |
| **Two containers for one user** | `docker-compose.yml` runs `finn_frontend` and `finn_backend` as separate services with separate Dockerfiles, separate `requirements.txt`, separate health checks |
| **Duplicated dependencies** | Both `frontend/requirements.txt` and `backend/requirements.txt` list `httpx`, `python-dotenv`, `python-dateutil` |
| **No shared state** | Flask and FastAPI have separate `SECRET_KEY` configs. Flash messages, sessions, and API errors live in different processes |
| **Fragile template JS** | Chart configs are Jinja2-interpolated JS strings (e.g., `dashboard.html:386` — `{% for pt in daily_series.series %}{{ pt.cumulative_return }}{% if not loop.last %},{% endif %}{% endfor %}`). No syntax highlighting, no IDE support |

### What the Migration Eliminates

```
BEFORE:  Browser → Flask (proxy) → FastAPI (API) → PostgreSQL
AFTER:   Browser → FastAPI (API + HTML)  → PostgreSQL
```

| Eliminated | Impact |
|-----------|--------|
| Entire `frontend/` container | Faster startup, less memory, simpler deploys |
| `frontend/Dockerfile` | One Dockerfile instead of two |
| `frontend/requirements.txt` | 7 fewer dependencies to maintain |
| All `httpx.Client` proxy calls | No inter-service latency on page loads |
| `API_BASE_URL` configuration | No more coordinating service URLs |
| CORS configuration | Same-origin — CORS becomes irrelevant for HTML pages |

### What the Migration Enables

| Capability | Why it matters for multi-user |
|-----------|------------------------------|
| **Server-side sessions** | FastAPI `SessionMiddleware` + cookie auth — one place, one process |
| **Auth middleware** | Single `Depends(get_current_user)` protects both API and HTML routes |
| **Direct DB access in templates** | No serialization round-trip for simple page renders |
| **Alpine.js interactivity** | Client-side `fetch()` to `/api/v1/*` — same origin, no proxy |
| **Flash messages that work** | Starlette `SessionMiddleware` handles flash natively |
| **Simpler deployment** | One Railway/Render/Fly service instead of two |

---

## Architecture Decision

### Chosen: FastAPI + Jinja2 + Alpine.js

| Factor | Flask Proxy (current) | FastAPI + Jinja2 + Alpine.js | React SPA |
|--------|----------------------|------------------------------|-----------|
| Services to deploy | 2 | **1** | 2 (API + static host) |
| Auth complexity | Medium (session in Flask, verify in FastAPI) | **Low** (one `Depends()`) | High (JWT + refresh + interceptors) |
| Build toolchain | None | **None** | Webpack/Vite + npm |
| Interactivity | Page reload only | **Good** (Alpine.js directives) | Excellent |
| Template reuse | Jinja2 | **Same Jinja2 templates** | Full rewrite to JSX |
| Time to migrate | N/A | **~2-3 sessions** | ~2-3 weeks |
| Future mobile app | API exists | **API unchanged** | API unchanged |

### Why Not React/Vue?

- The app has 14 templates and 7 charts — not complex enough to justify a build system
- Multi-user auth with server-rendered forms is significantly simpler than JWT + SPA guards
- If we ever need a SPA, the API layer is untouched — we can bolt one on later
- Alpine.js gives us 80% of SPA interactivity (reactive forms, fetch-based chart updates, toggles) with 0% of the build complexity

---

## Detailed Migration Plan

### Phase 1: Backend Preparation (Foundation)

Add Jinja2 and static file serving to the existing FastAPI app. No Flask changes yet — both run simultaneously during migration.

**1.1 Add dependencies to `backend/requirements.txt`**

```
jinja2==3.1.2
itsdangerous==2.1.2      # For session signing
python-multipart==0.0.6  # Already present — for form data
```

**1.2 Create template infrastructure in `backend/app/`**

```
backend/app/
├── templates/           # Move from frontend/app/templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── accounts/
│   ├── assets/
│   ├── transactions/
│   ├── income/
│   └── settings/
├── static/              # Move from frontend/app/static/
│   ├── manifest.json
│   └── sw.js
└── web/                 # NEW — page route handlers
    ├── __init__.py
    ├── dependencies.py  # Shared template dependencies
    ├── dashboard.py
    ├── accounts.py
    ├── assets.py
    ├── transactions.py
    ├── income.py
    └── settings.py
```

**1.3 Configure FastAPI to serve templates and static files**

In `backend/app/main.py`:

```python
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

# Session support (needed for flash messages and future auth)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates available globally
templates = Jinja2Templates(directory="app/templates")
```

### Phase 2: Migrate Page Routes (One at a Time)

Convert each Flask blueprint to a FastAPI router that renders Jinja2 templates directly. The key difference: instead of calling `httpx.Client`, we call the database directly (reusing existing SQLAlchemy models).

**Migration pattern for each route:**

BEFORE (Flask — proxy to API):
```python
# frontend/app/routes/accounts.py
@bp.route('/')
def index():
    with httpx.Client() as client:
        resp = client.get(f"{api_url}/api/v1/accounts")
        accounts = resp.json()
    return render_template('accounts/index.html', accounts=accounts)
```

AFTER (FastAPI — direct DB access):
```python
# backend/app/web/accounts.py
@router.get("/accounts")
def index(request: Request, db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.is_active == True).all()
    return templates.TemplateResponse("accounts/index.html", {
        "request": request,
        "accounts": accounts,
    })
```

**Migration order (by dependency):**

| Order | Route File | Pages | Complexity | Notes |
|-------|-----------|-------|------------|-------|
| 1 | `dashboard.py` | 1 | Medium | 6 data fetches → 6 direct DB queries. Migrating this first proves the pattern works |
| 2 | `accounts.py` | 4 (list, add, edit, view) | Low | Simple CRUD, tests form POST handling |
| 3 | `assets.py` | 3 (list, add, edit) | Low | Similar to accounts |
| 4 | `transactions.py` | 2 (list, add) | Low | Similar pattern |
| 5 | `income.py` | 2 (list, add) | Low | Similar pattern |
| 6 | `settings.py` | 3 (index, allocation, snapshots) | Medium | Bulk allocation POST is slightly different |

**Template changes required:**

- Replace `{{ url_for('accounts.index') }}` with `{{ request.url_for('accounts_index') }}` (FastAPI uses function names, not blueprint.endpoint)
- Replace `get_flashed_messages()` with a custom flash helper using Starlette sessions
- Replace `{{ request.endpoint }}` sidebar active detection with path-based matching

**Create a shared flash message helper** (`backend/app/web/dependencies.py`):

```python
def flash(request: Request, message: str, category: str = "info"):
    """Add a flash message to the session."""
    if "_flashes" not in request.session:
        request.session["_flashes"] = []
    request.session["_flashes"].append({"message": message, "category": category})

def get_flashed_messages(request: Request):
    """Pop flash messages from the session."""
    messages = request.session.pop("_flashes", [])
    return messages
```

Register as a Jinja2 global so templates can call `get_flashed_messages(request)`.

### Phase 3: Template Adaptation

**3.1 Update `base.html`**

- Swap Flask `url_for()` to FastAPI `request.url_for()`
- Swap sidebar active class from `request.endpoint` to `request.url.path.startswith('/accounts')`
- Add Alpine.js CDN alongside existing Bootstrap + ApexCharts:

```html
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

**3.2 Update form templates**

Flask forms use `request.form['field']`. FastAPI uses `Form(...)` parameters. The HTML forms stay identical — only the server route handler changes.

**3.3 Refactor chart JavaScript**

Move chart data from Jinja2 interpolation to a `<script>` block with JSON:

BEFORE:
```html
data: [{% for pt in series %}{{ pt.value }}{% if not loop.last %},{% endif %}{% endfor %}]
```

AFTER:
```html
<div id="chart" x-data="chartComponent()" x-init="init()">
    <div x-ref="chart"></div>
</div>
<script>
    const chartData = {{ series_json | safe }};  <!-- One clean JSON dump -->
    function chartComponent() { /* Alpine.js component using chartData */ }
</script>
```

This gives us proper JSON serialization, IDE syntax highlighting, and the ability to refetch data with Alpine.js later.

### Phase 4: Docker Simplification

**4.1 Update `docker-compose.yml`**

Remove the `frontend` service entirely:

```yaml
services:
  db:
    # ... unchanged ...

  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"   # API
      - "5000:5000"   # HTML pages (optional: use same port)
    volumes:
      - ./backend/app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or serve everything on port 8000 (simpler) and update documentation.

**4.2 Update `backend/Dockerfile`**

Add the templates and static directories to the image.

**4.3 Clean up**

- Delete `frontend/Dockerfile`
- Delete `frontend/requirements.txt`
- Delete `frontend/app/__init__.py`
- Delete `frontend/app/routes/` (all 6 files)
- Keep `frontend/app/templates/` and `frontend/app/static/` until fully migrated to `backend/`
- Remove `API_BASE_URL` and `FLASK_ENV` from `.env.example`

### Phase 5: Alpine.js Interactivity (Enhancement)

After migration is complete, incrementally add Alpine.js where it improves UX:

**5.1 Dashboard date range picker**

```html
<div x-data="{ startDate: '2026-01-01', endDate: '2026-02-13' }">
    <input type="date" x-model="startDate" @change="refreshCharts()">
    <input type="date" x-model="endDate" @change="refreshCharts()">
    <div x-ref="dietzChart"></div>
</div>
```

When user changes dates, Alpine.js calls `fetch('/api/v1/returns/modified-dietz?start_date=...')` and updates the ApexChart — no page reload.

**5.2 Asset class filter toggles on charts**

```html
<div x-data="{ selectedClass: null }">
    <button @click="selectedClass = null" :class="{ active: !selectedClass }">All</button>
    <template x-for="ac in assetClasses">
        <button @click="selectedClass = ac.id; refreshChart()" x-text="ac.name"></button>
    </template>
</div>
```

**5.3 Inline delete confirmations**

Replace full-page form POSTs with Alpine.js confirm dialogs + `fetch()` DELETE calls.

### Phase 6: Auth Preparation (Future — Multi-User)

This phase is NOT part of the migration but is the reason we consolidate now.

**6.1 User model**

```python
class User(Base):
    __tablename__ = "users"
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

**6.2 Auth dependency**

```python
def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return user
```

**6.3 Data scoping**

Every query that currently does `db.query(Account).filter(Account.is_active == True)` becomes:

```python
db.query(Account).filter(Account.is_active == True, Account.user_id == user.id)
```

This is trivial when HTML routes and API routes share the same `Depends()` chain — which is exactly what consolidation gives us.

**Why this is hard with Flask proxy:**
- Flask has its own session → needs separate auth check
- FastAPI has its own session → needs separate auth check
- Token passing between services adds complexity
- CORS with credentials is finicky
- Two places to handle "unauthorized" → inconsistent UX

**Why this is easy with consolidated FastAPI:**
- One `SessionMiddleware`, one `get_current_user` dependency
- Both HTML and JSON routes use the same dependency
- No CORS needed (same origin)
- One place to redirect to `/login`

---

## Files Changed Summary

### New Files

| File | Purpose |
|------|---------|
| `backend/app/web/__init__.py` | Web router registration |
| `backend/app/web/dependencies.py` | Flash messages, template helpers |
| `backend/app/web/dashboard.py` | Dashboard page route |
| `backend/app/web/accounts.py` | Account CRUD page routes |
| `backend/app/web/assets.py` | Asset CRUD page routes |
| `backend/app/web/transactions.py` | Transaction page routes |
| `backend/app/web/income.py` | Income page routes |
| `backend/app/web/settings.py` | Settings page routes |

### Moved Files

| From | To |
|------|-----|
| `frontend/app/templates/*` | `backend/app/templates/*` |
| `frontend/app/static/*` | `backend/app/static/*` |

### Modified Files

| File | Change |
|------|--------|
| `backend/app/main.py` | Add SessionMiddleware, StaticFiles mount, template config, web routers |
| `backend/requirements.txt` | Add `jinja2`, `itsdangerous` |
| `backend/Dockerfile` | Include templates and static dirs |
| `docker-compose.yml` | Remove `frontend` service |
| `backend/app/templates/base.html` | Update `url_for()` calls, add Alpine.js CDN, path-based sidebar active |
| All 14 template files | Update `url_for()` to `request.url_for()` |
| `.env.example` | Remove `API_BASE_URL`, `FLASK_ENV` |

### Deleted Files

| File | Reason |
|------|--------|
| `frontend/Dockerfile` | No longer needed |
| `frontend/requirements.txt` | No longer needed |
| `frontend/app/__init__.py` | No longer needed |
| `frontend/app/routes/*.py` (6 files) | Replaced by `backend/app/web/*.py` |

---

## Implementation Order

```
Phase 1  →  Backend preparation (add Jinja2 + static + session middleware)
Phase 2  →  Migrate dashboard.py first (validates the pattern)
Phase 2  →  Migrate remaining 5 route files
Phase 3  →  Adapt all templates (url_for, flash, sidebar)
Phase 4  →  Docker simplification (remove frontend service)
Phase 5  →  Alpine.js enhancements (date pickers, filters)
Phase 6  →  Auth (future — multi-user)
```

Each phase is independently deployable. Phase 2 routes can be migrated one at a time while Flask still serves the unmigrated pages (both services run in parallel during transition).

---

## Verification Plan

1. **After Phase 1:** `http://localhost:8000/` serves a test HTML page with correct static files
2. **After Phase 2 (dashboard):** `http://localhost:8000/dashboard` renders all 7 charts with live data
3. **After Phase 2 (all routes):** Every page at `http://localhost:8000/*` matches the current Flask output
4. **After Phase 3:** Sidebar navigation, flash messages, and form submissions all work
5. **After Phase 4:** `docker-compose up` starts 2 services (db + backend) instead of 3
6. **Regression:** All API endpoints (`/api/v1/*`) continue to work unchanged — verified via Swagger UI at `/docs`

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Template breakage during migration | Migrate one route at a time, keep Flask running in parallel |
| `url_for()` differences break links | Create a Jinja2 global helper that wraps FastAPI's `request.url_for()` with the same interface |
| Flash messages don't work | Implement custom flash helper before migrating any POST routes |
| Static files not found | Test static mount path early in Phase 1 |
| API regression | API routers (`/api/v1/*`) are untouched — zero risk |
| Rollback needed | Keep `frontend/` directory until Phase 4 is verified — `git checkout` restores it |
