# FINDING — `isovist_fields` uses a non-supercover visibility march (diagonal-wall leak)

**Date:** 2026-07-30 · **Severity:** medium · **Found by:** the validation harness, first objective slice
**Predicate:** `cnfa_algs.plan.isovist_fields` · **Engine:** `cnfa-algs-2026-07-14 @ ee1f2a98`
**Status:** confirmed by run; fix proposed, not yet applied (David's/owner's call)

## What was checked

The harness validated `isovist_fields` on known geometry and on real Structured3D ground-truth scenes,
and compared its internal visibility model against `los.segment_is_free` — the supercover line-of-sight
primitive the panel installed (module `los.py`, "S1 fix") specifically to stop rays slipping through
one-cell-thick diagonal walls. `los.segment_is_free` itself passed its full analytic self-test (7/7,
zero diagonal leaks) and is treated here as ground truth for "does a wall block this sightline."

## What passed

- **Runs correctly on real ground truth.** All three Structured3D scenes (`scene_00889`, `00924`,
  `03457`) load via `annotation_to_plangrid` and produce finite openness on **100%** of free cells, with
  plausible `cell_m` (~0.08 m) and free/obstructed fractions, in ~1.5 s each. The adapter → PlanGrid →
  isovist path is sound.
- **The field is correctly monotone.** On a room with an alcove, mean radial openness is higher in the
  open area (0.825 m) than inside the enclosed pocket (0.651 m) — enclosure reduces openness, as it must.
- **Open space agrees perfectly.** In an obstacle-free room, the isovist march and the validated LOS
  primitive agree on 1500/1500 sampled sightlines.

## The finding

`isovist_fields` marches each ray with an integer-truncation step (`ri, ci = int(rr), int(cc)`; advance
`rr += dr, cc += dc`; stop on a non-free cell). This is the classic **thin/DDA** ray, **not** the
supercover test. An independent reconstruction of that same march, compared against `segment_is_free`
on identical geometry, shows it is **not conservative**:

| Geometry | Sightlines | Disagreements | All of them are… |
|---|---|---|---|
| Open room | 1500 | 0 | — |
| Axis-aligned partition + doorway | 1499 | 16 | rays leaking **through** the wall at grazing corners |
| Diagonal wall (OBST chain) | 1500 | 156 | rays leaking **through** the diagonal wall |

Every disagreement is in the unsafe direction: the isovist march reports a sightline **open** that the
validated primitive (correctly) reports **blocked**. This is precisely the defect `los.py` documents and
fixes — "a ray sampled by max-step passes THROUGH a one-cell-thick diagonal wall" — but `isovist_fields`
predates or bypasses that fix and still carries it.

## Why it matters (and its bounds)

Openness/prospect/refuge are averages over many rays, so a few leaking rays perturb a cell's value rather
than invert it — and Structured3D interiors are largely axis-aligned, so the practical error there is
small and concentrated at grazing corners (which is why the field still looks sane and monotone). But the
leak is real, it is systematic (always over-reporting visibility), and it grows with **diagonal or angled
walls** — bay windows, splayed entries, angled partitions, furniture edges — i.e., exactly the richer
geometry the 3D-intake thread is heading toward. Any downstream measure built on isovist visibility
(view-equity, prospect-refuge seat choice, VGA-style integration) inherits the optimism.

## Proposed fix (name-a-fix, per the bar)

Route the per-ray occlusion test in `isovist_fields` (and any sibling that marches rays — check
`space_syntax.py`, `daylight_view.py`, `composition.py`, `movement.py`) through the already-validated
`los.segment_is_free` / a supercover step, instead of the `int()`-truncation march. The S1 fix was
applied to "six modules"; this finding is that the isovist field computation was not among them. After
the change, re-run this harness entry — the three analytic cases should drop to **0** leaks, and the
Structured3D openness values should shift slightly (and correctly) downward near walls.

## Reproduce

`harness/run_isovist.py` (uses the real `los.py`, `plan.py`, `geometry.py`,
`adapters/structured3d_adapter.py`). Canonical in-repo confirmation of the primitive: `python -m
cnfa_algs.los`.

*Caveat on method: the leak counts come from an independent reconstruction of the engine's march model
(unit-step, integer truncation), not from instrumenting `isovist_fields` line-by-line. The reconstruction
matches the source's stepping style; the direction and existence of the finding are robust, the exact
counts are indicative. Instrumenting the real per-ray loop to emit its visited cells would make the
counts exact — a good next hardening step.*
