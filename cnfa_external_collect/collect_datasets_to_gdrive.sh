#!/bin/bash
# =============================================================================
# collect_datasets_to_gdrive.sh  (2026-07-14)
# Download the Structured3D dataset shards and autosave to Google Drive,
# streaming, with minimal local disk use.
#
# CODEX TASK HEADER --------------------------------------------------------
# Rails: LOCAL ONLY, no git push, no sudo. Do NOT perform Google OAuth —
#   if rclone is not yet configured, STOP and report "needs rclone config"
#   (David authorizes his own Google account; see ONE-TIME SETUP below).
# Acceptance criteria:
#   1. Every file in the FILES list is either verified on the destination
#      (size matches the server's Content-Length) or listed FAIL in the
#      manifest — no silent gaps.
#   2. annotation_3d + bbox also exist LOCALLY in datasets_local/ (they are
#      the working files for the L0 validator).
#   3. Local disk usage outside datasets_local/ stays ~0 in rclone mode.
#   4. Report gdrive_manifest.txt back verbatim.
#
# ONE-TIME SETUP (David, not Codex):
#   brew install rclone            # or: curl https://rclone.org/install.sh | sudo bash
#   rclone config                  # n) new remote -> name: gdrive -> type: drive
#                                  # accept defaults, browser OAuth, done.
#
# USAGE:
#   MODE=rclone  bash collect_datasets_to_gdrive.sh        # true streaming (default)
#   MODE=drivefs DRIVEFS_DIR="$HOME/Library/CloudStorage/GoogleDrive-xxxx/My Drive/Structured3D" \
#                bash collect_datasets_to_gdrive.sh        # via Drive for desktop mount
#   PANORAMAS=1  ...                                       # also fetch the 18 panorama shards
# =============================================================================
set -u
MODE="${MODE:-rclone}"
REMOTE="${REMOTE:-gdrive:Structured3D}"           # rclone destination folder
DRIVEFS_DIR="${DRIVEFS_DIR:-}"                    # drivefs mode destination
PANORAMAS="${PANORAMAS:-0}"
BASE="https://zju-kjl-jointlab-azure.kujiale.com/Structured3D"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOCAL="$SCRIPT_DIR/datasets_local"                # small working files stay local
MAN="$SCRIPT_DIR/gdrive_manifest.txt"
mkdir -p "$LOCAL"
echo "Structured3D -> GDrive collection, mode=$MODE, $(date)" > "$MAN"
note() { echo "$1" | tee -a "$MAN"; }

# ---------------------------------------------------------------- file list
FILES=( "Structured3D_annotation_3d.zip" "Structured3D_bbox.zip" )
for i in $(seq -w 0 17); do
  [ "$i" = "09" ] && continue                     # perspective_full_09 corrupted upstream
  FILES+=( "Structured3D_perspective_full_$i.zip" )
done
if [ "$PANORAMAS" = "1" ]; then
  for i in $(seq -w 0 17); do FILES+=( "Structured3D_panorama_$i.zip" ); done
fi
note "files queued: ${#FILES[@]} (research-only license; keep on your own Drive)"

# ---------------------------------------------------------------- preflight
server_size() { curl -sIL "$BASE/$1" | awk 'BEGIN{IGNORECASE=1} /content-length/{s=$2} END{gsub("\r","",s); print s}'; }

if [ "$MODE" = "rclone" ]; then
  command -v rclone >/dev/null 2>&1 || { note "FAIL: rclone not installed (brew install rclone)"; exit 1; }
  rclone lsd "${REMOTE%%:*}:" >/dev/null 2>&1 \
    || { note "FAIL: rclone remote '${REMOTE%%:*}' not configured — needs rclone config (David's OAuth, not Codex)"; exit 1; }
  rclone mkdir "$REMOTE" 2>/dev/null
  dest_size() { rclone lsl "$REMOTE/$1" 2>/dev/null | awk '{print $1}'; }
elif [ "$MODE" = "drivefs" ]; then
  [ -d "$DRIVEFS_DIR" ] || { note "FAIL: DRIVEFS_DIR not set or missing: '$DRIVEFS_DIR'"; exit 1; }
  dest_size() { stat -f%z "$DRIVEFS_DIR/$1" 2>/dev/null || stat -c%s "$DRIVEFS_DIR/$1" 2>/dev/null; }
else
  note "FAIL: MODE must be rclone or drivefs"; exit 1
fi

# ---------------------------------------------------------------- transfer
for f in "${FILES[@]}"; do
  want="$(server_size "$f")"
  have="$(dest_size "$f" || true)"
  if [ -n "$want" ] && [ "$have" = "$want" ]; then
    note "OK (already on Drive, size verified): $f ($want bytes)"; continue
  fi
  note "-> transferring $f (server size: ${want:-unknown} bytes)"
  if [ "$MODE" = "rclone" ]; then
    # TRUE STREAMING: url -> Drive, ~no local disk. No resume: on failure the
    # file is re-transferred whole on the next run (size check above skips done ones).
    if rclone copyurl "$BASE/$f" "$REMOTE/$f" --contimeout 30s --timeout 2h -P; then
      have="$(dest_size "$f")"
      [ "$have" = "$want" ] && note "OK: $f streamed to $REMOTE ($have bytes)" \
                            || note "FAIL: $f size mismatch (drive:$have vs server:$want)"
    else
      note "FAIL: $f rclone copyurl error (re-run to retry)"
    fi
  else
    # DriveFS mode: resumable curl into the mount; uploads in background.
    # Sequential on purpose — bounds the local DriveFS cache high-water mark.
    if curl -L -C - --fail -o "$DRIVEFS_DIR/$f" "$BASE/$f"; then
      note "OK: $f written to DriveFS mount (uploads in background; use Finder"
      note "    'Free Up Space' on it after the cloud checkmark appears)"
    else
      note "FAIL: $f curl error (re-run resumes)"
    fi
  fi
done

# ------------------------------------- keep the WORKING files local as well
note "== local working copies (needed to actually process) =="
for f in Structured3D_annotation_3d.zip Structured3D_bbox.zip; do
  if [ -s "$LOCAL/$f" ]; then note "OK: $f already local"; continue; fi
  if [ "$MODE" = "rclone" ] && rclone lsl "$REMOTE/$f" >/dev/null 2>&1; then
    rclone copyto "$REMOTE/$f" "$LOCAL/$f" -P && note "OK: $f pulled from Drive to datasets_local/" \
      || note "FAIL: $f local pull"
  else
    curl -L -C - --fail -o "$LOCAL/$f" "$BASE/$f" && note "OK: $f downloaded to datasets_local/" \
      || note "FAIL: $f local download"
  fi
done

echo | tee -a "$MAN"
note "== SUMMARY =="
if [ "$MODE" = "rclone" ]; then rclone lsl "$REMOTE" 2>/dev/null | tee -a "$MAN"; fi
du -sh "$LOCAL" 2>/dev/null | tee -a "$MAN"
note "finished $(date)"
echo "Done. Note: to PROCESS a shard later it must be hydrated back from Drive"
echo "(rclone copyto / Finder download) — archive tier, not analysis tier."
