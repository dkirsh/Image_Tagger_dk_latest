# CNfA Testing Plan
### Full attribute test plan from Codex execution, 2026-07-18

This plan covers the current registry operators and the kept Section-D candidates. It separates five tiers:

1. **Synthetic**: pure-core arrays or analytic grids with known ordering.
2. **Negative control**: degenerate or fabricated input that must abstain or be RED.
3. **Real-image**: qualitative ordering on reachable images.
4. **Cross-environment**: exact replay on Mac and sandbox with identical bytes and M1' stats.
5. **Construct**: labeled calibration corpus or A-vs-B region pairs.

Status vocabulary: **NOW** means runnable with current files/code. **PARTIAL** means mechanical testable but not construct-valid. **BLOCKED** means blocked on faithful implementation, declared inputs, detector, or corpus.

## M1' Checks By Audit Class

| audit_class | applies to | synthetic | negative | real-image | cross-env | construct |
|---|---|---|---|---|---|---|
| `luminance_field` | brightness, glare, vertical illuminance, daylight-hard/soft | NOW: gradients, bright spots, dark corners | NOW: overexposed/blank image must not claim physical lux | NOW: Example + POE | BLOCKED until M1' implemented | BLOCKED on corpus |
| `color_palette` | palette entropy, warmth, color diversity, temperature mismatch | NOW: warm/cool swatches, fixed k clusters | NOW: grayscale image must not claim warmth | NOW: warm/cool office pairs | BLOCKED until M1' implemented | BLOCKED on corpus and white-balance controls |
| `radial_fft` | current V2 proxy | NOW: stripes, checkerboards, pink noise | NOW: blank/flat image low confidence | NOW: interiors with repetitive louvers if supplied | BLOCKED until M1' implemented | PARTIAL; faithful V2 still blocked |
| `fft_2d` | faithful V2 | BLOCKED until implemented | BLOCKED | BLOCKED | BLOCKED | BLOCKED on angular calibration corpus |
| `orientation_hist` | V13, orderliness/alignment | NOW: single-line, grid, isotropic noise | NOW: blank image must abstain | NOW: corridors/offices | BLOCKED until M1' implemented | BLOCKED on A-vs-B labels |
| `steerable_pyramid` | faithful V6 | BLOCKED until implemented | BLOCKED | BLOCKED | BLOCKED | BLOCKED |
| `feature_congestion` | faithful V7 | BLOCKED until implemented | BLOCKED | BLOCKED | BLOCKED | BLOCKED |
| `box_count` | fractal dimension, V9 | NOW: line, checker, noise, synthetic fractal | NOW: low-R2 pattern cannot claim scaling validity | NOW: interiors | BLOCKED until M1' implemented | BLOCKED on corpus |
| `geometry_plan` | C1-C4, C13, C24, C01, C29, prospect, enclosure | NOW: analytic grids | NOW: seeded fabricated C8/C14 already RED | PARTIAL: image-inferred geometry only | BLOCKED until M1' implemented | BLOCKED on plan/depth ground truth |
| `segmentation_mask` | vegetation, materials, windows, seats, signage | BLOCKED until detector added | BLOCKED | BLOCKED | BLOCKED | BLOCKED on labeled masks |

## Current Registry Operators

| predicate | synthetic test | negative control | real-image test | cross-env pass | construct pass |
|---|---|---|---|---|---|
| `cnfa.light.brightness_variance` | flat gray < gradient < checker luminance SD. NOW. | all-NaN or tiny image rejected/handled; no physical lux claim. NOW. | Daylit vs dim `Example Images`. NOW. | scalar + luminance M1' digest identical. BLOCKED M1'. | A-vs-B "more uneven/contrasty light" labels. BLOCKED corpus. |
| `cnfa.fluency.edge_clarity_mean` | blurred edge < sharp edge. NOW. | blank image near zero, no high clarity. NOW. | corridor lines vs soft render. NOW. | Sobel/Canny stats digest identical. BLOCKED M1'. | A-vs-B edge clarity labels. BLOCKED. |
| `cnfa.fluency.symmetry_score_horizontal` | symmetric shape > shifted asymmetric shape. NOW. | off-center crop should lower score. NOW. | corridor axial views vs asymmetric office. NOW. | SSIM map digest identical. BLOCKED M1'. | A-vs-B perceived symmetry. BLOCKED. |
| `cnfa.fluency.color_palette_entropy` | one-color < two-color < multi-color swatches. NOW. | grayscale low-saturation must not imply warmth. NOW. | colorful office vs monochrome corridor. NOW. | kmeans centers/proportions digest identical. BLOCKED M1'. | color diversity labels. BLOCKED. |
| `cnfa.fluency.processing_load_proxy` | smooth < noisy/textured JPEG bytes. NOW. | sensor noise synthetic flagged as photo artifact. PARTIAL. | minimal gallery/corridor vs cluttered office. NOW. | JPEG bytes/tile map identical. BLOCKED M1'. | clutter/load A-vs-B. BLOCKED. |
| `cnfa.fractal_dimension` | line < grid/noise; valid D requires sufficient edge pixels. NOW. | blank/low edge returns low confidence/abstain behavior. PARTIAL. | foliage/ornament vs plain wall if available. PARTIAL. | box counts exact. BLOCKED M1'. | fractal preference/complexity labels. BLOCKED. |
| `cnfa.fluency.fractal_mid_d_band` | synthetic D band around target scores higher than outside. NOW. | checkerboard high R2 alone cannot prove natural scaling; should remain AMBER. PARTIAL. | real interiors only qualitative. PARTIAL. | box-count series digest exact. BLOCKED M1'. | Requires corpus and literature target. BLOCKED. |
| `cnfa.fluency.spectral_slope_deviation` | high-contrast stripe/checker > pink noise/natural slope. NOW proxy. | blank/flat should low confidence or low score. PARTIAL. | louver/stripe images needed; current local set weak. BLOCKED Drive. | radial FFT stats exact. BLOCKED M1'. | Faithful V2 needs angular calibration. BLOCKED. |
| `cnfa.fluency.edge_orientation_entropy` | single orientation < orthogonal grid < isotropic edge noise. NOW. | blank image must abstain below 40 edge pixels. NOW. | corridor vs complex office. NOW. | orientation hist/co-occurrence digest exact. BLOCKED M1'. | A-vs-B orderliness/complexity labels. BLOCKED. |
| `cnfa.geometry.contour_angularity` | circle/curve > polygon with sharp corners. NOW. | no-contour image abstains. NOW. | curved furniture/interior vs rectilinear office. BLOCKED Drive. | contour-turning stats exact. BLOCKED M1'. | Curvature preference labels. BLOCKED. |
| `cnfa.fluency.grayscale_gabor_entropy_proxy` | smooth < multi-orientation texture. NOW proxy. | blank low entropy, no Rosenholtz claim. NOW. | cluttered vs minimal interiors. NOW. | proxy Gabor stats exact. BLOCKED M1'. | Faithful V6 and corpus. BLOCKED. |
| `cnfa.fluency.local_congestion_proxy` | uniform < local dense patch. NOW proxy. | arbitrary weights remain AMBER; cannot claim V7. NOW. | shelf/cluttered office vs open corridor. PARTIAL. | proxy covariance digest exact. BLOCKED M1'. | Faithful V7 and corpus. BLOCKED. |
| `glare-risk` | clipped white spot on dark field high. NOW. | uniformly bright image should not equal point glare without top-hat contrast. PARTIAL. | window/glare examples in Example Images. NOW. | bright mask/tophat digest exact. BLOCKED M1'. | A-vs-B glare discomfort labels. BLOCKED. |
| `cnfa.light.warm_vs_cool_ratio` | warm hue swatch > cool hue swatch. NOW. | grayscale/low saturation neutral. NOW. | warm wood vs cool clinical images. PARTIAL. | HSV mask digest exact. BLOCKED M1'. | Warm/cool ratings with white-balance flag. BLOCKED. |
| `cnfa.cognitive.landmark_salience` | one high-contrast blob > uniform/no many equal blobs. NOW. | bright window should be noted as possible false landmark. PARTIAL. | distinctive object/feature vs plain corridor. PARTIAL. | saliency map + bbox digest exact. BLOCKED M1'. | Landmark A-vs-B labels. BLOCKED. |
| `cnfa.spatial.enclosure_index` | analytic planes: solid room > apertures. PARTIAL. | unknown/all-open planes cannot claim high enclosure. NOW. | desk-facing-wall vs glass house. NOW. | plane/depth/grid digest exact. BLOCKED M1'. | Requires plan/depth labels. BLOCKED. |
| `cnfa.spatial.prospect` | analytic depth long corridor > close wall. PARTIAL. | glass-house/window inversion should remain AMBER. NOW. | corridor/glass house vs desk wall. NOW. | depth/plane digest exact. BLOCKED M1'. | Requires depth/prospect labels. BLOCKED. |
| `acoustic_absorption_proxy` | material mask soft > hard. PARTIAL. | no acoustic params means no RT60/STI claim. NOW. | soft lounge vs hard corridor needed. BLOCKED Drive. | material mask digest exact. BLOCKED M1'. | Acoustic ground truth/spec. BLOCKED. |
| `cnfa.light.vertical_illuminance_proxy` | bright wall mask > dark wall mask. PARTIAL. | no wall mask or exposure-only cannot claim lux. NOW. | wall-lit scenes in Example Images. PARTIAL. | plane mask + wall luminance digest exact. BLOCKED M1'. | Needs measured/simulated illuminance. BLOCKED. |
| `C1.visual_integration` | analytic open grid > partitioned grid. NOW. | fabricated plan_chain/grid hash fails verify. NOW. | image-inferred plan only. PARTIAL. | PlanGrid digest identical. BLOCKED M1'. | Requires real plan/VGA labels. BLOCKED. |
| `C2.connectivity` | grid with more neighbors scores higher. NOW. | blocked grid low connectivity. NOW. | image inferred only. PARTIAL. | PlanGrid digest identical. BLOCKED M1'. | Real plan graph labels. BLOCKED. |
| `C3.intelligibility` | connected/open grid > maze. NOW. | random grid with no free cells abstains/rejects. PARTIAL. | corridor/maze images. PARTIAL. | PlanGrid digest identical. BLOCKED M1'. | Wayfinding labels. BLOCKED. |
| `C4.wayfinding_load` | maze > straight corridor. NOW. | no path graph cannot fabricate score. NOW. | corridor examples. NOW. | PlanGrid and graph digest exact. BLOCKED M1'. | Human wayfinding difficulty. BLOCKED. |
| `C13.setting_fit` | mixed open/enclosed/circulation > monoculture. NOW. | all-open fails sanctuary in self-test. NOW. | open office vs cellular mix. PARTIAL. | region-classification digest exact. BLOCKED M1'. | Occupant-demand labels. BLOCKED. |
| `C24.spatial_generosity` | open grid > cramped grid. NOW. | no height means not true awe. NOW. | atrium/high ceiling needed. BLOCKED Drive/POE partial. | PlanGrid digest exact. BLOCKED M1'. | Awe/generosity ratings plus height. BLOCKED. |
| `C01.triangulation_ignition` | landmark on desire-line ridge > off-ridge. NOW. | unregistered or off-ridge anchor low. NOW. | needs seating/amenity-rich real images. BLOCKED Drive. | compound upstream digests exact. BLOCKED M1'. | Social interaction observations/ratings. BLOCKED. |
| `C29.stranded_amenity_index` | appealing anchor off ridge > on ridge. NOW. | no anchor or no usable surface low/unknown. NOW. | amenity off-path examples needed. BLOCKED Drive. | compound upstream digests exact. BLOCKED M1'. | Redesign/usage validation. BLOCKED. |
| `C5.collaborator_proximity` | declared seats/collab pairs near > far. NOW with fixtures. | image-only must ABSTAIN. NOW. | requires seat/collab inputs. BLOCKED. | input digest exact. BLOCKED M1'. | Workplace collaboration labels. BLOCKED. |
| `C6.path_overlap` | shared routes > segregated routes. NOW with plan fixture. | image-only missing seats/destinations abstains. NOW. | requires plan inputs. BLOCKED. | input+path digest exact. BLOCKED M1'. | Observed path overlap. BLOCKED. |
| `C7.focus_speech_privacy` | separated focus/collab > adjacent. NOW with fixture. | image-only abstains. NOW. | requires collab/focus inputs. BLOCKED. | input digest exact. BLOCKED M1'. | STI/privacy data. BLOCKED. |
| `C8.distraction_distance` | acoustic params near/noisy > far/quiet. NOW with fixture. | seeded constant/default C8 RED. NOW. | requires acoustic params. BLOCKED. | acoustic input digest exact. BLOCKED M1'. | Acoustic measurements. BLOCKED. |
| `C9.view_equity` | seats with window LOS fraction matches analytic layout. NOW. | no seats/glazing abstains. NOW. | requires seats/glazing. BLOCKED. | LOS rows digest exact. BLOCKED M1'. | View-quality labels/LEED-style check. BLOCKED. |
| `C10.daylight_proximity` | near-window seats > core seats. NOW. | no spectral daylight cannot claim melanopic EDI. NOW. | requires seats/glazing. BLOCKED. | LOS/distance digest exact. BLOCKED M1'. | Daylight/spectral sim or labels. BLOCKED. |
| `C11.prospect_refuge` | backed seat with view > exposed or blind seat. PARTIAL. | no seats abstains. NOW. | requires seats. BLOCKED. | upstream digest exact. BLOCKED M1'. | Prospect/refuge ratings. BLOCKED. |
| `C12.crowding_risk` | dense seats/area > sparse. NOW with fixture. | no seats abstains. NOW. | requires seats/scale. BLOCKED. | input digest exact. BLOCKED M1'. | Occupancy/crowding labels. BLOCKED. |
| `C14.focus_collab_separation` | high C7 separation > low. NOW with fixture. | seeded score without C7 RED. NOW. | requires collab/focus inputs. BLOCKED. | upstream C7/C1 digests exact. BLOCKED M1'. | Focus/collaboration outcomes. BLOCKED. |
| `C15.active_design` | stairs/amenities distributed > absent. PARTIAL. | no seats/amenities abstains. NOW. | requires amenity inputs. BLOCKED. | input digest exact. BLOCKED M1'. | Movement/active design observations. BLOCKED. |
| `C16.territory` | declared zones clear > ambiguous. PARTIAL. | no territory_spec abstains. NOW. | requires territory spec. BLOCKED. | spec digest exact. BLOCKED M1'. | Territoriality ratings. BLOCKED. |
| `C17.local_control` | control zones near seats > absent. PARTIAL. | no control_zones abstains. NOW. | detector not enough for actual control. BLOCKED. | spec digest exact. BLOCKED M1'. | Agency/control labels. BLOCKED. |
| `C18.air_quality` | good air spec > poor. PARTIAL. | image-only abstains. NOW. | requires air spec/instrument. BLOCKED. | spec digest exact. BLOCKED M1'. | CO2/TVOC/PM data. BLOCKED. |
| `C19.restoration_nature` | seats near nature cells > none. PARTIAL. | no nature_cells abstains. NOW. | needs vegetation/window labels. BLOCKED. | spec digest exact. BLOCKED M1'. | Restoration/PRS labels. BLOCKED. |
| `C20.chronic_soundscape` | collab-source exposure high > low. PARTIAL. | no collab_sources abstains. NOW. | requires acoustic/source inputs. BLOCKED. | spec digest exact. BLOCKED M1'. | Soundscape data. BLOCKED. |
| `C21.thermal` | seats near solar/glazing thermal risk > neutral. PARTIAL. | no seats/glazing abstains. NOW. | requires thermal spec. BLOCKED. | spec digest exact. BLOCKED M1'. | Thermal comfort data. BLOCKED. |
| `C22.circadian_contrast` | daylight + evening restraint > no restraint. NOW with fixture. | no spectral_daylight cannot claim certified melanopic. NOW. | requires seats/glazing/evening spec. BLOCKED. | spec digest exact. BLOCKED M1'. | Circadian/sleep proxy labels. BLOCKED. |
| `C23.social_connectedness` | seats near commons > isolated. PARTIAL. | no seats/commons abstains. NOW. | requires commons inputs. BLOCKED. | spec digest exact. BLOCKED M1'. | Social connectedness outcomes. BLOCKED. |

## Kept Section-D Candidate Tests

| candidate/operator | synthetic | negative control | real-image | cross-env | construct |
|---|---|---|---|---|---|
| `v2a_004.brightness_gradient_contrast` | gradient and contrast-ratio panels order correctly. NOW after implementation. | uniform panel low; no lux claim. | Example daylit offices. | M1' luminance stats. | A-vs-B light-contrast labels. |
| `v2a_009.shadow_softness` + daylight hard/soft | hard edge vs blurred penumbra. | painted dark surface must not count as shadow without luminance geometry. | Drive hard/soft daylight pairs needed. | M1' luminance/edge stats. | Comfort/glare ratings. |
| `v2a_011.evening_daytime_ambience` | warm dim vs cool bright swatches. | white-balance-shifted duplicate flags capture confound. | warm/cool local images plus Drive evening. | color/luminance stats. | Ambience labels. |
| `v2a_013.spotlight_social_exposure` | bright circular pool around seat/person vs even light. | glare spot without social/seat region cannot claim social exposure. | Drive seating/spotlight pairs. | luminance + region stats. | Social exposure ratings. |
| `v2a_014.natural_light_patterns` | sun-patch polygon vs artificial uniform light. | white wall highlight cannot prove sun; AMBER. | Drive daylit interiors. | luminance geometry stats. | Daylight-pattern labels. |
| `v2a_015.temperature_mismatch` | warm and cool clusters in same image > uniform. | low-saturation grayscale abstain/low. | mixed CCT interiors needed. | color stats. | Mismatch discomfort labels. |
| `v2a_067.ceiling_height_openness` | analytic perspective/depth high vs low. | fisheye distortion flagged. | POE high-vs-low ceiling plus Drive. | geometry/depth stats. | Height/openness ratings. |
| `v2a_068.room_scale_cues` | calibrated scale markers/order. | no scale reference caps AMBER. | Drive same-room scale pairs. | depth/geometry stats. | Perceived scale labels. |
| `v2a_072.blind_corners_transparency` | occluding wall vs transparent partition grid. | mirror/glass ambiguity abstains or AMBER. | Drive corridor/partition pairs. | segmentation/geometry. | Safety/legibility labels. |
| `v2a_077.barrier_permeability` | full wall > half wall/glass aperture contrast. | curtains/reflections flagged. | Drive partitions. | segmentation/geometry. | Privacy/prospect labels. |
| `v2a_080.verticality_cues` | strong vertical line/depth vs low horizontal. | lens tilt/roll flag. | atria and high-ceiling examples. | line/depth stats. | Verticality ratings. |
| `v2a_081.dark_corner_safety` | dark corner map vs evenly lit corner. | global dim image not same as unsafe corner. | Drive dim-corner interiors. | luminance + geometry stats. | Perceived safety labels. |
| `v2a_088.texture_density` | uniform < fine texture < dense texture. | compression/noise flagged. | materials/fabric/wood examples. | texture stats. | Texture-density labels. |
| `v2a_094.orderliness_alignment` | aligned grid > random lines. | low edge count abstains. | corridors vs cluttered offices. | orientation hist stats. | Orderliness labels. |
| `v2a_096.visible_vegetation` | mask fractions from labeled toy masks. | green wall/painting not plant unless model confidence. | Drive plant-rich vs plant-free. | segmentation digest. | Restoration/biophilia labels. |
| `v2a_097.window_view_content` | labeled window masks with greenery/sky/water. | indoor green object not outside view. | Drive view pairs. | segmentation + window mask. | View-content labels. |
| `v2a_099.blue_space` | water/sky view masks. | blue wall/carpet negative. | Drive blue-space views. | segmentation digest. | Blue-space restoration labels. |
| `v2a_106.sociopetal_seating_detector` | circular seats > rows. | object false positives do not score without facing. | Drive seating layouts. | detector/provenance digest. | Social affordance labels. |
| `v2a_118.choice_richness_zones` | multi-zone plan > monoculture. | decorative variation without usable zones low. | Drive mixed settings. | setting classifier digest. | Agency/choice labels. |
| `arch.pattern.corner_window` | window on two adjacent walls. | glass art/reflection not counted. | Drive corner-window rooms. | detector/geometry digest. | Prospect/daylight labels. |
| `arch.pattern.daylight_hard` | hard-shadow synthetic. | overexposed patch not hard daylight. | Drive daylit hard-shadow pairs. | luminance stats. | Comfort labels. |
| `arch.pattern.daylight_soft` | blurred diffuse shadow synthetic. | low contrast due blur not daylight. | Drive soft daylight pairs. | luminance stats. | Comfort labels. |
| `arch.pattern.double_height_space` | high-ceiling geometry. | wide-angle/fisheye cap AMBER. | POE high/low ceiling; Drive atria. | depth/geometry stats. | Spatial generosity/awe labels. |
| `arch.pattern.threshold_emphasized` | doorway/threshold synthetic plan. | picture frame not threshold. | Drive entry/threshold images. | detector/geometry stats. | Wayfinding/transition labels. |

## Current Real-Image Smoke Set

Use these immediately for smoke and qualitative sanity, not final validation:

- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Example Images/50-day-street-offices-norwalk-1200x1165-compact.jpg`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Example Images/BalancedCare-Render-Corridor2-wpeople1_960x530.webp`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg`
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Example Images/korridor.jpg`
- `/Users/davidusa/REPOS/Post_Occupancy_Evals/Images/desk facing wall.webp`
- `/Users/davidusa/REPOS/Post_Occupancy_Evals/Images/high vs low ceiling.webp`
- `/Users/davidusa/REPOS/Post_Occupancy_Evals/Images/looking out window at wall.jpg`

Pass criterion for smoke: no UNKNOWN for applicable current predicates, RED only with named verifier problems, AMBER honestly carried for geometry/proxy predicates, and no score for missing declared inputs.

## Gates Before GREEN Expansion

1. M1' is implemented and shows it can reject a stat-mismatched record.
2. Faithful V2/V6/V7 either match a reference implementation or remain proxy-named AMBER.
3. Mac-sandbox replay is run on at least five byte-identical images.
4. Drive corpus exists with region A-vs-B labels and negative controls.
5. Detector-backed candidates include mask/provenance digests and fail closed on missing detector confidence.
6. Construct validation reports false-positive and false-negative rates, not only examples.
