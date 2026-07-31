# Occupancy Register — tagger read-path spec

*How the social-presence knowledge base enters the tagger pipeline. Lives at
`docs/space_effects/social_presence/OCCUPANCY_REGISTER_SPEC.md`. Draft 2026-07-31 (cowork). Mirrors the
clutter-species pattern: image-readable cues → graded hypotheses → HITL validation. Outputs are hypotheses,
never answer keys.*

## What the register is for
Occupancy is a **modulator**, not a fixed attribute of the image (see README). The register's job is to read,
from an image, *what the occupancy is*, so the tagger can emit every other register's impact **conditional
on** it. An empty-room prediction and an occupied-room prediction are different outputs of the same pipeline.

## Cues the tagger reads (image-computable → hypothesis)
Graded low → high, each with presence ∈ present|absent|abstain, degree, uncertainty (same schema as the
clutter species):
- **headcount** — number of people detected. Firm cue; off-the-shelf person detection (see roadmap image-DB
  list: crowd-counting sets).
- **density-relative-to-area** — headcount ÷ estimated floor area / seating capacity. The variable that turns
  presence into *crowding*. Needs a rough area/capacity estimate; **abstain** when area is unreadable.
- **personal-distance proxy** — nearest-neighbour spacing between people vs body scale (a proxemics proxy).
  Present only when ≥2 people and scale is readable.
- **gathering structure** — queue / cluster / dispersed / seated-rows. Weak but cheap; conditions whether
  presence reads as chosen (event) vs imposed (crowd).
- **relationship / behaviour signal** — supportive-group vs stranger-crowd cues (orientation, interaction).
  **Hard; abstain by default.** This is where the register's residual is largest and where HITL earns its
  keep — the late/observer component, exactly as with the clutter late species.

## Output contract (matches the Phase-1 artifact shape)
One row per (image, cue): `{ image_id, path, cue, value, presence, uncertainty, queue[], model_version,
calibrated:false }`. The register also emits one **conditioning tag** per image —
`occupancy_state ∈ {empty, low, working, crowded, full_supportive, cannot_tell}` — derived from the cues,
carried alongside every *other* register's output for that image so downstream impact predictions can be read
against it (MATRIX.md Matrix 2).

## The conditional-emission rule (the point of the whole register)
For any other register R (clutter, materials, acoustics…), the tagger emits R's predicted impact **twice** or
**tagged**: the baseline (space-only) value, and the occupancy-conditioned value. Worked example: predicted
stress from reverberation (materials §1) × occupancy_state=crowded+strangers → upgraded; × empty → baseline.
The register never overwrites R; it annotates it. `cannot_tell` → emit baseline only and flag.

## What is image-computable vs abstain (be honest about the ceiling)
- **Computable now:** headcount, gathering structure (coarse), density given a usable area estimate.
- **Abstain / HITL-only:** relationship (supportive vs threat), chosen vs imposed presence, individual
  differences (social anxiety weakens buffering — MECHANISMS §3). These set the *sign*, and no image measure
  reads them reliably. The register's residual against human judgment **measures** this late component, rather
  than pretending to compute it — same discipline as the clutter tagger.

## Validation (HITL, same gates as the species)
Species-gated study: identify occupancy_state (present/absent/cannot-tell/applicability/confidence), then
within-state degree; cross-cue probes test discrimination (is this density or is this arrangement?), not
ranking; active corpus selection prioritises boundary occupancy_state and the same-space-varying-occupancy
series (roadmap purpose-built set). Objection loop feeds species/cue redefinition (reserved for humans).

## Dependencies / sequence
Downstream of: person-detection intake (off-the-shelf), the occupancy image series (purpose-built). Parallel
to: clutter Phase-1 (shares the artifact shape and viewer). Not on the clutter critical path — this is a new
register that reuses the same machinery, so it can start once the occupancy image series exists.
