#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_DIR="$ROOT/cnfa_external/repos/SpatialLM"
ENV_NAME="${SPATIALLM_ENV_NAME:-spatiallm}"

cat <<INFO
SpatialLM manual install prep

Local repo: $REPO_DIR
Conda env: $ENV_NAME

License posture:
- Local SpatialLM repo includes the Llama 3.2 Community License.
- SpatialLM1.1-Qwen-0.5B local model card declares CC-BY-NC-4.0.
- README says Qwen base is Apache-2.0, SpatialLM1.1 weights are CC-BY-NC-4.0,
  Pointcept-derived code is Apache-2.0, and TorchSparse is MIT.
- Use only for non-commercial local research unless David/legal approves more.

Technical posture:
- README-tested stack is Python 3.11, PyTorch 2.4.1, CUDA 12.4.
- This is intentionally manual because it may install CUDA/toolchain packages.

This script is guarded. Re-run with --run to execute the environment setup.
INFO

if [[ "${1:-}" != "--run" ]]; then
  exit 0
fi

if ! command -v conda >/dev/null 2>&1; then
  echo "Missing conda. Install Miniconda/Miniforge first." >&2
  exit 1
fi

if [[ ! -d "$REPO_DIR" ]]; then
  echo "Missing SpatialLM repo at $REPO_DIR" >&2
  exit 1
fi

conda create -y -n "$ENV_NAME" python=3.11
conda run -n "$ENV_NAME" conda install -y -c nvidia/label/cuda-12.4.0 cuda-toolkit conda-forge::sparsehash
conda run -n "$ENV_NAME" python -m pip install poetry
cd "$REPO_DIR"
conda run -n "$ENV_NAME" poetry config virtualenvs.create false --local
conda run -n "$ENV_NAME" poetry install
conda run -n "$ENV_NAME" poe install-torchsparse
conda run -n "$ENV_NAME" poe install-sonata
echo "SpatialLM environment prepared: $ENV_NAME"
