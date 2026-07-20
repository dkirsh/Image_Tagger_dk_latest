#!/usr/bin/env python3
"""
collect_corpus_L6.py — a licence-clean image collector for the L6 calibration corpus.

WHAT IT DOES
  Fetches interior / biophilia / material / etc. photos from properly-licensed sources, filters for
  quality (min resolution, sane aspect, de-dup), converts each to canonical PNG at NATIVE resolution
  (no upscaling), places it under corpus_L6/<category>/, appends a row to corpus_L6/manifest.csv in
  the repo's exact schema, and records full provenance (source, author, licence, URL, dims, sha256)
  in corpus_L6/_provenance.csv so every image is attributable and re-checkable.

  It collects SINGLETONS (interiors + niche categories). Genuine A/B pairs need human judgment for the
  "expected better" call — use --make-pair for that step (see below); the collector never guesses it.

SOURCES (pick with --source; combine by running more than once)
  openverse  keyless (optional OPENVERSE_TOKEN for higher rate limits) — aggregates CC/PD images
             from Flickr, Wikimedia, museums, etc. Good default; licence metadata comes back per image.
  unsplash   needs UNSPLASH_ACCESS_KEY. High-res, watermark-free. Unsplash Licence (commercial OK).
  pexels     needs PEXELS_API_KEY. High-res, watermark-free. Pexels Licence (commercial OK).

WHY these: free/known licence, native resolution, no watermarks or UI chrome — exactly the corpus rule.
Avoid scraping ArchDaily/Dezeen/Pinterest (copyright) and Freepik (attribution / AI content).

INSTALL (Mac)
  pip3 install requests pillow --break-system-packages

USAGE
  export UNSPLASH_ACCESS_KEY=...        # optional
  export PEXELS_API_KEY=...             # optional
  # see what WOULD be collected, no downloads, no writes:
  python3 scripts/collect_corpus_L6.py --category interiors --source openverse --limit 20 --dry-run
  # actually collect 40 interiors from Unsplash into corpus_L6/interiors/:
  python3 scripts/collect_corpus_L6.py --category interiors --source unsplash --limit 40
  # collect every category's default queries (10 each) from openverse:
  python3 scripts/collect_corpus_L6.py --all --source openverse --limit 10
  # register a curated A/B pair (YOU decide the better one):
  python3 scripts/collect_corpus_L6.py --make-pair pairs/atrium_daylit.png pairs/atrium_dim.png A \
          "daylit atrium expected more restorative than the dim variant (same room)"

NOTES
  - Idempotent: already-collected source ids (tracked in _provenance.csv) are skipped.
  - --min-px (default 1024) drops small / likely-upscaled images (checked on the DOWNLOADED pixels).
  - Manifest rows are written in the repo schema: filename,category,pair_id,pair_expected_better,notes.
  - Run from the repo root (it locates corpus_L6/ relative to this file's parent-of-parent).
"""
from __future__ import annotations
import argparse, csv, hashlib, io, os, re, sys, time, json
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    from PIL import Image
except ImportError:
    sys.exit("Missing deps. Run: pip3 install requests pillow --break-system-packages")

REPO = Path(__file__).resolve().parent.parent
CORPUS = REPO / "corpus_L6"
MANIFEST = CORPUS / "manifest.csv"
PROVENANCE = CORPUS / "_provenance.csv"          # gitignored (corpus_L6/*), full attribution
MANIFEST_COLS = ["filename", "category", "pair_id", "pair_expected_better", "notes"]
PROV_COLS = ["filename", "source", "source_id", "creator", "license", "license_url",
             "orig_url", "width", "height", "sha256", "query", "collected_utc"]

CATEGORIES = ["interiors", "pairs", "materials", "collections", "nature_glass"]

# category -> search queries. Edit freely; these target the L6 gaps David listed.
CATEGORY_QUERIES = {
    "interiors": ["interior room", "office interior", "lobby interior", "waiting room",
                  "living room interior", "atrium interior", "hotel lobby", "classroom interior",
                  "cluttered room", "ordinary office"],                       # incl. ugly/ordinary
    "nature_glass": ["window view greenery", "office plants window", "garden through window",
                     "conservatory interior", "sunroom plants", "biophilic office greenery"],
    "materials": ["wood interior", "stone wall interior", "timber interior", "concrete interior",
                  "brick interior wall", "marble interior"],
    "collections": ["bookshelf interior", "library reading room", "shelves ornaments",
                    "gallery wall interior", "cabinet of curiosities", "collection display shelf"],
    "pairs": ["interior room"],   # collect candidates; PAIR them by hand with --make-pair
    # extra niche positives (collected into interiors/ unless you move them):
    "_water": ["indoor water feature", "lobby fountain", "interior reflecting pool"],
    "_fire": ["fireplace living room", "hearth interior", "lounge fireplace"],
    "_sky": ["atrium skylight", "sunlit interior", "bright daylight atrium"],
}


def slug(s: str, n: int = 40) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return s[:n] or "img"


def load_seen() -> set:
    seen = set()
    if PROVENANCE.exists():
        for r in csv.DictReader(PROVENANCE.open()):
            seen.add(f"{r['source']}:{r['source_id']}")
    return seen


def load_hashes() -> set:
    h = set()
    if PROVENANCE.exists():
        for r in csv.DictReader(PROVENANCE.open()):
            if r.get("sha256"):
                h.add(r["sha256"])
    return h


# ----------------------------------------------------------------- source adapters
def search_openverse(query, limit):
    """Keyless (optional OPENVERSE_TOKEN). Returns normalized candidate dicts."""
    hdr = {}
    tok = os.environ.get("OPENVERSE_TOKEN")
    if tok:
        hdr["Authorization"] = f"Bearer {tok}"
    out, page = [], 1
    while len(out) < limit and page <= 5:
        r = requests.get("https://api.openverse.org/v1/images/",
                         params={"q": query, "license_type": "commercial,modification",
                                 "size": "large", "page_size": min(20, limit), "page": page},
                         headers=hdr, timeout=30)
        if r.status_code != 200:
            print(f"    openverse HTTP {r.status_code}: {r.text[:120]}"); break
        for it in r.json().get("results", []):
            out.append({"source": "openverse", "id": str(it.get("id")),
                        "url": it.get("url"), "w": it.get("width"), "h": it.get("height"),
                        "creator": it.get("creator") or "unknown",
                        "license": f"{it.get('license','?').upper()} {it.get('license_version','')}".strip(),
                        "license_url": it.get("license_url") or "",
                        "orig_url": it.get("foreign_landing_url") or it.get("url"),
                        "download_location": None})
        page += 1
        time.sleep(0.5)
    return out[:limit]


def search_unsplash(query, limit):
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        sys.exit("Set UNSPLASH_ACCESS_KEY (register a free app at unsplash.com/developers).")
    out, page = [], 1
    while len(out) < limit and page <= 10:
        r = requests.get("https://api.unsplash.com/search/photos",
                         params={"query": query, "per_page": 30, "page": page,
                                 "orientation": "landscape", "content_filter": "high"},
                         headers={"Authorization": f"Client-ID {key}"}, timeout=30)
        if r.status_code != 200:
            print(f"    unsplash HTTP {r.status_code}: {r.text[:120]}"); break
        res = r.json().get("results", [])
        if not res:
            break
        for it in res:
            out.append({"source": "unsplash", "id": it["id"],
                        "url": it["urls"].get("raw") or it["urls"].get("full"),
                        "w": it.get("width"), "h": it.get("height"),
                        "creator": (it.get("user") or {}).get("name", "unknown"),
                        "license": "Unsplash License",
                        "license_url": "https://unsplash.com/license",
                        "orig_url": (it.get("links") or {}).get("html", ""),
                        "download_location": (it.get("links") or {}).get("download_location")})
        page += 1
        time.sleep(0.5)
    return out[:limit]


def search_pexels(query, limit):
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        sys.exit("Set PEXELS_API_KEY (register free at pexels.com/api).")
    out, page = [], 1
    while len(out) < limit and page <= 10:
        r = requests.get("https://api.pexels.com/v1/search",
                         params={"query": query, "per_page": 40, "page": page,
                                 "orientation": "landscape"},
                         headers={"Authorization": key}, timeout=30)
        if r.status_code != 200:
            print(f"    pexels HTTP {r.status_code}: {r.text[:120]}"); break
        photos = r.json().get("photos", [])
        if not photos:
            break
        for it in photos:
            out.append({"source": "pexels", "id": str(it["id"]),
                        "url": (it.get("src") or {}).get("original"),
                        "w": it.get("width"), "h": it.get("height"),
                        "creator": it.get("photographer", "unknown"),
                        "license": "Pexels License",
                        "license_url": "https://www.pexels.com/license/",
                        "orig_url": it.get("url", ""), "download_location": None})
        page += 1
        time.sleep(0.5)
    return out[:limit]


SEARCH = {"openverse": search_openverse, "unsplash": search_unsplash, "pexels": search_pexels}


# ----------------------------------------------------------------- collect
def collect(category, source, limit, min_px, dry, max_aspect=3.0):
    queries = CATEGORY_QUERIES.get(category)
    if not queries:
        sys.exit(f"Unknown category '{category}'. Known: {list(CATEGORY_QUERIES)}")
    dest_cat = "interiors" if category.startswith("_") else category   # niche -> interiors folder
    outdir = CORPUS / dest_cat
    if not dry:
        outdir.mkdir(parents=True, exist_ok=True)
    seen_ids, seen_hash = load_seen(), load_hashes()
    key = os.environ.get("UNSPLASH_ACCESS_KEY") if source == "unsplash" else None
    kept = 0
    per_q = max(1, limit // len(queries) + 1)
    for q in queries:
        if kept >= limit:
            break
        print(f"  [{source}] '{q}' ...")
        for c in SEARCH[source](q, per_q):
            if kept >= limit:
                break
            sid = f"{c['source']}:{c['id']}"
            if sid in seen_ids or not c.get("url"):
                continue
            # cheap pre-filter on reported dims
            if c.get("w") and c.get("h") and min(c["w"], c["h"]) < min_px:
                continue
            if dry:
                print(f"    WOULD KEEP {sid}  {c.get('w')}x{c.get('h')}  {c['license']}  by {c['creator']}")
                seen_ids.add(sid); kept += 1
                continue
            try:
                img_bytes = _download(c, key)
                im = Image.open(io.BytesIO(img_bytes))
                im = im.convert("RGB")
            except Exception as e:
                print(f"    skip {sid}: {type(e).__name__} {e}"); continue
            w, h = im.size
            if min(w, h) < min_px or max(w, h) / max(1, min(w, h)) > max_aspect:
                print(f"    drop {sid}: {w}x{h} (too small or extreme aspect)"); continue
            sha = hashlib.sha256(img_bytes).hexdigest()
            if sha in seen_hash:
                print(f"    dup   {sid} (identical bytes already have)"); continue
            name = f"{c['source']}_{slug(c['id'],24)}_{slug(q,24)}.png"
            path = outdir / name
            im.save(path, "PNG")                              # native resolution, no resample
            notes = f"source={c['source']}; {c['license']}; by {c['creator']}; {c['orig_url']}"
            _append(MANIFEST, MANIFEST_COLS,
                    {"filename": f"{dest_cat}/{name}", "category": dest_cat, "pair_id": "",
                     "pair_expected_better": "unknown", "notes": notes})
            _append(PROVENANCE, PROV_COLS,
                    {"filename": f"{dest_cat}/{name}", "source": c["source"], "source_id": c["id"],
                     "creator": c["creator"], "license": c["license"], "license_url": c["license_url"],
                     "orig_url": c["orig_url"], "width": w, "height": h, "sha256": sha,
                     "query": q, "collected_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")})
            seen_ids.add(sid); seen_hash.add(sha); kept += 1
            print(f"    + {dest_cat}/{name}  {w}x{h}")
            time.sleep(0.4)
    print(f"  -> kept {kept} for category '{category}' (folder {dest_cat}/)")
    return kept


def _download(c, unsplash_key):
    # Unsplash API guideline: ping download_location so the photographer gets a download credit.
    if c["source"] == "unsplash" and c.get("download_location") and unsplash_key:
        try:
            requests.get(c["download_location"], headers={"Authorization": f"Client-ID {unsplash_key}"},
                         timeout=15)
        except Exception:
            pass
    r = requests.get(c["url"], timeout=60)
    r.raise_for_status()
    return r.content


def _append(path, cols, row):
    new = not path.exists()
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        w.writerow(row)


def make_pair(a_rel, b_rel, better, note):
    """Register a curated A/B pair: both files must already sit under corpus_L6/. Adds/updates their
    manifest rows with a shared pair_id and the human 'expected better' verdict (A|B|unknown)."""
    assert better in ("A", "B", "unknown"), "expected_better must be A, B, or unknown"
    a, b = CORPUS / a_rel, CORPUS / b_rel
    for p in (a, b):
        if not p.exists():
            sys.exit(f"missing {p} — place both images under corpus_L6/ first")
    pid = "pair_" + hashlib.sha1(f"{a_rel}|{b_rel}".encode()).hexdigest()[:8]
    rows, seen = [], set()
    if MANIFEST.exists():
        rows = list(csv.DictReader(MANIFEST.open()))
    def upsert(rel, side):
        for r in rows:
            if r["filename"] == rel:
                r["pair_id"] = pid; r["category"] = "pairs"
                r["pair_expected_better"] = better if side == "A" else better
                r["notes"] = (r.get("notes", "") + f" | A/B {side} of {pid}: {note}").strip(" |")
                seen.add(rel); return
        rows.append({"filename": rel, "category": "pairs", "pair_id": pid,
                     "pair_expected_better": better, "notes": f"A/B {side} of {pid}: {note}"})
    upsert(a_rel, "A"); upsert(b_rel, "B")
    with MANIFEST.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLS); w.writeheader(); w.writerows(rows)
    print(f"registered pair {pid}: A={a_rel} B={b_rel} expected_better={better}")


def main():
    ap = argparse.ArgumentParser(description="Collect licence-clean images into the L6 corpus.")
    ap.add_argument("--category", choices=list(CATEGORY_QUERIES))
    ap.add_argument("--all", action="store_true", help="run every category")
    ap.add_argument("--source", choices=list(SEARCH), default="openverse")
    ap.add_argument("--limit", type=int, default=20, help="images per category")
    ap.add_argument("--min-px", type=int, default=1024, help="min short-side pixels (anti-upscale)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--make-pair", nargs=4, metavar=("A_REL", "B_REL", "BETTER", "NOTE"),
                    help="register an A/B pair (paths relative to corpus_L6/)")
    a = ap.parse_args()
    if a.make_pair:
        return make_pair(*a.make_pair)
    if not CORPUS.exists() and not a.dry_run:
        sys.exit(f"{CORPUS} not found — run from the repo root.")
    cats = list(CATEGORY_QUERIES) if a.all else ([a.category] if a.category else None)
    if not cats:
        ap.error("give --category X, --all, or --make-pair ...")
    total = 0
    for c in cats:
        print(f"== category {c} ==")
        total += collect(c, a.source, a.limit, a.min_px, a.dry_run)
    print(f"\nDONE. {'(dry-run) ' if a.dry_run else ''}collected {total} images.")
    if not a.dry_run:
        print("Review them, then commit ONLY the manifest:  git add corpus_L6/manifest.csv && git commit")


if __name__ == "__main__":
    main()
