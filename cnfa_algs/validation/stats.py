"""
cnfa_algs.validation.stats — convergent-validity statistics between
judge ratings (VLM or human) and algorithm scalars.

Reports per attribute:
  - Spearman rho + p (ordinal ratings vs algorithm scalar across images)
  - Kendall tau (robust for small N)
  - judge test-retest stability across repeats (mean SD of ratings)
  - pairwise agreement % (if pairwise data present)
  - localization IoU (if bboxes present, vs algorithm evidence regions)

Interpretation bands (pre-registered, do not move after seeing data):
  rho >= 0.6  -> CONVERGING: operationalization tracks the construct
  0.3 - 0.6   -> WEAK: keep, demote confidence, investigate residuals
  <  0.3      -> FAILING: revise algorithm or reject probe wording
Failing the judge is evidence, not proof: check probe wording, judge
variance, and range restriction before condemning the algorithm.
"""
from __future__ import annotations
import json, sys, csv
import numpy as np
from scipy.stats import spearmanr, kendalltau


def load_matrix(csv_path):
    rows = list(csv.reader(open(csv_path)))
    hdr = rows[0][1:]
    data = {}
    for r in rows[1:]:
        name = r[0].replace("_in_", "")
        data[name] = {k: (float(v) if v not in ("", "None") else None)
                      for k, v in zip(hdr, r[1:])}
    return data


def evaluate(ratings_json, matrix_csv, name_map=None):
    ratings = json.load(open(ratings_json))["ratings"]
    matrix = load_matrix(matrix_csv)
    name_map = name_map or {}
    report = {}
    attrs = sorted({a for v in ratings.values() for a in v})
    for attr in attrs:
        xs, ys, sds = [], [], []
        for img, per_attr in ratings.items():
            mkey = name_map.get(img, img)
            if mkey not in matrix or attr not in per_attr:
                continue
            scal = matrix[mkey].get(attr)
            vals = [o.get("rating") for o in per_attr[attr].get("ordinal", [])
                    if isinstance(o.get("rating"), (int, float))]
            if scal is None or not vals:
                continue
            xs.append(scal)
            ys.append(float(np.mean(vals)))
            sds.append(float(np.std(vals)))
        if len(xs) >= 4:
            rho, p = spearmanr(xs, ys)
            tau, tp = kendalltau(xs, ys)
            band = ("CONVERGING" if rho >= 0.6 else
                    "WEAK" if rho >= 0.3 else "FAILING")
            report[attr] = {"n": len(xs), "spearman_rho": round(float(rho), 3),
                            "p": round(float(p), 4), "kendall_tau": round(float(tau), 3),
                            "judge_mean_sd": round(float(np.mean(sds)), 3) if sds else None,
                            "verdict": band}
        else:
            report[attr] = {"n": len(xs), "verdict": "INSUFFICIENT_N"}
    return report


def iou(a, b):
    ax0, ay0, ax1, ay1 = a; bx0, by0, bx1, by1 = b
    ix = max(0, min(ax1, bx1) - max(ax0, bx0))
    iy = max(0, min(ay1, by1) - max(ay0, by0))
    inter = ix * iy
    union = (ax1-ax0)*(ay1-ay0) + (bx1-bx0)*(by1-by0) - inter
    return inter / union if union > 0 else 0.0


if __name__ == "__main__":
    rep = evaluate(sys.argv[1], sys.argv[2])
    print(json.dumps(rep, indent=2))
