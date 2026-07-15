# External downloadable functions we can use (catalog, 2026-07-14)

Organized by which stage of OUR pipeline each replaces or upgrades. "Adapter"
= code in `cnfa_algs/adapters/` that already exists. Everything here runs on a
lab machine (most on CPU or a single modest GPU); the Claude sandbox blocks
model-weight downloads, so weights are fetched locally.

## 1. Plane / boundary segmentation (replaces the k-means heuristic, conf 0.45 -> ~0.85)
- **SegFormer ADE20K** (nvidia, Hugging Face) — wall/floor/ceiling/window/door/
  curtain/painting/plant among 150 classes. ADAPTER DONE
  (`segmentation_adapter.py`), incl. the class remap that fixes our two logged
  failure modes (art-as-opening, plant-as-opening).
- **Mask2Former / OneFormer ADE20K panoptic** — same classes + instance masks
  (each chair separately) in one pass; feeds clutter counts and seats too.
- **ESANet RGB-D** (TUI-NICR, PyTorch) — fuses depth + RGB for boundary
  precision that surpasses RGB-only models in cluttered rooms. ADAPTER DONE
  (`esanet_adapter.py`). Set `ESANET_CHECKPOINT` to enable; NYUv2 40-class
  → CNfA plane label mapping included. Pairs naturally with any depth provider.

## 2. Depth (replaces vanishing-point fallback, conf 0.35 -> ~0.7-0.9)
- **Depth Anything V2** ONNX — hook already wired (`DEPTH_ANYTHING_ONNX_PATH`).
  Small variant is Apache-2.0; larger ones CC-BY-NC.
- **Apple Depth Pro** (Apple, MIT) — TRUE METRIC depth in metres + estimated
  focal length, zero camera intrinsics needed. ADAPTER DONE
  (`depth_pro_adapter.py`). Set `DEPTH_PRO_CHECKPOINT` to enable. Priority-1 in
  DepthProvider — if present, everything downstream (prospect, openness, plan
  projection) gets metric-scale depth. Fixes the pre-registered failure
  "cross-image prospect not comparable."
- **Marigold** (prs-eth, Diffusers/HuggingFace) — diffusion-prior relative
  depth with superior visual quality. ADAPTER DONE (`marigold_adapter.py`).
  Auto-downloads from HuggingFace on first use. Highest visual quality tier
  for rendering/display, but relative (not metric).
- **Metric3D v2 / ZoeDepth / UniDepth** — METRIC depth alternatives.

## 3. Camera geometry (replaces the Hough vanishing-point estimate)
- **GeoCalib / PerspectiveFields** — per-image focal length, horizon, roll from
  a single photo. Kills the conf-0.20 VP failures (e.g. curved_classic) and
  gives the plan projection a trustworthy FOV instead of the assumed 65°.
- **HAWP** (cherubicXN, wireframe parser) — structural wireframe lines +
  junctions. ADAPTER DONE (`hawp_adapter.py`). Set `HAWP_CHECKPOINT` to enable.
  Provides `wireframe_vanishing_point()` that falls back to the existing Hough
  method automatically. Higher-confidence VP from learned architectural lines.

## 4. Layout -> floor plan (upgrades Tier B from heuristic to trained model)
- **SpatialLM 1.1** (manycore-research, NeurIPS 2025) — point cloud (from a
  casual phone VIDEO via MASt3R-SLAM/SLAM3R) -> walls/doors/windows/oriented
  furniture boxes as text. ADAPTER DONE (`spatiallm_adapter.py`): their text
  rasterizes into our PlanGrid at conf 0.8, and seat-class boxes with angle_z
  become REAL sociopetal-seating input (facing included!). Qwen-0.5B variant
  is Apache-2.0-based; 1.1 encoder weights CC-BY-NC (research OK).
- **uLayout** (JonathanLee112) — room layout boundaries (floor/ceiling/wall
  polygons) from a single perspective image. ADAPTER DONE
  (`ulayout_adapter.py`). Set `ULAYOUT_CHECKPOINT` to enable. Provides
  `layout_to_planes()` for direct feeding into `segment_planes(provided=)`.
- **HorizonNet / LGT-Net / DuLa-Net** (MIT-licensed, pretrained on
  Structured3D/PanoContext) — single 360-degree PANORAMA -> room boundary ->
  plan polygon. Relevant if the lab captures panoramas (one Ricoh Theta shot
  per room = a full Tier-C-grade plan).
- **MASt3R / DUSt3R / VGGT** — a handful of overlapping photos -> point cloud
  + camera poses, feed-forward, no SLAM rig. The missing link that turns
  "walk through with a phone" into SpatialLM input.

## 5. Objects / furniture (feeds sociopetal, clutter, activity zones)
- **GroundingDINO / OWL-ViT** (Apache) — open-vocabulary detection: "armchair",
  "sofa", "whiteboard", "coffee machine" — no fixed class list, so magnet-space
  and triangulation objects are detectable by NAME.
- **Ultralytics YOLO** (AGPL — license caution) or **RT-DETR** (Apache) for
  fast fixed-class furniture boxes.

## 6. Physics engines (upgrade proxies to simulations when a 3D model exists)
- **pyroomacoustics** (pip, MIT) — ADAPTER DONE (`acoustics_sim.py`, import-guarded; self-test included). Image-source + ray acoustic simulation:
  actual impulse responses, RT60, and STI in polyhedral rooms. Upgrades our
  alpha-table proxy to simulation-grade the moment a room polygon + material
  map exists (which SpatialLM/Structured3D provide). The essay's Part VI,
  runnable.
- **Radiance / DAYSIM (+ Accelerad GPU)** — the gold-standard daylight stack:
  sDA, ASE, UDI, and DGP glare on the 3D model. Replaces our glare heuristic
  with the metric the literature actually validates.

## 7. Plan-space analysis (cross-check OUR isovist fields)
- **depthmapX / depthmapXnet** (UCL, open source) — the canonical space-syntax
  VGA engine (visual integration, connectivity, clustering coefficient).
  Running it on the same PlanGrid cross-validates our ray fields against the
  field's reference implementation — reviewer-proofing.

## 8. Scene/context priors (already partly in the repo)
- **Places365** weights — already used by `room_detection.py` (scene class
  gates which attribute profile applies).
- **CLIP/SigLIP** embeddings — style/affect priors and image retrieval for
  building stratified validation sets ("find me 50 cool-toned clinical
  corridors").

## 9. Saliency / visual attention (replaces spectral-residual FFT)
- **TranSalNet** (deep transformer fixation prediction) — ADAPTER DONE
  (`saliency_adapter.py`). Set `TRANSALNET_CHECKPOINT` to enable. Falls back to
  spectral-residual FFT automatically. Fixes the pre-registered failure "bright
  window outsalients a memorable sculpture" in `landmark_salience`.
- Alternatives from the `awesome-human-visual-attention` collection: DeepGaze
  IIE, MSI-Net, UNISAL. Any model that outputs an (H,W) fixation probability
  map can drop in via the same `deep_saliency()` interface.

## 10. Composition analysis (pure code, no external model needed)
- **Rule of thirds + visual balance** — MODULE DONE (`composition.py`).
  Saliency-weighted composition metrics. Uses deep saliency if available,
  else spectral-residual FFT. Exports `rule_of_thirds()` and `visual_balance()`.

## Collection status (2026-07-14)
- Sandbox can fetch: common pip packages only. Weights (HF), GitHub clones, and
  niche packages (pyroomacoustics) are proxy-blocked from the sandbox.
- Therefore: run `structured3d/collect_external.sh`'s sibling
  `cnfa_external_collect/collect_external.sh` ONCE on a lab machine — it pip-installs
  the python layer, downloads all HF checkpoints, clones all repos into
  `cnfa_external/{weights,repos}`, writes a MANIFEST.txt, and lists the 5 manual
  steps that remain (HorizonNet GDrive weights, depthmapX binary, SpatialLM CUDA
  env, Radiance install, license review).

## Priority order for the lab (effort vs payoff)
1. **Depth Pro** — biggest single quality jump: metric depth → all downstream
   attributes (prospect, openness, plan) become cross-image comparable. MIT license.
2. SegFormer adapter live (pip install transformers; zero training) — biggest
   single reliability jump, fixes 2 logged failure modes.
3. **TranSalNet saliency** — fixes the landmark_salience FFT failure; enables
   composition metrics to use real fixation data.
4. **HAWP wireframe** — improves VP robustness on curved/difficult images.
5. GeoCalib — fixes the weak-VP images.
6. pyroomacoustics — acoustic proxy -> simulation on SpatialLM/S3D rooms.
7. **uLayout / ESANet** — structured layout + depth-fused segmentation.
8. **Marigold** — visual quality depth for rendering (lower priority than
   Depth Pro because it's relative, not metric).
9. SpatialLM video pipeline — one phone walkthrough per lab space -> plans +
   seats for every room in the building.
10. depthmapX cross-validation run.

