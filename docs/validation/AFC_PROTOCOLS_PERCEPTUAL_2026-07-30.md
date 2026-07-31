# 2AFC judgment protocols — the perceptual/evaluative validation slice

## 2026-07-30 · draft for David to critique and own

*The human-judgment half of the harness. Three attributes, each elicited as adaptive two-alternative
forced choice (2AFC) on the verified `adaptive_preference` engine (v3.5.11 + 11-July attribute layer).
`perceived_clutter` is fully specified and stimulus-ready; `welcoming` and `good_for_meeting` are
specified but gated on a small stimulus-curation pass. All three run in **validation mode (tagger-blind,
flat prior)** so the human scale is independent of the tagger — see the harness design doc §4.2. The
number each produces is the tagger↔human `r` that both promotes the predicate in the ledger and
warm-starts future studies via `attribute_layer.warm_start_state()`.*

---

## Shared method (all three)

- **Instrument.** The neutral 2AFC trial screen (`adaptive_preference/frontend_next/subject_trial_redesign.html`):
  two equal fixed frames, achromatic surround, keyboard input (←/→/Enter). The surround must not bias the
  judgment — this is a measurement requirement, not cosmetic.
- **Sampler.** The verified Bayesian adaptive 2AFC core (`backend/bayesian_adaptive.py`; recovers a known
  ranking at ρ≈0.99). **Flat prior** for validation (do not warm-start from the tagger — that would make
  the validation circular).
- **Two sampling regimes.** A **random-sampled hold-out** set of pairs → the *unbiased* tagger↔human
  correlation. The **adaptive** set → efficiency + it naturally probes the tagger's failure boundary. The
  ledger records which regime produced which number.
- **Latent scale + agreement.** The engine fits a Thurstonian latent utility per stimulus (with 95%
  credible intervals). Validation metrics: **Spearman ρ(tagger score, human latent)** on the hold-out set,
  and **pairwise accuracy** (does the tagger predict the human's 2AFC choice). Report both with CIs.
- **Verdict rule (proposed).** `validated` if the hold-out ρ 95%-CI lower bound ≥ 0.5 *and* pairwise
  accuracy CI lower bound ≥ 0.65; `failing` if the CI includes 0; else `candidate` (needs more data).
  Thresholds are David's to set — these are placeholders that map to "usefully better than chance."
- **Hygiene.** Allow an explicit *"can't tell"* response; counterbalance left/right; attention + reaction-
  time QA (drop implausibly fast trials); record that no machine suggestion was shown (flat prior).
- **VLM dry-run first.** Before any human runs, the VLM stands in as rater over the same stimuli so the
  whole loop (elicit → latent fit → ρ → ledger record) is proven end-to-end and returns a *provisional* ρ.
  The VLM is also kept as a permanent third signal, but it never substitutes for the human ρ.

---

## Protocol 1 — `perceived_clutter`  (READY TO RUN)

**Subject question:** *"Which room looks more cluttered?"*

**Construct (what the rater is judging).** The felt busyness / disorder of the visible scene — how much
visual "stuff" competes for attention. Deliberately *not* "which is messier" (moral/tidiness framing) and
*not* "which is more complex" (which can be orderly). One neutral framing line for raters: *"Cluttered =
lots of competing visual elements, hard to take in at a glance."* No further priming.

**Tagger predicate under test.** `faithful_clutter` — the Rosenholtz feature-congestion / subband-entropy
scalar per image. Its *computation* is already validated (~1e-7 vs pyrtools; ledger entry
`faithful-clutter-computation`). This protocol tests whether that validated number tracks **human
perceived** clutter — the open question the computation validation explicitly does not answer.

**Stimuli (already on disk — no curation needed).** `corpus_L6/` (539 images). Backbone: the **164
designed A/B pairs** (`category=pairs`, `pair_expected_better`) built for exactly the complexity/clutter
contrast — they give (a) strong spanning stimuli and (b) a *designed expected ordering* the VLM dry-run
can score against before any human. Supplement with a spread from the 347 `interiors` to cover the mid-
range. Target ~30–40 stimuli spanning low→high `faithful_clutter` (bin by the tagger score, sample evenly
across bins so the range is covered — coverage, not tagger-agreement, is the sampling goal).

**Why this one first.** Stimuli ready; a designed ground-truth ordering exists for the dry-run; and it
directly closes the most-scrutinized gap in the engine (the clutter stack the panels spent the most time
on). The dry-run will populate the `results_dashboard.html` (ranking + CIs, tagger↔human calibration
scatter, convergence) with real structure — a live example to look at, not a mockup.

**First run (concrete).**
1. Build the stimulus manifest: 30–40 `corpus_L6` images (all pairs + evenly-binned interiors) with their
   `faithful_clutter` scores.
2. Emit the `AttributeSpec` (`key=perceived_clutter`, the question, the `faithful_clutter` link, flat
   prior) via `experimenter_define_attribute.html` / `build_experiment_spec()`.
3. VLM dry-run over the random hold-out → provisional ρ + full dashboard; sanity-check against the 164
   pairs' `pair_expected_better`.
4. Read out: provisional ρ, and the exact human study ready to hand to raters.

---

## Protocol 2 — `welcoming`  (SPECIFIED · needs stimulus curation)

**Subject question:** *"Which entrance feels more welcoming?"*

**Construct.** Affective approach-pull of an entry/threshold — does it invite you in. Affective, not
geometric; no objective ground truth, so human `r` is the only validation.

**Tagger predicate under test.** The tagger's `welcoming` affect attribute (confirm exact key in
`attributes.py`/`hedonics.py` at run time).

**Stimulus gap + fix.** `corpus_L6` is interiors/complexity-centric, not entrances. Curate a license-clean
set via the existing L6 collector — pull **Places365** `entrance_hall` / `lobby` / `reception` and
**MIT-Indoor67** `lobby`; target ~30 spanning the tagger's `welcoming` range. This is a collection pass
(extend the collector's category list), not hand-labeling.

---

## Protocol 3 — `good_for_meeting`  (SPECIFIED · needs stimulus curation)

**Subject question:** *"Which space looks better for a small meeting?"*

**Construct.** Perceived affordance for a small co-present group to meet and share attention. Evaluative
affordance — bridges to the SPACE_USE priority `shared_focal_surface_access`. Keep the judgment about
*suitability as depicted*, not inferred use.

**Tagger predicate under test.** The `good_for_meeting` / meeting-affordance attribute (confirm key at run
time; may compose activity + seating + shared-surface signals).

**Stimulus gap + fix.** Curate via the L6 collector — **Places365** `conference_room` and **MIT-Indoor67**
`meeting_room`; target ~30 spanning the tagger's range. Same cheap collection pass.

---

## What David owns here (the protocol-designer seat)

The judgments themselves come from a VLM (dry-run), then raters/SME/crowd. Your calls are the ones baked
into *what gets asked*: the exact construct framing per attribute (the one-line rater frame above), the
verdict thresholds, the stimulus count/coverage, and whether `welcoming`/`good_for_meeting` are worth the
curation pass now or later. Those are the science decisions; the machinery is ready to execute whichever
way you set them.

*Next build step (not done here): the VLM dry-run runner for `perceived_clutter` over the hold-out set,
emitting the dashboard + a provisional-ρ ledger record. Ready to build on your go.*
