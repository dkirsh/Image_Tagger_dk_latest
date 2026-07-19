# CNfA Section-D Triage And Image Request
### Codex execution of `CODEX_DEEPEN_PLAN_AND_TESTPLAN_PROMPT_2026-07-18.md`

This document covers Task 1 and Task 3. It verifies the harvested Section-D candidate pool against the current codebase and inventories the reachable image stores. It is intentionally conservative: duplicates merge into existing operators, sensor/spec items are rejected from the image pipeline, and detector/VLM items are deferred unless they earn a clear build slot.

## Evidence Used

Local code checked:

- `annotation_socket/registry.py`: 45 predicates registered; 27 applicable to image-only units, 18 abstain without declared inputs.
- `cnfa_algs/attributes.py`: brightness, edge clarity, symmetry, palette entropy, processing load, fractal dimension, glare, warmth, vertical illuminance proxy, enclosure, prospect, landmark salience, acoustic/material proxy, sociopetal seating.
- `cnfa_algs/reliable_attrs.py`: V1, V2, V6, V7, V9, V13 AMBER proxy family.
- `cnfa_algs/daylight_view.py`: C9/C10/C22 plan daylight/view screens.
- `cnfa_algs/setting_classifier.py`: C13 setting variety/segment fit.

Baseline:

```text
pytest annotation_socket/tests -q -> 19 passed.
run_stage on 3 Example Images -> GREEN=0 AMBER=1 RED=2; negative control RED; run2 zero work.
```

## Decision Counts

| pool | keep | merge | defer | reject | note |
|---|---:|---:|---:|---:|---|
| `env.v2a` 74 cues | 18 | 27 | 24 | 5 | Many are duplicates of brightness, prospect, clutter, C7/C17, or require detectors/specs. |
| `arch.pattern` 20 patterns | 5 | 8 | 7 | 0 | Most are pattern/detector AMBERs or duplicates of prospect/daylight/wayfinding. |
| Remaining canonical families | 3 family-level keeps | 8 family-level merges | 4 family-level defers | 5 family-level rejects | Do not enumerate 330+ until a family earns a build lane. |

## env.v2a Per-Construct Triage

Construct-link shorthand: `light/wellbeing`, `daylight/view`, `prospect/refuge`, `wayfinding`, `clutter/load`, `biophilia/restoration`, `social/privacy/control`, `perceptual fluency`, or `descriptive only`. These are construct-family links from the current CNfA docs/code comments, not new literature validation.

| id | decision | class | existing fraction verified | tier | slot | reason |
|---|---|---|---|---|---|---|
| `v2a_001` | merge | classical-CV | `color_palette_entropy`, warmth | AMBER if harmony claimed | none | Palette hue/saturation/lightness exists; "harmony" needs a validated formula and corpus. |
| `v2a_002` | merge | classical-CV | `warm_vs_cool_ratio` | GREEN current, AMBER construct | none | Operator exists; construct link is light/coziness but white balance limits interpretation. |
| `v2a_003` | merge | image proxy / needs spec | brightness variance, vertical illuminance proxy | AMBER | none | Camera luminance is not lux; do not rebuild eye/task-plane illuminance from photo. |
| `v2a_004` | keep | classical-CV | brightness variance partial | GREEN/AMBER | Wave 1 | Add explicit luminance-gradient and contrast-ratio stats; useful for light/wellbeing. |
| `v2a_005` | merge | geometry/detector | C9/C10/prospect | AMBER | none | Daylight presence and outside view overlap existing daylight/view screens; view content deferred. |
| `v2a_006` | merge | classical-CV | `glare-risk` | GREEN current, AMBER DGP | none | Bright-source risk exists; count can be an extra, not a new construct. |
| `v2a_007` | reject | temporal sensor | none | out | none | Flicker cannot be inferred from a still image. |
| `v2a_008` | reject | needs declared/spec input | palette entropy partial | out/AMBER | none | Color rendering is a lamp/spectral property, not image saturation. |
| `v2a_009` | keep | classical-CV | brightness partial | AMBER | Wave 1 | Shadow softness/hardness can be estimated from penumbra gradients; construct link is lighting comfort. |
| `v2a_010` | defer | pretrained/object/OCR | C17 input only | AMBER | Wave 3 | Visible dimmers/blinds/task lights need object detection and accessibility labels. |
| `v2a_011` | keep | classical-CV | warmth/brightness partial | AMBER | Wave 1 | Evening/daytime ambience can be an honest image proxy from color temperature and luminance distribution. |
| `v2a_012` | defer | geometry/detector | C7 input only | AMBER | Wave 3 | Visual privacy via silhouettes needs people/window/partition detection. |
| `v2a_013` | keep | classical-CV | brightness/glare partial | AMBER | Wave 1 | Spotlight exposure is high local contrast around person/seat zones; needs region pairing. |
| `v2a_014` | keep | classical-CV | brightness partial | AMBER | Wave 1 | Natural light patches are computable as warm/high-luminance polygonal patches, but not proof of sun. |
| `v2a_015` | keep | classical-CV | warmth partial | AMBER | Wave 1 | Temperature mismatch can compare local hue-temperature clusters; needs camera white-balance controls. |
| `v2a_067` | keep | geometry/depth | height absent | AMBER | Wave 2 | Ceiling height/openness requires depth/vanishing geometry; important spatial-affect link. |
| `v2a_068` | keep | geometry/depth | C24 partial | AMBER | Wave 2 | Room-scale cues need scale proxies; useful but cannot be metric without calibration. |
| `v2a_069` | merge | geometry | enclosure, prospect, C9/C10 | AMBER | none | Wall/window balance already lies inside enclosure/prospect/daylight. |
| `v2a_070` | merge | geometry/input | prospect, C11 | AMBER | none | Prospect/refuge exists as image and plan/input family; no new primitive. |
| `v2a_071` | merge | geometry/detector | C4, processing load | AMBER | none | Exit visibility needs exit detector; path complexity already C4/wayfinding. |
| `v2a_072` | keep | geometry/depth | enclosure/prospect partial | AMBER | Wave 2 | Blind corners vs transparent partitions is a real spatial risk cue; needs aperture/occlusion geometry. |
| `v2a_073` | defer | detector + scale | C12 partial | AMBER | Wave 3 | Distance to others requires people/seat detection and calibrated scale. |
| `v2a_074` | merge | geometry | C3/C4 | AMBER | none | Straight sightline legibility is already C3/C4 territory. |
| `v2a_075` | merge | geometry | C4, V6/processing | AMBER | none | Branching corridors belong to C4 wayfinding load; no duplicate. |
| `v2a_076` | defer | needs declared input | C16 | GREEN with spec | none | Territorial zones require a territory spec or reliable markers; image-only is weak. |
| `v2a_077` | keep | geometry/detector | enclosure partial | AMBER | Wave 2 | Barrier permeability is a distinct aperture/partition measure; useful for privacy/prospect. |
| `v2a_078` | defer | detector | C9/C10/prospect partial | AMBER | Wave 3 | Outdoor/nature escape requires window and view-content detection. |
| `v2a_079` | defer | detector + plan | C11 partial | AMBER | Wave 3 | Seat facing entrance needs seat, facing, and entrance detection. |
| `v2a_080` | keep | geometry/depth | height partial | AMBER | Wave 2 | Verticality cues can be estimated from vanishing/depth/ceiling-line geometry. |
| `v2a_081` | keep | classical-CV + geometry | glare/brightness partial | AMBER | Wave 1/2 | Dark-corner safety cue is spatial luminance distribution; needs corner/region localization. |
| `v2a_082` | merge | classical-CV | V1 contour angularity | AMBER | none | Already built as AMBER contour proxy. |
| `v2a_083` | merge | classical-CV | symmetry | GREEN current, AMBER construct | none | Already built. |
| `v2a_084` | merge | classical-CV | fractal_dimension, V9, V13 | AMBER | none | Already in fractal/orientation family; no extra fractal primitive until M1' and corpus. |
| `v2a_085` | merge | classical-CV | V6, V7, processing_load, C12 | AMBER | none | Clutter has three measures; Decision D2 says do not build a fourth. |
| `v2a_086` | defer | pretrained/VLM | none | AMBER | none | Maintenance/wear is semantic and bias-prone; previous V34 rejected. |
| `v2a_087` | merge | classical-CV | palette entropy, warmth | GREEN current, AMBER construct | none | Already covered by color entropy/saturation proxies. |
| `v2a_088` | keep | classical-CV | material/acoustic texture partial | AMBER | Wave 1 | Texture density is computable with local texture energy; distinct from global clutter. |
| `v2a_089` | defer | detector/VLM | landmark/clutter partial | AMBER | Wave 3 | Artwork density and semantic content need detector/VLM; descriptive unless tied to outcomes. |
| `v2a_090` | defer | detector/material | acoustic/material heuristic partial | AMBER | Wave 3 | Natural material fraction needs segmentation/material model; useful for wellbeing. |
| `v2a_091` | merge | classical-CV | V6/V7/processing | AMBER | none | Complexity gradients are clutter fields. |
| `v2a_092` | defer | detector/OCR | landmark/C4 partial | AMBER | Wave 3 | Signage density needs OCR/object detection; wayfinding link real. |
| `v2a_093` | defer | detector/VLM | none | AMBER | none | "Organization affordance" too semantic until components are specified. |
| `v2a_094` | keep | classical-CV | orientation entropy partial | AMBER | Wave 1 | Alignment/orderliness can use line orientation dispersion and vanishing consistency. |
| `v2a_095` | defer | geometry + corpus | V4 planned | AMBER | Wave 2/3 | Mystery is a construct target; image operator needs occlusivity/preview labels. |
| `v2a_096` | keep | pretrained segmentation | V3 planned | AMBER | Wave 3 | Visible vegetation is high-value and not built; needs segmentation/model and corpus. |
| `v2a_097` | keep | pretrained segmentation | C9/C10/prospect partial | AMBER | Wave 3 | Window-view content greenery/sky/water is high-value, detector-backed. |
| `v2a_098` | defer | material segmentation | material heuristic partial | AMBER | Wave 3 | Duplicates v2a_090; merge when material detector exists. |
| `v2a_099` | keep | pretrained segmentation | none | AMBER | Wave 3 | Blue-space view content is distinct but needs water/sky-through-window labels. |
| `v2a_100` | merge | geometry | prospect/C9/C10 | AMBER | none | Distant prospect is current prospect/view family. |
| `v2a_101` | defer | detector/spec | none | AMBER/spec | none | Natural ventilation cues are visible only weakly; operable windows need detector/spec. |
| `v2a_102` | reject | non-image sensor | C20 partial | out | none | Natural sound sources require audio or explicit source labels; still image not adequate. |
| `v2a_103` | merge | compound | C10 + future V3 | AMBER | none | Daylight-nature coupling should be a compound once V3 exists. |
| `v2a_104` | defer | VLM | none | AMBER | none | Seasonal cues are semantic and weak for interiors. |
| `v2a_105` | defer | detector/VLM | none | AMBER | none | Animal presence is detectable but rare and descriptive-only in architectural interiors. |
| `v2a_106` | keep | detector + geometry | sociopetal_seating function partial | AMBER | Wave 3 | Sociopetal seating exists if seats are supplied; needs native seat detector/labels. |
| `v2a_107` | merge | detector + geometry | C12 | AMBER | none | Crowding belongs to C12 plus seat/person inputs. |
| `v2a_108` | defer | detector/VLM | C7/C23 partial | AMBER | Wave 3 | Surveillance cameras/exposed workstations need object + plan semantics. |
| `v2a_109` | defer | detector + plan | C7 | AMBER/GREEN with inputs | Wave 3 | Privacy partitions/doors/curtains are useful detector targets. |
| `v2a_110` | defer | OCR/VLM | C16 | AMBER | none | Territorial markers need OCR/VLM and probably local policy context. |
| `v2a_111` | defer | VLM/style | none | AMBER | none | Formal/informal norms are descriptive style labels, not robust operators yet. |
| `v2a_112` | reject | operational/social | none | out | none | Shared-resource competition is not recoverable from one photo without usage data. |
| `v2a_113` | merge | compound/input | C23/C01 partial | AMBER | none | Social mixing affordance should be composed from seating, commons, path overlap. |
| `v2a_114` | reject | acoustic/social | C7/C20 partial | out/spec | none | Overhearing risk needs acoustic model and source/receiver inputs. |
| `v2a_115` | reject | operational/time | none | out | none | Waiting time is not an image attribute. |
| `v2a_116` | defer | detector/OCR | C17 | AMBER/GREEN with input | Wave 3 | Visible controls can populate `control_zones` but need detector/OCR. |
| `v2a_117` | defer | detector/VLM | none | AMBER | Wave 3 | Furniture adjustability needs furniture component classification. |
| `v2a_118` | keep | geometry/setting classifier | C13 partial | AMBER | Wave 2 | Choice richness can extend setting variety/zones; meaningful for agency. |
| `v2a_119` | defer | detector/VLM | C16 partial | AMBER | none | Personalization affordances need object/semantic labels; privacy risk. |
| `v2a_120` | defer | OCR/VLM | C17 partial | AMBER | none | Policy cues need text/sign detection; descriptive unless tied to actual agency. |
| `v2a_121` | merge | input/spec | C7/C17 | GREEN with input | none | Control over privacy doors belongs to C7/C17 declared inputs. |
| `v2a_122` | defer | detector + acoustic | C7/C20/C17 | AMBER | none | Headsets/sound controls are object-level and not enough for actual sound control. |
| `v2a_123` | defer | detector/spec | C17/C21 | AMBER | none | Fans/thermal controls need object detection and thermal spec. |
| `v2a_124` | defer | detector/spec | C17, lighting | AMBER | Wave 3 | Task lamps/blinds can feed local-control if detected. |
| `v2a_125` | merge | geometry/OCR | C4/C17 partial | AMBER | none | Wayfinding clarity is C4 plus future signage/OCR, not a separate primitive now. |

## arch.pattern Per-Construct Triage

| id | decision | class | existing fraction verified | tier | slot | reason |
|---|---|---|---|---|---|---|
| `arch.pattern.axial_circulation_clear` | merge | geometry | C3/C4, C1/C2 | AMBER | none | Axial clarity is wayfinding/integration geometry. |
| `arch.pattern.bay_window` | defer | detector | prospect/daylight | AMBER | Wave 3 | Pattern detector may help view/daylight, but not before window detector corpus. |
| `arch.pattern.central_hearth` | defer | detector/VLM | landmark partial | AMBER | none | Semantic pattern; weak generality outside residential/hospitality. |
| `arch.pattern.circulation_maze_like` | merge | geometry | C4 | AMBER | none | Maze-like circulation is C4 wayfinding load. |
| `arch.pattern.colonnade` | defer | detector/VLM | rhythm/edge partial | AMBER | none | Pattern is object/architectural-semantics; no immediate construct slot. |
| `arch.pattern.corner_window` | keep | detector/geometry | prospect/daylight partial | AMBER | Wave 3 | Distinct daylight/prospect pattern if window geometry is available. |
| `arch.pattern.daylight_hard` | keep | classical-CV | brightness/glare partial | AMBER | Wave 1 | Hard daylight is shadow-edge/contrast and maps to glare/ambience. |
| `arch.pattern.daylight_soft` | keep | classical-CV | brightness partial | AMBER | Wave 1 | Soft daylight is useful contrast to hard daylight; same operator family. |
| `arch.pattern.double_height_space` | keep | geometry/depth | C24/height partial | AMBER | Wave 2 | High-value spatial generosity cue; needs ceiling/depth validation. |
| `arch.pattern.gallery_edge` | merge | geometry | edge clarity, C4 | AMBER | none | Edge/circulation condition; no separate detector yet. |
| `arch.pattern.loft_mezzanine` | defer | detector/VLM | height partial | AMBER | none | Distinct but too semantic for current corpus. |
| `arch.pattern.long_view_corridor` | merge | geometry | C4, prospect, C9/C10 | AMBER | none | Already captured by sightline/prospect/wayfinding. |
| `arch.pattern.perimeter_seating` | defer | detector + plan | seats/C11 partial | AMBER | Wave 3 | Needs reliable seat detection and boundary relation. |
| `arch.pattern.prospect_strong` | merge | geometry | prospect/C11 | AMBER | none | Duplicate of prospect family. |
| `arch.pattern.refuge_nook` | merge | geometry/input | C11 | AMBER | none | Refuge belongs to C11/solitary-retreat compounds. |
| `arch.pattern.refuge_strong` | merge | geometry/input | C11 | AMBER | none | Duplicate of C11 refuge. |
| `arch.pattern.skylight_dominant` | defer | detector | daylight partial | AMBER | Wave 3 | Needs skylight detection; useful but not first wave. |
| `arch.pattern.staircase_sculptural` | defer | detector/VLM | landmark partial | AMBER | none | Mostly semantic landmark/object pattern. |
| `arch.pattern.threshold_emphasized` | keep | geometry/detector | doorway/edge partial | AMBER | Wave 2/3 | Useful for transition/wayfinding if thresholds can be detected. |
| `arch.pattern.window_seat_niche` | defer | detector + plan | prospect/daylight/C11 | AMBER | Wave 3 | Requires seat + window + niche geometry. |

## Remaining Family Verdicts

| family | decision | reason |
|---|---|---|
| `env.ae` | defer/merge | High-level binary tags should mostly be thresholds or compounds over continuous operators; keep only if a threshold is needed for UI, not as new science. |
| `env.v1` | reject from image pipeline | Physical-code values need instruments or declared spec inputs. They are valid CNfA inputs, not image operators. |
| `cnfa.*` | merge/selectively keep | Own namespace overlaps current registry; enumerate only missing dynamic/depth operators after M1'. |
| `component.*` | defer | Object/material detection needs pretrained models and labeled corpus; AMBER ceiling. |
| misc semantic | defer/keep plant_count only | Plant/biophilic ratio can feed V3; provenance/science rows are metadata. |
| `materials.*` | merge/defer | Existing material/acoustic heuristic exists; faithful material fractions need segmentation. |
| `spatial.*` | merge | Overlaps C1/prospect/enclosure/isovist planned family. |
| `style.*` | reject/defer | Style classifiers are descriptive and weakly linked; VLM-only, not first-order CNfA operators. |
| cross-modal sound/smell/touch | reject from image pipeline | Needs other sensors. |
| `color.*` | merge | Covered by palette entropy, warmth, luminance stats, unless a validated color-harmony formula is introduced. |
| `cognitive.*` | reject as operators | These are targets or outcomes; map to C3/C4/V4 but do not score directly. |
| `affect.*` | reject as operators | Cozy/tranquil/scary are labels for validation, not image features. |
| isovist/affordance | merge/selectively keep | Isovist variants belong to existing C1/prospect/enclosure geometry lane. |
| `texture.*` | merge/keep texture density | Most overlap V6/material texture; one texture-density primitive earns Wave 1. |
| `complexity.*` | merge | V6/V7/processing/fractal already cover it. |
| `social.*` | defer/merge | Needs seats/people/commons; use C7/C12/C23. |
| meta/provenance | reject as attributes | Metadata, not visual attributes. |

## Machine Image Inventory

### `Example Images/`

Reachable at `/Users/davidusa/REPOS/Image_Tagger_dk_latest/Example Images`. Count: 16 image files. All opened with PIL.

Usable subset:

| file | size | use |
|---|---:|---|
| `50-day-street-offices-norwalk-1200x1165-compact.jpg` | 1200x1165 | daylit office, warm/cool, glare/daylight, open office. |
| `50-day-street-offices-norwalk-3-1200x1131-compact.jpg` | 1200x1131 | same environment alternate view for replay. |
| `BalancedCare-Render-Corridor2-wpeople1_960x530.webp` | 2880x1200 | corridor, wayfinding, people/crowding caveat. |
| `Corridors_of_Classroom_Complex.jpg` | 1280x1707 | corridor/axial/wayfinding load. |
| `Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg` | 1024x819 | open-plan/clutter/material/warmth; baseline AMBER unit. |
| `Ludwig_Mies_van_der_Rohe__Farnsworth_House__1945-1951_2.jpg` | 1600x1092 | glass/prospect/daylight/high view. |
| `Office-Grade-1-1536x838.jpg` | 1536x838 | open office, ceiling, brightness variance. |
| `Seesaw-Studio_Office-Fitout_Bowen-Interiors-4-1536x1016.jpg` | 1536x1016 | seating/material/biophilic candidates. |
| `UPCycle-Gensler-5-889x592-1.jpg` | 889x592 | office, material/landmark/complexity. |
| `bede-offices-sofia-6-1200x800-compact.jpg` | 1200x800 | office, daylight/warmth/setting. |
| `heb-digital-and-favor-delivery-eastside-tech-hub-austin-6.jpg` | 1200x800 | open office, large-scale/ceiling/crowding. |
| `korridor.jpg` | 2000x1125 | corridor/long-view/wayfinding. |
| `mrwFhJGYxuweao836aMC9i.jpg` | 2000x1333 | interior visual complexity/material. |

The other three are usable only after visual inspection: `1 f_pic948 - David Židlický.jpg`, `image-asset.webp`, `originalfile1769166756859-4785.jpg`.

### `/Users/davidusa/REPOS/Post_Occupancy_Evals/Images`

The prompt's relative path was not under Image_Tagger; the actual local path is `/Users/davidusa/REPOS/Post_Occupancy_Evals/Images`. Count: 26 files by extension. PIL opened 24; two AVIF files did not open in the current PIL build.

Usable interiors or interior-like references:

| file | size/status | use |
|---|---:|---|
| `converted warehouse office.webp` | 360x201 | rough office material/ceiling; low resolution. |
| `desk facing wall.webp` | 462x280 | cellular/low prospect negative. |
| `desk open plan facing wall.png` | 1224x920 | desk-facing-wall comparison; prospect/refuge. |
| `high vs low ceiling.webp` | 676x481 | ceiling-height A-vs-B reference. |
| `looking out window at wall.jpg` | 539x360 | negative view/prospect control. |
| `room density.png` | 3024x5626 | density/crowding reference, likely diagram/collage. |
| `Prospect-and-Refuge-as-applied-to-project_W640.jpg` | 640x460 | concept illustration, not a natural corpus photo. |

Non-interior or only conceptual/instrument support: `EDI_melanopic meter.jpg`, `Fisheye lens.png`, `Nasa Tax Load Index.webp`, `PRS revised image*.png`, `STIPA.png`, `TVOC CO2 particulates.jpg`, `office temp survey.png`, `reaction time experiment.png`, `thermal imaging camera.jpg`, wavelength images, Holscher task images.

Unreadable here: `desk facing wall_2.avif`, `globe thermometer.avif`.

### Zotero Bibliography

Path checked: `/Users/davidusa/REPOS/__Zotero whole bibliography/files/`.

Direct image files found: 0. File type summary: 1319 PDFs, 93 HTML, 1 `.DS_Store`. This is valuable for literature and possible figure extraction, but it is not an immediately usable interior image database unless a separate PDF-figure extraction step is run and licensed.

## Explicit Google Drive Image Request

The local machine is too small and too biased to validate the candidate pool. Please export a Drive corpus with stable filenames, license/source notes, and, where possible, paired views of the same site. Minimum viable set: 120 interiors plus 80 labeled A-vs-B region pairs. Better first corpus: 200 interiors plus 150 A-vs-B pairs.

### Minimum Viable Drive Export

| category | count | required contrasts |
|---|---:|---|
| open-plan offices | 16 | cluttered/minimal, daylit/electric, high/low ceiling, warm/cool. |
| cellular/private offices | 12 | enclosed/open, desk-facing-wall/window, personalized/plain. |
| corridors | 12 | straight/axial, maze-like/branching, bright/dim corners, long/short view. |
| atrium/lobby/entrance | 12 | double-height/normal, landmark/no-landmark, prospect/refuge. |
| healthcare/waiting | 10 | seating density, view to nature, privacy, glare. |
| classrooms/libraries | 10 | legibility, clutter, daylight, seating arrangement. |
| hospitality/residential lounges | 10 | warm/cool, soft/hard materials, sociopetal/perimeter seating. |
| retail/cafe/common areas | 10 | dense objects, signage, social mixing, resource competition caveat. |
| biophilic interiors | 12 | high/low vegetation, visible sky/water, natural/synthetic materials. |
| negative controls | 16 | exteriors, diagrams, instrument photos, close-up objects, blank/near-blank scenes. |

### Required A-vs-B Region Pairs

| pair family | count | attributes exercised |
|---|---:|---|
| same image cluttered vs clean regions | 12 | V6/V7/processing, v2a_085, complexity gradients. |
| hard-shadow vs soft-shadow/daylight | 10 | v2a_009, v2a_014, arch.pattern.daylight_hard/soft. |
| warm vs cool zones | 8 | warmth, palette, v2a_011/v2a_015. |
| bright/glare source vs comfortable bright area | 8 | glare-risk, v2a_006, v2a_013. |
| high prospect vs low prospect seats | 12 | prospect, C11, v2a_070/v2a_079. |
| enclosed refuge vs exposed social zone | 10 | enclosure, refuge, privacy. |
| straight sightline vs branching choice point | 10 | C3/C4, v2a_071/v2a_074/v2a_075. |
| high ceiling vs low ceiling | 8 | v2a_067/v2a_080, double-height. |
| vegetation/window-view vs built/no-view | 12 | V3, v2a_096/v2a_097/v2a_099. |
| natural material vs synthetic/hard material | 8 | V12, v2a_090/v2a_098, acoustic proxy. |
| sociopetal vs anti-sociopetal seating | 8 | v2a_106, C23, conversation compounds. |
| visible user controls vs no controls | 6 | C17, v2a_116/v2a_124. |
| signage/clear route vs information overload | 8 | C4, v2a_092/v2a_125. |
| same image A/B equal controls | 8 | negative controls for pairwise false positives. |

### Image-To-Attribute Map

| image type requested | attributes it tests |
|---|---|
| striped or louvered high-contrast interior surface | faithful V2, spectral proxy, pattern-glare negative/positive ordering. |
| dense retail shelf or cluttered project room | V6/V7/processing, v2a_085, v2a_091. |
| minimal gallery or plain corridor | low clutter, low edge entropy, negative control for salience. |
| glass house / window-wall office | prospect, C9/C10, v2a_005/v2a_097/v2a_100. |
| desk facing blank wall | low prospect, high enclosure, refuge/prospect boundary. |
| straight institutional corridor | axial circulation, long-view corridor, C4. |
| branching corridor or maze-like school/hospital | wayfinding load, decision-point preview, blind corners. |
| double-height atrium | spatial generosity, ceiling height, verticality. |
| low-ceiling compressed office | ceiling-height contrast, enclosure, spatial generosity negative. |
| warm wood lounge | warmth, natural materials, hominess compounds, acoustic material proxy. |
| cool white clinical office | warm/cool opposite, glare/brightness controls. |
| plant-rich lobby or office | V3 vegetation, biophilia/restoration compounds. |
| window view to greenery/water/sky | view content, V3/V5, blue/green space. |
| window view to blank wall or built-up obstruction | negative view-content control. |
| seating in a circle around focal object | sociopetal seating, triangulation, social connectedness. |
| rows of seats facing same direction | anti-sociopetal negative control. |
| task lamp/blind/thermostat close-ups in context | local control detector, v2a_116/v2a_124. |
| signage-heavy corridor | signage salience/load, information control. |
| fisheye/panorama of same room as normal photo | capture-quality boundary test for geometry. |
| rendered CGI version and real photo of similar room | render-vs-photo robustness. |
