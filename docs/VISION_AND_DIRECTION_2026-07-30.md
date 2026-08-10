# Image Tagger — Reading Space as Cognitive Code

## Updated high-level account · 2026-07-30

*A refreshed, thorough high-level account of the DK image tagger (`Image_Tagger_dk_latest`,
remote `dkirsh/image_tagger`, branch `cnfa-algs-2026-07-14`). It updates the founding account,
`docs/VISION_AND_DIRECTION_2026-07-14.md` ("Reading Space"), which remains the canonical statement
of the vision and the register model. This document does not replace it — it carries the vision
forward and records **what has actually been built since 14 July**, honestly separating what is
operational, what runs in parallel and is not yet integrated, what is foundational, and what is still
a design on paper. Every state claim here is grounded in the repo, the two 29 July current-state
documents, the VIEW-3 composer doc, the 3D model-intake working set, and the git log; assumptions are
flagged. Governing documents are indexed in §8.*

---

## 1. The vision has not moved — only the ground beneath it

The founding claim still holds and is worth restating because everything below serves it. The tagger
exists to read a space as a **place** — a building-in-relation-to-its-occupants — and to make that
reading *computable, searchable, interrogable, and evaluable*. This is the distinction between
**physical code** (what is geometrically there: walls, openings, dimensions) and **cognitive code**
(what the space affords, means, and does to the people in it). A photograph or a model is the physical
code; the tagger's job is to recover as much of the cognitive code as evidence honestly permits, and
to refuse to invent the rest.

The **register model** from §2 of the founding doc is unchanged and remains the organizing lens: any
reading of a space is a move within one or more registers — metric, morphological, luminous, tectonic,
perceptual, affective, affordance, configurational, semantic, evaluative, comparative. Critique is a
*cross-register* act. The strategic commitment is also unchanged: **engine-first**, climbing the ladder
from primitives → perceptual/tectonic features → cognitive constructs, and **validating at every rung**
against both a vision-language model and human judges (the credibility harness). What has changed since
14 July is that large parts of this ladder are now built, tested, and — crucially — instrumented with an
audit discipline that makes their honesty checkable rather than merely asserted.

---

## 2. What we have built since 14 July

### 2.1 The CNFA engine (the biggest single advance)

The founding doc described an engine we intended to build. It now exists as a working body of code in
`cnfa_algs/` with an `annotation_socket/`, running **68 predicates** — roughly 40 image attributes plus
28 plan-derived metrics — spanning the primitive, perceptual/tectonic, and configurational registers.
It is honest by construction rather than by promise:

- **The M1′ audit spine.** Every run is checked against an eight-class audit; any sign of tampering or
  fabricated inputs flips the result to **RED** rather than producing a plausible-looking number. The
  engine can **abstain with evidence** — it is allowed to say "I cannot support this" and show why.
- **Tiered honesty.** Results are graded **GREEN / AMBER / RED**. In the current predicate set the
  large majority are AMBER ("supported, but disclose the assumption / sensitivity") and a smaller set
  are GREEN ("firm"); RED is a live outcome, not a theoretical one. The AMBER tier is not a weakness —
  it is the mechanism by which the engine reports honest uncertainty instead of false confidence.
- **Faithful feature computation.** Where the literature has a defensible operationalization (for
  example a pyramid-based clutter measure adjudicated against `pyrtools` to ~1e-7 agreement), the engine
  computes the faithful version rather than a cheap proxy, and an 11-class complexity partition backs the
  morphological reading.
- **A clean seam to geometry.** The `PlanGrid` abstraction (free / obstructed / unknown cells at a
  declared metre resolution) is the engine's interface to floor-plan and 3D-derived geometry, and CNFA
  criteria already consume it for isovists, visibility, movement, seating, crowding, and view-equity
  analyses.

A representative recent socket run over three images — an office, a corridor, and the Farnsworth House —
produced GREEN/AMBER/RED across the set, **rejected a deliberately fabricated control**, and **replayed
idempotently**. That is the behaviour we wanted: the engine is trustworthy about its own limits.

**Honest caveat (unchanged from the 29 July state doc):** the CNFA engine currently runs *parallel to*
the production web pipeline; it is not yet the canonical science-run inside the app. Integrating it into
the app's `backend/science/pipeline.py` path is named, open work (see §6). The socket test suite passes
33 and fails 4, and the 4 failures are a hard-coded Linux fixture path, not a logic defect.

### 2.2 The application

The operational 2D product is the React/FastAPI app (`Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`),
with the science pipeline in `backend/science/pipeline.py` and run orchestration in
`services/science_runs.py`. This is the mature, working surface: it ingests images, runs the tagging
pipeline, and serves results.

### 2.3 The viewer ladder — VIEW-0 through VIEW-3

Since 14 July we built out a family of viewers, VIEW-0/1/2/3, that turn engine output into something a
person can actually read. VIEW-3 is the one that matters most for your current question and is treated
on its own in §3.

### 2.4 The L6 correctness program and the label supply chain

Two supporting programs matured in parallel and are what make the engine's numbers defensible rather
than merely produced:

- **The L6 correctness program** and repeated panel reviews (including the M1′ expansion from 15 to
  28-of-68 predicates, the CC-1..CC-4 correctness cycles, and a second QA round) — the discipline that
  keeps each rung of the ladder validated as it is added.
- **The DK-1 corpus + labeling supply chain** — corpus collectors, A/B collection, a Google-Drive
  offload path, an S3 labeling console, and the Tanishq handoff and onboarding. This is the human-
  calibration layer the founding doc's §4 called out as a *need*; it now has real infrastructure.

---

## 3. Connecting questions and answers to images — where this actually stands

You flagged this as "one new thing" and were unsure whether we'd done much or only begun planning.
The honest answer: **we did more than begin — one layer shipped, and a second, more ambitious layer is
specified.** They are worth separating.

### 3.1 VIEW-3 — the question-driven composer (BUILT, 2026-07-20)

VIEW-3 (`viz/question_composer.py`) is the operational Q&A→image capability and it is **done**. It takes
a natural-language question about a space, classifies it (`classify_question` → a class such as noise,
clutter, biophilia, wayfinding, privacy, or overview), composes a display specification (`compose()`),
and renders a **self-contained HTML** question-answer view (`render_question_view()`) that foregrounds
exactly the evidence relevant to the question.

Its design is deliberately conservative, and this is the important part: it is **advisory-only** and
built on a strict *"≠-mind" separation*. The language model curates *which layers to show and how to
phrase the surrounding prose* — it does **not** compute or alter scores. Numbers are substituted into
the prose from the engine record by an internal `_fill()` step, and any number that is not verified is
rendered as `[redacted:unverified]` rather than shown. It fails closed. The acceptance test — the
question *"effects of street noise on the foyer"* — passes. So the capability to *ask a question of an
image and get an evidence-bound visual answer* exists today.

### 3.2 The user-tailored QA architecture + question-to-test contract (SPECIFIED, 2026-07-29)

On 29 July a broader framing was written down: `USER_TAILORED_QA_SYSTEM_ARCHITECTURE_2026-07-29.md`.
It generalizes VIEW-3's instinct into a **cross-system invariant**: tailoring to a user *may* change
language, ordering, examples, assistance level, and which actions are offered; it **may not** change
evidence, provenance, gate results, uncertainty, or truth status. It represents a session along five
dimensions (purpose, expertise, authority, current task, assistance policy) rather than baking people
into fixed roles, and it defines a ladder of **epistemic object types** — source fact → effective model
fact → derived measure → proxy/simulation → hypothesis → local human result → transferable claim — where
*promotion between types requires a typed warrant and confidence alone never promotes.*

Its centrepiece for your question is the **Question-to-Test Contract (§6)**: a structure that turns
"connect a question to a space" into a *doable study*, requiring the decision at stake, intended users
and activity, the changeable design alternatives, the source/effective model facts, the derived measure,
the hypothesized consequence, a competing explanation, the cheapest adequate test, the observable
outcome, the result that would *weaken* the hypothesis, and the population/medium limits. The worked
example ("Will first-time visitors find reception?" → occlusion measure → randomized walkthrough of
variants → wrong-turn/route-length outcomes → falsifier) shows the ambition: not just answering a
question about an image, but proposing the experiment that would answer it credibly.

This second layer is **design-stage, not built** — it is a proposed architecture whose *first branch*
is the 3D Model-Intake Workbench (§5). So the accurate one-line status is: **the Q&A→image view is
operational (VIEW-3); the Q&A→testable-study contract is specified and awaiting implementation.**

---

## 4. Reading space *for use* — the activity and space-use thread

The founding doc's thread 3.5 (activity-space fit) was marked *unstarted, needs David's theory*. It has
since acquired a real foundation. Two things now exist:

- **Activity / room-use inference** — a 24-activity vocabulary, an attribute-profile matcher, and a
  structured VLM prompt for inferring what a room is *for*.
- **The SPACE_USE attribute-mining brief** (`IMAGE_TAGGER_SPACE_USE_ATTRIBUTE_MINING_BRIEF_2026-07-29.md`,
  grounded in `SPACE_USE_REPERTOIRE_FOUNDATION_2026-07-29.md`). Its governing chain is disciplined:
  *activity episode → the person-object-space relations that episode requires → the visually recoverable
  evidence for those relations → an attribute → a testable prediction.* It classifies candidate attributes
  four ways (visible primitive / relational affordance proxy / declared-input measure / behavioral
  outcome), lists **21 candidate relational attributes** with the question, evidence, substrate, and limit
  for each, and picks **8 first priorities** (shared-focal-surface access, arrival-orientation support,
  waiting/route conflict, focus-seat interruption exposure, interaction-choice diversity, presentation-
  sightline equity, conversation-cluster clearance, mobility-approach clearance).

Its scientific rules are the point: **do not infer behaviour from affordance**, keep declared inputs
distinct from visible evidence, and never let a proxy pose as an outcome. This thread is grounded in the
environment-behaviour literature (Barker's behaviour settings, Heft's functional affordances, Ng, and
related work). It is a *foundation and a priority list*, not yet a shipped set of predicates — the honest
status is "theory and taxonomy in place; attributes to be implemented and validated."

---

## 5. The 3D thread — model intake before analysis

This is the largest genuinely new direction since 14 July, and its most important lesson is
architectural humility. The goal is to let the same cognitive-code reading apply to 3D models, not just
photographs. The insight that reorganized the work: **a plausible rendering does not prove the system
understood the model.** Scale, axes, spaces, entrances, walkable surfaces, and object meanings can all
be wrong even when the picture looks right. So the first 3D feature is deliberately *not* analysis or
advice — it is an **intake workbench** whose only job is to establish, with a human in the loop, that a
model has been understood well enough to analyse, and to refuse downstream measures until it has.

**Where the code actually is (foundational).** The additive `model_intake_core` package exists and its
21 tests pass; it contains a strict **GLB preflight** (header, chunks, embedded-resource profile,
extensions, reference and limit checks) that deliberately ends at `REVIEW_REQUIRED` — it never pretends
a valid GLB has correct architectural semantics — plus canonical digests, a scene contract, an
attestation validator, and a sprint-ledger enforcer. On the analysis side, the tagger already has the
downstream targets the founding engine needs: `Structured3DAdapter` and `SpatialLMAdapter` both produce
a `PlanGrid` (the Structured3D path validated on one real 260×260 fixture at cell size 0.0498 m), and a
family of depth/segmentation adapters is stubbed or partially working (Depth Anything V2, Depth Pro,
Marigold, SegFormer, ESANet, HAWP, uLayout). The honest caveats from the 29 July state doc stand:
`model_intake_core` is still untracked pending a named committer, SpatialLM has no confirmed run yet,
the Depth Anything V2 adapter fails on dynamic dims, and the asset/dataset footprint is large
(~9.3 GB assets + ~13 GB Structured3D).

**The assurance redesign (the important intellectual move).** A four-lens methodological panel — BIM/asset
assurance, human-AI interaction, safety/control, and building-performance evaluation — reviewed the first
workbench spec and *broke it with adversarial fixtures*: a scene-shape schema alone let through traversal
paths, inverted bounds, a zero quaternion, dangling references, a confirmation belonging to a different
revision, the same person in both confirmer roles, and an accepted blocking error. The correction: a
mutable scene `status` **cannot** be the release authority. Readiness is now an **immutable, analysis-
specific attestation** (`MODEL_READINESS_ATTESTATION_SCHEMA_v0.json`) that digest-binds the raw source,
the effective scene, the package manifest, the assurance profile, the validator receipts and named
negative controls, and — in version 0 — **three distinct people** (technical confirmer, semantic
confirmer, and an independent release checker who is neither). Any change to source, scene, parser,
profile, annotations, or artifacts invalidates the attestation. State is split into four structures
(processing state, job state, a per-gate result vector, and the attestations) rather than one linear FSM.

**Ownership is settled.** `experiment-platform` owns the upload, the workbench UI, workflow state, and
orchestration; **Image_Tagger owns the normalization workers, the scene→PlanGrid / scene→navigation
adapters, and the CNFA analyses and analysis-specific readiness checks**; psych tasks consume an immutable
normalized-scene reference and never parse raw models; Knowledge_Atlas owns evidence/warrant presentation.
The combined architecture is therefore: *GLB → safe preflight → visible geometric + semantic audit →
human correction → immutable normalized-scene package → PlanGrid/navigation adapters → existing CNFA
analyses.* The first integrated milestone is explicitly modest: **one real foyer model** carried
end-to-end (Tanishq resolves technical findings, Stephan labels entrance/destination/waiting zone, both
confirm, the package normalizes, Image_Tagger derives and validates a PlanGrid, one eye-level isovist is
computed, and the exact package revision reopens with the result overlaid) — not generic BIM support.

A binding cross-cutting rule from this thread applies to the whole engine: **a computed spatial measure
is a candidate measure and hypothesis generator, not a validated occupant outcome.** The panel explicitly
reclassified the current CNFA scoring criteria this way. This is the same honesty the M1′ tiers enforce
inside the 2D engine, now stated as program policy for 3D.

---

## 6. Honest current state — one table

| Layer | Status | Note |
|---|---|---|
| Vision + register model | **Firm / unchanged** | Founding doc `VISION_AND_DIRECTION_2026-07-14.md` still canonical |
| 2D web app (React/FastAPI) | **Operational** | `backend/science/pipeline.py`, `services/science_runs.py` |
| CNFA engine (68 predicates, M1′ tiers) | **Built, runs parallel** | Not yet the canonical in-app science-run; socket tests 33 pass / 4 fail (fixture path) |
| VIEW-0/1/2/3 viewers | **Built** | VIEW-3 question composer done 2026-07-20 |
| Q&A → image view (VIEW-3) | **Operational** | Advisory-only, fail-closed, unverified numbers redacted |
| Q&A → testable-study (question-to-test contract) | **Specified, not built** | `USER_TAILORED_QA_SYSTEM_ARCHITECTURE_2026-07-29.md` |
| L6 correctness + panel program | **Active** | Keeps each rung validated |
| DK-1 corpus + S3 labeling | **Operational infrastructure** | Human-calibration layer |
| Activity / room-use inference | **Foundational** | 24-activity vocab + matcher + VLM prompt |
| Space-use relational attributes | **Theory + priority list** | 21 candidates, 8 priorities; not yet implemented predicates |
| 3D `model_intake_core` (GLB preflight, digests, attestation) | **Foundational, 21 tests pass** | Untracked pending named committer; ends at `REVIEW_REQUIRED` |
| Structured3D → PlanGrid | **One real fixture validated** | 260×260, cell 0.0498 m |
| SpatialLM / depth / segmentation adapters | **Stubbed / partial** | SpatialLM no confirmed run; Depth Anything V2 fails on dynamic dims |
| 3D intake workbench (UI + orchestration) | **Specified, assurance-redesigned** | Owned by experiment-platform; foyer last-mile is the first target |

## 6b. The consolidated next-work list

Folding the 29 July 2D/3D state doc and the model-intake sprint system together, the near-term work is:
commit the `model_intake_core` package under a named Image_Tagger committer; pin the official Khronos
glTF Validator and add hostile fixtures; get real GLBs (the six-model fixture set from Tanishq/Stephan);
build and test `scene_to_plangrid` against a normalized scene; add multi-view rendering and conservative
aggregation so 3D feeds the 2D taggers; repair the Depth Anything V2 adapter; define the first narrow
assurance profile (`single_level_isovist_v0`); **integrate the CNFA engine into the canonical in-app
science-run**; run the foyer last-mile test; and — the standing requirement over all of it — **validate
the measures against people** before any of them is spoken of as an occupant outcome.

---

## 7. What has *not* changed, and why it matters

The six missing capacities the founding doc named in §5 — morphological reading, metric-scale geometry,
comparative embedding, calibrated evaluative composites, configuration-from-limited-input, and interactive
latent control — are the honest gap list still. We have made real progress on morphological reading (the
complexity partition and faithful clutter) and on metric-scale geometry (PlanGrid + the 3D intake path),
and the calibrated-composite question is exactly what the "candidate measure, not occupant outcome" policy
is holding the line on. Comparative embedding and interactive latent control remain largely ahead of us.
Naming this plainly is itself the deliverable David asked the founding doc to enforce: the tagger's value
is that it tells the truth about what it can and cannot yet read.

---

## 8. Map of the governing documents

For any session picking this up, the canonical reading order is:

1. `docs/VISION_AND_DIRECTION_2026-07-14.md` — the founding vision + register model (still canonical).
2. **This document** — the 2026-07-30 high-level update (what's built since, honest state).
3. `docs/VISION_TAGGING_2D_3D_CURRENT_STATE_2026-07-29.md` — the granular, code-level current state.
4. `docs/VIEW3_QUESTION_COMPOSER_2026-07-20.md` — the shipped Q&A→image composer.
5. `docs/IMAGE_TAGGER_SPACE_USE_ATTRIBUTE_MINING_BRIEF_2026-07-29.md` — the space-use attribute program.
6. The 3D model-intake working set (currently in `/Users/davidusa/Documents/New project/`, and slated to
   move into a versioned repo location): `MODEL_INTAKE_WORKBENCH_SPEC_2026-07-29.md`,
   `MODEL_INTAKE_SPRINT_SYSTEM_2026-07-29.md`, `MODEL_INTAKE_PANEL_REVIEW_2026-07-29.md`,
   `USER_TAILORED_QA_SYSTEM_ARCHITECTURE_2026-07-29.md`, and the `*_SCHEMA_v0.json` contracts.
7. `TASKS.md` — the live sprint queue (authoritative; this account points to it, never duplicates it).

*A note on provenance: the 3D model-intake working set (item 6) currently lives outside the tagger repo,
under `Documents/New project/`. A recommended housekeeping step is to move that set into
`Image_Tagger_dk_latest/docs/` (or a `model_intake/` folder) so the whole account lives in one versioned
home — but that is a move for David to authorize, not something done implicitly.*

---

*Prepared 2026-07-30. State claims verified against the founding doc, the two 29 July current-state
documents, the VIEW-3 composer doc, the model-intake working set (spec, sprint system, panel review, and
QA architecture), and the git log since 14 July. This is a new dated account; it does not overwrite the
founding document (RULE 0). Committing it into the repo is a one-committer action for the tagger's owner
lane — see the delivery note.*
