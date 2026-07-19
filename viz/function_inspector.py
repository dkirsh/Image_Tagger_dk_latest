"""
viz.function_inspector — VIEW-2: the per-predicate inspector for ONE annotated unit.

One self-contained HTML: a sidebar of every registry predicate (grouped by run outcome),
and for each predicate a page showing EVERYTHING the run declared about itself:
  - registry contract: id, tier hint, required inputs, MAY_LACK_SIGNAL membership
  - run result: scalar, confidence, full method string, failure modes
  - ALL declared parameters/constants (manifest `extras`, pretty-printed tree)
  - the field thumbnail (if the operator emits one), with its sha256 digest
  - M1' binding: audit class + params (from M1P_BINDINGS), digest when a record is supplied
Deep-linkable: #<predicate-id> anchors — the layered viewer (VIEW-1) can link straight in.

Consumes ONLY the VIEW-0 sidecar (npz + manifest, sidecar_version >= 2) and optionally the
annotation record. NEVER recomputes an operator. Parameterized re-runs are VIEW-5 (server).
"""
from __future__ import annotations
import base64, json, sys
from pathlib import Path

sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/Users/davidusa/REPOS/Image_Tagger_dk_latest")
import numpy as np

from viz.field_sidecars import layer_group

THUMB_W = 260


def _thumb_url(a: np.ndarray) -> str:
    import cv2
    a = np.nan_to_num(np.asarray(a, np.float32))
    rng = float(a.max() - a.min())
    a01 = (a - a.min()) / rng if rng > 1e-9 else np.zeros_like(a)
    h = max(2, int(THUMB_W * a.shape[0] / max(1, a.shape[1])))
    small = cv2.resize(a01, (THUMB_W, h), interpolation=cv2.INTER_AREA)
    heat = cv2.applyColorMap((small * 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS)
    ok, buf = cv2.imencode(".png", heat, [cv2.IMWRITE_PNG_COMPRESSION, 9])
    return "data:image/png;base64," + base64.b64encode(buf.tobytes()).decode()


def build_inspector(sidecar_dir: str, unit_id: str, record_path: str | None = None,
                    html_out: str | None = None) -> str:
    from annotation_socket import registry as R
    from annotation_socket import m1_prime as MP

    root = Path(sidecar_dir)
    man = json.loads((root / f"{unit_id}.manifest.json").read_text())
    if man.get("sidecar_version", 1) < 2:
        raise ValueError("sidecar_version < 2: regenerate the sidecar (meta channel required)")
    npz = np.load(root / f"{unit_id}.npz")
    record = json.loads(Path(record_path).read_text()) if record_path else None
    rec_by_pid = {}
    if record:
        rec_by_pid = {s["predicate"]: s for s in record.get("scores", [])}

    meta, extras = man.get("meta", {}), man.get("extras", {})
    pages = []
    for spec in R.PREDICATES:
        pid = spec["id"]
        m = meta.get(pid)
        ex = extras.get(pid)
        rs = rec_by_pid.get(pid)
        m1p_bind = MP.M1P_BINDINGS.get(pid)
        thumb, fdig = None, None
        if pid in npz.files:
            thumb = _thumb_url(npz[pid])
            fdig = man["arrays"][pid]["sha256"][:16]
        # run outcome bucket for the sidebar
        if m is None:
            bucket = "not_run"          # abstained-inapplicable / plan-path / compound
        elif m.get("scalar") is None:
            bucket = "abstained"
        else:
            bucket = "scored"
        if rs and rs.get("status"):
            bucket = str(rs["status"]).lower()
        pages.append({
            "pid": pid, "bucket": bucket, "group": layer_group(pid),
            "tier": spec.get("tier_hint", "?"),
            "requires": sorted(spec.get("requires", [])),
            "may_lack_signal": pid in R.MAY_LACK_SIGNAL,
            "meta": m, "extras": ex, "thumb": thumb, "field_digest": fdig,
            "m1p": ({"audit_class": m1p_bind[0], "params": m1p_bind[1]} if m1p_bind else None),
            "m1p_digest": ((rs or {}).get("m1p", {}) or {}).get("digest"),
        })

    counts = {}
    for p in pages:
        counts[p["bucket"]] = counts.get(p["bucket"], 0) + 1
    payload = {"unit": man["unit_id"], "model": man["model_version"], "pages": pages,
               "counts": counts,
               "note": "Values, params, and digests are READ from the annotation run of "
                       "record (sidecar); this page never recomputes. Parameterized re-run "
                       "is server mode (VIEW-5)."}
    html = _TEMPLATE.replace("__PAYLOAD__", json.dumps(payload)) \
                    .replace("__TITLE__", f"CNfA inspector — unit {unit_id}")
    out = Path(html_out or (root / f"{unit_id}.inspector.html"))
    out.write_text(html)
    return str(out)


_TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>__TITLE__</title><style>
 body{margin:0;background:#16181d;color:#e8e8e8;font:14px/1.5 -apple-system,Segoe UI,sans-serif;display:flex}
 #side{width:330px;min-width:330px;height:100vh;overflow-y:auto;background:#1f232b;padding:12px;box-sizing:border-box}
 #main{flex:1;height:100vh;overflow-y:auto;padding:20px 28px;box-sizing:border-box}
 h1{font-size:15px;margin:0 0 8px;color:#ffd866}
 .b{font-size:11px;color:#7fd4d4;text-transform:uppercase;letter-spacing:.06em;margin:12px 0 4px}
 .plink{display:block;padding:2px 6px;border-radius:4px;color:#cdd;text-decoration:none;font-size:12.5px;cursor:pointer}
 .plink:hover{background:#2b3140}.plink.sel{background:#37405a;color:#fff}
 .tag{display:inline-block;font-size:10px;padding:0 6px;border-radius:8px;margin-left:6px;vertical-align:1px}
 .t-scored{background:#2e5d3a}.t-abstained{background:#6b5b21}.t-not_run{background:#444}.t-unknown{background:#6b2a2a}
 .card{background:#1d2129;border:1px solid #333a48;border-radius:8px;padding:14px 16px;margin-bottom:14px}
 .k{color:#8fb8e8}.mono{font-family:ui-monospace,Menlo,monospace;font-size:12px;white-space:pre-wrap;word-break:break-word}
 .fm{color:#e0a060}.big{font-size:22px;color:#ffd866}
 img.th{border-radius:6px;border:1px solid #333a48;display:block;margin:6px 0}
 .note{font-size:11px;color:#9aa;margin-top:16px}
 table{border-collapse:collapse;font-size:12px}td{padding:1px 8px 1px 0;vertical-align:top}
</style></head><body>
<div id="side"><h1>__TITLE__</h1><div id="nav"></div><div class="note" id="gnote"></div></div>
<div id="main"></div>
<script>
const P=__PAYLOAD__;
const nav=document.getElementById('nav'),main=document.getElementById('main');
document.getElementById('gnote').textContent=P.note+' · model '+P.model;
const buckets=['scored','abstained','unknown','not_run'];
const label={scored:'Scored ('+(P.counts.scored||0)+')',abstained:'Abstained ('+(P.counts.abstained||0)+')',unknown:'Unknown ('+(P.counts.unknown||0)+')',not_run:'Not run on this unit ('+(P.counts.not_run||0)+')'};
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function tree(o,ind){if(o===null||typeof o!=='object')return esc(JSON.stringify(o));
 if(Array.isArray(o)){if(o.length>12)return esc(JSON.stringify(o.slice(0,12)))+' …('+o.length+')';return esc(JSON.stringify(o))}
 return Object.entries(o).map(([k,v])=>'\n'+' '.repeat(ind)+'<span class="k">'+esc(k)+'</span>: '+tree(v,ind+2)).join('')}
function show(pid){
 [...nav.querySelectorAll('.plink')].forEach(a=>a.classList.toggle('sel',a.dataset.pid===pid));
 const p=P.pages.find(x=>x.pid===pid);if(!p)return;location.hash=encodeURIComponent(pid);
 let h='<div class="card"><div style="font-size:16px;color:#fff">'+esc(p.pid)+'<span class="tag t-'+p.bucket+'">'+p.bucket+'</span></div>';
 h+='<table><tr><td class="k">tier hint</td><td>'+esc(p.tier)+'</td></tr>';
 h+='<tr><td class="k">requires</td><td>'+(p.requires.length?esc(p.requires.join(', ')):'image only')+'</td></tr>';
 h+='<tr><td class="k">may lack signal</td><td>'+(p.may_lack_signal?'yes (signal_absent abstention licensed)':'no')+'</td></tr></table></div>';
 if(p.meta){h+='<div class="card">';
  if(p.meta.scalar!==null&&p.meta.scalar!==undefined)h+='<div class="big">'+p.meta.scalar.toFixed(4)+'</div><div style="font-size:11px;color:#9aa">scalar · confidence '+p.meta.confidence+'</div>';
  h+='<div class="mono" style="margin-top:8px">'+esc(p.meta.method||'')+'</div>';
  if(p.meta.failure_modes&&p.meta.failure_modes.length)h+='<div class="b">declared failure modes</div>'+p.meta.failure_modes.map(f=>'<div class="fm">• '+esc(f)+'</div>').join('');
  h+='</div>';}
 if(p.thumb){h+='<div class="card"><div class="b">field</div><img class="th" src="'+p.thumb+'"><div class="mono">sha256 '+p.field_digest+'… (full digest in manifest)</div></div>';}
 if(p.extras){h+='<div class="card"><div class="b">declared parameters & constants (all of them)</div><div class="mono">'+tree(p.extras,0)+'</div></div>';}
 if(p.m1p){h+='<div class="card"><div class="b">M1&prime; audit binding</div><div class="mono">audit_class: '+esc(p.m1p.audit_class)+tree(p.m1p.params,0)+(p.m1p_digest?'\ndigest: '+esc(p.m1p_digest):'\n(digest appears when a record is supplied)')+'</div></div>';}
 else{h+='<div class="card"><div class="b">M1&prime; audit binding</div><div class="mono">none yet — owed under CC-2 if scored</div></div>';}
 main.innerHTML=h;}
buckets.forEach(b=>{const ps=P.pages.filter(p=>p.bucket===b);if(!ps.length)return;
 const d=document.createElement('div');d.className='b';d.textContent=label[b];nav.appendChild(d);
 ps.forEach(p=>{const a=document.createElement('a');a.className='plink';a.dataset.pid=p.pid;
  a.textContent=p.pid.replace(/^cnfa\./,'');a.onclick=()=>show(p.pid);nav.appendChild(a);});});
const h0=decodeURIComponent(location.hash.slice(1));
show(P.pages.find(p=>p.pid===h0)?h0:(P.pages.find(p=>p.bucket==='scored')||P.pages[0]).pid);
</script></body></html>"""


# ------------------------------------------------------------------ self-test (VERIFY rule 1)
if __name__ == "__main__":
    out = build_inspector("/home/claude/viz_out", "04d7e703eb98678e")
    p = Path(out); txt = p.read_text()
    payload = json.loads(txt.split("__PAYLOAD__")[0].split("const P=")[1].rsplit(";\nconst nav", 1)[0]) \
        if False else None
    assert p.stat().st_size > 40_000, "suspiciously small inspector"
    assert txt.count("data:image/png") >= 15, "missing field thumbnails"
    assert "declared parameters" in txt and "M1" in txt, "core sections missing"
    assert "never recomputes" in txt, "no-recompute contract note missing"
    # spot-check payload integrity: FC page must carry its combination constants
    raw = txt.split("const P=", 1)[1].split(";\nconst nav", 1)[0]
    P = json.loads(raw)
    fc = next(x for x in P["pages"] if x["pid"] == "cnfa.fluency.feature_congestion")
    assert fc["extras"]["combination"]["color_div"] == 0.2088, "FC constants not surfaced"
    assert fc["meta"]["failure_modes"], "FC failure modes missing"
    n_th = sum(1 for x in P["pages"] if x["thumb"])
    print(f"OK function_inspector: {out} ({p.stat().st_size/1e6:.2f} MB, "
          f"{len(P['pages'])} predicate pages, {n_th} field thumbnails, "
          f"buckets {P['counts']})")
