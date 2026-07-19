# CODEX ATTACK PROMPT — Sprint COMP-CORRECT batch S0+S2 (M1′ + Wave-1 + street-noise)
### 2026-07-19. Self-contained. Repo = /Users/davidusa/REPOS/Image_Tagger_dk_latest (branch cnfa-algs-2026-07-14). Run with `PYTHONPATH=.`

You are an adversarial verifier. A new batch claims to be COMPUTATIONALLY CORRECT and honestly tiered.
Your job is to break it — the method claims, the constants, the abstention paths, the wiring — not to
admire it. Determinism is table stakes; attack ADEQUACY: does each algorithm compute what its method
string claims, are the constants defensible, does anything overclaim its tier, and does the new M1′
machinery actually catch what it says it catches?

## Files in the batch (commits `6e0050b9`, `66d6ec1e`; verify each exists)
- `annotation_socket/m1_prime.py` — NEW: M1′ sufficient-statistic replay core. 5 audit classes
  (luminance_field, radial_fft, orientation_hist, box_count, color_palette), canonical-JSON sha256
  digest with a 6-decimal rounding grid, `M1P_BINDINGS`, shared loader `load_for_m1p`.
- `annotation_socket/annotator.py` — MODIFIED: emits `m1p` blocks on 5 bound predicates; 9 new Wave-1
  bindings; None-scalar → UNKNOWN(`signal_undefined:*`) guard.
- `annotation_socket/verify.py` — MODIFIED: M1′ replay stage after M1 (stats-tamper → RED problem
  `M1_PRIME:<pid>:stats_mismatch`; missing block → AMBER demotion).
- `annotation_socket/registry.py` — MODIFIED: 10 new predicates (9 image AMBER + street-noise
  plan_metric requiring {outdoor_leq, facade_spec}); MODEL_VERSION bumped `+m1prime+wave1`.
- `annotation_socket/tests/test_m1_prime.py` — NEW.
- `cnfa_algs/wave1_ops.py` — NEW: 9 classical-CV operators (v2a_004/009/011/013/014/015/081/088/094).
- `cnfa_algs/street_noise.py` — NEW: facade energy model × ISO 3382-3 masking (spec in
  `docs/STREET_NOISE_ACOUSTIC_OPERATOR_SPEC_2026-07-19.md`).
- `cnfa_algs/hedonics.py` — REGRESSION FIX (`66d6ec1e`): V7 delicensed again; verify it holds in HEAD
  AND working tree.
- Context: `docs/SPRINT_COMPCORRECT_ALGORITHMS_2026-07-19.md`, `docs/CNFA_VALIDATION_METHODOLOGY_2026-07-19.md`.

## Run first (report literally)
1. `PYTHONPATH=. python3 annotation_socket/tests/test_m1_prime.py` and the other 5 test files.
2. `PYTHONPATH=. python3 -m cnfa_algs.wave1_ops` and `PYTHONPATH=. python3 -m cnfa_algs.street_noise`.
3. `PYTHONPATH=. python3 -m annotation_socket.run_stage /tmp/codex_attack_s0s2 'Example Images/korridor.jpg'
   'Example Images/50-day-street-offices-norwalk-1200x1165-compact.jpg'
   'Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg'` — expect 36/36
   scored on AMBER units, negative control RED, run2 zero work.

## Attack surfaces (in priority order)
**A1 — M1′ can be gamed?** The tamper test re-forges the digest and is caught because verify RECOMPUTES
from bytes. Find a path around it: (a) a record whose `m1p.stats` are copied from a DIFFERENT image that
digests the same after 6-decimal rounding; (b) exploit `load_for_m1p` drift — it duplicates the
annotator's load/resize inline; change one and show the other silently diverges; (c) the `color_palette`
class coarsens rounding (centers 1dp) "for BLAS jitter" — quantify how much tamper fits UNDER that
rounding (is a 0.05-entropy shift catchable?); (d) missing-block demotion: an attacker who STRIPS m1p
gets AMBER, same as legacy — is that consistent with the fail-closed philosophy, and can an AMBER unit's
stripped record still reach acceptance anywhere?
**A2 — Wave-1 method-string honesty.** For each of the 9: does the code compute what the method string
says? Hunt for: McCamy validity range abuse (clusters near the locus edge), the shadow operator's
chromaticity test misclassifying colored-light boundaries (a warm sunset shadow IS a chromaticity
change — does it get rejected as material, biasing softness?), texture_density's structure mask on
wallpaper (periodic pattern = edges = masked out = texture undercounted?), orderliness' mode-neighbor
zeroing (m2 selection when the histogram is bimodal-adjacent), evening_ambience's fixed weights
[0.45/0.35/0.20] (pure inventions — are they at least declared as such everywhere consumer-visible?).
**A3 — calibration honesty.** W1.1 fullscale=60, W1.2 ramp 0.045/soft-flag 0.02, W1.6 2% pool cap +
0.02 soft-sat scale were fit on NINE images from ONE image set. Attack: are these constants declared as
smoke-calibrated in every consumer-visible surface (registry note, method, extras)? Do any tests
hard-code them so a corpus refit would silently break?
**A4 — socket contract.** The None-scalar → UNKNOWN(`signal_undefined`) path: UNKNOWN REDs a unit by M5.
Construct an image where a Wave-1 operator legitimately abstains (e.g. blank wall photo → shadow_softness
undefined) and show whether an otherwise-honest unit goes RED. Is that the right behavior, or does it
punish honesty? Recommend (do not implement) the resolution; this is a standing design question (D-S2.1).
**A5 — street-noise physics.** Check the invariants' completeness: is there a configuration where the
inverted-U test passes trivially (e.g. COMFORT_MAX below noise_min everywhere)? Is the single-zone
Sabine limitation stated everywhere the fields are consumed? Does the registry `requires`
({outdoor_leq, facade_spec}) match what the function actually needs (facade_row? Rp per column? alpha)?
The annotator has NO binding for it — confirm it abstains rather than UNKNOWNs on plan-input units.
**A6 — regression seal.** `git show HEAD:cnfa_algs/hedonics.py | grep -c "DESIGNATED hedonic"` must be
0 and working tree must match HEAD for that block. Also confirm V7 `licensed=False` by executing.

## Output
`docs/CODEX_ATTACK_S0S2_VERDICT_2026-07-19.md`: per-surface findings with severity (HIGH/MED/LOW),
each with the executed evidence (command + output) or marked unverified. Commit ONLY that doc — do not
modify the batch files; recommendations in prose. Do not touch other dirty/untracked files. No push.
