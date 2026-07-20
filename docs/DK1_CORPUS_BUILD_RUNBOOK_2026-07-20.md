# DK-1 — L6 corpus build runbook (2026-07-20)

The collector `scripts/collect_corpus_L6.py` turns corpus-building into a few commands. Payloads go
to Google Drive; `corpus_L6/manifest.csv` (git-tracked) + `corpus_L6/_provenance.csv` (sidecar) are
the local index. Targets: ~116 interiors, ~80 A/B pairs, plus nature_glass/materials/collections.

## 0. One-time setup (Mac)
    pip3 install requests pillow datasets kaggle --break-system-packages
    export UNSPLASH_ACCESS_KEY=...        # unsplash.com/developers (optional but best quality)
    export PEXELS_API_KEY=...             # pexels.com/api (optional)
    # Kaggle token -> ~/.kaggle/kaggle.json ; chmod 600 it   (for MIT Indoor67)
    rclone config                         # remote 'gdrive' -> type drive (already used for Structured3D)

## 1. Seed everything to Drive (one command)
    cd /Users/davidusa/REPOS/Image_Tagger_dk_latest
    python3 scripts/collect_corpus_L6.py --seed-all --gdrive gdrive:corpus_L6
Runs: MIT Indoor67 (volume + niches auto-routed) -> Unsplash niche top-ups -> A/B batch from the
collected interiors. Idempotent — safe to re-run to top up.

## 2. Check progress
    python3 scripts/collect_corpus_L6.py --status
Progress bars vs targets + source/licence/resolution/on-Drive breakdown + gap callouts. Repeat 1<->2
until "targets met".

## 3. Fill specific gaps (examples)
    python3 scripts/collect_corpus_L6.py --category nature_glass --source unsplash --limit 15 --gdrive
    python3 scripts/collect_corpus_L6.py --source from-dir --from-dir ~/indoorCVPR_09/Images --limit 80 --gdrive
    python3 scripts/collect_corpus_L6.py --source hf --hf-preset places365 --min-px 256 --limit 100 --gdrive

## 4. A/B pairs
    # controlled photometric pairs (light/affect operators; base = expected better):
    python3 scripts/collect_corpus_L6.py --gen-ab-batch 80 --ab-from interiors --gdrive
    # or a single hand-picked one:
    python3 scripts/collect_corpus_L6.py --gen-ab interiors/office_grade_1.png glare
    # a fully hand-curated real pair (YOUR expected-better call):
    python3 scripts/collect_corpus_L6.py --make-pair pairs/atriumA.png pairs/atriumB.png A "note"

## 5. Commit the index (NOT the payloads — .gitignore keeps PNGs out)
    git add corpus_L6/manifest.csv && git commit -m "L6 corpus: <what>"

## 6. Before an L6 calibration pass, pull payloads back local
    python3 scripts/collect_corpus_L6.py --rehydrate gdrive:corpus_L6

## Licences (all recorded per-image in _provenance.csv)
Unsplash/Pexels = commercial-OK, no attribution required. Openverse = per-image CC/PD. MIT Indoor67 /
Places365 / ADE20K = research licence — keep on your Drive, not redistributable (hence gitignored).

## Known gap — geometry / biophilia A/B pairs
The photometric generator makes controlled pairs for LIGHT/colour/affect operators only (same room,
one variable). Genuine geometry (prospect/enclosure/blind-corner) and biophilia (real greenery) A/B
still need either: (a) Structured3D render variants — same viewpoint, warm-vs-cold lighting or
full-vs-empty furniture — which requires the perspective-render download to succeed (the rclone
offload FAILED: only annotation_3d.zip transferred; copyurl errored on the image zips, partly the
rclone shared client_id retiring in 2026). Fix: create your own Google client_id
(rclone.org/drive/#making-your-own-client-id) and re-run cnfa_external_collect/collect_datasets_to_gdrive.sh,
or download the Structured3D perspective zips locally then `rclone copy` them up. Once the renders
exist, a Structured3D render-variant A/B generator is the clean next build. (b) Hand-curation of
real before/after or design-alternative pairs with an explicit expected-better.
