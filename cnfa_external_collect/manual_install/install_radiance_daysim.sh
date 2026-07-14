#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS_DIR="$ROOT/cnfa_external/tools"
DAYSIM_DIR="$TOOLS_DIR/Daysim"

cat <<INFO
Radiance/DAYSIM manual install prep

Tools dir: $TOOLS_DIR
DAYSIM dir: $DAYSIM_DIR

License posture:
- Radiance current upstream license is Radiance Software License v2.0.
- DAYSIM public repository carries Radiance Software License v1.0.
- Local research use is acceptable. Redistribution/bundling needs David's legal
  call because DAYSIM uses older Radiance license terms and name-use clauses.

Manual steps:
1. Install Radiance. On macOS, Homebrew is the simplest path if available:
   brew install radiance
2. Confirm:
   rpict -version
3. Fetch DAYSIM source for inspection/build:
   git clone https://github.com/MITSustainableDesignLab/Daysim.git "$DAYSIM_DIR"
4. Follow DAYSIM build instructions for the target platform before wiring it
   into Image_Tagger_dk.

This script is guarded. Re-run with --run to run the Homebrew and git steps.
INFO

if [[ "${1:-}" != "--run" ]]; then
  exit 0
fi

mkdir -p "$TOOLS_DIR"

if command -v brew >/dev/null 2>&1; then
  brew install radiance
else
  echo "Homebrew not found. Install Radiance manually from https://www.radiance-online.org/download-install" >&2
fi

if [[ ! -d "$DAYSIM_DIR/.git" ]]; then
  git clone https://github.com/MITSustainableDesignLab/Daysim.git "$DAYSIM_DIR"
else
  git -C "$DAYSIM_DIR" pull --ff-only
fi

echo "Radiance/DAYSIM prep complete. Verify Radiance with: rpict -version"
