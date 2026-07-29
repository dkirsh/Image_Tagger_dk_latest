# DISPOSITION of Codex-2's attack on the Reliable-A disposition
### 2026-07-18 (Cowork). Response to `FABLE_ATTACK_DISPOSITION_CODEX2_RESULT_2026-07-18.md`

**Verdict accepted in full.** Codex-2's attack was correct on every point. My previous disposition
fixed the *logic* of several findings but left the *emitted evidence* and one *new guard* overclaiming
or defective. All are now fixed and re-verified. Two of Codex-2's catches were genuine new defects my
fixes introduced (V9 split-brain, F7 outlier), plus a portability crash it exposed by running in a
skimage-free environment mine happened to have.

## Actions (all applied + re-verified in sandbox 2026-07-18)

| Codex-2 finding | Verdict it gave | Root cause | Fix | Re-verified |
|---|---|---|---|---|
| **F5 V9 split-brain** | NEW-DEFECT | `fractal_band.py` producer constant `TIER_HINT="GREEN"` while registry said AMBER; the emitted score self-labelled GREEN | `TIER_HINT="AMBER"` | V9 emits AMBER ✓ |
| **F2 V2 FOV contradiction** | STILL-BROKEN | FOV was ornamental but still in the method string, extras, and failure modes | Removed the `FOV_DEG` constant and every reference; method now says "PROXY, NOT the 2-D Penacchio-Wilkins metric; no angular calibration"; failure mode states scale-dependence | no "FOV" token in output ✓ |
| **F3 V6 evidence** | RELABEL-ONLY (still-misleading) | AttributeResult.method still said "Rosenholtz 2007" | method now "grayscale Gabor-magnitude entropy PROXY — NOT Rosenholtz Subband Entropy" | ✓ |
| **F4 V7 evidence** | RELABEL-ONLY (still-misleading) | method still said "Feature Congestion (Rosenholtz 2005)" | method now "local-variance … congestion PROXY — NOT Rosenholtz Feature Congestion" | ✓ |
| **F7 outlier ridge** | NEW-DEFECT | degeneracy used coefficient-of-variation, inflated by the single 1e6 clipped VGA cell, so flat-field+outlier passed | switched to ROBUST interquartile-range/median (ignores the outlier) + a "ridge must leave a real off-ridge population" check | flat+outlier → degenerate ✓; structured → not ✓; near-flat → degenerate ✓ |
| **Full-stage RED/crash** | NEW-DEFECT | `symmetry_horizontal` hard-imported `skimage.metrics.ssim` (absent in Codex's env) → compute_failed → UNKNOWN → RED; then `run_stage.py:90` `IndexError` on all-RED | replaced with a dependency-free cv2-Gaussian SSIM (`_ssim_cv2`); guarded run_stage to fall back to any quarantined record | run_stage: 27/27 scored, AMBER=4 RED=0, no compute_failed, no crash ✓ |
| F1 V13 / F8 V1 | FIXED-CONFIRMED | — | (unchanged; Codex confirmed) | ✓ |
| F6 C29 | RELABEL-ONLY (honest) | — | (unchanged; honestly crude, AMBER) | ✓ |

## The important admission
Codex-2's headline — "V9 emitted GREEN despite registry AMBER" — is the kind of split-brain that a
description-level review misses and only an execution-level attack catches. It is exactly why the
two-layer / cross-agent adversarial protocol earns its cost. My disposition said "demoted to AMBER"
and was true of the registry but false of the producer. Fixed.

## Re-verification evidence (sandbox, 2026-07-18)
- All 4 core suites PASS (C01, C29, V9, reliable-attrs).
- F7 probes: `[500]*99+[1e6]` → degenerate; structured `i²` field → not; near-flat → degenerate.
- V2 output carries no "FOV" token and is PROXY-labelled; V6/V7 methods say "PROXY — NOT Rosenholtz …".
- V9 `TIER_HINT == "AMBER"`.
- `symmetry_horizontal` runs with no skimage; `run_stage` on 4 real interiors → 27/27 scored, AMBER=4,
  RED=0, negative control REJECTED (RED), idempotent, no IndexError.
- MODEL_VERSION → `…+reviewfix+codex2fix`.

## Still owed (unchanged — NOT closed by these fixes)
Faithful V2/V6/V7 reimplementations (or keep as the now-honestly-named proxies); M1′ sufficient-
statistic replay; Mac↔sandbox exact-replay; Article_Eater grounding; labeled A-vs-B corpus for
C01/C29 + V9 constants; V13 true Grebenkina second-order. The dependency-free SSIM also means the
symmetry attribute's values changed — old accepted records must be re-derived (MODEL_VERSION bump
handles this).

## Recommended next
Re-run Codex (or a fresh agent) with the SAME attack prompt against this disposition — a third pass
confirms the fixes hold and nothing new broke. If clean, proceed to the constructive batch: the
faithful reimplementations + M1′.
