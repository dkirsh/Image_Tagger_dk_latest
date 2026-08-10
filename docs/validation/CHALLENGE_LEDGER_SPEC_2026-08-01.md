# Challenge Ledger — record spec

*2026-08-01, cowork. The first-class artifact from §3.7 of `PROGRAM_STATE_AND_DIRECTION`: where a divergence
between a **CNFA prediction** and a **POE/HITL observation** is registered as data and never silently absorbed
by the entrenched engine. Lives at `docs/validation/CHALLENGE_LEDGER_SPEC_2026-08-01.md`. Append-only,
versioned, content-addressed — same discipline as the Phase-1 artifact contract.*

## What it is (and is not)
A challenge is an **observational claim that a prediction and an observation diverged**. It is **not** an
experimental refutation and it **never auto-revises** the engine. Its job is to (1) make contradictions
visible, (2) accumulate them, and (3) **route** scarce controlled testing to where the web of belief is under
the most strain. The failure mode it exists to prevent: the entrenched engine explaining away its own
anomalies.

## The two registers a challenge must know
- `applied` — normal-business: the engine's measure is presupposed and used for recommendations. Observations
  here (a POE, a HITL study) can *flag* a challenge but cannot, on their own, revise the belief.
- `instrument_conformance` — declared, out-of-band: a deliberate test of one named instrument against a human
  sample. Only findings tagged this register are licensed to *warrant belief revision*, and only with a stated
  method. A challenge moves from `applied` accumulation → an `instrument_conformance` test when it concentrates
  (below).

## Record schema (one JSON object per challenge; stored `challenge_ledger.jsonl`)
```json
{
  "challenge_id": "chg_<sha256-short>",
  "created": "<ISO-8601, stamped outside the workflow>",
  "source": "poe_run | hitl_study | masking_diagnostic | field_report",
  "register": "applied | instrument_conformance",
  "space": { "space_id": "...", "context": "e.g. midday/occupied/ZHA-foyer-A", "medium": "image|3D|in_situ" },
  "construct": { "predicate_id": "C23_social_connectedness", "name": "...", "register_of_measure": "WB|SHARED|cognitive" },

  "prediction": {
    "value": 0.72, "tier": "AMBER", "model_version": "L6-...",
    "provenance": "M1' digest / evidence bbox / derivation chain",
    "entrenchment": "firm | framework | contested",   // how load-bearing the challenged belief is
    "science_basis": "e.g. speech-intelligibility literature (STI→comprehension)"
  },

  "observation": {
    "kind": "single_stimulus_rating | pairwise_preference | behavioral | biosignal | survey",
    "value": "human scale value / preference outcome / measured DV",
    "method": "VAS | 2AFC(Bradley-Terry) | HRV | ESM | ...",
    "n": 24, "provenance": "study_id / instrument / labeling_console_export",
    "design": "observational_fixed_IV_measured_DV"   // POE is not a manipulation
  },

  "divergence": {
    "magnitude": 0.41, "direction": "observation_below_prediction | ordering_reversed",
    "tolerance": 0.15, "exceeded": true,
    "kind": "level | ordering | direction"   // a reversed A>B preference is 'ordering'
  },

  "status": "open | accumulating | concentrated | under_conformance_test | resolved | retired",
  "resolution": null,   // when resolved: "belief_revised" | "measurement_error" | "context_moderator" | "upheld"
  "routing": { "concentration_count": 1, "triggers_conformance_test": false },
  "links": {
    "phase1_hypothesis": "hypotheses_corpusL6.jsonl#<image,species>",   // the prediction row
    "study": "hitl_study_id",
    "ontology_edge": null   // when TX-3 stabilizes: the is-realized-by / causes edge this strains
  },
  "notes": ""
}
```

## Lifecycle (state machine)
1. `open` → a single divergence logged (any source, `applied` register).
2. `accumulating` → more challenges land on the **same construct/context**; `routing.concentration_count` rises.
3. `concentrated` → count (or weighted count, weighted by entrenchment × magnitude) crosses a threshold →
   `routing.triggers_conformance_test = true`.
4. `under_conformance_test` → an out-of-band `instrument_conformance` study is run on that one instrument.
5. `resolved` → one of: `belief_revised` (the science-as-applied was wrong *here*), `measurement_error` (our
   instrument, not the belief), `context_moderator` (both right; a moderator the entrenched claim omitted),
   `upheld` (the challenge did not survive the test). `retired` → superseded / duplicate.

## Rules
- **Entrenchment-aware routing.** Revise the periphery first. A concentration on a *strongly-entrenched* node is
  the expensive-test trigger, precisely because moving it costs the most elsewhere in the web.
- **Ordering divergences are first-class.** A human preference reversal (A>B where the engine predicted B>A) is
  a `kind:"ordering"` challenge — this is how adaptive-preference HITL feeds the ledger (see the HITL note).
- **Masking diagnostics are challenges.** "Space reports well while physiology loads" is logged here, not
  buried in a run report.
- **No auto-revision.** Nothing in the `applied` register changes a belief; only a completed
  `instrument_conformance` resolution can, and only with its method recorded.
- **Content-addressed + append-only.** `challenge_id` = sha256 over (predicate, space, prediction, observation);
  never edit in place — a change is a new record that supersedes (link + `retired`).

## Where it plugs in
- **Prediction side:** the Phase-1 `hypotheses_corpusL6.jsonl` rows (the engine's per-construct predictions).
- **Observation side:** the review-pack viewer exports and the HITL studies (single-stimulus, pairwise,
  biosignal) — see `HITL_STUDY_DESIGN_NOTE_2026-08-01.md`.
- **Belief side (later):** when the construct taxonomy stabilizes (TX-3), `links.ontology_edge` resolves a
  challenge to the exact `is-realized-by` / `causes` edge it strains.
- **Governance:** it is a versioned science artifact under the socket, not a premature DB table.
