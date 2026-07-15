# Adversarial Review — Image Annotation Pipeline Red Team Results

30 antagonistic probes across 10 attack categories.  
**Result: 20 pass, 9 fail, 0 crash. Verdict: DEGRADED.**

---

## The 9 Failures

### 🔴 Critical (will silently lose data in production)

| # | Category | Probe | What broke | Root cause | Fix |
|---|----------|-------|-----------|-----------|-----|
| 1 | SILENT DROP | Key prefix | `glare-risk` and `acoustic_absorption_proxy` don't start with `cnfa.` | Legacy naming — written before the convention existed | Rename keys, add alias map |
| 2 | SILENT DROP | Scalar range | `fractal_dimension=1.93`, `prospect=3.00` — outside [0,1] | Fractal D is naturally ∈[1,2]; prospect is un-normalized distance | Rescale fractal: `(D-1)/1.0`; clamp prospect to [0,1] |
| 3 | SILENT DROP | Field shape | `processing_load` field `(16,21)`, `fractal_dimension` field `(7,10)` — don't match image `(480,640)` | Both use tile-based computation and return the tile grid, not upscaled to image | `cv2.resize(field, (W,H))` before returning |

### 🟡 Moderate (wrong answers, not data loss)

| # | Category | Probe | What broke | Root cause | Fix |
|---|----------|-------|-----------|-----------|-----|
| 4 | NaN/INF | NaN depth | `enclosure_index` returns NaN from NaN depth | `1/Z` where Z=NaN → NaN, no guard | `Z = np.nan_to_num(Z, nan=10.0)` in structural attrs |
| 5 | NaN/INF | Inf depth | `prospect` returns Inf from Inf depth | Same — no depth-validity guard | Clamp Z to `[0.1, 100]` at entry |
| 6 | SEMANTIC | Prospect vs enclosure | Both =1.0 on same image — architecturally contradictory | All-WALL + all-FLOOR image → high enclosure is correct, but prospect should be ~0 (short sightlines) | Bug in prospect: it doesn't use depth correctly for enclosed rooms |
| 7 | SEMANTIC | Saliency localization | Region center (440,319) — far from the actual bright patch at (280-360, 200-260) | Spectral-residual FFT saliency is known-bad at precise localization | This is the exact failure the TranSalNet adapter was built to fix |

### 🟢 Minor (edge case, acceptable for now)

| # | Category | Probe | What broke | Root cause | Fix |
|---|----------|-------|-----------|-----------|-----|
| 8 | PATHOLOGICAL | 1×1 image | k-means crashes (OpenCV needs >K samples) | No minimum image size guard | Add `if min(H,W) < 32: return fallback_result()` |
| 9 | DETERMINISM | palette_entropy | `0.991866` vs `0.991196` on same image | k-means color clustering uses random initialization | Set `cv2.KMEANS_PP_CENTERS` or fix random seed |

---

## What passed (20/30) — the system does survive

| Category | Probes | Status |
|----------|--------|--------|
| **PATHOLOGICAL** | All-black, all-white, extreme aspect, large image, random noise, uniform color | ✅ All survived |
| **NaN/INF** | Invalid plane labels (-99) | ✅ Handled gracefully |
| **CONFIDENCE** | Confidence varies with input; fallback → lower confidence | ✅ Both correct |
| **PROPAGATION** | VP on featureless; all-UNKNOWN planes; empty seats | ✅ All survived |
| **PIPELINE** | Full synthetic interior; timing <5s | ✅ Both pass |
| **ADAPTER** | is_available() never raises; DepthProvider fallback | ✅ Both correct |
| **AUDIT** | Method strings non-empty; failure modes documented | ✅ Both pass |

---

## Attack Surface Map

```
┌───────────────────────────────────────────────────────────────────────────┐
│                          ATTACK SURFACE MAP                              │
├────────────┬─────────────┬───────────────────────────────────────────────┤
│ Layer      │ Probes      │ Findings                                     │
├────────────┼─────────────┼───────────────────────────────────────────────┤
│ Input      │ 7 probes    │ 1×1 crash (minor). Rest robust.              │
│ Stage 0    │ 3 probes    │ VP, planes, depth all survive pathological.   │
│ Stage 1a   │ 8 probes    │ 3 SILENT DROPS: key, scalar, field.          │
│            │             │ 1 non-determinism. 1 saliency mislocalization │
│ Stage 1b   │ 5 probes    │ 2 NaN propagation. 1 semantic absurdity.     │
│ Adapters   │ 2 probes    │ Clean.                                       │
│ Audit      │ 2 probes    │ Clean.                                       │
│ Pipeline   │ 2 probes    │ Clean (<5s timing, full round-trip).          │
├────────────┼─────────────┼───────────────────────────────────────────────┤
│ TOTAL      │ 30 probes   │ 9 failures, 0 crashes                        │
└────────────┴─────────────┴───────────────────────────────────────────────┘
```

---

## Fix priority

The 3 **SILENT DROP** failures (#1–#3) are the highest priority because they cause
data loss that nobody notices — the exact bug class described. The NaN propagation
failures (#4–#5) are next because they corrupt downstream composites. The semantic
and edge-case failures are important but less urgent.

> [!IMPORTANT]
> The adversarial review lives at [adversarial_review.py](file:///Users/davidusa/REPOS/Image_Tagger_dk_latest/validation/adversarial_review.py).
> Run it after every change: `python3 validation/adversarial_review.py`.
> The target is **30/30 PASS**. The system is not production-ready until the verdict is CLEAN.

---

## Test hierarchy

```
Level 0: test_adapters.py           — 11/11 ✅  (imports + fallbacks)
Level 1: test_contract_conformance  — 8/15  ❌  (output schema)
Level 2: adversarial_review.py      — 20/29 ❌  (antagonistic correctness)
Level 3: (not yet built)            — last-mile delivery to SciencePayload
```
