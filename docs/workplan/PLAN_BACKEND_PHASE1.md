# BACKEND PHASE 1

**Owner:** Engineer A. **Scope:** everything under `/backend/`, `/deploy/`, and deploy-facing docs needed for a v1 release. **Out of scope:** anything under `/frontend/`, formal ML evaluation reports, and optional hardening that does not block v1.

Required v1 coordination note: `docs/workplan/COORDINATION.md` is part of the execution authority for this track. Coordination Tasks C-1, C-1.5, and C-2 are mandatory supporting tasks for the Phase 1 release and are not optional reference material.

## Phase 1 End State

Phase 1 is complete when:

- protected routes enforce bearer JWT auth using the contract-defined claims
- all v1 endpoints validate input and return structured errors
- the backend emits request-scoped logs
- ML outputs are returned in the trust-envelope format, with `untested` used honestly where evidence is missing
- smoke-critical integration tests cover the explorer, workbench, admin, and monitor paths used by the v1 runbook
- the backend is deployable from committed repo configuration and passes the backend-owned portions of the shared smoke runbook

Phase 1 does **not** claim:

- formal statistical validation of the ML models
- upgraded `validated` status without evidence
- production-grade abuse protection beyond the basic auth and validation boundary
- Prometheus `/metrics`, full Alembic replacement, broad endpoint-group integration coverage, Sentry integration, GitHub deploy automation, and the dedicated monitor seed workflow

## Task List

#### Task A-1: Environment & Secrets Management
- **Goal:** Eliminate all hardcoded secrets and fail-fast on missing configuration.
- **Files to create or modify:** `backend/settings.py` (new, using `pydantic-settings`), `backend/main.py`, `deploy/docker-compose.yml`, `.env.example`.
- **Implementation notes:** This task absorbs the deferred pre-sprint setup work for secret externalization and local backend bootstrap. Use the environment variable list in `/docs/CONTRACT.md` as the baseline source of names for `.env.example`, adding any backend-only runtime variables discovered during implementation. Use `pydantic_settings.BaseSettings` with `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`. All settings (`database_url`, `supabase_jwt_secret`, `cors_allowed_origins`, `vlm_hard_limit_usd`) must be typed and required (no default) for production-critical ones; dev defaults allowed only when `ENVIRONMENT=development`. Raise `RuntimeError` in `main.py` lifespan startup if any required var is unset in production mode. Remove all `os.getenv(..., "dev_secret_key_change_me")` occurrences.
- **Acceptance criteria:** `ENVIRONMENT=production uvicorn backend.main:app` fails immediately with a clear message when `SUPABASE_JWT_SECRET` is unset; `grep -rn "dev_secret_key_change_me\|tagger_pass" backend/ deploy/` returns zero matches; after creating `.env` from `.env.example` with local dev values, `uvicorn backend.main:app --reload` starts successfully from repo root.
- **Depends on:** pre-sprint only.

#### Task A-2: Structured Logging and Request Middleware
- **Goal:** Replace `print()` and default logging with JSON structured logs, request IDs, and timing middleware.
- **Files to create or modify:** `backend/logging_config.py` (new), `backend/middleware/request_context.py` (new), `backend/main.py`, `backend/services/auth.py`.
- **Implementation notes:** Use `structlog` configured to emit JSON to stdout. Middleware generates a `request_id` (uuid4), attaches it to a `contextvars.ContextVar`, binds it to the logger, and includes it in the `X-Request-ID` response header. Log one line per request at INFO with method, path, status, duration_ms, user_id, role. Use `logger.warning` for failed admin auth attempts with the attempted user id.
- **Acceptance criteria:** `curl -v http://localhost:8000/health` response contains `X-Request-ID`; stdout shows one JSON log line per request with parseable fields; `grep -rn "print(" backend/services/ backend/api/` returns zero matches.
- **Depends on:** A-1.

#### Task A-3: Authentication via Supabase Auth
- **Goal:** Replace header-trust auth with JWT validation against a free-tier identity provider.
- **Files to create or modify:** `backend/services/auth.py` (rewrite), `backend/tests/test_auth.py` (new).
- **Implementation notes:** Use `python-jose` to verify JWTs signed by Supabase using HS256 and `SUPABASE_JWT_SECRET`. Extract `sub` as user id and top-level `role` as the authorization role claim. Provide FastAPI dependencies `require_tagger`, `require_scientist`, `require_supervisor`, `require_admin`. Explorer routes remain public and must not require auth headers. Reject any request without a valid bearer token on protected routes with 401; reject mismatched roles with 403. Keep a single `dev_bypass_token` path guarded by `ENVIRONMENT=development` for local work.
- **Acceptance criteria:** `pytest backend/tests/test_auth.py -k "valid_admin_jwt"` passes; the same test with a tampered signature returns 401; a valid tagger JWT hitting `/v1/admin/budget` returns 403.
- **Depends on:** A-1, A-2.

#### Task A-4: Input Validation and Error Handling on All Endpoints
- **Goal:** Every endpoint validates input via Pydantic and returns structured error responses; no unhandled exceptions escape.
- **Files to create or modify:** all files under `backend/api/v1_*.py`, `backend/schemas/*.py`, `backend/main.py`.
- **Implementation notes:** Tighten Pydantic schemas: `Field(ge=1)` on page, `Field(max_length=...)` on all free-text strings, `conlist` on batch endpoints. Register exception handlers in `main.py` so validation failures and runtime failures both return the shared `ErrorResponse` contract from `/docs/CONTRACT.md`: `{ error: { code, message, request_id, details? } }`, with `code: "VALIDATION_ERROR"` and canonical `message: "Request validation failed"` for every query, body, and multipart validation failure, including `POST /v1/admin/upload`. Log unexpected exceptions with stack traces at ERROR. Wrap the upload commit in `try/except` with explicit `db.rollback()` on failure. Remove runtime clamping logic now handled by schema.
- **Acceptance criteria:** `curl -s -o /tmp/a4.json -w "%{http_code}" "http://localhost:8000/v1/explorer/search?page=-5"` returns `422`, and `jq -e '.error.code == "VALIDATION_ERROR" and .error.message == "Request validation failed" and (.error.request_id | type == "string") and (.error.details | type == "array") and (.error.details[0].field == "page")' /tmp/a4.json` exits `0`, asserting the shared `{ error: { code, message, request_id, details } }` shape for the `GET /v1/explorer/search` validation error; `curl -s -o /tmp/a4-upload.json -w "%{http_code}" -X POST http://localhost:8000/v1/admin/upload` with an invalid multipart payload returns a non-2xx response and `jq -e '.error.code == "VALIDATION_ERROR" and .error.message == "Request validation failed"' /tmp/a4-upload.json` exits `0`; `pytest backend/tests/integration/test_errors.py::test_db_error_returns_request_id -v` passes; `rg -n "db.rollback\\(" backend/api backend/services` shows an explicit rollback in each mutating database-write path.
- **Depends on:** A-2.

#### Task A-7: ML Trust Envelope and Feature Registry Refactor
- **Goal:** Every ML output passes through a uniform trust envelope declaring its evaluation status.
- **Files to create or modify:** `backend/science/trust.py` (new), `backend/science/pipeline.py`, `backend/science/features_registry.py`, `backend/schemas/science.py`, `backend/tests/test_science_schema.py` (new or updated).
- **Implementation notes:** Define `TrustEnvelope` Pydantic model matching the contract. Mark each feature in the canonical feature registry with one of `validated`, `proxy_validated`, `untested`. The pipeline assembly code wraps every feature output directly inside `SciencePayload.features`; do not emit a separate feature-confidence map. For legacy features without metadata, default to `untested`. Verification for this task is test-driven, not seed-driven: use `backend/tests/test_science_schema.py` to construct controlled pipeline-output fixtures in-process and validate them against `SciencePayload` or the final response-assembly function, rather than depending on a seeded image ID or a live `curl` target. Phase 1 stops here: it establishes the mechanism for honest trust display without requiring immediate evidence collection.
- **Acceptance criteria:** Running `pytest backend/tests/test_science_schema.py -k "trust_envelope or legacy_feature_untested or missing_evaluation_status" -v` passes; those tests assert that every feature is serialized as an object containing `value`, `model_id`, `evaluation_status`, `confidence_interval_95`, `n_training`, and `notes`, that `.science` does not expose any separate `confidence` map for features, that a pipeline output missing `evaluation_status` fails schema validation, and that at least one legacy feature without registry metadata is returned with `evaluation_status == "untested"`.
- **Depends on:** A-4.

#### Task A-10: Health Check and Observability Baseline
- **Goal:** `/health` performs real dependency checks; Phase 1 observability stops at request-scoped structured logs and a truthful health endpoint.
- **Files to create or modify:** `backend/api/health.py` (new), `backend/main.py`.
- **Implementation notes:** `/health` runs `SELECT 1` against the DB, checks `IMAGE_STORAGE_ROOT` is writable, and returns `{status: "ok"|"degraded", db: bool, storage: bool, version: str}`. Do not add a `/metrics` endpoint in Phase 1; Prometheus instrumentation is explicitly deferred to follow-up work. Do not add Sentry in Phase 1.
- **Acceptance criteria:** With the app running, `curl -s -o /tmp/health.json -w "%{http_code}" http://localhost:8000/health` returns `200` and `jq -e '.status == "ok" and .db == true and .storage == true and (.version | type == "string")' /tmp/health.json` exits `0`; after stopping the database dependency, the same command returns `503` and `jq -e '.db == false' /tmp/health.json` exits `0` within 2 seconds; `rg -n '"/metrics"|prometheus-client|http_requests_total|http_request_duration_seconds_bucket|ml_pipeline_runs_total' backend/ deploy/` returns no matches added for Phase 1 observability work.
- **Depends on:** A-2.

#### Task A-11: Integration Tests — Smoke-Critical Coverage Only
- **Goal:** Cover the smoke-critical backend flows with integration tests instead of full endpoint-group exhaustiveness.
- **Files to create or modify:** `backend/tests/integration/test_explorer.py`, `backend/tests/integration/test_workbench.py`, `backend/tests/integration/test_admin.py`, `backend/tests/integration/test_monitor.py`, `backend/tests/conftest.py`, `.github/workflows/test_backend.yml` (new or updated).
- **Implementation notes:** Use `pytest`, `httpx.AsyncClient`, and a per-test SQLite-in-memory override of `DATABASE_URL` via dependency injection. Provide fixtures that mint test JWTs with arbitrary roles using the same `SUPABASE_JWT_SECRET` the app uses in test mode. Follow Arrange-Act-Assert. Phase 1 coverage is limited to the deployed smoke journey and its critical failure modes: anonymous explorer search/detail, protected workbench next/validate, admin upload/budget/kill-switch auth boundary, monitor velocity/irr shape including `{ rows: [] }`, and shared validation/auth error shapes. Add or update the backend CI workflow so the repo contains a concrete `pytest` invocation for these smoke-critical integration tests. Do not introduce `test_bn_export.py`; BN export is not in the v1 contract.
- **Acceptance criteria:** `pytest backend/tests/integration/test_explorer.py backend/tests/integration/test_workbench.py backend/tests/integration/test_admin.py backend/tests/integration/test_monitor.py -v` passes; the CI workflow contains a concrete `pytest` invocation for those smoke-critical integration tests and does not enforce a Phase 1 coverage threshold; no file named `backend/tests/integration/test_bn_export.py` is introduced by this task.
- **Depends on:** A-3, A-4, A-7, A-10.

#### Task A-12a: Backend Deployment Repo Configuration
- **Goal:** Make the repository deployable to Render from code and config alone.
- **Files to create or modify:** `render.yaml` (new), `deploy/Dockerfile.backend`, `docs/SMOKE_TEST.md`.
- **Implementation notes:** This is the agent-executable portion of deployment work. Use Render's free Web Service + free PostgreSQL in the repo configuration. `render.yaml` declares the service and database. The Dockerfile adds a non-root user and starts `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`; if the current repo already has a stable startup migration/bootstrap command, preserve it, but do not make full Alembic adoption a Phase 1 prerequisite. Image storage uses Supabase Storage rather than Render's ephemeral disk. Create `docs/SMOKE_TEST.md` with the deployed smoke sequence for public explorer plus protected admin/workbench/monitor flows using placeholder env vars for short-lived JWTs. Engineer A owns JWT provisioning for the smoke session: create the three Supabase Auth test identities with `admin`, `tagger`, and `supervisor` role claims, then obtain fresh access tokens immediately before the session and export them locally as `SMOKE_ADMIN_JWT`, `SMOKE_TAGGER_JWT`, and `SMOKE_SUPERVISOR_JWT`. The runbook must reference only those env var names and must never contain raw tokens or passwords. The upload contract is asynchronous: `/v1/admin/upload` must return `job_id`, `items`, created `image_ids`, and `status: "queued"`, the uploaded smoke-test image must become reachable at `GET /v1/explorer/images/{image_id}` within 5 seconds, and its science payload must reach `run_status: "completed"` within 60 seconds for the smoke test. For monitor in Phase 1, the runbook must state the contracted response shape and the manual prerequisite that monitor data must already exist; the dedicated seed automation is deferred to Phase 2.
- **Acceptance criteria:** `test -f render.yaml && test -f deploy/Dockerfile.backend && test -f docs/SMOKE_TEST.md` exits `0`; `rg -n "SMOKE_ADMIN_JWT|SMOKE_TAGGER_JWT|SMOKE_SUPERVISOR_JWT|Engineer A" docs/SMOKE_TEST.md` returns matches; `rg -n "seed_monitor_smoke\\.py|deploy_backend\\.yml|Sentry|prometheus-client|alembic upgrade head" docs/SMOKE_TEST.md deploy/Dockerfile.backend render.yaml` returns no Phase 1-only implementation dependency on those deferred items; `rg -n "eyJ[A-Za-z0-9_-]{10,}" docs/SMOKE_TEST.md` returns no matches so no raw JWT-like strings were committed.
- **Depends on:** A-1, A-10, A-11.

#### Task A-12b: Backend Platform Provisioning and Live Verification
- **Goal:** Verify the configured backend deployment against actual Render, Supabase, and GitHub platform state.
- **Human-owned prerequisites:** A Render Web Service exists and is linked to the repo; a Render PostgreSQL instance exists; the required backend secrets and env vars are populated in Render/GitHub; a Supabase project exists with Auth and Storage configured; Engineer A can obtain short-lived JWTs for `admin`, `tagger`, and `supervisor`.
- **Files to create or modify:** none required beyond Task A-12a unless a repo-config correction is discovered during verification.
- **Implementation notes:** This is the human-verification portion of deployment work. Do not hand this task to an agent as if repo context alone were sufficient. Use the repo configuration from Task A-12a plus the live platform accounts above. If platform verification reveals a repo defect, fix it in a follow-up commit against the same task chain.
- **Acceptance criteria:** A human Render deploy using the committed Phase 1 repo configuration produces a live backend; the deployed `/health` endpoint returns `200` with `db: true`; a valid admin upload returns `status: "queued"` and at least one created `image_id`; the uploaded smoke-test image is reachable via `GET /v1/explorer/images/{image_id}` within 5 seconds and reaches `science.run_status: "completed"` within 60 seconds; using a valid `SMOKE_TAGGER_JWT`, one validation can be submitted successfully against the deployed instance; if monitor data already exists in the target environment, the deployed `/v1/monitor/irr` endpoint returns the contracted `{ rows: [...] }` shape, otherwise the runbook records monitor as not yet IRR-seeded in Phase 1.
- **Depends on:** A-12a.
