# real_photo_2026-08-27 — the loop run on an actual photograph

This directory is one milestone: the photo→VR loop driven end to end against a real
photograph rather than a fixture, with both a human accept and a human reject recorded
against it. Everything here was produced against `loop/orchestrate.py` and
`loop/run_loop_compare.py` as they stand at `ba4c90b0` (render-verdict/v0.7).

The target is `inputs/Office-Grade-1-1536x838.jpg`, with its annotation
`Office-Grade-1-1536x838_DK.json` and the corrected reference scene
`Office-Grade-1.reference_scene.json`.

**`runA_real_producer/`** — the real producer. One iteration, no opening mismatches,
score 0.0, final status `STOPPED_BELOW_THRESHOLD`.

**`runB_wrong_wall_stub/`** — a negative control. `wrong_wall_stub_producer.py` puts the
glazed wall on the north wall instead of the east wall, which is the error David's own
critique of this photograph identified. The comparator reports it as
`expected_wall=east, rendered_wall=north`. Three iterations, cap reached, final status
`CAP_REACHED_FLAGGED`. The producer never consumes the prior verdict, so the three
iterations are identical rather than an attempt to converge — the adjuster is `none_v0`
and remains open work.

## The rows already on disk

Both were typed by Tanishq at a shell on 2026-08-27, one per run:

| run | verdict | `run_summary_sha256` |
| --- | --- | --- |
| `runA_real_producer` | accept | `efd01885036231e5100a2e660768a003334c8c8128cc5a484ae3da00ed19118e` |
| `runB_wrong_wall_stub` | reject | `0bb3b73f74bf9ecdedf9eacae73f13b8319880692bcc855fd479c1d7a611732a` |

The digest is sha256 over the UTF-8 text of that run's `run_summary.json`, so anyone can
recompute it and see whether the row still describes the run it was attached to.

## David's rows, if he wants them

`hitl.jsonl` is opened in append mode and never rewritten, so these add rows beside
Tanishq's rather than replacing them. Run from the repo root; `--who` is required, and the
orchestrator refuses a row without it.

```
python3 loop/orchestrate.py hitl \
  --run-dir loop_runs/real_photo_2026-08-27/runA_real_producer \
  --verdict accept --who david \
  --note "your reading of the run against the photograph"
```

```
python3 loop/orchestrate.py hitl \
  --run-dir loop_runs/real_photo_2026-08-27/runB_wrong_wall_stub \
  --verdict reject --who david \
  --note "your reading of the run against the photograph"
```

## What this does not show

Worth stating plainly, because the run is easy to over-read.

The renders are placeholder PNGs — a single grey pixel. Both runs carry the same
`render_png` digest (`e5dd92ac…`), which is the giveaway: nothing here is a picture of a
room, and no one has looked at a rendered image. The verdict compares the producer's
`room.json` against the reference scene, not pixels against a photograph.

Scores are `exploratory_uncalibrated`. Run A's 0.0 means no structural disagreement was
detected on the axes the comparator actually checks. It does not mean the reconstruction
is correct, and the number has no calibrated scale behind it.

The objects axis is vacuous on this target — `objects_mode: "vacuous"`, every `object_diff`
list empty. The whole result rests on the wall-layout axis, two openings compared. So run
B's rejection turns on one mismatch, which is the one the stub was built to produce.

And the human notes agree with the verdict because the same person read both. That is
consistency between a verdict and a reader, not independent confirmation of either. An
independent check would need a reader who had not seen the verdict first.
