# CNfA COMPUTATIONAL ATTRIBUTES — the authoritative table (generated FROM the registry)
### 2026-07-19 (Cowork/Fable) · source of truth: `annotation_socket/registry.py` · MODEL_VERSION `cnfa_algs-2026-07-19+seed1234+reliableA+reviewfix+codex2fix+codex3fix+m1prime+wave1+codexS0S2fix+clutterstack`

*Every row below is REGISTERED AND EXECUTABLE through the socket today (annotate -> derive ->
verify). This supersedes the static counts in the 2026-07-18 inventory docs, which predate the
Wave-1/street-noise/clutter-stack builds. Regenerate with the snippet at the bottom whenever the
registry changes — never hand-edit the rows.*

**Totals: 58 registered predicates — 31 image-computable, 27 plan/declared-input.** M1′ sufficient-statistic audit active on 8 bindings; 11 predicates may return evidenced signal-absent abstentions.

## A. Image-computable attributes (run on any photo) (31)

| # | predicate | tier | audit | M1′ | requires | module | note |
|---|---|---|---|---|---|---|---|
| 1 | `acoustic_absorption_proxy` | AMBER | replayable |  | image only | `cnfa_algs/attributes.py` | material table over heuristic planes |
| 2 | `cnfa.cognitive.landmark_salience` | GREEN | replayable |  | image only | `cnfa_algs/attributes.py` |  |
| 3 | `cnfa.fluency.color_palette_entropy` | GREEN | replayable | ✓ | image only | `cnfa_algs/attributes.py` |  |
| 4 | `cnfa.fluency.edge_clarity_mean` | GREEN | replayable | ✓ | image only | `cnfa_algs/attributes.py` |  |
| 5 | `cnfa.fluency.edge_orientation_entropy` | AMBER | replayable_tol | ✓ | image only | `cnfa_algs/reliable_attrs.py` | V13 (AMBER per Fable F1, blank-image bug FIXED -> abstains on <40 edge px). 2nd-order is a firs |
| 6 | `cnfa.fluency.fractal_mid_d_band` | AMBER | replayable_tol |  | image only | `annotation_socket/predicates/fractal_band.py` | V9 (AMBER per Fable F5): declared trapezoid over whole-interior Canny box-count D. R2 does NOT  |
| 7 | `cnfa.fluency.grayscale_gabor_entropy_proxy` | AMBER | replayable_tol |  | image only | `cnfa_algs/reliable_attrs.py` | V6 (AMBER + RENAMED per Fable F3): grayscale Gabor-magnitude entropy PROXY. NOT the published R |
| 8 | `cnfa.fluency.local_congestion_proxy` | AMBER | replayable_tol |  | image only | `cnfa_algs/reliable_attrs.py` | V7 (AMBER + RENAMED per Fable F4): local-variance colour/contrast/orientation PROXY with declar |
| 9 | `cnfa.fluency.multiscale_gradient` | AMBER | replayable_tol |  | image only | `cnfa_algs/clutter_stack.py` | MSG-inspired multi-scale Sobel mean (arXiv:2501.15890) — structural layer; named PROXY |
| 10 | `cnfa.fluency.multiscale_unique_color` | AMBER | replayable_tol |  | image only | `cnfa_algs/clutter_stack.py` | MUC-inspired occupied color-bin fraction — chromatic-variety layer; named PROXY |
| 11 | `cnfa.fluency.processing_load_proxy` | GREEN | replayable | ✓ | image only | `cnfa_algs/attributes.py` |  |
| 12 | `cnfa.fluency.proto_object_count` | AMBER | replayable_tol |  | image only | `cnfa_algs/clutter_stack.py` | mean-shift proto-object COUNT (Yu et al. 2014 family) — numerosity layer; PROXY |
| 13 | `cnfa.fluency.spectral_slope_deviation` | AMBER | replayable_tol | ✓ | image only | `cnfa_algs/reliable_attrs.py` | V2 (AMBER + RENAMED per Fable F2): radial 1/f power-slope + mid-band residual. This is NOT the  |
| 14 | `cnfa.fluency.symmetry_score_horizontal` | GREEN | replayable |  | image only | `cnfa_algs/attributes.py` |  |
| 15 | `cnfa.fractal_dimension` | GREEN | replayable | ✓ | image only | `cnfa_algs/attributes.py` |  |
| 16 | `cnfa.geometry.contour_angularity` | AMBER | replayable_tol |  | image only | `cnfa_algs/reliable_attrs.py` | V1 (AMBER per Fable F8): whole-image contour curve/corner statistic; NOT validated architectura |
| 17 | `cnfa.geometry.orderliness_alignment` | AMBER | replayable_tol |  | image only | `cnfa_algs/wave1_ops.py` | LSD segment orientation order (segment-scale; V13 stays pixel-scale); abstains <20 segments |
| 18 | `cnfa.light.brightness_variance` | GREEN | replayable | ✓ | image only | `cnfa_algs/attributes.py` |  |
| 19 | `cnfa.light.dark_zone_map` | AMBER | replayable_tol |  | image only | `cnfa_algs/wave1_ops.py` | dark zones map, NOT 'safety'; abstains on globally-dark input |
| 20 | `cnfa.light.evening_ambience` | AMBER | replayable_tol |  | image only | `cnfa_algs/wave1_ops.py` | McCamy CCT proxy + dimness + skew; AWB confound declared |
| 21 | `cnfa.light.luminance_gradient_contrast` | AMBER | replayable |  | image only | `cnfa_algs/wave1_ops.py` | large-scale light architecture (sigma=diag/64); fullscale=60 calibrated on 9-interior smoke |
| 22 | `cnfa.light.shadow_softness` | AMBER | replayable_tol |  | image only | `cnfa_algs/wave1_ops.py` | penumbra 10-90% width over chromaticity-stable edges; hard flag in px; abstains <25 edges |
| 23 | `cnfa.light.spotlight_pool_geometry` | AMBER | replayable_tol |  | image only | `cnfa_algs/wave1_ops.py` | top-hat pool geometry ONLY; social-exposure claim deferred to seat-input compound |
| 24 | `cnfa.light.sun_patch_geometry` | AMBER | replayable_tol |  | image only | `cnfa_algs/wave1_ops.py` | bright warm straight-boundary patch GEOMETRY — candidate, cannot prove sun |
| 25 | `cnfa.light.temperature_mismatch` | AMBER | replayable_tol |  | image only | `cnfa_algs/wave1_ops.py` | max weighted mired gap between chromaticity clusters; abstains on low saturation |
| 26 | `cnfa.light.vertical_illuminance_proxy` | AMBER | replayable |  | image only | `cnfa_algs/attributes.py` |  |
| 27 | `cnfa.light.warm_vs_cool_ratio` | GREEN | replayable |  | image only | `cnfa_algs/attributes.py` |  |
| 28 | `cnfa.material.texture_density` | AMBER | replayable_tol |  | image only | `cnfa_algs/wave1_ops.py` | RESIDUAL micro-texture EXCLUDING structured/periodic pattern (wallpaper/ribbing read as structu |
| 29 | `cnfa.spatial.enclosure_index` | AMBER | replayable |  | image only | `cnfa_algs/attributes.py` | rides heuristic segment_planes (conf~0.45); panel: labels are colour clusters |
| 30 | `cnfa.spatial.prospect` | AMBER | replayable |  | image only | `cnfa_algs/attributes.py` | panel: glass-house inversion — view terminates at glazing |
| 31 | `glare-risk` | GREEN | replayable |  | image only | `cnfa_algs/attributes.py` |  |

## B. Plan / declared-input metrics (inferred plan or declared inputs) (27)

| # | predicate | tier | audit | M1′ | requires | module | note |
|---|---|---|---|---|---|---|---|
| 1 | `C01.triangulation_ignition` | AMBER | replayable_tol |  | plan | `annotation_socket/predicates/triangulation.py` | COMPOUND: landmark_salience x C1 integration x co-location gate to the desire-line ridge; ancho |
| 2 | `C1.visual_integration` | AMBER | replayable_tol | ✓ | plan | `cnfa_algs/ (plan-metric suite)` | VGA on inferred PlanGrid; heuristic geometry caps at AMBER |
| 3 | `C10.daylight_proximity` | AMBER | replayable_tol |  | glazing, plan, seats | `cnfa_algs/ (plan-metric suite)` | geometric screen; certified melanopic needs spectral_daylight |
| 4 | `C11.prospect_refuge` | AMBER | replayable_tol |  | plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 5 | `C12.crowding_risk` | AMBER | replayable_tol |  | plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 6 | `C13.setting_fit` | AMBER | replayable_tol |  | plan | `cnfa_algs/ (plan-metric suite)` |  |
| 7 | `C14.focus_collab_separation` | GREEN | replayable_tol |  | collab_sources, focus_seats, plan | `cnfa_algs/ (plan-metric suite)` | DERIVED from C1 x C7 — scoring it without C7 evidence is the fabrication regression |
| 8 | `C15.active_design` | GREEN | replayable_tol |  | amenities, plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 9 | `C16.territory` | GREEN | replayable |  | territory_spec | `cnfa_algs/ (plan-metric suite)` |  |
| 10 | `C17.local_control` | GREEN | replayable |  | control_zones | `cnfa_algs/ (plan-metric suite)` |  |
| 11 | `C18.air_quality` | GREEN | replayable |  | air_spec | `cnfa_algs/ (plan-metric suite)` |  |
| 12 | `C19.restoration_nature` | AMBER | replayable_tol |  | nature_cells, plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 13 | `C2.connectivity` | AMBER | replayable_tol |  | plan | `cnfa_algs/ (plan-metric suite)` |  |
| 14 | `C20.chronic_soundscape` | AMBER | replayable_tol |  | collab_sources, plan | `cnfa_algs/ (plan-metric suite)` |  |
| 15 | `C21.thermal` | AMBER | replayable_tol |  | glazing, plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 16 | `C22.circadian_contrast` | AMBER | replayable_tol |  | glazing, plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 17 | `C23.social_connectedness` | AMBER | replayable_tol |  | commons, plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 18 | `C24.spatial_generosity` | AMBER | replayable_tol |  | plan | `cnfa_algs/ (plan-metric suite)` | 2D openness-contrast proxy; true awe wants Tier-C height |
| 19 | `C29.stranded_amenity_index` | AMBER | replayable_tol |  | plan | `annotation_socket/predicates/stranded_amenity.py` | COMPOUND (C01 inverse): appeal x (1-co-location gate) x usable-surface; high = attractive ameni |
| 20 | `C3.intelligibility` | AMBER | replayable_tol |  | plan | `cnfa_algs/ (plan-metric suite)` |  |
| 21 | `C4.wayfinding_load` | AMBER | replayable_tol |  | plan | `cnfa_algs/ (plan-metric suite)` |  |
| 22 | `C5.collaborator_proximity` | GREEN | replayable_tol |  | collab_pairs, plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 23 | `C6.path_overlap` | GREEN | replayable_tol |  | destinations, plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 24 | `C7.focus_speech_privacy` | GREEN | replayable_tol |  | collab_sources, focus_seats, plan | `cnfa_algs/ (plan-metric suite)` |  |
| 25 | `C8.distraction_distance` | GREEN | replayable |  | acoustic_params | `cnfa_algs/ (plan-metric suite)` | floor-global acoustic spec; NEVER scored from defaults (panel S4) |
| 26 | `C9.view_equity` | GREEN | replayable_tol |  | glazing, plan, seats | `cnfa_algs/ (plan-metric suite)` |  |
| 27 | `cnfa.acoustic.street_noise_intrusion` | AMBER | replayable_tol |  | facade_spec, outdoor_leq | `cnfa_algs/street_noise.py` | facade-transmission energy model x ISO3382-3 masking; ABSTAINS without Leq_out + R' |

## C. Built but NOT yet registered (next registration slot)

| operator | module | status |
|---|---|---|
| `cnfa.geometry.verticality_cues` (W2.1) | `cnfa_algs/wave2_geometry.py` | self-tested (roll gate); registration pending S3 gate |
| `cnfa.plan.choice_richness` (W2.6) | `cnfa_algs/wave2_geometry.py` | self-tested; registration pending S3 gate |

## D. Planned (kept candidates, not yet built)

Codex Section-D triage keeps not yet in code: Wave-2 remainder (ceiling openness v2a_067,
double-height, blind corners v2a_072, barrier permeability v2a_077, room-scale v2a_068,
thresholds), Wave-3 detector-backed (vegetation v2a_096, window-view v2a_097, blue-space
v2a_099, sociopetal-detected v2a_106, corner-window), faithful V2/V6/V7 reimplementations
([PORT]-gated), semantic-surprise clutter layer (VLM-tier), C-CLUT segment-count-from-
pinned-model variant. Full provenance: `CNFA_SECTION_D_TRIAGE_AND_IMAGE_REQUEST_CODEX_2026-07-18.md`,
`SPRINT_COMPCORRECT_ALGORITHMS_2026-07-19.md` §4-6.

## Regeneration snippet
```
PYTHONPATH=. python3 scripts/gen_attribute_table.py   # (this file was generated by the
inline equivalent; promote to scripts/ on next housekeeping pass)
```