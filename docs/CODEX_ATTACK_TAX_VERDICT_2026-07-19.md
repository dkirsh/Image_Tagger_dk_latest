# CODEX ATTACK TAX VERDICT 2026-07-19

Prompt start: 2026-07-19 14:49 PDT.
Resumed attack segment: 2026-07-19 15:24 PDT.
Verdict written: 2026-07-19 16:53 PDT.

Repo: `/Users/davidusa/REPOS/Image_Tagger_dk_latest`
Branch: `cnfa-algs-2026-07-14`
Prompt manifest expected HEAD: `fde0e2dc`
Actual HEAD attacked: `88e55989`

Overall line:

`GATE: FAIL (TAX-0, FC-1, FC-2, CP-1, CP-2, W2-1)`

The decisive failures are operational, not philosophical: the faithful FC/SE path cannot run in the present repo environment because `visual_clutter` imports `skimage`, and a real socket smoke over three images goes RED because FC/SE become UNKNOWN. Several taxonomy probes also show that the new semantic complexity partition is honest about being AMBER, but not yet precise enough to be treated as a robust semantic classifier.

## Commands Run

Direct prompt-required per-file commands:

| Command | Result |
|---|---|
| `python3 cnfa_algs/clutter_stack.py` | RC 1, `ImportError: attempted relative import with no known parent package` |
| `python3 cnfa_algs/complexity_partition.py` | RC 1, same relative-import failure |
| `python3 cnfa_algs/faithful_clutter.py` | RC 1, same relative-import failure before its own self-test can run |
| `python3 cnfa_algs/wave2_geometry.py` | RC 1, same relative-import failure |

Module-form self-tests:

| Command | Result |
|---|---|
| `PYTHONPATH=. python3 -m cnfa_algs.clutter_stack` | PASS |
| `PYTHONPATH=. python3 -m cnfa_algs.complexity_partition` | PASS |
| `PYTHONPATH=. python3 -m cnfa_algs.faithful_clutter` | FAIL, `ModuleNotFoundError: No module named 'skimage'` |
| `PYTHONPATH=. python3 -m cnfa_algs.wave2_geometry` | PASS |
| `python3 -m cnfa_algs._pyrtools_min` | PASS |

Socket tests:

| Command | Result |
|---|---|
| `PYTHONPATH=. python3 annotation_socket/tests/test_m1_prime.py` | PASS |
| `PYTHONPATH=. python3 annotation_socket/tests/test_reliable_attrs.py` | PASS |
| `PYTHONPATH=. python3 annotation_socket/tests/test_v9_fractal_band.py` | PASS |
| `PYTHONPATH=. python3 annotation_socket/tests/test_f7_ridge_boundary.py` | PASS |
| `PYTHONPATH=. python3 annotation_socket/tests/test_c01_triangulation.py` | PASS |
| `PYTHONPATH=. python3 annotation_socket/tests/test_c29_stranded.py` | PASS |

Real stage smoke:

```
PYTHONPATH=. python3 -m annotation_socket.run_stage /tmp/codex_attack_tax_stage \
  'Example Images/korridor.jpg' \
  'Example Images/50-day-street-offices-norwalk-1200x1165-compact.jpg' \
  'Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg'
```

Observed:

```
[controller] queue: 3 units
[worker] run1 processed=3 skipped=0
[checker] verdicts: GREEN=0 AMBER=0 RED=3
[negative-control] REJECTED (RED), absent from accepted/
[worker] run2 processed=0 skipped_content_addressed=3
[authority] worker write to control.jsonl DENIED (BoundaryError)
[authority] worker write to accepted/ DENIED (BoundaryError)
```

Quarantine inspection: each real unit had `total_registry=61`, `applicable=42`, `abstained=19`; all three had UNKNOWN `cnfa.fluency.feature_congestion` and `cnfa.fluency.subband_entropy` with `compute_failed:ModuleNotFoundError`. One unit also had C01/C29 `anchor_registration_unconfident`.

## Target 1: `clutter_stack.py`

| ID | Severity | Claim | Reproduction pointer |
|---|---:|---|---|
| TAX-0 | BROKEN | The prompt-required invocation style is broken for all four attacked modules. Each has a direct `python3 file.py` path, but direct execution fails on relative imports. | `python3 cnfa_algs/clutter_stack.py`, `python3 cnfa_algs/complexity_partition.py`, `python3 cnfa_algs/faithful_clutter.py`, `python3 cnfa_algs/wave2_geometry.py`; all RC 1. |
| CS-1 | CLEAN | `proto_object_count` did not change count under a simple same-scene scale attack at 256, 512, and 1024 px. | Eight colored blobs scaled proportionally: count was 9 at all three sizes; scalar was 0.0225 at all three. Density changed, but the registry score uses count/fullscale, not density. |
| CS-2 | CLEAN | Degenerate one-color and 1-4 px-wide images abstain instead of crashing. | 120 x 1/2/3/4 px flat BGR images returned `scalar=None`, method `ABSTAIN: near-blank image`. |
| CS-3 | FRAGILE | Alpha-channel input does not crash, but the semantics are accidental: OpenCV conversion effectively ignores alpha. This should be declared or normalized at the socket boundary. | 120 x 160 x 4 RGBA flat field: proto and MSG abstained; MUC scored a low value `0.001831...`, treating the color data as ordinary image input. |
| CS-4 | CLEAN | MSG and MUC are labeled as proxies, and the method strings do not claim literal Rosenholtz 2007 FC/SE. | Registry notes: `MSG-inspired ... PROXY`, `MUC-inspired ... PROXY`. |
| CS-5 | CLEAN | The known `cv2.connectedComponentsWithStats(..., connectivity=4)` regression is fixed in `clutter_stack.py`; I found no other silent positional connectivity call in this file. | Source inspection: keyword `connectivity=4` is used for proto-object components. |

## Target 2: `complexity_partition.py`

| ID | Severity | Claim | Reproduction pointer |
|---|---:|---|---|
| CP-1 | DISHONEST | Not all load-bearing taxonomy constants are surfaced in `extras`, although the prompt explicitly asks that every tuned constant be declared. | Probe `complexity_partition(green_stone_wall).extras["constants"]` returned only `min_zone_frac`, `green_hue`, `green_sat_min`, `green_frac_gate`, `d_band`, `r2_min`, `edge_dense`. Missing from extras: `MAT_TEXTURE_MIN`, `MAT_HUE_STD_MAX`, wood thresholds, `FIRE_LUM_MIN`, `FIRE_STD_MIN`, `PERIODIC_PEAK_MIN`, `ORNAMENT_PEAK_MIN`, `COHERENCE_MIN`, `ART_FRAME_EDGE_MIN`, and the 4-connectivity merge rule. |
| CP-2 | BROKEN | Blue wall plus a specular oval is classified mainly as `water`, a semantic false positive caused by chromatic/smoothness gates. | Synthetic 240 x 320 BGR wall `(190,150,90)` with bright oval: `area_fracs.water=0.7285`, `biophilic_total=0.7285`, scalar `0.0`. There is no water in the fixture. |
| CP-3 | FRAGILE | A framed mirror is partly classified as `biophilic_material`, `sky_daylight`, and `ornament_pattern`; no `art_candidate` fired. The art/mirror/frame boundary is not robust. | Synthetic framed mirror: `biophilic_material=0.3143`, `sky_daylight=0.1429`, `ornament_pattern=0.1571`, `art_candidate=0`. |
| CP-4 | FRAGILE | Bright textured white ceiling is treated as `junk_clutter=1.0`. That may be a defensible negative texture result, but it shows how the sky/ceiling/junk distinction rests on hand-tuned thresholds. | Synthetic bright noisy ceiling: scalar `1.0`, `area_fracs.junk_clutter=1.0`, zone D `1.861`, R2 `0.998`. |
| CP-5 | CLEAN | Green-tinted stone did not get stolen by the vegetation gate in the constructed grid-wall attack. | Synthetic green stone wall: `ordered_structure=0.8571`, `ornament_pattern=0.1429`, `biophilic_vegetation=0.0`, despite `green_frac=1.0` in zones. |
| CP-6 | CLEAN | Tiny/blank zones abstain rather than emit garbage D. Taylor/Hagerhall band is emitted as a flag, not used as a gate in the score. | 24 x 24 flat image returned `scalar=None`, `ABSTAIN: near-blank image`; zone outputs contain `in_preferred_band` as metadata. |
| CP-7 | CLEAN | Hedonic tags are marked as hypotheses/unlicensed and are not consumed by the socket as scored values. | Source and grep: registry says `hedonic HYPOTHESES`; `complexity_partition.py` says `HEDONIC LICENSING... NOT licensed`; no downstream socket consumer of `hedonic_hypothesis` found. |
| CP-8 | FRAGILE | Merge adjacency is 4-connected but not surfaced in extras or method. For a tile merge classifier, 4-vs-8 adjacency is a real semantic choice. | Source inspection: merge uses `cv2.connectedComponentsWithStats(m, connectivity=4)`, but extras/method do not declare `connectivity=4`. |

## Target 3: `faithful_clutter.py`, `_pyrtools_min.py`, and vendor

| ID | Severity | Claim | Reproduction pointer |
|---|---:|---|---|
| FC-1 | BROKEN | Faithful Feature Congestion and Subband Entropy cannot run in this repo environment because the unmodified vendored package imports `skimage`, which is not installed. This breaks direct module self-test, the reference comparison harness, and socket annotation. | `PYTHONPATH=. python3 -m cnfa_algs.faithful_clutter` fails with `ModuleNotFoundError: No module named 'skimage'`; `python3 scripts/reference_clutter_compare.py --backend shim --env codex_attack --out /tmp/codex_attack_clutter_shim.json` fails the same way. |
| FC-2 | BROKEN | The real stage smoke goes RED solely or partly because FC/SE compute failures become UNKNOWN. This means the current registered predicates are not operationally registerable as image-only predicates until dependency packaging is fixed. | `/tmp/codex_attack_tax_stage` verdicts: `GREEN=0 AMBER=0 RED=3`; quarantine records show UNKNOWN `cnfa.fluency.feature_congestion` and `cnfa.fluency.subband_entropy`, reason `compute_failed:ModuleNotFoundError`. |
| FC-3 | DISHONEST | Registry notes say `ADJUDICATED reference port` and "AMBER pending CORPUS construct validation only", but the current environment cannot execute the reference. The remaining blocker is dependency/runtime, not only corpus validation. | `annotation_socket/registry.py` notes for FC/SE, plus failing self-test/harness above. |
| FC-4 | CLEAN | Vendor integrity passed: the vendored Python files are byte-identical to the wheel files. | Compared `cnfa_algs/_vendor/visual_clutter/{__init__.py,clutter.py,utils.py}` to `reference/visual_clutter-1.0.7-py3-none-any.whl`; all sha256s identical. |
| FC-5 | CLEAN | `_pyrtools_min.py` self-test passes its internal invariants. | `python3 -m cnfa_algs._pyrtools_min`: Gaussian shapes/DC gain, upConv, steerable mask complementarity, angular identity, determinism all PASS. |
| FC-6 | FRAGILE | Near-blank guard works below the threshold, but the threshold itself is not surfaced as `std_threshold_dn`; and any texture above the threshold currently crashes on missing `skimage`. | Noise std probes: std 0.0, 1.9, 2.0, 2.1 all abstained with observed `std_dn` below 2.0 after uint8 quantization; std 8.0 raised `ModuleNotFoundError`. Extras show `std_dn`, not the threshold. |
| FC-7 | CLEAN | P3 exposure is declared in the faithful module failure modes: package collapse lacks MATLAB x4 upConv gain. | `faithful_clutter.py` failure_modes includes package-vs-MATLAB caveat for FC/SE. |

## Target 4: `wave2_geometry.py`

| ID | Severity | Claim | Reproduction pointer |
|---|---:|---|---|
| W2-1 | BROKEN | The prompt asks for six ops, but this file currently implements only two: `verticality_cues` and `choice_richness_zones`. The missing ops should be DO-NOT-REGISTER-YET: ceiling openness, double-height flag, blind corners, barrier permeability, and thresholds. | Source header explicitly says these are deferred: W2.2, W2.3, W2.4, W2.5, W2.8. |
| W2-2 | CLEAN | Implemented W2.1 verticality handles blanks and too-few-segment cases by abstaining, and the self-test catches rolled-camera failure. | `python3 -m cnfa_algs.wave2_geometry` PASS; blank returned `ABSTAIN: 0 segments < 20`; horizontal fixture returned `ABSTAIN: 16 segments < 20`; rolled 20 deg colonnade abstains. |
| W2-3 | CLEAN | Implemented W2.6 is explicitly downstream of inferred plan/C13 and admits AMBER confidence. | Source: `choice_richness_zones(pg)` uses `classify_settings(pg)`, confidence `min(0.4, cs["confidence"])`, failure mode says usable choice needs occupancy/affordance labels. |
| W2-4 | FRAGILE | W2.1 is continuous but rests on image-plane verticality and LSD segment count; reasonable low-segment interiors can abstain. That is honest AMBER behavior, but it is not a broad-coverage registered metric yet. | Direct probe on horizontal line fixture abstained because only 16 segments were detected, below `VERT_MIN_SEGMENTS=20`. |

## Cross-Cutting Socket and Determinism

| ID | Severity | Claim | Reproduction pointer |
|---|---:|---|---|
| X-1 | CLEAN | `MAY_LACK_SIGNAL` is enforced for sanctioned signal-absent abstentions, and a blank image verifies AMBER, not RED, when operators provide absence evidence. | Blank 220 x 280 image through `annotate_image` then `verify_record(replay=True)`: tier AMBER; coverage `scored=30`, `unknown=0`, `abstained=31`; verifier problems `[]`. |
| X-2 | CLEAN | M1-prime strict gate is not bypassed. Removing one emitted M1-prime block from a scored bound predicate turns verification RED. | Removed `m1p` from `cnfa.light.brightness_variance`; `verify_record` returned RED with `M1_PRIME:cnfa.light.brightness_variance:missing_stats`. |
| X-3 | CLEAN | Worker/controller boundary and idempotency survived the real stage smoke. | Negative control rejected RED; second worker run processed zero units; worker writes to `control.jsonl` and `accepted/` denied with `BoundaryError`. |
| X-4 | FRAGILE | Full-stage determinism is not meaningful while FC/SE are registered but non-runnable: replay can only prove the same failure mode. | Real stage smoke proves idempotent quarantine/verdict behavior, but not faithful FC/SE numerical determinism. |

## Attacks Not Run or Not Completed

1. I did not run the `--backend real` pyrtools comparison because the local blocker is earlier: the vendored `visual_clutter` path cannot import `skimage`, and the prompt asked for no dependency installation.
2. I did not produce a real Mac-vs-sandbox FC/SE numeric adjudication file because `scripts/reference_clutter_compare.py --backend shim` fails before writing output.
3. I did not construct fixtures for missing Wave-2 operators because the source file explicitly defers those operators and exposes no callable implementation for them.
4. I did not run a separate two-process JSON equality harness for faithful FC/SE because those operators fail before producing values. Other module self-tests include deterministic reruns for clutter stack, complexity partition, `_pyrtools_min`, and wave2 geometry.
5. I did not edit any batch or algorithm files. This report is the only intended artifact.

## Final Recommendation

Do not pass this batch as registerable. The clean items are real: vendor bytes match the wheel, M1-prime is strict, signal-absent handling is much better, and several proxy methods are honestly labeled. But the faithful FC/SE dependency failure is a hard stop, and the taxonomy constants/semantic gates need fuller declaration and corpus calibration before anyone can read the 11-class partition as more than an AMBER heuristic.
