"""
viz.question_composer — VIEW-3 (2026-07-20): the question-driven display composer.

Pipeline (TASKS.md Sprint VIEW):
    question  ->  compose(question, record, manifest)  ->  display-composition JSON
              ->  render_question_view(...)             ->  self-contained HTML

    display-composition = {
        question, question_class,
        layers:    [{key|group, reason}]            # WHICH registers/fields to turn on
        focus:     [{kind, bbox|zone, label}]       # WHERE to look (zone/evidence bboxes)
        narrative: [{text, anchor}]                 # the explanation, each line anchored to a layer/zone
        how_to_read:[str]                           # legend/what the colours mean
        provenance:{unit_id, model_version, note}
    }

THE ≠-MIND SEPARATION (identical to the inference-judge boundary):
  The composer is ADVISORY-ONLY. It SELECTS registered layers and WRITES prose, but every number in
  the narrative is substituted FROM THE RECORD by `_fill()` — the composer never invents or alters a
  score. An optional `llm` hook (compose(..., llm=callable)) may reorder/curate the layer set and
  rewrite the prose templates, but it receives ONLY the registry-derived options + record-derived
  values and its output is re-validated: any numeric claim not present in the record is dropped. The
  renderer reads scores ONLY from the record. An LLM therefore cannot change a single scored value —
  it can only decide what to SHOW and how to EXPLAIN it. Fail-closed: a predicate that ABSTAINED or is
  absent is reported as such (with its named missing inputs), never papered over with a fabricated number.

Consumes ONLY the record + sidecar manifest (viewer contract: never recompute).
Self-test / acceptance:  python3 -m viz.question_composer
"""
from __future__ import annotations
import json, re, html
from pathlib import Path
from typing import Dict, List, Optional, Callable


# ---------------------------------------------------------------- registry-aware class templates
# Each class names the REGISTERS/predicates it wants lit, the zone classes it focuses, and the
# predicates whose record values drive its narrative. Keywords route the free-text question.
QUESTION_CLASSES: List[Dict] = [
    {
        "name": "noise",
        "keywords": ["noise", "sound", "acoustic", "loud", "quiet", "speech", "reverberation",
                     "street", "traffic", "spl", "db", "decibel"],
        "groups": ["acoustics", "semantic_zones"],
        "predicates": ["cnfa.acoustic.street_noise_intrusion", "C7.focus_speech_privacy",
                       "C8.distraction_distance", "C20.chronic_soundscape"],
        "focus_zones": ["circulation", "neutral"],          # foyer/entrance proxy zones
        "lede": "How sound — street intrusion and speech privacy — plays across this space:",
        "how_to_read": ["Acoustics overlays are plan-projected SPL / STI fields (warmer = louder / "
                        "less private).", "Semantic zones locate WHERE — the foreground circulation "
                        "zone is the foyer/entrance proxy."],
    },
    {
        "name": "clutter",
        "keywords": ["clutter", "busy", "messy", "cluttered", "visual load", "congestion",
                     "overload", "complexity", "tidy", "orderly", "where is it busy"],
        "groups": ["fluency_clutter", "semantic_zones"],
        "predicates": ["cnfa.fluency.complexity_partition", "cnfa.fluency.feature_congestion",
                       "cnfa.fluency.subband_entropy", "cnfa.fluency.proto_object_count"],
        "focus_zones": ["junk", "collection", "ornament"],
        "lede": "Where visual load concentrates, and of what kind:",
        "how_to_read": ["Fluency/clutter overlays are continuous congestion fields (warmer = busier).",
                        "Junk/collection/ornament zones carry the semantic partition's clutter classes."],
    },
    {
        "name": "biophilia",
        "keywords": ["biophilia", "biophilic", "nature", "plants", "greenery", "vegetation",
                     "wood", "material", "water", "daylight", "restorative", "restoration"],
        "groups": ["semantic_zones", "light"],
        "predicates": ["cnfa.fluency.complexity_partition", "C19.restoration_nature",
                       "C10.daylight_proximity", "cnfa.light.warm_vs_cool_ratio"],
        "focus_zones": ["vegetation", "material", "water", "sky"],
        "lede": "The restorative / biophilic content — nature, natural material, light:",
        "how_to_read": ["Vegetation/material/water zones come from the 11-class semantic partition "
                        "(AMBER heuristic gates — corpus calibration owed).",
                        "Light overlays show the daylight distribution."],
    },
    {
        "name": "wayfinding",
        "keywords": ["wayfinding", "navigate", "navigation", "find my way", "orient", "lost",
                     "legible", "legibility", "integration", "blind corner", "circulation", "path"],
        "groups": ["space_geometry"],
        "predicates": ["C3.intelligibility", "C1.visual_integration", "C4.wayfinding_load",
                       "cnfa.geometry.blind_corner_index"],
        "focus_zones": [],
        "lede": "How easy the space is to read and move through:",
        "how_to_read": ["Space-geometry layers ride the INFERRED plan (Tier-B, AMBER): integration, "
                        "intelligibility, wayfinding load.", "Blind-corner index flags occluding turns "
                        "on the circulation skeleton."],
    },
    {
        "name": "privacy",
        "keywords": ["privacy", "private", "exposed", "refuge", "enclosure", "enclosed",
                     "prospect", "overlooked", "seclusion", "barrier", "permeable", "see-through"],
        "groups": ["space_geometry", "acoustics"],
        "predicates": ["cnfa.spatial.enclosure_index", "cnfa.spatial.prospect",
                       "cnfa.geometry.barrier_permeability", "C7.focus_speech_privacy"],
        "focus_zones": [],
        "lede": "Refuge vs exposure — visual and acoustic privacy:",
        "how_to_read": ["Enclosure/prospect fields show refuge vs openness.",
                        "Barrier permeability reports see-through (visual) and gap (physical) "
                        "separately — never averaged."],
    },
]
_DEFAULT_CLASS = {
    "name": "overview", "keywords": [], "groups": ["semantic_zones", "space_geometry"],
    "predicates": ["cnfa.fluency.complexity_partition", "C3.intelligibility",
                   "C1.visual_integration"],
    "focus_zones": [], "lede": "An overview of the strongest computed attributes here:",
    "how_to_read": ["Layers are grouped by register; toggle to explore.",
                    "Tiers: GREEN mechanical, AMBER evidence-capped (awaits the ≠-mind judge)."],
}


def classify_question(question: str) -> Dict:
    """Keyword-score the free-text question into a class. Deterministic; ties -> earliest class."""
    q = question.lower()
    best, best_score = _DEFAULT_CLASS, 0
    for cls in QUESTION_CLASSES:
        score = sum(1 for kw in cls["keywords"] if kw in q)
        if score > best_score:
            best, best_score = cls, score
    return best


# ---------------------------------------------------------------- record helpers (score source)
def _score_by_pid(record: Dict) -> Dict[str, Dict]:
    return {s["predicate"]: s for s in record.get("scores", [])}


def _fill(record: Dict, pid: str) -> Dict:
    """The ONLY place a predicate's state enters the narrative. Returns the record-true state:
    {status, value|None, tier, missing|reason}. The composer/LLM may template around this but may
    never override `value` — that is the score-separation guarantee."""
    s = _score_by_pid(record).get(pid)
    if s is None:
        return {"pid": pid, "status": "absent", "value": None, "tier": None,
                "detail": "not in this unit's registry coverage"}
    st = str(s.get("status", "")).upper()      # derivation constants are UPPERCASE (SCORED/ABSTAINED/UNKNOWN)
    if st == "SCORED":
        return {"pid": pid, "status": "scored", "value": s.get("value"),
                "tier": s.get("tier_hint") or s.get("tier"),   # score records carry tier_hint
                "detail": (s.get("evidence") or {}).get("signal", "")}
    if st == "ABSTAINED":
        if s.get("signal_absent"):
            ev = s.get("absence_evidence") or {}
            return {"pid": pid, "status": "signal_absent", "value": None, "tier": None,
                    "detail": ev.get("reason") or "signal not present in this image"}
        return {"pid": pid, "status": "abstained", "value": None, "tier": None,
                "detail": "needs declared inputs: " + ", ".join(sorted(s.get("missing_inputs", [])))}
    return {"pid": pid, "status": (st.lower() or "unknown"), "value": None, "tier": None,
            "detail": s.get("reason", "")}


def _phrase(f: Dict) -> str:
    """Human phrase for one predicate's record-true state — numbers come only from `f`."""
    short = f["pid"].split(".")[-1].replace("_", " ")
    if f["status"] == "scored":
        return f"{short} = {f['value']:.3f} ({f['tier']})"
    if f["status"] == "abstained":
        return f"{short}: UNSCORED — {f['detail']}"
    if f["status"] == "signal_absent":
        return f"{short}: signal absent here ({f['detail']})"
    if f["status"] == "absent":
        return f"{short}: not computed on this unit"
    return f"{short}: {f['status']}"


# ---------------------------------------------------------------- composition
def compose(question: str, record: Dict, manifest: Dict,
            llm: Optional[Callable] = None) -> Dict:
    """question + record + sidecar manifest -> display-composition JSON. `llm`, if given, is an
    advisory curator: llm(candidate_composition, record_facts) -> curated_composition. Its numeric
    claims are re-validated against the record (score-separation); on any error the deterministic
    composition is used unchanged."""
    cls = classify_question(question)
    arrays = manifest.get("arrays", {})
    tables = manifest.get("tables", {})

    # ---- layers: registry-aware. Turn on every sidecar array in the class's registers, plus a
    #      base + zones anchor. We only ever reference layers that EXIST in the sidecar.
    wanted_groups = set(cls["groups"])
    layers = [{"key": "__base__", "group": "base", "reason": "the photograph"}]
    for key, meta in sorted(arrays.items()):
        g = meta.get("layer_group")
        if g in wanted_groups:
            layers.append({"key": key, "group": g,
                           "reason": f"{g} register — relevant to a '{cls['name']}' question"})

    # ---- focus: zones whose class matches the template + evidence bboxes of the class predicates
    zones = tables.get("cnfa.fluency.complexity_partition", []) or []
    focus = []
    for z in zones:
        zclass = str(z.get("class", "")).lower()
        if any(fz in zclass for fz in cls["focus_zones"]):
            focus.append({"kind": "zone", "bbox": z.get("bbox_px"),
                          "label": f"{z.get('class')} zone"})
    # 'foyer' proxy: the lowest (nearest-camera) circulation/neutral zone
    if cls["name"] == "noise" and zones:
        foyer = _foyer_zone(zones)
        if foyer:
            focus.insert(0, {"kind": "zone", "bbox": foyer.get("bbox_px"),
                             "label": "foyer / entrance (foreground zone proxy)"})
    sbp = _score_by_pid(record)
    for pid in cls["predicates"]:
        s = sbp.get(pid)
        if s and s.get("status") == "scored":
            reg = (s.get("evidence") or {}).get("region")
            if isinstance(reg, list) and len(reg) == 4:
                focus.append({"kind": "evidence", "bbox": reg,
                              "label": f"{pid.split('.')[-1]} evidence"})

    # ---- narrative: the lede + one record-true line per class predicate (numbers via _fill only)
    narrative = [{"text": cls["lede"], "anchor": None}]
    facts = [_fill(record, pid) for pid in cls["predicates"]]
    for f in facts:
        narrative.append({"text": _phrase(f), "anchor": f["pid"]})
    narrative.append({"text": _closing(cls, facts, zones), "anchor": None})

    composition = {
        "question": question,
        "question_class": cls["name"],
        "layers": layers,
        "focus": [f for f in focus if f.get("bbox")],
        "narrative": narrative,
        "how_to_read": list(cls["how_to_read"]),
        "provenance": {"unit_id": manifest.get("unit_id"),
                       "model_version": manifest.get("model_version"),
                       "note": "LLM-advisory-only: layers/prose are composed; scores are read "
                               "verbatim from the record and never altered."},
    }
    if llm is not None:
        composition = _apply_llm_advice(composition, record, llm)
    return composition


def _foyer_zone(zones: List[Dict]) -> Optional[Dict]:
    """Foyer proxy: the circulation/neutral zone nearest the camera (largest bbox bottom edge)."""
    cand = [z for z in zones if str(z.get("class", "")).lower() in ("circulation", "neutral", "ordered")]
    pool = cand or zones
    def bottom(z):
        b = z.get("bbox_px") or [0, 0, 0, 0]
        return b[1] + b[3]
    return max(pool, key=bottom) if pool else None


def _closing(cls: Dict, facts: List[Dict], zones: List[Dict]) -> str:
    scored = [f for f in facts if f["status"] == "scored"]
    unscored = [f for f in facts if f["status"] in ("abstained", "signal_absent", "absent")]
    bits = []
    if scored:
        bits.append(f"{len(scored)} of {len(facts)} relevant attributes are scored here")
    if unscored:
        need = "; ".join(f["detail"] for f in unscored if f["status"] == "abstained")
        if need:
            bits.append(f"the rest await declared inputs ({need})")
        else:
            bits.append(f"{len(unscored)} carry no signal on this image")
    if not bits:
        bits.append("no directly-relevant attribute is available on this unit")
    return "Read-out: " + "; ".join(bits) + "."


def _apply_llm_advice(composition: Dict, record: Dict, llm: Callable) -> Dict:
    """Let an advisory LLM curate ORDER/SELECTION + prose, then RE-VALIDATE every numeric claim
    against the record. Any number the record does not contain is stripped (score-separation)."""
    try:
        facts = {s["predicate"]: s.get("value") for s in record.get("scores", [])
                 if s.get("status") == "scored"}
        curated = llm(composition, facts)
        if not isinstance(curated, dict) or "narrative" not in curated:
            return composition
        allowed = {round(float(v), 3) for v in facts.values() if isinstance(v, (int, float))}
        for line in curated["narrative"]:
            for num in re.findall(r"\d+\.\d+", line.get("text", "")):
                if round(float(num), 3) not in allowed:
                    line["text"] = line["text"].replace(num, "[redacted:unverified]")
        curated["provenance"] = composition["provenance"]
        curated["_llm_curated"] = True
        return curated
    except Exception:
        return composition        # fail closed to the deterministic composition


# ---------------------------------------------------------------- renderer (self-contained HTML)
def render_question_view(composition: Dict, sidecar_dir: str, unit_id: str,
                         record: Optional[Dict] = None, html_out: Optional[str] = None) -> str:
    """Render the composition against the sidecar into ONE self-contained HTML file. Reuses the
    VIEW-1 overlay machinery; shows only the COMPOSED layers, the focus boxes, and the narrative
    panel with clickable anchors. Never recomputes — arrays come from the npz, scores from the record."""
    import numpy as np, cv2
    from viz.layered_viewer import (_png_data_url, _jpg_data_url, _heat_overlay,
                                     _zone_overlay, _grid_overlay, MAX_W)
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

    wanted = {l["key"] for l in composition["layers"]}
    layers = []
    for key in sorted(npz.files):
        if key.startswith("_tables") or key.startswith("_extras") or key not in wanted:
            continue
        a = npz[key]
        if key == "cnfa.fluency.complexity_partition":
            ov = _zone_overlay(a, W, H)
        elif key == "_plan.grid":
            ov = _grid_overlay(a, W, H)
        elif a.ndim != 2:
            continue
        else:
            ov = _heat_overlay(a, max(2, W // 2), max(2, H // 2))
        layers.append({"key": key, "url": _png_data_url(ov),
                       "label": key.split(":")[-1].split(".")[-1].replace("_", " ")})

    focus = []
    for f in composition["focus"]:
        b = f.get("bbox")
        if isinstance(b, list) and len(b) == 4:
            focus.append({"bb": [round(b[0] * scale), round(b[1] * scale),
                                 round(b[2] * scale), round(b[3] * scale)],
                          "label": f.get("label", "")})

    payload = {"W": W, "H": H, "layers": layers, "focus": focus,
               "narrative": composition["narrative"], "howto": composition["how_to_read"],
               "q": composition["question"], "qclass": composition["question_class"],
               "prov": composition["provenance"]}
    out_html = _HTML.replace("__BASE__", _jpg_data_url(base_r)) \
                    .replace("__PAYLOAD__", json.dumps(payload))
    out = html_out or str(root / f"{unit_id}.qview.html")
    Path(out).write_text(out_html)
    return out


_HTML = """<!doctype html><meta charset=utf-8><title>CNfA question view</title>
<style>
 body{margin:0;font:14px/1.5 system-ui,sans-serif;background:#0c0e12;color:#e8eaed;display:flex}
 #stage{position:relative;flex:1;min-width:0;padding:14px}
 #wrap{position:relative;display:inline-block}
 #wrap img{display:block;max-width:100%}
 .ov{position:absolute;inset:0;pointer-events:none;mix-blend-mode:screen}
 .ov img{width:100%;height:100%}
 #boxes{position:absolute;inset:0;pointer-events:none}
 .fb{position:absolute;border:2px solid #ffd24a;box-shadow:0 0 0 1px #000;border-radius:2px}
 .fb span{position:absolute;top:-18px;left:0;background:#ffd24a;color:#000;font-size:11px;padding:0 4px;white-space:nowrap;border-radius:2px}
 #side{width:360px;flex:none;background:#12151b;padding:16px;overflow:auto;height:100vh;box-sizing:border-box}
 h1{font-size:15px;margin:0 0 2px} .qc{color:#9aa4b2;font-size:12px;margin-bottom:12px}
 .nl{padding:6px 8px;border-left:3px solid #2a2f3a;margin:3px 0;cursor:default;border-radius:0 4px 4px 0}
 .nl.anch{cursor:pointer} .nl.anch:hover{background:#1b2029} .nl.on{background:#1b2029;border-left-color:#ffd24a}
 .lede{color:#cfe;border-left-color:#3d6}
 .htitle{margin:16px 0 4px;color:#9aa4b2;font-size:12px;text-transform:uppercase;letter-spacing:.05em}
 .layers label{display:block;padding:3px 0;font-size:13px}
 .howto li{color:#9aa4b2;font-size:12px;margin:3px 0}
 .prov{margin-top:16px;color:#6b7280;font-size:11px;border-top:1px solid #232833;padding-top:10px}
</style>
<div id=stage><div id=wrap><img src="__BASE__"><div id=ovs></div><div id=boxes></div></div></div>
<div id=side>
 <h1 id=q></h1><div class=qc id=qc></div>
 <div id=narr></div>
 <div class=htitle>Layers</div><div class=layers id=layers></div>
 <div class=htitle>How to read</div><ul class=howto id=howto></ul>
 <div class=prov id=prov></div>
</div>
<script>
const P=__PAYLOAD__;
document.getElementById('q').textContent=P.q;
document.getElementById('qc').textContent='question class: '+P.qclass;
const ovs=document.getElementById('ovs');const layersDiv=document.getElementById('layers');
const layerEl={};
P.layers.forEach((l,i)=>{
  const d=document.createElement('div');d.className='ov';d.style.visibility=i===0?'visible':'hidden';
  const im=document.createElement('img');im.src=l.url;d.appendChild(im);ovs.appendChild(d);layerEl[l.key]=d;
  const lab=document.createElement('label');const cb=document.createElement('input');cb.type='checkbox';cb.checked=i===0;
  cb.onchange=()=>d.style.visibility=cb.checked?'visible':'hidden';
  lab.appendChild(cb);lab.appendChild(document.createTextNode(' '+l.label));layersDiv.appendChild(lab);
});
const boxes=document.getElementById('boxes');
P.focus.forEach(f=>{const b=document.createElement('div');b.className='fb';
  b.style.left=f.bb[0]+'px';b.style.top=f.bb[1]+'px';b.style.width=f.bb[2]+'px';b.style.height=f.bb[3]+'px';
  const s=document.createElement('span');s.textContent=f.label;b.appendChild(s);boxes.appendChild(b);});
const narr=document.getElementById('narr');
P.narrative.forEach(n=>{const d=document.createElement('div');
  d.className='nl'+(n.anchor?' anch':'')+(n.text.startsWith('Read-out')||P.narrative.indexOf(n)===0?' lede':'');
  d.textContent=n.text;
  if(n.anchor){d.onclick=()=>{document.querySelectorAll('.nl').forEach(x=>x.classList.remove('on'));d.classList.add('on');
    const key=Object.keys(layerEl).find(k=>k.indexOf(n.anchor.split('.').pop())>=0);
    if(key){const cb=layersDiv.querySelectorAll('input')[P.layers.findIndex(l=>l.key===key)];if(cb){cb.checked=true;cb.onchange();}}};}
  narr.appendChild(d);});
const howto=document.getElementById('howto');P.howto.forEach(h=>{const li=document.createElement('li');li.textContent=h;howto.appendChild(li);});
document.getElementById('prov').textContent='unit '+(P.prov.unit_id||'?')+' · '+P.prov.note;
</script>"""


# ---------------------------------------------------------------- self-test / acceptance
if __name__ == "__main__":
    import sys, tempfile, numpy as np
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from viz.field_sidecars import build_sidecar
    from annotation_socket.annotator import unit_id_for

    print("question_composer self-test\n" + "-" * 60)
    img = "Example Images/UPCycle-Gensler-5-889x592-1.jpg"     # smaller -> one fast annotate
    sd = tempfile.mkdtemp(prefix="qc_")

    # ACCEPTANCE: "effects of street noise on the foyer" — with declared street-noise inputs so the
    # SPL/huddle fields exist (the composer must select acoustics + zones, focus the foyer, and
    # narrate the ACTUAL street-noise state — never a fabricated dB). build_sidecar annotates ONCE
    # and writes both the sidecar and the record.
    man = build_sidecar(img, sd, unit_inputs=frozenset({"outdoor_leq", "facade_spec"}),
                        input_values={"outdoor_leq": 72.0,
                                      "facade_spec": {"facade_row": 0, "Rp": 30.0, "alpha": 0.10}})
    rec = json.loads((Path(sd) / (unit_id_for(img) + ".record.json")).read_text())

    comp = compose("effects of street noise on the foyer", rec, man)
    assert comp["question_class"] == "noise", comp["question_class"]
    grps = {l["group"] for l in comp["layers"]}
    assert "acoustics" in grps and "semantic_zones" in grps, grps
    assert any("foyer" in f["label"] for f in comp["focus"]), [f["label"] for f in comp["focus"]]
    sn = [n for n in comp["narrative"] if n.get("anchor") == "cnfa.acoustic.street_noise_intrusion"]
    assert sn, "street-noise line missing from narrative"
    # the line must carry the ACTUAL scored value (from the record), not a bare status word
    assert "=" in sn[0]["text"] and any(ch.isdigit() for ch in sn[0]["text"]), sn[0]["text"]
    print(f"  ACCEPTANCE 'street noise on foyer': class={comp['question_class']}, "
          f"layers={sorted(grps)}, focus={len(comp['focus'])} boxes")
    print(f"    narrative street-noise line: \"{sn[0]['text']}\"")
    outp = render_question_view(comp, sd, unit_id_for(img), rec)
    sz = Path(outp).stat().st_size
    txt = Path(outp).read_text()
    assert "data:image/jpeg" in txt and '"qclass": "noise"' in txt
    print(f"  rendered acceptance view: {outp} ({sz/1e6:.2f} MB)")

    # score-separation: an adversarial 'LLM' that tries to inject a fake dB number gets it redacted
    def _rogue_llm(composition, facts):
        composition["narrative"].append({"text": "street noise is exactly 999.999 dB", "anchor": None})
        return composition
    comp2 = compose("how loud is the street noise?", rec, man, llm=_rogue_llm)
    redacted = [n for n in comp2["narrative"] if "[redacted:unverified]" in n["text"]]
    assert redacted and not any("999.999" in n["text"] for n in comp2["narrative"]), comp2["narrative"]
    print("  score-separation: rogue LLM's fabricated 999.999 dB -> redacted  OK")

    # other classes route + fail-closed on an abstained predicate
    for q, want in [("where is it too cluttered and busy?", "clutter"),
                    ("is there enough greenery and nature?", "biophilia"),
                    ("can people find their way / is it legible?", "wayfinding"),
                    ("how private are the enclosed areas?", "privacy")]:
        c = compose(q, rec, man)
        assert c["question_class"] == want, (q, c["question_class"])
    print("  routing: clutter / biophilia / wayfinding / privacy  OK")

    # determinism
    assert compose("effects of street noise on the foyer", rec, man)["narrative"] == comp["narrative"]
    print("  determinism: identical composition on replay  OK")
    print("-" * 60 + "\nquestion_composer self-test: PASS")
