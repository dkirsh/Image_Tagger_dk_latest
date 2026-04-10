## Shared Contracts (committed as `/docs/CONTRACT.md`)

### REST API Endpoints (v1)

All endpoints are prefixed `/v1`.

Auth rules:
- Explorer endpoints are public and do not require auth headers.
- Workbench, monitor, and admin endpoints require `Authorization: Bearer <jwt>`.
- The backend derives identity from JWT claims only. Client-supplied `X-User-Id` and `X-User-Role` headers are not part of the auth contract and must not be trusted for authorization.

**Explorer (public browse)**
- `GET /v1/explorer/search?q=&page=&page_size=&room_type=&tag=` → `ExplorerSearchResponse`
- `GET /v1/explorer/images/{image_id}` → `ImageDetail`
- `GET /v1/explorer/attributes` → `{ attributes: AttributeDef[] }`

Explorer search pagination contract:
- `page` default: `1`
- `page` minimum: `1`
- `page_size` default: `20`
- `page_size` minimum: `1`
- `page_size` maximum: `100`

**Workbench (human tagging)**
- `GET /v1/workbench/next` → `WorkbenchAssignment | { empty: true }`
- `POST /v1/workbench/validate` body `ValidationSubmit` → `{ validation_id: int, accepted: bool }`
- `POST /v1/workbench/region` body `RegionCreate` → `Region`

**Monitor (supervisor)**
- `GET /v1/monitor/velocity?window_hours=` → `{ series: VelocityPoint[] }`
- `GET /v1/monitor/irr` → `{ rows: IRRRow[] }`

**Admin**
- `POST /v1/admin/upload` multipart field `files[]` → `{ job_id: str, items: int, image_ids: int[], status: "queued" }`
- `GET /v1/admin/budget` → `{ spent_usd: float, limit_usd: float, remaining_usd: float }`
- `POST /v1/admin/kill-switch` body `{ enabled: bool }` → `{ enabled: bool, changed_at: iso8601 }`

**Health**
- `GET /health` → `{ status: "ok"|"degraded", version: str, db: bool, storage: bool }`

### Shared TypeScript / Pydantic Types

```ts
type Role = "tagger" | "scientist" | "supervisor" | "admin";

type JwtClaims = {
  sub: string;
  role: Role;
};

type TrustEvaluationStatus = "validated" | "proxy_validated" | "untested";

type TrustEnvelope<T> = {
  value: T;
  model_id: string;
  evaluation_status: TrustEvaluationStatus;
  confidence_interval_95: [number, number] | null;
  n_training: number;
  notes: string;
};

type ExplorerSearchResponse = {
  items: ImageSummary[];
  total: number;
  page: number;
  page_size: number;
};

type ImageSummary = {
  id: number;
  url: string;
  thumbnail_url: string;
  room_type: string | null;
  canonical_tags: string[];
  validation_count: number;
};

type AttributeDef = {
  id: number;
  key: string;
  name: string;
  category: string | null;
  level: string | null;
  range: string | null;
  sources: string | null;
  notes: string | null;
};

type RegionGeometry =
  | {
      type: "bbox";
      x: number;
      y: number;
      width: number;
      height: number;
    }
  | {
      type: "polygon";
      points: Array<{ x: number; y: number }>;
    };

type RegionCreate = {
  image_id: number;
  geometry: RegionGeometry;
  manual_label: string;
};

type Region = {
  id: number;
  image_id: number;
  geometry: RegionGeometry;
  auto_label: string | null;
  auto_confidence: number | null;
  manual_label: string | null;
};

type AffordancePrediction = {
  key: string;
  label: string;
  score: number;
  confidence: TrustEnvelope<number>;
};

type VelocityPoint = {
  timestamp: string; // iso8601
  count: number;
};

type IRRRow = {
  attribute_key: string;
  attribute_name: string;
  irr: number;
  bin: "low" | "medium" | "high";
  n_pairs: number;
};

type ImageDetail = ImageSummary & {
  width: number;
  height: number;
  science: SciencePayload | null;
  regions: Region[];
};

type WorkbenchAssignment = {
  image: ImageDetail;
  assignment: {
    attribute_key: string;
    attribute_name: string;
    prompt: string;
    value_type: "boolean" | "number" | "enum";
    allowed_values: Array<string | number | boolean> | null;
    min: number | null;
    max: number | null;
    step: number | null;
    required: true;
  };
};

type SciencePayload = {
  run_id: number;
  run_status: "pending" | "running" | "completed" | "failed";
  features: Record<string, TrustEnvelope<number>>;
  affordances: AffordancePrediction[];
};

type ValidationSubmit = {
  image_id: number;
  attribute_key: string;
  value: string | number | boolean;
  duration_ms: number;
};

type ErrorDetail = {
  field: string;
  message: string;
  type: string;
};

type ErrorResponse = {
  error: {
    code: string;
    message: string;
    request_id: string;
    details?: ErrorDetail[];
  };
};
```

Region geometry note:
- Earlier docs said `GeoJSON or {x,y,w,h}` while the persisted backend model only guarantees JSON storage for a box or polygon.
- This contract standardizes the wire format as the explicit `RegionGeometry` union above so Track B can build exact mocks without guessing between GeoJSON variants.

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

`SciencePayload.features` is a map keyed by canonical feature keys. Each value is the trust envelope for that feature's numeric output. There is no separate `confidence` map for features.

`AffordancePrediction.confidence` uses the same trust envelope shape, scoped to the affordance `score`.

### Monitor IRR Contract Notes

`GET /v1/monitor/irr` returns a table-oriented list, not a single-attribute detail view.

An `IRRRow` is included only when the backend has at least 10 overlapping validation pairs for the same `attribute_key`, produced by two distinct taggers across 10 distinct images. This keeps v1 efficient while avoiding numerically meaningless IRR rows from one-off overlaps.

If no attributes meet that minimum, the endpoint returns `{ "rows": [] }` and the frontend shows the contracted empty state.

### Upload Policy

`POST /v1/admin/upload` accepts only image files with MIME types `image/jpeg`, `image/png`, or `image/webp`.

Upload limits:
- maximum per-file size: `10 MiB`
- maximum batch size: `200` files

Client-side validation in the admin UI MUST exactly mirror these server-side rules for MIME type, per-file size, and batch size. If the backend rejects a file that the client allowed, or the client rejects a file that the backend would accept, that is a contract violation.

Representative upload validation failures use `ErrorResponse.details` with `field: "files"`.

Multipart upload validation failures use the same canonical validation message, `Request validation failed`; they are not a special-case error message in v1.

### Post-Upload Processing Contract

`POST /v1/admin/upload` is asynchronous. A successful upload means:
- the original file batch has been accepted for ingestion
- image records have been created
- the response returns the created `image_ids`
- the response `status` is always `"queued"` for newly accepted work

Discoverability rules:
- an uploaded image becomes discoverable in Explorer as soon as its image record is committed
- the smoke-test target image must be reachable by `GET /v1/explorer/images/{image_id}` within 5 seconds of a successful upload response

Science-population rules:
- science processing runs asynchronously after upload
- `GET /v1/explorer/images/{image_id}` may initially return `science: null` or a non-null `science` payload with `run_status: "pending"` or `"running"`
- for the v1 smoke test, the backend must populate `science` to `run_status: "completed"` for the uploaded smoke-test image within 60 seconds of upload acceptance

Smoke-test wait rule:
- after upload, the smoke runbook polls `GET /v1/explorer/images/{image_id}` until `science.run_status === "completed"` or until 60 seconds elapse
- the explorer trust-badge verification step is not considered ready before that condition is met

### Workbench Assignment Contract

`GET /v1/workbench/next` is an assigned single-attribute labeling endpoint.

Assignment rules:
- the backend returns exactly one image plus exactly one assigned attribute to label
- the tagger does not choose the attribute in v1
- the frontend renders its form entirely from the returned `assignment` metadata
- `allowed_values` is required for `value_type: "enum"` and `null` otherwise
- `min`, `max`, and `step` are required for `value_type: "number"` and `null` otherwise

This is the canonical v1 interaction model for workbench. If the assignment metadata changes, frontend form behavior changes with it; no hardcoded attribute rules belong in the client.

### Standard Error Response

All non-2xx responses MUST use the shared `ErrorResponse` shape. `ErrorResponse` is the canonical response contract for every non-2xx API response, including validation failures:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "request_id": "9bb4fd59-d495-4f0b-a9f0-6e57e8d22496",
    "details": [
      {
        "field": "page",
        "message": "Input should be greater than or equal to 1",
        "type": "greater_than_equal"
      }
    ]
  }
}
```

Error code guidance:
- `AUTH_REQUIRED` for missing or invalid bearer token
- `FORBIDDEN` for valid auth without sufficient role
- `VALIDATION_ERROR` for query/body/multipart validation failures
- `NOT_FOUND` for missing resources
- `RATE_LIMITED` for 429 responses
- `INTERNAL_ERROR` for unexpected server failures

`POST /v1/admin/upload` uses the same error shape for auth failures and upload validation failures.

### Auth Structure

- JWT issued by a free-tier identity provider (Supabase Auth); backend validates signature using `SUPABASE_JWT_SECRET`
- Identity comes from JWT claims only; backend reads `sub` as user id and top-level `role`
- Roles encoded in JWT claim `role ∈ {tagger, scientist, supervisor, admin}`
- Explorer endpoints are anonymous/public read routes
- Workbench endpoints require valid JWT (no anonymous writes)
- Supervisor/admin endpoints require both valid JWT and matching role claim

Representative auth errors:
- `401 Unauthorized`:

```json
{
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Bearer token required or invalid",
    "request_id": "dcaa4bd2-3a10-4807-a0f8-2ca223b5df27"
  }
}
```

- `403 Forbidden`:

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Admin role required",
    "request_id": "0fef5c40-1a8a-43ba-86cc-512b1f9fbd24"
  }
}
```

### Example Payloads By Endpoint Group

**Explorer**

Request:

```http
GET /v1/explorer/search?q=window&page=1&page_size=20&room_type=living_room&tag=biophilic
```

Response:

```json
{
  "items": [
    {
      "id": 101,
      "url": "https://cdn.example.com/images/101.jpg",
      "thumbnail_url": "https://cdn.example.com/images/101-thumb.jpg",
      "room_type": "living_room",
      "canonical_tags": ["biophilic", "window", "daylight"],
      "validation_count": 4
    }
  ],
  "total": 37,
  "page": 1,
  "page_size": 20
}
```

Request:

```http
GET /v1/explorer/images/101
```

Response:

```json
{
  "id": 101,
  "url": "https://cdn.example.com/images/101.jpg",
  "thumbnail_url": "https://cdn.example.com/images/101-thumb.jpg",
  "room_type": "living_room",
  "canonical_tags": ["biophilic", "window", "daylight"],
  "validation_count": 4,
  "width": 1600,
  "height": 1200,
  "science": {
    "run_id": 8801,
    "run_status": "completed",
    "features": {
      "light.daylight_ratio": {
        "value": 0.84,
        "model_id": "feature_daylight_ratio_v1",
        "evaluation_status": "proxy_validated",
        "confidence_interval_95": [0.79, 0.88],
        "n_training": 0,
        "notes": "Derived feature; proxy validated against internal reference set."
      },
      "texture.visual_complexity": {
        "value": 0.41,
        "model_id": "feature_visual_complexity_v1",
        "evaluation_status": "untested",
        "confidence_interval_95": null,
        "n_training": 0,
        "notes": "Evaluation provenance not yet documented in ML_EVALUATION.md; display as untested in v1."
      }
    },
    "affordances": [
      {
        "key": "L059",
        "label": "sleep_suitability",
        "score": 5.8,
        "confidence": {
          "value": 5.8,
          "model_id": "affordance_L059_lgbm_v1",
          "evaluation_status": "validated",
          "confidence_interval_95": [5.2, 6.1],
          "n_training": 1523,
          "notes": "held-out test R²=0.71; see ML_EVALUATION.md#L059"
        }
      }
    ]
  },
  "regions": [
    {
      "id": 901,
      "image_id": 101,
      "geometry": {
        "type": "bbox",
        "x": 245,
        "y": 180,
        "width": 320,
        "height": 210
      },
      "auto_label": null,
      "auto_confidence": null,
      "manual_label": "window"
    }
  ]
}
```

Request:

```http
GET /v1/explorer/attributes
```

Response:

```json
{
  "attributes": [
    {
      "id": 12,
      "key": "light.daylight_ratio",
      "name": "Daylight Ratio",
      "category": "light",
      "level": "continuous",
      "range": "0..1",
      "sources": "science_pipeline_v3.4",
      "notes": "Used by explorer filters and workbench validation."
    }
  ]
}
```

Example validation error using the shared `ErrorResponse` shape:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "request_id": "f7f4d9e4-a86c-47f0-8bb7-3a351f35bb5a",
    "details": [
      {
        "field": "page",
        "message": "Input should be greater than or equal to 1",
        "type": "greater_than_equal"
      }
    ]
  }
}
```

Example validation error for page size above the contract maximum:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "request_id": "5a0bf8fd-2150-4c74-8bf0-5985901fdb2f",
    "details": [
      {
        "field": "page_size",
        "message": "Input should be less than or equal to 100",
        "type": "less_than_equal"
      }
    ]
  }
}
```

**Workbench**

Request:

```http
GET /v1/workbench/next
```

Response:

```json
{
  "image": {
    "id": 101,
    "url": "https://cdn.example.com/images/101.jpg",
    "thumbnail_url": "https://cdn.example.com/images/101-thumb.jpg",
    "room_type": "living_room",
    "canonical_tags": ["biophilic", "window", "daylight"],
    "validation_count": 4,
    "width": 1600,
    "height": 1200,
    "science": null,
    "regions": []
  },
  "assignment": {
    "attribute_key": "light.daylight_ratio",
    "attribute_name": "Daylight Ratio",
    "prompt": "Estimate the fraction of the room lit by daylight.",
    "value_type": "number",
    "allowed_values": null,
    "min": 0,
    "max": 1,
    "step": 0.05,
    "required": true
  }
}
```

Request:

```json
{
  "image_id": 101,
  "attribute_key": "light.daylight_ratio",
  "value": 0.9,
  "duration_ms": 18340
}
```

Response:

```json
{
  "validation_id": 4402,
  "accepted": true
}
```

Request:

```json
{
  "image_id": 101,
  "geometry": {
    "type": "polygon",
    "points": [
      { "x": 120, "y": 160 },
      { "x": 410, "y": 155 },
      { "x": 420, "y": 380 },
      { "x": 125, "y": 392 }
    ]
  },
  "manual_label": "window"
}
```

Response:

```json
{
  "id": 901,
  "image_id": 101,
  "geometry": {
    "type": "polygon",
    "points": [
      { "x": 120, "y": 160 },
      { "x": 410, "y": 155 },
      { "x": 420, "y": 380 },
      { "x": 125, "y": 392 }
    ]
  },
  "auto_label": null,
  "auto_confidence": null,
  "manual_label": "window"
}
```

**Monitor**

Request:

```http
GET /v1/monitor/velocity?window_hours=24
```

Response:

```json
{
  "series": [
    { "timestamp": "2026-04-07T08:00:00Z", "count": 12 },
    { "timestamp": "2026-04-07T09:00:00Z", "count": 18 },
    { "timestamp": "2026-04-07T10:00:00Z", "count": 15 }
  ]
}
```

Request:

```http
GET /v1/monitor/irr
```

Response:

```json
{
  "rows": [
    {
      "attribute_key": "light.daylight_ratio",
      "attribute_name": "Daylight Ratio",
      "irr": 0.67,
      "bin": "high",
      "n_pairs": 28
    },
    {
      "attribute_key": "texture.visual_complexity",
      "attribute_name": "Visual Complexity",
      "irr": 0.44,
      "bin": "medium",
      "n_pairs": 14
    }
  ]
}
```

**Admin**

Request:

```http
POST /v1/admin/upload
Content-Type: multipart/form-data

files[]: living-room-01.jpg
files[]: living-room-02.png
```

Response:

```json
{
  "job_id": "upl_20260407_0001",
  "items": 2,
  "image_ids": [101, 102],
  "status": "queued"
}
```

Representative upload errors:

```json
{
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Bearer token required or invalid",
    "request_id": "93af460c-01ce-4704-b690-af24f2ea5fc9"
  }
}
```

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Admin role required",
    "request_id": "523f43ed-c856-4e0c-8334-aa2f10c86da7"
  }
}
```

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "request_id": "e1367f06-fd2f-4f9d-89aa-7546d4962b58",
    "details": [
      {
        "field": "files",
        "message": "Maximum batch size is 200 files",
        "type": "max_items"
      }
    ]
  }
}
```

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "request_id": "2bc7258a-8b56-4254-9548-d70d482976a7",
    "details": [
      {
        "field": "files",
        "message": "Each file must be JPEG, PNG, or WebP and no larger than 10 MiB",
        "type": "file_constraints"
      }
    ]
  }
}
```

Request:

```http
GET /v1/admin/budget
```

Response:

```json
{
  "spent_usd": 4.25,
  "limit_usd": 15.0,
  "remaining_usd": 10.75
}
```

Request:

```json
{
  "enabled": false
}
```

Response:

```json
{
  "enabled": false,
  "changed_at": "2026-04-07T17:41:12Z"
}
```

**Health**

Request:

```http
GET /health
```

Response:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "db": true,
  "storage": true
}
```

### Shared Environment Variables (names only)

`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_JWT_SECRET`, `IMAGE_STORAGE_ROOT`, `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `VLM_HARD_LIMIT_USD`, `LOG_LEVEL`, `SENTRY_DSN`, `CORS_ALLOWED_ORIGINS`.
