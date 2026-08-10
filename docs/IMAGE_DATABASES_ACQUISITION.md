# Image Databases — what we want and how to get them

*Acquisition list for the Image_Tagger program. For Stephan (downloads + research agreements) and Tanishq
(purpose-built sets). Compiled 2026-07-31 by cowork. Lives at `docs/IMAGE_DATABASES_ACQUISITION.md`. Pairs
with the collection rationale in `docs/PROGRAM_ROADMAP.md` (§Image databases).*

## How to read this — four things before downloading anything
1. **Where the data must live.** On the machine where the tagger runs (Codex's environment / a shared data
   volume), **not** in the Cowork cloud session. Cowork only needs manifests or small samples for study
   design. Do not try to route multi-GB sets through the desktop bridge.
2. **Storage.** Everything at full resolution is >2 TB. Pull **subsets first** (validation splits; MINC-2500
   instead of full MINC; Hypersim per-scene; Places365 small-256). A dedicated external/data drive is worth
   it.
3. **Licensing.** Several are research-only and need a **PI signature or a terms form** (flagged ⚠️ below).
   David or Stephan signs those; a student cannot.
4. **Priority.** Do them in the order in the last section, not top-to-bottom. Two datasets unblock the current
   critical path; most of the rest are backbone.

## What we already have (don't re-fetch)
- **SAVOIAS** — the complexity ground-truth set, already in the repo (`corpus_L6` is derived from it).
- **Drive `image collection` folder** (your link 1): subfolders `interiors`, `pairs`, `collections` — the
  working corpus and the **start of the facet-isolation `pairs`**. Worth auditing before building more.
- **Structured3D annotations** (your link 2): `Structured3D_annotation_3d.zip` — the 3D strand is partly
  seeded; still need the Structured3D *images* (⚠️ registration).
- **Downloads / other mounts:** no ML image datasets found (one `Material samples.zip` of unknown content —
  worth a look for the materials strand).

---

## Off-the-shelf datasets (Stephan downloads)

### Strand A — complexity / clutter / scenes
| dataset | why we want it | ~size | access | method |
|---|---|---|---|---|
| **ADE20K** ⚠️ | full scene parsing (objects + parts + materials) → ground truth for surface_density & arrangement | ~4 GB | registration/terms | GitHub `CSAILVision/ADE20K`; full data via the ADE20K site terms form. Benchmark subset is direct in `CSAILVision/sceneparsing`. |
| **SUN Attributes** | 102 human scene attributes incl. **"cluttered," "open area," "cluttered space"** — direct human labels for our species | ~2 GB annotations (+ SUN397 base images) | direct | Patterson & Hays SUN Attribute DB page; base images from the SUN397 release. |
| **Places365** | scene backbone, 365 categories, 1.8 M images | ~24 GB (Standard-256) | direct | `places2.csail.mit.edu` — direct tars; grab the val split first (~0.5 GB). |
| **MIT Indoor67** | indoor-scene coverage | ~2.4 GB | direct | `web.mit.edu/torralba/www/indoor.html`. |

### Strand B — materials & texture
| dataset | why | ~size | access | method |
|---|---|---|---|---|
| **MINC-2500** | material recognition, 23 classes — lets the tagger *propose* a material register | ~2.6 GB | direct / HuggingFace | Cornell `opensurfaces.cs.cornell.edu/publications/minc/`; mirror `huggingface.co/datasets/mcimpoi/minc-2500_split_1`. (Full MINC is much larger — the 2500 subset is enough to start.) |
| **OpenSurfaces** ⚠️ | segmented surfaces with **material + reflectance/gloss** labels (maps onto MEDIATORS §2) | ~20 GB | registration | `opensurfaces.cs.cornell.edu`. |
| **DTD (Describable Textures)** | 47 texture attributes → feeds fractal / textural_discomfort | ~600 MB | direct | `robots.ox.ac.uk/~vgg/data/dtd`. |
| **FMD (Flickr Material DB)** | 10 materials, clean — good cross-check | ~200 MB | direct | `people.csail.mit.edu/celiu/CVPR2010/FMD`. |

### Strand F — aesthetics / affect
| dataset | why | ~size | access | method |
|---|---|---|---|---|
| **OASIS** | 900 images with **valence/arousal norms**, **open** — anchors the affective-stress channel | small | direct | open academic download (Kurdi, Lozano & Banaji). **Use instead of IAPS.** |
| **GAPED** | affective picture set, open | ~1 GB | direct | Geneva Affective Picture Database. |
| **AVA** | 250 k images with aesthetic ratings + attributes | ~30 GB | script | downloader e.g. `mtobeiyf/ava_downloader` (images from DPChallenge). |
| **IAPS** ⚠️ | classic affective norms | small | restricted request | request from CSEA (Univ. Florida). Gated — prefer OASIS/GAPED unless a reviewer insists. |

### Strand C — occupancy / crowd (density ground truth)
| dataset | why | ~size | access | method |
|---|---|---|---|---|
| **ShanghaiTech Crowd Counting** | density ground truth for the occupancy-cue reader | ~2 GB | direct | GitHub mirrors. |
| **JHU-CROWD++** ⚠️ | large, richer crowd annotations | ~4 GB | registration | `crowd-counting.com`. |
| **UCF-QNRF** ⚠️ | high-count crowds | ~4 GB | registration | `crcv.ucf.edu/data/ucf-qnrf`. |

### Strand E — 3D / geometry (for isovist/visibility on real geometry)
| dataset | why | ~size | access | method |
|---|---|---|---|---|
| **Structured3D** ⚠️ | synthetic interiors w/ geometry (we have the annotations) | large | registration (non-commercial) | `structured3d-dataset.org` — need the *image* archives. |
| **Hypersim** | photorealistic synthetic interiors w/ ground-truth geometry/material/lighting | ~1.9 TB full | script (per-scene) | `github.com/apple/ml-hypersim` download script — pull a handful of scenes, not the whole thing. |
| **Matterport3D** ⚠️ | real RGBD building scans | large | academic-use agreement | `niessner.github.io/Matterport` (sign + email). |
| **ScanNet** ⚠️ | real RGBD indoor scans | large | terms-of-use form | `github.com/ScanNet/ScanNet`. |
| **Replica** | high-quality reconstructed indoor spaces | ~10 GB | direct | `github.com/facebookresearch/Replica-Dataset`. |

---

## Purpose-built sets (Tanishq / RA — nothing public substitutes)
These carry our **novel** claims; they isolate one variable, so no off-the-shelf set works. Small, high-value.
Cowork supplies the generation scripts and manifests; Tanishq collects/curates.

| set | what | who builds it | method |
|---|---|---|---|
| **Facet-isolation pairs** | same scene, one clutter species varied (hold surface_density, vary arrangement, etc.) | Tanishq (from the Drive `pairs` start) | edit/re-stage real interiors; cowork writes the edit protocol + checks with the reference measures |
| **Gestalt-refund / Mooney set** | two-tone images that resolve on closure vs disorder baked into statistics — the manuscript's sharpest test | Tanishq + cowork script | threshold grayscale photos → Mooney; pair with grayscale solutions; cowork provides the generator |
| **Occupancy series** | the **same space** empty / working / crowded — unblocks the social strand | Tanishq (short shoot or time-lapse/webcam pull) | almost nothing public holds the space constant while varying people; a purpose shoot or time-lapse extraction |
| **Phase-scrambled controls** | identical amplitude spectrum, structure destroyed — the "no gestalt" arm | cowork script (trivial) | run any scene set through a phase-scramble script |
| **Neurodiverse sensory set** | curated glare / echo / high-variety scenes for the sensory-load claims | Tanishq curates | tag from Places365 / SUN + a few purpose shots |

---

## Priority order (do this, not top-to-bottom)
1. **ADE20K + SUN Attributes** — unblock the clutter strand (segmentation GT + human "cluttered" labels).
2. **MINC-2500 + OpenSurfaces** — unblock the materials register.
3. **Build the facet-isolation and gestalt-refund/Mooney pairs** — unblock the manuscript's experiments (audit
   the Drive `pairs` folder first; you may be partway there).
4. **Occupancy series** — unblock the social-presence strand.
5. Backbone, when convenient: **Places365, DTD, OASIS**, then the **3D sets** (we have Structured3D annotations;
   add Hypersim per-scene).

## Who does what
- **Stephan** — download the off-the-shelf sets above; sign the ⚠️ research agreements (ADE20K, OpenSurfaces,
  Structured3D, Matterport3D, ScanNet, JHU/QNRF, IAPS if used); stage onto the tagger's data volume.
- **Tanishq** — build the purpose-built sets; audit the existing Drive `pairs`/`collections`; run cowork's
  phase-scramble / Mooney generators.
- **Cowork** — supply the generation scripts (phase-scramble, Mooney threshold, facet-edit protocol) and the
  manifests; validate the constructed pairs against the reference measures.
- **Codex** — point the tagger at the staged data; write the loaders; wire material/occupancy recognition.

*Verify each URL at download time — dataset hosts move. The access **method** (direct / registration / script)
is the stable part.*
