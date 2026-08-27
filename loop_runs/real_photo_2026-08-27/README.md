# real_photo_2026-08-27 — the loop run on an actual photograph

This directory holds the photo→VR loop driven end to end against a real photograph rather
than a fixture, with a human accept and a human reject recorded against it, plus the first
visual comparison of the photograph with what the reconstruction claims.

The target is `inputs/Office-Grade-1-1536x838.jpg`, with its annotation
`Office-Grade-1-1536x838_DK.json` and the corrected reference scene
`Office-Grade-1.reference_scene.json`.

## Two generations of the same run, and why both are here

The runs were first done against `ba4c90b0`. David then integrated our v0.7 on `main` and
repaired four review findings, one of which changed the run-summary schema — it now binds
`target_sha256` and `producer_cmd_sha256`. His hardened `record_hitl` validates those, so
it refuses the original run directories outright (`exit 2, invalid target_snapshot`). Both
generations are kept rather than one overwriting the other:

| directory | orchestrator | status | `run_summary_sha256` |
| --- | --- | --- | --- |
| `runA_real_producer/` | `ba4c90b0` | `STOPPED_BELOW_THRESHOLD` | `efd01885…19118e` |
| `runB_wrong_wall_stub/` | `ba4c90b0` | `CAP_REACHED_FLAGGED` | `0bb3b73f…11732a` |
| `runA_real_producer_postmerge/` | merged v0.7 | `STOPPED_BELOW_THRESHOLD` | `514d63d0bdc0d2c79fb12dc39c3e3574bf4894486d33cf8b922cd30ea0158813` |
| `runB_wrong_wall_stub_postmerge/` | merged v0.7 | `CAP_REACHED_FLAGGED` | `f3a1b37de7ae070e4fb0b0c8afa921ecd9969d1e0d6c1c447d5ad28f97836246` |

**The original run stands at `cd08cc2b` against `ba4c90b0`**, with its two HITL rows by
Tanishq intact. Nothing about it was rewritten. It simply predates the repairs, and its
HITL commands only work against a checkout at that commit.

The two generations agree: run A scores 0.0 with no opening mismatches either way, run B
reports `expected_wall=east, rendered_wall=north` and reaches the cap either way. The
repairs hardened the contract without moving the result, which is what you want from a
repair.

## What each run is

**Run A** — the real producer, `New_VR_Platform@fb3a873`. One iteration, two target
openings against two render apertures, zero mismatches.

**Run B** — a negative control. `wrong_wall_stub_producer.py` puts the glazed wall on the
north wall instead of the east wall, which is the error David's own critique of this
photograph identified. Three iterations, cap reached. Its three iterations are identical
because the adjuster is `none_v0` and the producer never consumes the prior verdict; that
is open work, not convergence.

## David's commands

Run from the repo root on the merged branch. `--who` is required, and the orchestrator
refuses a row without it. `hitl.jsonl` is append-only — rows now carry a
`previous_hitl_sha256` / `row_sha256` chain, so these append beside Tanishq's rather than
replacing them.

```
python3 loop/orchestrate.py hitl \
  --run-dir loop_runs/real_photo_2026-08-27/runA_real_producer_postmerge \
  --verdict accept --who david \
  --note "your reading of the run against the photograph"
```

```
python3 loop/orchestrate.py hitl \
  --run-dir loop_runs/real_photo_2026-08-27/runB_wrong_wall_stub_postmerge \
  --verdict reject --who david \
  --note "your reading of the run against the photograph"
```

Both were smoke-tested against copies of these exact directories and returned 0.

## Reproducing the runs

Run B's stub is stdlib-only. Run A's producer imports `vr_condition_audit`, which needs
`jsonschema`, and the Homebrew Python refuses installs under PEP 668 — so run A used a
venv at `~/.venvs/vr-producer` (`python3 -m venv`, then `pip install jsonschema`). That
path is baked into run A's `producer_cmd_sha256`, so it records this machine's interpreter
rather than a portable template. Worth replacing with a declared project environment.

```
python3 loop/orchestrate.py run \
  --target loop_runs/real_photo_2026-08-27/inputs/Office-Grade-1.reference_scene.json \
  --run-dir loop_runs/real_photo_2026-08-27/<a fresh directory> \
  --producer-cmd "<producer> --scene {target} --out-dir {render_dir} --run-id {run_id} --iter {iter}" \
  --cap 3 --threshold 0.0
```

The orchestrator now refuses a run directory that already exists, so each run needs a new
one.

## comparison/ — the photograph beside the reconstruction

`render_room.py` draws a `room.json` from the packet's own declared camera, using only the
standard library and Pillow. `render_east_glazing.png` is run A's reconstruction drawn
that way; `side_by_side_office_grade_1.png` sets it against the photograph;
`comparison_office_grade_1.html` is a self-contained page with both images inlined.

Three consecutive renders on one machine produce byte-identical PNGs. Across machines they
differ — this Mac renders `2c0f3b3f…` where the committed `render_east_glazing.png` from
the Cowork box is `cc608ad5…` — because the fonts resolve differently. Determinism holds
per environment, not across them, which is the same lesson already recorded for JPEG decode
in the L5 cross-environment findings.

## What this does not show

Worth stating plainly, because the run is easy to over-read.

Something can now be seen and compared, but only structurally. The render draws exactly
what the reconstruction claims — walls, apertures, and furniture as dimensioned boxes sized
by Neufert priors rather than meshes — from exactly the camera the packet declares. It is
not photoreal, and the footer says so on the image itself. Each run's own `render.png`
remains a `structural_placeholder_v0`, a single grey pixel; the comparison images are drawn
afterwards from the room JSON, not produced by the loop.

Scores are `exploratory_uncalibrated`. Run A's 0.0 means no structural disagreement was
detected on the axes the comparator checks. It does not mean the reconstruction is correct,
and there is no calibrated scale behind the number.

The objects axis is vacuous — `objects_mode: "vacuous"`, every `object_diff` list empty.
The whole result rests on the wall-layout axis, two openings compared. So run B's rejection
turns on one mismatch, the one the stub was built to produce.

And the human notes agree with the verdict because the same person read both. That is
consistency between a verdict and a reader, not independent confirmation of either. An
independent check would need a reader who had not seen the verdict first.
