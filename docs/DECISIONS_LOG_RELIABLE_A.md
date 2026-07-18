# DECISIONS LOG — Sprint Reliable-A (2026-07-15)

*Every non-obvious choice made during autonomous execution, with pros/cons and the default taken,
per David's instruction ("store the context and create a discussion of the pros and cons of each
choice, then go on"). Fable will review these and advise; then attack the reviews.*

Risk key: Low = reversible/local · Med = affects several files/needs migration · High = hard to reverse.

---

### D1 — GREEN predicate vs GREEN unit (Tier-A-only pass mode)
- **Context.** V9 (and V2/V13/V1/V6/V7) are GREEN *predicates*, but a mixed image unit verdicts
  AMBER because it also carries AMBER plan-metrics (C1, C29…); unit tier = min over predicates.
- **Alternatives.** (a) Leave it — reliability is a per-predicate property, consumers read the
  predicate tier. (b) Add a Tier-A-only annotation MODE that runs only GREEN image-attrs, so the
  unit itself can verdict GREEN. (c) Change unit-tier rule to report a per-tier breakdown.
- **Chosen: (b) + (c-lite).** Add an opt-in `tier_a_only` mode AND have coverage already report
  per-status counts; the unit in full mode stays AMBER (honest).
- **Pros.** A genuinely GREEN-certifiable reliable layer exists for downstream use (e.g. the
  hedonics register) without waiting on the ≠-mind for plan metrics; non-breaking (opt-in).
- **Cons.** A second code path to maintain; risk of two "truths" (Tier-A-only vs full) if consumers
  aren't told which mode produced a record — mitigated by stamping `mode` in the record.
- **Risk: Low.** Reversible, additive. **Panel concern:** does GREEN-unit-in-Tier-A-mode mislead
  anyone into thinking the plan metrics were validated? (mode stamp must be loud.)

### D2 — V6/V7 clutter vs the legacy tiled processing-load proxy (RETIRE or KEEP?)
- **Context.** Skeptic said: ship the validated Rosenholtz measures (V6 subband entropy, V7 feature
  congestion) and RETIRE the ad-hoc legacy `cnfa.fluency.processing_load_proxy` so hedonics doesn't
  get three correlated clutter numbers (double-count).
- **Alternatives.** (a) Retire the legacy proxy now. (b) Keep all three, flag for a corpus
  calibration that decides retirement on evidence. (c) Keep legacy as a cheap sanity check only,
  excluded from hedonics.
- **Chosen: (b).** Ship V6+V7 as GREEN predicates; add a `clutter_family` note; do NOT delete the
  legacy proxy — mark it "candidate-for-retirement pending corpus agreement."
- **Pros.** Honors RULE 0 (no deletion of a working, possibly-uniquely-consumed measure without
  containment proof + authorization); the retirement becomes an evidence-based decision, not a
  guess; nothing downstream breaks.
- **Cons.** Temporarily three clutter numbers exist; if a consumer naively sums them into hedonics
  now, double-count persists until calibration. **Mitigation:** the score_layout guard already
  excludes non-aggregated fields; document that V6/V7/legacy are one family — pick ONE for hedonics.
- **Risk: Med** (touches hedonics weighting). **Panel concern:** which single clutter measure should
  hedonics use — and is subband-entropy vs feature-congestion redundancy itself a double-count?

### D3 — V2 cycles/degree calibration (the FOV / viewing-distance assumption)
- **Context.** Wilkins discomfort is defined in cycles/degree, but an image only gives
  cycles/pixel; converting needs a field-of-view + viewing-distance assumption.
- **Alternatives.** (a) Assume a fixed FOV (declare it). (b) Estimate FOV from the vanishing-point
  geometry (couples V2 to the AMBER geometry stack → would demote V2 to AMBER). (c) Report the
  slope/residual in cycles/pixel and abstain on the calibrated discomfort number.
- **Chosen: (a) 65° horizontal FOV** (matching `plan.infer_plan_from_image`'s default), EMITTED
  with every score; the raw slope is reported cycles/pixel-independent (scale-free), the
  CSF-weighted discomfort term carries the declared-FOV caveat.
- **Pros.** Keeps V2 GREEN (no coupling to heuristic geometry); the scale-free 1/f slope is the
  robust part and needs no FOV; assumption is transparent and swappable.
- **Cons.** The absolute discomfort magnitude is only as right as the FOV guess; a very wide-angle
  or cropped photo mis-calibrates it. **Mitigation:** emit assumption; downstream can rescale.
- **Risk: Low.** **Panel concern:** is the CSF-weighted term trustworthy at all without true FOV,
  or should only the slope ship until a per-image FOV exists?

### D4 — V1 contour angularity: base GREEN vs full (person/plant-masked) AMBER
- **Context.** Contour curvature conflates architectural contours with object contours (plants,
  fabric, people); the masked variant needs segmentation → AMBER.
- **Chosen.** Ship the **base variant GREEN** (whole-image curve fraction + corner density; pure
  Canny + turning angle, deterministic); note the object-contour confound as a declared failure
  mode; the person-masked variant is deferred (AMBER, later).
- **Pros.** The base measure is deterministic and honestly GREEN; delivers the biggest missing
  valence signal now. **Cons.** A cluttered plant-filled room reads "curvy" from foliage, not
  architecture. **Mitigation:** failure mode declared; eye-level band weighting reduces (not
  removes) it.
- **Citation fix applied (skeptic):** anchor only on curvature-PREFERENCE (Bar & Neta 2006/2007,
  Dazkir & Read 2012, Chuquichambi 2022); the misremembered Vartanian 2013 "approach decisions"
  clause is STRIPPED. **Risk: Low.**

### D5 — Lens-distortion handling for V1/V2 (barrel distortion curves straight lines)
- **Context.** Wide-angle interior photos bow straight architectural lines, inflating curvature
  and shifting spectra.
- **Chosen.** Do NOT auto-undistort (no reliable per-image intrinsics); instead emit a
  `straight-line-bow` caveat computed cheaply (residual of long edges from straight fits) so the
  consumer/≠-mind is warned. **Pros.** No fabricated intrinsics; honest flag. **Cons.** Doesn't
  fix, only warns. **Risk: Low.**

### D6 — Adversarial gate cadence: per-predicate vs per-pair vs end-only
- **Chosen: per-pair** (G1 after V2+V13, G2 after V1+V6/V7, G3 master batch). **Pros.** Batches
  reviews to Fable-sized chunks; keeps momentum; still catches issues before they compound.
  **Cons.** A bad pattern in V2 could propagate to V13 before review. **Mitigation:** the shared
  recipe + mechanical gate catch structural errors immediately; the pair-gate catches construct
  errors. **Risk: Low.**

### D7 — Registry MODEL_VERSION bump
- **Context.** Adding predicates changes the annotation record; replay-verification rejects old
  accepted re-derivations unless MODEL_VERSION bumps.
- **Chosen.** Bump `MODEL_VERSION` once at sprint end (not per predicate) to a single new tag, so
  all sprint predicates land under one content-address epoch. **Pros.** One re-annotation epoch;
  clean. **Cons.** Mid-sprint content addresses are transient (fine — nothing published mid-sprint).
  **Risk: Low.**
