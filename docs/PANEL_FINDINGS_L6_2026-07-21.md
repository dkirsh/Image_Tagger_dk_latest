# Super-Expert Panel Findings — L6 Correctness Program (2026-07-21, Cowork/Opus, overnight)

Four independent super-expert reviewers convened to review `docs/L6_CORRECTNESS_PROGRAM_2026-07-21.md`
(what's done, what's planned, advice) and mine the literature. Panels: (1) low/mid-level vision
psychophysics; (2) environmental psychology / architectural cognition; (3) psychometrics /
crowdsourcing methodology; (4) software verification / reproducibility. Each searched arXiv /
Consensus / journals for primary sources. Full reviews below; **synthesis + prioritized actions
first.**

---

## SYNTHESIS — cross-cutting themes & prioritized actions

### Theme 1 — Several operators measure a *proxy of* the construct, not the construct (validity gap)
- **Prospect** is floor-depth P95; the literature's prospect is **isovist openness / viewshed** (you
  already have the isovist machinery). **Refuge is missing entirely** — prospect-refuge is a *joint*
  construct and cannot validate as specified. **Add a refuge operator; re-ground prospect on isovist
  area + eye-level openness.** [env-psych] → new queue item **A2b / CC-11**.
- **landmark_salience** is bottom-up conspicuity, not wayfinding landmark-ness (semantic/memorable).
  **Rename its claim; do not let it validate against "wayfinding."** [env-psych]
- **fractal_dimension_local** box-counts a *Canny edge map* with fixed thresholds — not the
  luminance-surface / amplitude-spectrum fractal the aesthetics literature cites, and exposure-
  dependent. **Re-derive D from the amplitude-spectrum slope** so fractal-D and spectral-slope are one
  coherent 1/f story. [vision] → **CC-7b**.

### Theme 2 — The rating constructs (Part C) need revision before S3
- **Split "restorative"** into a **PRS-anchored** multi-item construct (being-away / fascination /
  extent / compatibility), not one folk word. **"calm/stress" is redundant** with it — move to a
  Russell **valence+arousal** circumplex. **"wayfinding-ease" won't validate from a single photo**
  (it's a building-configuration property) — drop or reframe as *local legibility*. **Add MYSTERY**
  ("is there more to see around the corner?" — the human target for blind_corner / barrier_permeability)
  **and REFUGE/shelter** (to validate prospect-refuge as a pair) **and FASCINATION** (distinct from
  preference; the fractal/complexity target). [env-psych + psychometrics] → **revised construct set**.
- **Biophilia is multi-dimensional** — split into **view-to-nature (classify what's *through* the
  window), indoor greenery, natural materials, water**; a single "biophilia" scalar won't validate.
  [env-psych] → shapes **CC-5 / DEC-1**.
- **fractal → restorative must be fit NON-monotonically** (inverted-U, D≈1.3–1.5 peak); a Spearman ρ
  understates an inverted-U and could wrongly reject a valid operator. [env-psych + vision]

### Theme 3 — The validation *design* (S3/S4) has fixable statistical defects
- **Budget is inverted:** 90% of judgments on between-worker absolute Likert (the *least* comparable
  instrument). **Reallocate to pairwise; keep only a shared ~15–20-image anchor set** for the origin.
  [psychometrics] → rewrite **D2**.
- **Promotion rule (ρ≥0.5 AND AUC≥0.70) is unsound as written:** promotes on point estimates.
  **Fix:** promote on **bootstrap lower CI bound** (cluster-bootstrap over *workers*), **held-out
  image split** (fit on calibration half, report on held-out), **MTMM discriminant matrix** (each
  attribute must correlate more with its target than off-target constructs), **FDR** across the 68×6
  tests, and **report disattenuated ρ against the human-reliability ceiling**. ρ=0.5 is "honest
  AMBER-plus," not validated. [psychometrics] → rewrite **S4 exit + A1**.
- **Sparse global pairwise is inefficient/fragile:** use **two-stage active sampling (ASAP)**,
  **regularized/Bayesian Bradley-Terry** (separation-safe prior), **Davidson tie model** (don't drop
  "can't tell"), inject A/B pairs + anchor edges for graph connectivity. [psychometrics]
- **Cost realism:** ~$1,700 core (not $1–1.5k); up to $3–5k for the full Likert+pairwise; **$15/hr**,
  **12–20 s/judgment**, **pilot 40–60/platform** (not 20). Prolific+CloudResearch dual-source, but
  **treat platform as a covariate — don't pool until exchangeability is shown on golds**. [psychometrics]
- **#1 corpus confound = brightness/exposure.** Audit `--gen-ab` for **luminance leakage** (a
  "daylight" manipulation must not just be an exposure shift); balance + covary mean luminance. Also
  control photo aesthetic quality, colour temperature, FOV, clutter×openness collinearity. [env-psych]

### Theme 4 — M1′ cross-env story is mislabeled; coverage metric conflates two things
- **The 6-decimal digest is a *same-machine* tamper/stale control, NOT the cross-machine exact-replay
  guarantee the docstring claims.** `round(x,6)` is an **absolute** grid (not "6 sig-figs"); L5 measured
  cross-env deltas of ~4e-4 on entropy/D — **100× the grid** — so large-magnitude float stats
  (radial_logpower, lstsq slope, box-count D) will NOT survive Mac↔sandbox at 1e-6. The real cross-env
  layer is the **un-audited, un-unit-tested `CROSS_ENV_TOL`** side script. **Fix:** per-field
  **exact / tol:<eps>** schema per audit class; emit two verdicts **DIGEST-MATCH** (same machine) vs
  **TOL-MATCH** (cross machine, declared eps); pin `cv2.setNumThreads(1)` + BLAS threads; record an
  **env fingerprint** (cv2 build / BLAS vendor). [verification] → new queue item **CC-9b / A6**.
- **Report TWO coverage numbers:** *independent-recompute faithfulness signature* (~8 predicates:
  luminance_field, radial_fft, ssim_map, orientation_hist, box_count, edge_stats, color_palette,
  jpeg_tiles) vs *tamper/stale-only* (the 20 operator_extract, incl. this session's 13). The "15→28"
  count is honest as plumbing but inflates the faithfulness metric. [verification]
- **`geometry_plan.grid_hash` is an exact hash of a nondeterministic, branch-unstable grid** (13%
  cell_m swing, L5) → **same-machine-only; label it.** [verification]
- **"Audit substrate once" (geometry_plan on C1) leaves a plan-identity provenance hole:** C2…C29
  aren't tied to the exact plan instance C1 digested. **Fix:** every plan-consumer record carries a
  cheap **plan-ref tag = grid_hash + cell_m**; checker verifies all consumers share the one grid_hash
  C1 certifies. Middle path: substrate digested once + O(1) per-consumer plan-ref. [verification] →
  shapes **A5 tranche 2**.
- **CC-3 value-input criteria M1′ = (canonical inputs) + (plan ref) + (reduction signature)** on a
  **FIXED synthetic plan fixture** (separates reduction-faithfulness from the plan's 13% instability).
  [verification]
- **RISK on this session's batch:** `orderliness_alignment` / `verticality_cues` digest `n_segments`
  from **LSD (`createLineSegmentDetector`), which is build-variable across environments** — fine as a
  *same-machine* tamper control (my determinism test passed in-sandbox), but flag for the cross-env
  tolerance schema (candidate `tol` or drop from cross-env digest). `jpeg_tiles` (processing_load_proxy)
  digests libjpeg **byte lengths** — cross-env false-RED risk; measure explicitly. [verification]

### Theme 5 — A2 (faithful V2 / Penacchio-Wilkins) is PARTIALLY unblocked
The vision panel recovered the faithful recipe (2° tiles → 64×64 px, 50% overlap, ≤16 cpd; fit tile
2-D log-amplitude spectrum to a **reference anisotropic cone**; weight residuals by the
**Mannos-Sakrison CSF** `A(f)=2.6·(0.0192+0.114f)·exp(−(0.114f)^1.1)`, f in cpd; report peak/mean/CoV
residual). **Still reference-gated on the exact cone parameters** (ViStA's 350-image cone) — a [PORT]
acquisition target (authors / Dryad `g79cnp5kw` / ViStA *Buildings* 2025 paper). **Also: the faithful
metric needs cycles-per-degree → couples A2 to A4/W2.7 scale anchor.** And the **FC ×4 upConv gain**
is almost certainly a real faithfulness bug interacting with element-wise-max collapse (coarse clutter
drops out) — **adjudicate the FC *map* (not just scalar) against the authors' MATLAB to 1e-6.** [vision]

### Prioritized action list (overnight-executable vs David/panel-gated)
**Executable now (engineering, no external dep):** (a) M1′ cross-env per-field tolerance schema +
thread-pin + env fingerprint + two-verdict replay [CC-9b]; (b) M1′ tranche-2 geometry/plan bindings
with per-consumer plan-ref tag [A5]; (c) build the revised 2AFC console with the corrected constructs +
QC + two-stage design [S3]; (d) corpus retrieval index; (e) split the coverage metric + fix the
docstring cross-env claims. **Panel/David-gated:** DEC-1 model, the Penacchio-Wilkins cone acquisition,
the FC-map MATLAB adjudication, the actual Prolific campaign + budget, and re-grounding prospect/adding
refuge (design sign-off).

---

## FULL REVIEW 1 — Vision psychophysics (fluency / clutter / spectral / fractal)

**Done — assessment.** FC/SE faithful ports (`faithful_clutter.py`) are sound and done the right way:
unmodified vendored `visual_clutter` 1.0.7 on the invariant-tested `_pyrtools_min` shim; every constant
the reference's own (color/0.2088, contrast/0.0660, orient/0.0269, Minkowski p=1; SE chroma 0.0625);
subband std adjudicated ~1e-7 vs real pyrtools. The abstain gate (grayscale std < 2 DN → None) is
correct. `scalar/12` (FC) and `se/4` (SE) are honestly flagged as display full-scale only. **DT-1 is
the substantive finding and handled correctly**: reference FC/SE rank the minimal foliage-framed
Farnsworth House *above* the cluttered industrial office because vegetation's contrast/orientation/
colour variance reads as feature congestion — the classic maps/UI→natural-scene transfer failure of
the 2007 measure. Handled right: no ordering assert, both directions recorded, corpus adjudicates,
`proto_object_count` recovers the human ordering. `spectral_slope_deviation` (V2 proxy) is an honest,
correctly self-labeled radial-slope statistic (Hann window, DC/Nyquist exclusion, R²-gated) that does
not overclaim to be the 2-D metric. **`fractal_dimension_local` is the most fragile**: box-counting D
on a *Canny edge map* (fixed thresholds 60,160) — not the luminance-surface/amplitude-spectrum fractal
the aesthetics literature cites, and exposure/scale-dependent.

**Planned (A2) — critique.** (1) The true 2-D Penacchio-Wilkins metric **fundamentally requires an
angular anchor (cpd)** the proxy dropped — the CSF weighting lives in cycles-per-degree; this **couples
A2 to A4/W2.7**. Implement the 2-D cone-residual parameterized by a *declared* pixels-per-degree, emit
that assumption, let W2.7 replace it later. (2) The **reference anisotropic cone is a load-bearing
constant you don't have verbatim** — acquire ViStA's 350-image cone params under [PORT] discipline, do
not invent. (3) Keep the proxy running in parallel; DEC-3 retirement fires only after the faithful
metric beats it on the corpus.

**Faithful recipe / constants to port:** luminance → tiles subtending 2° VFOV, resize each to 64×64 px
(32 px/deg, Nyquist ~16 cpd), 50% overlap → per-tile 2-D FFT amplitude → log-amp vs log-radial-freq →
fit to reference cone (natural 1/f + cardinal-orientation excess) → residual = summed Fourier-space
differences → **weight residuals by Mannos-Sakrison CSF: `A(f)=2.6·(0.0192+0.114f)·exp(−(0.114f)^1.1)`,
f in cpd, peak ≈8 cpd** (single biggest lever: 18%→~27% variance) → aggregate tiles as peak / mean /
coefficient-of-variation residual. Verify these constants against the paper to ~1e-6 before committing.

**FC ×4 upConv gain — yes, needed, not cosmetic.** `upConv` inserts zeros (2×/axis → 1/4 nonzero) then
convolves with `[0.05 0.25 0.4 0.25 0.05]`; amplitude preservation across the upsample needs ×4. With
**element-wise-max cross-scale collapse**, coarse clutter attenuated 4×/level systematically *loses the
max* to fine detail and drops out — biasing FC toward fine texture and plausibly worsening DT-1.
Decisive test: reproduce the authors' MATLAB FC **scalar AND map** to ~1e-6; a low-frequency-blob
synthetic exposes it in one run. Fix for faithfulness regardless (it changes cross-scale ranking + the
map, both claimed).

**Top risks:** (1) 2007-clutter→natural-interior transfer gap (no code fix; corpus only — force
foliage-rich vs bare A/B pairs so calibration *sees* it; consider promoting proto_object_count as the
interior "busyness" measure). (2) Scale/angular dependence pervades the family and is unanchored (make
W2.7 a hard dep of A2; emit ppd; jitter-test these ops). (3) FC ×4 gain × max-collapse latent bug
(reproduce the *map*). (4) fractal_dimension measures Canny edges w/ fixed thresholds (re-derive D from
amplitude-spectrum slope). (5) Invented CSF/normalization constants in V2 (replace with Mannos-Sakrison
in cpd; retire proxy constants, don't calibrate them).

**References:** [1] **Penacchio & Wilkins (2015), Visual discomfort and the spatial distribution of
Fourier energy, *Vision Research* 108:1–18**, doi:10.1016/j.visres.2014.12.013 — THE primary source.
[2] **ViStA / Visual Discomfort in the Built Environment (2025), *Buildings* 15(13):2208** — clearest
reimplementation recipe + constants, on architectural interiors/façades (your domain). [3] **Mannos &
Sakrison (1974), *IEEE Trans. IT* 20(4):525–536** — the CSF constants. [4] **Penacchio et al. (2023),
A mechanistic account of visual discomfort, *Front. Neurosci.* 17:1200661**, code Dryad
doi:10.5061/dryad.g79cnp5kw — likely reference implementation. [5] **Juricevic et al. (2010),
*Perception* 39(7):884–899**, doi:10.1068/p6656 — departure-from-1/f → discomfort. [6] **Fernandez &
Wilkins (2008), *Perception* 37(7):1098–1113** — human-discomfort dataset. [7] **O'Hare & Hibbard
(2011), *Vision Research* 51(15):1767–1777** — mid-SF energy → discomfort. [8] **Penacchio et al.
(2021), *Front. Neurosci.* 15:711064**, code github.com/openacchio — chromatic extension + author code.
[9] **Field (1987), *JOSA A* 4(12):2379–2394** — the 1/f baseline the "naturalness" premise cites.
_Author code to pursue for a verbatim reference: github.com/openacchio + Dryad g79cnp5kw; the 2015
metric has no standalone public repo — ViStA is the most implementation-complete public description.
ScienceDirect/ResearchGate full texts were robots-blocked; adjudicate cone params + Mannos-Sakrison
normalization against the paper before committing._

## FULL REVIEW 2 — Environmental psychology / architectural cognition

**Bottom line.** Engineering discipline is unusually good (honest abstention, declared constants, the
`1-RA` integration fix, refusing to average visual vs physical permeability). But almost none of the
spatial/biophilia/prospect-refuge operators are yet operationalized in a way a domain expert would sign
off as *construct-valid* — the tier language (mechanically-green ≠ construct-validated) is exactly
right. Dominant threats: (a) single-view operationalization of constructs defined over the 3-D
navigable environment; (b) a rating design that conflates distinct latent constructs and under-anchors
them.

**Operators as done.** *Prospect* = P95 floor view-depth → **weak validity**: floor-depth ≠ prospect
(deep narrow corridor scores high, shallow room w/ vista scores low); re-ground on **isovist area +
openness + eye-level/horizon band** (you have the isovist machinery). Window-view contamination is a
first-order confound. **No refuge operator at all** — prospect-refuge is joint; preference peaks at
moderate prospect *with* refuge. *Enclosure_index* is plausible (right family) but overlaps W2.2
ceiling-openness — validate both against the *same* "open vs enclosed" latent or you double-count.
*Landmark_salience* = bottom-up conspicuity, **not** a wayfinding landmark (semantic/memorable/
decision-relevant — Lynch, Sorrows & Hirtle); rename its claim. *VGA/intelligibility* is the strongest
module (faithful Turner port, correct qualitative self-tests) **but** intelligibility/integration are
building-configuration properties computed here from an *inferred* plan of one ~65° view — a
level-of-analysis mismatch. *Wayfinding load (C4)* junction heuristic is honest but not a validated
cognitive-map-error predictor. **Firewall `spatial_syntax.py` agent-sim scalars** (occupancy/trace-
entropy/clustering — "no published source") from tier promotion; they're illustrative. Fluency family:
the **hedonic tags are the unlicensed part** — fractal→preference is a *non-monotonic inverted-U*
(D≈1.3–1.5, Taylor/Hagerhall); enforce non-monotonic fits (S4 isotonic instinct is right).

**Planned — Wave-3 detector (highest-value item).** Right move (chromaticity "plant" heuristic won't
survive review). Requirements: **biophilia is multi-dimensional** (Terrapin 14 Patterns) — split
view-to-nature / indoor greenery / natural materials / water (different, non-additive restorative
effects; window-view-to-nature has the strongest stress-recovery evidence). **View content matters more
than view existence** — classify what's *through* the aperture (nature/built/sky). Report per-class IoU
on *your* corpus; abstain on low-confidence masks. Materials need a texture/material model, not hue.

**The 6 constructs — revision (per-construct verdicts):** restorative → **split, anchor to PRS**;
visually-busy → **keep** (cleanest); wayfinding-ease → **won't validate from one photo, drop/reframe as
local legibility**; open-vs-enclosed → **keep** (expect collinearity w/ prospect+restorative); calm/
stress → **redundant, use Russell valence+arousal**; prefer-overall → **keep as criterion, not
predictor**. **Missing:** mystery (invites-exploration — target for blind_corner/barrier_permeability),
refuge/shelter (to validate prospect-refuge as a pair), fascination (≠ preference; the complexity
target), optionally coherence/order.

**Design advice.** Confounds to control in the corpus: **luminance/exposure (#1 — brighter = calmer/
more open/preferred regardless; audit `--gen-ab` for exposure leakage)**, photo aesthetic quality,
colour temperature (you compute warmth — covary it), **clutter×openness collinearity (include crossing
pairs)**, FOV/focal length, people/furniture scale cues. **Anchor to instruments:** restorativeness →
**PRS / PRS-11** (3–4 items); affect → **Russell circumplex**; preference → single-item liking;
prospect-refuge → **Stamps permeability** + outlook/shelter item pair (validate the *interaction*);
openness → **Vartanian enclosure/ceiling-height** wording. 2AFC+BT is the right workhorse; anchor BT to
absolute ratings + check BT–Likert rank convergence; model **rater random effects**. **Expertise
reverses effects** (architects prefer more complex/enclosed) — keep expert adjudication for *objective*
attributes, crowd for *hedonic*. **Culture** shifts biophilia/water/enclosure — record region, test
culture×construct before pooling (else WEIRD bias baked into constants). Add a monitor-brightness check
trial. Expect clutter/openness to clear α≥0.6 and wayfinding/one-word-restorative to fall short (itself
diagnostic).

**Top risks:** (1) single-image operationalization of configuration-scale constructs (prospect/
intelligibility/wayfinding) — highest severity (operators "work" mechanically, measure the wrong
thing). (2) Prospect=floor-depth + refuge/mystery missing → prospect-refuge unvalidatable as specified.
(3) Construct collinearity (restorative≈calm≈preference≈open) → ρ≥0.5 promotes on shared variance
(pre-register primary predictors; partial correlations/multivariate, not bare pairwise ρ). (4)
Brightness confound in `--gen-ab` + corpus (every "validated" hedonic effect may be a lighting
artifact). (5) Biophilia collapsed to green-fraction; view content not classified.

**References:** [1] **Hartig et al. (1997), PRS**, doi:10.1080/02815739708730435 (short form Pasini/
Berto PRS-11, 2014). [2] **Kaplan (1995), ART, *JEP***, doi:10.1016/0272-4944(95)90001-2. [3] **Ulrich
et al. (1991), SRT, *JEP***, doi:10.1016/S0272-4944(05)80184-7. [4] **Stamps (2016), prospect-refuge
meta-analysis, *City Territory Arch.***, doi:10.1186/s40410-016-0033-1. [5] **Vartanian et al. (2013),
contour/approach-avoidance, *PNAS***, doi:10.1073/pnas.1301227110 (+ 2015 ceiling-height, JEP). [6]
**Coburn, Vartanian & Chatterjee (2017), *J. Cog. Neuro.***, doi:10.1162/jocn_a_01146. [7] **Turner et
al. (2001), isovists→visibility graphs, *EPB***, doi:10.1068/b2684. [8] **Hagerhall, Purcell & Taylor
(2004), fractal landscape preference, *JEP***, doi:10.1016/S0272-4944(03)00087-6 (inverted-U). [9]
**Rosenholtz, Li & Nakano (2007), Measuring visual clutter, *J. Vision***, doi:10.1167/7.2.17. [10]
**Browning, Ryan & Clancy (2014/2024), 14 Patterns of Biophilic Design, Terrapin Bright Green.**
(Supporting: Berto 2005; Peer 2022 / Douglas 2023 on Prolific quality.)

## FULL REVIEW 3 — Psychometrics / crowdsourcing methodology

**Summary verdict.** Well above the median crowd-validation effort (2AFC-primary, gold/attention QC, BT
aggregation, explicit promotion rule, "record the measured ρ" honesty). But won't yet produce a
defensible *construct-validity* claim, for four fixable reasons: (1) budget inverted toward the weakest
instrument; (2) promotion rule fires on point estimates — no CIs, no held-out, no multiple-comparison/
winner's-curse control, no discriminant validity; (3) global pairwise is random-sparse (1.5–3×
inefficient, identifiability-fragile) and drops ties; (4) cost/time optimistic ~2–3×.

**Design critique.** K=15 is adequate for the *designed A/B pairs* (~0.85 power at true P=0.75; ~1.0 at
0.85) but K-per-item is **not** what governs BT precision for the 200 singletons — that's *comparisons
per object* + graph connectivity, set at only 8–12/image/construct (thin). **Budget inverted:** D2
spends 18,000 of ~20,000 judgments (90%) on absolute Likert, but between-worker Likert has no shared
reference frame — exactly the instrument C1 says not to trust. Reallocate: minimal Likert as a fixed
**shared anchor set** (~15–20 images every worker rates) to fix the BT origin; move the rest into
pairwise. **Promotion rule (ρ≥0.5 AND AUC≥0.70) not sound:** promotes on point estimates — ρ=0.50 over
n=200 has 95% CI ≈[0.36,0.62]; AUC=0.70 over 80 pairs has CI ≈[0.59,0.81]. **Promote on the CI lower
bound.** Winner's curse across 68×6 tests → **held-out image split** (fit on calibration half, report on
held-out) + **Benjamini-Hochberg FDR**. ρ=0.5 = 25% shared variance = honest AMBER-plus, not
validated. **Missing convergent/discriminant structure** → build a **6×6 MTMM matrix** (each attribute
must correlate more with its target than off-target — highest-value addition). Sparse-random pairwise
risks a disconnected graph (non-identifiable BT) → **two-stage active sampling** (ASAP: equal accuracy
at 1.5–3× fewer comparisons; or "Just Sort It!"), inject A/B pairs as high-info edges + long-range
anchors for connectivity.

**QC gaps (baseline good).** (1) Two-tier golds; **pre-register independent golds** (expert/physical
ground truth, not crowd-consensus on the same construct → circularity). (2) Counterbalance L/R, measure
per-worker side bias; re-show ~5% pairs for intra-rater reliability; seed identical-image pairs
(answer="can't tell"). (3) 2024–26 bot/AI crisis: gold-only is insufficient — copy-paste disable,
device/UA fingerprint, Prolific native bot detection, RT anomaly detection, **max-time** as well as min.
(4) **Don't hard-drop minority raters** — mixed-effects w/ random rater effects; hard drops only for
demonstrable inattention. (5) Demographics: **quota-sample + pre-register covariates**; name the target
population per attribute's cited theory. Report **Krippendorff's α per construct w/ bootstrap CI** and a
**split-half BT reliability**.

**Stats pipeline.** **Hierarchical/Bayesian BT** (or penalized MLE) w/ weakly-informative prior N(0,1–2)
— mandatory (objects winning/losing all comparisons give infinite MLEs under plain BT = the sparse-
design failure); pwcmp implements it. **Model ties (Davidson 1970 / Rao-Kupper)** — don't drop
"can't tell." **CIs: cluster-bootstrap over workers** (judgments non-independent); promote on the lower
bound. **Anchoring BT to Likert is largely unnecessary for validation** — ρ (monotone) and AUC
(directional) are invariant to the affine BT transform; keep the pipeline scale-free, anchor only for a
hedonic zero. **Calibration: Platt/logistic over isotonic at n≈200** (isotonic is data-hungry,
overfits); cross-validate out-of-sample; Youden in-sample is optimistic — report full ROC+CI,
CV the threshold. **State a measured number honestly:** headline ρ (cluster-bootstrap 95% CI) + ρ² +
AUC (CI) on held-out; report human-reliability + the **attenuation ceiling** (observed ρ capped at
√reliability → quote disattenuated ρ); report the MTMM discriminant contrast. Pre-register before
unblinding.

**Platform.** Prolific-primary + CloudResearch-Connect A/B is right for 2026 (Douglas 2023, Peer 2022
put both top-tier over raw MTurk); dual-source as risk management but **treat platform as a covariate —
don't pool until exchangeability shown on golds**. **Cost realism: estimate is optimistic ~2–3×** —
10 s/judgment too fast (budget 12–20 s + consent/instruction/gold overhead); $12/hr is a floor,
2026 norm ~**$15/hr** → 20k×15 s ≈ 83 hr × $15 ≈ $1,250 worker + ~35% fee ≈ **~$1,700 core**; full
Likert+pairwise (~40k) ≈ **$3,000–5,000**. **Pilot 40–60/platform** (n=20 α CIs uselessly wide); run a
5–10-worker soft launch first, then confirm BT graph connectivity before scale-up.

**Top risks:** (1) instrument inversion + Likert reference-frame drift; (2) under-powered/possibly-
circular promotion rule; (3) ground-truth/population validity of culturally-variable constructs; (4)
2024–26 data-quality crisis (noise attenuates ρ → false AMBER); (5) BT identifiability & efficiency.

**References:** [1] **Douglas, Ewell & Brauer (2023), *PLOS One***, doi:10.1371/journal.pone.0279720 —
platform quality. [2] **Peer et al. (2022), *Behavior Research Methods* 54:1643**, doi:10.3758/
s13428-021-01694-3. [3] **Mikhailiuk et al. (2020), ASAP, arXiv:2004.05691.** [4] **Perez-Ortiz &
Mantiuk (2017), pwcmp, arXiv:1712.03686** — regularized Thurstonian BT + CIs. [5] **Maystre &
Grossglauser (2015), Just Sort It!, arXiv:1502.05556.** [6] **Davidson (1970), BT with ties, *JASA*
65:317**, doi:10.1080/01621459.1970.10481082. [7] **Zapf et al. (2016), Krippendorff α + CIs, *BMC MRM*
16:93**, doi:10.1186/s12874-016-0200-9. [8] **Niculescu-Mizil & Caruana (2005), Platt vs isotonic,
ICML**, doi:10.1145/1102351.1102430. [9] **Hanley & McNeil (1982), AUC SE/CI, *Radiology* 143:29**,
doi:10.1148/radiology.143.1.7063747. [10] **Asher et al. (2026), keystroke AI-cheating detection,
*AMPPS***, doi:10.1177/25152459261424723. (Depth: BT survey arXiv:2601.14727.)

## FULL REVIEW 4 — Software verification / reproducibility

**M1′ assessment.** The boundary (RULE-0: shared operator code → catches tamper/stale/wrong-pipeline/
wrong-image/abstention-lie, NOT algorithm bugs) is honestly drawn and well-documented. **But two tiers
are conflated:** (1) *independent-recompute* classes (luminance_field, radial_fft, ssim_map, + the
reference-mirrored orientation_hist, box_count, edge_stats, color_palette, jpeg_tiles) reimplement the
pre-scalar stage → genuine (partial) **faithfulness** signal; (2) *shared-code* classes (the 20
operator_extract, incl. this session's 13; and the no-extras glare/landmark = scalar-only) → **pure
tamper/stale, zero faithfulness content.** Report TWO coverage numbers, not "15→28" as one.

**6-decimal tolerance is wrong for cross-env, and the docstring overstates it.** `round(x,6)` is a
**6-decimal absolute grid, not "6 sig-figs"** (comment L47 wrong). `radial_logpower` (−12…+30), lstsq
slope/intercept, box-count D are raw floats; a 1e-4 BLAS delta on magnitude ~20 is **100× above** the
grid → digest flips. **L5 already measured this** (entropy/D cross-machine ≤4e-4, edge counts ≤0.15% —
100–1000× the grid), so the strict digest does NOT survive Mac↔sandbox for Sobel/Canny/FFT/LAPACK
classes; the real guarantee rests on the **separate, un-audited, un-unit-tested `CROSS_ENV_TOL`** side
script. Docstring claims (L20, L44) that fixed rounding "IS the Mac↔sandbox exact-replay check" are
over-stated. **Fix: per-field tolerance schema per audit class** — each stat `exact` (integer counts,
discrete tags, pre-rounded 3dp) or `tol:<eps>` (BLAS/LAPACK/FFT floats, eps from L5); emit **two
verdicts DIGEST-MATCH (same machine, bitwise) vs TOL-MATCH (cross machine, per-field eps)**. Promotes
`CROSS_ENV_TOL` into the audited, tested core.

**Coverage plan.** "Audit substrate once" (geometry_plan on C1) is defensible (17× recompute avoided)
but leaves a **plan-identity provenance hole**: C2…C29 are separate records, and the chain is
run-to-run nondeterministic (L5: cell_m 13% swing at a branch point), so "the plan C1 read" ≠
guaranteed "the plan C29 read." **Middle path: keep the one substrate digest on C1 + require every
plan-consumer to carry a cheap plan-ref tag = `grid_hash` (exists, `derivation.grid_hash`) + `cell_m`;
checker verifies all consumers share the grid_hash C1 certifies.** O(1) per consumer, closes the hole.
`grid_hash` is an exact hash of a nondeterministic grid → **same-machine-only, label it** (never
replays cross-machine). **CC-3 value-input M1′ = (canonical inputs) + (plan ref) + (reduction
signature)** on a **FIXED synthetic plan fixture** (separates reduction-faithfulness from the plan's
13% instability; else flaky RED). The CC-3 fail-closed skeleton (token-no-value→UNKNOWN,
no-token→ABSTAINED) is the right hanger.

**Robustness (A6) — keep two axes separate:** cross-env exact replay (same input, diff machine =
determinism) vs jittered-input (perturbed input, same machine = stability). **Cross-env:** PNG-only
(L5 Finding 1: JPEG decodes differently across libjpeg builds — no digest survives); pin
`cv2.setNumThreads(1)` + `OMP/OPENBLAS/MKL_NUM_THREADS=1`; record a per-record **env fingerprint**
(cv2.getBuildInformation hash, numpy BLAS vendor, versions) — a digest without it is uninterpretable
cross-machine. **Metamorphic suite — pre-register relations:** invariance MRs (circular roll — make the
allowlist a *positive* test; h-flip; geometry equivariant), monotonic MRs (gamma↑→glare↑; contrast→
edge_clarity), bounded-perturbation jitter (Gaussian σ≈1–3 DN, high-Q JPEG round-trip), publish
dScalar/dNoise amplifiers. **Geometry chain needs distributional, not mean, robustness** (branch
point): N≈30 jittered replicates/image, report **CoV(cell_m)** + bimodality → convert the global "13%"
into a **per-image trustworthiness flag** (high CoV → that image's plan metrics abstain/cap AMBER),
far more honest than a blanket Tier-B cap. Fixed logged seeds, bootstrap CIs, pre-declared tolerances.

**Top risks:** (R1) **`jpeg_tiles` (processing_load_proxy)** digests libjpeg **byte lengths** →
build-dependent → cross-env false-RED; likely not in L5's 8-class panel — measure it. (R2) 6-decimal
grid ≈ zero cross-env tolerance for large-magnitude floats; real guarantee in un-audited side script.
(R3) `geometry_plan.grid_hash` = exact hash of nondeterministic branch-unstable grid (HoughLinesP
threshold cliff, seeded kmeans basin-switches, morphology thread-sensitivity) → same-machine-only,
silently presented as replayable. (R4) substrate-once plan-identity hole. (R5) **discrete-cliff
fragility: LSD `n_segments`** in orderliness/verticality digests (createLineSegmentDetector is
build-variable), orientation_hist bin `.astype(int)`, `mag>frac*max`, `np.digitize`, Canny — sub-ULP
jitter → digest flips; **m1_prime.py does not pin cv2/BLAS threads** (determinism depends on ambient
env). (R6 minor) `replay()` `tol=0.02` absolute → use `max(0.02, 0.01·|s|)`.

**References:** [1] **Segura et al. (2016), Survey on Metamorphic Testing, *IEEE TSE* 42(9)**,
doi:10.1109/TSE.2016.2532875 — MR taxonomy for A6. [2] **Chen et al. (2018), Metamorphic Testing review,
*ACM CSUR* 51(1)**, doi:10.1145/3143561 — testing programs with no oracle (construct-unvalidated ops).
[3] **Xu et al. (2024), Floating-Point Non-Associativity & reproducibility, arXiv:2408.05148** —
mechanism behind L5 SIMD deltas + R5. [4] **Numerical Nondeterminism in LLM Inference (2025),
arXiv:2506.09501** — batch/reduction-order determinism → thread pinning + env fingerprint. [5]
**Nondeterminism-Aware Optimistic Verification for FP NNs (2025), arXiv:2510.16028** — per-op declared
tolerances = the DIGEST-MATCH vs TOL-MATCH two-tier verdict. [6] **Goldberg (1991), What Every CS
Should Know About Floating-Point, *ACM CSUR* 23(1)**, doi:10.1145/103162.103163. [7] **Claessen &
Hughes (2000), QuickCheck, *ICFP***, doi:10.1145/351240.351266 — property-based jitter generation. [8]
**Fisher (1922), Mathematical Foundations of Theoretical Statistics, *Phil. Trans. R. Soc. A* 222**,
doi:10.1098/rsta.1922.0009 — the sufficiency principle the independent-recompute classes must satisfy
for the faithfulness guarantee to be real.

**Bottom line:** boundary is honest; the biggest gap is the **cross-env story** (same-machine tamper
control mislabeled as cross-machine exact-replay) — formalize a per-field exact/tol schema, pin threads
+ record env fingerprint, split the coverage metric, close the plan-identity hole with a per-consumer
grid_hash tag, and treat the geometry 13% instability as a per-image trustworthiness flag.
