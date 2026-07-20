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

ACADEMIC SOURCES (label/folder based; research licence — keep on your own storage)
  mit_indoor  MIT Indoor67 via Kaggle (--kaggle-dataset, default itsahmad/indoor-scenes-cvpr-2019).
              Needs the Kaggle CLI + ~/.kaggle/kaggle.json. Original-res photos; its 67 categories map
              onto the niches (greenhouse/florist/nursery->nature_glass, library/bookstore/museum->
              collections, winecellar->materials, the rest->interiors). Best academic fit.
  from-dir    Walk an already-extracted dataset tree (--from-dir ROOT), category = parent folder.
              Use for the MIT tar (indoorCVPR_09/Images/<cat>/) or any ImageNet-style layout.
  hf          Stream a Hugging Face dataset (--hf-preset places365|ade20k, or --hf-dataset ID +
              --hf-split/--hf-image-field/--hf-label-field). `pip3 install datasets`; gated sets need
              `huggingface-cli login`. NOTE: Places365 HF mirrors are 256px (raise/lower --min-px
              knowingly); ADE20K has no per-image scene label so everything routes to --default-cat.

  ACADEMIC EXAMPLES
    pip3 install datasets kaggle --break-system-packages
    python3 scripts/collect_corpus_L6.py --source mit_indoor --limit 120           # niches auto-routed
    python3 scripts/collect_corpus_L6.py --source from-dir --from-dir ~/indoorCVPR_09/Images --limit 80
    python3 scripts/collect_corpus_L6.py --source hf --hf-preset places365 --min-px 256 --limit 100

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

STORAGE — Google Drive (recommended; payloads off local disk + git)
  The PNG payloads should live on Drive like the Structured3D offload; manifest.csv (git-tracked) and
  _provenance.csv (sidecar) stay LOCAL as the index. Uses rclone with the same remote pattern as
  cnfa_external_collect/collect_datasets_to_gdrive.sh.
    rclone config                        # once: new remote 'gdrive' -> type drive
    # collect straight to Drive (keep a local working copy too):
    python3 scripts/collect_corpus_L6.py --source mit_indoor --limit 120 --gdrive gdrive:corpus_L6
    # collect to Drive and free local disk (keep only manifest/provenance locally):
    python3 scripts/collect_corpus_L6.py --source unsplash --category interiors --limit 40 \
            --gdrive gdrive:corpus_L6 --offload
    # before an L6 calibration pass, pull the payloads back locally:
    python3 scripts/collect_corpus_L6.py --rehydrate gdrive:corpus_L6
  (--gdrive with no value defaults to gdrive:corpus_L6. Each PNG's Drive path is recorded in
  _provenance.csv/gdrive_path and the manifest notes.)

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
             "orig_url", "width", "height", "sha256", "query", "collected_utc", "gdrive_path"]

# Storage: PNG payloads should live on Google Drive (like the Structured3D offload), not bloat local
# disk or git. manifest.csv (git-tracked) + _provenance.csv (sidecar) stay LOCAL as the index. Set
# via --gdrive; uploaded through rclone using the same remote as collect_datasets_to_gdrive.sh.
GDRIVE_REMOTE = None        # e.g. "gdrive:corpus_L6"; None = local-only
OFFLOAD = False             # delete the local PNG after a verified Drive upload (keep disk ~0)

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


# ================================================================= ACADEMIC datasets
# Academic scene sets carry their OWN scene-category labels; we map the relevant ones onto the
# corpus_L6 folders and route the rest of the interior labels to interiors/. Everything not in a
# keep-map is skipped. All are research-licence — keep them on your own storage (as with Structured3D).
#
# MIT Indoor67 (Kaggle: itsahmad/indoor-scenes-cvpr-2019 -> indoorCVPR_09/Images/<category>/*.jpg,
# or the MIT tar). Original resolution real photos; its 67 categories cover the niches directly.
MIT_INDOOR_KEEP = {
    # biophilia / nature-through-glazing
    "greenhouse": "nature_glass", "florist": "nature_glass", "nursery": "nature_glass",
    # material-forward
    "winecellar": "materials",
    # collections / ornament / shelving
    "library": "collections", "bookstore": "collections", "museum": "collections",
    "toystore": "collections", "jewelleryshop": "collections", "videostore": "collections",
    "clothingstore": "collections", "shoeshop": "collections", "grocerystore": "collections",
    "deli": "collections", "bakery": "collections",
    # general + ordinary/ugly interiors -> interiors/
    "livingroom": "interiors", "lobby": "interiors", "waitingroom": "interiors", "office": "interiors",
    "meeting_room": "interiors", "dining_room": "interiors", "classroom": "interiors",
    "bedroom": "interiors", "kitchen": "interiors", "corridor": "interiors", "bathroom": "interiors",
    "hospitalroom": "interiors", "restaurant": "interiors", "auditorium": "interiors",
    "concert_hall": "interiors", "church_inside": "interiors", "mall": "interiors", "gym": "interiors",
    "computerroom": "interiors", "poolinside": "interiors", "pantry": "interiors", "closet": "interiors",
    "garage": "interiors", "locker_room": "interiors", "prisoncell": "interiors",
    "stairscase": "interiors", "dentaloffice": "interiors", "operating_room": "interiors",
    "artstudio": "interiors", "gameroom": "interiors", "children_room": "interiors",
    "laundromat": "interiors", "kindergarden": "interiors", "buffet": "interiors", "bar": "interiors",
}
# Places365: 365 categories; keep the interior ones. (256px mirrors will be dropped by --min-px;
# use --min-px 256 knowingly, or pull the high-res Places365-large tars.)
PLACES365_KEEP = {c: "interiors" for c in [
    "living_room", "waiting_room", "lobby", "atrium/public", "reception", "office", "office_cubicles",
    "conference_room", "hospital_room", "art_gallery", "library/indoor", "bookstore", "restaurant",
    "dining_room", "bedroom", "kitchen", "corridor", "classroom", "auditorium", "museum/indoor",
    "art_studio", "childs_room", "computer_room", "recreation_room", "television_room", "home_office",
    "hotel_room", "dorm_room", "physics_laboratory", "server_room", "clean_room"]}
PLACES365_KEEP.update({"greenhouse/indoor": "nature_glass", "conservatory": "nature_glass",
                       "botanical_garden": "nature_glass"})

# HF presets for `--source hf` (streamed; filter by the dataset's own label feature).
HF_PRESETS = {
    "places365": {"hf": "torch-uncertainty/Places365", "split": "train", "image_field": "image",
                  "label_field": "label", "keep": PLACES365_KEEP, "default_cat": None},
    "ade20k":    {"hf": "zhoubolei/scene_parse_150", "split": "train", "image_field": "image",
                  "label_field": None, "keep": None, "default_cat": "interiors"},  # no per-image scene
}


def _pil_from(x):
    """Accept a PIL image, a datasets Image dict {bytes|path}, or a filesystem path -> RGB PIL."""
    from PIL import Image as _I
    if hasattr(x, "convert"):
        return x.convert("RGB")
    if isinstance(x, dict):
        if x.get("bytes"):
            return _I.open(io.BytesIO(x["bytes"])).convert("RGB")
        if x.get("path"):
            return _I.open(x["path"]).convert("RGB")
    if isinstance(x, (str, Path)):
        return _I.open(x).convert("RGB")
    raise ValueError("unrecognized image field")


def walk_dir(root, keep_map, default_cat, source_tag, limit):
    """Yield (meta, PIL) from an extracted dataset tree <root>/**/<category>/<file>. The category is
    the immediate parent folder (MIT Indoor67, ImageNet-style, Kaggle unzips). keep_map routes
    category->corpus folder; unknown categories go to default_cat (or are skipped if None)."""
    root = Path(root)
    exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    n = 0
    for p in sorted(root.rglob("*")):
        if n >= limit:
            break
        if p.suffix.lower() not in exts or not p.is_file():
            continue
        cat_raw = p.parent.name
        corpus_cat = keep_map.get(_norm(cat_raw), default_cat)
        if corpus_cat is None:
            continue
        try:
            im = _pil_from(p)
        except Exception as e:
            print(f"    skip {p.name}: {e}"); continue
        meta = {"source": source_tag, "id": f"{cat_raw}_{p.stem}", "creator": "dataset",
                "license": f"{source_tag} research licence", "license_url": "",
                "orig_url": str(p), "_corpus_cat": corpus_cat, "_tag": cat_raw}
        yield meta, im
        n += 1


def _norm(s):
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def stream_hf(name, split, image_field, label_field, keep_map, default_cat, source_tag, limit):
    """Yield (meta, PIL) from a Hugging Face dataset in streaming mode, filtered by its label feature.
    Gated datasets need `huggingface-cli login` first. If label_field is None, no scene filter is
    applied (everything -> default_cat)."""
    try:
        from datasets import load_dataset
    except ImportError:
        sys.exit("pip3 install datasets --break-system-packages   (needed for --source hf)")
    ds = load_dataset(name, split=split, streaming=True)
    int2str = None
    try:
        feat = ds.features.get(label_field) if label_field else None
        if feat is not None and hasattr(feat, "int2str"):
            int2str = feat.int2str
    except Exception:
        pass
    n = 0
    for ex in ds:
        if n >= limit:
            break
        lab_name = None
        if label_field is not None and label_field in ex:
            lv = ex[label_field]
            lab_name = int2str(lv) if (int2str and isinstance(lv, int)) else str(lv)
        corpus_cat = default_cat if label_field is None else (keep_map or {}).get(_norm(lab_name))
        if corpus_cat is None:
            continue
        try:
            im = _pil_from(ex[image_field])
        except Exception as e:
            print(f"    skip hf#{n}: {e}"); continue
        meta = {"source": source_tag, "id": f"{lab_name or 'img'}_{n}", "creator": "dataset",
                "license": f"{name} research licence", "license_url": f"https://huggingface.co/datasets/{name}",
                "orig_url": f"hf://{name}", "_corpus_cat": corpus_cat, "_tag": lab_name or split}
        yield meta, im
        n += 1


def check_rclone(remote):
    """Verify rclone exists and the remote is configured before collecting (fail early, clearly)."""
    import subprocess
    name = remote.split(":", 1)[0]
    try:
        remotes = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        sys.exit("rclone not found. brew install rclone  (or curl https://rclone.org/install.sh | sudo bash)")
    except subprocess.CalledProcessError as e:
        sys.exit(f"rclone error: {e}")
    if f"{name}:" not in remotes:
        sys.exit(f"rclone remote '{name}:' not configured. Run: rclone config  "
                 f"(new remote -> name: {name} -> type: drive). Configured: {remotes.strip() or '(none)'}")


def gdrive_upload(local_path, remote, category, name):
    """rclone copy the PNG to <remote>/<category>/<name>. Returns the Drive path (raises on failure)."""
    import subprocess
    dest_dir = f"{remote.rstrip('/')}/{category}"
    subprocess.run(["rclone", "copyto", str(local_path), f"{dest_dir}/{name}"], check=True)
    return f"{dest_dir}/{name}"


def rehydrate(remote, dest=None):
    """Pull the corpus PNGs back from Drive for a local calibration pass: rclone copy remote -> dest."""
    import subprocess
    dest = dest or str(CORPUS)
    check_rclone(remote)
    print(f"rclone copy {remote} -> {dest}")
    subprocess.run(["rclone", "copy", remote, dest, "--progress"], check=True)
    print("rehydrated. (manifest.csv is the index; payloads now local for calibration)")


def _save_image(im, meta, dest_cat, tag, min_px, max_aspect, seen_ids, seen_hash, dry):
    """The ONE save path shared by every source: dims/aspect filter, de-dup on native pixels, save
    canonical PNG at native resolution, optionally mirror to Google Drive (and offload the local copy),
    append manifest (repo schema) + provenance. Returns kept?"""
    sid = f"{meta['source']}:{meta['id']}"
    if sid in seen_ids:
        return False
    im = im.convert("RGB")
    w, h = im.size
    if min(w, h) < min_px or max(w, h) / max(1, min(w, h)) > max_aspect:
        print(f"    drop {sid}: {w}x{h} (too small or extreme aspect)"); return False
    sha = hashlib.sha256(im.tobytes()).hexdigest()          # native-pixel hash -> cross-source de-dup
    if sha in seen_hash:
        print(f"    dup   {sid}"); return False
    seen_ids.add(sid); seen_hash.add(sha)
    if dry:
        tgt = f" -> {GDRIVE_REMOTE}/{dest_cat}/" if GDRIVE_REMOTE else f" -> {dest_cat}/ (local)"
        print(f"    WOULD KEEP {sid}{tgt}  {w}x{h}  {meta['license']}"); return True
    outdir = CORPUS / dest_cat; outdir.mkdir(parents=True, exist_ok=True)
    name = f"{meta['source']}_{slug(meta['id'], 28)}_{slug(tag, 20)}.png"
    local = outdir / name
    im.save(local, "PNG")                                   # native resolution, no resample
    gdrive_path = ""
    if GDRIVE_REMOTE:
        try:
            gdrive_path = gdrive_upload(local, GDRIVE_REMOTE, dest_cat, name)
            if OFFLOAD:
                local.unlink()                              # verified on Drive -> free local disk
        except Exception as e:
            print(f"    UPLOAD FAILED {sid}: {e} (kept local copy)")
    notes = f"source={meta['source']}; {meta['license']}; by {meta['creator']}; {meta['orig_url']}"
    if gdrive_path:
        notes += f"; stored={gdrive_path}" + ("; local_offloaded" if OFFLOAD else "")
    _append(MANIFEST, MANIFEST_COLS,
            {"filename": f"{dest_cat}/{name}", "category": dest_cat, "pair_id": "",
             "pair_expected_better": "unknown", "notes": notes})
    _append(PROVENANCE, PROV_COLS,
            {"filename": f"{dest_cat}/{name}", "source": meta["source"], "source_id": meta["id"],
             "creator": meta["creator"], "license": meta["license"], "license_url": meta["license_url"],
             "orig_url": meta["orig_url"], "width": w, "height": h, "sha256": sha, "query": tag,
             "collected_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
             "gdrive_path": gdrive_path})
    where = gdrive_path if gdrive_path else f"{dest_cat}/{name}"
    print(f"    + {where}  {w}x{h}" + ("  [offloaded]" if (gdrive_path and OFFLOAD) else ""))
    return True


def collect_from_examples(gen, limit, min_px, dry, max_aspect=3.0):
    """Consume a (meta, PIL) generator (academic sources) through the shared save path."""
    seen_ids, seen_hash = load_seen(), load_hashes()
    kept = 0
    for meta, im in gen:
        if kept >= limit:
            break
        if _save_image(im, meta, meta["_corpus_cat"], meta.get("_tag", ""), min_px, max_aspect,
                       seen_ids, seen_hash, dry):
            kept += 1
    print(f"  -> kept {kept}")
    return kept


def kaggle_download(dataset, cache="~/.cache/l6_kaggle"):
    """Download+unzip a Kaggle dataset via the kaggle CLI (needs ~/.kaggle/kaggle.json). Returns dir."""
    import subprocess, zipfile
    d = Path(os.path.expanduser(cache)) / slug(dataset)
    d.mkdir(parents=True, exist_ok=True)
    if not any(d.iterdir()):
        print(f"  kaggle download {dataset} -> {d} ...")
        subprocess.run(["kaggle", "datasets", "download", "-d", dataset, "-p", str(d)], check=True)
        for z in d.glob("*.zip"):
            with zipfile.ZipFile(z) as zf:
                zf.extractall(d)
    return d


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
            if c.get("w") and c.get("h") and max(c["w"], c["h"]) / max(1, min(c["w"], c["h"])) > max_aspect:
                continue
            try:
                img_bytes = _download(c, key) if not dry else None
                im = Image.open(io.BytesIO(img_bytes)) if img_bytes is not None else None
            except Exception as e:
                print(f"    skip {sid}: {type(e).__name__} {e}"); continue
            if dry:
                print(f"    WOULD KEEP {sid} -> {dest_cat}/  {c.get('w')}x{c.get('h')}  "
                      f"{c['license']}  by {c['creator']}")
                seen_ids.add(sid); kept += 1
                continue
            meta = {"source": c["source"], "id": c["id"], "creator": c["creator"],
                    "license": c["license"], "license_url": c["license_url"], "orig_url": c["orig_url"]}
            if _save_image(im, meta, dest_cat, q, min_px, max_aspect, seen_ids, seen_hash, dry=False):
                kept += 1
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
    existing = None
    if path.exists():
        with path.open() as f:
            try:
                existing = next(csv.reader(f))
            except StopIteration:
                existing = None
    use = existing or cols                         # adapt to an older header if one is already there
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=use, extrasaction="ignore")
        if existing is None:
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


def _apply_manip(im, manip):
    """Degrade a base interior along ONE well-being axis -> a controlled A/B variant. The base is the
    ground-truth 'better' (expected_better='A'). Returns (variant, default_expected, operator, desc).
    Photometric only: valid for the LIGHT / colour / affect operators, NOT geometry/biophilia (same
    room, one variable changed — a cleaner signal than two different rooms for those operators)."""
    from PIL import ImageEnhance, ImageFilter, ImageDraw, ImageChops
    m = manip.lower()
    if m == "daylight":                       # dim -> less daylight access
        v = ImageEnhance.Brightness(im).enhance(0.5)
        return v, "A", "C10 daylight_proximity / C22 circadian_contrast", "brightness x0.5 (dimmer)"
    if m == "glare":                          # add a blown-out hotspot -> glare cost
        v = im.copy(); w, h = v.size
        blob = Image.new("L", (w, h), 0); d = ImageDraw.Draw(blob)
        r = int(min(w, h) * 0.18); cx, cy = int(w * 0.72), int(h * 0.28)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
        blob = blob.filter(ImageFilter.GaussianBlur(r * 0.6))
        white = Image.new("RGB", (w, h), (255, 255, 255))
        v = Image.composite(white, v, blob)
        v = ImageChops.screen(v, Image.merge("RGB", [blob] * 3))
        return v, "A", "glare-risk", "added specular hotspot (upper-right)"
    if m == "warmth":                         # cold blue cast -> loses evening warmth
        rr, gg, bb = im.split()
        rr = rr.point(lambda p: int(p * 0.78)); bb = bb.point(lambda p: min(255, int(p * 1.25)))
        v = Image.merge("RGB", (rr, gg, bb))
        return v, "A", "evening_ambience / temperature_mismatch", "cool colour cast (R x0.78, B x1.25)"
    if m == "contrast":                       # harsh contrast + crushed shadows
        v = ImageEnhance.Contrast(im).enhance(1.8)
        v = ImageEnhance.Brightness(v).enhance(0.85)
        return v, "A", "processing_load / fluency", "contrast x1.8, brightness x0.85 (harsh)"
    sys.exit(f"unknown manip '{manip}'. Choose: daylight | glare | warmth | contrast")


def gen_ab(base_rel, manip, expected=None, note=""):
    """Make a controlled photometric A/B pair from a base image already under corpus_L6/: writes
    pairs/<pid>_A_base.png and pairs/<pid>_B_<manip>.png, registers them with the manipulation's known
    'expected better', and (if --gdrive is set) mirrors both to Drive."""
    from PIL import Image as _I
    base = CORPUS / base_rel
    if not base.exists():
        sys.exit(f"base not found: {base} (path relative to corpus_L6/)")
    im = _I.open(base).convert("RGB")
    variant, dexp, op, desc = _apply_manip(im, manip)
    pid = "gab_" + hashlib.sha1(f"{base_rel}|{manip}".encode()).hexdigest()[:8]
    (CORPUS / "pairs").mkdir(parents=True, exist_ok=True)
    a_rel, b_rel = f"pairs/{pid}_A_base.png", f"pairs/{pid}_B_{manip}.png"
    im.save(CORPUS / a_rel, "PNG"); variant.save(CORPUS / b_rel, "PNG")
    exp = expected or dexp
    full = (f"controlled photometric A/B from {base_rel}; manip={manip} ({desc}); targets {op}. "
            f"{note}").strip()
    make_pair(a_rel, b_rel, exp, full)
    if GDRIVE_REMOTE:
        try:
            for rel in (a_rel, b_rel):
                gdrive_upload(CORPUS / rel, GDRIVE_REMOTE, "pairs", Path(rel).name)
            print(f"  mirrored pair to {GDRIVE_REMOTE}/pairs/")
        except Exception as e:
            print(f"  pair upload failed: {e} (kept local)")
    print(f"generated A/B {pid}: A=base B={manip}  expected_better={exp}  (targets {op})")


# target corpus composition (DK-1 plan: ~120 interiors + 80 A/B pairs + niches). Edit to taste.
TARGETS = {"interiors": 116, "nature_glass": 20, "materials": 15, "collections": 15}
PAIR_TARGET = 80
AB_MANIPS = ["daylight", "glare", "warmth", "contrast"]


def gen_ab_batch(from_cat, n, manips):
    """Generate n controlled A/B pairs from the singleton images already in corpus_L6/<from_cat>/,
    cycling the manipulation list for variety. Idempotent per (base, manip): re-running overwrites
    the same pair id rather than duplicating."""
    bases = sorted(p for p in (CORPUS / from_cat).glob("*.png") if "_A_base" not in p.name)
    if not bases:
        sys.exit(f"no base images in corpus_L6/{from_cat}/ — collect some interiors first")
    made = 0
    for i, base in enumerate(bases):
        if made >= n:
            break
        manip = manips[i % len(manips)]
        gen_ab(f"{from_cat}/{base.name}", manip)
        made += 1
    print(f"\ngenerated {made} A/B pairs from {from_cat}/ (targets: {', '.join(manips)})")


def corpus_status():
    """Report corpus composition vs targets from the manifest + provenance — the 'are we there yet'."""
    from collections import Counter, defaultdict
    if not MANIFEST.exists():
        print("no manifest yet — nothing collected."); return
    rows = list(csv.DictReader(MANIFEST.open()))
    prov = list(csv.DictReader(PROVENANCE.open())) if PROVENANCE.exists() else []
    singles = [r for r in rows if not r["pair_id"]]
    cat = Counter(r["category"] for r in singles)
    pairs = defaultdict(list)
    for r in rows:
        if r["pair_id"]:
            pairs[r["pair_id"]].append(r)
    complete = [p for p, rs in pairs.items() if len(rs) == 2]
    verdicted = [p for p in complete if any(rs["pair_expected_better"] in ("A", "B") for rs in pairs[p])]

    def bar(have, want, w=24):
        f = min(1.0, have / want) if want else 1.0
        return "[" + "#" * int(f * w) + "-" * (w - int(f * w)) + f"] {have}/{want} ({f*100:.0f}%)"

    print("\n==================== L6 CORPUS STATUS ====================")
    print("Singletons by category:")
    for c, want in TARGETS.items():
        print(f"  {c:14s} {bar(cat.get(c, 0), want)}")
    other = {c: n for c, n in cat.items() if c not in TARGETS}
    if other:
        print(f"  (other: {other})")
    print(f"\nA/B pairs:       {bar(len(complete), PAIR_TARGET)}  "
          f"({len(verdicted)} with an expected-better verdict)")
    total_imgs = sum(cat.values()) + sum(len(rs) for rs in pairs.values())
    print(f"\nTotal images:    {total_imgs}   (manifest rows: {len(rows)})")
    if prov:
        src = Counter(r["source"] for r in prov)
        lic = Counter((r["license"].split(";")[0].split(" by ")[0]).strip() for r in prov)
        on_drive = sum(1 for r in prov if r.get("gdrive_path"))
        dims = [(int(r["width"]), int(r["height"])) for r in prov if r.get("width")]
        print(f"Sources:         {dict(src)}")
        print(f"Licences:        {dict(lic)}")
        print(f"On Google Drive: {on_drive}/{len(prov)} provenance rows")
        if dims:
            shorts = sorted(min(w, h) for w, h in dims)
            print(f"Short-side px:   min {shorts[0]}, median {shorts[len(shorts)//2]}, max {shorts[-1]}")
    # gap callouts
    gaps = [f"{want - cat.get(c, 0)} more {c}" for c, want in TARGETS.items() if cat.get(c, 0) < want]
    if len(complete) < PAIR_TARGET:
        gaps.append(f"{PAIR_TARGET - len(complete)} more A/B pairs")
    print("\nStill needed:    " + ("; ".join(gaps) if gaps else "targets met ✓"))
    print("==========================================================\n")


def seed_all(gdrive, per_web=12):
    """One-shot: run the recommended collection plan to Drive. Runs on YOUR machine (live network +
    keys). Academic MIT Indoor67 for volume+niches, Unsplash for high-res niche shots, then batch A/B
    from the collected interiors. Adjust budgets inline; safe to re-run (idempotent per source id)."""
    global GDRIVE_REMOTE
    if gdrive:
        GDRIVE_REMOTE = gdrive; check_rclone(GDRIVE_REMOTE)
    print("SEED-ALL plan -> filling every category, then A/B pairs.\n")
    # 1) MIT Indoor67 (volume + niches auto-routed) — needs Kaggle creds
    try:
        root = kaggle_download("itsahmad/indoor-scenes-cvpr-2019")
        collect_from_examples(walk_dir(root, MIT_INDOOR_KEEP, "interiors", "mit_indoor67", 600),
                              limit=200, min_px=1024, dry=False)
    except Exception as e:
        print(f"  [skip mit_indoor: {e}]")
    # 2) Unsplash high-res niche top-ups (needs UNSPLASH_ACCESS_KEY)
    if os.environ.get("UNSPLASH_ACCESS_KEY"):
        for c in ["nature_glass", "materials", "collections", "_water", "_fire", "_sky"]:
            try:
                collect(c, "unsplash", per_web, 1024, dry=False)
            except SystemExit:
                pass
    else:
        print("  [skip unsplash top-ups: set UNSPLASH_ACCESS_KEY]")
    # 3) A/B pairs from collected interiors
    try:
        gen_ab_batch("interiors", PAIR_TARGET, AB_MANIPS)
    except SystemExit as e:
        print(f"  [A/B batch: {e}]")
    print("\nSEED-ALL done. Run --status to see composition.")


def main():
    global GDRIVE_REMOTE, OFFLOAD
    ap = argparse.ArgumentParser(description="Collect licence-clean images into the L6 corpus.")
    web_sources = list(SEARCH)                               # openverse/unsplash/pexels (query-based)
    academic = ["mit_indoor", "hf", "from-dir"]              # label/folder-based
    ap.add_argument("--category", choices=list(CATEGORY_QUERIES))
    ap.add_argument("--all", action="store_true", help="run every web category")
    ap.add_argument("--source", choices=web_sources + academic, default="openverse")
    ap.add_argument("--limit", type=int, default=20, help="images (per web category, or total for academic)")
    ap.add_argument("--min-px", type=int, default=1024,
                    help="min short-side pixels (anti-upscale; use 256 knowingly for Places365-256)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--make-pair", nargs=4, metavar=("A_REL", "B_REL", "BETTER", "NOTE"),
                    help="register an A/B pair (paths relative to corpus_L6/)")
    ap.add_argument("--gen-ab", nargs=2, metavar=("BASE_REL", "MANIP"),
                    help="generate a controlled photometric A/B pair from a base image; "
                         "MANIP = daylight | glare | warmth | contrast")
    ap.add_argument("--ab-expected", choices=["A", "B", "unknown"], default=None,
                    help="override the manipulation's default expected-better (default A = base)")
    ap.add_argument("--ab-note", default="", help="extra note for the generated pair")
    ap.add_argument("--gen-ab-batch", type=int, metavar="N",
                    help="generate N A/B pairs from collected interiors (cycles manipulations)")
    ap.add_argument("--ab-from", default="interiors", help="category folder to draw A/B bases from")
    ap.add_argument("--ab-manips", default=",".join(AB_MANIPS),
                    help="comma list of manipulations to cycle for --gen-ab-batch")
    ap.add_argument("--status", action="store_true", help="report corpus composition vs targets, then exit")
    ap.add_argument("--seed-all", action="store_true",
                    help="one-shot: run the full recommended collection plan (academic+web+A/B)")
    # storage: mirror payloads to Google Drive (manifest + provenance stay local as the index)
    ap.add_argument("--gdrive", nargs="?", const="gdrive:corpus_L6", default=None,
                    help="mirror each PNG to this rclone remote (default gdrive:corpus_L6 if bare)")
    ap.add_argument("--offload", action="store_true",
                    help="delete the local PNG after a verified Drive upload (needs --gdrive)")
    ap.add_argument("--rehydrate", nargs="?", const="gdrive:corpus_L6", default=None,
                    metavar="REMOTE", help="pull the corpus PNGs back from Drive into corpus_L6/, then exit")
    # academic-source options
    ap.add_argument("--kaggle-dataset", default="itsahmad/indoor-scenes-cvpr-2019",
                    help="for --source mit_indoor: Kaggle owner/name to download")
    ap.add_argument("--from-dir", help="for --source from-dir: root of an extracted dataset tree")
    ap.add_argument("--default-cat", default="interiors",
                    help="for --source from-dir/hf: corpus folder for unmapped interior labels")
    ap.add_argument("--hf-preset", choices=list(HF_PRESETS), help="for --source hf: places365 | ade20k")
    ap.add_argument("--hf-dataset", help="for --source hf: override the HF dataset id")
    ap.add_argument("--hf-split", default="train")
    ap.add_argument("--hf-image-field", default="image")
    ap.add_argument("--hf-label-field", default="label")
    a = ap.parse_args()
    if a.status:
        return corpus_status()
    if a.rehydrate:
        return rehydrate(a.rehydrate)
    if a.seed_all:
        return seed_all(a.gdrive)
    if a.make_pair:
        return make_pair(*a.make_pair)
    if a.gen_ab:
        if a.gdrive:
            GDRIVE_REMOTE = a.gdrive; check_rclone(GDRIVE_REMOTE)
        return gen_ab(a.gen_ab[0], a.gen_ab[1], a.ab_expected, a.ab_note)
    if a.gen_ab_batch:
        if a.gdrive:
            GDRIVE_REMOTE = a.gdrive; check_rclone(GDRIVE_REMOTE)
        return gen_ab_batch(a.ab_from, a.gen_ab_batch, [m.strip() for m in a.ab_manips.split(",")])
    if not CORPUS.exists() and not a.dry_run:
        sys.exit(f"{CORPUS} not found — run from the repo root.")
    if a.offload and not a.gdrive:
        ap.error("--offload needs --gdrive")
    if a.gdrive:
        GDRIVE_REMOTE, OFFLOAD = a.gdrive, a.offload
        if not a.dry_run:
            check_rclone(GDRIVE_REMOTE)
        print(f"storage: mirroring PNGs to {GDRIVE_REMOTE}" + ("  [offload local]" if OFFLOAD else ""))

    # ---- academic sources (folder/label based) -------------------------------------
    if a.source in academic:
        if a.source == "mit_indoor":
            root = kaggle_download(a.kaggle_dataset)
            gen = walk_dir(root, MIT_INDOOR_KEEP, a.default_cat, "mit_indoor67", a.limit * 4)
        elif a.source == "from-dir":
            if not a.from_dir:
                ap.error("--source from-dir needs --from-dir <path>")
            gen = walk_dir(a.from_dir, MIT_INDOOR_KEEP, a.default_cat,
                           slug(Path(a.from_dir).name), a.limit * 4)
        else:  # hf
            p = HF_PRESETS.get(a.hf_preset, {})
            name = a.hf_dataset or p.get("hf")
            if not name:
                ap.error("--source hf needs --hf-preset or --hf-dataset")
            gen = stream_hf(name, p.get("split", a.hf_split), p.get("image_field", a.hf_image_field),
                            p.get("label_field", a.hf_label_field), p.get("keep"),
                            p.get("default_cat", a.default_cat), a.hf_preset or slug(name), a.limit * 4)
        print(f"== academic source {a.source} ==")
        total = collect_from_examples(gen, a.limit, a.min_px, a.dry_run)
        print(f"\nDONE. {'(dry-run) ' if a.dry_run else ''}collected {total} images.")
        if not a.dry_run:
            print("Review, then commit ONLY the manifest:  git add corpus_L6/manifest.csv && git commit")
        return

    # ---- web sources (query based) -------------------------------------------------
    cats = list(CATEGORY_QUERIES) if a.all else ([a.category] if a.category else None)
    if not cats:
        ap.error("give --category X, --all, --make-pair ..., or an academic --source")
    total = 0
    for c in cats:
        print(f"== category {c} ==")
        total += collect(c, a.source, a.limit, a.min_px, a.dry_run)
    print(f"\nDONE. {'(dry-run) ' if a.dry_run else ''}collected {total} images.")
    if not a.dry_run:
        print("Review them, then commit ONLY the manifest:  git add corpus_L6/manifest.csv && git commit")


if __name__ == "__main__":
    main()
