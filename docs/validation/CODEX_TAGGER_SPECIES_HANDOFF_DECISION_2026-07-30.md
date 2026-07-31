# Complexity-species tagger integration decision

**Status:** implemented as an additive v1 sidecar
**Prompt start:** 2026-07-30 23:26 PDT (America/Los_Angeles)
**Prompt stop:** 2026-07-30 23:40 PDT (America/Los_Angeles)
**Naming reconciliation:** 2026-07-30 23:41 PDT (America/Los_Angeles)
**Owner:** Codex, the sole committer for tagger-side integration

## Decision

The tagger owns:

1. immutable, versioned per-image species hypotheses;
2. deterministic candidate-queue manifests derived from those hypotheses and imported human
   identification rows;
3. the validation rules that prevent late or observer-dependent species from receiving fabricated
   pixel scores.

The experiment platform owns mutable study state: assignment, scheduling, rater responses, locks,
completion state, and the adaptive policy that mixes candidate queues. The platform must not become
the canonical store for tagger inference.

The initial handoff is file-first rather than an endpoint. This makes a study replayable, hashable,
portable between repositories, and independent of service availability. A later read-only endpoint
may expose precisely the same records; it must not introduce a second schema.

## Public vocabulary

The canonical species is `arrangement_disorder`; `arrangement_order` is retired and must not appear in
public contracts. Its polarity is higher = more disordered: regimented layouts score low and scattered
layouts score high. This follows the standing rule that every species is named for the load and higher
means more of that load.

The public v1 species are:

- `surface_density`
- `arrangement_disorder`
- `variety`
- `textural_discomfort`
- `semantic_incongruity`
- `concealed_order`

The last two are declared but delegated. They return no presence or severity number because they
require a VLM, an observer, an activity frame, or expertise.

## Handoff

The command is:

```bash
python3 scripts/build_complexity_species_handoff.py \
  --corpus-root /absolute/path/to/corpus \
  --out /absolute/path/to/new/handoff \
  [--identify-jsonl /absolute/path/to/identify_rows.jsonl]
```

It writes:

| File | Purpose |
|---|---|
| `hypotheses.jsonl` | one complete six-species vector per image |
| `boundary.jsonl` | image/species candidates near the provisional presence boundary |
| `coverage.jsonl` | candidates in sparse within-species severity bins |
| `disagreement.jsonl` | candidates where aggregated human presence differs from the tagger |
| `manifest.json` | schema/model versions, row counts, and SHA-256 for every JSONL |

No absolute image path is emitted. `source_ref` is corpus-relative and `image_id` is the full image
SHA-256 in the CLI.

Schemas:

- hypotheses: `cnfa.complexity-species-hypotheses/v1`
- queues: `cnfa.complexity-selection-queues/v1`
- manifest: `cnfa.complexity-species-handoff/v1`

The platform's §5 `identify.tagger_hypothesis` projection is mechanical:

```json
{
  "present": "presence_probability >= the preregistered threshold",
  "value": "provisional_severity",
  "confidence": "confidence"
}
```

The platform should also retain the handoff manifest hash and tagger model version. The study's
human answer remains separate and supplies `agree_with_tagger`; the hypothesis is never scored as
ground truth.

## Measures and honesty

All four image-computable values are labelled
`calibration: engineering_proxy_uncalibrated`. A field named `presence_probability` is therefore a
provisional 0–1 selection signal, not yet an empirically calibrated probability.
It is kept distinct from severity by a disclosed provisional logistic mapping (neutral severity
threshold 0.50, slope 8). Human data must replace that common mapping with a calibrated per-species model.

`surface_density` wraps the supplied contrast-energy primitive at 256 and 64 pixels and retains both
fine and coarse components. The supplied reference file did not itself contain a two-scale density
function, despite the prose describing one; this wrapper makes that missing step explicit.

`arrangement_disorder` ports the supplied 48×48 PNG-compressibility ratio exactly and caps method
confidence at 0.25. It remains **WEAK** because texture and tonal noise can masquerade as layout
disorder.

`variety` is quantised RGB colour count. It does not yet measure material or semantic variety.

`textural_discomfort` is the supplied mid/high-frequency spectral-energy fraction with a declared
provisional scale. It is not a direct measure of felt discomfort.

Human calibration must estimate validity per species and population. Tagger-blind validation comes
first; production may use tagger hypotheses only after that validity is known.

## Queue boundaries

The tagger produces deterministic candidates and reasons. It does not decide which participant sees
which image.

- **Boundary:** high uncertainty and closeness to the provisional 0.5 boundary.
- **Coverage:** inverse occupancy of a within-species severity bin.
- **Disagreement:** absolute difference between tagger probability and the yes/no human presence rate;
  `cannot_tell` is excluded and retained by the platform as human data.

Semantic and concealed-order species do not enter pixel-derived queues. Their candidates must come
from VLM/human/task-frame evidence.

## Integration boundary

This increment does not change `annotation_socket/annotator.py`, the authoritative predicate registry,
or the certified annotation payload. Once the sidecar contract survives corpus replay and HITL review,
the tagger can add a reference to the sidecar or embed this vector in a deliberately version-bumped
annotation payload. Until then, keeping it additive avoids silently changing a certified contract.

## Coordination answer

- **a. Location:** canonical hypotheses and deterministic candidate manifests live with the tagger;
  mutable queue scheduling and responses live in the platform.
- **b. Format:** hash-bearing JSONL files plus `manifest.json`, as specified above; an endpoint may later
  mirror these schemas unchanged.
- **c. Committer:** confirmed. Codex is the one committer for these tagger-integration files. Cowork owns
  taxonomy, teaching sets, instrument, analysis, and reference algorithms. Ccode owns platform changes.
