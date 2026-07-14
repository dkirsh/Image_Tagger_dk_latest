#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="$ROOT/cnfa_external/bin"
RELEASE_URL="${DEPTHMAPX_RELEASE_URL:-https://github.com/SpaceGroupUCL/depthmapX/releases}"

cat <<INFO
depthmapX manual install prep

Target bin dir: $BIN_DIR
Releases: $RELEASE_URL

License posture:
- depthmapX is GPLv3.
- Qt5 usage is LGPLv3.
- Local research use is acceptable, but redistribution/bundling needs David's
  legal call because GPLv3 is strong copyleft.

Manual steps:
1. Open the releases page.
2. Download the macOS release appropriate for this machine.
3. Place the executable or app wrapper under:
   $BIN_DIR/depthmapX
4. Verify with:
   $BIN_DIR/depthmapX --help

This script is guarded. Re-run with --run to create the target bin directory
and print the release URL again; it does not install binaries automatically.
INFO

if [[ "${1:-}" != "--run" ]]; then
  exit 0
fi

mkdir -p "$BIN_DIR"
echo "Download manually from: $RELEASE_URL"
echo "Place the binary at: $BIN_DIR/depthmapX"
