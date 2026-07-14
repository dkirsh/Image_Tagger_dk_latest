#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="$ROOT/cnfa_external/repos/HorizonNet"
CKPT_DIR="$REPO_DIR/ckpt"
WEIGHT_FILE="${HORIZONNET_WEIGHT_FILE:-resnet50_rnn__panos2d3d.pth}"
HF_REPO="${HORIZONNET_HF_REPO:-sunset1995/HorizonNet}"

cat <<INFO
HorizonNet manual install prep

Local repo: $REPO_DIR
Checkpoint dir: $CKPT_DIR
Hugging Face repo: $HF_REPO
Weight file: $WEIGHT_FILE

License posture:
- HorizonNet code is MIT.
- HorizonNet README says pretrained weights inherit the training datasets'
  licenses and terms of use.
- Do not redistribute downloaded weights until those dataset terms are reviewed.

This script is guarded. Re-run with --run to download the selected weight.
Override with:
  HORIZONNET_WEIGHT_FILE=<name>.pth bash $0 --run
INFO

if [[ "${1:-}" != "--run" ]]; then
  exit 0
fi

if ! command -v huggingface-cli >/dev/null 2>&1; then
  echo "Missing huggingface-cli. Install it first, for example: python3 -m pip install huggingface_hub" >&2
  exit 1
fi

mkdir -p "$CKPT_DIR"
huggingface-cli download "$HF_REPO" "$WEIGHT_FILE" --local-dir "$CKPT_DIR"
echo "Downloaded HorizonNet weight to $CKPT_DIR/$WEIGHT_FILE"
