# Codex Adversarial Certification: Batch 1-4 Verdicts

As the adversarial certifier ("Codex") for the Image-Tagger project, I have rigorously evaluated the implementations of the requested perceptual and spatial attributes against their academic citations documented in `JUSTIFICATION_TABLE.md` and their source code in `wave1_ops.py`, `wave2_geometry.py`, and `attributes.py`.

Below are the detailed verdicts (GREEN vs AMBER) for each attribute based on the fidelity to published algorithms and inherent proxy limitations.

## Batch 1

### v2a_007: flicker_banding
*   **Implementation**: `wave1_ops.py::flicker_banding`
*   **Mechanism**: Computes high-frequency row-wise luminance oscillation via FFT as a proxy for PWM rolling shutter artifacts.
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: The implementation relies on rolling-shutter artifacts of CMOS cameras as a proxy for high-frequency LED flicker (Wilkins et al., 2010). This introduces severe hardware-dependent confounds: mechanical shutters or sufficiently long exposures mask the effect completely, and physical horizontal blinds in the scene will trigger false positives. It is fundamentally an approximation of reality via camera artifacts.

### v2a_008: color_rendering_proxy
*   **Implementation**: `wave1_ops.py::color_rendering_proxy`
*   **Mechanism**: Calculates the standard deviation and median of the HSV saturation channel. 
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: The justification table honestly lists this as a "Project convention" acting as a proxy for the Color Rendering Index (CRI). It operates under the heuristic that environments with poor CRI collapse color variance. However, it suffers from a massive confound: monochromatic interior design (e.g., a gray room) under perfect full-spectrum sunlight will yield a near-zero saturation variance, failing to distinguish between poor lighting and intentional aesthetic desaturation.

---

## Batch 2

### v2a_074: wayfinding_legibility
*   **Implementation**: `wave2_geometry.py::wayfinding_sightlines_hough`
*   **Mechanism**: Proxies legibility by the confidence of a single geometric vanishing point (VP). 
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: While Kaplan & Kaplan (1989) discuss perspective and wayfinding, using VP confidence is a 2D heuristic. As noted in the table, a brick wall photographed straight-on yields strong orthogonal lines (and a strong VP score) but zero actual physical depth or wayfinding affordance. It conflates 2D perspective convergence with actual 3D navigational paths.

### v2a_082: curvature_vs_sharp
*   **Implementation**: `wave1_ops.py::curvature_vs_sharp_angles`
*   **Mechanism**: Extracts Canny edges and uses `approxPolyDP` to classify contours as sharp (few vertices) or curved (many vertices).
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: Vartanian et al. (2013) studied architectural curvilinearity, but this 2D edge-based method lacks semantic understanding. It cannot distinguish true architectural curvature (e.g., a vaulted ceiling) from circular objects (e.g., plates, clocks, or lamps). This limits the algorithm to a 2D pixel-level heuristic.

### v2a_091: complexity_gradient
*   **Implementation**: `wave1_ops.py::visual_complexity_gradients`
*   **Mechanism**: Computes standard deviation of Canny edge densities across a 4x4 spatial grid.
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: Inspired by Stamps (2003), it assumes that variance across the grid represents a visual gradient. However, mathematically, an extremely sparse/empty room and a completely chaotic/cluttered room will both yield a low variance (flat distribution). It only measures spatial non-uniformity of edges, not true hierarchical complexity.

---

## Batch 3 & 4

### v2a_083: symmetry_score_horizontal
*   **Implementation**: `attributes.py::symmetry_horizontal`
*   **Mechanism**: Flips the image horizontally and compares with the original using Structural Similarity Index (SSIM).
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: Marked honestly as a "Gap" in the justification table, this method lacks a published basis for using SSIM specifically as an architectural symmetry measure. Furthermore, it is entirely constrained by camera positioning: an off-center view of a perfectly symmetrical room will yield a low score, meaning it measures image-plane symmetry, not true 3D spatial symmetry.

### v2a_084: fractal_dimension
*   **Implementation**: `attributes.py::fractal_dimension_local`
*   **Mechanism**: Uses box-counting (Mandelbrot 1983, Bovill 1996) on Canny edge maps over a tile grid.
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: The implementation evaluates a narrow scale range (2–16 pixels). Because it operates on Canny edges rather than structural representations, the resulting metric is highly sensitive to image resolution, blur, and edge-detector threshold choices, making it a proxy rather than a robust intrinsic measure of the environment's fractal nature.

### v2a_085: processing_load
*   **Implementation**: `attributes.py::processing_load`
*   **Mechanism**: Uses JPEG compression bytes-per-pixel (at Q75) as a proxy for cognitive processing load.
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: Documented as an honest gap with no formal citation. While Rosenholtz et al. (2007) correlate clutter with search times, linking file size compressibility to human cognitive load is an unvalidated heuristic. Sensor noise artificially inflates this metric, while smooth CGI deflates it, and it cannot separate "organized complexity" from "chaotic mess".

### v2a_087: color_palette_entropy
*   **Implementation**: `attributes.py::palette_entropy`
*   **Mechanism**: Performs k-means clustering (k=8) in LAB space and computes Shannon entropy over the cluster proportions.
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: The Shannon entropy math matches the literature (Hasler & Suesstrunk, 2003; Schloss & Palmer, 2011), but k-means on a continuous color space is heavily dependent on the chosen `k` and deterministic seeds. The metric also completely ignores color harmony/semantics—a palette of highly clashing, ugly colors could score the identical entropy to a balanced, aesthetically pleasing polychrome environment.

### v2a_088: texture_density
*   **Implementation**: `wave1_ops.py::texture_density`
*   **Mechanism**: Evaluates 5x5 local luminance range (energy) on non-structure pixels (excluding dilated Canny edges).
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: While texturing gradients aid depth perception (Kaplan & Kaplan, 1989), extracting this from 2D images is highly confounded by sensor noise (especially in low light) being misidentified as micro-texture, and defocus blur artificially removing it. 

### v2a_100: prospect
*   **Implementation**: `attributes.py::prospect`
*   **Mechanism**: Computes the 95th percentile of estimated monocular depth (`Z`) over pixels classified as `FLOOR`.
*   **Verdict**: **AMBER** (Honest Proxy/Ceiling)
*   **Critique**: Based on Appleton (1975) and Benedikt (1979), true prospect requires metric sightline lengths and an understanding of physical vistas. The code uses relative monocular depth on a 2D image, which compresses far ranges and frequently mistakes smooth featureless surfaces (like blank walls) for open voids. 

---
**Summary Statement**: Every reviewed attribute functions as a 2D proxy/heuristic for a 3D architectural or perceptual reality. None achieve a pure `GREEN` tier, as they are universally bounded by the limitations of single-image spatial inference, sensor noise, camera angles, and unvalidated engineering heuristics. They are honest, computationally stable proxies, but undeniably `AMBER`.
