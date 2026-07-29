#!/bin/bash
# =============================================================================
# bg_offload.sh — detached, sleep-proof, resumable Structured3D → GDrive offload
# Built 2026-07-14 for offload over a flaky/mobile connection.
#
# LAUNCH ONCE, then walk away (survives terminal close + Mac sleep):
#   cd /Users/davidusa/REPOS/Image_Tagger_dk_latest
#   caffeinate -is nohup bash cnfa_external_collect/bg_offload.sh \
#       > cnfa_external_collect/gdrive_offload.log 2>&1 &
#
# CHECK PROGRESS anytime (safe, read-only):
#   tail -n 20 cnfa_external_collect/gdrive_offload.log
#   /opt/homebrew/bin/rclone lsl gdrive:Structured3D
#
# What it does, in priority order (critical + resumable first):
#   1. annotation_3d.zip + bbox.zip  -> copy to Drive, keep local (working set)
#   2. perspective_full_00.zip       -> copy to Drive, then free local disk
#   3. (optional) a few more shards only if PULL_EXTRA is set
# rclone `copy` is RESUMABLE and retry-heavy, so a dropped connection resumes
# rather than restarting. Every file is size-verified on Drive before any local
# delete (RULE 0). Nothing is deleted that isn't first confirmed on Drive.
# =============================================================================
set -u
export PATH=/opt/homebrew/bin:$PATH          # use the working rclone, not the crashing one
RCLONE=/opt/homebrew/bin/rclone
REMOTE=gdrive:Structured3D
ROOT=/Users/davidusa/REPOS/Image_Tagger_dk_latest
LOCALDIR="$ROOT/structured3d"                # where the ~13G already sit (per Codex)
KEEP="$ROOT/cnfa_external_collect/datasets_local"
mkdir -p "$KEEP"
PULL_EXTRA="${PULL_EXTRA:-}"                  # set to a space list e.g. "01 02" to also stream shards
BASE="https://zju-kjl-jointlab-azure.kujiale.com/Structured3D"

LOGFILE="$ROOT/cnfa_external_collect/gdrive_offload.log"
STATUS="$ROOT/cnfa_external_collect/gdrive_offload.status"
ts() { date "+%Y-%m-%d %H:%M:%S"; }
# append per-line so the log is readable live even under nohup (no block buffering)
log() { echo "[$(ts)] $*" >> "$LOGFILE"; echo "[$(ts)] $*"; }
setstatus() { echo "[$(ts)] $*" > "$STATUS"; }

: > "$LOGFILE"
setstatus "starting"
log "=== bg_offload start (PID $$) ==="
timeout 60 $RCLONE mkdir "$REMOTE" --contimeout 20s --timeout 60s 2>/dev/null

# retry-until-verified copy of a LOCAL file, then act (keep|free)
copy_local() {  # $1 filename  $2 keep|free
  local f="$1" mode="$2" srcdir=""
  for d in "$LOCALDIR" "$ROOT/cnfa_external_collect/cnfa_external/datasets"; do
    [ -f "$d/$f" ] && srcdir="$d" && break
  done
  if [ -z "$srcdir" ]; then log "SKIP $f (not found locally)"; return; fi
  local want; want=$(stat -f%z "$srcdir/$f" 2>/dev/null || stat -c%s "$srcdir/$f")
  log "COPY $f ($want bytes) from $srcdir ..."
  # resumable, patient on flaky links; loops until Drive size matches source
  local tries=0
  while true; do
    tries=$((tries+1))
    setstatus "copying $f (try $tries)"
    $RCLONE copy "$srcdir/$f" "$REMOTE/" \
        --contimeout 20s --timeout 120s \
        --retries 30 --low-level-retries 20 --retries-sleep 20s \
        --transfers 1 --checkers 2 --stats 30s --stats-one-line 2>&1 | tee -a "$LOGFILE"
    local have; have=$(timeout 60 $RCLONE lsl "$REMOTE/$f" --contimeout 20s 2>/dev/null | awk '{print $1}')
    if [ "$have" = "$want" ]; then
      log "VERIFIED on Drive: $f"
      break
    fi
    log "  $f incomplete (drive:$have want:$want) — retry $tries after 30s"
    sleep 30
  done
  if [ "$mode" = "keep" ]; then
    cp -f "$srcdir/$f" "$KEEP/$f" 2>/dev/null && log "KEPT local working copy: $KEEP/$f"
  else
    rm -f "$srcdir/$f" && log "FREED local disk: removed $srcdir/$f (verified on Drive first)"
  fi
}

# ---- priority 1: the working set (tiny, critical, keep local) ----
copy_local "Structured3D_annotation_3d.zip" keep
copy_local "Structured3D_bbox.zip"          keep

# ---- priority 2: the one perspective shard already downloaded (free disk) ----
copy_local "Structured3D_perspective_full_00.zip" free

# ---- priority 3 (optional): stream more shards only if asked ----
if [ -n "$PULL_EXTRA" ]; then
  for i in $PULL_EXTRA; do
    [ "$i" = "09" ] && { log "SKIP shard 09 (corrupted upstream)"; continue; }
    f="Structured3D_perspective_full_$i.zip"
    log "STREAM $f from server -> Drive (not resumable mid-file; retries whole)"
    $RCLONE copyurl "$BASE/$f" "$REMOTE/$f" --retries 10 --timeout 4h -P \
      && log "STREAMED: $f" || log "FAILED stream: $f (re-run to retry)"
  done
fi

setstatus "DONE"
log "=== bg_offload DONE ==="
log "Drive listing:"
$RCLONE lsl "$REMOTE" 2>/dev/null
log "Local working set:"
ls -la "$KEEP" 2>/dev/null
