# Licensing position

You intend to license the cognitive-code system commercially and to keep it
defensibly yours, so the licence class of every dependency is tracked in code
(`base.License`) and enforced by the gate in `registry.select_adapters(policy=)`.
A `"commercial"` build enables **permissive only**; the `"research"` build may
enable everything (for validation, never for shipping).

## Permissive — safe to embed in the commercial product

| adapter | upstream | licence |
|---|---|---|
| `aesthetics_toolbox` | Aesthetics-Toolbox (rbartho) | **MIT** |
| `visual_clutter` | visual-clutter (kargaranamir) | **MIT/BSD** |
| `colour_science` / `colour_opponent` | colour-science; scikit-image | **BSD** |
| `skimage_texture` | scikit-image | **BSD** |
| `mahotas_texture` | mahotas | **MIT** |
| `proximal_stats` | native (numpy/scipy/scikit-image/OpenCV) | permissive |
| `depth_midas` (worker) | MiDaS | **MIT** — prefer MiDaS or Depth-Anything-V2-**small** (Apache) over DAv2-large (CC-BY-NC) |
| `segmentation_sam` (worker) | SAM | **Apache-2.0** — SAM weights are Apache; some OneFormer/Mask2Former **weights are CC-BY-NC**, so pick a commercial-safe ADE20K checkpoint |

## Research / non-commercial — gate to the validation build only

| adapter | why gated |
|---|---|
| `saliency_deepgaze` | DeepGaze **weights are research-only**. Use the bundled spectral-residual fallback (licence-clean) as the permissive substitute in a shipped build. |
| `memorability` | ResMem weights are **UChicago non-commercial** (for-profit *internal research* allowed; productising needs a licence). ViTMem similar. |
| `aesthetic_score` | pyiqa *code* is Apache, but several *weights* and the AVA/TAD66K training provenance are research-only. These outputs are **validation-only** (`cnfa.evaluation.*`), never scored features. |
| `material_from_image` | perceived-gloss / intrinsic-decomposition models are academic-use / GPL. For a commercial build, use the permissive Motoyoshi luminance/sub-band-skew gloss cues in `proximal_stats` instead. |

## Copyleft — never embed (consume outputs, or reimplement)

Not wrapped here, but flagged from the survey so they don't creep in:
depthmapX (GPL), Ladybug/Honeybee & sDNA+ (AGPL), material-appearance-similarity
& material-illumination-geometry (GPL-2.0), Rosenholtz TTM (GPL-2.0), pyvispoly
(GPL via CGAL). Use them as **offline analysis tools whose results you import**,
or reimplement the (usually simple) maths under your own licence — never link
them into the shipped product.

## The quiet trap: non-commercial *weights* under permissive *code*

Several deep models ship Apache/MIT **code** with **CC-BY-NC weights**
(Depth-Anything-V2-large, some Mask2Former / DeepGaze / IQA checkpoints). Open
code does not make the pretrained weights free for commercial use. For anything
shipped, prefer the permissively-weighted variant (MiDaS, DAv2-small, SAM), or
retrain on licensable data. Have this checked per model before release.

## Vendored third-party code

`third_party/aesthetics-toolbox/` contains the MIT-licensed Aesthetics-Toolbox
(its `LICENSE` is included), wrapped not modified. Maintain a software
bill-of-materials (`requirements-*.txt` + this file) for the commercial audit.
