#!/usr/bin/env python3
"""build_corpus_index.py — the L6 corpus RETRIEVAL INDEX (David's ask, 2026-07-21).

Function of the index (what it must let us retrieve — the spec, realised):
  Join manifest.csv (curation: category, A/B pairing, notes) with _provenance.csv (source, licence,
  resolution, sha, gdrive_path, class-query) into ONE queryable record per image, enrich it with a
  derived ARCHITECTURAL TYPE (room/space class) and a higher-level SPACE FAMILY, and emit:
    - corpus_L6/index.json   — machine-readable, one record/image + facet summaries (for programmatic
                               retrieval by the viz-attribute test harness and future score joins)
    - corpus_L6/index.html   — a self-contained browsable index (filter/search/sort; A/B pair view)
  Three audiences it serves: (1) viz-attribute testing (filter by type/resolution/licence/pairing,
  later by computed attribute scores); (2) students browsing varied stimuli by space type;
  (3) architects seeking examples meeting a spec.

  Retrieval dimensions supported: filename, space_family, arch_type (67 MIT + SUN classes),
  category (interiors/pairs/collections/niches), source, licence, short-side px bucket, on-Drive,
  A/B pair_id + expected_better, and an OPTIONAL scores.csv join (filename,<attr>=value,...) so once
  annotate has run over the corpus you can query "high clutter / low openness / biophilic" directly.

Usage:  python3 scripts/build_corpus_index.py [--corpus corpus_L6] [--scores corpus_L6/scores.csv]
Read-only on the corpus; writes only index.json + index.html.
"""
from __future__ import annotations
import argparse, csv, json, html, re
from collections import Counter, defaultdict
from pathlib import Path

# --- space family grouping: map the fine room class -> a browsable family (students/architects) ---
FAMILY = {
    "circulation": ["corridor", "stairs", "staircase", "elevator", "lobby", "hallway", "escalator"],
    "work":        ["office", "conference_room", "computerroom", "meeting", "cubicle_office",
                    "office_cubicles", "trading_floor", "reception"],
    "learning":    ["classroom", "auditorium", "lecture", "library", "bookstore", "study_space"],
    "domestic":    ["living_room", "bedroom", "kitchen", "dining_room", "bathroom", "closet",
                    "nursery", "childs_room", "home_office", "playroom"],
    "hospitality": ["restaurant", "bar", "hotel_room", "cafeteria", "coffee_shop", "fastfood_restaurant",
                    "banquet_hall", "wine_cellar", "winecellar", "pub_indoor"],
    "retail":      ["mall", "store", "shop", "clothing_store", "grocerystore", "bakery", "toystore",
                    "deli", "jewelleryshop", "shoeshop", "gameroom"],
    "civic":       ["airport_inside", "church_inside", "museum", "cathedral", "train_station",
                    "subway", "waitingroom", "courtroom", "gym", "locker_room", "prison_cell",
                    "hospitalroom", "operating_room", "concert_hall", "movietheater", "inside_bus",
                    "inside_subway", "artstudio", "greenhouse", "florist", "nursery_plants",
                    "warehouse", "garage", "laundromat", "buffet", "casino", "elevator_shaft"],
    "industrial":  ["industrial", "factory", "warehouse_indoor", "cleanroom", "server_room",
                    "manufactured_home", "workshop"],
}
FAMILY_OF = {c: fam for fam, cs in FAMILY.items() for c in cs}


def arch_type(rec_man, rec_prov) -> str:
    """Best available room/space class. Prefer provenance 'query' (the class the collector used);
    else parse the trailing '_<class>.png' token; else fall back to category."""
    if rec_prov and (rec_prov.get("query") or "").strip():
        return rec_prov["query"].strip().lower()
    fn = rec_man["filename"]
    m = re.search(r"_([a-z][a-z_]+)\.png$", fn.split("/")[-1])
    if m:
        # strip a trailing hash-ish token if the class was duplicated
        return m.group(1)
    return rec_man.get("category", "unknown")


def family_of(t: str) -> str:
    if t in FAMILY_OF:
        return FAMILY_OF[t]
    # heuristic contains-match
    for c, fam in FAMILY_OF.items():
        if c in t:
            return fam
    return "other"


def px_bucket(w, h) -> str:
    try:
        s = min(int(w), int(h))
    except Exception:
        return "unknown"
    if s >= 2048: return ">=2048"
    if s >= 1024: return "1024-2047"
    if s >= 512:  return "512-1023"
    return "<512"


def build(corpus: Path, scores_path: Path | None):
    man = list(csv.DictReader((corpus / "manifest.csv").open()))
    prov = {r["filename"]: r for r in csv.DictReader((corpus / "_provenance.csv").open())}
    scores = {}
    if scores_path and scores_path.exists():
        for r in csv.DictReader(scores_path.open()):
            scores[r["filename"]] = {k: v for k, v in r.items() if k != "filename"}

    records = []
    for m in man:
        fn = m["filename"]
        p = prov.get(fn)
        t = arch_type(m, p)
        rec = {
            "filename": fn,
            "category": m.get("category", ""),
            "space_family": family_of(t),
            "arch_type": t,
            "source": (p or {}).get("source", "curated"),
            "license": (p or {}).get("license", ""),
            "width": (p or {}).get("width", ""),
            "height": (p or {}).get("height", ""),
            "px_bucket": px_bucket((p or {}).get("width"), (p or {}).get("height")),
            "on_drive": bool((p or {}).get("gdrive_path")),
            "gdrive_path": (p or {}).get("gdrive_path", ""),
            "sha256": (p or {}).get("sha256", ""),
            "pair_id": m.get("pair_id", ""),
            "pair_expected_better": m.get("pair_expected_better", ""),
            "notes": m.get("notes", ""),
        }
        if fn in scores:
            rec["scores"] = scores[fn]
        records.append(rec)

    facets = {
        "space_family": Counter(r["space_family"] for r in records),
        "arch_type": Counter(r["arch_type"] for r in records),
        "category": Counter(r["category"] for r in records),
        "source": Counter(r["source"] for r in records),
        "px_bucket": Counter(r["px_bucket"] for r in records),
        "on_drive": Counter("on_drive" if r["on_drive"] else "not_on_drive" for r in records),
    }
    summary = {
        "n_images": len(records),
        "n_on_drive": sum(r["on_drive"] for r in records),
        "n_pairs": len(set(r["pair_id"] for r in records if r["pair_id"])),
        "has_scores": bool(scores),
        "facets": {k: dict(v.most_common()) for k, v in facets.items()},
    }
    (corpus / "index.json").write_text(json.dumps({"summary": summary, "records": records}, indent=1))
    (corpus / "index.html").write_text(render_html(records, summary))
    return summary


def render_html(records, summary) -> str:
    data = json.dumps(records)
    fam = json.dumps(dict(summary["facets"]["space_family"]))
    return HTML_TMPL.replace("__DATA__", data).replace("__SUMMARY__", json.dumps(summary)).replace("__FAM__", fam)


HTML_TMPL = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>L6 Corpus Index</title>
<style>
:root{--bg:#0f1115;--panel:#171a21;--ink:#eef1f6;--muted:#9aa4b2;--line:#262b34;--accent:#5b8cff;--chip:#1f2530;--good:#3fb68b}
@media(prefers-color-scheme:light){:root{--bg:#f6f7f9;--panel:#fff;--ink:#141821;--muted:#5b6472;--line:#e4e8ee;--chip:#eef1f6}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1300px;margin:0 auto;padding:18px}
h1{font-size:16px;margin:0 0 4px}.muted{color:var(--muted)}
.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:12px 0;padding:12px;background:var(--panel);border:1px solid var(--line);border-radius:12px}
select,input{background:var(--chip);border:1px solid var(--line);color:var(--ink);border-radius:8px;padding:7px 9px;font:inherit}
.pill{font-size:11px;color:var(--muted);background:var(--chip);border:1px solid var(--line);border-radius:999px;padding:3px 9px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px;margin-top:14px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.card .thumb{aspect-ratio:4/3;background:#0b0d11 center/cover;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:11px;text-align:center;padding:6px}
.card .meta{padding:8px 10px;font-size:12px}
.card .t{font-weight:600}.card .s{color:var(--muted)}
.badge{display:inline-block;font-size:10px;padding:1px 6px;border-radius:999px;border:1px solid var(--line);margin:2px 3px 0 0}
.badge.drive{border-color:var(--good);color:var(--good)}
.count{font-size:12px;color:var(--muted)}
a{color:var(--accent)}
</style></head><body><div class="wrap">
<h1>L6 Corpus Index <span class="pill" id="n"></span></h1>
<div class="muted" id="sub"></div>
<div class="bar">
  <input id="q" placeholder="search filename / type / notes" size="26"/>
  <select id="fam"><option value="">any family</option></select>
  <select id="type"><option value="">any type</option></select>
  <select id="src"><option value="">any source</option></select>
  <select id="px"><option value="">any resolution</option></select>
  <select id="cat"><option value="">any category</option></select>
  <select id="drive"><option value="">on-Drive: any</option><option value="1">on Drive</option><option value="0">not on Drive</option></select>
  <select id="sort"><option value="filename">sort: filename</option><option value="arch_type">type</option><option value="px">resolution</option></select>
  <span class="count" id="count"></span>
</div>
<div class="muted" style="font-size:12px">Thumbnails resolve to <code>gdrive_path</code> when public; otherwise the card shows metadata only. Set a CDN/Drive public base in <code>window.IMG_BASE</code> to render images.</div>
<div class="grid" id="grid"></div>
</div>
<script>
const DATA=__DATA__, SUMMARY=__SUMMARY__;
const IMG_BASE = window.IMG_BASE || "";  // set to a public base to render thumbnails
function opt(sel,vals){const s=document.getElementById(sel);Object.keys(vals).sort().forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v+" ("+vals[v]+")";s.appendChild(o);});}
opt("fam",SUMMARY.facets.space_family);opt("type",SUMMARY.facets.arch_type);opt("src",SUMMARY.facets.source);opt("px",SUMMARY.facets.px_bucket);opt("cat",SUMMARY.facets.category);
document.getElementById("n").textContent=SUMMARY.n_images+" images";
document.getElementById("sub").textContent=SUMMARY.n_on_drive+" on Drive · "+SUMMARY.n_pairs+" A/B pairs"+(SUMMARY.has_scores?" · attribute scores joined":" · (no attribute scores yet)");
const G=document.getElementById("grid");
function esc(s){return (s||"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]));}
function render(){
  const q=document.getElementById("q").value.toLowerCase();
  const f={fam:fam.value,type:type.value,src:src.value,px:px.value,cat:cat.value,drive:drive.value};
  let rows=DATA.filter(r=>{
    if(f.fam&&r.space_family!==f.fam)return false;
    if(f.type&&r.arch_type!==f.type)return false;
    if(f.src&&r.source!==f.src)return false;
    if(f.px&&r.px_bucket!==f.px)return false;
    if(f.cat&&r.category!==f.cat)return false;
    if(f.drive==="1"&&!r.on_drive)return false;
    if(f.drive==="0"&&r.on_drive)return false;
    if(q&&!(r.filename+" "+r.arch_type+" "+(r.notes||"")).toLowerCase().includes(q))return false;
    return true;
  });
  const s=sort.value;
  rows.sort((a,b)=> s==="px"? (b.width-a.width) : (""+a[s]).localeCompare(""+b[s]));
  document.getElementById("count").textContent=rows.length+" match";
  G.innerHTML=rows.slice(0,600).map(r=>{
    const img = IMG_BASE? `<div class="thumb" style="background-image:url('${IMG_BASE.replace(/\/$/,'')}/${esc(r.filename)}')"></div>` : `<div class="thumb">${esc(r.filename.split('/').pop())}</div>`;
    const drive = r.on_drive? '<span class="badge drive">Drive</span>':'';
    const pair = r.pair_id? `<span class="badge">pair ${esc(r.pair_id)}${r.pair_expected_better==='A'?' ✓A':''}</span>`:'';
    return `<div class="card">${img}<div class="meta"><div class="t">${esc(r.arch_type)}</div>
      <div class="s">${esc(r.space_family)} · ${esc(r.px_bucket)}px · ${esc(r.source)}</div>
      <div>${drive}${pair}</div></div></div>`;
  }).join("");
  if(rows.length>600)G.innerHTML+=`<div class="muted">…${rows.length-600} more (refine filters)</div>`;
}
["q","fam","type","src","px","cat","drive","sort"].forEach(id=>document.getElementById(id).addEventListener("input",render));
render();
</script></body></html>"""


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default="corpus_L6")
    ap.add_argument("--scores", default=None, help="optional filename,<attr>,... CSV to join")
    a = ap.parse_args()
    s = build(Path(a.corpus), Path(a.scores) if a.scores else None)
    print(json.dumps(s["facets"], indent=1))
    print(f"\n{s['n_images']} images · {s['n_on_drive']} on Drive · {s['n_pairs']} pairs · "
          f"scores={'yes' if s['has_scores'] else 'no'}")
    print("wrote corpus_L6/index.json + corpus_L6/index.html")
