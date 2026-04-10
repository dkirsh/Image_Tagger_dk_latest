# Image Tagger v3.4.74 — Codebase Analysis

## 1. External Dependencies & APIs

### 1.1 Python Dependencies (Dockerfile.backend)

| Category | Package | Version |
|----------|---------|---------|
| **Web** | FastAPI | 0.109.0 |
| | Uvicorn | 0.27.0 |
| **Database** | SQLAlchemy | 2.0.25 |
| | psycopg2-binary | 2.9.9 |
| **Validation** | Pydantic | 2.6.1 |
| | pydantic-settings | 2.1.0 |
| **Auth** | python-jose[cryptography] | 3.3.0 |
| | passlib[bcrypt] | 1.7.4 |
| **Image** | Pillow | 10.2.0 |
| | opencv-python-headless | 4.9.0.80 |
| | scikit-image | 0.22.0 |
| **Numeric** | NumPy | 1.26.3 |
| | SciPy | 1.11.4 |
| **HTTP** | requests | 2.31.0 |
| | httpx | 0.26.0 |
| **AI/VLM** | openai | 1.12.0 |
| | anthropic | 0.33.0 |
| | google-generativeai | 0.8.3 |
| | google-genai | 0.1.0 |
| **Deep Learning** | torch | 2.1.2 |
| | torchvision | 0.16.2 |
| | transformers | 4.49.0 |
| | timm | 1.0.3 |
| **ML** | supervision | 0.22.0 |
| | lightgbm | 4.5.0 |
| **Config** | PyYAML | 6.0.1 |
| **Multipart** | python-multipart | 0.0.7 |
| **Testing** | pytest | 7.4.4 |

### 1.2 JavaScript Dependencies (frontend/)

| Package | Version | Purpose |
|---------|---------|---------|
| react / react-dom | 18.2.0 | UI framework |
| vite | 5.0.0 | Build tool |
| tailwindcss | 3.3.5 | CSS framework |
| recharts | 2.9.0 | Chart components |
| lucide-react | 0.292.0 | Icons |
| concurrently | 8.2.2 | Dev script runner |
| @vitejs/plugin-react | 4.2.0 | Vite React plugin |
| autoprefixer | 10.4.16 | CSS post-processing |
| postcss | 8.4.31 | CSS tooling |

### 1.3 External API Integrations

| Provider | Model | Env Var | Fallback | File |
|----------|-------|---------|----------|------|
| **OpenAI** | GPT-4o / 4o-mini | `OPENAI_API_KEY` | StubEngine | `backend/services/vlm.py` |
| **Anthropic** | Claude 3.5 Sonnet | `ANTHROPIC_API_KEY` | StubEngine | `backend/services/vlm.py` |
| **Google Gemini** | gemini-3.0-flash | `GEMINI_API_KEY` / `GOOGLE_API_KEY` | StubEngine | `backend/services/vlm.py` |

**Provider selection priority:** explicit override > config file (`backend/data/vlm_config.json`) > env var auto-detect > StubEngine (placeholder JSON).

**VLM config admin endpoints:**
- `GET/POST /v1/admin/vlm/config` — read/update VLM settings
- `POST /v1/admin/vlm/test` — test VLM on a single image
- `POST /v1/admin/kill-switch` — disable all paid models

**Cost tracking:** `backend/services/costs.py` logs to `tool_usage` table (model, input/output tokens, cost_usd). Admin dashboard at `/v1/admin/costs/daily` and `/v1/admin/budget`.

### 1.4 Pre-trained Model Downloads

| Model | Source | File | Cache Location |
|-------|--------|------|----------------|
| OneFormer ADE20K (segmentation) | Hugging Face Hub | `backend/science/vision/segmentation.py` | `~/.cache/huggingface/` |
| SigLIP2 (material classification) | Hugging Face Hub | `backend/science/vision/clip_material.py` | `~/.cache/huggingface/` |
| Mask2Former COCO (panoptic) | Hugging Face Hub | `backend/science/vision/mask2former.py` | `~/.cache/huggingface/` |
| ResNet50 Places365 (room detection) | MIT CSAIL HTTP | `backend/science/vision/room_detection.py` | `backend/science/vision/weights/` |
| LightGBM affordance regressors (x5) | Local pickle files | `backend/science/data/affordance_models/` | In-repo |

### 1.5 Docker Base Images

| Service | Image |
|---------|-------|
| Backend | `python:3.11-slim` |
| Frontend (build) | `node:18-alpine` |
| Frontend (runtime) | `nginx:alpine` |
| Database | `postgres:15-alpine` |

### 1.6 Database

- **Engine:** PostgreSQL 15
- **Connection:** `DATABASE_URL` env var, default `postgresql://user:password@localhost:5432/image_tagger_v3`
- **ORM:** SQLAlchemy 2.0 with `pool_pre_ping=True`
- **Docker credentials:** `tagger` / `tagger_pass` (hardcoded in `docker-compose.yml`)

---

## 2. Data Flows

### 2.1 Image Ingestion

```
Admin Upload (POST /v1/admin/upload) or Seed (POST /v1/explorer/seed)
  -> Validate file type (.jpg/.jpeg/.png/.webp), max 10 MiB, max 200/batch
  -> Store to IMAGE_STORAGE_ROOT with UUID filename
  -> INSERT into `images` table (source="admin_upload" | "import")
  -> INSERT into `upload_jobs` + `upload_job_items` (status=PENDING)
  -> Background: run_upload_job() -> SciencePipeline -> INSERT `validations`
```

**Entry points:**
- `backend/api/v1_admin.py::upload_images()` (POST `/v1/admin/upload`)
- `backend/api/v1_discovery.py::seed_sample_images()` (POST `/v1/explorer/seed`)

**Tables touched:** `images`, `upload_jobs`, `upload_job_items`, `validations`

### 2.2 Human Tagging (HITL)

```
GET /v1/workbench/next
  -> "least validated" queue: fewest validations first, excludes images already tagged by user
  -> Returns image with metadata and URL

POST /v1/workbench/validate
  -> Auth via X-User-Id / X-User-Role headers
  -> INSERT `validations` (source="manual", includes duration_ms for spam detection)

POST /v1/workbench/region
  -> INSERT `regions` with geometry JSON, auto_label, manual_label
```

**Entry points:**
- `backend/api/v1_annotation.py::get_next_image()`
- `backend/api/v1_annotation.py::submit_validation()`
- `backend/api/v1_annotation.py::create_region()`

**Tables touched:** `images`, `validations`, `regions`, `users`, `attributes`

### 2.3 Science Pipeline (Automated Analysis)

```
Trigger: upload job | POST /v1/explorer/science/bootstrap | manual admin
  -> ensure_science_run() -> INSERT `science_runs` (status=PENDING)
  -> mark_run_started() -> status=RUNNING
  -> L0:    Color, Complexity, Texture, Fractal, Symmetry analyzers
  -> L1:    Naturalness, Fluency, Biophilia, Depth/Spatial
  -> L1.5:  Segmentation (OneFormer ADE20K)
  -> L1.55: Materials (heuristic, optional VLM, optional CLIP)
  -> L1.8:  Affordance prediction (LightGBM, 5 regressors)
  -> L2:    Cognitive + Semantic (VLM, if enabled)
  -> INSERT `validations` (source="science_pipeline_v3.4")
  -> INSERT `science_artifacts` (affordance_json, room_json, materials_json)
  -> derive_all_tags() -> INSERT `science_tags` (is_canonical=True)
  -> mark_run_completed()
```

**Entry points:**
- `backend/science/pipeline.py::SciencePipeline.process_image_canonical()`
- `backend/services/science_runs.py::ensure_science_run()`
- `backend/api/v1_discovery.py::bootstrap_science()`

**Tables touched:** `science_runs`, `validations`, `science_artifacts`, `science_tags`, `images`, `attributes`

### 2.4 VLM Integration

```
get_vlm_engine() -> detect available backends -> instantiate engine
  -> Encode image as JPEG base64
  -> engine.analyze_image(image_bytes, prompt) -> JSON response
  -> log_vlm_usage() -> INSERT `tool_usage` (provider, model, cost_usd)
  -> Parse JSON -> map to canonical attribute keys
  -> Results stored via science pipeline into `validations`
```

**Entry point:** `backend/services/vlm.py::get_vlm_engine()`

**Tables touched:** `tool_usage`, `validations`

### 2.5 BN Export (Bayesian Network)

```
GET /v1/export/bn-snapshot
  -> _collect_indices_for_image() -> query `validations` (source LIKE "science_pipeline%")
  -> _collect_bins_for_image() -> map numeric to categorical (low/mid/high)
  -> _compute_irr_for_image() -> pairwise agreement across human + pipeline
  -> _bin_irr() -> thresholds: <0.4="low", <0.7="medium", >=0.7="high"
  -> Assemble BNRow -> return CSV/JSON with codebook

POST /v1/explorer/export -> TrainingExporter
  -> Joins Validation + Image rows
  -> Flattens to JSONL (image_id, attribute_key, value, user_id, duration_ms, source)
```

**Entry points:**
- `backend/api/v1_bn_export.py::export_bn_snapshot()`
- `backend/api/v1_discovery.py::export_training_data()`
- `backend/services/training_export.py::TrainingExporter.export_for_images()`

**Tables touched:** `validations`, `images`, `attributes`

### 2.6 Auth Flow

```
Request headers: X-User-Id, X-User-Role, X-Auth-Token
  -> get_current_user() (FastAPI dependency injection)
  -> Privileged roles (admin/supervisor): require X-Auth-Token == API_SECRET
  -> Tagger/scientist: accepted with headers only (no token)
  -> Role decorators: require_tagger(), require_admin(), require_supervisor()
  -> 401 on invalid token for privileged roles
  -> 403 on insufficient role
```

**Entry point:** `backend/services/auth.py::get_current_user()`

### 2.7 Background / Async Processing

| Worker | Trigger | Mechanism |
|--------|---------|-----------|
| Upload job processor | Image upload | `BackgroundTasks` or `scripts/run_upload_job.py` |
| Science bootstrap | `POST /v1/explorer/science/bootstrap` | Daemon thread (up to 500 pending runs) |
| Manual science | `scripts/run_science_on_sample.py` | CLI, single image |
| Backfill script | `backend/scripts/backfill_science_runs.py` | CLI, batch processing |

### 2.8 Data Flow Topology

```
+------------------------------------------------------------------+
| EXTERNAL INPUT SOURCES                                            |
+--------------------+---------------------+-----------------------+
| Admin Upload       | Seed / Import       | Manual Tagging (UI)   |
| (files on disk)    | (JSON config)       | (tagger interaction)  |
+---------+----------+---------+-----------+----------+------------+
          |                    |                       |
          v                    v                       v
+------------------------------------------------------------------+
| API ROUTER LAYER (FastAPI)                                        |
| v1_admin.py     v1_discovery.py     v1_annotation.py              |
| v1_bn_export.py v1_features.py      v1_supervision.py             |
| v1_debug.py     v1_vlm_health.py                                  |
+---------+----------+---------+-----------+----------+------------+
          |                    |                       |
          v                    v                       v
+------------------------------------------------------------------+
| SERVICE LAYER                                                     |
| AnnotationService   SciencePipeline   TrainingExporter            |
| StorageService      AuthService       UploadJobs                  |
| VLMEngine           CostTracker       ScienceRuns                 |
+---------+----------+---------+-----------+----------+------------+
          |                    |                       |
          v                    v                       v
+------------------------------------------------------------------+
| DATA ACCESS LAYER (SQLAlchemy ORM)                                |
| Images  Validations  Regions  ScienceRuns  ScienceArtifacts       |
| Users   Attributes   Jobs     ScienceTags  ToolUsage              |
+---------+----------+---------+-----------+----------+------------+
          |                    |                       |
          v                    v                       v
+------------------------------------------------------------------+
| STORAGE LAYER                                                     |
| PostgreSQL 15              data_store/ (filesystem)               |
| (all relational data)      (raw image files)                      |
+------------------------------------------------------------------+
```

---

## 3. Missing Production Requirements

### 3.1 CRITICAL — Immediate Fix Required

| # | Gap | Detail | File(s) |
|---|-----|--------|---------|
| 1 | **Hardcoded secrets** | `API_SECRET` defaults to `"dev_secret_key_change_me"`; DB creds hardcoded in docker-compose (`tagger`/`tagger_pass`) | `auth.py:10`, `docker-compose.yml:9-11,30` |
| 2 | **No error handling on core endpoints** | `v1_annotation.py` has zero try/except blocks; upload commit can partially fail without rollback | `v1_annotation.py`, `v1_admin.py` |
| 3 | **No rate limiting** | None on any endpoint — upload, auth failures, VLM calls all unbounded | All routers |
| 4 | **Containers run as root** | No `USER` directive in either Dockerfile | `Dockerfile.backend`, `Dockerfile.frontend` |
| 5 | **No HTTPS** | Nginx listens on port 80 only, no TLS config, no HSTS headers | `nginx.conf` |
| 6 | **Manual database migrations** | No Alembic; migration scripts must be run manually inside container, no rollback | `backend/scripts/migrate_*.py` |
| 7 | **Security logging via print()** | Failed admin auth logged with `print()` instead of `logger` | `auth.py:41` |

### 3.2 HIGH — Important for Production

| # | Gap | Detail |
|---|-----|--------|
| 1 | **No centralized logging** | No log config in `main.py`; no structured/JSON logging; no request/response logging middleware |
| 2 | **No audit trail** | Admin operations (kill-switch, config changes, uploads) not logged; no who-modified-what-when |
| 3 | **Weak auth model** | Token is plain string comparison (not cryptographically signed), no expiration, no refresh, no CORS middleware |
| 4 | **Tagger role unauthenticated** | Any request with `X-User-Role: tagger` is accepted without a token |
| 5 | **Default user ID** | Missing `X-User-Id` header silently defaults to `"1"` |
| 6 | **No DB transaction rollback** | Relies on SQLAlchemy autocommit; no explicit rollback on failures; partial batch failures possible |
| 7 | **Health check incomplete** | `/health` returns version+status but does not check DB connectivity, disk space, or VLM availability |
| 8 | **No resource limits** | `docker-compose.yml` has no `mem_limit` or `cpus` constraints; backend can OOM |
| 9 | **Minimal test coverage** | Only 8 test functions in `test_v3_api.py`; most endpoints completely untested (see 3.6) |

### 3.3 MEDIUM — Should Fix Before Production

| # | Gap | Detail |
|---|-----|--------|
| 1 | **No `.env.example`** | No documentation of required/optional env vars |
| 2 | **No graceful shutdown** | No SIGTERM handler; no DB connection cleanup on container stop |
| 3 | **Static files via backend** | Nginx proxies `/static/` to FastAPI instead of serving directly; no caching headers |
| 4 | **No circuit breaker** | External API calls (VLM, model downloads) have no backoff/retry logic |
| 5 | **No metrics endpoint** | No Prometheus, StatsD, or APM integration |
| 6 | **No CORS middleware** | `CORSMiddleware` not added to `main.py` |
| 7 | **No DB pool tuning** | `pool_pre_ping=True` but no explicit pool size, connection timeout, or idle timeout |
| 8 | **No backup strategy** | Postgres volume + image volume with no documented backup procedure |
| 9 | **Input validation gaps** | `SearchQuery.page` allows negative values; most string fields lack max length; runtime clamping instead of schema validation |

### 3.4 LOW — Nice to Have

| # | Gap | Detail |
|---|-----|--------|
| 1 | No structured JSON logging | Logs not machine-parseable for log aggregation |
| 2 | No distributed tracing | No request ID propagation across services |
| 3 | No fine-grained RBAC | Admin is all-or-nothing; no read-only admin role |
| 4 | No caching headers | Static assets served without `Cache-Control` |
| 5 | No CDN integration | All assets served from origin |

### 3.5 Environment Variables (Complete Inventory)

| Variable | Default | Secure Default? |
|----------|---------|-----------------|
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/image_tagger_v3` | **NO** |
| `API_SECRET` | `dev_secret_key_change_me` | **NO** |
| `SECRET_KEY` | `production_secret_key_change_me_in_prod` | **NO** |
| `OPENAI_API_KEY` | empty | OK |
| `ANTHROPIC_API_KEY` | empty | OK |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | empty | OK |
| `VLM_PROVIDER` | auto-detect | OK |
| `IMAGE_STORAGE_ROOT` | `data_store` | OK |
| `VLM_HEALTH_ROOT` | `reports/vlm_health` | OK |
| `ENABLE_LEGACY_PREFIXES` | `"1"` | OK |
| `DEPTH_ANYTHING_ONNX_PATH` | none | OK |
| `IMAGE_SEGMENTATION_CACHE_ROOT` | `backend/data/debug_edges` | OK |
| `IMAGE_MATERIALS_CACHE_ROOT` | `backend/data/debug_materials` | OK |
| `IMAGE_MATERIALS2_CACHE_ROOT` | `backend/data/debug_materials2` | OK |
| `IMAGE_COMPLEXITY_CACHE_ROOT` | `backend/data/debug_complexity` | OK |
| `IMAGE_DEBUG_CACHE_ROOT` | `backend/data/debug_edges` | OK |
| `IMAGE_DEPTH_DEBUG_CACHE_ROOT` | `backend/data/debug_depth` | OK |
| `VLM_HARD_LIMIT_USD` | not set | OK |

### 3.6 Test Coverage Gaps

**Tested (8 functions in `test_v3_api.py`):**
- `test_health_root`, `test_health_endpoint`
- `test_admin_models_rbac`
- `test_explorer_attributes`, `test_explorer_search_smoketest`, `test_explorer_export_empty_list`
- `test_monitor_velocity_rbac_and_shape`, `test_monitor_irr_rbac_and_shape`

**Completely untested endpoints:**
- `POST /v1/workbench/validate` (core tagging)
- `POST /v1/workbench/region` (region creation)
- `POST /v1/admin/upload` (image upload)
- `POST /v1/admin/kill-switch` (VLM killswitch)
- `GET /v1/admin/budget` (budget status)
- `GET/POST /v1/admin/vlm/config` (VLM configuration)
- `POST /v1/admin/vlm/test` (VLM test)
- `POST /v1/admin/training/export` (training export)
- `GET /v1/admin/export/images` (image export)
- All `/v1/debug/*` endpoints
- All `/v1/vlm-health/*` endpoints
- All `/v1/bn_export/*` endpoints (BN export)
- `POST /v1/explorer/export` (training data export)
- `GET /v1/features/*` (feature catalog)
- `POST /v1/explorer/science/bootstrap` (science bootstrap)

**Missing test categories:**
- Auth flow end-to-end tests
- Database transaction/rollback tests
- Concurrent access tests
- Error condition / unhappy path tests
- Input validation boundary tests (negative page, oversized uploads, malformed JSON)
- Path traversal attack tests
- SQL injection tests on search fields

### 3.7 Files Requiring Immediate Attention

| Priority | File | Action Needed |
|----------|------|---------------|
| P0 | `backend/services/auth.py` | Replace hardcoded secret; add proper logging; implement token signing |
| P0 | `backend/api/v1_annotation.py` | Add error handling to all endpoints |
| P0 | `deploy/docker-compose.yml` | Externalize credentials; add resource limits |
| P0 | `deploy/Dockerfile.backend` | Add `USER` directive (non-root) |
| P0 | `deploy/nginx.conf` | Add HTTPS support; add caching headers |
| P1 | `backend/main.py` | Add CORS middleware; add request logging; improve health check |
| P1 | `backend/database/core.py` | Add pool tuning; remove insecure default URL |
| P1 | `backend/api/v1_admin.py` | Add transaction rollback on upload failures |
| P2 | root directory | Create `.env.example` with all variables documented |
| P2 | `tests/` | Expand coverage to untested endpoints |
