"""
viz.layered_viewer — VIEW-1: self-contained layered HTML viewer for ONE annotated unit.

Consumes ONLY the VIEW-0 sidecar (npz + manifest) and optionally the annotation record.
It NEVER recomputes an operator. One output file: <unit_id>.html — open it anywhere,
no server, no external assets, no browser storage.

Layer architecture (TASKS.md Sprint VIEW): groups by REGISTER —
  1 base image · 2 semantic zones · 3 light · 4 fluency-clutter · 5 space-geometry
  6 acoustics · 7 evidence (from record, if given) · 8 audit (coverage, digests, tier)

Every continuous field renders as a transparent viridis overlay (alpha follows magnitude);
the zone layer renders categorically with the 11-class palette + legend + hover tooltips
fed by the zone table (class, D, R2, hedonic HYPOTHESIS — labeled as such).
Acceptance (TASKS.md VIEW-1): open the file, understand the room's annotation without docs.
"""
from __future__ import annotations
import base64, io, json, sys
from pathlib import Path

sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/Users/davidusa/REPOS/Image_Tagger_dk_latest")
import numpy as np

from viz.field_sidecars import _ZONE_BGR, layer_group

MAX_W = 900          # overlay render width cap (keeps the single file small)
GROUP_ORDER = ["semantic_zones", "light", "fluency_clutter", "space_geometry", "acoustics"]
GROUP_TITLE = {"semantic_zones": "2 · Semantic zones", "light": "3 · Light",
               "fluency_clutter": "4 · Fluency / clutter", "space_geometry": "5 · Space geometry",
               "acoustics": "6 · Acoustics"}


def _png_data_url(bgra: np.ndarray) -> str:
    import cv2
    ok, buf = cv2.imencode(".png", bgra)
    assert ok
    return "data:image/png;base64," + base64.b64encode(buf.tobytes()).decode()


def _jpg_data_url(bgr: np.ndarray) -> str:
    import cv2
    ok, buf = cv2.imencode(".jpg", bgr, [cv2.IMWRITE_JPEG_QUALITY, 82])
    assert ok
    return "data:image/jpeg;base64," + base64.b64encode(buf.tobytes()).decode()


def _heat_overlay(a: np.ndarray, W: int, H: int) -> np.ndarray:
    """Transparent viridis overlay: alpha tracks normalized magnitude (weak -> invisible)."""
    import cv2
    a = np.nan_to_num(np.asarray(a, np.float32))
    rng = float(a.max() - a.min())
    a01 = (a - a.min()) / rng if rng > 1e-9 else np.zeros_like(a)
    a01 = cv2.resize(a01, (W, H), interpolation=cv2.INTER_LINEAR)
    heat = cv2.applyColorMap((a01 * 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS)
    alpha = (np.clip(a01, 0, 1) * 0.85 * 255).astype(np.uint8)
    return np.dstack([heat, alpha])


def _zone_overlay(class_field: np.ndarray, W: int, H: int) -> np.ndarray:
    import cv2
    cm = np.rint(np.asarray(class_field, np.float32) * 11.0).astype(np.int32)
    cm = cv2.resize(cm.astype(np.float32), (W, H), interpolation=cv2.INTER_NEAREST).astype(np.int32)
    out = np.zeros((H, W, 4), np.uint8)
    for cid, bgr in _ZONE_BGR.items():
        if bgr is not None:
            out[cm == cid] = (*bgr, 128)
    return out


def _grid_overlay(grid: np.ndarray, W: int, H: int) -> np.ndarray:
    """Plan grid is plan-space, not image-space: render as an inset thumbnail overlay
    (top-right corner) so it never pretends to be a pixel-registered field."""
    import cv2
    g = np.asarray(grid, np.float32)
    free = (g > 0).astype(np.uint8) * 255
    th = max(60, H // 4); tw = max(60, int(th * g.shape[1] / max(1, g.shape[0])))
    thumb = cv2.resize(free, (tw, th), interpolation=cv2.INTER_NEAREST)
    out = np.zeros((H, W, 4), np.uint8)
    x0 = W - tw - 8
    out[8:8 + th, x0:x0 + tw, 0] = 40
    out[8:8 + th, x0:x0 + tw, 1] = thumb
    out[8:8 + th, x0:x0 + tw, 2] = 220 - thumb // 2
    out[8:8 + th, x0:x0 + tw, 3] = 210
    return out


def build_viewer(sidecar_dir: str, unit_id: str, record_path: str | None = None,
                 html_out: str | None = None) -> str:
    import cv2
    root = Path(sidecar_dir)
    man = json.loads((root / f"{unit_id}.manifest.json").read_text())
    npz = np.load(root / f"{unit_id}.npz")

    base = cv2.imread(man["image_path"])
    if base is None:
        raise FileNotFoundError(man["image_path"])
    H0, W0 = base.shape[:2]
    scale = min(1.0, MAX_W / W0)
    W, H = int(W0 * scale), int(H0 * scale)
    base_r = cv2.resize(base, (W, H), interpolation=cv2.INTER_AREA)

    record = json.loads(Path(record_path).read_text()) if record_path else None

    # ---------------- layers
    layers = []          # {key, group, url, label}
    for key in sorted(npz.files):
        if key.startswith("_tables") or key.startswith("_extras"):
            continue     # promoted extras arrays: inspector material (VIEW-2), not map layers
        g = layer_group(key)
        a = npz[key]
        if key == "cnfa.fluency.complexity_partition":
            ov = _zone_overlay(a, W, H)
        elif key == "_plan.grid":
            ov = _grid_overlay(a, W, H)
        elif a.ndim != 2:
            continue
        else:
            ov = _heat_overlay(a, W, H)
        layers.append({"key": key, "group": g, "url": _png_data_url(ov),
                       "label": key.split(".")[-1].replace("_", " ")})

    # ---------------- zone legend + tooltip data
    zones = man["tables"].get("cnfa.fluency.complexity_partition", [])
    cids = (man["extras"].get("cnfa.fluency.complexity_partition", {}) or {}).get("class_ids", {})
    hexc = {name: "#{:02x}{:02x}{:02x}".format(*(_ZONE_BGR[cid][::-1]))
            for name, cid in cids.items() if _ZONE_BGR.get(cid)}
    for z in zones:                      # scale bboxes into display space
        x, y, w, h = z["bbox_px"]
        z["_bb"] = [round(x * scale), round(y * scale), round(w * scale), round(h * scale)]

    # ---------------- evidence chips (record only)
    chips = []
    if record:
        for s in record["scores"]:
            if s.get("status") == "scored" and isinstance(s.get("evidence"), dict):
                ev = s["evidence"]
                reg = ev.get("region")
                if isinstance(reg, list) and len(reg) == 4:
                    x0, y0, x1, y1 = [round(v * scale) for v in reg]
                    chips.append({"pid": s["predicate"], "val": s.get("value"),
                                  "bb": [x0, y0, x1 - x0, y1 - y0],
                                  "tier": s.get("tier", "?")})

    audit = {"unit_id": man["unit_id"], "model_version": man["model_version"],
             "image_sha256": man["image_sha256"][:16] + "…", "coverage": man["coverage"],
             "arrays": {k: v["sha256"][:12] for k, v in man["arrays"].items()},
             "sidecar_version": man["sidecar_version"]}

    payload = {"W": W, "H": H, "layers": layers, "zones": zones, "zoneColors": hexc,
               "chips": chips, "audit": audit,
               "hedonicNote": "zone hedonic tags are UNLICENSED hypotheses (corpus-pending), "
                              "never scored values"}

    html = _TEMPLATE.replace("__BASE__", _jpg_data_url(base_r)) \
                    .replace("__PAYLOAD__", json.dumps(payload)) \
                    .replace("__TITLE__", f"CNfA unit {unit_id}")
    out = Path(html_out or (root / f"{unit_id}.html"))
    out.write_text(html)
    return str(out)


_TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>__TITLE__</title><style>
 body{margin:0;background:#16181d;color:#e8e8e8;font:14px/1.45 -apple-system,Segoe UI,sans-serif;display:flex}
 #side{width:300px;min-width:300px;height:100vh;overflow-y:auto;background:#1f232b;padding:12px;box-sizing:border-box}
 #stage{position:relative;margin:16px auto}
 #stage img,#stage canvas{position:absolute;left:0;top:0}
 h1{font-size:15px;margin:0 0 10px;color:#ffd866}h2{font-size:12px;margin:14px 0 4px;color:#7fd4d4;text-transform:uppercase;letter-spacing:.06em}
 label{display:flex;gap:6px;align-items:center;padding:2px 0;cursor:pointer;font-size:13px}
 input[type=range]{width:90px;margin-left:auto}
 .sw{width:12px;height:12px;border-radius:3px;display:inline-block}
 #tip{position:fixed;pointer-events:none;background:#000d;color:#fff;padding:8px 10px;border-radius:6px;font-size:12px;max-width:280px;display:none;z-index:9;border:1px solid #555}
 #audit{font-size:11px;color:#aab;white-space:pre-wrap;word-break:break-all;background:#171a20;padding:8px;border-radius:6px;margin-top:6px}
 .note{font-size:11px;color:#e0b060;margin:4px 0}
 .chip{position:absolute;border:1.5px dashed #ffd866;border-radius:4px;pointer-events:none;display:none}
 .chiplab{position:absolute;background:#ffd866;color:#222;font-size:10px;padding:0 4px;border-radius:3px;transform:translateY(-100%);pointer-events:none;display:none}
</style></head><body>
<div id="side">
 <h1>__TITLE__</h1>
 <h2>1 · Base</h2><label><input type="checkbox" id="baseChk" checked> image</label>
 <div id="groups"></div>
 <h2>7 · Evidence</h2><label><input type="checkbox" id="chipChk"> predicate evidence boxes</label>
 <div id="chipInfo" class="note"></div>
 <h2>8 · Audit</h2><div id="audit"></div>
</div>
<div style="flex:1;overflow:auto"><div id="stage"></div></div>
<div id="tip"></div>
<script>
const P=__PAYLOAD__;
const stage=document.getElementById('stage');stage.style.width=P.W+'px';stage.style.height=P.H+'px';
const baseImg=new Image();baseImg.src="__BASE__";baseImg.width=P.W;baseImg.height=P.H;stage.appendChild(baseImg);
document.getElementById('baseChk').onchange=e=>baseImg.style.visibility=e.target.checked?'visible':'hidden';
const GT={semantic_zones:'2 · Semantic zones',light:'3 · Light',fluency_clutter:'4 · Fluency / clutter',space_geometry:'5 · Space geometry',acoustics:'6 · Acoustics'};
const groupsDiv=document.getElementById('groups');const order=['semantic_zones','light','fluency_clutter','space_geometry','acoustics'];
const byG={};P.layers.forEach(l=>{(byG[l.group]=byG[l.group]||[]).push(l)});
order.forEach(g=>{const ls=byG[g];if(!ls)return;
 const h=document.createElement('h2');h.textContent=GT[g]||g;groupsDiv.appendChild(h);
 const op=document.createElement('label');op.innerHTML='group opacity <input type="range" min="0" max="100" value="70">';groupsDiv.appendChild(op);
 const slider=op.querySelector('input');
 ls.forEach(l=>{const img=new Image();img.src=l.url;img.width=P.W;img.height=P.H;img.style.opacity=.7;img.style.visibility='hidden';stage.appendChild(img);l.el=img;
  const lab=document.createElement('label');
  const sw=l.key==='cnfa.fluency.complexity_partition'?'<span class="sw" style="background:linear-gradient(90deg,#50c850,#e63c3c,#dc8c5a)"></span>':'<span class="sw" style="background:linear-gradient(90deg,#440154,#21918c,#fde725)"></span>';
  lab.innerHTML='<input type="checkbox">'+sw+l.label;groupsDiv.appendChild(lab);
  lab.querySelector('input').onchange=e=>img.style.visibility=e.target.checked?'visible':'hidden';});
 slider.oninput=()=>ls.forEach(l=>l.el.style.opacity=slider.value/100);});
if(byG.semantic_zones){const leg=document.createElement('div');
 leg.innerHTML=Object.entries(P.zoneColors).map(([n,c])=>'<label><span class="sw" style="background:'+c+'"></span>'+n.replace(/_/g,' ')+'</label>').join('');
 const h=[...groupsDiv.querySelectorAll('h2')].find(x=>x.textContent.includes('Semantic'));h.after(leg);
 const nt=document.createElement('div');nt.className='note';nt.textContent=P.hedonicNote;leg.after(nt);
 const first=byG.semantic_zones[0];first.el.style.visibility='visible';groupsDiv.querySelectorAll('input[type=checkbox]')[0].checked=true;}
const tip=document.getElementById('tip');
stage.addEventListener('mousemove',e=>{const r=stage.getBoundingClientRect();const x=e.clientX-r.left,y=e.clientY-r.top;
 const hits=P.zones.filter(z=>{const[a,b,w,h]=z._bb;return x>=a&&x<=a+w&&y>=b&&y<=b+h});
 if(!hits.length){tip.style.display='none';return}
 hits.sort((p,q)=>p._bb[2]*p._bb[3]-q._bb[2]*q._bb[3]);const z=hits[0];
 tip.innerHTML='<b>'+z['class'].replace(/_/g,' ')+'</b><br>D='+z.D+' (R²='+z.R2+')'+(z.in_preferred_band?' · in 1.15–1.70 band':'')+'<br>area '+(z.area_frac*100).toFixed(1)+'%<br><i>hypothesis: '+z.hedonic_hypothesis.replace(/_/g,' ')+'</i>';
 tip.style.display='block';tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+10)+'px';});
stage.addEventListener('mouseleave',()=>tip.style.display='none');
const chipChk=document.getElementById('chipChk');const chipEls=[];
P.chips.forEach(c=>{const d=document.createElement('div');d.className='chip';d.style.left=c.bb[0]+'px';d.style.top=c.bb[1]+'px';d.style.width=c.bb[2]+'px';d.style.height=c.bb[3]+'px';
 const l=document.createElement('div');l.className='chiplab';l.style.left=c.bb[0]+'px';l.style.top=c.bb[1]+'px';l.textContent=c.pid.split('.').pop()+' '+(typeof c.val==='number'?c.val.toFixed(2):'');
 stage.appendChild(d);stage.appendChild(l);chipEls.push(d,l);});
document.getElementById('chipInfo').textContent=P.chips.length?P.chips.length+' scored predicates carry image-region evidence':'(no record supplied — evidence layer empty)';
chipChk.onchange=e=>chipEls.forEach(el=>el.style.display=e.target.checked?'block':'none');
document.getElementById('audit').textContent='unit '+P.audit.unit_id+'\nmodel '+P.audit.model_version+'\nimage sha '+P.audit.image_sha256+'\ncoverage '+JSON.stringify(P.audit.coverage)+'\narray digests (12-hex): '+Object.entries(P.audit.arrays).map(([k,v])=>'\n  '+k+' '+v).join('');
</script></body></html>"""


# ------------------------------------------------------------------ self-test (VERIFY rule 1)
if __name__ == "__main__":
    out = build_viewer("/home/claude/viz_out", "04d7e703eb98678e")
    p = Path(out)
    txt = p.read_text()
    assert p.stat().st_size > 100_000, "suspiciously small viewer"
    assert txt.count("data:image/png") >= 15, "missing layer overlays"
    assert "hedonic" in txt and "UNLICENSED" in txt, "hedonic honesty note missing"
    assert "array digests" in txt, "audit layer missing"
    print(f"OK layered_viewer: {out} ({p.stat().st_size/1e6:.2f} MB, "
          f"{txt.count('data:image/png')} overlay images)")
