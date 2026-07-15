# cnfa_algs CONTRACT — Pipeline, Adapters, and Last-Mile Delivery

This contract governs the `cnfa_algs` attribute-computation layer. It defines
how algorithms receive input, what they must produce, how results compose into
a complete annotation, and — critically — what constitutes success at the point
where output turns gears in the downstream system.

---

## 1. The Annotation Pipeline

A complete image annotation runs as a staged pipeline:

```
  Input Image (BGR uint8 HxWx3)
       │
       ▼
  ┌──────────────────────────────────────┐
  │  STAGE 0: Shared representations     │  ← geometry.py, adapters
  │  • depth map (metric or relative)    │
  │  • plane label map (floor/wall/…)    │
  │  • vanishing point + VP confidence   │
  │  • saliency map (deep or FFT)        │
  │  • wireframe lines + junctions       │
  └──────┬────────────────┬──────────────┘
         │                │
         ▼                ▼
  ┌──────────────┐  ┌──────────────────┐
  │  STAGE 1a:   │  │  STAGE 1b:       │   ← attributes.py, composition.py
  │  Pixel attrs │  │  Structural      │      (PARALLELIZABLE)
  │  (M1)        │  │  attrs (M2)      │
  └──────┬───────┘  └──────┬───────────┘
         │                 │
         ▼                 ▼
  ┌──────────────────────────────────────┐
  │  STAGE 2: Plan inference (M2.5/M3)  │  ← plan.py
  │  • isovist fields                   │
  │  • sociopetal/spatial metrics        │
  └──────────────────┬───────────────────┘
                     │
                     ▼
  ┌──────────────────────────────────────┐
  │  STAGE 3: Aggregation + delivery     │  ← core.save_results_json
  │  • merge into AnalysisFrame          │     + TRS_v1.1 SciencePayload
  │  • wrap in TrustEnvelope             │
  │  • persist to SciencePayload JSON    │
  └──────────────────────────────────────┘
```

### Parallelism rules
- Stage 0 representations are **serial prerequisites** — depth and planes
  must exist before any Stage 1b or Stage 2 attribute runs.
- Stage 1a (pixel-only attributes: brightness, color entropy, fractal D, etc.)
  can run **in parallel** with Stage 0, because they need only the raw image.
- Stage 1b (depth-dependent: prospect, openness, enclosure) runs **after**
  Stage 0 depth + planes.
- Stage 2 (plan inference, isovist) runs **after** Stage 0 + Stage 1b.
- Stage 1a and Stage 1b are **independent** and parallelizable with each other
  once their prerequisites are met.

---

## 2. Input Contract

Every attribute function receives:

| Parameter       | Type               | Required | Notes |
|-----------------|--------------------|----------|-------|
| `img_bgr`       | `np.ndarray` (H,W,3) uint8 BGR | **YES** | The original image. Always present. |
| `depth`         | `np.ndarray` (H,W) float32     | No  | Stage 0 output. None if unavailable. |
| `planes`        | `np.ndarray` (H,W) int32       | No  | Plane labels (0–4). None if unavailable. |
| `saliency_map`  | `np.ndarray` (H,W) float32     | No  | From saliency adapter. None if unavailable. |
| `vp`            | `Tuple[float,float,float]`     | No  | (vx, vy, confidence). |

**Rule:** A function that receives `None` for an optional input MUST still run
and return a valid `AttributeResult` at reduced confidence — never raise.

---

## 3. Output Contract (AttributeResult)

Every attribute function returns an `AttributeResult`:

| Field           | Type               | Constraint | Violation = |
|-----------------|--------------------|-----------|----|
| `key`           | `str`              | Must be a canonical key from the registry (e.g. `cnfa.light.brightness_variance`) | **LAST-MILE FAILURE**: unregistered key is silently dropped by SciencePayload |
| `scalar`        | `float ∈ [0.0, 1.0]` or `None` | If not None, must be in [0,1]. NaN is never valid. | Downstream div-by-zero, NaN propagation |
| `field`         | `np.ndarray` (H,W) float32 ∈ [0,1] or `None` | Shape must match input image `[:2]`. Values in [0,1]. | Overlay rendering crash, misaligned heatmap |
| `regions`       | `list[dict]`       | Each dict has `kind`, `coords`, `label`, `value` | Explorer region display broken |
| `confidence`    | `float ∈ [0.0, 1.0]` | Must reflect actual reliability, not be hardcoded to 1.0 | TrustEnvelope is meaningless |
| `method`        | `str`              | Must name the algorithm and tier, e.g. `"spectral-residual FFT (M1)"` | Audit trail broken |
| `failure_modes` | `list[str]`        | Must list known limitations honestly | False confidence in downstream decisions |

---

## 4. Adapter Contract

Every external-model adapter in `cnfa_algs/adapters/`:

| Rule | Contract | What breaks if violated |
|------|----------|----------------------|
| **A1: Availability guard** | Exposes `is_available() → bool`. Returns `False` if the checkpoint env var is unset or the file is missing. Never raises. | Pipeline crash on unconfigured machines |
| **A2: Lazy loading** | Model loads only on first inference call, not on import. | Import-time crash, memory waste |
| **A3: Env var documented** | Module docstring names the env var (e.g. `DEPTH_PRO_CHECKPOINT`). | Developer can't figure out how to enable it |
| **A4: Graceful fallback** | If the adapter is unavailable, the calling function uses a built-in fallback at reduced confidence — never raises, never returns None. | Silent pipeline hole |
| **A5: Output normalization** | Adapter output matches the shape and dtype the caller expects (see §2). Adapter handles any internal resizing/dtype conversion. | Misaligned arrays, subtle wrong-answer bugs |

---

## 5. Confidence Contract

Confidence is not a decoration — it governs the TrustEnvelope's
`evaluation_status` and the frontend badge color.

### Confidence sources and how they combine

| Source type | Confidence range | Example |
|-------------|-----------------|---------|
| Deterministic pixel computation (M1) | 0.8 – 1.0 | Brightness mean, color entropy |
| Heuristic approximation (M1) | 0.4 – 0.7 | Spectral-residual saliency, geometric VP |
| Trained model, proven dataset (M2) | 0.7 – 0.9 | SegFormer wall segmentation, Depth Pro |
| Trained model, domain shift risk (M2) | 0.5 – 0.7 | Places365 on unusual architecture |
| VLM judgment (M3/hypothesis) | 0.3 – 0.6 | Kaplan mystery, style classification |

### Competing algorithms

When two algorithms compute the same attribute:
1. **Higher-confidence wins** for the scalar. The lower-confidence result is
   stored in `extras["alternative"]` for audit.
2. **Agreement boosts**: if both algorithms agree (within 10%), confidence
   is boosted by `min(0.1, lower_conf * 0.2)`.
3. **Disagreement degrades**: if they disagree by >25%, confidence of the
   winner is degraded by 0.1, and both values are surfaced with a
   `failure_mode: "competing algorithms disagree"`.
4. The `method` field must name which algorithm won and which was the alternative.

### Propagation through composites

When a composite (L1) is computed from components (L0):
```
composite_confidence = min(component_confidences)
```
Never average — the weakest link governs. A prospect score derived from a
conf-0.35 geometric depth map cannot claim conf-0.8.

---

## 6. Last-Mile Success Conditions

**This is the contract that prevents the "it ran but nothing happened" bug.**

### 6.1 Per-attribute last mile

An attribute computation is **SUCCESSFUL** only when ALL of:

| Gate | Check | How to verify |
|------|-------|--------------|
| **LM-1: Valid result** | `AttributeResult` returned, `scalar` is not None and not NaN, `confidence > 0` | `assert result.scalar is not None and np.isfinite(result.scalar) and result.confidence > 0` |
| **LM-2: Key registered** | `result.key` exists in the canonical feature registry (`feature_stubs.py` or TRS registry) | `assert result.key in REGISTERED_KEYS` |
| **LM-3: Field shape match** | If `result.field` is not None, its shape matches `img.shape[:2]` | `assert result.field.shape == img.shape[:2]` |
| **LM-4: Written to frame** | Result has been written to `AnalysisFrame` via `add_proximal/add_derived/add_structural/add_hypothesis` | `assert result.key in frame.attributes` |
| **LM-5: Persisted** | Result appears in the saved `SciencePayload.features` JSON for this image | `assert key in saved_payload["features"]` |

### 6.2 Per-image last mile (pipeline success)

A complete image annotation is **SUCCESSFUL** only when:

| Gate | Check |
|------|-------|
| **PL-1: Minimum attribute count** | `len(frame.attributes) >= MINIMUM_ATTRIBUTES` (currently 12 for proximal-only, 20 for structural) |
| **PL-2: No NaN leakage** | No attribute value in the frame is NaN or infinite |
| **PL-3: Run status written** | `SciencePayload.run_status == "completed"` in the database, not stuck at `"pending"` or `"running"` |
| **PL-4: Timing recorded** | `PipelineResult.elapsed_seconds` and `analyzer_timings` are logged |
| **PL-5: Errors surfaced** | Any analyzer errors are in `PipelineResult.errors` AND in the morning digest (not swallowed silently) |
| **PL-6: Overlay renderable** | At least one `field` can be composited as a heatmap overlay without error |

### 6.3 Adapter last mile

A new adapter integration is **SUCCESSFUL** only when:

| Gate | Check |
|------|-------|
| **AL-1: Smoke import** | `is_available()` runs without error (returns True or False) |
| **AL-2: Fallback verified** | With adapter unavailable (env var unset), the calling attribute function still produces a valid result |
| **AL-3: Real-model run** | With weights present, a known reference image produces output with the expected shape, dtype, and value range |
| **AL-4: Confidence changes** | Attribute confidence is measurably higher with the adapter than without (document the delta) |
| **AL-5: Key still registered** | The same canonical key is produced whether the adapter is active or not — the key doesn't change, only the confidence and method |
| **AL-6: Written through** | Result from the adapted path reaches `SciencePayload.features` in the database (end-to-end, not just the algorithm layer) |

---

## 7. Visualization Contract

Annotation results must be presentable at three levels:

### 7.1 Heatmap overlay (per-attribute)

Every attribute with a non-None `field` can be rendered as a topographic
heatmap overlay on the source image:
- Colormap: `cv2.COLORMAP_INFERNO` (perceptually uniform, colorblind-safe)
- Alpha: 0.5 default, adjustable
- Iso-contours at 0.25, 0.5, 0.75 thresholds
- Title: `key (scalar=X.XX, conf=Y.YY, method)`
- The `heatmap_overlay()` function in `core.py` is the canonical renderer.

### 7.2 Gallery (per-image)

All attributes for one image are composited into a grid:
- Original image in position (0,0)
- One tile per attribute with field, sorted by category
- The `gallery()` function in `core.py` is the canonical renderer.
- **Success condition:** the gallery image is saved to disk and is viewable.

### 7.3 Dashboard (per-batch)

For batch runs, results are tabulated:
- One row per image, one column per attribute
- Confidence color-coded (green ≥ 0.7, yellow ≥ 0.4, red < 0.4)
- Failure modes listed in tooltip
- **This does not exist yet.** It is a gap.

---

## 8. Validation Test Suite

### Level 0: Smoke (runs on any machine, no weights)

```bash
python3 validation/test_adapters.py
```
- All adapters import
- All `is_available()` return bool without error
- Pure-code functions (composition, saliency fallback) produce valid output on synthetic images
- DepthProvider initializes to geometric fallback

### Level 1: Contract conformance (runs on any machine, no weights)

For every attribute function `f`:
```python
img = np.zeros((480, 640, 3), dtype=np.uint8)  # black image
result = f(img)
assert isinstance(result, AttributeResult)
assert result.key and result.key.startswith("cnfa.")
assert result.scalar is None or (0.0 <= result.scalar <= 1.0 and np.isfinite(result.scalar))
assert result.field is None or result.field.shape == (480, 640)
assert 0.0 <= result.confidence <= 1.0
assert result.method != ""
assert isinstance(result.failure_modes, list)
```

### Level 2: Pipeline end-to-end (requires a reference image)

```python
img = cv2.imread("validation/fixtures/reference_interior.jpg")
results = run_all_attributes(img)
assert len(results) >= 12  # PL-1
for r in results:
    assert r.key in REGISTERED_KEYS  # LM-2
    assert r.scalar is not None and np.isfinite(r.scalar)  # LM-1, PL-2
    if r.field is not None:
        assert r.field.shape == img.shape[:2]  # LM-3
```

### Level 3: Last-mile delivery (requires backend running)

```python
# Upload image → pipeline runs → check SciencePayload
payload = get_science_payload(image_id)
assert payload["run_status"] == "completed"  # PL-3
assert len(payload["features"]) >= 12  # PL-1
for key, envelope in payload["features"].items():
    assert key in REGISTERED_KEYS  # LM-2
    assert envelope["evaluation_status"] in ("validated", "proxy_validated", "untested")
    assert np.isfinite(envelope["value"])  # PL-2
```

---

## 9. Speed Optimization Targets

| Configuration | Target | Current estimate |
|---------------|--------|-----------------|
| Proximal only (L0+L1, no models) | < 2s per image | ~1.5s |
| Structural (L0+L1+L2, with depth+seg) | < 15s per image | ~8–12s (GPU), ~30s (CPU) |
| Full (L0–L3, with VLM) | < 60s per image | ~45s (depends on VLM latency) |

Optimization priority:
1. Parallelize Stage 1a and Stage 1b (independent after Stage 0)
2. Cache Stage 0 representations (depth map, plane map) — don't recompute for each attribute
3. Batch model inference (run SegFormer once for all segmentation-dependent attributes)

---

## 10. Gaps (honest)

| Gap | Severity | Status |
|-----|----------|--------|
| No `run_all_attributes()` function exists in cnfa_algs — each attribute is called individually | HIGH | Need to write orchestrator |
| cnfa_algs `AttributeResult` → TRS `AnalysisFrame` bridge is not formalized | HIGH | The key mapping and confidence translation are ad-hoc |
| Level 2 contract conformance tests do not exist yet | MEDIUM | Need reference image + expected-output fixture |
| Level 3 last-mile tests do not exist yet | MEDIUM | Requires running backend |
| Dashboard visualization (§7.3) does not exist | LOW | Pure frontend task |
| Competing-algorithm confidence logic (§5) is designed but not implemented | MEDIUM | Need to implement in a compositor |

```
Contract authored: 2026-07-14
```
