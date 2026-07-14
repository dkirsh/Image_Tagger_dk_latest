#!/bin/bash
# =============================================================================
# collect_external.sh  (v2, 2026-07-14)
# One-run collector for every external model/tool in
#   cnfa_algs/adapters/EXTERNAL_MODELS_CATALOG.md
#
# CODEX TASK HEADER --------------------------------------------------------
# Goal: run this script to completion in the repo folder
#   /Users/davidusa/REPOS/Image_Tagger_dk_latest/cnfa_external_collect/
# Rails: LOCAL ONLY. No git push. No sudo. No writes outside this folder's
#   cnfa_external/ tree and the local .venv it creates. If a single item
#   fails, continue; never fabricate a success line in the manifest.
# Acceptance criteria:
#   1. cnfa_external/MANIFEST.txt exists and every line is OK/FAIL/SKIP —
#      no item silently missing.
#   2. VERIFY section reports: venv imports OK; depth ONNX loads; acoustics
#      self-test PASS (hard room rings longer than soft room).
#   3. Total size printed; nothing outside cnfa_external/ and .venv modified.
#   4. Report the manifest verbatim back to David when done.
# Usage:
#   bash collect_external.sh                  # models + repos + pip layer
#   bash collect_external.sh --with-structured3d   # ALSO ~tens-of-GB dataset zips
# Resumable: safe to re-run; downloads resume/skip if already present.
# ----------------------------------------------------------------------------
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$SCRIPT_DIR/cnfa_external"
VENV="$SCRIPT_DIR/.venv"
MAN="$ROOT/MANIFEST.txt"
WITH_S3D=0
[ "${1:-}" = "--with-structured3d" ] && WITH_S3D=1

mkdir -p "$ROOT/weights" "$ROOT/repos" "$ROOT/datasets"
echo "cnfa external collection started $(date)" > "$MAN"
note() { echo "$1" | tee -a "$MAN"; }

# ------------------------------------------------------------ 0. python env
note "== [0] python venv =="
if [ ! -d "$VENV" ]; then python3 -m venv "$VENV" || { note "FAIL: venv creation"; exit 1; }; fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip -q && note "OK: pip upgraded ($(python -V))" \
  || note "FAIL: pip upgrade"

# ------------------------------------------------------------ 1. pip layer
note "== [1] pip packages =="
PIP_PKGS=(
  "numpy" "scipy" "pillow" "opencv-python-headless"
  "pyroomacoustics"            # acoustic image-source simulation (MIT)
  "transformers"               # SegFormer/ZoeDepth/GroundingDINO/OWLv2/CLIP runners
  "timm"                       # backbone zoo some models need
  "onnxruntime"                # depth ONNX inference
  "huggingface_hub[cli]"       # weight downloads
  "einops"                     # required by several vision repos
)
for pkg in "${PIP_PKGS[@]}"; do
  if pip install "$pkg" -q; then note "OK: pip $pkg"; else note "FAIL: pip $pkg"; fi
done
# torch: CPU wheel by default (Mac/CI safe). On the CUDA box, re-run with:
#   pip install torch --index-url https://download.pytorch.org/whl/cu124
if pip install torch --index-url https://download.pytorch.org/whl/cpu -q; then
  note "OK: pip torch (cpu build; swap for CUDA wheel on GPU box)"
else
  note "FAIL: pip torch"
fi

# ------------------------------------------------------- 2. HF checkpoints
note "== [2] Hugging Face checkpoints -> weights/ =="
# resolve whichever HF CLI name this hub version installed
if command -v hf >/dev/null 2>&1; then HFCLI="hf"
elif command -v huggingface-cli >/dev/null 2>&1; then HFCLI="huggingface-cli"
else HFCLI=""; note "FAIL: no HF CLI found (hf / huggingface-cli)"; fi

hfget() {  # $1 repo_id   $2 optional include-glob   $3 license note
  local repo="$1"; local inc="${2:-}"; local lic="${3:-}"
  local dest="$ROOT/weights/$(basename "$repo")"
  [ -z "$HFCLI" ] && { note "SKIP: $repo (no HF CLI)"; return; }
  if [ -n "$inc" ]; then
    $HFCLI download "$repo" --include "$inc" --local-dir "$dest" >/dev/null 2>&1
  else
    $HFCLI download "$repo" --local-dir "$dest" >/dev/null 2>&1
  fi
  if [ -d "$dest" ] && [ -n "$(ls -A "$dest" 2>/dev/null)" ]; then
    note "OK: HF $repo ($(du -sh "$dest" | cut -f1)) ${lic}"
  else
    note "FAIL: HF $repo"
  fi
}
hfget nvidia/segformer-b2-finetuned-ade-512-512 ""            "[license: NVIDIA, research OK]"
hfget facebook/mask2former-swin-base-ade-semantic ""          "[license: CC-BY-NC]"
hfget onnx-community/depth-anything-v2-small "onnx/*"         "[license: Apache-2.0]"
hfget Intel/zoedepth-nyu-kitti ""                             "[license: MIT] (METRIC depth)"
hfget IDEA-Research/grounding-dino-tiny ""                    "[license: Apache-2.0]"
hfget google/owlv2-base-patch16-ensemble ""                   "[license: Apache-2.0]"
hfget openai/clip-vit-base-patch32 ""                         "[license: MIT]"
hfget manycore-research/SpatialLM1.1-Qwen-0.5B ""             "[base Apache-2.0; encoder CC-BY-NC]"

# ------------------------------------------------------------- 3. repos
note "== [3] source repos -> repos/ =="
gget() {  # $1 org/repo   $2 note
  local dest="$ROOT/repos/$(basename "$1")"
  if [ -d "$dest/.git" ]; then note "OK: git $1 (already cloned)"; return; fi
  if git clone --depth 1 "https://github.com/$1" "$dest" >/dev/null 2>&1; then
    note "OK: git $1 ${2:-}"
  else
    note "FAIL: git $1"
  fi
}
gget manycore-research/SpatialLM   "(layout LLM inference code; CUDA env per its README)"
gget cvg/GeoCalib                  "(focal/horizon from one image; also: pip install geocalib)"
gget jinlinyi/PerspectiveFields    "(alt camera calibration)"
gget sunset1995/HorizonNet         "(pano->layout, MIT; weights are a MANUAL Google-Drive step)"
gget naver/mast3r                  "(photos->point cloud; weights per its README)"
gget SpaceGroupUCL/depthmapX       "(canonical VGA engine; build or use release binary)"

# --------------------------------------- 4. optional: Structured3D dataset
if [ "$WITH_S3D" = "1" ]; then
  note "== [4] Structured3D zips -> datasets/ (LARGE) =="
  S3D_BASE="https://zju-kjl-jointlab-azure.kujiale.com/Structured3D"
  for f in Structured3D_annotation_3d.zip Structured3D_bbox.zip \
           Structured3D_perspective_full_00.zip; do
    if curl -L -C - --fail -o "$ROOT/datasets/$f" "$S3D_BASE/$f"; then
      note "OK: $f ($(du -sh "$ROOT/datasets/$f" | cut -f1)) [research-only license]"
    else
      note "FAIL: $f"
    fi
  done
else
  note "SKIP: Structured3D zips (re-run with --with-structured3d; tens of GB)"
fi

# ------------------------------------------------------------- 5. verify
note "== [5] VERIFY =="
python - <<'PYEOF' 2>&1 | tee -a "$MAN"
import importlib, os, glob
ok = lambda m: print(f"OK: import {m}")
for m in ["numpy", "scipy", "cv2", "PIL", "transformers", "onnxruntime",
          "pyroomacoustics", "timm", "torch"]:
    try:
        importlib.import_module(m if m != "PIL" else "PIL.Image"); ok(m)
    except Exception as e:
        print(f"FAIL: import {m} -> {type(e).__name__}")

# depth ONNX loads?
root = os.path.join(os.path.dirname(os.path.abspath("MANIFEST.txt")), )
cands = glob.glob("cnfa_external/weights/depth-anything-v2-small/**/*.onnx", recursive=True)
if cands:
    try:
        import onnxruntime as ort
        s = ort.InferenceSession(cands[0], providers=["CPUExecutionProvider"])
        print(f"OK: depth ONNX loads ({os.path.basename(cands[0])}); "
              f"set DEPTH_ANYTHING_ONNX_PATH={os.path.abspath(cands[0])}")
    except Exception as e:
        print(f"FAIL: depth ONNX load -> {type(e).__name__}: {e}")
else:
    print("FAIL: no depth ONNX file found under weights/")

# acoustics simulation self-test (hard room must ring longer than soft)
try:
    import numpy as np, pyroomacoustics as pra
    def rt60(alpha):
        room = pra.Room.from_corners(np.array([[0,6,6,0],[0,0,4,4]], float),
                                     fs=16000, max_order=6,
                                     materials=pra.Material(alpha), air_absorption=True)
        room.extrude(2.8, materials=pra.Material(alpha))
        room.add_source([2.5, 2.0, 1.2]); room.add_microphone([3.8, 2.3, 1.2])
        room.compute_rir()
        return pra.experimental.rt60.measure_rt60(room.rir[0][0], fs=16000, decay_db=30)
    h, s = rt60(0.05), rt60(0.40)
    verdict = "PASS" if h > s else "FAIL"
    print(f"{'OK' if h>s else 'FAIL'}: acoustics self-test {verdict} "
          f"(hard {h:.2f}s vs soft {s:.2f}s)")
except Exception as e:
    print(f"FAIL: acoustics self-test -> {type(e).__name__}: {e}")
PYEOF

# ------------------------------------------------------------- 6. summary
note "== [6] manual steps remaining =="
note "MANUAL: HorizonNet pretrained .pth — Google Drive link in repos/HorizonNet/README"
note "MANUAL: depthmapX binary — GitHub releases page, or build repos/depthmapX"
note "MANUAL: SpatialLM inference env — CUDA 12.4 + Python 3.11 per repos/SpatialLM"
note "MANUAL: Radiance/DAYSIM (daylight) — https://www.radiance-online.org or brew"
note "MANUAL: license review before any redistribution (NC-flagged items above)"

echo | tee -a "$MAN"
note "== TOTALS =="
du -sh "$ROOT/weights" "$ROOT/repos" "$ROOT/datasets" 2>/dev/null | tee -a "$MAN"
note "collection finished $(date)"
echo
echo "==================== MANIFEST ===================="
cat "$MAN"
echo "=================================================="
echo "Done. Hand MANIFEST.txt back to David/Claude to wire adapter paths."
