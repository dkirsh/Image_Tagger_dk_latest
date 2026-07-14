# cnfa_algs — operational CNfA attribute algorithms (v0.1, 2026-07-13)

Working implementations of the CNfA attribute stubs, with **regional annotation,
global scalars, and heatmaps/topo-contours** for every attribute. Companion code to
`docs/CNFA_ATTRIBUTE_INVENTORY_AND_ALGORITHMS_2026-07-13.md` — Section 4 of that
document, made runnable.

## The strategy: one algorithm family, three fidelity tiers

| Tier | Input | Fidelity | What runs |
|---|---|---|---|
| **A** (M1/M2) | single photo (+ depth/seg) | approximate | image-plane heatmaps & overlays |
| **B** (M2.5) | single photo → **inferred floor plan** | approximate, confidence-discounted | TRUE plan-space fields on the inferred plan |
| **C** (M3) | supplied floor plan / BIM section | precise | the SAME plan-space fields, undiscounted |

Tier B is the bridge: monocular depth + plane segmentation → backproject the
visible floor to a ground-plane occupancy grid (an *inferred mini floor plan*) →
run isovist-field, prospect, refuge, and seat-choice algorithms on it. Tier C
runs the identical `isovist_fields()` code on a real plan. **Approximate from 2D,
precise from a plan, same code path** — so every Tier-B result upgrades for free
when a plan or 3D model arrives.

## Depth convention (matches the Image Tagger)

Set `DEPTH_ANYTHING_ONNX_PATH` to a monocular-depth ONNX model → network depth
(M2, conf 0.7). Unset → geometric fallback: vanishing point + flat-floor
ground-plane depth `Z = f·h/(y − y_horizon)` (M2-geo, conf 0.35). All confidences
propagate into every result.

## Modules

- `core.py` — `AttributeResult` schema (scalar, field, evidence regions,
  confidence, method, failure_modes, extras) matching the repo's Operational
  Rule; heatmap-with-iso-contours, mask, region, and gallery renderers.
- `geometry.py` — vanishing point; heuristic floor/ceiling/wall/opening
  segmentation (hook: pass a real label map via `segment_planes(..., provided=)`);
  `DepthProvider` (ONNX or geometric).
- `attributes.py` — Tier A algorithms: brightness_variance, edge_clarity,
  symmetry_horizontal, palette_entropy, processing_load, fractal_dimension_local,
  glare_risk, warmth_ratio, vertical_illuminance_proxy, enclosure_index,
  prospect, landmark_salience, acoustic_absorption (material→α→RT_rel),
  sociopetal_seating (detector-pluggable scorer).
- `plan.py` — Tier B `infer_plan_from_image()`; Tier C
  `plan_from_floorplan_image()`; shared `isovist_fields()` (openness, prospect,
  refuge, compactness, prospect-refuge seat-choice map), camera isovist,
  topo-map renderer.

## Run

```bash
python3 cnfa_demo/run_demo.py path/to/interior.png outdir/   # Tiers A + B
python3 cnfa_demo/run_tierC.py                               # Tier C on a drawn plan
```

Outputs per image: `*_0_diagnostics.png` (planes, depth), `*_1_tierA.png`
(attribute gallery), `*_2_tierB_plan.png` (inferred-plan topo maps),
`*_results.json` (all scalars + confidence + method + failure modes).

## Honest limits (v0.1)

- Plane segmentation is a k-means + prior heuristic (conf 0.45); plug a real
  segmenter for production. Wall art can misread as opening.
- Geometric depth assumes level camera + flat floor; scale depends on the
  vanishing-point estimate — **do not compare absolute metric scalars across
  images** without a real depth model (the per-image confidence tells you when).
- The inferred plan covers the *visible* room only; rays stop at the visibility
  boundary. That is a feature (honesty), not a bug.
- Sociopetal scorer needs seat boxes+facings from a detector/VLM; the demo uses
  manual boxes.
- Acoustic proxy is relative (echoey↔dead ranking). Absolute RT60 seconds
  requires a metric scale cue; deliberately not emitted.
