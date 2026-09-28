# Running the production loop

*For someone who has never opened this repository, working from a clean clone on their own
machine. You will take one photograph of a room, have the platform build a room from it, have
this repository compare the two, and record what you think of the result. Allow about twenty
minutes the first time; most of that is installing dependencies.*

## Two limits, before you run anything

These are not caveats to skim. They change what the output means, and you will misread your
own run without them. Six recorded limitations follow, grouped under the two that matter
most.

**1. The loop does not converge. It repeats.**

- The adjuster is a placeholder. Every run summary records it verbatim as
  `"none_v0 (producer does not yet consume prior verdicts — open work)"`.
- The producer never reads the previous verdict, so iteration *k+1* is not an improved
  attempt at iteration *k*.
- Repetition is therefore not convergence. The committed negative control makes this
  concrete: run B's three iterations all score exactly `0.1`, all `CONTINUE`. As
  `loop_runs/real_photo_2026-08-27/README.md` puts it, "that is open work, not convergence."

Making the loop genuinely iterate is task **D4** on the students' queue.

**2. No human verdict so far is independent.**

- Every verdict is `exploratory_uncalibrated`. The verdict schema pins that string as a
  constant, and each run summary carries the note
  `"scores are exploratory_uncalibrated; acceptance is a human act (hitl)"`. A score is a
  flag, not a measurement; there is no calibrated scale behind the number.
- The result rests on one axis. The object axis is vacuous — `objects_mode: "vacuous"`, every
  `object_diff` list empty — so the whole comparison is the wall-layout axis, **two openings
  compared**. Run B's rejection turns on the single mismatch its stub was built to produce.
- There are four human verdict rows in `loop_runs/`, and all four were written by the person
  who built the run being judged. None is blind, none is paired, and no agreement statistic
  (κ) exists, because you cannot compute agreement from one rater. The README says it
  plainly: "the human notes agree with the verdict because the same person read both. That is
  consistency between a verdict and a reader, not independent confirmation of either."

Producing the first blind paired verdicts is task **C2** on the students' queue.

So a green run means the comparator found no structural disagreement on the axes it checks.
It does not mean the reconstruction is right.

## What you need

Two repositories, because the loop spans both.

| Role | Repository | Ref to use |
|---|---|---|
| Orchestrator + comparator (this repo) | `Image_Tagger_dk_latest` | `main` |
| Producer (builds the room) | `New_VR_Platform` | branch `tanishq/production-loop`, commit `d22f4557` |

The producer is **not on `New_VR_Platform`'s `main`**. It lives only on
`tanishq/production-loop`, whose server tip is `d22f45575d697e41536e0ab258533188f53c2aa3`;
the producer file itself last changed in `fb3a8738`. Check out that branch by name — if you
clone `main` you will not find `production_loop/` at all. (Where the loop and its producer
finally live is an open decision, **S13** on the students' queue.)

## Install

No environment variables are required; the loop reads none.

```sh
# 1. the two repositories, side by side
git clone https://github.com/dkirsh/Image_Tagger_dk_latest.git
git clone https://github.com/dkirsh/New_VR_Platform.git
cd New_VR_Platform && git checkout tanishq/production-loop && cd ..

# 2. a virtual environment INSIDE your Image_Tagger clone
cd Image_Tagger_dk_latest
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install jsonschema Pillow
./.venv/bin/pip install -e ../New_VR_Platform
```

Python 3.11 or newer. `jsonschema` is required by the producer's platform imports; `Pillow` is
needed only to redraw the comparison images under `comparison/`, not by the loop. Installing
`New_VR_Platform` editable (`-e`) is what puts `vr_condition_audit` on the path.

A note on why the venv is relative. Homebrew's Python refuses installs under PEP 668, so a
venv is not optional — and the interpreter path you use is hashed into the run's
`producer_cmd_sha256`. A venv at `.venv` inside your clone keeps that hash a function of the
project rather than of your home directory. The older worked example baked an absolute
`~/.venvs/...` path into its recorded hash; that is exactly what this document replaces.

## Run it

From the root of your `Image_Tagger_dk_latest` clone:

```sh
./.venv/bin/python3 loop/orchestrate.py run \
  --target loop_runs/real_photo_2026-08-27/inputs/Office-Grade-1.reference_scene.json \
  --run-dir loop_runs/my_first_run \
  --producer-cmd "./.venv/bin/python3 ../New_VR_Platform/production_loop/emit_render_packet.py --scene {target} --out-dir {render_dir} --run-id {run_id} --iter {iter}" \
  --cap 3 --threshold 0.0
```

The four braces in `--producer-cmd` are placeholders the orchestrator substitutes per
iteration — leave them exactly as written. Choose a `--run-dir` that does not exist yet; the
orchestrator refuses to write into an existing directory rather than overwrite evidence.

**Inputs.** The target is a reference scene JSON — the corrected annotation of one
photograph. The committed example pairs
`inputs/Office-Grade-1.reference_scene.json` with the photograph
`inputs/Office-Grade-1-1536x838.jpg` and the raw annotation
`inputs/Office-Grade-1-1536x838_DK.json`.

**How long.** Run A is a single iteration and finishes in seconds. A capped three-iteration
run like run B still takes well under a minute. Installing is the slow part.

## Reading the result: success, refused, or capped

Exit codes are the first thing to check.

| Exit | Meaning |
|---|---|
| `0` | The run completed. Read `final_status` to learn *how* it completed |
| `2` | **REFUSED** — fail-closed. The run did not happen. The message begins `REFUSED:` and names the reason: cap below 1, threshold outside [0,1], run directory already exists, producer failed or timed out, producer mutated the target snapshot, packet identity mismatch, malformed input |
| `1` | Comparator-internal failure: a verdict failed self-validation, or a canonical round-trip diverged (`nondeterministic_run`) |

A refusal is not a failed comparison. It means the loop declined to produce a verdict because
a precondition was not met — which is the behaviour you want from a checker.

On exit 0, open `run_summary.json` and check four fields:

| Field | What you want |
|---|---|
| `final_status` | `STOPPED_BELOW_THRESHOLD` — no scored disagreement. `CAP_REACHED_FLAGGED` means it never got below the threshold and stopped at the cap; that is a flagged non-result |
| `iterations[].identity_mode` | `exact` — openings matched one-to-one by platform ids (`ap0`, `ap1`). `multiset_fallback` means ids were missing and the match is weaker; `vacuous` means neither side claimed anything on that axis |
| `iterations[].score` | `0.0` on a clean run — and see limit 2 above on what a score is worth |
| `target_sha256`, `producer_cmd_sha256` | Present, binding the run to the exact target file and producer command |

**The hash binding** is what makes a run evidence rather than an anecdote. The summary records
`target_sha256` and `producer_cmd_sha256`; each iteration's `verdict_sha256` names the verdict
file; and a human verdict row carries `run_summary_sha256` binding it to that exact summary,
plus `previous_hitl_sha256` and `row_sha256` forming an append-only chain. Change one byte
upstream and the chain stops verifying. Never edit a run directory by hand.

## Reproduce the negative control

Do this too. A checker that passes a good input and a deliberately broken one is not checking
anything.

`loop_runs/real_photo_2026-08-27/wrong_wall_stub_producer.py` is a stub that puts the glazed
wall on the **north** wall instead of the east — the error David's own critique of this
photograph identified. It is standard-library only, so it needs no venv:

```sh
python3 loop/orchestrate.py run \
  --target loop_runs/real_photo_2026-08-27/inputs/Office-Grade-1.reference_scene.json \
  --run-dir loop_runs/my_negative_control \
  --producer-cmd "python3 loop_runs/real_photo_2026-08-27/wrong_wall_stub_producer.py --scene {target} --out-dir {render_dir} --run-id {run_id} --iter {iter}" \
  --cap 3 --threshold 0.0
```

Expect it to be caught: `expected_wall=east, rendered_wall=north`, three identical iterations
at score `0.1`, and `final_status: CAP_REACHED_FLAGGED`. If your negative control comes back
clean, something is wrong with your setup — not with the room.

## Where things land, and where new work belongs

One run directory holds everything from one run:

```
loop_runs/my_first_run/
  target.snapshot.json          the target as it was at run time
  run_summary.json              status, iterations, hashes
  hitl.jsonl                    human verdicts, append-only (empty until you add one)
  iter_0/render/packet.json     producer manifest, sha256 per file
  iter_0/render/room.json       the reconstruction it claims
  iter_0/render/camera.json     the camera it rendered from
  iter_0/render/render.png      a 1×1 grey placeholder, not a rendering
  iter_0/verdict/verdict.json   the comparator's verdict
```

`render.png` being one grey pixel is deliberate and declared
(`render_kind: "structural_placeholder_v0"`). The platform renders in a browser and no
headless renderer is wired up, so the loop compares structure — `room.json` against the
target — not pixels. The images under `comparison/` are drawn afterwards from the room JSON.

**New run artifacts** belong in a fresh directory under `loop_runs/`, named for what the run
is. Never reuse or edit an existing one; the orchestrator enforces this by refusing an
existing `--run-dir`.

**Human verdicts** belong in that run's own `hitl.jsonl`, written only through the `hitl`
subcommand so the hash chain stays intact:

```sh
python3 loop/orchestrate.py hitl \
  --run-dir loop_runs/my_first_run \
  --verdict accept --who your-name \
  --note "what you actually saw when you compared the render against the photograph"
```

`--verdict` takes `accept` or `reject`; `--who` is required and the orchestrator refuses a row
without it. If you built the run you are rating, say so in the note — per limit 2, a
builder's verdict is worth recording and worth marking as such. Blind paired verdicts for the
students' lane ledger go under `hitl/ledgers/` in the students' package, following
`hitl/HITL_THREE_GATE_PROCEDURE.md`, not into this file.

---

*If a step here does not work from a clean clone, that is a finding about this document, not
a failure on your part. Record it in the students' `IMPROVEMENT_BACKLOG.md`.*
