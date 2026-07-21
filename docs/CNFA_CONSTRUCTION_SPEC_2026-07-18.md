# CNfA CONSTRUCTION SPEC (draft) — implementing the full attribute table
### Image_Tagger / CNfA · 2026-07-18 (Cowork) · DRAFT for Codex to deepen

*How we build the viz operators on the full table to a standard that survives adversarial review. This
is the engineering contract; the attribute list is `CNFA_FULL_ATTRIBUTE_TABLE_2026-07-18.md`; the testing
plan Codex is asked to produce sits beside it. Goal: keep pushing the ADEQUACY of implementations —
determinism is table stakes, faithfulness-to-paper and construct-validity are the bar.*

## 0. Three propositions every operator must clear (the review lesson)
1. **Deterministic** — same image → same number (seed everything; no optional-dep crashes).
2. **Faithful** — the code computes what the cited paper's measure actually is, OR it is honestly named
   a PROXY and tiered AMBER. (V2/V6/V7 failed this first pass — renamed to proxies.)
3. **Construct-valid** — moving the number moves the human/architectural outcome, shown against labeled
   data, not asserted. Until then the operator is AMBER, never GREEN.
GREEN is earned only when all three hold AND cross-environment (Mac↔sandbox) exact replay passes.

## 1. The per-operator build recipe (proven on C01/C29/V9)
1. `cnfa_algs/<module>.py` function → `AttributeResult` (scalar/field/method/confidence/extras/failure_modes);
   pure, deterministic, with directly-unit-testable pure helpers.
2. Registry entry: `_spec(id, kind, requires, audit_class, tier_hint, note)` — tier/note honest.
3. Route through the `derivation` chokepoint (scored/abstain/unknown); a value without evidence is impossible.
4. Pure-core test + M1 replay + a NEGATIVE control + boundary tests for every new threshold — **run them**.
5. Annotator binding (cache shared upstreams — geometry, VGA, fractal — compute once).
6. `run_stage` on ≥5 real interiors → SCORED + traceable + determinism ×3; then external attack.

## 2. Socket contract (unchanged, restated)
Tri-state SCORED/ABSTAINED/UNKNOWN; ABSTAIN names the missing declared input; UNKNOWN fails closed → RED.
Evidence is mandatory and typed (image_region / global_image / plan_chain) with the producing signal +
declared constants so replay is exact. checker≠author by topology; producer writes only events/claims/
quarantine. Compounds keep their own field — never summed back into the aggregate/hedonics (double-count).

## 3. Tiering rules (what caps an operator)
- Rides heuristic geometry (VGA/plane-seg/depth/inferred-plan/cross-tier registration) → **AMBER** ceiling.
- Rides a pretrained/frozen model (depth, segmentation, a detector, a VLM) → **AMBER**.
- A declared proxy that is not the faithful published algorithm → **AMBER (proxy)**, named as such in the
  method string AND the registry (both consumer-visible — Codex caught the evidence-string gap).
- Pure deterministic classical CV + settled construct + Mac↔sandbox exact replay → eligible for **GREEN**.

## 4. Faithful-reimplementation backlog (owed; highest adequacy value)
- **V6 subband_entropy**: implement CIELab + steerable pyramid (3 scales × 4 orient) + published channel
  weights (Rosenholtz, Li & Nakano 2007), OR keep the grayscale-Gabor proxy under its honest name.
- **V7 feature_congestion**: implement Lab covariance ellipsoids + band-passed contrast + oriented-energy
  covariance + Minkowski pooling with the paper's weights (Rosenholtz 2005), validate vs the paper's stimuli.
- **V2 discomfort**: the 2-D Fourier-energy distribution with real angular subtense (Penacchio & Wilkins
  2015), or keep the radial-slope proxy. Requires a declared FOV/viewing distance to make the angular claim.
- Each replaces the proxy only after validating against the paper's reference and a labeled interior set.

## 5. M1′ — sufficient-statistic replay (the Layer-2 upgrade, owed)
Scalar replay proves reproducibility, not provenance. M1′: each operator additionally emits and the checker
replays its **sufficient statistics** — spectrum hash, edge-count + orientation histogram, pyramid-band
entropies, feature-covariance summaries, box-count series — and compares against an independent reference
implementation. A value that equals the pipeline output by a *different* procedure fails M1′ where it
passes M1. Design M1′ as an additive verify stage (`verify.py`), keyed by `audit_class`.

## 6. Calibration corpus (blocking for GREEN + for all social/compound thresholds)
A labeled interior set is required to (a) validate construct links, (b) calibrate C01/C29 thresholds
(`D0`, `RIDGE_PCTL`, `dE`, `reg_floor`) and V9 constants, (c) test the env.v2a candidates. Needs: interiors
spanning open-plan ↔ cellular, low↔high clutter, warm↔cool, day↔evening, curved↔rectilinear, with A-vs-B
region pairs where possible. **Codex is asked to propose the exact image set from the Drive + local DBs.**

## 7. Wave structure for the full table (draft — Codex to deepen)
- **Wave 0 (owed, do first):** faithful V6/V7/V2 or confirm-proxy; M1′; Mac↔sandbox replay; Article_Eater
  grounding of every anchor already shipped.
- **Wave 1 (env.v2a classical-CV cues that dedupe cleanly):** shadow softness/hardness, brightness
  gradients, glare-source count, luminance distribution, sun-patch geometry, curvature prevalence,
  orderliness/alignment — the ones with no pretrained dependency and a real construct.
- **Wave 2 (env.v2a needing depth/plane geometry → AMBER):** ceiling-height/openness, enclosure ratio,
  exit visibility, blind-corners, barrier permeability.
- **Wave 3 (detector-dependent → AMBER):** vegetation quantity, artwork/signage density, cleanliness,
  component.* object/material tags, arch.pattern detectors — need a VLM/CNN; tier AMBER by rule 3.
- **Out of build:** env.v1 physical-code numerics (instruments/specs), cross-modal, affect/cognitive targets.
Each wave = the §1 recipe + external attack before the next wave.

## 8. Definition of done (per operator)
Unit + M1 + M1′ + negative + boundary tests pass (run); `run_stage` SCORED+traceable on ≥5 interiors;
determinism ×3; Mac↔sandbox exact replay (or documented AMBER); anchors Article_Eater-grounded; survives
one external adversarial attack. Only then does the operator lose its NEEDS-FINAL-VERIFICATION / AMBER mark.
