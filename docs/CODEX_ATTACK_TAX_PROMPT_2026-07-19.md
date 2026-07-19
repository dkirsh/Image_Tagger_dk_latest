# CODEX ATTACK PROMPT — Batch: clutter stack + complexity partition (11-class taxonomy) + faithful FC/SE + wave-2 geometry

**Date**: 2026-07-19 · **Requested by**: Fable (Cowork session) · **Role**: adversarial attacker (checker ≠ author)

## ARTIFACT CONTRACT (mandatory)

Write your complete verdict to:

```
/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CODEX_ATTACK_TAX_VERDICT_2026-07-19.md
```

then `git add -f` that file and commit on branch `cnfa-algs-2026-07-14` with message
`Codex attack verdict: taxonomy/clutter-stack/faithful/wave2 batch`. Do NOT push. Do NOT wait for
hand transfer — the requesting session polls the repo for this exact path. If a stale zero-byte
`.git/*.lock` blocks you, confirm no live git process, `mv` the lock into `_to_delete/`, retry.

## PATH MANIFEST (all verified to exist at these absolute paths, 2026-07-19)

Repo root: `/Users/davidusa/REPOS/Image_Tagger_dk_latest` (branch `cnfa-algs-2026-07-14`, HEAD fde0e2dc). All paths below are relative to that root.

- `cnfa_algs/clutter_stack.py` — proto_object_count (mean-shift), multiscale_gradient (MSG proxy), multiscale_unique_color (MUC proxy)
- `cnfa_algs/complexity_partition.py` — tile-then-merge regionalization + 11-class semantic taxonomy + per-zone fractal D + hedonic hypothesis tags
- `cnfa_algs/faithful_clutter.py` — faithful Feature Congestion + Subband Entropy via vendored reference
- `cnfa_algs/_pyrtools_min.py` — pyramid shim (P2 √2-binomial, P4a-c, S1B log_rad fixes)
- `cnfa_algs/_vendor/visual_clutter/clutter.py` (+ `utils.py`, `__init__.py`) — UNMODIFIED reference `visual_clutter` 1.0.7 (MIT). Any diff from upstream except the import shim is itself a finding.
- `cnfa_algs/wave2_geometry.py` — wave-2 geometry ops (built, mostly unregistered pending this attack)
- `annotation_socket/registry.py` — 44-predicate registry; MAY_LACK_SIGNAL gate; MODEL_VERSION
- `annotation_socket/verify.py`, `annotation_socket/m1_prime.py` — M1/M1′ replay machinery
- `scripts/reference_clutter_compare.py` — adjudication harness (real pyrtools vs shim)
- Context docs: `docs/CODEX_S1B_NOTE_2026-07-19.md`, `docs/PAPER_NOTE_ROSENHOLTZ_CLUTTER_2007_AND_AFTER_2026-07-19.md`, `docs/SPRINT_COMPCORRECT_ALGORITHMS_2026-07-19.md`, `TASKS.md`

Run tests per-file with `python3` (pytest is NOT assumed): each module has a `__main__` self-test; socket tests live in `annotation_socket/tests/` and run as `python3 annotation_socket/tests/<file>.py`.

## YOUR MISSION

Attack, do not review. For each target produce findings labeled **BROKEN** (wrong result on a
constructible input), **DISHONEST** (claims more than it verifies — tier, method string, abstention,
or registry note overstates), **FRAGILE** (correct now, breaks under reasonable perturbation), or
**CLEAN** (attacked and survived — say what you threw at it). Every BROKEN claim must come with a
minimal reproduction (code or exact fixture description + observed vs expected). No finding without
evidence; no "looks fine" without naming the attack that failed to break it.

### Target 1 — clutter_stack.py
1. **Mean-shift proto-objects**: does `proto_object_count` depend on image SIZE in a way the
   registry note doesn't declare? Try the same scene at 512px vs 1024px — is the count stable or
   does bandwidth-in-pixels make it resolution-dependent?
2. **Connectivity regression guard**: we were burned once by cv2's positional-connectivity silent
   ignore (now `connectivity=4` keyword). Verify no OTHER cv2 call in the stack has a positional
   arg that silently changes semantics (check signatures against cv2 docs).
3. **MSG/MUC proxies**: they are labeled proxies — is the label honest? Compare on 3+ fixtures
   against a literal re-read of the 2007 definitions; if a proxy departs structurally (not just in
   constants), the method string must say where.
4. Degenerate inputs: 1-color image, 2px-wide image, alpha channel present. SCORED, ABSTAINED, or
   crash?

### Target 2 — complexity_partition.py (the taxonomy — newest, least attacked)
5. **Gate-order exploits**: classifier order is vegetation→water→sky→fire→material→ordered→
   collection→ornament→junk→neutral, with an art reclass pass after. Construct inputs that
   exploit the ordering: (a) a green-tinted stone wall (vegetation gate steals material?);
   (b) blue wall + specular sheen (water?); (c) a bright white ceiling with texture (sky gate
   requires blue-bright OR tlum≥0.88 + smooth — does "smooth" hold on stucco?); (d) a framed
   MIRROR (art frame test fires on any frame — is that declared?).
6. **Constant provenance**: `GREEN_FRAC_GATE`, `MAT_TEXTURE_MIN`, `MAT_HUE_STD_MAX`, wood_frac
   0.30 / mean_sat 0.75 / 0.20, `FIRE_LUM_MIN=0.40`, `FIRE_STD_MIN=0.12`, `PERIODIC_PEAK_MIN=0.45`,
   `ORNAMENT_PEAK_MIN=0.58`, `COHERENCE_MIN=0.55`, `ART_FRAME_EDGE_MIN=0.45`. These were tuned on
   a handful of fixtures. The registry/tier must say AMBER-heuristic and the module must declare
   them refittable; verify each constant is (a) surfaced in extras, (b) not silently load-bearing
   for a claim the method string doesn't make.
7. **Fractal D per zone**: box-count implementation — check the regression fit (log-log slope) for
   (a) zones smaller than the smallest box scale, (b) zones with <2 populated scales. Does it
   ABSTAIN or emit garbage D? Is the Taylor/Hagerhall band correctly a FLAG, never a gate?
8. **Hedonic tags**: confirm every hedonic tag in output is marked hypothesis/UNLICENSED and that
   nothing downstream (registry, derivation) consumes it as a scored value.
9. **Merge correctness**: tile-then-merge — construct a zone that should be contiguous but is
   split by the merge rule (or vice versa: two semantically different regions merged because
   tiles agree on class). Is 4- vs 8-adjacency in the merge declared and consistent?

### Target 3 — faithful_clutter.py + _pyrtools_min.py + vendor
10. **Vendor integrity**: diff `cnfa_algs/_vendor/visual_clutter/` against upstream 1.0.7
    (wheel is at `reference/visual_clutter-1.0.7-py3-none-any.whl`). ONLY the pyrtools import
    redirection may differ. Report any other byte.
11. **Shim completeness**: the shim passed subband-std adjudication to ~1e-7 on the S1B fixtures.
    Attack the UNTESTED paths: non-square images, odd dimensions (513×511), images small enough
    that wlevels=3 exceeds what the pyramid supports. Does the shim fail loudly, or silently
    produce a wrong-shape pyramid?
12. **Near-blank abstain guard**: the guard abstains on featureless fields. Find the boundary —
    a barely-textured wall photo. Is the abstain threshold declared in extras, and does it fire
    monotonically (no SCORED sandwiched between two ABSTAINED at increasing texture)?
13. **P3 exposure**: the reference package's collapse() lacks the MATLAB ×4 upConv gain (known,
    filed for panel). Verify our method string / registry note DECLARES we compute
    package-semantics FC, not MATLAB-semantics FC, so no consumer can misread it.

### Target 4 — wave2_geometry.py (pre-registration attack)
14. Per-op: check the declared math (ceiling_openness_relative, double-height flag,
    blind_corner_index, barrier_permeability, verticality, choice_richness) against its docstring
    contract on ONE constructed fixture each. L5 showed the geometry chain amplifies sub-1% pixel
    noise into 13% cell_m shifts — for each op, state whether it sits downstream of that chain
    and whether its output granularity (continuous vs banded) is honest given that instability.
15. Any op that cannot be made robust at current tier should be flagged DO-NOT-REGISTER-YET with
    the specific missing precondition.

### Cross-cutting (all targets)
16. **Socket honesty**: for every predicate touched, tri-state discipline (SCORED/ABSTAINED/
    UNKNOWN), `signal_absent` only where MAY_LACK_SIGNAL licenses it, absence_evidence non-empty,
    M1′ strict gate not bypassed.
17. **Determinism**: run each operator twice on the same input in one process and across two
    processes — bit-identical extras? Any dict-ordering or float-accumulation nondeterminism is
    a finding (it breaks M1′ replay).

## VERDICT FORMAT

Per target: table of findings (ID, severity BROKEN/DISHONEST/FRAGILE/CLEAN, one-line claim,
reproduction pointer). Then an overall gate line: `GATE: PASS` (nothing BROKEN/DISHONEST) or
`GATE: FAIL (ids...)`. End with the exact commit hash you attacked and the list of attacks you did
NOT run (time or environment limits) — an unstated omission is itself a coordination failure.
