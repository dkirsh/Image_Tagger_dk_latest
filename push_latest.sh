#!/usr/bin/env bash
# push_latest.sh — commit the corpus index + push the branch to `latest` (the remote Tanishq uses).
# Usage:  bash push_latest.sh
# Assumes GitHub HTTPS auth is set up (macOS Keychain or a Personal Access Token).
set -euo pipefail

REPO="/Users/davidusa/REPOS/Image_Tagger_dk_latest"
BRANCH="cnfa-algs-2026-07-14"
REMOTE="latest"

cd "$REPO"
git checkout "$BRANCH"

echo "== $(git rev-list --count HEAD ^"$REMOTE/$BRANCH" 2>/dev/null || echo '?') commit(s) ahead of $REMOTE/$BRANCH:"
git log --oneline "$REMOTE/$BRANCH..HEAD" 2>/dev/null || git log --oneline -16

# 1) Commit the tracked corpus index if it changed (PNGs are git-ignored; manifest is tracked).
if ! git diff --quiet -- corpus_L6/manifest.csv; then
  git add corpus_L6/manifest.csv
  git commit -m "corpus: update manifest to current collection ($(date +%Y-%m-%d))"
  echo "== committed manifest update"
else
  echo "== manifest unchanged"
fi

# 2) Track the provenance sidecar so a fresh clone can build the image DB (currently git-ignored).
if ! git ls-files --error-unmatch corpus_L6/_provenance.csv >/dev/null 2>&1; then
  grep -qxF '!corpus_L6/_provenance.csv' .gitignore || printf '!corpus_L6/_provenance.csv\n' >> .gitignore
  git add .gitignore corpus_L6/_provenance.csv
  git commit -m "corpus: track _provenance.csv sidecar for the image DB handoff"
  echo "== now tracking _provenance.csv"
fi

# 3) Push.
git push -u "$REMOTE" "$BRANCH"
echo "== pushed $BRANCH -> $REMOTE. Done."

# To also mirror to your other remotes, uncomment:
# git push origin "$BRANCH"
# git push tag-ucsd "$BRANCH"
