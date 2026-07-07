# Image Tagger Visual Attribute Inventory

Generated: 2026-07-07 12:40 CEST

## Live Surface

The live application surface found in this repo is:

`/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`

Important live files:

- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/contracts/attributes.yml`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/science_tag_coverage_v1.json`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/feature_stubs.py`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/science/features_canonical.jsonl`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/SCIENCE_TAG_MAP.md`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/docs/science_overview.md`

## Max Planck / MPIB Materials Located

The Max Planck image feature import is present here:

- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/image_decomposition/README.md`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/image_decomposition/load_featureheaders.csv`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/image_decomposition/mainScript.m`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/image_decomposition/ImageDecomposer.m`

The README identifies the project as "Image Decomposer", by Izabela Maria Sztuka, Center for Environmental Neuroscience, Max Planck Institute for Human Development, with a contact at `mpib-berlin.mpg.de`.

The raw header file has 59 columns: one image column plus 58 numeric feature columns. These are:

`EdgeDensity`, `EdgeBareCanny`, `EdgeLog`, `EdgeLogFT`, `Hue`, `Sat`, `Brightness`, `sdHue`, `stSat`, `stBright`, `Entropy`, `EDlev1`, `EDlev2`, `EDlogLev`, `labL`, `labA`, `labB`, `sdLabL`, `sdLabA`, `sdLabB`, `EDH0`, `EDS0`, `EDV0`, `EDL0`, `EDA0`, `EDB0`, `EtrH`, `EtrS`, `EtrV`, `EtrL`, `EtrA`, `EtrB`, `SED`, `NSED`, `ED`, `DF`, `DF_SD`, `pixR`, `pixY`, `pixG`, `pixC`, `pixB`, `pixM`, `pixW`, `CEgray`, `CEblueyellow`, `CEredgreen`, `SCgray`, `SCblueyellow`, `SCredgreen`, `Betagray`, `Betablueyellow`, `Betaredgreen`, `Gammagray`, `Gammablueyellow`, `Gammaredgreen`, `total_energy`, `PowerSpectrumMean`.

These group into edge density, HSV/Lab color, entropy, straight/non-straight edges, fractal dimension, color pixel proportions, LGN image statistics, and spectrum/energy features.

## Python MPIB Port Located

There is also an older Python port of the MPIB feature set in the historical `TRS_v1.1` tree:

- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/TRS_v1.1/backend/science/L0_proximal/features.py`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/TRS_v1.1/backend/science/low_level/unified.py`

This port defines 20 named MPIB keys:

`brightness_mean`, `brightness_sd`, `color_pct_blue`, `color_pct_green`, `color_pct_red`, `color_pct_neutral`, `contrast_rms`, `entropy_shannon`, `edge_density_straight`, `edge_density_nonstraight`, `edge_density_total`, `symmetry_mse`, `symmetry_ssim`, `hsv_hue_mean`, `hsv_hue_sd`, `hsv_saturation_mean`, `hsv_saturation_sd`, `hsv_value_mean`, `hsv_value_sd`, `power_spectrum_mean`.

The unified historical extractor says it combines MPIB Berlin features with MATLAB-ported features into about 50+ low-level features.

## Live Canonical Math Already Implemented

The active v3.4.74 code has Python analyzers for many related low-level features, but it does not directly expose the MPIB MATLAB header names.

Implemented active analyzers include:

- color: `/backend/science/math/color.py`
- complexity: `/backend/science/math/complexity.py`
- fractals: `/backend/science/math/fractals.py`
- texture: `/backend/science/math/glcm.py`
- regional frequency: `/backend/science/math/regional_frequency.py`
- spatial frequency: `/backend/science/math/spatial_frequency.py`
- depth/clutter proxies: `/backend/science/spatial/depth.py`
- isovist proxies: `/backend/science/spatial/isovist.py`, `/backend/science/spatial/isovist_25d.py`
- material heuristics: `/backend/science/vision/materials.py`
- room detection: `/backend/science/vision/room_detection.py`

`docs/science_overview.md` says the current canonical default enables color, complexity, texture, fractals, spatial, affordance, room detection, and basic materials; segmentation, cognitive VLM, semantic VLM, materials VLM, and CLIP materials are off by default.

## Goldilocks Computational Candidates

The small Goldilocks seed file is present in both the live app and historical TRS tree:

- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/backend/data/goldilocks_attributes.csv`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/TRS_v1.1/backend/student_app/data/goldilocks_attributes.csv`

It names four attributes with proposed computational methods:

| Feature | Proposed method |
|---|---|
| `cnfa.fluency.processing_load_proxy` | `JPEG file size / total_pixels` |
| `cnfa.fluency.clutter_density_count` | `count(objects)/area(room_floor)` |
| `cnfa.fluency.symmetry_score` | `SSIM(image, flipped)` |
| `cnfa.spatial.prospect` | `Isovist Raycast > 5m` |

Later v3.4.74 names differ slightly:

- `cnfa.fluency.symmetry_score` became `cnfa.fluency.symmetry_score_horizontal`
- `cnfa.spatial.prospect` became partly `cnfa.spatial.prospect_to_refuge_ratio`, while `spatial.isovist_openness` and `spatial.central_openness` are live lower-level proxies.

## Stubbed CNFA Attributes Still Needing Real Compute

`science_tag_coverage_v1.json` reports 145 tracked keys, 69 stubs, and 30 CNFA stubs. The CNFA stubs are:

- `cnfa.biophilic.natural_material_ratio`
- `cnfa.cognitive.activity_zones_count`
- `cnfa.cognitive.landmark_salience`
- `cnfa.cognitive.legibility_score`
- `cnfa.dynamic.optic_flow_magnitude`
- `cnfa.dynamic.path_glare_max`
- `cnfa.dynamic.reflection_flow`
- `cnfa.dynamic.revelation_rate`
- `cnfa.dynamic.texture_gradient`
- `cnfa.fluency.anomaly_count`
- `cnfa.fluency.clutter_density_count`
- `cnfa.fluency.color_palette_entropy`
- `cnfa.fluency.edge_clarity_mean`
- `cnfa.fluency.figure_ground_clarity`
- `cnfa.fluency.hierarchy_depth`
- `cnfa.fluency.pattern_rhythm_regularity`
- `cnfa.fluency.processing_load_proxy`
- `cnfa.fluency.symmetry_score_horizontal`
- `cnfa.fluency.visual_entropy_spatial`
- `cnfa.fluency.zoning_clarity`
- `cnfa.fractal_dimension`
- `cnfa.haptic.soft_surface_ratio`
- `cnfa.haptic.texture_variation_index`
- `cnfa.light.brightness_variance`
- `cnfa.light.diffuse_vs_direct_ratio`
- `cnfa.light.vertical_illuminance_proxy`
- `cnfa.light.warm_vs_cool_ratio`
- `cnfa.spatial.ceiling_height_avg`
- `cnfa.spatial.enclosure_index`
- `cnfa.spatial.prospect_to_refuge_ratio`

## First Computational Sprint Candidates

The safest first sprint should not begin with VLM-dependent semantics. It should implement deterministic or mostly deterministic bridges from existing low-level analyzers:

1. `cnfa.fluency.processing_load_proxy`: JPEG bytes per pixel.
2. `cnfa.fluency.symmetry_score_horizontal`: reuse existing SSIM/mirror method from the MPIB port or current symmetry code.
3. `cnfa.light.brightness_variance`: grayscale standard deviation.
4. `cnfa.fluency.edge_clarity_mean`: Canny/Sobel edge gradient sharpness.
5. `cnfa.fluency.color_palette_entropy`: k-means palette proportions plus Shannon entropy.
6. `cnfa.fractal_dimension`: bridge from existing `fractal.D`.
7. `cnfa.fluency.visual_entropy_spatial`: object-center histogram entropy, gated on object detection/segmentation availability.
8. `cnfa.fluency.clutter_density_count`: object count normalized by visible floor or image area, initially image-area fallback if no room floor estimate is present.
9. `cnfa.biophilic.natural_material_ratio`: bridge from material coverage proxies, with explicit low-confidence status until segmentation/VLM surface area estimates are enabled.

## Caveats

1. The MPIB MATLAB feature headers are not directly wired into the active v3.4.74 canonical app.
2. `features_canonical.jsonl` is not normal JSONL: it uses literal `\n` separators in at least part of the file and needs special parsing.
3. Several registry entries are marked `active` in `features_canonical.jsonl` while coverage marks them `stub_only`. For operational truth, use `science_tag_coverage_v1.json` and `backend/science/feature_stubs.py`.
4. The live canonical docs say affordance inference is not reliable in the current environment because of a LightGBM pickle compatibility issue.
