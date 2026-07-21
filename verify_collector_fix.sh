#!/usr/bin/env bash
# verify_collector_fix.sh — prove filename uniqueness + audit the live L6 corpus. Read-only on corpus_L6/.
set -uo pipefail
REPO="/Users/davidusa/REPOS/Image_Tagger_dk_latest"
cd "$REPO" || { echo "repo not found"; exit 2; }

python3 - "$REPO" <<'PY'
import importlib.util, tempfile, csv, sys
from pathlib import Path
from PIL import Image

REPO = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("cc", REPO / "scripts" / "collect_corpus_L6.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)

rc = 0
# ---------- 1) REGRESSION: reproduce the MIT collision, assert it's gone ----------
tmp = Path(tempfile.mkdtemp()); (tmp / "corpus_L6").mkdir()
cc.CORPUS = tmp / "corpus_L6"; cc.MANIFEST = cc.CORPUS / "manifest.csv"; cc.PROVENANCE = cc.CORPUS / "_provenance.csv"
cc.GDRIVE_REMOTE = None; cc.OFFLOAD = False

N = 26
root = tmp / "indoorCVPR_09" / "Images" / "greenhouse"; root.mkdir(parents=True)
for i in range(N):
    # long common-prefix stems: the exact shape that collapsed under the old 28-char truncation
    stem = f"greenhouse_google_com_scancollection_{i:05d}"
    Image.new("RGB", (1100, 1100), (i * 7 % 256, (i * 13) % 256, (i * 29) % 256)).save(root / f"{stem}.jpg")

gen = cc.walk_dir(root.parent, cc.MIT_INDOOR_KEEP, "interiors", "mit_indoor67", N * 2)
kept = cc.collect_from_examples(gen, limit=N, min_px=1024, dry=False)

files = list(cc.CORPUS.rglob("*.png"))
rows = list(csv.DictReader(cc.MANIFEST.open()))
prov = list(csv.DictReader(cc.PROVENANCE.open()))
names = [r["filename"] for r in rows]
print(f"[regression] kept={kept}  files_on_disk={len(files)}  manifest_rows={len(rows)}  "
      f"provenance_rows={len(prov)}  distinct_filenames={len(set(names))}")
ok = (kept == N and len(files) == N and len(rows) == N and len(prov) == N and len(set(names)) == N)
if ok:
    print("[regression] PASS — 26 distinct source ids -> 26 distinct files, no overwrite")
else:
    print("[regression] FAIL — filename collision still present"); rc = 1

# ---------- 2) AUDIT the live corpus (read-only) ----------
M = REPO / "corpus_L6" / "manifest.csv"; P = REPO / "corpus_L6" / "_provenance.csv"
if M.exists():
    lrows = list(csv.DictReader(M.open()))
    lnames = [r["filename"] for r in lrows]
    from collections import Counter
    dupes = {n: c for n, c in Counter(lnames).items() if c > 1}
    print(f"\n[audit] manifest rows={len(lrows)}  distinct filenames={len(set(lnames))}")
    if dupes:
        print(f"[audit] DUPLICATE filenames still in manifest ({len(dupes)}): "
              f"{list(dupes.items())[:5]}{' ...' if len(dupes) > 5 else ''}"); rc = 1
    else:
        print("[audit] no duplicate filenames in manifest  OK")
    # orphans: rows whose local file is missing AND no gdrive_path recorded
    provmap = {}
    if P.exists():
        provmap = {r["filename"]: r.get("gdrive_path", "") for r in csv.DictReader(P.open())}
    orphans = [n for n in lnames
               if not (REPO / "corpus_L6" / n).exists() and not provmap.get(n)]
    if orphans:
        print(f"[audit] {len(orphans)} rows point to a missing local file with no gdrive_path "
              f"(reconcile these): {orphans[:5]}{' ...' if len(orphans) > 5 else ''}")
    else:
        print("[audit] every manifest row resolves to a local file or a Drive path  OK")
    # pairs referencing a missing base
    bad_pairs = [r["filename"] for r in lrows if r["pair_id"]
                 and not (REPO / "corpus_L6" / r["filename"]).exists() and not provmap.get(r["filename"])]
    if bad_pairs:
        print(f"[audit] pair members with no file/Drive object: {bad_pairs}")
else:
    print("\n[audit] no live manifest yet (nothing to audit)")

print("\nRESULT:", "ALL GOOD ✅" if rc == 0 else "PROBLEMS FOUND ❌")
sys.exit(rc)
PY
