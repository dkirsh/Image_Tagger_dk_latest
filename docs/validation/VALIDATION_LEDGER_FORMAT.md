# Validation Ledger — frozen format (v0)

## 2026-07-30

*The single, append-only record of what has been checked about each tagger predicate, against what,
with what verdict. One immutable entry per **predicate × ground-truth-source × engine-version**. A verdict
is never a bare status string — it carries its evidence. This mirrors the engine's own M1′ discipline,
now applied to the validation itself. Companion design: `HITL_VALIDATION_HARNESS_AND_ADAPTIVE_PREFERENCE_2026-07-30.md`.*

## Record shape

```json
{
  "entry_id": "string — stable id, e.g. los-primitive@ee1f2a98",
  "predicate": "engine function / attribute key",
  "register": "which reading register it serves (configurational, perceptual, ...)",
  "tier": "objective | perceptual",
  "ground_truth": "what the predicate was checked against",
  "engine_version": "commit / MODEL_VERSION hash the predicate was read/run at",
  "elicitation": null,
  "result": { "metric": "...", "value": 0.0, "detail": {} },
  "verdict": "validated | candidate | failing",
  "run": { "where": "cloud-reproduction | native-repo | ...",
           "canonical_cmd": "the in-repo command that reproduces it",
           "created_utc": "ISO-8601 Z" },
  "notes": "honest caveats + what would strengthen the entry"
}
```

Field rules:

- **tier = objective** → `elicitation` is `null`; ground truth is analytic, a reference implementation, or
  measured geometry; `result` is a pass/agreement metric. These need **no human**.
- **tier = perceptual** → `elicitation` is the 2AFC record (mode, engine, n_subjects, n_comparisons,
  sampling), and `result.metric` is the tagger↔human correlation `r` (with CI). Validation mode must be
  **tagger-blind (flat prior)** — see the design doc §4.2. The `r` here is what warm-starts future
  adaptive-preference studies.
- **verdict = validated** requires the evidence to be reproducible from `run.canonical_cmd`.
- **verdict = failing** is a real, useful result — it redirects effort off a measure that does not track
  what we thought.

## Verdict ladder (maps to the QA epistemic types)

`candidate` (computed, unchecked) → `validated` (checked against ground truth / human `r`) → later,
`transferable` (holds across held-out contexts). Confidence never promotes a rung; only evidence does.
