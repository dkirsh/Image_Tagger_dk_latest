# L6 Correctness Program — Revisions v2 (2026-07-21, Cowork/Opus, overnight)

Folds the four super-expert panel reviews (`docs/PANEL_FINDINGS_L6_2026-07-21.md`) back into the plan
of record (`docs/L6_CORRECTNESS_PROGRAM_2026-07-21.md`). The original doc stays the plan of record;
this is the **v2 delta** — what changes, plus concrete implementation specs for the engineering that
was deferred (rather than shipped under-verified) this session. New queue IDs proposed at the end.

---

## 1. Construct set (Part C) — REVISED
Replace the 6 constructs with the panel-corrected set. Each is one 2AFC question + the attributes it
validates; absolute-Likert only on a shared anchor set.

| Construct | 2AFC question | Validates | Change |
|---|---|---|---|
| clutter | "more visually busy / cluttered?" | FC, SE, complexity_partition, proto-object stack | keep (cleanest) |
| openness | "more open vs enclosed?" | prospect(isovist), enclosure, W2.2 | keep |
| restorative | "easier to rest & mentally recover?" | biophilia split, spectral/fractal, restoration_nature | **anchor to PRS** (being-away/fascination/extent/compatibility) |
| mystery | "more curious to explore beyond view?" | blind_corner, barrier_permeability, choice_richness | **ADDED** (was unmeasured) |
| refuge | "stronger safe/sheltered vantage?" | refuge(new), enclosure, prospect×refuge | **ADDED** (validates prospect-refuge as a pair) |
| preference | "prefer overall?" | global hedonic → affect | keep as **criterion**, not predictor |
| ~~wayfinding-ease~~ | — | — | **DROPPED** (not judgeable from a single photo) |
| ~~calm/stress~~ | — | — | **FOLDED** into affect (Russell valence+arousal, Likert `affect_val`/`affect_aro`) |

Anchor-set Likert battery: `prs_away`, `prs_fascin` (restorativeness) + `affect_val`, `affect_aro`
(Russell). Already implemented in `viz/labeling_console.html`.

## 2. Operators — construct-validity fixes (new queue items)
- **CC-11 (prospect/refuge re-grounding):** re-ground `prospect` on **isovist area + eye-level
  openness** (use the existing `_isovist_area`/VGA machinery), not floor-depth P95; **add a `refuge`
  operator** (protected-vantage: enclosed cells with low back-exposure + forward outlook); expose a
  **prospect×refuge interaction**. Prospect-refuge cannot validate until refuge exists.
- **CC-7b (fractal faithfulness):** re-derive `fractal_dimension` from the **amplitude-spectrum slope**
  (β↔D relation) instead of box-counting a fixed-threshold Canny edge map — makes fractal-D and
  spectral-slope one coherent 1/f story and removes exposure dependence.
- **Rename `landmark_salience`'s claim** to "visual conspicuity" — it is NOT a wayfinding-landmark
  operator; do not let it validate against wayfinding.
- **Biophilia split (shapes CC-5/DEC-1):** the Wave-3 detector must produce **4 masks**
  (view-to-nature — *classify what's through the aperture* nature/built/sky; indoor greenery; natural
  materials; water), not one "biophilia" scalar. Report per-class IoU on a held-out slice of *our*
  corpus; abstain on low-confidence masks.
- **Firewall** `spatial_syntax.py` agent-sim scalars (occupancy/trace-entropy/clustering — "no
  published source") from the tier-promotion pipeline; they are visualization-only.
- **Non-monotonic fit:** fractal→restorative (and any inverted-U construct) must be fit
  non-monotonically; a Spearman ρ understates an inverted-U and could wrongly reject a valid operator.

## 3. Validation design (S3/S4 + A1) — REVISED
- **Budget (D2 rewrite):** move the bulk of judgments to **pairwise**; keep Likert only on a shared
  ~15–20-image anchor set. (90%-on-between-worker-Likert was the biggest design defect.)
- **Sampling:** `design.json` generator = **two-stage active pairwise (ASAP)** + inject the 80 A/B
  pairs as high-information edges + long-range anchors for BT graph connectivity. Not random-sparse.
- **Aggregation:** **regularized/Bayesian Bradley-Terry** (weakly-informative prior, separation-safe)
  + **Davidson tie model** ("can't tell"=tie, don't drop); per-item scores + **cluster-bootstrap CIs
  over workers**; model **rater random effects**. Output `corpus_L6/human_labels.csv`
  (`filename, construct, human_score, ci_low, ci_high, n_judgments, agreement`).
- **Promotion rule (S4 exit) — REPLACE:** promote on the **bootstrap lower CI bound** of ρ and AUC (not
  point estimates); fit thresholds/constants on a **calibration half**, report ρ/AUC on a **held-out
  half**; **Benjamini-Hochberg FDR** across the 68×6 tests; build a **6×6 MTMM discriminant matrix**
  (each attribute must correlate more with its target than off-target constructs); report **disattenuated
  ρ against the human-reliability ceiling** (observed ρ ≤ √reliability). ρ=0.5 = honest AMBER-plus, not
  validated. **Pre-register** rule + thresholds before unblinding.
- **Calibration:** **Platt/logistic** (or monotone spline / beta) over isotonic at n≈200; cross-validate
  the threshold out-of-sample; report full ROC+CI, not in-sample Youden.
- **QC additions:** independent pre-registered golds (two difficulty tiers, NOT crowd-consensus on the
  construct under test → circularity); L/R counterbalance + per-worker side-bias; intra-rater re-show
  (~5%); identical-image "can't tell" catch; min AND max time; device/UA + bot/AI detection; **quota-
  sample demographics + covariates**; don't hard-drop minority raters (model rater effects). Report
  Krippendorff α per construct with bootstrap CI + split-half BT reliability.
- **Corpus confounds (S0/curation):** audit `--gen-ab` for **luminance leakage** (a manipulation must
  not just be an exposure shift); balance + covary mean luminance, photo quality, colour temperature,
  FOV; include **clutter×openness crossing pairs** to break collinearity.
- **Platform/cost (D-rewrite):** Prolific-primary + CloudResearch A/B, **platform as a covariate — don't
  pool until exchangeable on golds**; **$15/hr, 12–20 s/judgment**; **pilot 40–60/platform** (not 20),
  soft-launch 5–10 first; realistic **~$1,700 core / ~$3–5k full** (was $1–1.5k).

## 4. M1′ / verification (A5/A6) — REVISED + implementation spec for the deferred batch
**Reporting fix (do first, cheap):** report **two** coverage numbers — *independent-recompute
faithfulness signature* (~8 preds: luminance_field, radial_fft, ssim_map, orientation_hist, box_count,
edge_stats, color_palette, jpeg_tiles) vs *tamper/stale-only* (the 20 operator_extract, incl. this
session's 13). Fix the `m1_prime.py` docstring: `round(x,6)` is a **6-decimal absolute grid** (not "6
sig-figs"), and it is a **same-machine tamper/stale control, NOT the cross-machine exact-replay
guarantee** — cross-env lives in a separate tolerance layer.

**CC-9b — cross-env tolerance schema (spec, next session):**
1. Per audit class, declare each stat field `exact` (integer counts, discrete tags, pre-rounded 3dp) or
   `tol:<eps>` (BLAS/LAPACK/FFT floats; eps from the L5 measurements ≈ 4e-4). Large-magnitude stats
   (`radial_logpower`, lstsq slope/intercept, box-count D) MUST be `tol`.
2. `replay()` emits two verdicts: **DIGEST-MATCH** (same machine, bitwise) and **TOL-MATCH** (cross
   machine, per-field eps). Promotes the un-audited `CROSS_ENV_TOL` script into the tested core.
3. **Pin determinism at the operator entry point** (not just the loader): `cv2.setNumThreads(1)` +
   `OMP/OPENBLAS/MKL_NUM_THREADS=1` set process-wide at annotator import; record a per-record **env
   fingerprint** (`cv2.getBuildInformation` hash, numpy BLAS vendor, versions) into the record.
4. Change `replay()` scalar tol from absolute `0.02` to `max(0.02, 0.01·|s|)`.
5. **Measure `jpeg_tiles` (processing_load_proxy) cross-env explicitly** — it digests libjpeg byte
   lengths (build-dependent); likely needs `tol` or a decode-only respec. **Flag `orderliness_alignment`
   / `verticality_cues`** — `n_segments` from LSD is build-variable → mark those fields `tol` or drop
   from the cross-env digest (they remain valid *same-machine* tamper controls, as shipped).

**A5 tranche-2 — geometry/plan bindings (spec, next session):** keep the single expensive
`geometry_plan` substrate digest on C1, and add a cheap **`plan_ref` audit class** = digest of
`{grid_hash (derivation.grid_hash), cell_m}` for every plan-consumer (9 geometry-chain ops + 8
`req=['plan']` metrics). Requires threading the **already-computed** plan from the annotator's
`geometry_chain` into the emit path (avoid re-running the chain — that was the whole point). Checker
verifies all plan-consumers in a stage share the one `grid_hash` C1 certifies → closes the plan-identity
provenance hole at O(1)/consumer. Label `geometry_plan`/`plan_ref` **same-machine-only** (exact hash of
a branch-unstable grid). **CC-3 value-input criteria M1′** = `(canonical input_values) + (plan_ref) +
(reduction signature)` digested on a **FIXED synthetic plan fixture** (separates reduction-faithfulness
from the plan's 13% instability).

**A6 robustness:** keep the two axes separate (cross-env determinism vs jittered stability). Metamorphic
suite with pre-registered relations (invariance: roll/flip/geometry-equivariance; monotonic: gamma↑→
glare↑; bounded jitter σ≈1–3 DN + high-Q JPEG). Geometry chain: **N≈30 jittered replicates/image →
CoV(cell_m) + bimodality → per-image trustworthiness flag** (high CoV → that image's plan metrics
abstain/cap AMBER) instead of a blanket Tier-B cap.

## 5. A2 (faithful V2 / Penacchio-Wilkins) — partially unblocked
Recipe recovered (2° tiles → 64×64 px, 50% overlap, ≤16 cpd; fit tile 2-D log-amplitude spectrum to a
reference anisotropic cone; weight residuals by **Mannos-Sakrison CSF** `A(f)=2.6·(0.0192+0.114f)·
exp(−(0.114f)^1.1)`, f in cpd; report peak/mean/CoV residual). **Still reference-gated on the exact
cone params** (ViStA 350-image cone — acquire from authors / Dryad `g79cnp5kw` / ViStA *Buildings* 2025).
Faithful metric needs **cpd → couples A2 to A4/W2.7 scale anchor**; implement with a *declared* ppd
emitted in extras until W2.7 lands. **FC ×4 upConv gain** is almost certainly a real faithfulness bug
(× element-wise-max collapse, coarse clutter drops out) — adjudicate the FC **map** (not just scalar)
vs the authors' MATLAB to 1e-6.

## 6. Proposed new/updated queue IDs
`CC-7b` fractal-from-spectrum · `CC-9b` M1′ cross-env tol schema + thread-pin + env fingerprint ·
`CC-11` prospect isovist re-grounding + refuge operator + interaction · `A5-t2` geometry/plan `plan_ref`
bindings · `A5-t3` CC-3 value-input M1′ on fixed plan fixture · `DEC-1` now includes the 4-way biophilia
mask split · `S3` console DONE (revised constructs) · `S4` promotion-rule v2 (CI lower-bound + held-out +
MTMM + FDR + disattenuation) · `D2` budget → pairwise-dominant + anchor set · index DONE.

## 7. Critical-path note
S0 (corpus + Drive backfill, David-gated on the own client_id) still gates S3-pilot → S4. Engineering
(A5 tranche-2, CC-9b, CC-7b, CC-11, A2) runs in parallel and is not corpus-gated. The single biggest
lever is still A1 (construct validation) — now with a defensible design.
