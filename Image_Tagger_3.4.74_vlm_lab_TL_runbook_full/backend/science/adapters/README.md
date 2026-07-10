# cnfa_adapters — open-source visual toolboxes as cognitive-code analyzers

This package wraps a curated set of open-source visual-analysis tools as
**repo-compatible analyzers** that fill the `cnfa.*` attribute stubs of the
Image Tagger cognitive-code bank. It turns a single interior photograph or
rendered view into a bank of **deep, causally-active perceptual attributes**
(fractal dimension, visual complexity/entropy, symmetry, clutter, spectral
slope, colour-opponent statistics, texture, gloss cues, depth/openness,
saliency, memorability), each stamped with provenance, confidence and a licence
class — and each tied, in `mapping.py`, to the *distal* environmental attribute
it stands for and the *psychological/neural* construct it connects to.

It is built to **drop into `backend/science/adapters/`** and work with the
existing `analyze(frame)` / `frame.add_attribute(...)` pattern, but it also runs
standalone (a bundled `StandaloneFrame` + a vendored copy of the MIT
Aesthetics-Toolbox) so you can try it without the repo.

## What's inside

**Permissive adapters (safe to ship — MIT/BSD/Apache), 49 attributes:**

| adapter | tool (licence) | fills |
|---|---|---|
| `aesthetics_toolbox` | Aesthetics-Toolbox / Redies QIPs (MIT) | fractal D, spectral slope, edge entropy, symmetry, balance, PHOG self-similarity/complexity/anisotropy, colour entropy |
| `visual_clutter` | Rosenholtz Feature Congestion + Subband Entropy (MIT/BSD) | clutter density, subband-entropy clutter |
| `colour_science` | colour-science + Hasler–Süsstrunk (BSD) | colour temperature (warm/cool), colourfulness |
| `colour_opponent` | scikit-image + colour-science (BSD) | CIELab/LGN opponent stats, hue entropy, saturation, dominant wavelength |
| `skimage_texture` | scikit-image (BSD) | GLCM texture, shape-index curvilinearity |
| `mahotas_texture` | mahotas (MIT) | Haralick texture, LBP entropy, Zernike shape |
| `proximal_stats` | native numpy/scipy/skimage/opencv (permissive) | luminance skew/kurtosis (Motoyoshi gloss cue), sub-band skew, RMS contrast, straight-vs-curved edge ratio, blur/DoF, radial 1/f slope, mirror-symmetry correlations |

**Model-worker adapters (isolated subprocess; heavier / licence-gated), 16 attributes:**

| adapter | tool (licence) | fills | policy |
|---|---|---|---|
| `depth_midas` | MiDaS depth (MIT) | enclosure, openness, ceiling proxy, prospect/refuge, texture gradient | commercial ok |
| `segmentation_sam` | SAM/OneFormer (Apache; gate NC weights) | natural-material ratio, greenery, activity zones | commercial ok |
| `saliency_deepgaze` | DeepGaze (weights research-only) + SR fallback | landmark salience, figure-ground clarity | research |
| `memorability` | ResMem/ViTMem (non-commercial weights) | memorability | research |
| `aesthetic_score` | pyiqa NIMA/MUSIQ (mixed weights) | aesthetic/quality — **validation only** | research |
| `material_from_image` | perceived-gloss / intrinsic (research) | perceived gloss, albedo, metallicness | research |

The model workers ship as **runnable scaffolds**: each has a real inference path
plus, where honest, a permissive fallback (segmentation → HSV greenery; saliency
→ spectral-residual) so the pipeline returns something before the heavy weights
are installed.

## Install & run (standalone)

```bash
pip install -r requirements-permissive.txt      # numpy scipy scikit-image opencv-python colour-science statsmodels mahotas visual-clutter pyrtools
python examples/run_all.py path/to/room.jpg     # prints the cnfa.* attributes
python examples/run_all.py                       # uses a scikit-image sample
python examples/run_all.py room.jpg --policy research --workers   # include model workers
```

The MIT Aesthetics-Toolbox is **vendored** under `third_party/aesthetics-toolbox`
and auto-located, so no extra setup is needed. To point at a different copy, set
`AESTHETICS_TOOLBOX_PATH`.

## Use in code

```python
from cnfa_adapters import StandaloneFrame, select_adapters, run_frame
frame = StandaloneFrame.from_path("room.jpg")
run_frame(frame, select_adapters(policy="commercial", include_workers=False))
print(frame.as_dict())          # {"cnfa.fractal_dimension": 1.39, ...}
```

`select_adapters(policy=...)` enforces the licence gate: `"commercial"` returns
permissive adapters only; `"research"` returns everything.

## Dropping into the Image Tagger repo

1. Copy the `cnfa_adapters/` package under `backend/science/adapters/`.
2. In `pipeline.py`, register each adapter behind its `enable_flag`
   (`enable_aesthetics_toolbox`, `enable_proximal_stats`, …) and call
   `adapter.analyze(frame)` in the analyzer loop.
3. Move each key an adapter `provides` out of `STUB_FEATURE_KEYS`, and add it to
   `features_canonical.jsonl` / `contracts/attributes.yml` (the three-file
   registry) — `registry.STUB_TO_FUNCTION` is the source list.
4. Keep the licence gate: ship the `"commercial"` policy; enable the
   research/NC adapters only in a validation config.

The adapters duck-type the frame (see `base.get_rgb/get_gray/get_path`), so they
bind to the real `AnalysisFrame` without changes as long as it exposes an RGB
image (or a path) and `add_attribute(key, value, **meta)`.

## The proximal → distal → psych/neural mapping

`mapping.py` holds, as data, the chain that makes each number meaningful: what is
measured in the image (**proximal**), the environmental attribute it stands for
(**distal**), and the psychological/neural construct it connects to, with a
`status` flag (`established` / `supported-with-debate` / `proxy` / `exploratory`)
and short-form evidence. Run `python -m cnfa_adapters.mapping` to print it.

## Tests

```bash
python tests/test_registry.py             # registry + mapping integrity (no heavy deps)
python tests/test_permissive_adapters.py  # golden directional checks on synthetic images
# or: pytest tests/
```

## Performance & robustness notes

- The Aesthetics-Toolbox edge-orientation entropy uses a Gabor filterbank and
  costs **~10 s/image** (it internally normalises resolution). It is the one
  expensive permissive feature; disable it via `enable_aesthetics_toolbox` for a
  fast pass, or run the bank offline.
- Near-constant images (e.g. a blank wall render) have undefined edge
  statistics; the toolbox's second-order counter runs away on them, so the
  adapter **skips the edge/PHOG/Fourier group when the image is near-flat** and
  emits only the safe QIPs.
- Compatibility shims (`compat.py`) restore `PIL.Image.ANTIALIAS` for
  visual-clutter and force writable arrays for scikit-image's GLCM, so the
  upstream tools run **unmodified** (licence-clean: we wrap, we don't fork).

See `LICENSING.md` for the per-adapter commercial-use position.
