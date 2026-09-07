# Claim: the hand-corrected room as a scored reference

*Written 2026-08-31, before the scoring script exists. Method-card order: the claim is
recorded first so it can be checked against what happens, rather than fitted to it.*

## FREEZE

The two inputs are already committed and are not modified by this work:

- `room.json` — the pipeline's placement, produced by `place_furniture` from
  `inputs/eval_scene_mapped.json`, committed at `Image_Tagger_dk_latest@6cd13533`.
- `room.hand_edited.json` — Tanishq's hand-placed ground truth, `_edited_by tanishq`,
  `_edited_utc 2026-08-30T22:09:24.846Z`, committed at `@c61dc862`.

Their shells agree: `geometry` and `apertures` are byte-equal between the two files, so
every difference between them is a furniture difference.

## CLAIM

A deterministic script under `loop_runs/furniture_eval_office_grade_1/` — on the evaluation
side, not in platform code — reads both files, matches furniture objects **by `id`**, and
emits JSON giving, for every object, the pipeline position, the hand position, and the
planar placement error; plus a mean error across the objects the pipeline actually placed.
Run twice on unchanged inputs it produces byte-identical output, because it does nothing but
read, subtract and format.

Placement error is the planar distance `hypot(x_pipe − x_hand, y_pipe − y_hand)` in metres.
The vertical axis is excluded: every object in both files sits at `z_m 0.0`, so a third term
would add nothing but a false suggestion of 3D scoring.

## REFUTATION

Run it against the current pair. It must reproduce the numbers already established by hand:

| object | expected error |
| --- | --- |
| `reception_desk` (o1) | 0.99 m |
| `built_in_shelving` (o4) | 1.64 m |
| `sofa` (o2) | 2.94 m |
| `round_table` (o3) | unplaced by the pipeline — no error defined |
| `slat_divider` (o5) | unplaced by the pipeline — no error defined |

Any other result and the script is wrong, not the hand numbers. It is also refuted if it
reports an error for an object the pipeline never placed, if it silently drops an object
present in either file, or if two runs on the same inputs differ.

## The mean, and what it is allowed to average

The mean is taken over the **three placed objects only**, and the JSON says so in the same
breath as the number. Two of five objects were never placed, and there is no honest error
value for them: zero would read as perfect, and any imputed distance would be invented. The
count of unplaced objects is reported beside the mean so the mean can never be read as
covering all five. On the current pair that mean is expected near 1.86 m.

## Calibration

Every score carries `exploratory_uncalibrated`. Five objects, one photograph, one hand, and
the same person who drafted and corrected the scene also placed the ground truth. These are
measurements of a difference between two files, not a calibrated error rate, and nothing
here supports a distributional claim.

## Bounds carried in

The pipeline's own `_provenance` already flags the mechanism this measures: size from the
Neufert dimensional priors, position along-room from the bbox centre, depth from the bbox
bottom via a crude floor projection, with metric depth needing camera calibration. The hand
edit changed only positions — widths, depths and heights match the priors exactly — so what
this script scores is that placement heuristic, not the sizing.
