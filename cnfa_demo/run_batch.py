#!/usr/bin/env python3
"""Batch: run the pipeline on every example image; write per-image outputs,
a cross-image scalar matrix (CSV), and a compact contact sheet."""
import sys, os, glob, json, unicodedata, re
sys.path.insert(0, "/home/claude")
import numpy as np, cv2
import cnfa_algs as ca
from cnfa_demo.run_demo import run

SRC = "/mnt/user-data/uploads/Image_Tagger_dk_latest/example images"
OUT = "/home/claude/cnfa_demo/batch_outputs"
os.makedirs(OUT, exist_ok=True)

def slug(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "_", os.path.splitext(s)[0]).strip("_")
    return s[:40]

rows = {}
order = []
for path in sorted(glob.glob(os.path.join(SRC, "*"))):
    name = slug(os.path.basename(path))
    img = cv2.imread(path)
    if img is None:
        print("SKIP (unreadable):", path); continue
    # normalize size: max dim 900 (real photos are big; keeps runtime sane)
    scale = 900 / max(img.shape[:2])
    if scale < 1:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    tmp = f"{OUT}/_in_{name}.png"
    cv2.imwrite(tmp, img)
    try:
        results = run(tmp, OUT, seats=None, upscale=1)
        rows[name] = {r.key: r.scalar for r in results}
        rows[name]["_conf_notes"] = ""
        order.append(name)
    except Exception as e:
        print("FAIL", name, "->", repr(e))
        rows[name] = {"_error": str(e)}

# ---- scalar matrix CSV
keys = ["cnfa.spatial.enclosure_index", "cnfa.spatial.prospect",
        "spatial.isovist_openness_plan", "cnfa.spatial.prospect_to_refuge_ratio",
        "acoustic_absorption_proxy", "glare-risk", "cnfa.light.warm_vs_cool_ratio",
        "cnfa.light.brightness_variance", "cnfa.fluency.processing_load_proxy",
        "cnfa.fluency.color_palette_entropy", "cnfa.fractal_dimension",
        "cnfa.cognitive.landmark_salience", "cnfa.fluency.symmetry_score_horizontal"]
import csv
with open(f"{OUT}/batch_scalar_matrix.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["image"] + keys)
    for name in order:
        w.writerow([name] + [None if rows[name].get(k) is None else round(rows[name][k], 3)
                             for k in keys])
print("\nwrote batch_scalar_matrix.csv with", len(order), "images")

# ---- contact sheet: input | plane seg | tierB openness for each image
tiles = []
for name in order:
    base = cv2.imread(f"{OUT}/_in_{name}.png")
    h = 240; wpx = int(base.shape[1] * h / base.shape[0])
    t1 = ca.annotate_title(cv2.resize(base, (wpx, h)), name[:34])
    diag = cv2.imread(f"{OUT}/{('_in_' + name)}_0_diagnostics.png")
    plan = cv2.imread(f"{OUT}/{('_in_' + name)}_2_tierB_plan.png")
    t2 = ca.annotate_title(cv2.resize(diag, (int(diag.shape[1]*h/diag.shape[0]), h)), "diagnostics")
    t3 = ca.annotate_title(cv2.resize(plan, (int(plan.shape[1]*h/plan.shape[0]), h)), "inferred-plan fields")
    tiles += [t1, t2, t3]
cv2.imwrite(f"{OUT}/batch_contact_sheet.png", ca.gallery(tiles, cols=3))
print("wrote batch_contact_sheet.png")
