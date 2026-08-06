# CPP consumer boundary — Image_Tagger (CLAUDE-M1-BUILD, 2026-08-06)

**Author:** claude-term-1
**Worktree:** `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1`
**Branch:** `codex/claude-m1-portable-cpp-2026-08` (base `49fac5033bcc3ba05c69e4bde9b29a794a6cc00a`)
**Charge:** `/Users/davidusa/REPOS/_control/prompts/claude-m1/CLAUDE_M1_BUILD_CHARGE_2026-08-06.md`
**Status:** BUILT AND SELF-RUN. **Not certified.** The author of a repair may not clear it; CODEX-CONTROL
or another independent reviewer attacks this commit before adoption.

## Absolute-path manifest (every file this document names, verified to exist 2026-08-06)

Written or modified by this charge:

- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/annotation_socket/_cpp_bootstrap.py` (new)
- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/annotation_socket/annotator.py`
- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/annotation_socket/verify.py`
- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/annotation_socket/controller_drive.py`
- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/annotation_socket/run_stage.py`
- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/annotation_socket/controller.py`
- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/annotation_socket/derivation.py`
- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/annotation_socket/tests/test_cpp_bootstrap.py` (new)
- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/contracts/cross_repo/IMAGE_TAGGER_CPP_INTERFACE_V1.json` (new)
- `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/docs/CPP_CONSUMER_BOUNDARY_2026-08-06.md` (this file)

Read-only inputs (NOT modified; they live OUTSIDE this repository, under the `/Users/davidusa/REPOS/` parent):

- `/Users/davidusa/REPOS/_control/cpp/locate.py`
- `/Users/davidusa/REPOS/_control/cpp/stage.py`
- `/Users/davidusa/REPOS/_control/cpp/README.md`
- `/Users/davidusa/REPOS/_control/cpp/conformance.py`
- `/Users/davidusa/REPOS/_control/supervisor/trusted_derivation.py`
- `/Users/davidusa/REPOS/_control/supervisor/supervisor.py`
- `/Users/davidusa/REPOS/_control/status/canon/recovery_2026-08/M1_image_tagger_cpp/M1_IMAGE_TAGGER_CPP_2026-08-05.md`
- `/Users/davidusa/REPOS/Article_Eater_PostQuinean_v1_recovery/contracts/cross_repo/AE_REPO_INTERFACE_V2.json`

*Inside this document, a bare path such as `annotation_socket/verify.py` is relative to the worktree root
`/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1`.*

---

## 1. The defect, re-verified from source rather than accepted from the diagnosis

Fable's M1 report is a diagnosis; Fable therefore cannot countersign this repair, and I did not implement from
it. I re-ran the census against the live tree first. Literal output, before any edit:

```
$ grep -rn --include='*.py' -e '/home/claude' -e '/Users/davidusa' annotation_socket/
annotation_socket/run_stage.py:18:sys.path.insert(0, "/home/claude/_control_deps")
annotation_socket/run_stage.py:19:sys.path.insert(0, "/Users/davidusa/REPOS/_control")
annotation_socket/controller.py:26:sys.path.insert(0, "/Users/davidusa/REPOS/_control")
annotation_socket/derivation.py:26:sys.path.insert(0, "/home/claude/_control_deps/supervisor")
annotation_socket/derivation.py:30:    sys.path.insert(0, "/Users/davidusa/REPOS/_control/supervisor")
annotation_socket/controller_drive.py:28:os.environ.setdefault("CONTROL_ROOT", "/home/claude/_control_deps"
annotation_socket/controller_drive.py:29:                      if Path("/home/claude/_control_deps").exists()
annotation_socket/controller_drive.py:30:                      else "/Users/davidusa/REPOS/_control")
annotation_socket/controller_drive.py:47:    code = ("import sys, json; sys.path.insert(0, '/home/claude'); "
annotation_socket/verify.py:35:sys.path.insert(0, "/home/claude/_control_deps")
annotation_socket/verify.py:36:sys.path.insert(0, "/Users/davidusa/REPOS/_control")
annotation_socket/annotator.py:19:sys.path.insert(0, "/home/claude/_control_deps")     # cpp library (sandbox vendored copy)
annotation_socket/annotator.py:20:sys.path.insert(0, "/home/claude")                    # cnfa_algs
annotation_socket/annotator.py:21:sys.path.insert(0, "/Users/davidusa/REPOS/_control")  # cpp library (Mac path)
```

Confirmed, and one correction to the diagnosis worth recording: the report describes
`controller_drive.py:28` as defaulting `CONTROL_ROOT` to the container path `/home/claude/_control_deps`
unconditionally. In the tree as it actually stands, that default is already guarded by an `.exists()` check
and falls back to the Mac path, so it is not a live break on this machine. What *is* real in every module is
the class of defect: a host user's path and a container sandbox's path compiled into committed source, with
resolution logic re-implemented six times and one silent fallback that invents a trust sentinel. That is what
this charge repairs.

Also verified independently (these bound what the new contract may claim):

```
$ ls /Users/davidusa/REPOS/_control/cpp/pyproject.toml /Users/davidusa/REPOS/_control/pyproject.toml
ls: /Users/davidusa/REPOS/_control/cpp/pyproject.toml: No such file or directory
ls: /Users/davidusa/REPOS/_control/pyproject.toml: No such file or directory

$ python3 -c "import importlib.util as u; print('cpp:', u.find_spec('cpp')); print('cnfa_cpp:', u.find_spec('cnfa_cpp'))"
cpp: None
cnfa_cpp: None
```

So there is **no `cnfa-cpp` package and no pin to make**. Article_Eater's
`AE_REPO_INTERFACE_V2.json` declares `cnfa_cpp.stage.v1` with `provider_contract: pyproject.toml` and
`provider_commit: f882af95…`; that provider contract file does not exist in the provider checkout observed
here. This repository therefore declares the local bootstrap state and describes the pinned-package state as
a target, and claims no pin.

---

## 2. What was built

### 2.1 One fail-closed resolution point

`annotation_socket/_cpp_bootstrap.py` is now the only place this repository resolves anything external. Its
resolution order, in precedence order, each clause covered by a test:

| # | Mode | Rule |
|---|------|------|
| 1 | `packaged` | `import cpp` already resolves (installed distribution or embedder-supplied). Wins outright, and we then perform **no** `sys.path` mutation at all. |
| 2 | `control_root_env` | An explicit `CONTROL_ROOT`. Honored **strictly**: when set it is the *only* candidate. A wrong value fails loudly; it never falls through to a guess. |
| 3 | `derived_local` | A bounded ancestor scan: `<ancestor>/_control` and `<ancestor>/_control_deps`, nearest ancestor first, at most 6 levels above this checkout and above the cwd. Derived at run time from `__file__`; no user, host, or container path is written down. |
| 4 | `unresolved` | One `CppBootstrapError` naming the missing contract, the root and source tried, every candidate searched, and three remedies. |

A candidate is accepted on **content** (`cpp/locate.py` and `cpp/stage.py` are real files), never on directory
existence — the RULE 0 discipline applied to path resolution.

Observed on this machine (`python3 -m annotation_socket._cpp_bootstrap`):

```
"resolution": {
  "cpp_mode": "derived_local",
  "control_root": "/Users/davidusa/REPOS/_control",
  "root_source": "derived",
  "searched": [
    "/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/_control",
    "/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/_control_deps",
    "/Users/davidusa/REPOS/Image_Tagger_worktrees/_control",
    "/Users/davidusa/REPOS/Image_Tagger_worktrees/_control_deps",
    "/Users/davidusa/REPOS/_control"
  ],
  "env_control_root": null,
  "packaged_cpp": false
},
"cpp": true, "supervisor": true, "trusted_unknown": "UNKNOWN"
```

Note the worktree case falls out for free: the provider is two levels up, not one, and nothing had to be told
so.

### 2.2 Delegating to the provider instead of re-implementing it

The charge requires calling the provider's sanctioned `cpp.locate.bootstrap()` while accounting for the fact
that `cpp.locate` cannot be imported until the provider is already reachable. The sequence:

1. Resolve a root by the order above.
2. Set `os.environ["CONTROL_ROOT"]` to **that** root. This is done *before* the delegation, so
   `cpp/locate.py`'s own built-in default (`/Users/davidusa/REPOS/_control`, hardcoded on the provider side)
   can never fire and re-import a host path through the back door.
3. Seed `sys.path` with the resolved root — the one irreducible step, since it is what makes `cpp.locate`
   importable at all.
4. `from cpp import locate; locate.bootstrap()` — the provider defines bootstrap semantics from here.
5. Assert the provider returned the root we resolved; a mismatch is a fail-closed error, not a shrug.

This is verified rather than assumed: the synthetic provider in the test suite writes a sentinel file when its
`bootstrap()` is called, and the tests assert the sentinel exists and contains the resolved root — and, in
packaged mode, assert it does **not** exist.

### 2.3 Per-module changes

Root: `/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1`.

| File | Was | Now |
|------|-----|-----|
| `annotation_socket/_cpp_bootstrap.py` | — | new; the whole resolution contract |
| `annotation_socket/annotator.py` | 3 stacked `sys.path.insert` (2 container, 1 host) | `stage = import_stage()` |
| `annotation_socket/verify.py` | 2 `sys.path.insert` | `stage = import_stage()` |
| `annotation_socket/run_stage.py` | 2 `sys.path.insert` | `stage = import_stage()` |
| `annotation_socket/controller.py` | 1 `sys.path.insert` | `stage = import_stage()` |
| `annotation_socket/controller_drive.py` | host/container `CONTROL_ROOT` default + 2 inserts + a path baked into the worker `python -c` string | `import_stage()` / `import_supervisor()` / `worker_env()` |
| `annotation_socket/derivation.py` | 2 inserts + a silent `UNKNOWN = "UNKNOWN"` fallback | `UNKNOWN = trusted_unknown()` |

The `/home/claude` insert in `annotator.py:20` existed to make `cnfa_algs` importable. Its intent is preserved
portably by `ensure_consumer_root_importable()`, which *appends* the checkout root derived from `__file__`.
Stated honestly: in the common invocations (run from the repo root, or run as a child of `worker_env()`) the
cwd entry or PYTHONPATH already covers `cnfa_algs`, so this is a safety net for out-of-tree invocation rather
than the load-bearing mechanism. It is appended, not prepended, so it cannot silently outrank whatever the
operator put earlier on `sys.path`.

### 2.4 One trust vocabulary (charge requirement 4)

`derivation.py` previously ended its import ladder with `UNKNOWN = "UNKNOWN"` if both provider paths failed.
That is the exact failure the chokepoint exists to prevent: a second sentinel that merely *compares equal*
today, forking the vocabulary the moment either side changes. It is gone. `UNKNOWN` is now bound only by
calling `trusted_unknown()`, which reads it from
`/Users/davidusa/REPOS/_control/supervisor/trusted_derivation.py` and fails closed otherwise — importing
`annotation_socket.derivation` without the provider now raises rather than running on a lookalike.

The test for this is structural, not textual: it parses `derivation.py` and asserts there is exactly one
binding of `UNKNOWN`, that it is not a literal, and that it is a call to `trusted_unknown`. A grep would have
been fooled by the comment that documents the removed fallback (and, on the first run, was — which is why the
check is on the parse tree).

An ambient module is accepted for either provider contract **only if it carries the contract's attribute**.
This matters concretely: `supervisor` is also the name of an unrelated PyPI process manager, and a bare
`import supervisor` succeeding would otherwise satisfy the contract while breaking it. When the ambient module
fails that check, the provider file is loaded under a private namespaced module name rather than by mutating
`sys.modules["supervisor"]` out from under any other consumer in the process.

### 2.5 Portable worker startup (charge requirement 5)

Before, the controller spawned its worker with a container path compiled into the source string and the stage
directory interpolated into it:

```python
code = ("import sys, json; sys.path.insert(0, '/home/claude'); "
        "from annotation_socket.annotator import run_worker; "
        f"print(json.dumps(run_worker({stage_dir!r})))")
proc = subprocess.run([sys.executable, "-c", code], ..., env={**os.environ})
```

After, the code string carries no path and no data; the layout travels in the environment and the stage
directory travels as `argv`:

```python
WORKER_CODE = ("import json, sys; "
               "from annotation_socket.annotator import run_worker; "
               "print(json.dumps(run_worker(sys.argv[1])))")
proc = subprocess.run([sys.executable, "-c", WORKER_CODE, str(stage_dir)], ..., env=worker_env())
```

`worker_env()` builds `PYTHONPATH` from the derived checkout root plus the resolved provider root and pins
`CONTROL_ROOT`. Because the directory is an `argv` element rather than source text, a stage directory
containing spaces or quotes is just data. Verified end-to-end from a foreign cwd with nothing inherited
(§4.4) and on a checkout whose path contains spaces (§4.2, `test_worker_subprocess_imports_from_path_with_spaces`).

---

## 3. The external supervisor dependency (charge requirement 7)

**`_control/cpp` is not self-contained at run time, and this is the single most important thing for anyone
packaging it to know.**

`cpp/` publishes the Controller-Pipeline Protocol, but two of its consumers' needs are satisfied from a
sibling directory it does not contain:

| Consumer site | Needs | Lives in |
|---|---|---|
| `annotation_socket/derivation.py` | `trusted_derivation.UNKNOWN` — the trust sentinel every predicate status is typed against | `/Users/davidusa/REPOS/_control/supervisor/trusted_derivation.py` |
| `annotation_socket/controller_drive.py` | `supervisor.classify_result` — worker death classification | `/Users/davidusa/REPOS/_control/supervisor/supervisor.py` |
| `_control/cpp/worker_shim.py` (provider-internal) | the supervisor's classification and progress-watchdog primitives | same directory; the provider's own README states the absolute path |

Consequence, stated plainly: **a `cnfa-cpp` wheel that shipped only `cpp/` would satisfy
`cnfa_cpp.stage.v1` and leave this repository broken.** `import cpp` would succeed, `trusted_derivation`
would not resolve, and — because the silent fallback is now removed — `annotation_socket.derivation` would
fail closed at import.

That is why the new contract declares **two** interfaces, not one, and why the bootstrap helper resolves and
diagnoses them independently. The packaged-precedence test asserts exactly this shape: with a packaged `cpp`
importable, the CPP contract is satisfied by the package while the supervisor contract is still satisfied
separately from the local provider root.

Whether `supervisor/` ships inside `cnfa-cpp` or as its own distribution is a provider-side (`_control`)
decision. It is recorded as `blocking` in the contract's `target_state`, unresolved, and is not this
consumer's to make.

---

## 4. Tests and evidence

Everything below was executed in this worktree on 2026-08-06. Python 3.14.2, pytest 9.0.2 available.
`PYTHONDONTWRITEBYTECODE=1` was exported for the suite and driver runs so that reading the provider left no
new bytecode in `/Users/davidusa/REPOS/_control`.

### 4.1 New test file

`annotation_socket/tests/test_cpp_bootstrap.py` — 13 tests, pure stdlib, no image dependencies. Each
path-resolution case runs in a **real child process** against a **synthetic provider tree** in a temporary
directory, so what is exercised is the actual import machinery rather than a mock of it.

| Charge-required test | Function |
|---|---|
| arbitrary directory layout, no David/Claude path | `test_derived_resolution_in_arbitrary_layout` |
| `CONTROL_ROOT` override | `test_control_root_override_wins_over_derived` |
| packaged-import precedence | `test_packaged_cpp_takes_precedence_without_syspath_surgery` |
| missing CPP failure | `test_missing_cpp_fails_closed_with_one_diagnostic` |
| missing `supervisor/trusted_derivation.py` failure | `test_missing_trusted_derivation_fails_closed_separately` |
| subprocess import from a path containing spaces | `test_worker_subprocess_imports_from_path_with_spaces` |
| source census over the six runtime modules | `test_runtime_modules_contain_no_host_or_container_paths` |

Six added beyond the required set: `test_derived_scan_is_bounded_and_named` (the scan cannot walk to `/`),
`test_explicit_control_root_never_falls_through_to_a_guess` (the anti-fallback property, which is the R1
defect class), `test_derivation_has_no_local_unknown_fallback` (AST-level),
`test_controller_drive_worker_code_carries_no_path` (static contract on the spawn string),
`test_runtime_modules_have_no_manual_syspath_bootstrap`, and
`test_real_provider_contract_is_satisfied_here` (both contracts against the actual provider).

### 4.2 The new tests

```
$ cd /Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1
$ PYTHONPATH=. python3 annotation_socket/tests/test_cpp_bootstrap.py
test_derived_resolution_in_arbitrary_layout
  derived local scan resolves an arbitrary layout; provider bootstrap() delegated  OK
test_derived_scan_is_bounded_and_named
  candidate scan bounded to 6 levels x 2 names, nearest ancestor first  OK
test_control_root_override_wins_over_derived
  explicit CONTROL_ROOT overrides the derived scan and is the only candidate  OK
test_explicit_control_root_never_falls_through_to_a_guess
  a wrong explicit CONTROL_ROOT fails closed instead of guessing  OK
test_packaged_cpp_takes_precedence_without_syspath_surgery
  packaged `cpp` wins with zero sys.path surgery; supervisor resolved separately  OK
test_missing_cpp_fails_closed_with_one_diagnostic
  missing CPP -> one fail-closed diagnostic naming the contract + 3 remedies  OK
test_missing_trusted_derivation_fails_closed_separately
  missing supervisor/trusted_derivation.py -> its OWN fail-closed diagnostic  OK
test_derivation_has_no_local_unknown_fallback
  derivation.py binds UNKNOWN only via trusted_unknown(), no literal fallback  OK
test_worker_subprocess_imports_from_path_with_spaces
  worker_env + argv start a child from a spaced checkout, no path in the source  OK
test_controller_drive_worker_code_carries_no_path
  controller_drive WORKER_CODE embeds no source-tree path  OK
test_runtime_modules_contain_no_host_or_container_paths
  census: 6 runtime modules + the helper, 0 literal /home/claude / /Users/davidusa  OK
test_runtime_modules_have_no_manual_syspath_bootstrap
  no runtime module performs its own sys.path bootstrap  OK
test_real_provider_contract_is_satisfied_here
  real provider: mode=derived_local root=/Users/davidusa/REPOS/_control UNKNOWN='UNKNOWN'  OK

CPP BOOTSTRAP TESTS PASSED (13)
EXIT=0
```

### 4.3 Every `annotation_socket/tests/test_*.py`, per file, under `PYTHONPATH=.`

```
$ for f in annotation_socket/tests/test_*.py; do PYTHONPATH=. python3 "$f"; done

----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_c01_triangulation.py
RESULT: PASS
  M1 replay: deterministic (|Δ|<=1e-03); fabricated 0.90 vs true 0.0000 -> REJECT  OK
ALL C01 CORE TESTS PASSED
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_c29_stranded.py
RESULT: PASS
  M1: deterministic; fabricated 0.90 vs on-ridge 0.0049 / wall-art 0.0340 -> REJECT  OK
ALL C29 CORE TESTS PASSED
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_cc3_layout_inputs.py
RESULT: PASS
  out-of-grid seat -> UNKNOWN cell guard  OK
CC-3 LAYOUT-INPUT TESTS PASSED
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_codex_tax_fixes.py
RESULT: PASS
  TAX-0: direct `python3 cnfa_algs/<file>.py` runs  OK
CODEX TAX-FIX REGRESSION LOCKS PASSED
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_complexity_review_pack.py
RESULT: PASS
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_complexity_species.py
RESULT: PASS
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_cpp_bootstrap.py
RESULT: PASS
  real provider: mode=derived_local root=/Users/davidusa/REPOS/_control UNKNOWN='UNKNOWN'  OK
CPP BOOTSTRAP TESTS PASSED (13)
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_f7_ridge_boundary.py
RESULT: PASS
  boundary locked: near-flat -> degenerate; bimodal -> passes (RIDGE_MIN_RELIQR=0.05)  OK
F7 RIDGE BOUNDARY TESTS PASSED
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_m1_prime.py
RESULT: PASS
  operator_extract: 20 bindings x2 fixtures — determ+roundtrip+real-field-tamper (18/20 real-field on synth, 2 abstained, LSD ops scored on lines)  OK
M1' TESTS PASSED
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_reliable_attrs.py
RESULT: PASS
  V7 clutter: cluttered=0.715 > blank=0.000 ; deterministic  OK
ALL RELIABLE-ATTR CORE TESTS PASSED (V2, V13, V1, V6, V7)
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_v9_fractal_band.py
RESULT: PASS
  M1: deterministic; chaotic D=2.0 -> band=0.091 (cannot be laundered high)  OK
ALL V9 CORE TESTS PASSED
----- CMD: PYTHONPATH=. python3 annotation_socket/tests/test_wave2_geometry.py
RESULT: PASS
  determinism: W2.2 + W2.4 replay identical  OK
WAVE-2 GEOMETRY (CC-4) SOCKET TESTS PASSED

### SUMMARY per-file: PASS=12 FAIL=0
```

### 4.4 The worker-spawn contract, against the real modules, from a foreign cwd

The spaced-path test uses a synthetic provider. This run uses the **real** provider, the **real** annotator,
and `cwd=/` with `PYTHONPATH` and `CONTROL_ROOT` explicitly unset in the parent — so nothing but the derived
resolution and `worker_env()` can make the import work.

```
$ cd / && env -u PYTHONPATH -u CONTROL_ROOT python3 -c "<build worker_env(), spawn the real worker import>"
PYTHONPATH  = /Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1:/Users/davidusa/REPOS/_control
CONTROL_ROOT= /Users/davidusa/REPOS/_control
WORKER_CODE = import json, sys; from annotation_socket.annotator import run_worker; print(json.dumps(run_worker(sys.argv[1])))
child rc = 0
child import OK cwd=/
cnfa_algs from /Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1/cnfa_algs/__init__.py
EXIT=0
```

### 4.5 `CONTROL_ROOT` edge cases

```
----- CONTROL_ROOT=[]
  mode=derived_local source=derived root=/Users/davidusa/REPOS/_control     import_stage: OK
----- CONTROL_ROOT=[  ]
  mode=derived_local source=derived root=/Users/davidusa/REPOS/_control     import_stage: OK
----- CONTROL_ROOT=[/Users/davidusa/REPOS/_control/]
  mode=control_root_env source=env root=/Users/davidusa/REPOS/_control      import_stage: OK
----- CONTROL_ROOT=[../../_control]
  mode=control_root_env source=env root=/Users/davidusa/REPOS/_control      import_stage: OK
```

Empty and whitespace-only values are treated as unset (not as an explicit declaration of the empty path);
trailing slashes normalise; a relative value resolves against the cwd — see residual risks.

### 4.6 The provider's focused CPP self-test

`SOCKET_CONFORMANCE.md` §2 names `/Users/davidusa/REPOS/_control/cpp/conformance.py` as the focused CPP
harness. Run read-only against a scratch stage directory; `_control` was not modified.

```
$ python3 /Users/davidusa/REPOS/_control/cpp/conformance.py --stage-dir /tmp/cpp-stage-m1
PASS schedule+claim: enqueued=5 claimed=5 forced_race_successes=1 double_claims=0
PASS observe: started=5 heartbeat=5 terminal=5 coverage=5/5 from events.jsonl
PASS gate: good_GREEN_accepted=4 seeded_BAD_RED=1 bad_accepted=0 coverage_lt_100_batch_red=1
PASS liveness!=progress: heartbeat_fresh=3 accepted_growth=0 classification=SPEND_DEAD_SUSPECTED
PASS idempotent-resume: kill_mid_run_restart accepted=4 redundant_work=0
PASS authority: worker_control_write=DENIED worker_accepted_write=DENIED privilege_fields=trusted_derivation
NEGATIVE PASS: seeded BAD unit was RED and absent from accepted/
PASS paired-readers: read_quarantine(unit-1).stdout='processed alpha'; events/verdicts/accepted read via lib
PASS unit-key-roundtrip: legacy unit_id and canonical id both claim/quarantine/verdict/accept; idempotent skip OK
STAGE: /tmp/cpp-stage-m1
SUMMARY: 6/6 conformance checks PASS; negative gate PASS
VERDICT: PARTIAL: builder-run harness passes; awaiting ≠-mind run for certification
EXIT=0
```

This exercises the provider library, not my changes. It is included because it establishes that the library
being resolved is intact, so a failure in §4.7 would be attributable to the consumer boundary.

### 4.7 The socket end-to-end, through the changed import path

Both in-repo drivers, on three real images from `Example Images/`. One filename deliberately carries spaces
and non-ASCII characters (`1 f_pic948 - David Židlický.jpg`) — exactly the sort of argument the old
`f"...run_worker({stage_dir!r})..."` spawn string had to escape into source text, and the new `argv` path
simply passes.

```
$ cd /Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1
$ PYTHONPATH=. python3 -m annotation_socket.run_stage /tmp/anno-stage-m1 \
      "Example Images/1 f_pic948 - David Židlický.jpg" \
      "Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg" \
      "Example Images/Ludwig_Mies_van_der_Rohe__Farnsworth_House__1945-1951_2.jpg"
[controller] queue: 3 units
[worker] run1 processed=3 skipped=0
[checker] verdicts: GREEN=0 AMBER=2 RED=1
  unit 043b714c7078b725 (1 f_pic948 - David Židlický.jpg): tier=AMBER scored=48/48 applicable, abstained=20, unknown=0  amber_preds=40
    e.g. cnfa.light.brightness_variance=0.2257 <- region [694, 64, 697, 67] signal='local luminance SD, 31px window (M1)'
    e.g. C1.visual_integration=0.994 <- plan_chain grid=08f6f1d75fd44fa3 upstream=4 steps
    e.g. ABSTAINED cnfa.acoustic.street_noise_intrusion ['facade_spec', 'outdoor_leq']
  unit fa42ccbadec5d594 (Industrial-open-concept-office-project-b): tier=AMBER scored=48/48 applicable, abstained=20, unknown=0  amber_preds=40
    e.g. cnfa.light.brightness_variance=0.2474 <- region [747, 207, 750, 210] signal='local luminance SD, 31px window (M1)'
    e.g. C1.visual_integration=0.995 <- plan_chain grid=22ceaa8150fd2b78 upstream=4 steps
    e.g. ABSTAINED cnfa.acoustic.street_noise_intrusion ['facade_spec', 'outdoor_leq']
[negative-control] seeded defaulted-C14 + constant-C8 -> tier=RED
    FABRICATION:C8.distraction_distance scored but requires ['acoustic_params'] absent from unit
    FABRICATION:C14.focus_collab_separation scored but requires ['collab_sources', 'focus_seats'] absent from unit
[negative-control] REJECTED (RED), absent from accepted/ — the score_layout bug cannot recur
[worker] run2 processed=0 skipped_content_addressed=3
[idempotency] second run: ZERO work, all units skipped by content address
[authority] worker write to control.jsonl DENIED (BoundaryError) — [W:] boundary holds
[authority] worker write to accepted/ DENIED (BoundaryError)

RUN/TEST RUBRIC: (a)+(b)+(c) demonstrated. AMBER units await the ≠-mind judge (not self-certified).
EXIT=0
```

`controller_drive.py` is the module this charge changed most invasively — it is the one that spawns the
worker — so it was driven too:

```
$ PYTHONPATH=. python3 -m annotation_socket.controller_drive /tmp/anno-ctrl-m1 <the same 3 images>
[nn-controller] ENQUEUE 043b714c7078b725 <- 1 f_pic948 - David Židlický.jpg
[nn-controller] ENQUEUE fa42ccbadec5d594 <- Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg
[nn-controller] ENQUEUE 70ccdd877f8f79a5 <- Ludwig_Mies_van_der_Rohe__Farnsworth_House__1945-1951_2.jpg
[nn-controller] worker subprocess -> classified 'success'; result={"processed": ["043b714c7078b725", "fa42ccbadec5d594", "70ccdd877f8f79a5"], "skipped_content_address
[nn-controller] tick: observe={'queued': 3, 'events': {'started': 3, 'heartbeat': 3, 'done': 3}, 'verdicted': 0, 'accepted': 0}
[nn-controller] tick: gate={'GREEN': 0, 'AMBER': 2, 'RED': 1} liveness=progressing
[nn-controller] tick: batch=complete: {'AMBER': 2, 'RED': 1}

[nn-controller] DIGEST (what David sees):
    AMBER unit 043b714c7078b725 awaits ≠-mind inference judge
    AMBER unit fa42ccbadec5d594 awaits ≠-mind inference judge
    RED   unit 70ccdd877f8f79a5 REJECTED by mechanical gate — quarantined
[nn-controller] AUDIT (last 8 decisions, logged before enactment):
    enqueue                unit=70ccdd877f8f79a5 {"image": "Ludwig_Mies_van_der_Rohe__Farnsworth_House__1945-
    enqueue                unit=70ccdd877f8f79a5 {"controller_id": "nn-controller"}
    worker_run             unit=None             {"classification": "success"}
    gate_begin             unit=None             {"pending": 3}
    adjudicate_needed      unit=043b714c7078b725 {"tier": "AMBER"}
    adjudicate_needed      unit=fa42ccbadec5d594 {"tier": "AMBER"}
    escalate               unit=70ccdd877f8f79a5 {"tier": "RED"}
    tick_end               unit=None             {"AMBER": 2, "GREEN": 0, "RED": 1}
EXIT=0
```

`classified 'success'` is the supervisor's own verdict on a child process started **entirely** from
`worker_env()` — the new startup path, the real annotator, three units processed. Both provider contracts are
live in that single run: `cpp.stage` for every artifact, `supervisor.classify_result` for the death
classification, each resolved through the new helper.

#### One unit is RED — and an A/B against the base commit shows it is not this change

`run_stage` prints detail only for GREEN/AMBER units, so the RED unit's reasons come from `verdicts.jsonl`:

```
043b714c7078b725 -> AMBER | n_scored= 48
70ccdd877f8f79a5 -> RED   | n_scored= 47
     PROBLEM: UNKNOWN:C01.triangulation_ignition reason=anchor_registration_unconfident
     PROBLEM: UNKNOWN:C29.stranded_amenity_index reason=anchor_registration_unconfident
fa42ccbadec5d594 -> AMBER | n_scored= 48
negctrl-043b714c -> RED   | n_scored= 50
     PROBLEM: FABRICATION:C8.distraction_distance scored but requires ['acoustic_params'] absent from unit
     PROBLEM: FABRICATION:C14.focus_collab_separation scored but requires ['collab_sources', 'focus_seats'] absent from unit
```

Both problems are C01/C29's *documented* fail-closed path — `triangulation.py`'s header specifies "anchor
detected but cross-tier registration is unconfident -> DO NOT guess the centroid (skeptic's fix) ... Routes
RED, never a number." The Farnsworth House image is a hard case for cross-tier anchor registration and the
pipeline correctly refuses to invent a value.

I could have argued from the diff that an import-resolution change cannot alter a predicate value. Arguing is
not evidence, so I ran the A/B instead. The six modules at base commit `49fac5033bcc3ba05c69e4bde9b29a794a6cc00a`
were extracted with `git show` into `/tmp/m1_base/annotation_socket/`, with **every other file in the package
symlinked to this worktree** and `cnfa_algs` supplied from this worktree — so the six modules are the only
variable — and the same three images were run:

```
$ cd /tmp/m1_base && PYTHONPATH=/Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1 \
      python3 -m annotation_socket.run_stage /tmp/anno-stage-base <the same 3 images>
[controller] queue: 3 units
[worker] run1 processed=3 skipped=0
[checker] verdicts: GREEN=0 AMBER=2 RED=1
  unit 043b714c7078b725 (1 f_pic948 - David Židlický.jpg): tier=AMBER scored=48/48 applicable, abstained=20, unknown=0  amber_preds=40
    e.g. cnfa.light.brightness_variance=0.2257 <- region [694, 64, 697, 67] signal='local luminance SD, 31px window (M1)'
    e.g. C1.visual_integration=0.994 <- plan_chain grid=08f6f1d75fd44fa3 upstream=4 steps
    e.g. ABSTAINED cnfa.acoustic.street_noise_intrusion ['facade_spec', 'outdoor_leq']
  unit fa42ccbadec5d594 (Industrial-open-concept-office-project-b): tier=AMBER scored=48/48 applicable, abstained=20, unknown=0  amber_preds=40
    e.g. cnfa.light.brightness_variance=0.2474 <- region [747, 207, 750, 210] signal='local luminance SD, 31px window (M1)'
    e.g. C1.visual_integration=0.995 <- plan_chain grid=22ceaa8150fd2b78 upstream=4 steps
    e.g. ABSTAINED cnfa.acoustic.street_noise_intrusion ['facade_spec', 'outdoor_leq']
[negative-control] seeded defaulted-C14 + constant-C8 -> tier=RED
    FABRICATION:C8.distraction_distance scored but requires ['acoustic_params'] absent from unit
    FABRICATION:C14.focus_collab_separation scored but requires ['collab_sources', 'focus_seats'] absent from unit
[negative-control] REJECTED (RED), absent from accepted/ — the score_layout bug cannot recur
[worker] run2 processed=0 skipped_content_addressed=3
[idempotency] second run: ZERO work, all units skipped by content address
[authority] worker write to control.jsonl DENIED (BoundaryError) — [W:] boundary holds
[authority] worker write to accepted/ DENIED (BoundaryError)

RUN/TEST RUBRIC: (a)+(b)+(c) demonstrated. AMBER units await the ≠-mind judge (not self-certified).
EXIT=0
```

The base-commit output is **identical to the branch output**, line for line: the same
`GREEN=0 AMBER=2 RED=1`, the same unit ids, the same `brightness_variance` values to four decimals
(0.2257 / 0.2474), the same plan-chain grid hashes (`08f6f1d75fd44fa3`, `22ceaa8150fd2b78`), the same
`48/48 applicable`, and the same RED unit with the same two `anchor_registration_unconfident` UNKNOWNs. The
RED pre-dates this branch and this change is behaviour-neutral on the pipeline.

Two things this A/B does *not* establish, said plainly: it covers three images, not the corpus, and it
compares the branch against its own base on one machine — it says nothing about cross-environment replay
(see the L5 findings, out of scope here).

---

## 5. The declared interface

`contracts/cross_repo/IMAGE_TAGGER_CPP_INTERFACE_V1.json` declares two interfaces:

- **`cnfa_cpp.stage.v1`** — same id Article_Eater uses, so both consumers name one interface.
  `status: local_source_bootstrap`. `current_state` records the resolution order, the acceptance markers, and
  the delegation to `cpp.locate.bootstrap()`. `target_state` records the pinned-package end state with
  `pin_present: false` and an explicit `blocking` list quoting the two verifications in §1.
- **`control_supervisor.trusted_derivation.v1`** — the supervisor contract, with `why_separate` recording the
  non-self-containment argument of §3.

The provider commits (`_control` HEAD `20d3c8e3cb843d62e2a31dd8969cd83f0e653b86`, `cpp` subtree
`e03d7ebf10d3b35d9fd9f4457a602485cc89d366`) are recorded under `provider_observation` with
`enforced: false`. They are provenance. **Nothing in this repository checks them at run time**, and the
resolver will adopt whatever provider revision it finds. Calling them a pin would be the proxy-as-proof
failure this contract is meant to prevent.

The file carries a `not_claimed` block listing what it does *not* assert.

---

## 6. Verification boundary

**Verified, by execution, in this worktree on 2026-08-06:**

- All 13 new bootstrap tests pass; all 12 `annotation_socket/tests/test_*.py` files pass per file under
  `PYTHONPATH=.` (11 pre-existing + 1 new), 0 failures.
- The six runtime modules and the new helper contain zero occurrences of `/home/claude` or `/Users/davidusa`
  (grep and an in-suite census test).
- No runtime module performs its own `sys.path` bootstrap.
- Resolution works in `packaged`, `control_root_env`, and `derived_local` modes, and fails closed with a
  single per-contract diagnostic in the two missing-provider modes.
- The provider's `cpp.locate.bootstrap()` is genuinely called in the local modes and genuinely *not* called in
  packaged mode (sentinel-file evidence).
- The real worker subprocess starts from `cwd=/` with no inherited `PYTHONPATH`/`CONTROL_ROOT`.
- Both in-repo drivers (`run_stage`, `controller_drive`) run end-to-end on three real images, exit 0, with the
  negative control still RED and the `[W:]` boundary still denying worker writes.
- **Behaviour neutrality, by A/B against the base commit**, not by argument: the six modules at
  `49fac503` produce output identical to the branch on the same three images, with every other file in the
  package held constant (§4.7).
- No file outside this repository was modified; no in-repo consumer of `cpp` exists outside
  `annotation_socket/` (grep over all `*.py`).

**NOT verified — stated so no reader infers it:**

- **Not certified.** I authored this repair, so my passing it proves nothing about its adequacy. An
  independent reviewer must attack it.
- **Behaviour in the Cowork sandbox was not exercised.** The `_control_deps` candidate name is supported and
  unit-tested against a synthetic tree, but no run happened inside a container where the provider actually
  lives at `/home/claude/_control_deps`. It is bounded-ancestor-derived, so it works only if the provider is
  an ancestor-sibling of the checkout there.
- **The provider's internal correctness was not verified** — the `[W:]` boundary, `O_EXCL` claims and
  `accepted/` content addressing are the provider's business and were not audited. §4.6 is the provider's own
  builder-run harness, not an independent check of it.
- **No pixel-level cross-environment claim.** Nothing here addresses the L5 cross-environment replay findings.
- **`annotation_socket/__init__.py` still names `/Users/davidusa/REPOS/...` in its module docstring** (lines 9
  and 11). It is outside this charge's allowed-writes list and is documentation, not runtime resolution, so it
  was left alone. Flagged for whoever owns the follow-up.
- **Seven existing test files still carry `sys.path.insert(0, "/home/claude")`** (`test_c01_triangulation.py`,
  `test_c29_stranded.py`, `test_codex_tax_fixes.py`, `test_f7_ridge_boundary.py`, `test_m1_prime.py`,
  `test_reliable_attrs.py`, `test_v9_fractal_band.py`). The charge scopes the census to the six *runtime*
  modules and forbids editing unrelated tests, so these were left alone. The `/home/claude` inserts are inert
  on this machine (a nonexistent path on `sys.path` is a no-op), but they are the same defect class and should
  be swept.
- **`annotation_socket/tests/test_codex_tax_fixes.py` does not test this worktree at all**, and its PASS in
  §4.3 must not be read as evidence about this branch. Line 8 is
  `sys.path.insert(0, "/Users/davidusa/REPOS/Image_Tagger_dk_latest")` — the *primary* checkout — which lands
  ahead of `PYTHONPATH=.`. Replicating its own preamble exactly:

  ```
  $ cd /Users/davidusa/REPOS/Image_Tagger_worktrees/claude-m1
  $ PYTHONPATH=. python3 -c "<the test's lines 7-8, then import annotation_socket, cnfa_algs>"
  annotation_socket -> /Users/davidusa/REPOS/Image_Tagger_dk_latest/annotation_socket/__init__.py
  cnfa_algs         -> /Users/davidusa/REPOS/Image_Tagger_dk_latest/cnfa_algs/__init__.py
  ```

  So that file exercises the primary (dirty) checkout wherever it is run from. This is exactly the defect
  class this charge repairs, still live in the test layer, and it is a stronger reason to sweep the tests than
  tidiness: a hardcoded checkout path makes a test silently measure the wrong tree. Out of scope here
  (`Do not edit ... unrelated tests`), flagged for the follow-up owner. The other eleven test files resolve
  against this worktree normally.
- **`TASKS.md` was not updated.** The root `CLAUDE.md` requires it; this charge's allowed-writes list does not
  include it and explicitly forbids broadening scope. The charge won. Flagged for the orchestrator.

---

## 7. Residual risks

1. **The derived scan is a heuristic.** It adopts the nearest ancestor directory named `_control` or
   `_control_deps` that carries `cpp/locate.py` and `cpp/stage.py`. Two provider checkouts in the ancestor
   chain means the nearest wins silently. Mitigations in place: it is bounded to 6 levels, it never reaches
   `/` from a normally-nested checkout, it requires content markers rather than a name match, and the chosen
   root plus every candidate searched is reported in `resolve()` and in every failure diagnostic. Setting
   `CONTROL_ROOT` removes the heuristic entirely.
2. **A relative `CONTROL_ROOT` resolves against the cwd** (§4.5), so the same value can mean different roots
   from different working directories. This matches the provider's own `locate.control_root()` behaviour;
   documenting rather than diverging seemed right, but an operator should pass an absolute path.
3. **`PYTHONPATH` cannot express a path containing `os.pathsep`** (`:` on POSIX). Spaces are fine and tested;
   a colon in a checkout path would break `worker_env()`. Stated in the helper's docstring rather than hidden.
4. **`_load_provider_module` inserts the provider's `supervisor/` directory at `sys.path[0]`**, which makes
   `supervisor` and `trusted_derivation` importable top-level for the rest of the process and could shadow a
   same-named installed package elsewhere in that process. This preserves the prior behaviour and is what
   keeps provider-internal bare-name imports consistent; the two files in question currently import only
   stdlib, so the insert is defensive rather than required today.
5. **`derivation.py` now fails at import time when the provider is absent.** That is the intended fail-closed
   semantics and is the point of requirement 4, but it does convert a previously-silent degradation into a
   hard failure — a machine that was quietly running on the invented `"UNKNOWN"` will now stop. That is the
   correct direction, and it is a behaviour change worth naming.
6. **The contract's `provider_observation` commits will drift.** Nothing enforces them. They are marked
   `enforced: false` precisely so a future reader cannot mistake them for a pin.
7. **The real end-to-end fix — a packaged, pinned `cnfa-cpp`** — is not done and cannot be done from this
   repository. It is blocked on `_control` shipping packaging metadata and deciding where `supervisor/` lives.
   Until then both consumers reach into a local source tree; this charge makes that reach explicit, bounded,
   portable, and fail-closed, but it does not make it a package.

---

## 8. Not certified

This document is builder-run evidence. Every command shown here was executed and its output is reproduced
literally; nothing is a prediction. What that does *not* establish is that the boundary is right — I wrote it,
so I am the wrong mind to clear it. Per the charge: no merge, no push, no certification. The commit is for an
independent reviewer to attack.
