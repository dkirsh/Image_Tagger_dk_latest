# cnfa_algs Justification Table

Every parameter in the annotation pipeline that constitutes a scientific
design decision is listed here with its citation, rationale, and known
limitations. Parameters without citations are marked honestly.

---

## Pixel-Level Attributes (M1)

### brightness_variance

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Window size | 31×31 px | Project convention, no published source | Roughly 5% of a 640px image width; captures local luminance variation at ~furniture scale | Not calibrated to any viewing distance or angular subtense |
| Metric | Local luminance SD | Reinhard et al. 2001, "Color Transfer between Images" | Standard deviation of luminance is the simplest non-parametric measure of light distribution heterogeneity | Does not distinguish meaningful brightness variation (e.g. light/shadow) from noise |

### edge_clarity

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Canny thresholds | 50, 150 | **No published source — project convention** | Standard OpenCV defaults; empirically reasonable for architectural photos | Not tuned for architectural images specifically; may over-detect texture edges |
| L2gradient | True | Canny 1986 original paper recommends L2 for accuracy over L1 speed | More accurate gradient magnitude | Negligible speed difference on modern hardware |

### fractal_dimension_local

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Box-counting method | Canny edge → box count over scales 2–16 px | Mandelbrot 1983, "The Fractal Geometry of Nature"; applied to architecture by Bovill 1996, "Fractal Geometry in Architecture and Design" | Box-counting on edge maps is the standard method for computing fractal dimension of architectural facades and interiors | Scale range 2–16 px is narrow; results are edge-detector dependent (Canny parameters affect D) |
| Tile size | 64×64 px | **No published source — project convention** | Chosen to give ~7–10 tiles per image dimension at 480×640 | Not calibrated to any architectural or perceptual scale |
| D range | Naturally ∈ [1, 2] for 2D edge images | Mandelbrot 1983; Bovill 1996 | D=1 is a straight line, D=2 fills the plane | Must be rescaled to [0,1] for pipeline; (D−1)/1.0 preserves ordering |

### glare_risk

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Overexposure threshold | >0.95 (normalized luminance) | **No published source** — project convention inspired by CIE 117:1995 glare indices | 95th percentile of luminance is a common heuristic for "blown" pixels in HDR photography | Not the same as Daylight Glare Probability (DGP, Wienold & Christoffersen 2006); no eye position model; camera response ≠ radiometric luminance |
| Top-hat kernel | 31×31 px | **No published source — project convention** | Detects local bright spots at furniture-to-window scale | Kernel size is image-resolution-dependent, not angular-resolution-dependent |

### warmth_ratio

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Warm hue band | H < 30° or H ≥ 160° (HSV) | Ou et al. 2004, "A study of colour emotion and colour preference. Part I: Colour emotions for single colours" | Reds, oranges, yellows are the canonical "warm" hues in colour psychology | Camera white balance shifts the hue distribution; cultural variation in warm/cool associations (Ou's data is cross-cultural but limited to object colours) |
| Cool hue band | 45° ≤ H ≤ 135° | Same | Blues and greens; gap between 30–45° and 135–160° is the "neutral" zone | Architectural materials (concrete, wood) often fall in the neutral zone |
| Saturation gate | S > 0.15 | **No published source — project convention** | Excludes near-neutral pixels (grays) that have unstable hue | Threshold is arbitrary; perceptual saturation depends on lightness |

### palette_entropy

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| k (number of clusters) | 8 | Schloss & Palmer 2011, "Aesthetic response to color combinations" — 8 is within the 5–11 range they use for colour preference studies | Captures the dominant palette without over-segmenting | |
| Quantization method | Median Cut | Heckbert 1982, "Color Image Quantization for Frame Buffer Display" — deterministic spatial subdivision of RGB cube | Replaces non-deterministic k-means; identical runs produce identical palettes | Median Cut may produce fewer than k colors on uniform images; handled with n_actual guard |
| Entropy formula | Shannon entropy over cluster proportions | Shannon 1948; applied to colour by Hasler & Suesstrunk 2003, "Measuring colorfulness in natural images" | Information-theoretic measure of palette diversity | Entropy depends on k; not directly comparable across different k values |

---

## Structural Attributes (M2)

### enclosure_index

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Formula | Nearness-weighted solid-boundary share | Benedikt 1979, "To Take Hold of Space: Isovists and Isovist Fields" — occlusivity measure | Enclosure is the fraction of the visual boundary that is solid (wall/floor/ceiling) weighted by proximity | Single-image proxy for 2D isovist occlusivity; misses surfaces behind the camera |
| Nearness weight | 1/Z (inverse depth) | Stamps 2005, "Visual permeability, locomotive permeability, safety, and enclosure" — closer surfaces contribute more to felt enclosure | Perceptually, a wall 1m away is more enclosing than one 10m away | Weight function shape (1/Z vs 1/Z² vs log) is not empirically settled |

### prospect

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Formula | Fraction of pixels with sightlines > 2× median depth | Benedikt 1979, "To Take Hold of Space: Isovists and Isovist Fields"; Dosen & Ostwald 2016, "Evidence for prospect-refuge theory" | Prospect = isovist area normalized by bounding area; in image space: fraction of pixels with long sightlines | Single-image proxy; Z from monocular depth is relative, not metric; Dosen & Ostwald 2016 note empirical support is "inconsistent" |
| Opening-pixel gate | Cap at 0.25 if no OPENING pixels | Project convention, no published source | Architecturally, can't see far through solid walls; prevents prospect > 0.25 in enclosed boxes | Heuristic — some enclosed spaces genuinely have long interior sightlines |

### vertical_illuminance_proxy

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Target surface | Wall pixels only | CIE 2011, "IEQ Standards for Lighting"; Veitch et al. 2008 — vertical illuminance at eye level (on walls) is the best predictor of perceived brightness in offices | Camera luminance on wall surfaces is a proxy for vertical illuminance | Camera exposure ≠ radiometric luminance; heuristic segmentation quality limits accuracy |

### acoustic_absorption

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Alpha table | hard_floor=0.05, carpet=0.30, glass=0.03, curtain=0.50, upholstery=0.55, etc. | Kuttruff 2009, "Room Acoustics" (5th ed.), Table 5.1 — mid-band (500 Hz–1 kHz) absorption coefficients | Standard published absorption coefficients for common materials | Lab-measured α ≠ in-situ α; material classification is heuristic (no VLM), misclassification is the dominant error source |
| Depth weighting | Z² | Sabine 1922; area-weighting: far pixels subtend less solid angle but cover more actual surface area, so Z² corrects for perspective foreshortening | Standard acoustic treatment: absorption is area-weighted | Sabine's formula assumes diffuse field, which is a poor model for small or irregular rooms |
| Social distance band | 0.45–3.7 m | Hall 1966, "The Hidden Dimension" — personal distance (0.45–1.2 m) through social distance (1.2–3.7 m) | Sociopetal layout requires seat pairs within conversational distance | Hall's measurements were for standing North American adults; seated distance and cross-cultural variation not accounted for |

---

## Composition Attributes (M1)

### rule_of_thirds

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Grid lines | 1/3 and 2/3 of image dimensions | Widely attributed to John Thomas Smith 1797, "Remarks on Rural Scenery"; photographic pedagogy standard | Compositional guideline; saliency near these lines suggests adherence | No strong empirical evidence that thirds-adherence predicts aesthetic preference (see McManus et al. 2011) |
| Score function | Mean saliency within ±5% of grid lines | **Project convention, no published source** | Simple proxy for compositional alignment | Conflates saliency with compositional intent |

### visual_balance

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Balance metric | 1 − |center_of_mass − image_center| / max_offset | Arnheim 1974, "Art and Visual Perception" — visual weight and balance | Balanced compositions have saliency centered; off-center saliency indicates tension | Arnheim's framework is qualitative; the 1−|offset| formula is a linearization with no published validation |

---

## Saliency

### landmark_salience

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| FFT fallback method | Spectral residual | Hou & Zhang 2007, "Saliency Detection: A Spectral Residual Approach" (CVPR 2007) | Detects "proto-objects" via log-spectrum residual; fast (no model) | AUC-Judd ~0.65 on MIT300 (barely above chance); poor localization accuracy; MIT/Tübingen Saliency Benchmark confirms deep models (DeepGaze IIE, NSS~2.3) are far superior |
| FFT confidence | 0.35 | MIT/Tübingen Saliency Benchmark (saliency.tuebingen.ai) — FFT methods rank near bottom on all metrics | Reflects actual benchmark AUC-Judd ~0.65 for spectral-residual | Even 0.35 may be generous for architectural interiors, where spectral-residual confuses bright windows with salient objects |
| Deep model (TranSalNet) confidence | 0.75 | Xu et al. 2022, TranSalNet — competitive with DeepGaze IIE on SALICON | Transformer-based; good accuracy-vs-speed tradeoff | Not validated on architectural interior images specifically |

---

## Gaps (honest)

| Attribute | Parameter | Status |
|-----------|-----------|--------|
| processing_load | All parameters | **No citation.** Tile-based contrast metric with no published justification for tile size, weighting, or the claim that it correlates with cognitive processing load |
| symmetry_horizontal | SSIM threshold | Uses `skimage.structural_similarity` defaults; no published justification for using SSIM as a symmetry measure specifically |
| sociopetal_seating | Facing angle threshold (85°) | **No published source.** Osmond 1957 coined "sociopetal" but gave no angular threshold |
| sociopetal_seating | Depth-scaled distance formula | **Project convention.** `d_m = abs(zi - zj) + d_px/W * (zi+zj)/2 * 1.2` has no published derivation |

## Activity Prediction (activity.py)

### Condition signature profiles

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Profile values | HIGH=0.8, MID=0.5, LOW=0.2, REJECT=0.0 | Project convention — ordinal scale | Symmetric ordinal scale centered at 0.5; spacing matches Mehrabian-Russell 1974 "information rate" bands | Not empirically calibrated to any specific architectural preference data |
| Activity taxonomy | 24 activities in 5 tiers | Gehl 2011 (necessary/optional/social); Whyte 1980; Alexander 1977 Pattern Language | Covers the range from passage to intimate social interaction to special modes | Taxonomy is not exhaustive; cultural context not modeled |

### Personality moderators

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Introvert enclosure weight | 1.15× | Mehrabian & Russell 1974; Zuckerman 1979 Optimal Stimulation Level | Introverts prefer lower-arousal (more enclosed) spaces | Weight magnitude is a project convention; not derived from any specific effect size |
| Extrovert prospect weight | 1.10× | Same | Extroverts seek higher-stimulation (more open) spaces | Same limitation |

### Time-of-day moderators

| Parameter | Value | Citation | Rationale | Limitations |
|-----------|-------|----------|-----------|-------------|
| Morning brightness boost | 1.15× | Cajochen et al. 2005, 2011 — melatonin suppression by blue-enriched light | Morning cortisol peak requires bright light for alertness | Effects measured in laboratory; may not transfer to architectural image analysis |
| Evening warmth boost | 1.15× | Same | Warm dim light prevents melatonin disruption in evening | Same limitation |

```
Table authored: 2026-07-14
Last updated: 2026-07-15
```
