# Image_Tagger — Repo State Model and Plan

**Generated-state header — do not hand-edit these six lines; `scripts/refresh_state_model.py` rewrites them.**
- `STATE_AS_OF: 2026-08-05T06:19Z`
- `HEAD: df7887751`
- `STALE_AFTER_DAYS: 7`
- `VERIFIED_BY: scripts/refresh_state_model.py` (re-derives every number in §5 by execution)
- `MEASURED_ON: python3.14.2 darwin · numpy=yes cv2=yes PIL=yes skimage=yes scipy=yes pytest=yes`
- `MEASUREMENT_QUORUM: 13/13 measurements returned a value (0 ABSENT or ERROR)`
- `JUDGED_REVIEWED: 2026-08-05`
- `JUDGED_REVIEW_INTERVAL_DAYS: 90`

> **Why the last two lines exist, and why they are hand-maintained.** The six generated lines above
> watch content that is *derived* — numbers a script can re-execute. They cannot watch §1–§4 and §7,
> which are **judgements**: what the system is for, which traps matter, what the parts are really
> trying to achieve. Judgements rot with the world rather than with the repository, so a repo could
> pass its freshness check indefinitely while §1 described a system it had stopped being. Until this
> pair was added, `scripts/prevention/state_model_freshness_check.py` reported this document STALE for
> exactly that reason and no other. The refresher does not emit these fields; a person re-reads §1–§4
> and §7 and re-stamps the date. *Added 2026-08-05.*

> **`MEASURED_ON` is load-bearing, not decoration.** Several §5 figures are *environment-dependent*
> — the socket test tallies change depending on whether `skimage`, `scipy` and `pytest` are importable.
> A figure re-derived on a machine with a different dependency set is a *different figure*, not a
> fresher one. The refresher refuses to stamp `STATE_AS_OF` at all unless a quorum of measurements
> actually returned values; see §10.
>
> **This is no longer a caution; it is a measured result.** The same commit was measured on two
> machines within twenty minutes. One reports `33 collected, 31 pass, 2 fail`; the other reports
> `55 collected, 49 pass, 6 fail`. Neither is stale. Neither is wrong. They are figures about two
> different environments, and **§5.3 below is bound to the first one only** — §5.3b records the
> second, side by side, because collapsing them into one number destroys the finding that matters.
> Do not "update" §5.3 by overwriting it with a run from your machine. Add your machine.

## How to read this doc

**§1–§4 and §7 are STABLE.** They describe what the system is for, how the calls chain, what the
parts are actually trying to achieve, where data lives, and which traps have already caught someone.
They change when the architecture changes — not weekly. Hand-edit them.

**§5–§6 are VOLATILE.** §5 is a snapshot with a command beside every number. §6 is the plan, which
moves as work lands. Do not trust §5 if the header above is stale; run the refresher.

**Every figure in §5 carries the command that produced it.** A number with no command beside it is a
defect in this document. If you find one, that is a bug report, not a detail.

---

## §1 — What this system is FOR

Image_Tagger exists to turn photographs (and, where available, floor plans) of interior architectural
space into **measurements a researcher can defend in a paper** — not into labels a demo can display.

The distinction that governs everything here is David's *cognitive code vs physical code*. Physical
code is what a building literally is: geometry, materials, luminance, reverberation. Cognitive code is
what the space *does to a mind that is in it*: how legible it is, how much processing it costs, whether
it affords retreat or exposure, whether it invites or repels. The programme's bet is that cognitive
code is measurable from image evidence, and that the measurement is only worth anything if a hostile
reader can replay it.

So the real objective is not "tag the image". It is:

> **Produce a per-image, per-predicate value whose derivation can be re-executed by someone who does
> not trust the person who produced it — and which says ABSTAINED, loudly and with evidence, whenever
> it cannot.**

That single sentence explains almost every design choice you will find odd:

- why a predicate that *could* return a plausible number returns `None` with a named `failure_mode`
  instead (silence is a lie; abstention is data);
- why the registry declares `tier_hint` as a **ceiling** — a predicate riding heuristic Tier-B geometry
  is forbidden from self-claiming GREEN, because GREEN is an *outcome of evidence*, never a target;
- why `verify.py` re-executes the method rather than reading the annotator's own claim (the author's
  own test is compromised by the same pressure that produced the defect);
- why tampering with a stored derivation is designed to produce **RED**, not a warning.

The failure this repo is built against is not a wrong number. It is a **confident** wrong number.

## §2 — The chain of calls

**The most important structural fact in this repository: there are TWO independent attribute engines,
and they are not connected to each other.** A newcomer told "work on the tagger's attributes" will,
more likely than not, edit the wrong one. See §7.1.

### Engine A — the research / science core (honest-by-construction, AMBER, NOT the app's pipeline)

```
image bytes (+ optional plan, seats, glazing, … "requires" tokens)
   |
   v
annotation_socket/annotator.py        -- walks the registry, calls each applicable predicate
   |
   +-- annotation_socket/registry.py  -- PREDICATES: id / requires / audit_class / tier_hint / kind
   |                                     THE APPLICABLE-SET ORACLE. Applicability is DATA, not code.
   v
cnfa_algs/*.py                        -- the actual measurement functions
   |   core.py .......... AttributeResult  (every value in the system flows through this type)
   |   geometry.py, los.py, contracts.py, setting_classifier.py, hedonics.py, activity.py   [foundation]
   |   attributes.py, composition.py                                                        [Tier A]
   |   plan.py, spatial_syntax.py                                                           [Tier B]
   |   movement / acoustics_plan / daylight_view / thermal_plan / space_syntax /
   |   affordance / wellbeing_plan                                                           [plan-space]
   |   score_layout.py, validate_pipeline.py, vlm_activity_prompt.py                         [aggregation]
   v
annotation_socket/derivation.py       -- THE TRUST CHOKEPOINT. scored() / abstain() / unknown().
   |                                     No result enters the record except through these three doors.
   v
annotation_socket/m1_prime.py         -- M1' audit spine: binds value <-> method <-> inputs
   |
   v
annotation_socket/verify.py           -- METHOD REPLAY. Re-executes the declared method and compares.
   |                                     audit_class "replayable"     -> exact match demanded
   |                                     audit_class "replayable_tol" -> match within tolerance
   |                                     mismatch or tampering        -> RED
   v
annotation_socket/controller.py       -- routes units, applies tier ceilings, emits the record
   |
   v
tri-state annotation record: SCORED | ABSTAINED (with named missing input) | UNKNOWN
```

Unit identity is content-addressed: `sha256(image_bytes + MODEL_VERSION)[:16]`. Change the algorithm,
change `MODEL_VERSION`, and every previously-derived unit becomes a *different* unit rather than a
silently-overwritten one.

The socket depends on the shared **CPP `stage` library**, which lives in a **sibling repository**
(`_control/cpp`), adopted rather than vendored. This is the single largest portability trap in the
repo — see §4 and §7.2.

### Engine B — the production web application (what actually runs when a user uploads a photo)

```
browser upload
   v
Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/     (VERSION: 3.4.74_vlm_lab_notebook_TL_runbook)
   backend/science/pipeline.py                   "Science Pipeline Orchestrator v3.4 (OneFormer Edition)"
      SCIENCE_SOURCE = "science_pipeline_v3.4"
      SciencePipelineConfig:
         enable_mpib_low_level          (MPIB low-level features)
         cognitive / semantic / segmentation stages are OPT-IN
   v
SciencePayload -> frontend
```

Engine B has its own `tests/` (20 files), its own `features_registry.py`, its own `governance.lock`
(policy_version 3.0.0, hash + size per protected file), and its own `PROJECT_CONSTITUTION.md`
(no-deletion rule, `archive/` subtree, `guardian.py verify|freeze`, no `...` placeholders in code).

**Engine A runs *parallel to* Engine B. It is not yet the canonical science-run inside the app.**
Making it so is the central item of §6.

## §3 — The parts, their REAL objective, and the observable condition that says they succeeded

The middle column is the part's *actual* purpose, which is frequently not what its name suggests. The
right column is what you can *observe* — not what someone asserts.

| Part | REAL objective (not the label) | Observable success condition |
|---|---|---|
| `annotation_socket/registry.py` | Be the **applicable-set oracle**, so coverage is a mechanical fact rather than a judgement call. Declare tier ceilings as data so no predicate can promote itself. | `PREDICATES` enumerates; for a given unit, the set of predicates whose `requires` are satisfied is computable *without running any predicate*; every entry's `tier_hint` is a ceiling that the controller can enforce. |
| `annotation_socket/derivation.py` | Be the **only door** into the record, so "silence" is structurally impossible. | Every record entry is SCORED, ABSTAINED or UNKNOWN. Grep finds no path that appends a result without passing through `scored()`/`abstain()`/`unknown()`. |
| `annotation_socket/verify.py` | Defeat the **curse of authorship**: check the method by re-running it, not by reading the annotator's claim. | A deliberately tampered stored derivation produces **RED**. (Negative control; see §8.) |
| `annotation_socket/m1_prime.py` | Bind value ↔ method ↔ inputs so a value cannot be separated from how it was obtained. | `test_m1_prime.py` exercises scalar-mismatch and missing-block verdicts; both return the tampering verdict rather than passing. |
| `cnfa_algs/core.py` (`AttributeResult`) | Force every measurement in the system into one shape carrying scalar, method, extras, failure_modes. | Every module in `cnfa_algs/ARCHITECTURE.md`'s graph returns `AttributeResult`; a scalar can always be traced to its `method` string. |
| `cnfa_algs/` predicate modules | Measure cognitive code from image/plan evidence **or abstain with a named reason**. | Given an input the predicate cannot handle, `scalar is None` **and** `extras["reason"]` names the deficiency **and** `failure_modes` is non-empty. (See §7.4 — this is the behaviour a self-test currently punishes.) |
| `cnfa_algs/CONTRACT.md` | Define the last-mile: per-attribute, per-image, and adapter success conditions, plus a 4-level validation ladder (L0 smoke → L1 contract → L2 end-to-end → L3 backend). Includes an explicit §10 "Gaps (honest)". | The L0/L1 levels are declared to run *on any machine with no weights*; that claim is testable and is the first thing to check on a new machine. |
| `Image_Tagger_.../backend/science/pipeline.py` | Deliver a science payload to real users **now**, with heavier stages opt-in so the app stays responsive. | An upload returns a `SciencePayload` with `SCIENCE_SOURCE = "science_pipeline_v3.4"`; disabling optional stages measurably changes latency, not correctness of the enabled ones. |
| `model_intake_core/` | Give the 3D Model Intake Workbench a **stdlib-only, deterministic** foundation, and refuse to certify anything it cannot. | Every successful GLB report is `REVIEW_REQUIRED`; exit 0 = structurally acceptable *and still needs human review*, exit 2 = rejected. Readiness comes from an immutable profile-specific attestation, **never** from a mutable scene status. |
| `docs/validation/` (ledgers) | Keep validation claims and their challenges as **separate registers**: what was applied vs what was declared. | `validation_ledger.json` and the challenge ledger can disagree, and the disagreement is visible rather than reconciled away. |
| `governance.json` / `GOVERNANCE_REPORT.md` | Detect process failure, and state its own bounds. | Report footer reads "no violations detected means NOT-DETECTED-BY-V1-CHECKS, never compliance". |

## §4 — Where the data lives, and the traps in each store

| Store | What is in it | Trap |
|---|---|---|
| `corpus_L6/` | The calibration corpus: `manifest.csv`, `_provenance.csv`, and the subfolders `collections/`, `interiors/`, `materials/`, `nature_glass/`, `pairs/`. | **`.gitignore` blocks `corpus_L6/*` except `manifest.csv` and `_provenance.csv`.** A fresh clone has the manifest and none of the images. Code that reads the manifest will run and produce an empty or partial result rather than an error. **Images must be PNG** — the L5 cross-environment finding established that JPEG decode is platform-dependent, so a JPEG corpus makes cross-machine replay non-reproducible. |
| `Example Images/` | 16 files, mixed `.jpg`/`.webp`, human-collected. | These are *examples*, not the calibration corpus. They are the wrong input for any replay or calibration claim — mixed formats, and JPEGs (see above). |
| `structured3d/` | `Structured3D_annotation_3d.zip`, `Structured3D_bbox.zip`, `Structured3D_perspective_full_00.zip`, `_extract_tmp/`, `download_structured3d.sh`. | `.gitignore` blocks `structured3d/*.zip`. The download script is tracked; the data is not. |
| `docs/validation/` | 20 dated analysis/spec documents, plus `figures/`, `foyer_hitl/`, `review_pack/`, `studies/`, `coordination/`. `validation_ledger.json`, `VALIDATION_LEDGER_FORMAT.md`, `CHALLENGE_LEDGER_SPEC_2026-08-01.md`, `foyer_hitl/challenge_ledger.py`, `foyer_hitl/build_ledger.json`. | Documents are **dated in the filename** and supersede one another silently. Two manuscripts differ only by date (`..._2026-07-30.md` vs `..._2026-07-31.md`). Always sort by the date *in the name*, and check it against git, not against the mtime. |
| `docs/collections/` | `README_Image_Collections.md`, `DIRECTIONS_STEPHAN.md`, `DIRECTIONS_TANISHQ.md` — instructions to human collectors. | Untracked at the recorded HEAD. These describe how the corpus is *supposed* to be built; the corpus may not yet match. |
| `_control/cpp` (**sibling repo**) | The shared CPP `stage` library the socket runs on. Adopted, not vendored. | Not in this repo. Not in `VENDORED_DEPENDENCIES.md` (which covers only `image_decomposition/`, `low-level-image-features/`, `ImageDecomposer/`). The socket reaches it via **hard-coded absolute paths** — see §7.2. |
| `TRS_v1.1/`, `image_decomposition/`, `low-level-image-features/`, `ImageDecomposer/` | Reference material. `image_decomposition/` ← LMGEnvNeuro @ `01dff6f`; `low-level-image-features/` ← MPIB @ `71f11b8`; `ImageDecomposer/` ← local MATLAB, **no upstream**. | The repo `README.md` says plainly these are **reference only**. They contain working-looking code that is not on any live path. `ImageDecomposer/` has no upstream, so it cannot be re-fetched — treat as irreplaceable. |
| `_to_delete/` | Quarantine. Nothing here is live. | It is *quarantine*, not a graveyard: RULE 0 forbids deleting unique data, so material lands here instead of being removed. Do not read anything here as current, and do not empty it without authorisation. |
| `cnfa_external_collect/.venv/` | A checked-out virtualenv containing torch and friends. | It will dominate any recursive grep. Exclude it explicitly or your search results are noise. |
| `__pycache__/` throughout | Compiled bytecode. | The `.pyc` tags record **cpython-314** while the sandbox interpreter is **3.10.12**. That mismatch is a live signal that the authoring machine and the analysis machine are different environments — see §7.3. |

## §5 — Current state (VOLATILE — every figure carries its command)

All figures below were re-derived by execution at the recorded `HEAD`, in the environment named in
`MEASURED_ON`. Nothing here is transcribed from another document. Where a figure disagrees with an
older document, the older document is noted rather than silently corrected.

### 5.1 Repository

| Figure | Value | Command |
|---|---|---|
| HEAD | `084b3f3d93780f158c9aaa1188caa156f42f9bf4` | `git --no-optional-locks rev-parse HEAD` |
| Branch | `cnfa-algs-2026-07-14` | `git --no-optional-locks rev-parse --abbrev-ref HEAD` |
| HEAD date | `2026-08-02 19:31:19 +0000` | `git --no-optional-locks log -1 --format=%ad --date=iso` |
| HEAD subject | `untrack TRS_v1.1/.env (governance G5 triage: benign port/version config; env files do not belong in the index)` | `git --no-optional-locks log -1 --format=%s` |
| Commits, total | 135 | `git --no-optional-locks rev-list --count HEAD` |
| Commits, last 7d | 15 | `git --no-optional-locks rev-list --count --since='7 days ago' HEAD` |
| Commits, last 14d | 29 | `git --no-optional-locks rev-list --count --since='14 days ago' HEAD` |
| Tracked files | 18675 | `git --no-optional-locks ls-files \| wc -l` |
| Working-tree entries not clean | 26 → **29** (see below; both are correct, at different times) | `git --no-optional-locks status --porcelain \| wc -l` |
| Other branch | `main` @ `b7bbf8b4` | `git --no-optional-locks branch -v` |
| Remotes | `origin`, `old-image-tagger`, `tag-ucsd` | `git --no-optional-locks remote` |

At the first measurement, of the 26 unclean entries, 3 were modified (`CLAUDE.md`, `TASKS.md`,
`docs/validation/coordination/COWORK_LOG.md`) and 23 were untracked — including `governance.json`,
`GOVERNANCE_REPORT.md`, `model_intake_core/`, `docs/governance/`, `docs/collections/` and
`_to_delete/`. **Named, not counted**: the governance apparatus and the model-intake package are
currently *outside* version control. That is a §6 item, not a formatting nicety.

#### 5.1a The one figure in §5.1 that moved while this document was being written — and what a count could not tell me

Two later re-derivations of the same table, on the authoring machine, both report **29**, not 26. The
temptation is to overwrite `26` with `29` and move on. That would be the §10 clause-6 failure in
miniature: a fresher number written over an older one destroys the only thing that made the movement
legible. Both numbers are correct measurements of different moments; the *difference* is the finding.

A count alone cannot say whether a working tree moved because the repository changed or because the
act of documenting it added files to the tree being documented. So the third measurement was run with
names attached (`_control/hands/out_it_status.txt`, receipt `it-probe-status`, exit 0):

```
TOTAL 29  =  3 tracked-and-changed  +  26 untracked
  tracked and changed (3):
     M CLAUDE.md
     M TASKS.md
     M docs/validation/coordination/COWORK_LOG.md
```

The modified set is **identical, by name, to the set recorded above**. The entire delta is untracked:
23 → 26. And the current untracked list contains exactly three entries that are deliverables of the
program that produced this document:

- `docs/REPO_STATE_MODEL_AND_PLAN.md` — this file
- `scripts/refresh_state_model.py` — the refresher §10 requires
- `scripts/prevention/` — the freshness check and its falsification harness (§10)

Three added, three deliverables, and the modified set unchanged. That is a strong candidate
explanation and it is **not a proof**, because the 26-entry measurement was recorded as a bare count:
no name list survives from it, so I cannot rule out that some other untracked entry appeared and one
of these three predated the count. The honest statement is the bounded one: *the delta is +3 untracked
entries; three of the current untracked entries are this document's own deliverables; the identity of
the three added entries cannot be established from the evidence retained.*

I am leaving that gap visible rather than closing it with a plausible sentence, because it makes the
rule concrete for whoever reads this next: **the earlier measurement was unfalsifiable the moment it
was written down as a number instead of a list.** Every count in §5 that can carry names now carries
them. Where a future pass finds one that does not, that is a defect in this document, not a style
preference.

Also note what the tree is doing here: this document is being counted by the measurement it contains.
That is the fourth instance in one day of an instrument appearing inside its own sample (§7.11), and
it is the mildest of the four only because it was caught.

### 5.2 The predicate registry

Command for every row in this subsection:

```bash
PYTHONPATH=. python3 -c "
from annotation_socket.registry import PREDICATES, MODEL_VERSION
from collections import Counter
print(MODEL_VERSION); print(len(PREDICATES))
print(Counter(p['kind'] for p in PREDICATES))
print(Counter(p['tier_hint'] for p in PREDICATES))
print(Counter(p['audit_class'] for p in PREDICATES))"
```

| Figure | Value |
|---|---|
| `MODEL_VERSION` | `cnfa_algs-2026-07-19+seed1234+reliableA+reviewfix+codex2fix+codex3fix+m1prime+wave1+codexS0S2fix+clutterstack+cpart+faithfulV6V7+tax2+cc2m1p+taxfix+reliableAreconcile+wave2geomCC4` |
| Predicates registered | **68** |
| by `kind` | `image_attr` 40 · `plan_metric` 28 |
| by `tier_hint` (evidence **ceiling**) | `GREEN` 19 · `AMBER` 49 |
| by `audit_class` | `replayable` 18 · `replayable_tol` 50 |
| by `requires` | image-only 40 · plan-only 9 · needs additional declared inputs 19 |

Read the last row carefully, because it is the applicability fact that governs coverage: **for a bare
photograph with no plan and no declared inputs, exactly 40 of 68 predicates are applicable.** Nine more
become applicable once a plan is inferred (Tier B). The remaining 19 require inputs a photo cannot
supply — `seats`, `glazing`, `amenities`, `collab_sources`, `focus_seats`, `destinations`,
`acoustic_params`, `control_zones`, `territory_spec`, `air_spec`, `nature_cells`, `commons`,
`facade_spec`, `outdoor_leq` — and must ABSTAIN with the missing input named.

Names, not bare counts. The 19 predicates whose declared ceiling is GREEN:

`cnfa.light.brightness_variance`, `cnfa.fluency.edge_clarity_mean`,
`cnfa.fluency.symmetry_score_horizontal`, `cnfa.fluency.color_palette_entropy`,
`cnfa.fluency.processing_load_proxy`, `cnfa.fractal_dimension`, `glare-risk`,
`cnfa.light.warm_vs_cool_ratio`, `cnfa.cognitive.landmark_salience`, `C5.collaborator_proximity`,
`C6.path_overlap`, `C7.focus_speech_privacy`, `C8.distraction_distance`, `C9.view_equity`,
`C14.focus_collab_separation`, `C15.active_design`, `C16.territory`, `C17.local_control`,
`C18.air_quality`.

Note the shape of that list: the GREEN-capable image predicates are the *simple, defensible* ones
(brightness variance, edge clarity, symmetry, palette entropy), and the GREEN-capable plan metrics are
the ones fed by **declared** inputs (seats, glazing, acoustic parameters) rather than inferred ones.
Every predicate that depends on inferred Tier-B geometry is capped at AMBER by construction. That is
the design working, not a backlog.

Two registry entries carry explicit demotion notes in their `note` field, which are worth quoting
because they are the house style for honest labelling:

- `cnfa.fluency.fractal_mid_d_band` — *"V9 (AMBER per Fable F5) … R2 does NOT prove a valid scale range
  (checkerboard D=0,R2=1); response constants are engineering. Scaling validity + labeled calibration
  owed before GREEN."*
- `cnfa.fluency.spectral_slope_deviation` — *"V2 (AMBER + RENAMED per Fable F2) … This is NOT the 2-D
  Penacchio-Wilkins discomfort metric (radial averaging discards the 2-D Fourier-energy distribution)
  and does NOT use FOV (removed). Ship as a named spectral statistic only."*

### 5.3 The socket test suite, as it actually runs here

`pytest` is **not installed** in the measuring environment, so the suite was executed the way this
repo's `CLAUDE.md` prescribes — per file, by importing the module and invoking each `test_*` callable:

```bash
for f in annotation_socket/tests/test_*.py; do
  PYTHONPATH=. python3 -c "
import importlib.util,sys
spec=importlib.util.spec_from_file_location('t','$f')
m=importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(m)
except BaseException as e: print('COLLECT_ERROR',type(e).__name__,e); raise SystemExit(0)
fns=[n for n in dir(m) if n.startswith('test_') and callable(getattr(m,n))]
p=f_=0
for n in fns:
    try: getattr(m,n)(); p+=1
    except BaseException as e: f_+=1; print('FAIL',n,type(e).__name__,e)
print('pass',p,'fail',f_,'total',len(fns))"
done
```

| Test file | Result |
|---|---|
| `test_c01_triangulation.py` | 5 pass / 0 fail |
| `test_c29_stranded.py` | 3 pass / 0 fail |
| `test_cc3_layout_inputs.py` | **COLLECT ERROR** — `ModuleNotFoundError: No module named 'cpp'` |
| `test_codex_tax_fixes.py` | 3 pass / **1 fail** (`test_tax0_direct_invocation`) |
| `test_complexity_review_pack.py` | **COLLECT ERROR** — `ModuleNotFoundError: No module named 'pytest'` |
| `test_complexity_species.py` | **COLLECT ERROR** — `ModuleNotFoundError: No module named 'pytest'` |
| `test_f7_ridge_boundary.py` | 3 pass / 0 fail |
| `test_m1_prime.py` | 5 pass / **1 fail** (`test_operator_extract_bindings`) |
| `test_reliable_attrs.py` | 5 pass / 0 fail |
| `test_v9_fractal_band.py` | 3 pass / 0 fail |
| `test_wave2_geometry.py` | 4 pass / 0 fail |

**Totals: 11 files · 8 collected · 3 uncollectable · 33 tests collected · 31 pass · 2 fail.**

`docs/PROGRAM_STATE_AND_DIRECTION_2026-08-01.md` records "Socket suite: 33 pass / 4 fail, the 4 a
hard-coded Linux fixture path (not a logic defect)". The collected-test count agrees (33). The rest
does not, and the difference matters:

- **`test_cc3_layout_inputs.py` — the hard-coded-path failure, correctly diagnosed but misdescribed.**
  With `_control` added to `PYTHONPATH` the failure advances to
  `FileNotFoundError: '/Users/davidusa/REPOS/_control/supervisor/trusted_derivation.py'`. The path is
  hard-coded and **absolute to David's Mac**, not "a Linux fixture path". On any other machine — a CI
  runner, a collaborator's laptop, the Cowork sandbox mount — it cannot resolve.
  *Command:* `PYTHONPATH=.:../\_control python3 -c "import annotation_socket.tests.test_cc3_layout_inputs"`.

- **`test_m1_prime.py::test_operator_extract_bindings` — a missing optional dependency.**
  `ModuleNotFoundError: No module named 'scipy'`. Environment, not logic.

- **`test_codex_tax_fixes.py::test_tax0_direct_invocation` — NOT a path failure, and worth reading
  closely.** It shells out to run `cnfa_algs/wave2_geometry.py` directly; that module's `__main__`
  self-test fails at line 565 on `assert bl_L.scalar is not None and bl_S.scalar is not None`. The root
  cause, traced by execution: `blind_corner_index` needs `skimage.morphology.skeletonize`, and when
  skimage is unavailable it returns `scalar=None`, `extras={"reason": "skimage_unavailable"}`, and
  `failure_modes=["blind-corner walk needs a morphological skeleton (skimage dependency)"]`
  (`cnfa_algs/wave2_geometry.py:270-276`).
  **The predicate is behaving exactly as the contract demands — it abstains, with the missing input
  named. The self-test is the thing that is wrong: it asserts a SCORED outcome in a situation where the
  contract requires ABSTAINED.** See §7.4; this is the most instructive defect currently in the repo.

So the honest statement of test state is: *31 of 33 collected tests pass at HEAD `084b3f3d9` in an
environment lacking skimage, scipy and pytest; 3 further test files cannot be collected at all in that
environment; of the 2 failures, one is a missing optional dependency and one is a self-test that
forbids a legitimate abstention.* No claim is made about the state on David's Mac (python 3.14, deps
present) — that is a different environment and would need its own run. **A verdict certifies only the
interval and environment it examined.**

### 5.3b The same commit, measured on the authoring machine — and why the two disagree

The sentence directly above ("no claim is made about the state on David's Mac — that is a different
environment and would need its own run") was written as a caveat. It has since been given its own
run, natively on the Mac through the `fable_hands` daemon, at the same HEAD, with the same loop.
The result is the most instructive thing in this document, so it is recorded rather than merged.

| | Linux VM (§5.3, and the header's `MEASURED_ON`) | macOS, authoring machine |
|---|---|---|
| Interpreter | `3.10.12`, `/usr/bin/python3` | `3.14.2`, `/opt/homebrew/opt/python@3.14/bin/python3.14` |
| `skimage` / `scipy` / `pytest` | **absent / absent / absent** | present / present / present |
| Files collected | 8 of 11 (**3 uncollectable**) | **11 of 11** (0 uncollectable) |
| Tests collected | 33 | 55 |
| Pass | 31 | 49 |
| Fail | 2 | 6 |
| Failures attributable to the repository | **1** | **0** |

*Command:* identical per-file loop, printed in §5.3. *Probe that decomposed the six:*
`python3 _control/hands/probe_tests.py <repo>` — output in `_control/hands/out_it_probe.txt`.

**The six macOS "failures" are not failures.** All six raise
`TypeError: … missing 1 required positional argument: 'tmp_path'`. Their signatures are
`test_x(tmp_path: 'Path')` — they are pytest tests taking the `tmp_path` fixture, and this repo's
prescribed no-pytest loop calls them with no arguments. They are five tests in
`test_complexity_review_pack.py` and one (`test_handoff_is_deterministic_and_hashes_match`) in
`test_complexity_species.py`. **The measuring instrument's own incapacity is being rendered as the
subject's failure.** In the Linux VM the same six were invisible, because without `pytest`
importable the files did not collect at all — the instrument was silent about its own blind spot
rather than loud about it, which is worse.

**And the failure that matters vanished.** On the Mac, `test_tax0_direct_invocation` **passes**, and
prints ``TAX-0: direct `python3 cnfa_algs/<file>.py` runs  OK``. So does
`test_operator_extract_bindings` (scipy present), and `test_cc3_layout_inputs.py` collects and passes
4/4. Every one of the Linux failures is green here.

That is not good news. `blind_corner_index` abstains **only when skimage is missing**. On a machine
where skimage is installed the predicate never abstains, the assertion at
`cnfa_algs/wave2_geometry.py:565` never fires, and the self-test that forbids a legitimate abstention
reports OK. Stated generally, and this belongs in §7:

> **A self-test suite exercised only in a fully-provisioned environment cannot execute any abstention
> path — so the better-equipped the machine, the blinder the governance tests run on it.** The
> abstention contract is this repo's central claim, and the only environment that tests it is the
> deprived one.

Compose that with §5.5 and the trap closes on itself: the audit spine is bound by hard-coded absolute
paths to the authoring machine, and the authoring machine is precisely the environment in which the
spine's own governance defect cannot be observed. **The machine that is able to run the audit is the
machine that is unable to see the defect.** That is why Phase A (§6) blocks everything else.

**The honest joint statement,** which is neither of the two rows above: *at HEAD `084b3f3d9`, 49 of
55 socket tests pass on macOS/3.14 with all optional dependencies present and 6 are not executable
under the no-pytest loop; 31 of 33 pass on Linux/3.10 without skimage, scipy or pytest, where 3 files
do not collect; exactly one test failure in either environment reflects a defect in the repository
(`test_tax0_direct_invocation`), and it is observable only in the environment lacking skimage.*

### 5.4 Environment

| Figure | Value | Command |
|---|---|---|
| Interpreter | `Python 3.10.12` (`/usr/bin/python3`) | `python3 -V` |
| `numpy` | present | `python3 -c "import numpy"` |
| `cv2` | present | `python3 -c "import cv2"` |
| `PIL` | present | `python3 -c "import PIL"` |
| `skimage` | **ABSENT** | `python3 -c "import skimage"` |
| `scipy` | **ABSENT** | `python3 -c "import scipy"` |
| `pytest` | **ABSENT** | `python3 -c "import pytest"` |
| Authoring interpreter (inferred) | `cpython-314` | `ls annotation_socket/__pycache__/` |

The last row was an inference from `.pyc` tags when this document was first written. It has since
been **confirmed by execution** rather than left as an inference — the authoring machine reports
`Python 3.14.2` on `darwin` at `/opt/homebrew/opt/python@3.14/bin/python3.14`, with `numpy`, `cv2`,
`PIL`, `skimage`, `scipy` and `pytest` all present (`_control/hands/out_it_probe.txt`). An inference
that survives execution should be relabelled as measured; an inference that does not should be
deleted rather than softened.

### 5.5 Portability

| Figure | Value | Command |
|---|---|---|
| Tracked `.py` files hard-coding `/Users/davidusa` | **13** | `grep -rln "/Users/davidusa" --include=*.py . \| grep -v _to_delete \| grep -v "\.venv" \| wc -l` |

Named: `annotation_socket/controller.py`, `run_stage.py`, `derivation.py`, `annotator.py`,
`controller_drive.py`, `verify.py`, `__init__.py`, `tests/test_codex_tax_fixes.py`,
`viz/field_sidecars.py`, `viz/function_inspector.py`, `viz/layered_viewer.py`,
`scripts/reference_clutter_compare.py`, `scripts/m1p_cross_env_replay.py`.

**Eight** of those thirteen are in `annotation_socket/` (`__init__.py`, `annotator.py`,
`controller.py`, `controller_drive.py`, `derivation.py`, `run_stage.py`, `verify.py`, and
`tests/test_codex_tax_fixes.py`) — i.e. **the audit spine itself is machine-bound.** An audit
apparatus that only runs on the machine of the person being audited is not yet an audit apparatus.
This is §6 Phase A. *(An earlier revision of this line said "seven"; the count of names in the same
paragraph was thirteen and the count under `annotation_socket/` was eight. A bare count and a name
list in adjacent sentences disagreed, which is the exact failure the "names, never bare counts" rule
exists to make impossible. Recount from names; never carry a count forward by hand.)*

**This figure has a documented excursion, and it is worth more than the figure.** Between two runs
of the refresher it read **14**, then **13** again. Nothing in the repository changed. The 14th entry
was `scripts/prevention/falsify_state_model_freshness.py` — a deliverable written *for this document*,
whose argument is that an audit apparatus must be executable off the author's machine, and which
resolved its own paths from a default containing that same absolute path. The harness became an
instance of the thing it measured, inside the measurement that reports it. Fixed by deriving all
paths from `__file__`; the harness now carries `SCENARIO 6`, which greps its own source for the
needle and fails the run if it finds it. Differential on record:
`_control/hands/out_it_refresh_check.txt` (14, naming the harness) →
`_control/hands/out_it_refresh_check2.txt` (13, harness absent).

### 5.6 Governance

| Figure | Value | Command |
|---|---|---|
| Tier | `full`, `canonical: true` | `cat governance.json` |
| Findings | 6 | `cat GOVERNANCE_REPORT.md` |
| RED | 2 × G4, both `rm -rf` in `Image_Tagger_3.4.74_.../infra/cloud/full_stack_vm_setup.sh` and `install_cognitive_code.sh` | `cat GOVERNANCE_REPORT.md` |
| AMBER | 4 × G6 bare-path findings in handoff docs | `cat GOVERNANCE_REPORT.md` |

The report's own footer states the bound: *"no violations detected means NOT-DETECTED-BY-V1-CHECKS,
never compliance."* Reproduce that framing anywhere you quote the result.

### 5.7 Standing status from repo documents (NOT re-derived — flagged as such)

These are claims made by documents in the repo that I did **not** re-execute. They are listed here so
you know they exist and know they are unverified at this HEAD, not so you can cite them as current.

- `annotation_socket/SOCKET_CONFORMANCE.md` records a 2026-07-15 run: GREEN 0 / AMBER 3 / RED 0, 19/19
  applicable predicates scored, 18 abstained, 0 unknown, negative control RED, 6/6 CPP conformance
  checks passing. Its own §4 says: *"I built both the annotator and verify(); this document is
  builder-run evidence, NOT certification."* **That self-assessment is the correct one. The socket sits
  AMBER pending a ≠-mind certification run.**
- `annotation_socket/controller.py`'s docstring records a CPP ABI integration finding
  (`unit["unit_id"]` vs `unit["id"]`) and a dual-key temporary bridge, marked **UNRUN**.
- `TASKS.md` (stamped "Last updated: 2026-07-19 late") is the live queue: Sprint COMP-CORRECT rows
  CC-1…CC-10, Sprint VIEW (VIEW-3 DONE, VIEW-4, VIEW-5), Sprint NEW-ATTR legibility, ENV-PHYSICS rows
  ACO-1 and LUM-1, and a DAVID-only block (DK-1 corpus export gating all of L6, DK-4 recurring push).
- **New_VR_Platform seam (recorded 2026-08-12, read from the platform repo — NOT re-derived here).** The
  `New_VR_Platform` repository added a two-layer *attribute charter* on branch `vr-impl/perception-lane`
  that formally makes this tagger its measurement instrument. It splits attributes into a **structural**
  layer (architectural facts that define a VR model's semantic spec, validated by a
  build→re-shoot→compare *design cycle*) and a **proximal** layer (perceptual constructs), and it names two
  jobs for this repo: a *structural extractor* emitting a room's elements to the platform's `room-v0.3`
  vocabulary, and *witness-3*, the measurement-on-renders leg that may corroborate a scientific claim. The
  platform enforces, in code and fail-closed, that our **GREEN/AMBER tiers are consumed as
  measurement-faithfulness only** — a GREEN measure is never a validated cause and cannot be a confirmatory
  witness until the platform's own calibration gate promotes it. The agreed interface is a single
  machine-readable `measure_registry.json` this repo will author (canonical `cnfa.*` keys, per-measure
  tier / determinism / licence / faithfulness) and the platform will pin by content hash. **Platform side:
  built and independently reviewed. This repo's side (the extractor and the registry): specified and
  agreed, not yet built.** Source: the platform's `constraints/attribute_charter.json`,
  `src/vr_condition_audit/attribute_map.py`, and `docs/ATTRIBUTE_ARCHITECTURE_AND_DIVISION_OF_LABOR.md`.
  When this repo builds its side, the registry and extractor become §5-measurable here.

## §6 — The plan to green

"Green" here means one specific thing: **the socket's verdicts are certifiable by someone who did not
build it, on a machine that is not David's.** Everything below is ordered by what unblocks what.

### Phase A — make the audit spine machine-independent *(blocks everything else)*

The 13 hard-coded `/Users/davidusa` paths (§5.5) must become resolution through an environment
variable or a discovery function with a declared fallback, failing **closed** with a clear message when
the CPP library is genuinely absent. Success condition: `test_cc3_layout_inputs.py` collects and runs
on a machine that has never seen `/Users/davidusa`. This is Phase A because a ≠-mind cannot certify
what a ≠-mind cannot execute.

### Phase B — declare the dependency surface honestly

There is no requirements file governing the socket, and three of its optional dependencies (`skimage`,
`scipy`, `pytest`) silently change the test tally. Success condition: a declared dependency manifest
distinguishing **required** from **optional-with-declared-degradation**, plus a startup probe that
prints which optional capabilities are live. A predicate that abstains because skimage is missing is
correct; a *suite* that cannot tell you that is why it abstained is not.

### Phase C — fix the self-tests that forbid legitimate abstention

`cnfa_algs/wave2_geometry.py:565` is the known instance (§5.3, §7.4). The fix is not to install skimage;
it is to make the self-test assert the **contract** — either a scalar, or an abstention carrying
`extras["reason"]` and a non-empty `failure_modes` — and to assert the ordering claim
(`bl_L > bl_S`) only in the branch where both scored. Then audit the other module self-tests for the
same pattern, because it will not be the only one.

### Phase D — the ≠-mind certification run

Only after A–C. An independent reviewer, on their own machine, runs the socket end-to-end against a
PNG corpus subset and the negative control, and issues a verdict **bound to a commit and an
environment**. Until this lands, `SOCKET_CONFORMANCE.md` remains builder-run evidence and the socket
remains AMBER. Do not let a clean self-run be mistaken for this.

### Phase E — connect Engine A to Engine B

Make the research core the canonical science-run inside the app (§2), behind the tri-state contract, so
what ships is what was audited. This is last on purpose: promoting an uncertified engine into
production is how a research artefact becomes a confident wrong answer at scale.

### Phase F — bring the governance apparatus under version control

`governance.json`, `GOVERNANCE_REPORT.md`, `docs/governance/` and `model_intake_core/` are untracked at
HEAD (§5.1). Track them with named paths — **never `git add -A`** — and triage the 2 RED G4 findings.

Running alongside all of the above: **DK-1**, the PNG corpus export, which gates every L6 calibration
claim and is not a software task.

## §7 — Mistakes a newcomer will make

Every entry below is a failure that has actually happened, in this repo, to someone. Nothing here is
hypothetical.

### 7.1 Editing the wrong engine

You are asked to "improve the tagger's attributes". You open the app, find
`backend/science/pipeline.py`, and edit it. Or you open `cnfa_algs/` and edit that. **Either way you
have a 50% chance of editing an engine that has nothing to do with the outcome you were asked to
change**, because the two are not connected (§2). Before touching anything, establish which engine the
request is about. If the request mentions predicates, registry, abstention, tiers, M1′ or verification,
it is Engine A. If it mentions upload, payload, OneFormer, latency or the front end, it is Engine B.

### 7.2 Assuming the repo is self-contained

The socket imports the CPP `stage` library from a **sibling repository** by hard-coded absolute Mac
path. A clean clone of this repo alone cannot run the socket. This is not documented in
`VENDORED_DEPENDENCIES.md`, which covers only the three vendored reference trees.

### 7.3 Trusting a clean clone to carry the repo's rules

`.gitignore` blocks `CLAUDE.md`, `AGENTS.md`, `*PROMPT*.md`, `*prompt*.md`, `AI_*.md`, `*LLM*.md`. The
file containing the Cross-AI Artifact Contract, the standing "never `git add -A`" rule, the L5
PNG-only finding, the `[PORT]`-gated Rosenholtz constants and the sandbox git procedure **is not in
the repository**. A newcomer who clones and starts work is working without the rules and does not know
it. If you are an AI reading this on a fresh clone: `CLAUDE.md` exists on David's disk. Ask for it.

### 7.4 Reading an abstention as a failure

`blind_corner_index` returning `None` when skimage is absent is the system **working**. The socket's
entire thesis is that a measurement which cannot be made must say so, with the missing input named.
The reflex to "fix" that by making it return a number — or by installing the dependency and moving on
without noticing that the *self-test* forbade the abstention — is precisely the substitution this repo
exists to prevent. Read `extras["reason"]` and `failure_modes` before concluding anything is broken.

### 7.5 Running `git status` without `--no-optional-locks`

Per `CLAUDE.md`: the Cowork sandbox mount blocks `unlink` but permits `rename`, and **`git status`
itself leaves an `index.lock` behind**. A stale lock blocks David's native commits afterwards. Always
`git --no-optional-locks status`. If a lock exists, `mv` it into `_to_delete/` (never force-delete
without checking it is zero-byte and unheld). Verify afterwards: `ls -la .git/*.lock`.

### 7.6 Deleting anything

RULE 0: never delete or overwrite unique or expensive data without proof and human authorisation.
Quarantine into `_to_delete/` instead. Note also that the sandbox **cannot** delete — `rm` fails with
"Operation not permitted" — so the correct move and the only available move happen to coincide.

### 7.7 Grabbing the newest-looking document

Documents here are dated in the filename and supersede each other silently.
`docs/PROGRAM_STATE_AND_DIRECTION_2026-08-01.md` supersedes the master-status chain but `TASKS.md` is
stamped 2026-07-19, so the *older* file is the authoritative live queue while the *newer* one is the
authoritative narrative. Neither one tells you that. Also: mtimes on the mount reflect the mount, not
authorship — sort by the date in the name and confirm against `git log`.

### 7.8 Working in the wrong repository entirely

There is a sibling directory `image-tagger` whose files date from April. It looks like this project.
It is not. The canonical repository is `Image_Tagger_dk_latest` — confirmed by
`governance.json: {"tier":"full","canonical":true}` and by a HEAD dated 2026-08-02. Check
`governance.json` before you start, every time.

### 7.9 Quoting a corpus result without checking the corpus is there

`corpus_L6/*` is gitignored except two CSVs. Code that reads `manifest.csv` will happily run against
zero images and report a clean result over an empty set. A "pass" on an empty corpus is the purest
form of the failure this repo is about.

### 7.10 Concluding the suite is green because it is green on a well-equipped machine

This one happened on 2026-08-03 and is fully recorded in §5.3b. The same commit was measured on two
machines twenty minutes apart. On the machine with every optional dependency installed, **every
failure that reflects an actual defect disappeared** — because the defect is in a self-test that
forbids an abstention, and a fully-provisioned environment never triggers the abstention. The
green run was not evidence that the repo is healthy; it was evidence that the environment was too
rich to test the thing this repo exists to guarantee.

The corollary a newcomer needs: **if you have skimage, scipy and pytest installed, your test run
cannot see the abstention defects, and abstention is the whole product.** Before you report a suite
result here, say which optional dependencies were importable. A tally without that is not a
measurement of the repo, it is a measurement of your laptop.

The mirror-image error, from the same pair of runs: on the well-equipped machine the loop reported
6 failures that are *not* failures at all — pytest tests taking a `tmp_path` fixture, invoked by a
loop that supplies no fixtures. Do not fix the repo to satisfy the harness. Check the signature
first (`inspect.signature`), which is what `_control/hands/probe_tests.py` does.

### 7.11 Letting a measuring instrument see itself

Four times in one day, in tooling written *for this document*: a "read-only" refresher that wrote a
scratch file into the repo whose cleanliness it was counting; a grep that counted its own source
because the search string was a literal in it; a portability harness that failed the portability
metric it exists to defend (§5.5); and this document itself, which is one of the untracked entries in
the working-tree count it publishes (§5.1a). None of the first three was visible by reading the code.
Each took one run.

The fourth is the interesting one, because it is the only one that cannot be fixed. The refresher can
stop writing scratch files; the grep can exclude itself; the harness can derive its paths from
`__file__`. But a state-of-the-repo document that reports how many uncommitted files the repo has will
always be one of them until it is committed, and committing it changes the number it reports. There is
no position from which this measurement is clean. The available move is not to eliminate the effect
but to **declare it**: say which of the counted entries are the measurement's own, and let the reader
subtract. §5.1a does that.

**Whenever a measurement can see itself, the number it reports is partly about the measurement.**
Before trusting any repo-wide count here, ask whether the counter is inside the counted set — this
repo's tooling greps its own tree by default, so the answer is usually yes. Where the answer is yes
and cannot be made no, the count must ship with the names of the self-referential entries; a bare
number in that situation is not a measurement, it is an accident waiting to be quoted.

## §8 — How to verify anything here

**The rule: execute, do not inspect.** Reading a function and concluding it works is the single most
common failure mode in this codebase's history.

Establish where you are:

```bash
cat governance.json                                  # canonical:true, or you are in the wrong repo
git --no-optional-locks rev-parse HEAD               # bind every claim you make to this
git --no-optional-locks status --porcelain | wc -l   # know what is uncommitted before you judge state
ls -la .git/*.lock                                   # must print nothing
```

Establish what your environment can actually do, before believing any test result:

```bash
python3 -V
for m in numpy cv2 PIL skimage scipy pytest; do
  python3 -c "import $m" 2>/dev/null && echo "$m yes" || echo "$m NO"
done
```

Re-derive the registry rather than quoting it:

```bash
PYTHONPATH=. python3 -c "
from annotation_socket.registry import PREDICATES
for p in PREDICATES:
    print(p['id'], p['kind'], p['tier_hint'], p['audit_class'],
          sorted(p['requires']) or 'image-only')"
```

Run the tests the way this repo runs them (per file; pytest may be absent) — the loop is in §5.3.

**Verify the verifier with the negative control.** A verification suite that has never been shown to
fail has not been shown to do anything:

- tamper with a stored derivation and confirm the verdict is **RED**, not a warning;
- confirm a predicate denied its required input returns ABSTAINED **with the missing input named**,
  not a default value;
- confirm the registry's tier ceiling holds — a Tier-B-geometry predicate must not be able to emit
  GREEN.

`cnfa_algs/CONTRACT.md` §8 defines the ladder: L0 smoke and L1 contract conformance are declared to run
on any machine with no weights; L2 needs a reference image; L3 needs the backend running. Start at L0
and do not skip upward.

Finally: **state the interval of every claim.** "The socket passes" is not a statement. "31 of 33
collected tests passed at `084b3f3d9` under python 3.10.12 without skimage/scipy/pytest, with 3 files
uncollectable" is.

## §9 — The companion human introduction

This document is written for a machine that has to act. A human arriving cold needs something
different, and it should be a **separate document** — `docs/README_HUMAN_INTRODUCTION.md` — because
merging the two produces a file that serves neither.

It should be one sitting's reading and should cover, in prose: what cognitive code is and why anyone
would want to measure it; the worked example of a single photograph becoming one predicate value, with
the abstention case shown as prominently as the success case; why the system says "I don't know" so
often and why that is the product rather than a limitation; the two-engine situation stated plainly in
one paragraph so nobody has to discover it; who to ask about what (David: research direction, corpus,
taxonomy sign-off, assembly priors — the code cannot answer those); and an explicit statement of what
this system does *not* do, which is certify anything about a real building.

It should **not** contain: figures that live in §5 (they will rot at a different rate and the human
document has no refresher), file inventories, or task tables. Where it needs a current number it should
say "see §5 of `REPO_STATE_MODEL_AND_PLAN.md`" and stop.

## §10 — Freshness contract

This document is a state model. **A state model without a freshness mechanism recreates the exact
problem it was written to prevent, one document later** — it becomes a confident, authoritative,
out-of-date account that a newcomer trusts precisely because it is well-organised.

The contract:

1. **§5 is stale after `STALE_AFTER_DAYS` (7) — but only if the repository moved.** A document that is
   nine days old describing a repository that has not received a commit in nine days is not stale; it
   is accurate. Age alone is not the trigger. Age *plus* commits since the recorded HEAD is.

2. **The recorded `HEAD` must be reachable in current history.** If it is not — rebase, reset,
   force-push, branch switch — this document describes a history that no longer exists and is
   **invalid**, not merely stale. That is a harder failure than age and is reported separately.

3. **`MEASURED_ON` binds §5's environment-dependent figures.** If your environment's optional-dependency
   set differs from the one in the header, §5.3's test tallies do not apply to you and must be
   re-derived before you cite them. This is not pedantry: the difference between "31/33 pass" and
   "33/33 pass" in this repo is entirely an artefact of which optional packages are importable.

4. **The refresher refuses to stamp a timestamp it did not earn.** `scripts/refresh_state_model.py`
   rewrites the header **only** if a quorum of its measurements actually returned values. If
   measurements fail, it writes `STATE_AS_OF: FAILED-<utc>` and exits non-zero rather than recording a
   fresh-looking timestamp over a failed run. A freshness timestamp that can be earned without
   verifying anything is a proxy for verification, and proxies get optimised for.

5. **The freshness check has a positive control for *each* failing condition and a negative control.**
   A check that has only ever been observed passing has not been observed working. Both AGE and DRIFT
   are exercised on synthetic inputs at every run; if either control fails to fire — or the negative
   control fires — the check exits non-zero on the grounds that it cannot vouch for itself.

6. **§5 prose is not machine-rewritten, deliberately.** The refresher re-derives the figures and prints
   a diff against what is written; a human or an agent must reconcile it. Auto-rewriting §5 would
   silently discard the *interpretation* around each number — the notes about which failure is a
   dependency and which is a contract violation — and that interpretation is the part with the value.
   The cost is that §5 can drift from its own refresher output; the mitigation is that the refresher
   prints the drift loudly rather than papering over it.

   **This clause was an argument when it was written. It is now an experiment with a result.** Run
   on the authoring machine, the refresher derives `55 collected, 49 pass, 6 fail`. An auto-rewriter
   would have replaced §5.3's line with that and, in the same stroke, deleted the paragraph
   explaining that `test_tax0_direct_invocation` fails because a self-test forbids a legitimate
   abstention — the single most important sentence in §5 — because on that machine it does not fail.
   The number would have moved in the approved direction (2 fails → 0 real fails) while the meaning
   inverted, and no human would have been obliged to read anything. **The moment a metric improves is
   the moment its interpretation is most likely to be discarded, and an auto-rewriter is a machine
   for doing that at scale.** See §5.3b.

7. **What is still missing, stated plainly rather than left for a reader to notice.** Clause 6
   protects the prose from the generator but leaves it unprotected from time: §5's sentences can
   drift from the refresher's output indefinitely and *nothing fails*. The refresher prints the
   drift; a human must notice. That is principal vigilance doing load-bearing work, which is the
   arrangement this whole programme declines to trust everywhere else.

   The fix is neither auto-rewrite nor refuse-to-touch. It is to **make the drift a failing check**:
   have the refresher emit a machine-readable sidecar of every derived figure, and have the
   *freshness check* exit non-zero when the sidecar disagrees with what §5 asserts. The prose stays
   hand-written; the disagreement is caught mechanically. **The sidecar must be keyed by environment
   fingerprint, not by commit alone** — §5.3b is the proof: two sidecars at the same commit with
   different dependency sets legitimately disagree, and a reconciliation check that did not know
   that would fire constantly and be switched off within a week. This is not implemented here, and
   it is not implemented in the Article_Eater reference either. It is the top item for the next pass.

**How to refresh:**

```bash
python3 scripts/refresh_state_model.py            # re-derives §5 by execution, rewrites the header
python3 scripts/prevention/state_model_freshness_check.py    # exits non-zero when this doc is stale/invalid
```

Exit codes for the freshness check: `0` fresh · `1` stale (AGE, and the repo moved) · `2` invalid
(DRIFT — recorded HEAD not in current history) · `3` header unparseable or absent · `4` a positive
control failed to fire · `5` the negative control fired.

---

*A verdict certifies only the commit and the environment it examined. Every claim in §5 is bound to
HEAD `084b3f3d9` and to the interpreter and dependency set named in the header — and to nothing else.*
