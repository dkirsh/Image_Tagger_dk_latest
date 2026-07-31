# Complexity & clutter: measurement + testing revision spec

**2026-07-30 · implementation spec.** Turns the theory (complexity is operation-indexed, model-relative,
time-extended; a fast affective channel and a slow cognitive channel that dissociate) into concrete changes
to (A) how the image tagger *measures* complexity/clutter and (B) how the adaptive-preference engine *tests*
it on users. Written to be lane-aware: **cowork** (Claude), **codex**, **ccode** (experiment-platform).
Cross-lane work is delivered as findings, not edits. A Codex context note is expected; §0 is the seam to
reconcile against it.

## 0. Coordination seam (reconcile with Codex's note)

Proposed split, to confirm once Codex's context note arrives:

- **codex** — engine-code integration inside `cnfa_algs/` (new measures, the output contract, ledger
  wiring). One committer for the tagger.
- **cowork** — the spec, the new-measure algorithms (as reference implementations + tests), the user-study
  design and analysis, and the adaptive-preference wiring delivered as findings to **ccode**.
- **ccode** — the `experiment-platform` / `adaptive_preference` changes (per-facet prior, ratings, framing),
  received as findings.

Reference implementations here are numpy/cv2, self-contained, so codex can port or wrap them without taking
a dependency on cowork code.

**Canonical names + polarity (resolves Codex's 2026-07-30 flag).** The species/measure is
**`arrangement_disorder`**, polarity **higher = more disordered** (regimented → low, scattered → high). This
is canonical across all contracts — the measurement spec (this doc), the HITL species contract, the teaching
sets, and `measures2_reference.py` — superseding the earlier `arrangement_order` (which had inverted
polarity). Rule going forward: every species is named for the *load* and higher = more of it
(`surface_density`, `variety`, `textural_discomfort`, `semantic_incongruity`, `arrangement_disorder`).

---

# Part A — How the tagger measures complexity/clutter

## A1. The core change: emit a tagged vector, never a scalar

Replace the single clutter/complexity score with a small vector. Each facet carries tags so a consumer
knows what the number is *for* and how far to trust it:

```json
{
  "facet": "surface_density",
  "value": 0.0,                 // normalised 0–1
  "operation": "visual_search", // the downstream cost it proxies
  "stage": "early",             // early (image-computable) | late (model-relative)
  "channel": "cognitive",       // cognitive-effort | affective-stress | both
  "image_computable": true,
  "confidence": 0.0,
  "observer_dependence": "low"  // low | medium | high  — how much the human judgment will diverge
}
```

The scalar "clutter" is retired; anything that needs one picks the facet whose *operation* matches its use.

## A2. The facet set (v1 of the tagged vector)

| facet | what it is | operation | stage | channel | image-only? |
|---|---|---|---|---|---|
| `surface_density` | fine-scale feature congestion (small elements per area) | visual search / crowding | early | cognitive+affective | yes |
| `arrangement_disorder` | coarse-scale (dis)order of large elements | legibility / wayfinding | early–mid | cognitive | yes (**new**) |
| `variety` | heterogeneity of colour/material/edges | encoding / interest | early | cognitive | yes |
| `spectral_discomfort` | departure from natural 1/f statistics | comfort / stress | early | **affective** | yes (**new**) |
| `semantic_incongruity` | objects out of place (scene-grammar violation) | comprehension | late | cognitive | no (VLM) |
| `legibility_to_observer` | model-relative order (expertise/activity) | task fit | late | both | no (observer) |

The first four are the tagger's real territory (early, image-computable). The last two are declared but
delegated — the tagger reports that they are late/observer-dependent and does not fake a pixel score.

## A3. New measures to implement (reference algorithms)

**`arrangement_disorder` (coarse-scale compressibility).** The order/disorder axis the current engine lacks.
Compute at a *coarse* scale so it reflects big-element layout, not fine texture: downsample to ~64×64, then
take a compressibility ratio = (size of coarse map compressed) / (size of a same-histogram random permutation
compressed). **Polarity: higher = more disordered** — regimented layouts → low, scattered → high — matching
every other species (more = more of that load). Reference: the order-vs-disorder figure (same 36 squares,
grid 1.4 KB vs scattered 5.2 KB, 3.6×). **Known limitation (found in teaching-set assembly):** this
compressibility proxy conflates natural texture with layout disorder, so it is a **placeholder**; the
production measure should segment large elements and score their placement regularity. Reference
implementation: `teaching_sets/measures2_reference.py::arrangement_disorder`.

**`spectral_discomfort` (1/f departure).** The affective-stress proxy. Compute the radially-averaged power
spectrum; fit slope on log–log; `spectral_discomfort` = excess energy in the mid-high spatial-frequency band
relative to a natural-image 1/f reference (larger departure → more discomfort). This is the measure the
experiment predicts is a *good stress predictor* even though it is a poor general complexity measure.

**Two-scale `surface_density`.** Do not collapse the pyramid: report feature congestion at a coarse and a
fine band separately (`surface_density.coarse`, `.fine`) so arrangement and surface clutter are separable.

All three are numpy/cv2, testable against fixtures, and slot beside the existing `faithful_clutter`.

## A4. Null-model + residual discipline

The tagger is explicitly an **early, image-only null model**. Two rules:

1. It emits its estimate **plus** an `observer_dependence` flag by scene type (high for scenes whose order is
   knowledge-encoded, e.g., specialised workspaces; low for generic scenes).
2. The **residual** between the tagger and human judgment is reported as a *measurement of the late/observer
   component*, not hidden as error. This fits the M1′ honesty discipline already in the engine (report tier +
   evidence; abstain rather than fabricate).

## A5. Operation routing

Expose the facets by use so callers stop asking for "clutter":
- findability / search UI → `surface_density`;
- designed-artifact richness → compression/`variety`;
- **stress / restoration (CNfA wellbeing)** → `spectral_discomfort` (+ `surface_density`);
- legibility / wayfinding → `arrangement_disorder` (+ the late `legibility_to_observer`, delegated).

## A6. Ledger

`perceived_clutter` becomes a **vector of ledger entries**, one per facet, each validated separately (a ρ
per facet, per the harness). The image-only facets are validated against the matching operation; the late
facets are marked "behavioural / not image-validatable."

---

# Part B — How we test it in the adaptive-preference engine on users

## B1. Elicit the vector, plus affect and timing

Run the 2AFC facet study (v2 already built: holistic + D1–D4). Add, per trial or per block:
- a **comfort/stress rating** (so we can validate `spectral_discomfort` against felt stress — the P7 test);
- **recognition RT** (already captured) as the cheap dynamics proxy.

## B2. Stimulus design (span and orthogonalise)

Select stimuli with the SAVOIAS-style battery so **order and density are decorrelated** (high-density/
low-disorder, low-density/high-disorder, etc.), and include two special sets:
- **intact vs phase-scrambled** pairs (gestalt-available vs not) — the resolvable/baked-in contrast;
- **repeat-exposure** trials (same image seen twice) — does discomfort drop once recognised (a behavioural
  read on the refund, no physiology needed).

## B3. Observer manipulation (expose the model-relative component)

Add an **activity/expertise frame**: rate identical scenes "as a chef about to cook service" vs "as a
visitor", and stratify raters by expertise. Prediction: order/clutter judgments *reverse* with the frame for
practitioners — the projection thesis, tested on users.

## B4. Per-facet, per-population trust weight

The adaptive sampler warm-starts from the tagger with weight `r`. Change `r` from one number to a
**per-facet, per-population** value: high for facets/channels the tagger models (`spectral_discomfort`,
`surface_density`), low for the late facets, and re-estimated per activity-frame/expertise stratum. Keep the
**circularity rule**: validation runs tagger-blind (flat prior) to get the honest `r`; tagger-as-prior is
production-only, after `r` is measured.

## B5. Validation targets (what each facet is checked against)

- `spectral_discomfort` → the **comfort/stress rating** (the headline: does an image measure predict felt
  stress?).
- `surface_density` → holistic clutter / search-style judgment.
- `arrangement_disorder` → the "disorganised?" facet.
- `variety` → the "variety?" facet.
- late facets → behavioural signatures (RT, frame-reversal), not the tagger.

## B6. Analysis

Fit latent scales per facet (the verified Bayesian 2AFC core); estimate the **effective dimensionality** by
cross-validation (how many facets people actually use); regress the tagger facets onto the human facets and
onto the stress rating; test the **refund proxy** (repeat-exposure and intact-vs-scrambled) and the
**frame-reversal**. Outputs: the dimensionality result, the per-facet ρ (the ledger vector), the per-frame
`r`, and the tagger↔stress validity.

---

# Part C — Sequenced build

1. **cowork**: reference implementations + tests for `arrangement_disorder`, `spectral_discomfort`, two-scale
   `surface_density` (numpy/cv2); validate on SAVOIAS + fixtures.
2. **codex**: integrate the three measures + the tagged-vector output contract into `cnfa_algs/`; emit the
   per-facet ledger.
3. **cowork**: VLM dry-run of the v2 vector study → provisional per-facet ρ + a populated dashboard.
4. **cowork → ccode**: findings for the adaptive-preference changes (per-facet/per-population `r`, comfort
   rating, activity-frame, intact/scrambled, repeat-exposure).
5. **run**: the human study (Stephan + RA, then crowd) once the dry-run and stimuli are ready.

Dependencies: 1→2 (codex needs the reference algs); 1→3 (dry-run needs the measures to correlate against);
2 unblocks the in-app science-run integration (separate backlog item).

---

*This spec is the seam between the theory paper and the code. It stands alone; when Codex's context note
arrives we reconcile §0 and lock the lane split. Tracked in `OPEN_TASKS.md`.*
