# Student Sprint S1 Direct Statistics Acceptance Report

Date: 2026-07-08  
Repo: Image_Tagger_dk_latest  
Active app root: Image_Tagger_3.4.74_vlm_lab_TL_runbook_full  
Status: ACCEPTED  

## Sprint goal

Sprint S1 implements deterministic direct image statistics with no VLM calls. The implemented outputs are canonical CNfA feature keys already present in backend/science/features_canonical.jsonl.

## Implemented canonical feature keys

* cnfa.fluency.processing_load_proxy
* cnfa.light.brightness_variance
* cnfa.fluency.edge_clarity_mean
* cnfa.fluency.color_palette_entropy
* cnfa.fluency.symmetry_score_horizontal
* cnfa.fractal_dimension

## Files changed / added

* backend/science/math/architectural_primitives.py
* backend/science/pipeline.py
* backend/science/feature_stubs.py
* tests/test_architectural_direct_stats.py
* tests/fixtures/architectural_tags/
* backend/science/math/mpib_low_level.py

## Implementation summary

Added ArchitecturalPrimitivesAnalyzer as a deterministic OpenCV/NumPy analyzer. It computes six Sprint S1 direct-statistics values and writes them using frame.add_attribute(...), so they are persisted through the existing AnalysisFrame attribute pathway.

The analyzer is integrated into SciencePipelineConfig as enable_architectural_primitives and is enabled by default when enable_all=True. It runs with the low-level deterministic math analyzers before heavier optional VLM or segmentation paths.

## Measurement methods

### cnfa.fluency.processing_load_proxy

Compression/entropy-based proxy combining zlib compression ratio, color palette entropy, edge density, and brightness variance. Higher values indicate higher visual processing load proxy.

### cnfa.light.brightness_variance

Normalized grayscale luminance variance in [0,1]. Higher values indicate stronger luminance variation.

### cnfa.fluency.edge_clarity_mean

Mean Sobel gradient magnitude on Canny edge pixels, normalized to [0,1]. Higher values indicate sharper/crisper detected edges.

### cnfa.fluency.color_palette_entropy

Deterministic quantized RGB histogram entropy. Higher values indicate more diverse color palettes.

### cnfa.fluency.symmetry_score_horizontal

Pixel-level left-right mirror similarity after horizontal flip, normalized to [0,1]. Higher values indicate stronger bilateral symmetry.

### cnfa.fractal_dimension

Normalized box-counting fractal dimension proxy over Canny edges. Higher values indicate more edge-structure complexity.

## Fixtures

Created deterministic synthetic fixtures under tests/fixtures/architectural_tags/:

* flat.png
* high_edge.png
* high_color.png
* symmetric.png
* asymmetric.png
* low_brightness_variance.png
* high_brightness_variance.png
* README.md

## Validation commands run

    PYTHONPATH=. pytest tests/test_architectural_direct_stats.py -v | tee reports/STUDENT_SPRINT_S1_DIRECT_STATS_TEST_OUTPUT_2026-07-08.txt

Result:

    5 passed

Combined validation command:

    PYTHONPATH=. pytest tests/test_mpib_low_level.py tests/test_feature_registry_coverage.py tests/test_architectural_direct_stats.py -v | tee reports/S1_DIRECT_STATS_VALIDATION_BUNDLE_2026-07-08.txt

Result:

    9 passed

## Fixture direction checks

* high_brightness_variance > low_brightness_variance for cnfa.light.brightness_variance
* high_edge > flat for cnfa.fluency.edge_clarity_mean
* high_color > flat for cnfa.fluency.color_palette_entropy
* symmetric > asymmetric for cnfa.fluency.symmetry_score_horizontal
* high_edge >= flat for cnfa.fractal_dimension
* high_color > flat for cnfa.fluency.processing_load_proxy

## Determinism and safety checks

* Direct stats are deterministic across repeated runs on the same image.
* All six output keys are finite numeric values.
* All six output values are clamped to [0,1].
* Blank images fail safely with finite values.
* No VLM calls are used.

## Baseline cleanup completed before S1

Before Sprint S1 implementation, the MPIB verification test exposed an OpenCV Hough line shape compatibility issue in backend/science/math/mpib_low_level.py. The edge-density line unpacking was patched by flattening each Hough line before unpacking coordinates. After patching, tests/test_mpib_low_level.py passed fully.

The registry coverage test also had pre-existing baseline dangling keys for affordance, room-function, and style registry entries. These were added to backend/science/feature_stubs.py as intentional stubs because they are not part of the deterministic S1 direct-stat implementation.

## Known limitations / failure modes

* These are 2D image statistics and do not infer true 3D geometry.
* Edge metrics are sensitive to blur, resolution, and image compression.
* Palette entropy can increase because of noise or artifacts.
* Symmetry score measures pixel-level mirror similarity, not semantic design symmetry.
* Fractal dimension is a box-counting proxy over Canny edges, not a full architectural complexity model.

## Final status

ACCEPTED
