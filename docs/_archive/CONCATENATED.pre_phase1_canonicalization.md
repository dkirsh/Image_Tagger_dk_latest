Claude:
# DOCUMENT 1: SEAM ANALYSIS

**1. Are frontend and backend concerns physically mixed in the same files?**

No — not within individual files. The inventory shows clean file-level separation: Python modules live under `backend/` and React/Vite code lives under `frontend/apps/*`. There is no evidence of JSX imported into Python or of backend logic embedded in frontend components. However, *structural* mixing exists at the repository root: `backend/`, `frontend/`, `scripts/`, `tests/`, `docs/`, `deploy/`, `infra/`, `ai/`, `contracts/`, `governance/`, `archive/`, `scrapping/`, and twenty-odd changelog markdown files all sit at the top level of `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/`, alongside two sibling projects (`TRS_v1.1`, `biophilia-index-main`) that further dilute the boundary.

**2. Is there an identifiable folder boundary between frontend and backend?**

Yes, and it is cleaner than the top-level chaos suggests. `frontend/apps/{admin,explorer,monitor,workbench}` and `frontend/shared/` form a coherent monorepo, and `backend/{api,services,models,schemas,science,database}` is a textbook FastAPI layout. The boundary exists; it is simply buried under archival clutter (the `archive/` subtree contains ~60 historical snapshots from v3.2.x through v3.4.x) and under a single repository containing three independent projects.

**3. Riskiest structural dependency for parallel work**

The single most dangerous artifact is the repository root itself — specifically the coexistence of three projects (`Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`, `TRS_v1.1`, `biophilia-index-main`) with overlapping ML concerns, combined with the massive `archive/` tree. Two engineers pulling from this root will hit merge conflicts on `.gitignore`, CI workflows, root-level READMEs, and — most importantly — will have no shared mental model of "where does new code go?" The second-riskiest item is `backend/science/pipeline.py`, which is the orchestration choke-point touched by both ML validation work (Track A) and any debug-view work that might bleed into Track B.

**4. Recommended scenario**

**Scenario C** — a time-boxed pre-sprint (target 3–4 hours) to establish boundaries only, with no logic rewrites.

**5. Justification**

A full joint restructure (A) is unjustified because the internal structure of `backend/` and `frontend/` is already sound; the problem is scope, not architecture. A solo branch restructure (B) would block both engineers for a full day and create a single reviewer bottleneck. A short joint pre-sprint is sufficient because the required moves are mechanical: promote the active project to repo root, quarantine `archive/` and the sibling projects, commit the contract document, and verify both laptops run the stack — after which the clean `backend/`/`frontend/` seam that already exists becomes usable for genuinely parallel work.

---

# DOCUMENT 2: PRE_SPRINT.md

**Duration:** 3–4 hours, both engineers pairing on one machine then verifying on the other.

## Target Folder Structure

```
/                              # repo root — was Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/
├── backend/                   # FastAPI application (Track A territory)
│   ├── api/                   # versioned routers (v1_*)
│   ├── services/              # business logic layer
│   ├── models/                # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic request/response schemas
│   ├── science/               # ML pipeline (math, vision, semantics, spatial)
│   │   └── data/              # model weights and reference data (tracked)
│   ├── database/              # engine, session, migrations
│   ├── scripts/               # backend-local ops scripts
│   ├── tests/                 # backend unit + integration tests
│   └── main.py                # FastAPI entrypoint
├── frontend/                  # React monorepo (Track B territory)
│   ├── apps/
│   │   ├── explorer/          # public browse journey
│   │   ├── workbench/         # tagger journey (HITL)
│   │   ├── monitor/           # supervisor journey
│   │   └── admin/             # admin cockpit journey
│   ├── shared/                # shared components and API client
│   └── package.json           # npm workspace root
├── docs/                      # canonical documentation (both tracks read)
│   ├── CONTRACT.md            # shared API + schema contract (THIS pre-sprint)
│   ├── ML_EVALUATION.md       # to be written in Track A
│   └── ARCHITECTURE.md        # promoted from README_v3.md
├── deploy/                    # Dockerfiles, compose, nginx, host configs
├── .github/workflows/         # CI — one workflow per track plus integration
├── _archive/                  # EVERYTHING historical — git-tracked but frozen
│   ├── image_tagger_archive/  # old archive/ tree moved wholesale
│   ├── trs_v1_1/              # sibling project, out of scope
│   ├── biophilia_index/       # sibling project, out of scope
│   ├── changelogs/            # CHANGELOG_v3.4.*.md files
│   └── scrapping/             # exploratory scraping notebooks
├── .env.example               # all env vars documented, no values
├── .gitignore
└── README.md                  # short pointer to docs/ARCHITECTURE.md
```

## Shared Contracts (committed as `/docs/CONTRACT.md`)

### REST API Endpoints (v1)

All endpoints are prefixed `/v1`. All requests include `X-User-Id` and `X-User-Role` headers; privileged routes additionally require `Authorization: Bearer <jwt>`.

**Explorer (public browse)**
- `GET /v1/explorer/search?q=&page=&page_size=&room_type=&tag=` → `{ items: ImageSummary[], total: int, page: int, page_size: int }`
- `GET /v1/explorer/images/{image_id}` → `ImageDetail`
- `GET /v1/explorer/attributes` → `{ attributes: AttributeDef[] }`

**Workbench (human tagging)**
- `GET /v1/workbench/next` → `ImageDetail | { empty: true }`
- `POST /v1/workbench/validate` body `ValidationSubmit` → `{ validation_id: int, accepted: bool }`
- `POST /v1/workbench/region` body `RegionCreate` → `Region`

**Monitor (supervisor)**
- `GET /v1/monitor/velocity?window_hours=` → `{ series: VelocityPoint[] }`
- `GET /v1/monitor/irr?attribute_key=` → `{ attribute_key: str, irr: float, bin: "low"|"medium"|"high", n_pairs: int }`

**Admin**
- `POST /v1/admin/upload` multipart → `{ job_id: str, items: int }`
- `GET /v1/admin/budget` → `{ spent_usd: float, limit_usd: float, remaining_usd: float }`
- `POST /v1/admin/kill-switch` body `{ enabled: bool }` → `{ enabled: bool, changed_at: iso8601 }`

**Health**
- `GET /health` → `{ status: "ok"|"degraded", version: str, db: bool, storage: bool }`

### Shared TypeScript / Pydantic Types

```ts
type ImageSummary = {
  id: number;
  url: string;
  thumbnail_url: string;
  room_type: string | null;
  canonical_tags: string[];
  validation_count: number;
};

type ImageDetail = ImageSummary & {
  width: number; height: number;
  science: SciencePayload | null;
  regions: Region[];
};

type SciencePayload = {
  run_id: number;
  run_status: "pending" | "running" | "completed" | "failed";
  features: Record<string, number>;   // canonical feature keys
  affordances: AffordancePrediction[];
  confidence: ConfidenceBlock;         // see ML contract below
};

type ValidationSubmit = {
  image_id: number;
  attribute_key: string;
  value: string | number | boolean;
  duration_ms: number;
};
```

### ML Model I/O Contract

Every ML output object carries a **trust envelope**:

```json
{
  "value": <scalar or vector>,
  "model_id": "affordance_L059_lgbm_v1",
  "evaluation_status": "validated" | "proxy_validated" | "untested",
  "confidence_interval_95": [lower, upper] | null,
  "n_training": 1523,
  "notes": "held-out test R²=0.71; see ML_EVALUATION.md#L059"
}
```

Untested models MUST return `evaluation_status: "untested"` and the frontend MUST render a visible warning badge.

### Auth Structure

- JWT issued by a free-tier identity provider (Supabase Auth); backend validates signature using `SUPABASE_JWT_SECRET`
- Roles encoded in JWT claim `role ∈ {tagger, scientist, supervisor, admin}`
- Tagger endpoints require valid JWT (no anonymous writes)
- Supervisor/admin endpoints require both valid JWT and matching role claim

### Shared Environment Variables (names only)

`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`, `IMAGE_STORAGE_ROOT`, `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `VLM_HARD_LIMIT_USD`, `LOG_LEVEL`, `SENTRY_DSN`, `CORS_ALLOWED_ORIGINS`.

## Pre-Sprint Task List

- [ ] Create `_archive/` at repo root and move the entire `archive/`, `scrapping/`, root-level `CHANGELOG_v3.4.*.md` files, `deconcat_v3_3.py`, and the two sibling projects (`TRS_v1.1`, `biophilia-index-main`) into it. **Done when:** `ls` at repo root shows only the target structure above.
- [ ] Promote the active project up one level: move contents of `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/*` to repo root, resolving collisions against `_archive/`. **Done when:** `backend/main.py` and `frontend/package.json` exist at the canonical paths.
- [ ] Update `backend/main.py`, any `sys.path` hacks, and `pyproject.toml`/`requirements-install.txt` references that assumed the old nested root. **Done when:** `python -c "import backend.main"` succeeds from repo root.
- [ ] Create `.env.example` enumerating every variable from the Dependency & Gap Analysis §3.5 plus the new Supabase and Sentry vars. Values left blank. **Done when:** file is committed and `grep -c "=" .env.example` ≥ 18.
- [ ] Write and commit `/docs/CONTRACT.md` using the contract block above verbatim as the starting point. **Done when:** file is pushed to `main` and both engineers have pulled it.
- [ ] Update `deploy/docker-compose.yml` to read all credentials from `.env` (no hardcoded `tagger`/`tagger_pass`). **Done when:** `docker compose config` shows all secrets resolved from env.
- [ ] Rewrite repo-root `README.md` as a short pointer (≤ 20 lines) to `docs/ARCHITECTURE.md`, `docs/CONTRACT.md`, and the two track plans. **Done when:** committed.
- [ ] On **each engineer's laptop independently**: clone fresh, `cp .env.example .env`, fill dev values, run `docker compose up -d db && cd backend && pip install -r ../requirements-install.txt && uvicorn backend.main:app --reload` in one terminal and `cd frontend && npm install && npm run dev` in another. **Done when:** both engineers confirm `GET http://localhost:8000/health` returns `200` and `http://localhost:5173` loads the explorer shell.

## Exit Criteria

1. `git log --oneline -1` on `main` shows the pre-sprint merge commit and both engineers have pulled it.
2. `/docs/CONTRACT.md` exists on `main` and both engineers have read it end to end.
3. The smoke test `curl -s http://localhost:8000/health | grep '"status":"ok"'` passes on both laptops.
4. `ls` at repo root shows no stray changelogs, no sibling projects, and no `archive/` outside `_archive/`.
5. Two feature branches exist: `track-a-backend-ml` and `track-b-frontend-ux`, both branched from the post-pre-sprint `main`.

---

# DOCUMENT 3: PLAN_BACKEND_ML.md

**Owner:** Engineer A. **Scope:** everything under `/backend/`, `/deploy/`, `/docs/ML_EVALUATION.md`. **Out of scope:** anything under `/frontend/`.

#### Task A-1: Environment & Secrets Management
- **Goal:** Eliminate all hardcoded secrets and fail-fast on missing configuration.
- **Files to create or modify:** `backend/settings.py` (new, using `pydantic-settings`), `backend/main.py`, `deploy/docker-compose.yml`, `.env.example`.
- **Implementation notes:** Use `pydantic_settings.BaseSettings` with `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`. All settings (`database_url`, `supabase_jwt_secret`, `cors_allowed_origins`, `vlm_hard_limit_usd`) must be typed and required (no default) for production-critical ones; dev defaults allowed only when `ENVIRONMENT=development`. Raise `RuntimeError` in `main.py` lifespan startup if any required var is unset in production mode. Remove all `os.getenv(..., "dev_secret_key_change_me")` occurrences.
- **Acceptance criteria:** `ENVIRONMENT=production uvicorn backend.main:app` fails immediately with a clear message when `SUPABASE_JWT_SECRET` is unset; `grep -rn "dev_secret_key_change_me\|tagger_pass" backend/ deploy/` returns zero matches.
- **Depends on:** pre-sprint only.

#### Task A-2: Structured Logging and Request Middleware
- **Goal:** Replace `print()` and default logging with JSON structured logs, request IDs, and timing middleware.
- **Files to create or modify:** `backend/logging_config.py` (new), `backend/middleware/request_context.py` (new), `backend/main.py`, `backend/services/auth.py` (replace the `print` at line 41).
- **Implementation notes:** Use `structlog` configured to emit JSON to stdout. Middleware generates a `request_id` (uuid4), attaches it to a `contextvars.ContextVar`, binds it to the logger, and includes it in the `X-Request-ID` response header. Log one line per request at INFO with method, path, status, duration_ms, user_id, role. Use `logger.warning` for failed admin auth attempts with the attempted user id.
- **Acceptance criteria:** `curl -v http://localhost:8000/health` response contains `X-Request-ID`; stdout shows one JSON log line per request with parseable fields; `grep -rn "print(" backend/services/ backend/api/` returns zero matches.
- **Depends on:** A-1.

#### Task A-3: Authentication via Supabase Auth
- **Goal:** Replace header-trust auth with JWT validation against a free-tier identity provider.
- **Files to create or modify:** `backend/services/auth.py` (rewrite), `backend/tests/test_auth.py` (new).
- **Implementation notes:** Use `python-jose` to verify JWTs signed by Supabase using HS256 and `SUPABASE_JWT_SECRET`. Extract `sub` as user id and `role` from the `app_metadata.role` claim. Provide FastAPI dependencies `require_tagger`, `require_scientist`, `require_supervisor`, `require_admin`. Reject any request without a valid bearer token on protected routes with 401; reject mismatched roles with 403. Keep a single `dev_bypass_token` path guarded by `ENVIRONMENT=development` for local work.
- **Free tier note:** Supabase free tier allows 50,000 monthly active users and unlimited auth API calls — more than sufficient for a portfolio piece. The backend only validates JWTs locally, so Supabase is never a runtime dependency of request handling.
- **Acceptance criteria:** `pytest backend/tests/test_auth.py -k "valid_admin_jwt"` passes; the same test with a tampered signature returns 401; a valid tagger JWT hitting `/v1/admin/budget` returns 403.
- **Depends on:** A-1, A-2.

#### Task A-4: Input Validation and Error Handling on All Endpoints
- **Goal:** Every endpoint validates input via Pydantic and returns structured error responses; no unhandled exceptions escape.
- **Files to create or modify:** all files under `backend/api/v1_*.py`, `backend/schemas/*.py`, `backend/main.py` (add exception handlers).
- **Implementation notes:** Tighten Pydantic schemas: `Field(ge=1)` on page, `Field(max_length=...)` on all free-text strings, `conlist` on batch endpoints. Register a global exception handler in `main.py` that catches `SQLAlchemyError`, `ValueError`, and `Exception`, returning `{error: {code, message, request_id}}` with appropriate status and logging the stack trace at ERROR. Wrap the upload commit in `try/except` with explicit `db.rollback()` on failure. Remove runtime clamping logic now handled by schema.
- **Acceptance criteria:** `curl -X POST /v1/explorer/search -d '{"page": -5}'` returns 422 with a Pydantic error body; forcing a DB error in a test returns 500 with a `request_id` in both body and logs; every `POST` endpoint has at least one explicit `db.rollback()` in its error path.
- **Depends on:** A-2.

#### Task A-5: Rate Limiting
- **Goal:** Bound request rates per user and per IP on expensive and auth-sensitive endpoints.
- **Files to create or modify:** `backend/middleware/ratelimit.py` (new or adapt existing `TRS_v1.1/backend/app/ratelimit.py` as reference), `backend/main.py`.
- **Implementation notes:** Use `slowapi` (Flask-Limiter port for Starlette). Limits: `/v1/admin/upload` 20/hour per user; `/v1/workbench/validate` 600/hour per user; all `/v1/admin/*` 200/hour per user; unauthenticated endpoints 60/minute per IP. Storage backend is in-memory for single-instance deploy; document the Redis upgrade path in code comments.
- **Acceptance criteria:** An integration test that fires 25 upload requests in one second as the same user receives at least five 429 responses.
- **Depends on:** A-3.

#### Task A-6: Database Migrations with Alembic
- **Goal:** Replace hand-rolled `migrate_*.py` scripts with Alembic, including rollback capability.
- **Files to create or modify:** `backend/database/alembic/` (new directory tree), `backend/database/alembic.ini`, `backend/database/migrations/versions/*.py` (one initial revision capturing current schema), `deploy/Dockerfile.backend` (run `alembic upgrade head` on startup).
- **Implementation notes:** Use `alembic init` then autogenerate the initial revision from current SQLAlchemy models. Move the logic from `migrate_3_4_63_add_validation_fk.py` and `migrate_3_4_74_add_science_tables.py` into explicit named revisions rather than autogenerate where data transformation is involved. Keep the old scripts in `_archive/migrations_legacy/` for reference.
- **Acceptance criteria:** `alembic upgrade head` on an empty database produces a schema identical to current production; `alembic downgrade -1` followed by `alembic upgrade head` round-trips cleanly; container startup logs show migrations applied before Uvicorn binds.
- **Depends on:** A-1.

#### Task A-7: ML Trust Envelope and Feature Registry Refactor
- **Goal:** Every ML output passes through a uniform trust envelope declaring its evaluation status.
- **Files to create or modify:** `backend/science/trust.py` (new), `backend/science/pipeline.py`, `backend/science/features_registry.py`, `backend/schemas/science.py`.
- **Implementation notes:** Define `TrustEnvelope` Pydantic model matching the contract (Task pre-sprint). Mark each feature in `features_canonical.jsonl` with one of `validated`, `proxy_validated`, `untested`. The pipeline assembly code wraps every output in an envelope before insertion into `validations`. For legacy features without metadata, default to `untested`. This enables the frontend to show trust badges without parsing free-text notes.
- **Acceptance criteria:** `GET /v1/explorer/images/{id}` response JSON shows a `science.confidence` block on every feature; schema validation rejects a pipeline output lacking `evaluation_status`.
- **Depends on:** A-4.

#### Task A-8: ML Model Statistical Validation — Affordance LightGBM Models
- **Goal:** Produce held-out test metrics, confusion matrices (for classification) or residual plots and 95% bootstrap CIs (for regression) for the five LightGBM affordance models, and document them.
- **Files to create or modify:** `backend/science/evaluation/affordance_eval.py` (new), `docs/ML_EVALUATION.md` (new), `backend/science/data/affordance_models/L*/evaluation_report.json` (generated).
- **Implementation notes:** Load each model from its existing `.pkl`. Because the original train/test split may be lost, reconstruct a held-out set by stratified 80/20 split on whatever labeled data is available in the database (`validations` with `source="manual"`) matching the target affordance. Compute R², MAE, and Pearson r with 1,000-iteration bootstrap 95% CIs using `scipy.stats.bootstrap`. If fewer than 50 labeled examples exist, mark the model `untested` in the registry and explain the gap in ML_EVALUATION.md. Follow the reporting recommendations of Raschka (2020) on model evaluation under small-sample regimes.
- **Acceptance criteria:** `docs/ML_EVALUATION.md` contains one subsection per model with sample size, point estimates, 95% CIs, and a verdict (`validated` / `proxy_validated` / `untested`); the trust envelope for each affordance output reflects the same verdict at runtime.
- **Depends on:** A-7.

#### Task A-9: ML Model Validation — Segmentation and Room Detection
- **Goal:** Validate OneFormer (segmentation) and ResNet50-Places365 (room detection) against a small curated test set.
- **Files to create or modify:** `backend/science/evaluation/vision_eval.py` (new), `backend/science/evaluation/test_sets/rooms.csv` (new, ~200 images with gold room labels), `docs/ML_EVALUATION.md`.
- **Implementation notes:** Curate ~200 images from the existing corpus with human-assigned room labels (supervisor role can tag these via the existing workbench in a focused session). For room detection compute top-1 and top-3 accuracy plus a confusion matrix over the seven most common classes using `sklearn.metrics`. For segmentation use mean IoU on the subset of images with manual region polygons in the `regions` table. Report Wilson score intervals for accuracy per Brown, Cai & DasGupta (2001).
- **Acceptance criteria:** `docs/ML_EVALUATION.md` contains a confusion matrix figure and per-class precision/recall with 95% Wilson intervals; the frontend receives `evaluation_status: "validated"` on room detection outputs for classes that meet a ≥0.70 precision threshold.
- **Depends on:** A-8.

#### Task A-10: Health Check, Metrics, and Observability
- **Goal:** `/health` performs real dependency checks; basic metrics endpoint available.
- **Files to create or modify:** `backend/api/health.py` (new), `backend/main.py`, `backend/middleware/metrics.py` (new).
- **Implementation notes:** `/health` runs `SELECT 1` against the DB, checks `IMAGE_STORAGE_ROOT` is writable, and returns `{status: "ok"|"degraded", db: bool, storage: bool, version: str}`. Add a `/metrics` endpoint using `prometheus-client` exposing request count, latency histogram, and ML pipeline run count — Render free tier does not need Prometheus but the endpoint is portfolio evidence. Integrate Sentry SDK (`sentry-sdk[fastapi]`) gated on `SENTRY_DSN` being set.
- **Free tier note:** Sentry free tier allows 5,000 errors/month, which is ample for a portfolio deployment. Prometheus endpoint is self-hosted and costs nothing.
- **Acceptance criteria:** Stopping the database container causes `/health` to return 503 with `db: false` within 2 seconds; `/metrics` returns valid Prometheus text format.
- **Depends on:** A-2.

#### Task A-11: Integration Tests — One Per Endpoint
- **Goal:** Every v1 endpoint has at least one integration test exercising the happy path and at least one unhappy path (auth or validation).
- **Files to create or modify:** `backend/tests/integration/test_explorer.py`, `test_workbench.py`, `test_admin.py`, `test_monitor.py`, `test_bn_export.py`, `backend/tests/conftest.py`.
- **Implementation notes:** Use `pytest`, `httpx.AsyncClient`, and a per-test SQLite-in-memory override of `DATABASE_URL` via dependency injection. Provide fixtures that mint test JWTs with arbitrary roles using the same `SUPABASE_JWT_SECRET` the app uses in test mode. Follow the Arrange-Act-Assert discipline and include at minimum: valid token + happy path, missing token → 401, wrong role → 403, malformed body → 422 for each POST.
- **Acceptance criteria:** `pytest backend/tests/integration/ -v` reports coverage ≥ 85% on `backend/api/` as measured by `pytest-cov`; the CI workflow fails the build if coverage drops below 80%.
- **Depends on:** A-3, A-4.

#### Task A-12: Deployment to Render (Free Tier)
- **Goal:** Backend deployable by pushing to `main`; database hosted free; one-command teardown/redeploy.
- **Files to create or modify:** `render.yaml` (new, at repo root), `deploy/Dockerfile.backend` (add `USER app` non-root), `.github/workflows/deploy_backend.yml` (new).
- **Implementation notes:** Use Render's free Web Service + free PostgreSQL (limit: 1 GB storage, 90-day expiry, must be recreated thereafter). `render.yaml` declares the service, environment group, and database. The Dockerfile adds a non-root user and runs `alembic upgrade head && uvicorn backend.main:app --host 0.0.0.0 --port $PORT`. Image storage uses Supabase Storage (free tier: 1 GB) rather than Render's ephemeral disk — update `backend/services/storage.py` to support both `filesystem` and `supabase` backends via the `STORAGE_BACKEND` env var.
- **Free tier note:** Render Web Service free tier sleeps after 15 minutes of inactivity and has 750 hours/month — fine for a portfolio piece, but the README must state "first request may take ~30s to wake." Render PostgreSQL free tier expires after 90 days and must be recreated; Supabase PostgreSQL (500 MB, no expiry) is a sturdier alternative and is compatible with the same `DATABASE_URL` pattern.
- **Acceptance criteria:** A push to `main` that changes `backend/` triggers the GitHub Action, which triggers a Render deploy; the deployed `/health` endpoint returns 200 with `db: true`; a fresh tagger can sign in via the frontend and submit one validation against the deployed instance.
- **Depends on:** A-1, A-6, A-10, A-11.

---

# DOCUMENT 4: PLAN_FRONTEND_UX.md

**Owner:** Engineer B. **Scope:** everything under `/frontend/`. **Out of scope:** anything under `/backend/`.

**Mock-first mandate:** Every API call is routed through `frontend/shared/src/api-client.js`, which reads `VITE_USE_MOCKS`. When true (default during Track B), it returns fixtures matching `docs/CONTRACT.md` exactly. Engineer B does not wait for Track A.

**User journeys enumerated from the repo inventory:**
1. **Explorer** (public browse and image detail) — `frontend/apps/explorer`
2. **Workbench** (tagger human-in-the-loop annotation) — `frontend/apps/workbench`
3. **Monitor** (supervisor quality oversight) — `frontend/apps/monitor`
4. **Admin** (admin cockpit: uploads, VLM config, budget, kill-switch) — `frontend/apps/admin`

#### Task B-1: Mock API Client and Contract Fixtures
- **Goal:** Single API client used by all four apps, switchable between mock and live.
- **Files to create or modify:** `frontend/shared/src/api-client.js`, `frontend/shared/src/mocks/` (new, one file per endpoint group), `frontend/shared/src/types.ts` (new).
- **Implementation notes:** Use native `fetch` wrapped in typed functions: `explorer.search()`, `workbench.getNext()`, etc. When `import.meta.env.VITE_USE_MOCKS === "true"`, each function returns a Promise that resolves after a 150–400ms randomized delay with fixture data matching the Pydantic shapes in `CONTRACT.md`. Use `msw` (Mock Service Worker) if the team prefers intercepting at the network layer — either is acceptable, but `msw` makes the later mock-swap zero-code. Types are shared via TypeScript declaration files or JSDoc.
- **Acceptance criteria:** All four apps import from `frontend/shared` and render data without any backend running; flipping `VITE_USE_MOCKS=false` causes them to hit `VITE_API_BASE_URL` instead.
- **Depends on:** pre-sprint only.

#### Task B-2: Shared Design System and Layout Primitives
- **Goal:** Consistent visual language across all four apps: header, toasts, buttons, form inputs, loading skeletons, empty states, error banners, trust badges.
- **Files to create or modify:** `frontend/shared/src/components/{Button,Input,Select,Skeleton,EmptyState,ErrorBanner,TrustBadge,Modal,Pagination}.jsx`, `frontend/shared/src/theme.css`.
- **Implementation notes:** Build on the existing Tailwind config. The `TrustBadge` component takes an `evaluation_status` prop from the ML trust envelope and renders a color-coded pill (green "validated", amber "proxy", gray "untested") with a tooltip linking to `docs/ML_EVALUATION.md`. Keyboard focus rings must be visible (`focus-visible:ring-2 focus-visible:ring-offset-2`). All color pairs validated to meet WCAG AA (≥4.5:1) using the Level Access color contrast formulas.
- **Acceptance criteria:** Storybook or a `frontend/shared/preview.html` page renders every component in default, loading, error, and disabled states; automated `axe-core` run against the preview reports zero critical violations.
- **Depends on:** B-1.

#### Task B-3: Explorer Journey (public browse + detail)
- **Goal:** Search, filter, paginate, open image detail with science panel and trust badges.
- **Files to create or modify:** `frontend/apps/explorer/src/App.jsx`, `frontend/apps/explorer/src/SearchBar.jsx`, `frontend/apps/explorer/src/ImageGrid.jsx`, `frontend/apps/explorer/src/ImageDetailModal.jsx`.
- **Implementation notes:** URL-synced state (`?q=&page=&room_type=`) via `history.pushState` so deep links work. Grid uses CSS `grid-template-columns: repeat(auto-fill, minmax(240px, 1fr))`. Detail modal shows tabs: Overview, Science Features (each feature row shows value, 95% CI bar, and trust badge), Affordances. Loading shows skeleton cards; empty search shows friendly empty state; network error shows retry banner.
- **Acceptance criteria:** Every async state (loading, empty, error, success) is reachable by manipulating the mock client's behavior flags; Lighthouse performance score ≥ 85 on localhost for the explorer route.
- **Depends on:** B-2.

#### Task B-4: Workbench Journey (tagger HITL)
- **Goal:** Fetch next image, present attribute form with client-side validation, submit, advance.
- **Files to create or modify:** `frontend/apps/workbench/src/App.jsx`, `frontend/apps/workbench/src/AttributeForm.jsx`, `frontend/apps/workbench/src/RegionCanvas.jsx`, `frontend/apps/workbench/src/KeyboardShortcuts.jsx`.
- **Implementation notes:** Keyboard shortcuts (`1-9` to select category, `Enter` to submit, `n` for next) — a known driver of tagger throughput per Sheng, Provost & Ipeirotis (2008) on annotation efficiency. The submit handler captures `performance.now()` deltas for the `duration_ms` contract field. Form validation uses `zod` or a hand-rolled validator: required fields, numeric ranges, mutually exclusive options. Region canvas is an optional enhancement using plain `<canvas>` with mouse events — no heavy libraries. Undo button stores the last submission in memory for revocation within the same session.
- **Acceptance criteria:** Tagging ten mock images with keyboard only (no mouse) completes without errors; submitting with a missing required field shows inline validation and does not hit the network.
- **Depends on:** B-2.

#### Task B-5: Monitor Journey (supervisor oversight)
- **Goal:** Velocity chart, inter-rater reliability table, per-tagger drill-down.
- **Files to create or modify:** `frontend/apps/monitor/src/App.jsx`, `frontend/apps/monitor/src/VelocityChart.jsx`, `frontend/apps/monitor/src/IRRTable.jsx`.
- **Implementation notes:** Use `recharts` (already in dependencies) for the velocity line chart. IRR table columns: attribute, Cohen's κ or Krippendorff's α, n_pairs, bin. Color rows by bin. Per the thresholds of Landis & Koch (1977), κ < 0.4 is "poor", 0.4–0.6 "moderate", > 0.6 "substantial"; use these for tooltips. Empty state when no validation pairs exist yet. Respect the 403 response if the current user is not a supervisor, showing a dedicated unauthorized screen.
- **Acceptance criteria:** The IRR table sorts by any column; hovering a velocity point shows timestamp and count; a supervisor-role mock user sees data, a tagger-role mock user sees "Access Restricted."
- **Depends on:** B-2.

#### Task B-6: Admin Journey (cockpit)
- **Goal:** Upload images, view budget, toggle kill-switch, configure VLM provider.
- **Files to create or modify:** `frontend/apps/admin/src/App.jsx`, `frontend/apps/admin/src/UploadPanel.jsx`, `frontend/apps/admin/src/BudgetPanel.jsx`, `frontend/apps/admin/src/KillSwitch.jsx`, `frontend/apps/admin/src/VLMConfigPanel.jsx`.
- **Implementation notes:** Upload uses drag-and-drop (`ondrop`) with client-side validation (file type in `{jpg,jpeg,png,webp}`, size ≤ 10 MiB, ≤ 200 files per batch) enforcing the contract exactly. Kill-switch is a confirmation-gated toggle (two-click) because it disables paid models globally. Budget panel shows a progress bar colored green/amber/red at 50%/80% of `VLM_HARD_LIMIT_USD`. Every destructive or billing-impacting action triggers a toast on success and an error banner on failure.
- **Acceptance criteria:** Attempting to upload 201 files or a 20 MiB PNG shows an inline error before any network call; flipping the kill-switch requires explicit confirmation and shows an optimistic UI update that rolls back on error.
- **Depends on:** B-2.

#### Task B-7: Responsive Layout and Accessibility Audit
- **Goal:** All four apps usable on 360px mobile through 1920px desktop; WCAG AA baseline met.
- **Files to create or modify:** CSS and JSX across all four apps; `frontend/shared/src/hooks/useBreakpoint.js` (new).
- **Implementation notes:** Breakpoints at 640/768/1024/1280 (Tailwind defaults). Explorer grid collapses to single column below 640px. Workbench attribute form becomes a bottom sheet on mobile. All interactive elements ≥ 44×44 CSS px per WCAG 2.5.5 target size. Every image has `alt` text; every form input has an associated `<label>`; tab order is logical; visible focus rings on all focusable elements. Run `@axe-core/cli` against each built app.
- **Acceptance criteria:** `npx @axe-core/cli http://localhost:5173` against all four apps reports zero critical and zero serious violations; manual check at 360px wide shows no horizontal scrollbars on any primary screen.
- **Depends on:** B-3, B-4, B-5, B-6.

#### Task B-8: Deployment to Vercel (Free Tier)
- **Goal:** All four apps deployable by pushing to `main`; preview deployments on PRs.
- **Files to create or modify:** `frontend/vercel.json` (new), `.github/workflows/deploy_frontend.yml` (new), per-app `vite.config.js` `build.outDir` settings.
- **Implementation notes:** Configure Vercel as a monorepo with four projects (one per app) or a single project serving all four at subpaths (`/`, `/workbench`, `/monitor`, `/admin`) via rewrites in `vercel.json`. The single-project approach is simpler for portfolio use and stays well inside the Hobby plan's 100 GB bandwidth/month. Environment variables `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` set in Vercel dashboard. Preview deployments automatically provisioned for every PR.
- **Free tier note:** Vercel Hobby plan allows unlimited sites, 100 GB/month bandwidth, and preview deployments — no meaningful limit for a portfolio piece. Non-commercial use only, which a portfolio qualifies as.
- **Acceptance criteria:** Pushing a PR triggers a preview URL comment; merging to `main` updates the production URL; `VITE_USE_MOCKS=true` build still works for offline demos.
- **Depends on:** B-7.

#### Task B-9: Mock-to-Live Swap (FINAL TASK — joint with Engineer A)
- **Goal:** Replace mocks with real backend and run end-to-end smoke test.
- **Files to create or modify:** `frontend/shared/src/api-client.js` (flip default), `frontend/.env.production`, `README.md`.
- **Implementation notes:** Done in a joint session with Engineer A. Set `VITE_USE_MOCKS=false` and `VITE_API_BASE_URL` to the deployed Render URL. Walk through each journey once with both engineers watching, noting any contract mismatches. Any mismatch found is a contract bug and must be fixed in both places simultaneously. Update the root README with the live URLs and the portfolio blurb.
- **Acceptance criteria:** A fresh supervisor user can, on the deployed site: sign in, upload one image in admin, tag it in workbench, see it appear in explorer with science features and trust badges, and view its contribution on the monitor IRR table — all without console errors.
- **Depends on:** B-8, A-12.

---

# COORDINATION MAP

| Sync Point | Track A Deliverable | Track B Dependency |
|---|---|---|
| Pre-sprint (day 0) | `/docs/CONTRACT.md` committed to `main` | All of Track B reads this as the source of truth for mocks and types. |
| Mid-sprint checkpoint | Trust envelope schema finalized in `backend/schemas/science.py` (Task A-7) | `TrustBadge` component rendering logic (Task B-2) uses the exact `evaluation_status` enum values. |
| End-of-sprint joint session | Render deployment URL and live JWT issuance working (Task A-12) | Mock-to-live swap (Task B-9). |

**Three sync points — inside the stated budget of four.** The contract document absorbs what would otherwise have been a dozen coordination moments: endpoint shapes, error formats, auth header conventions, pagination, and the trust envelope are all resolved on day zero, so Engineer B proceeds against a stable target and Engineer A proceeds without frontend input until deployment day.

**Branching strategy.** Both engineers branch from `main` immediately after the pre-sprint merge. Engineer A works on `track-a-backend-ml` and Engineer B on `track-b-frontend-ux`. Within each track, use short-lived feature branches (`track-a/auth-supabase`, `track-b/workbench-form`) that open PRs back into the track branch; Engineer A reviews Engineer B's PRs for contract conformance only (not CSS), and Engineer B reviews Engineer A's PRs for API-shape conformance only (not SQL). Track branches merge into `main` in this order: Track A first (producing the live API), then Track B's `B-9` (swap + smoke) in a joint session, then a final squash merge of `main` onto itself with the portfolio-ready tag `v1.0.0`.

**The one joint task.** Task B-9 — mock-to-live swap with end-to-end smoke test — is performed by both engineers in one screen-sharing session lasting approximately one hour. The smoke test command sequence lives in `docs/SMOKE_TEST.md` and is the final acceptance gate for the portfolio piece.

---

## References

Brown, L. D., Cai, T. T., & DasGupta, A. (2001). Interval estimation for a binomial proportion. *Statistical Science*, 16(2), 101–133. https://doi.org/10.1214/ss/1009213286

Fowler, M. (2018). *Refactoring: Improving the design of existing code* (2nd ed.). Addison-Wesley.

Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159–174. https://doi.org/10.2307/2529310

Nygard, M. T. (2018). *Release it! Design and deploy production-ready software* (2nd ed.). Pragmatic Bookshelf.

Raschka, S. (2020). Model evaluation, model selection, and algorithm selection in machine learning. *arXiv Preprint*. https://doi.org/10.48550/arXiv.1811.12808

Richardson, C. (2018). *Microservices patterns: With examples in Java*. Manning.

Sculley, D., Holt, G., Golovin, D., Davydov, E., Phillips, T., Ebner, D., Chaudhary, V., Young, M., Crespo, J.-F., & Dennison, D. (2015). Hidden technical debt in machine learning systems. *Advances in Neural Information Processing Systems*, 28, 2503–2511. https://doi.org/10.5555/2969442.2969519

Sheng, V. S., Provost, F., & Ipeirotis, P. G. (2008). Get another label? Improving data quality and data mining using multiple, noisy labelers. In *Proceedings of the 14th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 614–622). https://doi.org/10.1145/1401890.1401965

Web Content Accessibility Guidelines (WCAG) 2.1. (2018). W3C Recommendation. https://www.w3.org/TR/WCAG21/


User:
Review the four documents you just produced and check specifically for:
1. Any task in Track A or Track B that requires a file path not established in the 
   pre-sprint folder structure — flag it and suggest where the file belongs
2. Any acceptance criterion that is subjective or untestable by an LLM agent — 
   rewrite it as a concrete command or observable output
3. Any free-tier service mentioned without a stated usage limit — add the limit
4. The coordination map — if there are more than four sync points, identify which 
   task is causing the excess coupling and suggest how to restructure it
Only output the flagged items and their fixes. Do not reprint the full documents.


Claude:
# Review Findings

## 1. File paths not in the pre-sprint folder structure

**Task A-2** — `backend/middleware/request_context.py`. The pre-sprint tree does not declare `backend/middleware/`.
*Fix:* Add `backend/middleware/` to the pre-sprint folder structure with the comment "cross-cutting request middleware (logging, rate limit, metrics)", or relocate to `backend/services/middleware/`. Recommend the former — middleware is not business logic.

**Task A-5** — `backend/middleware/ratelimit.py`. Same issue.
*Fix:* Same resolution as A-2; both files land in the newly declared `backend/middleware/` directory.

**Task A-6** — `backend/database/alembic/`, `backend/database/alembic.ini`, `backend/database/migrations/versions/`. Pre-sprint declares `backend/database/` but not these children, and the Alembic convention is `alembic/versions/` not `migrations/versions/`.
*Fix:* Standardize on `backend/database/alembic/` containing `alembic.ini`, `env.py`, and `versions/`. Remove the confusing dual `migrations/` path from A-6.

**Task A-8** — `backend/science/evaluation/affordance_eval.py`. Pre-sprint declares `backend/science/` but no `evaluation/` subpackage.
*Fix:* Add `backend/science/evaluation/` to the pre-sprint structure with comment "held-out validation scripts producing ML_EVALUATION.md inputs".

**Task A-9** — `backend/science/evaluation/vision_eval.py` and `backend/science/evaluation/test_sets/rooms.csv`. Same missing directory; additionally, a curated CSV test set is data, not code.
*Fix:* Place evaluation scripts in the new `backend/science/evaluation/`; place gold-label CSVs in `backend/science/evaluation/test_sets/` and declare both in the pre-sprint tree.

**Task A-10** — `backend/api/health.py` and `backend/middleware/metrics.py`. The inventory shows existing routers named `v1_*.py` under `backend/api/`, so `health.py` breaks the naming convention; `middleware/metrics.py` hits the undeclared directory again.
*Fix:* Rename to `backend/api/v1_health.py` for consistency with siblings. Metrics middleware lands in the newly declared `backend/middleware/`.

**Task A-11** — `backend/tests/integration/`. Pre-sprint declares `backend/tests/` but no `integration/` subfolder.
*Fix:* Add `backend/tests/integration/` and `backend/tests/unit/` to the pre-sprint tree; this is a minor clarification but worth committing so imports and `pytest` discovery paths are stable.

**Task B-2** — `frontend/shared/preview.html` is mentioned as an alternative to Storybook. Not flagged as a tree violation but ambiguous.
*Fix:* Pick one in the pre-sprint addendum: either commit to `frontend/shared/preview.html` as the component gallery, or add `frontend/shared/.storybook/`. Recommend the plain HTML preview — zero new dependencies.

## 2. Subjective or untestable acceptance criteria

**Task A-2** — "stdout shows one JSON log line per request with parseable fields."
*Rewrite:* `curl -s http://localhost:8000/health > /dev/null && docker compose logs backend --tail 1 | python -c "import sys, json; d=json.loads(sys.stdin.read().split(' ', 1)[1]); assert {'request_id','method','path','status','duration_ms'} <= d.keys()"` exits 0.

**Task A-5** — "receives at least five 429 responses."
*Rewrite:* `pytest backend/tests/integration/test_ratelimit.py::test_upload_burst_returns_429 -v` passes, where the test fires 25 requests in one second via `httpx.AsyncClient` and asserts `sum(1 for r in responses if r.status_code == 429) >= 5`.

**Task A-8** — "the trust envelope for each affordance output reflects the same verdict at runtime."
*Rewrite:* `pytest backend/tests/integration/test_science_trust.py::test_affordance_envelope_matches_registry -v` passes, where the test calls the pipeline on a fixture image and asserts that for each of the five affordance model IDs, the returned envelope's `evaluation_status` equals the value in `docs/ML_EVALUATION.md`'s machine-readable companion file `backend/science/data/affordance_models/evaluation_index.json`.

**Task A-9** — "the frontend receives `evaluation_status: validated` on room detection outputs for classes that meet a ≥0.70 precision threshold."
*Rewrite:* `python -m backend.science.evaluation.vision_eval --assert-thresholds` exits 0 when the generated `backend/science/data/vision_models/room_detection_eval.json` shows per-class precision ≥ 0.70 for all classes marked `validated`, and `curl -s http://localhost:8000/v1/explorer/images/1 | jq '.science.features.room_type.evaluation_status'` returns `"validated"` for a fixture image of a validated class.

**Task A-10** — "within 2 seconds."
*Rewrite:* `docker compose stop db && sleep 1 && curl -s -o /dev/null -w "%{http_code}" --max-time 2 http://localhost:8000/health` returns `503`.

**Task A-12** — "a fresh tagger can sign in via the frontend and submit one validation against the deployed instance."
*Rewrite:* `bash docs/smoke_deployed.sh` exits 0, where the script performs: (a) `curl $RENDER_URL/health` returns 200 with `db: true`, (b) a test JWT for role `tagger` is minted and POSTs a fixture validation to `$RENDER_URL/v1/workbench/validate` returning 200, (c) the same record is retrievable via `$RENDER_URL/v1/explorer/images/{id}`.

**Task B-2** — "automated `axe-core` run against the preview reports zero critical violations."
*Rewrite:* `npx @axe-core/cli http://localhost:5173/preview.html --exit` exits 0 and reports zero `critical` and zero `serious` violations in the JSON output.

**Task B-3** — "Lighthouse performance score ≥ 85 on localhost for the explorer route."
*Rewrite:* `npx lighthouse http://localhost:5173 --only-categories=performance --chrome-flags="--headless" --output=json --output-path=/tmp/lh.json && node -e "process.exit(require('/tmp/lh.json').categories.performance.score >= 0.85 ? 0 : 1)"` exits 0.

**Task B-4** — "Tagging ten mock images with keyboard only (no mouse) completes without errors."
*Rewrite:* `npx playwright test frontend/apps/workbench/tests/keyboard.spec.ts` passes, where the Playwright test disables mouse events and uses `page.keyboard.press()` to submit ten validations, asserting no console errors and ten successful submissions in the mock client's call log.

**Task B-5** — "hovering a velocity point shows timestamp and count."
*Rewrite:* `npx playwright test frontend/apps/monitor/tests/irr.spec.ts` passes, where the test asserts that `page.locator('.recharts-tooltip-wrapper')` becomes visible on `page.hover('.recharts-dot')` and contains text matching `/\d{4}-\d{2}-\d{2}/` and `/count:\s*\d+/`.

**Task B-6** — "shows an inline error before any network call."
*Rewrite:* `npx playwright test frontend/apps/admin/tests/upload_validation.spec.ts` passes, where the test attaches 201 files, asserts the error banner text contains `"200"`, and asserts `page.on('request')` recorded zero requests to `/v1/admin/upload`.

**Task B-7** — "manual check at 360px wide shows no horizontal scrollbars on any primary screen."
*Rewrite:* `npx playwright test frontend/tests/responsive.spec.ts` passes, where the test sets `viewport: {width: 360, height: 800}`, visits each app's primary route, and asserts `await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)` returns `true` on each.

**Task B-9** — "noting any contract mismatches... without console errors."
*Rewrite:* `bash docs/smoke_deployed.sh` (same script as A-12) exits 0, plus `npx playwright test frontend/tests/e2e_deployed.spec.ts --config=playwright.deployed.config.ts` passes, where the test exercises sign-in, admin upload, workbench submission, explorer detail view, and monitor IRR read, asserting `page.on('pageerror')` captured zero errors across the full run.

## 3. Free-tier services without stated usage limits

**Task A-3 (Supabase Auth)** — limit was stated (50,000 MAU, unlimited auth API calls). No fix needed.

**Task A-10 (Sentry)** — limit was stated (5,000 errors/month). No fix needed.

**Task A-12 (Render Web Service and Render Postgres)** — limits stated (750 hours/month, sleep after 15 min; Postgres 1 GB and 90-day expiry). No fix needed.

**Task A-12 (Supabase Storage)** — stated as "1 GB" but missing bandwidth and request limits.
*Fix:* Add: "Supabase Storage free tier: 1 GB storage, 5 GB egress/month, 2 GB cached egress. A portfolio piece serving ≤ 500 images at ≤ 2 MB each stays well inside both."

**Task A-12 (Supabase PostgreSQL alternative)** — stated as "500 MB, no expiry" but missing connection and bandwidth limits.
*Fix:* Add: "Supabase free Postgres: 500 MB storage, 60 concurrent connections, 5 GB egress/month, auto-paused after 7 days of inactivity (wakes on first query)."

**Task B-8 (Vercel Hobby)** — partially stated (100 GB bandwidth, non-commercial). Missing build minutes and serverless function limits.
*Fix:* Add: "Vercel Hobby: 100 GB bandwidth/month, 6,000 build minutes/month, 100 GB-hours serverless function execution, deployment limit 100/day. Since all four apps are static Vite builds, serverless limits are moot."

**Task B-1 (MSW)** — mentioned as a tool but MSW is a library, not a hosted service. No limit applies. No fix needed.

## 4. Coordination map — sync point count

The coordination map lists three sync points, which is inside the stated budget of four. **No excess coupling.** However, one latent coupling risk was not called out and should be added as an explicit fourth sync point rather than discovered as a surprise:

**Missing sync point:** the `evaluation_index.json` file introduced in the rewritten A-8 acceptance criterion is read by both the backend trust envelope (Task A-7/A-8) and — indirectly, via the API response — the frontend `TrustBadge` (Task B-2). The enum values (`validated`, `proxy_validated`, `untested`) must match exactly on both sides.

*Fix:* Promote the enum to `docs/CONTRACT.md` as a frozen three-value set committed during the pre-sprint, so that neither engineer can unilaterally introduce a fourth status (e.g., `preliminary`, `deprecated`) mid-sprint. This keeps the coordination map at three runtime sync points while eliminating the hidden coupling at zero cost — it is a contract clarification, not a new meeting.
