# CNfA Attribute Inventory & Operational Algorithms

**Prepared for David Kirsh — 2026-07-13**
**Scope:** the Image Tagger science pipeline (`Image_Tagger_3.4.74_vlm_lab_TL_runbook_full`), its `low-level-image-features`, `biophilia-index-main`, and the CNfA taxonomy. This document consolidates the *existing* attribute set with the *new* attributes proposed in the "Reading Rooms as Behavior" essay, states for each whether it has a **robust computational algorithm**, whether it can be **localized**, how a complex attribute is **displayed**, and how **reliable** the computation is. Where an attribute was not yet algorithmic, this document **makes it algorithmic** (Section 4).

---

## 0. The one reality check that governs everything

The pipeline's input is a **single RGB photograph of one interior**, not a floor plan or a 3D/BIM model. That fact splits the whole attribute universe into three **modalities**, and honesty about which modality an attribute needs is the difference between a real algorithm and a wish:

- **M1 — image-only.** Computable from the pixels alone (all current low-level primitives). Robust and cheap.
- **M2 — image + monocular depth / segmentation.** Needs a depth map (DepthAnything/MiDaS ONNX, already wired as optional in `spatial/depth.py`) and/or semantic segmentation of boundary planes and objects. Computable per-image but reliability is gated by the depth/segmentation quality.
- **M3 — plan / multi-view / BIM.** Fundamentally needs the *configuration of many spaces* — a floor plate, multiple rooms, or occupant positions. **A single interior photo does not contain this.** The essay's field measures (space-syntax integration, visibility-graph analysis over a plan, agent footfall, Allen-curve desk proximity, room-to-room acoustic privacy) live here and are **out of scope for the single-image tagger** (Section 5). They are not abandoned — they are a different input pipeline.

This is the core correction to the essay: its most powerful "topographic field" measures assume M3. On the current M1/M2 tagger, "localization" means a **per-pixel or per-region map over the image** (a heatmap, whose iso-contours are the topographic curves), an **evidence region** (bbox / mask / polygon), or a **detected-object overlay** — not a field over a plan.

### Simple vs complex — the definition used here

- **Simple attribute:** a single deterministic function of the pixels (or of one segmentation/depth pass) with no learned semantic gate and no fusion of sub-attributes. Example: brightness, edge density, palette entropy. These are M1, and essentially all are already robust.
- **Complex attribute:** either (a) requires a semantic model (segmentation, object detection, saliency, VLM) as an input, or (b) is a **fusion** of two or more sub-attributes with weights. Examples: enclosure index, landmark salience, biophilic score, acoustic reverberation proxy.

---

## 1. Legends

**Algorithm status** (does a robust, defensible algorithm exist?)

| Tag | Meaning |
|---|---|
| **ROBUST** | Deterministic, standard method, low variance; implemented or trivially so. Safe to defend. |
| **DEFINED** | Concrete algorithm given in Section 4 (inputs, steps, formula, params); implementable now; reliability varies. |
| **PROXY** | An honest algorithm exists but it estimates the construct only indirectly; treat outputs as low-confidence candidates. |
| **NEEDS-M3** | No sound single-image algorithm; requires plan/multi-view/BIM (Section 5). |

**Localizable** = can we point at *where* in the image the attribute lives?
`yes` (dense field or region), `partial` (coarse region / detected objects only), `no` (whole-image scalar only).

**Display type** (for complex attributes)

| Type | Use |
|---|---|
| **heatmap** | dense per-pixel scalar field over the image; iso-contours = topographic curves (e.g., saliency, luminance variance, view-depth). |
| **overlay-mask** | semantic regions painted on the image (e.g., absorptive-vs-reflective surfaces, boundary planes, material classes). |
| **object-overlay / graph** | detected boxes and links (e.g., sociopetal seat clusters, clutter objects). |
| **scalar + component-bar** | one number with an inspectable breakdown of its weighted parts (fusion composites). |
| **topo-map (plan)** | field over a floor plan — **M3 only**. |

**Reliability** = High / Med / Low, with the limiting factor named.

---

## 2. Simple attribute inventory (M1 primitives — the "viz primitives we have")

These are implemented in `low-level-image-features/main.py`, `backend/science/vision.py`, `backend/science/math/*` (color, complexity, fractals, glcm, spatial/regional frequency), and the MPIB port (`math/mpib_low_level.py`, 20 keys; MATLAB Image Decomposer, 58 features). All are ROBUST and M1.

| Attribute (key) | What it measures | Algorithm | Localizable → display | Reliability |
|---|---|---|---|---|
| `brightness_mean`, `brightness_sd` | Mean & SD of luminance | mean / std of grayscale ÷255 | yes → luminance heatmap | High |
| `color.luminance` | Perceived lightness | mean gray | yes → heatmap | High |
| `color_pct_{red,green,blue,neutral}` | Colour channel dominance ratios | per-pixel argmax of BGR | yes → class overlay | High |
| `hsv_{hue,sat,value}_{mean,sd}` | HSV distribution | HSV convert + moments | yes → per-channel heatmap | High |
| `color.warmth` / `warm_vs_cool_ratio` | Warm vs cool hue share | count hue∈[0,60] vs [90,150] | yes → warm/cool mask | High (camera WB caveat) |
| Lab means/SD (`labL/A/B`) | Perceptual colour | CIELAB convert + moments | yes → heatmap | High |
| `contrast_rms` | Global contrast | std of grayscale | partial → tiled heatmap | High |
| `entropy_shannon` | Grayscale information | Shannon entropy of histogram | partial → tiled heatmap | High |
| `edge_density_{straight,nonstraight,total}` (SED/NSED/ED) | Edge & line content | Canny + Hough line split | yes → edge map | High |
| `edge_clarity_mean` | Edge crispness | mean Sobel/Canny gradient magnitude | yes → gradient heatmap | High |
| `symmetry_mse`, `symmetry_ssim` | L–R mirror similarity | MSE / SSIM(image, fliplr) | partial → mirror-diff map | High |
| `power_spectrum_mean`, `total_energy` | Spatial-frequency energy | FFT magnitude² mean | no (global) or tiled | High |
| Slope of power spectrum (`Beta*`, `Gamma*`) | 1/f falloff (naturalness cue) | log-log fit of radial PSD | no | High |
| `fractal.D` / `cnfa.fractal_dimension` | Self-similar complexity | box-counting on edge map | partial → local-D heatmap | High global / Med local |
| GLCM texture (contrast, homogeneity, energy) | Micro-texture | gray-level co-occurrence | yes → per-tile heatmap | High |
| LGN stats (`CEgray`, `SCbluey…`, spatial-contrast) | Early-vision colour/contrast energy | MPIB LGN filters | no | High (as defined) |
| `regional_frequency`, `spatial_frequency` | Coarse vs fine energy split | band-pass energy ratios | partial → band heatmap | High |

> Note: every "no/partial" localization above becomes `yes` if computed on a sliding window — brightness, entropy, contrast, fractal-D, and spectral slope all have natural **local** variants that produce a heatmap. That is the cheapest way to give David more topographic curves from primitives he already has.

---

## 3. Complex attribute inventory (existing + new)

Columns: **Status** = current repo state (`live_core` / `live_partial` / `stub` / `new` = introduced by the essay). **Algo** = algorithm status per Section 1. **Loc** = localizable. **Display** = for the complex attribute. **Rel** = reliability + limiter. **Mod** = modality.

### 3.1 Spatial structure & enclosure

| Attribute | Status | Algo | Loc | Display | Rel | Mod |
|---|---|---|---|---|---|---|
| `spatial.isovist_openness` | live_partial | ROBUST (2D raycast on edge map) | yes | heatmap (ray-length) | Med — edge≠wall | M1 |
| `isovist.area_25d`, `.compactness_25d` | live_partial | DEFINED (depth threshold) | yes | heatmap | Low→Med — depth quality | M2 |
| `cnfa.spatial.enclosure_index` | stub | **DEFINED (§4.1)** | yes | overlay-mask (boundary planes) | Med | M2 |
| `cnfa.spatial.prospect` / `prospect` | live_core | **DEFINED (§4.2)** | yes | heatmap (view-depth) | Med | M2 |
| `refuge` | live_partial | **DEFINED (§4.3)** | partial | overlay-mask (refuge regions) | Low→Med | M2 |
| `cnfa.spatial.prospect_to_refuge_ratio` | stub | **DEFINED (§4.4)** | yes | dual overlay + scalar | Low→Med | M2 |
| `cnfa.spatial.ceiling_height_avg` | live_partial | PROXY (§4.5) | partial | scalar (+ vanishing-line overlay) | Low — scale ambiguity | M2 |
| `enclosure`/`plan_openness`/`spatial_compression` | live_partial | DEFINED (fuse enclosure+depth+ceiling) | yes | scalar + component-bar | Med | M2 |

### 3.2 Wayfinding & cognition

| Attribute | Status | Algo | Loc | Display | Rel | Mod |
|---|---|---|---|---|---|---|
| `cnfa.cognitive.landmark_salience` | stub | **DEFINED (§4.6)** | yes | heatmap (saliency) + bbox | Med | M1/M2 |
| `cnfa.cognitive.legibility_score` / `spatial-legibility` | stub | PROXY (§4.7, fusion) | partial | scalar + component-bar | Low | M2 |
| `cnfa.cognitive.activity_zones_count` / `zoning_clarity` | stub | DEFINED (§4.8, segment+cluster) | yes | overlay-mask (zones) | Low→Med | M2 |
| `interactional_visibility` | backlog | PROXY (§4.13) | partial | graph overlay | Low | M2 |
| **wayfinding difficulty field** (essay) | new | NEEDS-M3 | (plan) | topo-map (plan) | — | M3 |

### 3.3 Fluency / complexity / order

| Attribute | Status | Algo | Loc | Display | Rel | Mod |
|---|---|---|---|---|---|---|
| `science.visual_richness` | live_core | ROBUST (colour-entropy+edge+texture) | yes | heatmap | High | M1 |
| `science.organized_complexity` | live_core | ROBUST (fractal × organization) | partial | heatmap | Med | M1 |
| `cnfa.fluency.processing_load_proxy` | stub | ROBUST (§4.9, JPEG bytes/pixel) | partial | scalar (+ tiled heatmap) | Med | M1 |
| `cnfa.fluency.symmetry_score_horizontal` | stub | ROBUST (SSIM mirror) | partial | mirror-diff heatmap | High | M1 |
| `cnfa.fluency.color_palette_entropy` | stub | ROBUST (§4.10, k-means+Shannon) | partial | palette bar + region map | High | M1 |
| `cnfa.fluency.edge_clarity_mean` | stub | ROBUST (gradient) | yes | gradient heatmap | High | M1 |
| `cnfa.fluency.visual_entropy_spatial` | stub | DEFINED (object-centroid entropy) | partial | object heatmap | Med | M2 |
| `cnfa.fluency.figure_ground_clarity` | stub | DEFINED (§4.11, saliency+seg contrast) | yes | heatmap | Low→Med | M2 |
| `cnfa.fluency.hierarchy_depth` | stub | PROXY (saliency level count) | partial | scalar + saliency map | Low | M2 |
| `cnfa.fluency.pattern_rhythm_regularity` | stub | DEFINED (FFT peak sharpness of repeats) | partial | overlay (repeat group) | Med | M1 |
| `cnfa.fluency.clutter_density_count` | stub | DEFINED (§4.12, objects/floor-area) | yes | object-overlay + density heatmap | Med | M2 |
| `cnfa.fluency.anomaly_count` | stub | PROXY (reconstruction/rarity) | partial | anomaly heatmap | Low | M2 |

### 3.4 Light

| Attribute | Status | Algo | Loc | Display | Rel | Mod |
|---|---|---|---|---|---|---|
| `cnfa.light.brightness_variance` | stub | ROBUST (spatial luminance SD) | yes | luminance heatmap | High | M1 |
| `glare-risk` / `cnfa.dynamic.path_glare_max` | stub | DEFINED (§4.14, overexposure+contrast) | yes | glare heatmap | Med | M1 |
| `cnfa.light.diffuse_vs_direct_ratio` | stub | DEFINED (shadow-edge sharpness) | partial | shadow/highlight overlay | Low→Med | M1/M2 |
| `cnfa.light.vertical_illuminance_proxy` | stub | DEFINED (wall-mask luminance) | yes | wall-plane heatmap | Med | M2 |
| `cnfa.light.warm_vs_cool_ratio` | stub | ROBUST (hue bands) | yes | warm/cool mask | High (WB caveat) | M1 |

### 3.5 Material, haptic, acoustic (the geometry-and-materials payoff)

| Attribute | Status | Algo | Loc | Display | Rel | Mod |
|---|---|---|---|---|---|---|
| `materials-dominant-types` | live_core | ROBUST/PROXY (HSV heuristic; VLM better) | yes | material overlay-mask | Med heuristic / High VLM | M1/M2 |
| `natural_material_ratio` / `cnfa.biophilic.natural_material_ratio` | stub | DEFINED (material masks → ratio) | yes | overlay-mask | Med | M2 |
| `material_diversity_index` | backlog | ROBUST (class entropy) | partial | scalar + material bar | Med | M2 |
| `surface-reflectance-sheen` (`glossy/matte/specular`) | backlog | DEFINED (highlight statistics) | yes | sheen heatmap | Med | M1 |
| `cnfa.haptic.soft_surface_ratio` | stub | DEFINED (material→softness map) | yes | overlay-mask | Med | M2 |
| `cnfa.haptic.texture_variation_index` | stub | ROBUST (GLCM variance field) | yes | texture heatmap | Med | M1 |
| **`acoustic-reverberation-proxy` (RT60)** | backlog | **DEFINED (§4.15 — flagship)** | yes | absorptive/reflective overlay + scalar | Med relative / Low absolute | M2 |
| `acoustic_absorption_proxy` | backlog | **DEFINED (§4.15)** | yes | absorptive-area overlay | Med | M2 |

### 3.6 Social affordance

| Attribute | Status | Algo | Loc | Display | Rel | Mod |
|---|---|---|---|---|---|---|
| `sociopetal_seating` | backlog | **DEFINED (§4.16)** | yes | graph overlay (facing seats) | Med | M2 |
| `interactional_visibility` | backlog | PROXY (§4.13) | partial | graph overlay | Low | M2 |
| **interaction-potential field** (essay) | new | NEEDS-M3 | (plan) | topo-map (plan) | — | M3 |
| **awareness–privacy frontier** (essay) | new | NEEDS-M3 | (plan) | 2-field topo-map | — | M3 |

### 3.7 High-level affective composites (fusion, `composite_later`)

| Attribute | Status | Algo | Loc | Display | Rel | Mod |
|---|---|---|---|---|---|---|
| `biophilia.index` / `biophilic_design_score` | live_core | ROBUST fusion (§4.17) | partial | scalar + component-bar | Med | M1/M2 |
| `restorative-capacity` | backlog | DEFINED fusion (§4.17) | partial | scalar + component-bar | Low→Med | M2 |
| `intimacy_index` | backlog | DEFINED fusion | partial | scalar + component-bar | Low | M2 |
| `monumentality_index` | backlog | DEFINED fusion | partial | scalar + component-bar | Low | M2 |
| `serenity_index` / `tension_index` | backlog | DEFINED fusion | partial | scalar + component-bar | Low | M2 |
| `psych.coziness`, `style.modernity` | live (VLM) | VLM (not deterministic) | no | scalar | Med (VLM variance) | M1 |

---

## 4. Operational algorithm specifications (making them algorithmic)

Each spec gives **inputs** (from primitives the repo already has), **steps/formula**, **parameters**, **localization + display**, **reliability**, and **failure modes** (the Fable attack surface). Notation: `I` = RGB image, `G` = grayscale, `D` = normalized depth map in [0,1] (0 = near), `S` = semantic segmentation label map, `E` = edge map. All produce, in addition to any scalar, a dense field `F(x,y)` where localization is `yes` — the field's iso-contours are the topographic curves.

### 4.1 Enclosure index `cnfa.spatial.enclosure_index` — DEFINED, M2
- **Inputs:** `S` (classes: wall, ceiling, floor, window/opening, void-beyond, object), `D`.
- **Steps:** (1) Boundary planes B = wall∪ceiling∪floor. (2) Aperture A = window∪opening∪void-beyond. (3) Weight each boundary pixel by nearness w = (1 − D) so near surfaces enclose more. (4) `enclosure = Σ_{p∈B} w(p) / Σ_{p∈B∪A} w(p)`.
- **Params:** none tunable beyond the segmentation class set.
- **Localize/display:** per-pixel field `F = w·[p∈B]`; **overlay-mask** of boundary vs aperture, plus scalar gauge.
- **Reliability:** Med — bounded by segmentation quality; robust to lighting. **Failure:** mirrors/large art read as "void" or "opening"; open doorways to another enclosed room over-count as aperture.

### 4.2 Prospect `cnfa.spatial.prospect` — DEFINED, M2 (upgrades live isovist_openness)
- **Inputs:** `D`, floor mask from `S`.
- **Steps:** (1) From the camera, sample rays across the lower visual field (over the floor). (2) For each ray, view-depth = depth at the farthest still-floor/free pixel before an occluding object/wall. (3) `prospect = P95( raydepths )` (95th percentile view distance), normalized by image far-plane.
- **Localize/display:** `F(x,y)=D` restricted to sightline corridors; **heatmap** of view-depth (long corridors light up) — a genuine topographic view-distance map.
- **Reliability:** Med with depth model; Low with the current edge-raycast fallback. **Failure:** monocular depth compresses far distances; glazing that shows exterior inflates prospect (arguably correct).

### 4.3 Refuge `refuge` — DEFINED, M2
- **Inputs:** `D`, `S`, ceiling mask.
- **Steps:** refuge accrues where an occupiable near-field position has **overhead or lateral enclosure**: (1) detect low-overhead regions (ceiling pixels with small depth / low height), (2) detect lateral concavities (alcoves) as local maxima of "wall on ≥2 sides within radius r in the depth field", (3) `refuge = fraction of near-field floor (D<τ) that is backed on ≥2 sides or covered overhead`.
- **Params:** τ (near-field depth cutoff, ~0.4), r (concavity radius).
- **Localize/display:** **overlay-mask** of refuge regions (alcoves, canopied zones).
- **Reliability:** Low→Med — refuge is genuinely hard from a room-facing photo (you see the room, not the view *from* the refuge). **Failure:** furniture backs misread as walls.

### 4.4 Prospect-to-refuge ratio `cnfa.spatial.prospect_to_refuge_ratio` — DEFINED, M2
- **Steps:** `PR = prospect / (prospect + refuge + ε)`; report PR plus both components (never collapse).
- **Display:** dual overlay (prospect corridors + refuge pockets) + scalar. **Reliability:** inherits the weaker of §4.2/§4.3 → Low→Med.

### 4.5 Ceiling height (avg) `cnfa.spatial.ceiling_height_avg` — PROXY, M2
- **Inputs:** `D`, ceiling & floor masks, vertical vanishing point from line detection.
- **Steps:** ordinal estimate from (ceiling-plane depth gradient) + (image fraction of ceiling) + (vertical vanishing distance). Absolute metres need a scale cue (door ~2.0 m, riser ~0.17 m) detected in-frame; if none, emit an **ordinal** bin {low/normal/high/lofty}.
- **Reliability:** Low absolute (scale ambiguity is fundamental to monocular), Med ordinal. **Failure:** no metric scale → never claim metres without a detected reference object.

### 4.6 Landmark salience `cnfa.cognitive.landmark_salience` — DEFINED, M1/M2 (well-posed & localizable)
- **Inputs:** bottom-up saliency map `Sal` (spectral-residual FFT saliency — pure M1, or a deep saliency net), object detections O (optional).
- **Steps:** (1) compute `Sal(x,y)`. (2) Contrast term per object region: ΔE-Lab colour contrast + size + edge-uniqueness vs a surround ring. (3) `landmark_salience = max over object regions of ( Sal_mean · contrast )`; without detections, take the top saliency mode.
- **Localize/display:** **heatmap** (saliency field — topographic) + **bbox** on the winning landmark.
- **Reliability:** Med — bottom-up saliency is standard and stable; the *wayfinding* meaning ("does this anchor orientation") is the weak semantic link, so mark it candidate. **Failure:** saliency ≠ landmark (a bright window wins over a memorable sculpture).

### 4.7 Legibility `cnfa.cognitive.legibility_score` — PROXY (fusion), M2
- **Fusion:** `legibility = w1·figure_ground_clarity + w2·zoning_clarity + w3·axis_strength + w4·(1 − clutter_density)`, weights ~0.3/0.3/0.2/0.2.
- **Reliability:** Low — "how easy to understand/navigate" is barely a single-image property (true legibility is M3, over routes). Report as a coarse ordinal candidate only. **Failure:** a tidy but disorienting maze scores high.

### 4.8 Activity zones / zoning clarity `cnfa.cognitive.activity_zones_count`, `zoning_clarity` — DEFINED, M2
- **Inputs:** object detections, floor mask, furniture groupings.
- **Steps:** (1) cluster furniture/objects by spatial proximity on the floor plane (DBSCAN over projected centroids using `D`). (2) `activity_zones_count = #clusters`. (3) `zoning_clarity = 1 − overlap/adjacency ambiguity` (silhouette score of the clustering).
- **Localize/display:** **overlay-mask** of zone polygons. **Reliability:** Low→Med — depends on detector + floor projection. **Failure:** open-plan multi-use areas.

### 4.9 Processing-load proxy `cnfa.fluency.processing_load_proxy` — ROBUST, M1
- **Formula:** `load = JPEG_bytes(I, Q=75) / (W·H)` (bytes per pixel at fixed quality); optionally blend with normalized `entropy_shannon`.
- **Localize/display:** tiled version → heatmap of local compressibility. **Reliability:** Med — correlates with clutter/detail but confounded by texture and noise. **Failure:** a photo of a plain but noisy/grainy wall reads as high load.

### 4.10 Colour-palette entropy `cnfa.fluency.color_palette_entropy` — ROBUST, M1
- **Steps:** k-means (k=8) in Lab → cluster proportions p_i → `H = −Σ p_i log p_i` (normalize by log k).
- **Display:** palette bar + optional per-region palette map. **Reliability:** High. **Failure:** k sensitivity — fix k and seed for determinism.

### 4.11 Figure-ground clarity `cnfa.fluency.figure_ground_clarity` — DEFINED, M2
- **Steps:** salient-object mask vs background: `fg_clarity = mean boundary contrast (Lab ΔE across the object/background edge) × segmentation confidence`.
- **Display:** **heatmap** of boundary contrast. **Reliability:** Low→Med (segmentation-bound). **Failure:** camouflage / low-contrast interiors.

### 4.12 Clutter density `cnfa.fluency.clutter_density_count` — DEFINED, M2
- **Formula:** `clutter = N_objects / A_floor` where A_floor is visible floor area from `S`; **image-area fallback** `N/(W·H)` with an explicit method flag when no floor is found.
- **Display:** **object-overlay** + object-centroid density **heatmap**. **Reliability:** Med (detector recall). **Failure:** floor occluded → fallback inflates/deflates; report which denominator was used.

### 4.13 Interactional visibility `interactional_visibility` — PROXY, M2
- **Steps:** detect seats; for each seat pair estimate line-of-sight from `D` (no large occluder between projected seat centroids); `score = fraction of seat pairs mutually visible`.
- **Display:** **graph overlay** (visible seat pairs linked). **Reliability:** Low (single-view occlusion reasoning is weak). **Failure:** off-frame seats; monocular occlusion errors.

### 4.14 Glare risk / path glare `glare-risk`, `cnfa.dynamic.path_glare_max` — DEFINED, M1
- **Steps:** (1) over-exposure mask `Ov = luminance > 0.95`. (2) local luminance contrast around windows/light sources (top-hat filter). (3) `glare = w1·area(Ov) + w2·max local contrast`, normalized.
- **Display:** **heatmap** of glare sources (topographic). **Reliability:** Med — image glare ≠ perceived DGP (no eye position/luminance calibration). **Failure:** blown-out sky through a window vs true discomfort glare.

### 4.15 Acoustic reverberation & absorption proxies `acoustic-reverberation-proxy`, `acoustic_absorption_proxy` — DEFINED, M2 (the flagship: acoustics from visual structure + materials)
This is the operational form of "acoustics computed from what you can see plus the materials."
- **Inputs:** material segmentation (`materials.py` masks, or VLM), boundary-plane masks `S`, depth `D` for a rough volume/area estimate.
- **Material→absorption table:** map each material class to a mid-band (500 Hz–1 kHz) absorption coefficient α (lab averages): glass 0.03, concrete/stone/marble/tile 0.02–0.04, gypsum/plaster 0.05, wood 0.10, brick 0.03; carpet 0.30, heavy curtain/drapery 0.55, upholstered/fabric 0.60, acoustic tile 0.70, plants 0.10. (Ship the table as a JSON so it is inspectable/tunable.)
- **Steps:**
  1. For each visible surface class i, get its **visible area fraction** Sᵢ (pixels, optionally deprojected by `D` to reduce perspective bias).
  2. **Mean absorption** ᾱ = Σ Sᵢαᵢ / Σ Sᵢ  →  `acoustic_absorption_proxy = ᾱ` (0–1, higher = deader room).
  3. **Relative reverberation proxy** `RT_rel = (1 − ᾱ)` or, on a 0–1 scale, `RT_rel = clip( k·(1−ᾱ)/ᾱ )` — monotone in "how echoey."
  4. **Absolute RT60 (optional, low-confidence):** if a metric scale cue calibrates volume V and total surface Sₜₒₜ, apply **Sabine** `RT60 = 0.161·V / (Sₜₒₜ·ᾱ)`. Without scale, **do not** emit seconds — emit the relative proxy + an ordinal bin.
- **Localize/display:** **overlay-mask** painting each surface by its α (reflective = warm/red, absorptive = cool/green) — a literal "acoustic map" of the visible structure; plus the scalar proxy and a hard/soft-area bar.
- **Reliability:** **Med** for *relative ranking* of rooms (hard-glassy vs soft-furnished is visually obvious and robust); **Low** for absolute RT60 seconds (no metric volume from one photo; α lab-values differ from in-situ; Sabine assumes a diffuse field). **Failure:** unseen surfaces (behind camera) omitted; a visually hard room with hidden absorption; perspective over-weighting near surfaces (mitigated by depth deprojection).
- **Why this is the important one:** it demonstrates that a *material-tagged view* already determines an acoustic behavioural prior — the room's suitability for speech/focus — with **no microphone**. It is the single-image shadow of the essay's Sabine/STI argument, honestly bounded to *relative* claims.

### 4.16 Sociopetal seating `sociopetal_seating` — DEFINED, M2
- **Inputs:** seat/sofa detections (COCO classes), per-seat facing estimate (from seat pose / visible front), `D`.
- **Steps:** for seat pair (i,j): `a_ij = 𝟙[0.45 ≤ d̂_ij ≤ 2.1 m] · 𝟙[mutually facing] · LOS(i,j)` where d̂ is the depth-deprojected inter-seat distance; `sociopetal_score = Σ a_ij / normalization`; also emit cluster count.
- **Localize/display:** **graph overlay** — seats as nodes, sociopetal links drawn; sociofugal seats flagged.
- **Reliability:** Med — seat detection is good; **facing from a single view is the weak link** (mitigate with pose or chair-front heuristics). **Failure:** rows of chairs facing a screen (task-focused) misread as sociofugal or sociopetal depending on angle.

### 4.17 Affective fusion composites (biophilic, restorative, intimacy, monumentality, serenity, tension) — DEFINED, M1/M2
All follow one pattern: a **weighted, inspectable sum of normalized sub-attributes**, each already defined above.
- `biophilic_design_score = 0.25·plant_ratio + 0.20·natural_material_ratio + 0.20·daylight + 0.15·view_nature + 0.10·biomorphic_form + 0.10·fractal_naturalness`.
- `restorative-capacity = w·(naturalness, daylight, coherence[=1−clutter], low_glare, prospect_refuge_balance)`.
- `intimacy_index = w·(small_scale[=enclosure·low_ceiling], warm_light, refuge, soft_material, low_glare)`.
- `monumentality_index = w·(ceiling_height, volume, axis_strength, hierarchy_depth, hard_mass_material)`.
- `serenity_index = w·(low_clutter, diffuse_light, naturalness, pattern_coherence, low_sharpness)`; `tension_index` ≈ its complement (harsh light, sharp contours, high contrast, clutter, low refuge).
- **Display:** **scalar + component-bar** (every source component stays inspectable — required by the repo's composite rule). **Reliability:** Low→Med — these are hypotheses about affect; treat as candidate scores for human validation, never facts. **Failure:** weights are unvalidated; culture/context dependence.

---

## 5. Honest boundary — attributes that a single image cannot yield (NEEDS-M3)

These are the essay's most powerful *field* measures. They require the configuration of **many** spaces or occupant positions and belong to a **plan / multi-view / BIM** pipeline, not the single-image tagger. Listing them so the boundary is explicit and Fable has nothing to catch:

| Measure | Why not from one photo | Modality it needs | Display when available |
|---|---|---|---|
| Space-syntax **integration / choice / intelligibility** | Defined over the whole plan graph of spaces | Floor plan / IFC | topo-map over plan |
| **Visibility-graph analysis** (visual integration, clustering→decision points) | Needs the walkable floor plate, not one view | Plan section | topo-map over plan |
| **Isovist *field*** (vs the single-vantage isovist we do compute) | A field needs a grid of vantage points across the plan | Plan / mesh | topo-map |
| **Agent footfall / interaction-potential field** | Simulates movement over the plate | Plan + circulation graph | topo-map (heat) |
| **Allen-curve proximity / co-location** | Pairwise distances among all desks/teams | Plan with furniture layout | pairwise matrix / plan heat |
| **Room-to-room acoustic privacy** (STC across a partition) | Two rooms + the wall between them; one photo is one room | Multi-room plan + materials | plan overlay |
| **Newcomer vs familiar wayfinding cost surfaces** | Accumulate over routes across the plan | Plan + route set | two topo-maps |

**Bridge:** the single-image attributes in Section 4 are exactly the *per-space node features* these M3 fields consume. So the tagger is not a dead end for the essay — it is the **feature extractor** that populates each room-node before the plan-level fields are computed. The `isovist_25d` module is the seam: single-view isovist today, per-vantage isovist across a reconstructed plan tomorrow.

---

## 6. Display taxonomy (answering "how is a complex attribute shown")

| Attribute family | Default display | Topographic curves? |
|---|---|---|
| View-depth, saliency, luminance/glare, texture, brightness variance, figure-ground, fractal-local | **heatmap** | **yes** — iso-contours of the field |
| Enclosure, materials, absorption/reverberation, refuge, zoning, soft-surface, boundary planes | **overlay-mask** (semantic regions) | region contours |
| Sociopetal, interactional visibility, clutter, activity zones | **object-overlay / graph** | no (discrete) |
| Fusion composites (biophilic, restorative, intimacy, …) | **scalar + component-bar** | no (aggregate) |
| Plan fields (Section 5) | **topo-map over the floor plan** | **yes** — M3 only |

Every localized tag also carries an **evidence region** (bbox / mask / polygon) and, per the repo's Operational Rule, `confidence`, `measurement_method`, `known_failure_modes`, and `human_attestation_status`, surfaced in the annotation viewer.

---

## 7. Direct answer: did I make them algorithmic?

**Yes — with an explicit honesty map, which is the only kind of "yes" worth red-teaming.**

- **Robust now (defend without hesitation):** every Section-2 simple primitive; and the complex attributes `visual_richness`, `organized_complexity`, `landmark_salience` (as bottom-up saliency), `processing_load_proxy`, `color_palette_entropy`, `symmetry_score_horizontal`, `edge_clarity_mean`, `brightness_variance`, `texture_variation_index`, `material_diversity_index`.
- **Defined now (concrete algorithm in §4, implementable this sprint, reliability stated):** `enclosure_index`, `prospect`, `refuge`, `prospect_to_refuge_ratio`, `activity_zones_count`/`zoning_clarity`, `figure_ground_clarity`, `pattern_rhythm_regularity`, `clutter_density_count`, `glare-risk`, `diffuse_vs_direct_ratio`, `vertical_illuminance_proxy`, `natural_material_ratio`, `soft_surface_ratio`, `surface-reflectance-sheen`, **`acoustic-reverberation-proxy` and `acoustic_absorption_proxy`**, `sociopetal_seating`, and the affective fusions.
- **Proxy only (honest low-confidence, flagged as candidate):** `legibility_score`, `hierarchy_depth`, `interactional_visibility`, `anomaly_count`, `ceiling_height_avg` (ordinal), the `dynamic.*` motion tags (single image has no motion → require video or are proxies).
- **NEEDS-M3 (not claimed for single image):** the plan-level fields in Section 5.

The flagship claim — **acoustic behaviour from visual structure + materials** — is now an algorithm (§4.15): material masks → absorption table → mean-α → relative reverberation, with Sabine available when a scale cue calibrates volume, and it is honest that absolute RT60 in seconds is Low-confidence from one photo while *relative* echoey-vs-dead ranking is Med and defensible.

If that qualified "yes" is what you wanted, **turn on Fable** — §4 is written to be attacked: every algorithm names its inputs, its formula, its reliability ceiling, and its failure modes, and Section 5 concedes the M3 boundary up front so the red-team's job is to break the M1/M2 algorithms on their own terms.
