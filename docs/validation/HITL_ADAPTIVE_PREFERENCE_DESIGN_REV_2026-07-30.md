# HITL adaptive-preference design — revised to the species model

**2026-07-30 · revises the testing half of `COMPLEXITY_MEASUREMENT_AND_TESTING_SPEC` and supersedes the
single-question 2AFC study.** Written to Codex's context note (2026-07-30 18:40 PDT). Core change:
complexity and clutter are not scalars but **families of species** with different visible causes, meanings,
and consequences, so the method identifies *which species* is present before it estimates *degree*. The
result is a hierarchical, multi-label model. Lanes: **cowork** (design, algorithms, analysis), **codex**
(tagger integration), **ccode** (`adaptive_preference`/platform, via findings).

## 0. How this answers Codex's eight requirements

| # | Codex requirement | Where addressed |
|---|---|---|
| 1 | Teach one species at a time (low/intermediate/high/ambiguous) | §3 Teaching sequence |
| 2 | Test species discrimination before degree | §3 gate + §4 Phase B |
| 3 | Record species-present / applicability-or-cannot-tell / confidence / within-species severity | §5 Data schema |
| 4 | Adaptive selection primarily *within* a species | §6.1 |
| 5 | Cross-species cases test discrimination, not ranking | §4 Phase D, §6.1 |
| 6 | Select corpus images near boundaries, underrepresented regions, model–human disagreements | §6.2 |
| 7 | Repeated anchors + independent raters for reliability & drift | §6.3, §7 |
| 8 | Tagger outputs are hypotheses, never answer keys; human objection can correct examples/labels/task | §8 Objection loop |

## 1. The hierarchy

Two umbrella constructs (**visual complexity**, **clutter**) resolve into **species**. A species is a
distinguishable kind with its own visible cause, its own meaning, its own consequence, and its own
image-side *hypothesis* (a tagger measure that may or may not track it). Judgment is two-level: **presence**
(is this species here, multi-label) then **degree** (how severe, within species). Species are never ranked
against each other.

## 2. Species taxonomy (v1 — revisable by objection, §8)

| species | visible cause | meaning / consequence | image-side hypothesis (tagger) | example anchors (from our corpus) |
|---|---|---|---|---|
| **surface_density** | many small items on surfaces | busy; search cost | fine-scale feature congestion | low: elevator · high: restaurant kitchen |
| **arrangement_disorder** | large elements placed/oriented irregularly | illegible layout | coarse-scale `arrangement_order` | low: conference room · high: chairs askew |
| **variety** | many kinds of objects/colours/materials | rich or overloaded | subband entropy / colour count | low: monochrome corridor · high: bazaar |
| **textural_discomfort** | dense high-freq texture / 1/f departure | visual discomfort, stress | `spectral_discomfort` | low: matte wall · high: fine stripes/glare |
| **semantic_incongruity** | objects out of place | confusion, "wrong" | scene-grammar (VLM, late) | low: normal office · high: bed in a kitchen |
| **concealed_order** | looks disordered but has hidden structure | model-relative; the desk case | *none — observer-dependent* | ambiguous by design (expert vs novice) |

For each species the teaching set provides **low / intermediate / high / ambiguous** exemplars; the
ambiguous ones are the edge cases used to test discrimination, not degree.

## 3. Teaching sequence (per species, before any judging)

Run one species at a time:

1. **Definition** — a plain sentence naming the visible cause and what it is *not* (contrast with the
   nearest neighbouring species, e.g., surface_density vs arrangement_disorder).
2. **Graded exemplars** — low, intermediate, high, plus 2–3 **ambiguous** cases with the reason they are
   ambiguous.
3. **Discrimination pre-test (the gate)** — a short block: "Is *this* species present? — yes / no / cannot
   tell," mixing this species with distractors from other species. The rater proceeds to degree judgments
   for this species **only if** discrimination accuracy clears a threshold (pre-registered, e.g. ≥ 80% on
   unambiguous items). A rater who cannot distinguish the species does not rate its degree — and a species
   that *most* raters cannot distinguish is flagged for redefinition (§8).

## 4. Task flow (hierarchical, multi-label)

- **Phase A — Teach + gate** (per species; §3).
- **Phase B — Identify (multi-label presence).** For each image: for each taught species, record *present /
  absent / cannot-tell*, an *applicability* flag (some species don't apply to some scene types), and
  *confidence*. This is the "first identify the relevant species" step. No ranking here.
- **Phase C — Degree (within species).** For each species marked present across the set, place images on a
  **within-species severity scale** using adaptive 2AFC ("which shows more *surface density*?") among images
  that both carry that species. Latent severity per (image, species), with credible intervals.
- **Phase D — Cross-species discrimination probes.** Interleave pairs that differ in species and ask a
  *discrimination* question ("do these differ in kind, and which species dominates each?") — scored for
  accuracy against the taxonomy, **never** used to build a cross-species ranking. This tests whether the
  species boundaries are real to raters (the incommensurability check).

## 5. Data schema

```json
// identification (Phase B) — one row per (image, species, rater)
{ "type":"identify", "image_id":"", "species":"surface_density",
  "present":"yes|no|cannot_tell", "applicable":true, "confidence":0.0,
  "rater_id":"", "activity_frame":"neutral|chef|...", "ts":"", 
  "tagger_hypothesis":{"present":true,"value":0.0,"confidence":0.0}, "agree_with_tagger":true }

// degree (Phase C) — within-species adaptive comparison
{ "type":"compare", "species":"surface_density", "image_a":"", "image_b":"",
  "choice":"a|b|cant_tell", "rt_ms":0, "rater_id":"", "ts":"" }

// cross-species discrimination (Phase D)
{ "type":"discriminate", "image_a":"", "image_b":"", "species_a":"", "species_b":"",
  "response":"same_kind|different_kind", "dominant_a":"", "dominant_b":"", "correct":true, "rater_id":"" }

// anchor (reliability/drift) — flag on any image reused on a schedule
{ "type":"anchor", "image_id":"", "species":"", "repeat_index":2, "rater_id":"", "session_time_s":0 }

// objection (task-logic correction; §8)
{ "type":"objection", "target":"example|label|species_def|missing_species|task_logic",
  "image_id":"", "species":"", "note":"", "rater_id":"", "ts":"" }
```

Derived per (image, species): presence probability, severity (latent, with CI), applicability rate,
confidence. Derived per rater: discrimination accuracy per species, drift, self-consistency on anchors.

## 6. Selection policy

### 6.1 Adaptive comparisons (within-species first)
Severity comparisons are chosen by **information gain within a single species** — the verified Bayesian
adaptive 2AFC sampler, run per species. Cross-species pairs are drawn only for Phase-D discrimination, at a
controlled rate, and never enter a severity scale.

### 6.2 Corpus/image acquisition (active learning)
New images are pulled toward the places that most improve precision and coverage:
- **near classification boundaries** — where the tagger's per-species hypothesis is uncertain (probability
  near threshold);
- **underrepresented regions** — thin areas of the feature space / scene-type space (coverage);
- **model–human disagreements** — images where the human presence/severity contradicts the tagger
  hypothesis (the residual is the signal).
A scheduler blends the three (e.g., ε-greedy over boundary / coverage / disagreement), logged so no region
is silently starved.

### 6.3 Anchors & raters
A fixed **anchor set** (spanning each species' range, incl. ambiguous items) is re-shown on a schedule
within and across sessions → within-rater test–retest and drift. Every item is seen by **multiple
independent raters** → inter-rater reliability per species. Anchors are excluded from adaptive selection so
their statistics stay comparable.

## 7. Validation plan

- **Discrimination validity** — per species: rater accuracy on unambiguous items, inter-rater agreement on
  *presence* (κ). A species with poor discrimination is not measurable and is flagged (§8).
- **Severity reliability** — within species: inter-rater agreement and anchor test–retest on the latent
  scale; report credible intervals.
- **Drift** — anchor responses over session time; flag raters/timepoints that move.
- **Dimensionality / separability** — do species behave independently? Inter-species correlation of presence
  and severity; a species that never appears without another collapses into it (confirms multi-label vs a
  hidden scalar — the paper's claim, tested operationally).
- **Per-species tagger validity** — tagger-blind ρ(tagger hypothesis, human severity) per species; the
  headline test that `textural_discomfort`/`spectral_discomfort` predicts felt discomfort while general
  measures do not.
- **Coverage & precision gains** — feature-space regions filled over time; classifier precision improvement
  from boundary sampling.
- **Task-logic health** — objection rates by type; each triggers a taxonomy/example/label review.

## 8. Tagger-as-hypothesis and the objection loop (Codex #8)

The tagger seeds hypotheses only: which species are likely present, provisional severity, and *which images
to show next*. It is never the answer key. Raters can lodge an **objection** that flows upstream and can
change the task itself:
- **example** — "this teaching exemplar is mislabelled" → move/relabel the anchor;
- **label** — "the tagger says present, it is not" → correct the instance (feeds the disagreement set §6.2);
- **species definition** — "these two species are one," or "this definition is wrong" → revise §2;
- **missing species** — "there is a kind you are not asking about" → add a candidate species;
- **task logic** — "asking degree here is meaningless" → change the flow.
Objections are data, reviewed on a cadence; a recurring objection revises the taxonomy, the teaching set, or
the task before more ratings are collected. This makes the humans able to correct the model *and the
question*, not just the labels.

## 9. What changes vs the earlier study, and build order

The single-question 2AFC instrument (v2) is **superseded**: it asked degree without teaching, without a
presence phase, and without discrimination gates. The revised instrument needs: teaching screens per
species, the discrimination gate, the multi-label identification phase, within-species adaptive degree, and
the Phase-D probes.

Build order (lanes):
1. **cowork** — finalise the species taxonomy + assemble teaching sets (low/intermediate/high/ambiguous per
   species) from the corpus + SAVOIAS; write the reference severity/agreement analysis.
2. **cowork** — rebuild the web instrument to the §4 flow; VLM dry-run to exercise identify→degree end to end.
3. **codex** — expose per-species tagger *hypotheses* (presence + provisional severity + uncertainty) as the
   selection signal; wire the disagreement/boundary/coverage queues.
4. **ccode** (via findings) — `adaptive_preference`: per-species within-species sampler, per-population
   trust, the identification/objection records.
5. **run** — Stephan + RA on 2–3 species first (surface_density, arrangement_disorder, textural_discomfort),
   then widen.

## 10. Coordination (reconciled with Codex's note)

Confirmed split: **codex owns tagger-side integration** (per-species hypotheses, selection queues, output
contract) and is the tagger's one committer; **cowork owns** the taxonomy, teaching sets, instrument,
analysis, and the reference measure algorithms (`arrangement_order`, `spectral_discomfort`, two-scale
density), delivered so codex can port them; **adaptive_preference/platform changes go to ccode as findings.**
Open question for Codex: where the per-species hypothesis + selection queues should live (tagger service vs
platform), and the exact hand-off format for the disagreement/boundary sets.
