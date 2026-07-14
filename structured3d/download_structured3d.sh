#!/bin/bash
# Structured3D — minimal relevant subset for cnfa_algs validation (2026-07-13)
# Run this in YOUR terminal (needs normal internet). ~1 command, resumable (-C -).
#
# What and why:
#   annotation_3d  -> ground-truth room structure for ALL 3,500 scenes
#                     (true floor plans -> Tier C at scale + Tier B ground truth)
#   bbox           -> furniture instance boxes (sociopetal/clutter ground truth)
#   perspective_full_00 -> ONE shard of photorealistic renders with per-view
#                     ground-truth depth + semantics (Tier A/B validation).
#                     WARNING: shards are large (tens of GB). Start with one.
#                     Shard 09 is corrupted upstream - never fetch it.
#
# License: Structured3D is research-only; by downloading you accept its terms
# (https://structured3d-dataset.org). Do not redistribute.

set -e
DEST="$(dirname "$0")"
BASE="https://zju-kjl-jointlab-azure.kujiale.com/Structured3D"

for f in Structured3D_annotation_3d.zip Structured3D_bbox.zip; do
  echo "== $f"
  curl -L -C - -o "$DEST/$f" "$BASE/$f"
done

# Comment this out if disk is tight; annotation zips alone already enable
# the Tier C floor-plan validation on all 3,500 scenes.
echo "== Structured3D_perspective_full_00.zip (large - be patient)"
curl -L -C - -o "$DEST/Structured3D_perspective_full_00.zip" "$BASE/Structured3D_perspective_full_00.zip"

ls -lh "$DEST"/Structured3D_*.zip
echo "DONE. Tell Claude the files are here; it will unzip and process via the bridge."
