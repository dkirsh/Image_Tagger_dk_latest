# Claude Prompt: Entrance/Foyer Image_Tagger Evidence Bundle

You are Claude working on the evidence-producing side of an architectural
recommendation system.

## Repository

`/Users/davidusa/REPOS/Image_Tagger_dk_latest`

## Goal

Prepare a small, reliable Image_Tagger attribute bundle for an entrance/foyer
recommendation demonstrator. Codex is separately building the recommendation
schema and adapter. Your job is to make the measurements trustworthy and
exportable. Do not build or edit the recommendation engine.

## Read First

1. `docs/VISION_TAGGING_2D_3D_CURRENT_STATE_2026-07-29.md`
2. `docs/IMAGE_TAGGER_SPACE_USE_ATTRIBUTE_MINING_BRIEF_2026-07-29.md`
3. `docs/ACTIVITY_PREDICTION_FRAMEWORK.md`
4. `cnfa_algs/`
5. `annotation_socket/`
6. `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/pipeline.py`
7. The canonical science-run models and services referenced by the first document.

## Boundaries

- Inspect git status before editing.
- Do not touch `model_intake_core/`, its tests, recommendation-system files, or
  unrelated uncommitted work.
- Never use `git add -A`.
- Do not push.
- If committing, stage exact owned files only.
- Use Pacific local time, accurately labelled PDT or PST, in reports.
- Do not claim that an image establishes behavior, comfort, cognition, or
  performance. It may measure visible properties or estimate design support.
- Prefer explicit abstention to an unsupported value.
- Do not enlarge the attribute vocabulary merely to appear comprehensive.

## Task 1: Audit the Existing Paths

Trace the actual execution path for each candidate attribute:

```text
input image
-> implementation
-> model or algorithm
-> dependencies
-> output
-> confidence/evidence
-> checker/gate
-> persisted or exported representation
```

Separate:

A. canonical web science-pipeline attributes;  
B. CNFA annotation-socket attributes;  
C. VLM-derived attributes;  
D. plan/3D-dependent attributes;  
E. proposed but non-operational attributes.

Confirm which CNFA capabilities are integrated into the web application and
which remain parallel research code. Run relevant tests and record exact
commands and outputs. A passing import or fallback test is not proof of model
inference.

## Task 2: Select a Small Entrance/Foyer Bundle

Choose approximately 8-12 attributes that are most useful for comparing
entrance or foyer designs. Consider:

- visibility of the destination or onward route;
- entrance and threshold legibility;
- landmark or orientation-anchor salience;
- enclosure, prospect, and possible waiting refuge;
- bottleneck or circulation obstruction;
- sightline interruption and blind corners;
- waiting-place support and seating relation;
- privacy or exposure of waiting positions;
- glare, dark transition, and luminance variation;
- visual clutter or processing load;
- barrier permeability;
- accessibility cues, only where visually supportable.

For each candidate classify it as:

1. directly measurable from an image;
2. image-derived proxy;
3. requires a plan or 3D model;
4. requires another sensor or declared building data;
5. requires human observation, rating, or experiment.

Do not force every candidate into the image-only bundle. Rank candidates by
decision value, present reliability, and repair cost.

## Task 3: Test, Then Repair

Find a small local test set containing entrance/foyer examples and useful
non-examples. Use existing repository images where possible. Record the exact
fixture paths.

For each selected operational attribute:

- run positive, negative, and difficult examples;
- preserve raw outputs;
- test deterministic replay where applicable;
- test an invalid or unsupported input;
- inspect localization/evidence where the attribute claims a region;
- report false positives, false negatives, unknowns, and abstentions.

Repair only the highest-value failures needed for the small bundle. Add tests
that fail before and pass after the repair. Do not substitute a heuristic for a
missing model without identifying it as a weaker method.

## Task 4: Define the Export Contract

Produce a versioned JSON Schema for the adapter Codex will consume. Each
attribute record should include at least:

- `schema_version`
- `asset_id` and `asset_kind`
- source image/view identifier
- `attribute_id` and `display_name`
- `value` and `units`
- `value_type`
- localization or evidence region
- confidence
- scientific tier
- `evidence_kind`
- method and implementation version
- model or dependency versions
- required inputs
- limitations
- abstention status and reason
- runtime and timestamp

The contract must distinguish:

- observation;
- geometric or visual measurement;
- proxy;
- inference;
- unavailable or abstained result.

Include one real exported example and one abstention example. Validate both
against the schema.

## Task 5: Scientific Evidence Matrix

For each retained attribute, separate two questions:

A. Can Image_Tagger measure or estimate the attribute reliably?  
B. What evidence links that attribute to an architectural outcome?

Use primary scientific sources where possible. Do not convert correlation into
causation. State whether the relationship is established, provisional,
context-dependent, or merely proposed.

Likely architectural concerns include orientation, waiting, crowd movement,
social exposure, privacy, visual comfort, accessibility, and transition from
outside to inside. Mark claims that require plans, occupancy data, acoustics,
environmental sensors, or human testing.

## Deliverables

Create:

1. `docs/ENTRANCE_FOYER_TAGGER_AUDIT_2026-07-30.md`
2. `docs/ENTRANCE_FOYER_ATTRIBUTE_EVIDENCE_MATRIX_2026-07-30.md`
3. `docs/IMAGE_TAGGER_RECOMMENDER_EXPORT_CONTRACT_V1.schema.json`
4. A fixture export that validates against the schema.
5. Focused tests and repairs, where justified.
6. `docs/ENTRANCE_FOYER_TAGGER_RECEIPT_2026-07-30.md`

The receipt must contain:

- start and stop times in Pacific local time;
- files changed;
- exact commands and substantive outputs;
- test counts;
- selected attribute bundle;
- attributes rejected or deferred and why;
- known failures;
- git status;
- commit hash if committed.

## Success Condition

The result is not "many attributes exist." It is:

> Given an entrance or foyer image, Image_Tagger can return a small set of
> traceable measurements and cautious proxies, state what it cannot know, and
> provide a stable evidence-bearing object to the separate recommendation
> engine.

End with a concise handoff for Codex describing the contract location, retained
attributes, confidence boundaries, and unresolved blockers.
