# Running the production loop

*For someone who has never opened this repository. You will take one photograph of a room,
have the platform build a 3D room from it, have this repository compare the two, and record
what you think of the result. Allow about twenty minutes the first time, most of it
installing things.*

## Two limits, before you run anything

These are not caveats hidden at the bottom. They change what the output means, and you will
misread your own run without them.

**1. The loop does not converge. It repeats.** The adjuster is a placeholder called
`none_v0`: the producer never reads the previous verdict, so iteration 2 is not an improved
attempt at iteration 1 — it is the same attempt again. In the committed example, run B's
three iterations all score exactly 0.1. If you see a run stop at the cap with identical
scores, nothing is broken and nothing is converging. Making the loop actually iterate is an
open task on the student queue (**D4-1**).

**2. Every human verdict so far was written by the person who built the thing being
judged.** There are four verdict rows in `loop_runs/`, all of them mine. None is blind, none
is paired, and no agreement statistic (κ) has been computed, because you cannot compute
agreement from one rater. A verdict cast by the builder tells you the builder was
consistent; it does not tell you two people would agree. Producing the first blind paired
verdicts is also an open task (**C2-1**).

So: a green run is evidence that the comparator found no structural disagreement on the axes
it checks. It is not evidence that the reconstruction is right.

## Install

You need Python 3 and a virtual environment. The producer imports `vr_condition_audit` from
the platform repository, which needs `jsonschema`; Homebrew's Python refuses to install into
itself under PEP 668, so a venv is not optional.

```sh
python3 -m venv ~/.venvs/vr-producer
~/.venvs/vr-producer/bin/pip install jsonschema Pillow
~/.venvs/vr-producer/bin/pip install -e /path/to/New_VR_Platform
```

`Pillow` is only needed for the side-by-side comparison images under `comparison/`, not for
the loop itself. The comparator (`loop/run_loop_compare.py`) is standard library only.

One wrinkle worth knowing: the interpreter path you use gets hashed into the run's
`producer_cmd_sha256`, so a run made with `~/.venvs/vr-producer` records *your* machine's
interpreter rather than a portable command. Two people running the same photograph will
agree on everything except that hash.

## Run it

From the repository root. The example below is the committed worked example, run A — the
real producer against a real photograph of an office lobby.

```sh
python3 loop/orchestrate.py run \
  --target loop_runs/real_photo_2026-08-27/inputs/Office-Grade-1.reference_scene.json \
  --run-dir loop_runs/real_photo_2026-08-27/my_first_run \
  --producer-cmd "~/.venvs/vr-producer/bin/python3 /path/to/New_VR_Platform/production_loop/emit_render_packet.py --scene {target} --out-dir {render_dir} --run-id {run_id} --iter {iter}" \
  --cap 3 --threshold 0.0
```

The four braces in `--producer-cmd` are placeholders the orchestrator fills in per iteration;
leave them exactly as written. Pick a `--run-dir` that does not exist yet — the orchestrator
refuses to write into an existing directory rather than overwrite someone's evidence.

**How long:** the run itself is quick — run A is a single iteration and finishes in seconds;
a capped three-iteration run like run B still takes well under a minute. The install above is
the slow part.

## What a good run looks like

Open `run_summary.json` in your run directory and check four things.

| Field | What you want to see |
|---|---|
| `final_status` | `STOPPED_BELOW_THRESHOLD` — the comparator found no disagreement it scores. `CAP_REACHED_FLAGGED` means it never got below the threshold and gave up; that is a flagged non-result, not a failure of the software |
| `iterations[].identity_mode` | `exact` — openings were matched one-to-one by their platform ids (`ap0`, `ap1`). `multiset_fallback` means ids were missing and the match is weaker; `vacuous` means neither side claimed anything on that axis |
| `iterations[].score` | `0.0` for a clean run. Treat this as a flag, not a measurement — the schema pins it `exploratory_uncalibrated`, and there is no calibrated scale behind the number |
| `target_sha256`, `producer_cmd_sha256` | Present. These bind the run to the exact target file and producer command that made it |

The hash binding is the part that makes a run evidence rather than an anecdote. The run
records `target_sha256` for the input and `producer_cmd_sha256` for the command; each
iteration's `verdict_sha256` names the verdict file it produced; and when you record a human
verdict, that row carries `run_summary_sha256` binding it to this exact summary, plus
`previous_hitl_sha256` and `row_sha256` forming an append-only chain. Change any byte
upstream and the chain no longer verifies. This is why you never edit a run directory by
hand.

A useful sanity check: run the negative control too. `wrong_wall_stub_producer.py` puts the
glazed wall on the north wall instead of the east. It should be *rejected* —
`expected_wall=east, rendered_wall=north`, cap reached. A checker that passes both a good
input and a deliberately broken one is not checking anything.

## Where the output lands

Everything goes under your `--run-dir`:

```
my_first_run/
  target.snapshot.json          the target as it was at run time
  run_summary.json              the whole run: status, iterations, hashes
  hitl.jsonl                    human verdicts, append-only (empty until you add one)
  iter_0/render/packet.json     the producer's manifest, with sha256 per file
  iter_0/render/room.json       the reconstruction it claims
  iter_0/render/camera.json     the camera it rendered from
  iter_0/render/render.png      a 1×1 grey placeholder, not a real rendering
  iter_0/verdict/verdict.json   the comparator's verdict
```

`render.png` being one grey pixel is deliberate and declared (`render_kind:
"structural_placeholder_v0"`). The platform renders in a browser and no headless renderer is
wired up yet, so the loop compares structure — `room.json` against the target — rather than
pixels. The pictures under `comparison/` are drawn afterwards from the room JSON; they are
not loop output.

## Recording your verdict

Look at the photograph, look at what the reconstruction claims, and say what you think. The
`--who` flag is required and the orchestrator refuses a row without it.

```sh
python3 loop/orchestrate.py hitl \
  --run-dir loop_runs/real_photo_2026-08-27/my_first_run \
  --verdict accept --who your-name \
  --note "what you actually saw when you compared them"
```

`--verdict` takes `accept` or `reject`. The row appends; it never replaces. And per limit 2
above, if you built the run you are rating, say so in the note — a builder's verdict is worth
recording and worth marking.

---

*Questions this document cannot answer belong in `IMPROVEMENT_BACKLOG.md` in the students'
package. An instruction here that assumes something nobody told you is a finding about the
document, not a failure on your part.*
