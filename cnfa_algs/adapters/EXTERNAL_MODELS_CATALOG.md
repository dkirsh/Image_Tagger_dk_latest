# External downloadable functions we can use (catalog, 2026-07-13)

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

## 2. Depth (replaces vanishing-point fallback, conf 0.35 -> ~0.7-0.9)
- **Depth Anything V2** ONNX — hook already wired (`DEPTH_ANYTHING_ONNX_PATH`).
  Small variant is Apache-2.0; larger ones CC-BY-NC.
- **Metric3D v2 / ZoeDepth / UniDepth** — METRIC depth (metres, not relative).
  This single swap fixes the pre-registered failure "cross-image prospect not
  comparable" — absolute scale stops depending on the vanishing point.

## 3. Camera geometry (replaces the Hough vanishing-point estimate)
- **GeoCalib / PerspectiveFields** — per-image focal length, horizon, roll from
  a single photo. Kills the conf-0.20 VP failures (e.g. curved_classic) and
  gives the plan projection a trustworthy FOV instead of the assumed 65°.

## 4. Layout -> floor plan (upgrades Tier B from heuristic to trained model)
- **SpatialLM 1.1** (manycore-research, NeurIPS 2025) — point cloud (from a
  casual phone VIDEO via MASt3R-SLAM/SLAM3R) -> walls/doors/windows/oriented
  furniture boxes as text. ADAPTER DONE (`spatiallm_adapter.py`): their text
  rasterizes into our PlanGrid at conf 0.8, and seat-class boxes with angle_z
  become REAL sociopetal-seating input (facing included!). Qwen-0.5B variant
  is Apache-2.0-based; 1.1 encoder weights CC-BY-NC (research OK).
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

## Collection status (2026-07-13)
- Sandbox can fetch: common pip packages only. Weights (HF), GitHub clones, and
  niche packages (pyroomacoustics) are proxy-blocked from the sandbox.
- Therefore: run `structured3d/collect_external.sh`'s sibling
  `cnfa_external_collect/collect_external.sh` ONCE on a lab machine — it pip-installs
  the python layer, downloads all HF checkpoints, clones all repos into
  `cnfa_external/{weights,repos}`, writes a MANIFEST.txt, and lists the 5 manual
  steps that remain (HorizonNet GDrive weights, depthmapX binary, SpatialLM CUDA
  env, Radiance install, license review).

## Priority order for the lab (effort vs payoff)
1. SegFormer adapter live (pip install transformers; zero training) — biggest
   single reliability jump, fixes 2 logged failure modes.
2. Metric depth (Metric3D/ZoeDepth ONNX) — fixes cross-image comparability.
3. GeoCalib — fixes the weak-VP images.
4. pyroomacoustics — acoustic proxy -> simulation on SpatialLM/S3D rooms.
5. SpatialLM video pipeline — one phone walkthrough per lab space -> plans +
   seats for every room in the building.
6. depthmapX cross-validation run.
