# JOB — Legibility Field: a visibility/readability heat-map for wayfinding (contrast × luminance × distance)

*Posted 2026-07-23 (D. Kirsh, via Cowork/Fable) as a new Vision-Tagger attribute job. Written in the
IMG-2 causal-theoretic attribute style so it slots into the CNfA attribute taxonomy. This is an
**environment-side (IV) attribute** and a **position-tagged spatial field**, not a single image scalar —
it is the wayfinding-legibility computation for "can an agent at position p read sign s in its
sightline?"*

---

## 1. What this is and why it matters

Wayfinding depends on whether directional cues — signage, room numbers, arrows, thresholds — are
**actually legible from where a person is standing and looking**. Legibility is not a property of the
sign alone; it is a joint function of the mark's **luminance contrast** against its background, the
**adaptation luminance** (how bright the scene is), and the **visual angle** the sign's critical detail
(letter x-height / stroke width) subtends at the viewer's distance and angle — evaluated against the
human eye's **contrast-sensitivity limit**. The same sign is legible across a lobby in daylight and
illegible from 8 m in a dim corridor, or when it is low-contrast (grey-on-grey), or seen obliquely.

The deliverable is a **legibility field**: for each candidate target in a space, the set of viewer
positions/angles from which it is readable — renderable as a heat-map over the floor plan or over the
isovist — plus a per-sign **legibility distance** (max range at which it resolves). This lets us take an
agent's location and sightline and answer, per sign, **readable / not readable**, with a margin
(Visibility Level). That is a high-value, decision-relevant wayfinding annotation and a natural
environmental IV for POE and for the causal-abstraction ontology's `environment → wayfinding` edges.

## 2. The model (the science we're computing)

Three interlocking, well-established models; use them as a stack.

**(a) Luminance contrast of the target.** Weber contrast of mark vs local background:
`C = (L_target − L_background) / L_background` (use luminance, not lightness; for text, mark = stroke,
background = the sign field around it). Report signed contrast (dark-on-light vs light-on-dark differ).

**(b) Angular size of the critical detail.** The resolvable detail is the letter **x-height** `h` (or,
stricter, the stroke width / gap). At viewing distance `D`, angular size in arcminutes:
`α = 3438 · h / D` (foreshorten by `cos(viewing_angle)` for oblique lines of sight). Reading generally
needs the critical detail ≳ a few arcmin, not the 1-arcmin acuity limit — legibility ≠ bare detection.

**(c) Threshold: is it resolvable at this contrast and this light level?** Two equivalent framings:

- **Contrast-Sensitivity Function (CSF).** The eye's threshold contrast `C_th` depends on spatial
  frequency (∝ 1/α) and adaptation luminance `L_a` (Weber region at photopic levels, DeVries–Rose at
  low). The target resolves iff `C ≥ C_th(spatial_freq(α), L_a)`. Barten's parametric CSF gives
  `C_th(f, L_a, field_size)`.
- **Adrian Visibility Level (engineering-standard, preferred for a scalar field).** Adrian (1989)
  gives the threshold luminance difference `ΔL_th = f(α, L_a, age, exposure_time)`. Define
  **`VL = ΔL_actual / ΔL_th`**; `VL ≥ VL_crit` (commonly ~7 for comfortable suprathreshold reading;
  ~1 = bare threshold) ⇒ legible. VL is the "legibility reserve" and is exactly the heat-map quantity.

**(d) Optional performance layer.** Rea & Ouellette (1991) **Relative Visual Performance (RVP)** maps
(contrast, size, retinal illuminance) → a 0–1 performance surface — use if we want graded reading
*speed/accuracy* rather than a binary legible/not.

**Legibility distance** falls straight out: `D_max(s)` = largest `D` for which `VL(α(h,D), C, L_a) ≥
VL_crit`. Equivalently the familiar signage "legibility index" (letter-height-per-distance) but derived
from first principles instead of a fixed rule-of-thumb, so it adapts to the actual contrast and light.

**Modifiers to include (at least as flags):** observer **age** (Adrian has an age term; older eyes need
more contrast/light — settable per study population), **disability glare** from bright sources in the
field (Stiles–Holladay veiling luminance raises `L_a` and washes contrast), **colour** (compute
**luminance** contrast as primary; add a chromatic-contrast channel for colour-coded signage — CIE ΔE or
cone-contrast — since red-on-green can be high-chroma but low-luminance-contrast), and **exposure time**
(a glance while walking is not a fixation).

## 3. The computation (pipeline)

| Step | Operation | Notes / dependency |
|---|---|---|
| 1 | **Per-pixel luminance** `L(x,y)` | Best from the POE **HDR fisheye + Sekonic** capture (calibrated cd/m²). From an ordinary sRGB photo: linearize + relative luminance `Y=0.2126R+0.7152G+0.0722B`, then **flag as relative** (uncalibrated) — legibility distance needs true `L_a`. |
| 2 | **Detect targets** | Text/sign detection (scene-text detector + OCR) for signage; general small-feature targets otherwise. Get each target's bounding region + estimated **x-height in pixels**. |
| 3 | **Scale & geometry** | Convert x-height px → metres and get target 3-D position via known camera intrinsics/pose, monocular depth, or the space model. Reuse the tagger's **isovist / spatial** machinery for scene geometry. |
| 4 | **Target contrast** `C` | Weber contrast of stroke vs sign-field luminance (step 1) at the target region. |
| 5 | **Adaptation luminance** `L_a` | Local/global background luminance around the target and along the sightline; add veiling luminance from detected glare sources. |
| 6 | **Threshold model** | For a viewer at `(p, gaze)`: compute `α` (step 2/3 with distance `‖p−s‖` and oblique `cos`), then `VL = ΔL/ΔL_th(α, L_a, age, t)` (Adrian) or CSF check. |
| 7 | **Line-of-sight gate** | `VL(p,s)=0` unless `s` is within the isovist from `p` and inside the gaze cone (foveal/para-foveal for reading). |
| 8 | **Field + distance** | Sweep `p` over a floor grid → **legibility heat-map** per sign (and a max-over-signs "any cue legible?" field). Solve step 6 for `D_max(s)` → per-sign legibility distance. |

## 4. Output / annotation schema (position-tagged)

Per target (JSON, keyed to the image + the space model):
```
{ "target_id", "type": "sign|number|arrow|text", "text": "...",
  "position_3d": [x,y,z], "x_height_m": 0.06, "normal": [..],
  "luminance_target_cd_m2": 45.0, "luminance_bg_cd_m2": 160.0,
  "weber_contrast": -0.72, "adaptation_luminance_cd_m2": 120.0,
  "legibility_distance_m": { "VL7": 11.4, "VL1_threshold": 26.0 },
  "calibration": "hdr_calibrated | relative_uncalibrated",
  "modifiers": { "age": 40, "exposure_s": 0.3, "glare_veiling_cd_m2": 8.0 } }
```
Per space (the field): a raster `legibility_field[sign_id]` over the floor grid giving `VL(p)` (and a
combined "best available cue" layer), exportable as a heat-map overlay and as an isovist-intersected
"legible-from" region. **Everything tagged to position** — that is the point.

## 5. Dependencies & tiers

- **Tier 1 (now, standard CV):** relative-luminance map; text/sign detection + OCR; Weber contrast;
  x-height in px; a first-pass `VL` field using **relative** luminance and a fixed `L_a` — good enough
  to *rank* signs and produce a qualitative heat-map. Clearly labelled uncalibrated.
- **Tier 2 (calibrated):** cross-calibrate image luminance to cd/m² using the **HDR fisheye + Sekonic**
  the POE kit already captures → real `L_a`, real legibility distances. Add the Adrian age/glare/time
  terms. This is where the number becomes trustworthy for a claim.
- **Tier 3 (geometry-complete):** full 3-D sign positions + isovist/gaze gating → the true
  position-tagged field and agent-sightline queries; oblique-angle foreshortening; colour-coded-sign
  chromatic channel.

## 6. Validation

Check `D_max` against published legibility-distance / legibility-index data (e.g., letter-height rules
under stated contrast/luminance) and against **direct field measurement**: print targets at known
x-height/contrast, measure the distance at which readers can call the character, compare to the model's
`VL_crit` crossing. Cross-check the luminance calibration against the Sekonic. Report the model's
error, not a bare "legible" flag (house rule: measured validity, never a bare tier).

## 7. Open questions / decisions

1. **`VL_crit` for "readable"** — bare threshold (~1) vs comfortable glance-while-walking (~7+). Set per
   use (safety signage vs ambient wayfinding).
2. **Age / population** — fix the age term to the study population; expose as a parameter.
3. **Colour coding** — luminance contrast is primary; do we compute a chromatic-contrast channel for
   colour-dependent signage now or later?
4. **Calibration source** — commit to the HDR+Sekonic cross-cal as the Tier-2 path, or accept relative
   luminance for ranking-only.
5. **Reading vs detection** — decide whether the target detail is x-height (read the word) or
   stroke/gap (resolve the glyph); they give different `D_max`.

## 8. Fit into the program

This is an **environment-side IV attribute** with a spatial (position-tagged) output — it belongs in the
"legibility/visibility" branch of the environmental attribute forest (the IV side of the causal-
abstraction ontology), and it is the computational substrate for `signage/legibility → wayfinding`
causal edges. It reuses the tagger's isovist/spatial machinery and the POE kit's photometric capture,
and it produces exactly the kind of causally-active, measurable variable the causal-theoretic attribute
taxonomy (IMG-2) is built around. On pickup, register it in `CNFA_ATTRIBUTE_INVENTORY` /
`CNFA_COMPUTATIONAL_ATTRIBUTES_TABLE` as `ATTR-LEG1 Legibility Field (VL)` with the tier map above.

**Key references (for the implementer):** Adrian, W. (1989), *Visibility of targets: model for
calculation*, Light. Res. Technol.; Rea, M. & Ouellette, M. (1991), *Relative visual performance*,
Light. Res. Technol.; Barten, P. (1999), *Contrast Sensitivity of the Human Eye*; Pelli & Robson (1988)
contrast sensitivity; Arditi & Cho on letter legibility; IES RP-8 (Visibility Level / Small Target
Visibility) for the engineering lineage.
