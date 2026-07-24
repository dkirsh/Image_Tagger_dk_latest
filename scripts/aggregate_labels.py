#!/usr/bin/env python3
"""aggregate_labels.py — turn console judgment CSVs into corpus_L6/human_labels.csv.

Input: one or more CSVs exported/streamed by `viz/labeling_console.html`
(columns include: worker_id, kind, construct, left_item, right_item, chosen_item,
response, is_gold, gold_answer, gold_pass, item, likert_key, rt_ms, too_slow ...).

Pipeline:
  1. Worker QC — drop workers below the gold-accuracy floor (computed from the gold trials, or the
     console's own gold_pass), and optionally drop too-slow/flagged rows.
  2. Pairwise -> per-construct **regularized Davidson–Bradley–Terry**: a tie-aware BT model
     ("can't tell" = a genuine tie, modelled, not dropped) with an L2 (ridge) prior so the scale is
     identifiable and separation-safe. Yields a latent quality score per image per construct.
  3. Likert anchor items -> mean + CI per item per Likert key (fixes the BT origin downstream).
  4. CIs via **cluster bootstrap over workers** (the correct unit of resampling for crowd data).

Output: `corpus_L6/human_labels.csv` with
  `filename, construct, human_score, ci_low, ci_high, n_judgments, agreement`
— exactly the file S4 calibration fits every computed attribute against.

Usage:
    python aggregate_labels.py judgments*.csv --out corpus_L6/human_labels.csv
    python aggregate_labels.py j.csv --gold-floor 0.8 --n-boot 200 --drop-too-slow
"""
from __future__ import annotations
import argparse, csv, glob, sys
from collections import defaultdict
import numpy as np

CONSTRUCTS = ["clutter", "openness", "restorative", "mystery", "refuge", "preference"]


# --------------------------------------------------------------------------- #
# IO
# --------------------------------------------------------------------------- #
def load_rows(paths):
    rows = []
    for pat in paths:
        for path in sorted(glob.glob(pat)) or [pat]:
            try:
                with open(path, newline="") as f:
                    for r in csv.DictReader(f):
                        rows.append({(k or "").strip(): (v or "").strip() for k, v in r.items()})
            except FileNotFoundError:
                print(f"warn: no such file {path}", file=sys.stderr)
    return rows


def _truthy(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y", "t")


# --------------------------------------------------------------------------- #
# Worker QC
# --------------------------------------------------------------------------- #
def worker_gold_accuracy(rows):
    """Per worker: accuracy on gold trials (chosen matches gold_answer direction)."""
    hit = defaultdict(int); tot = defaultdict(int)
    for r in rows:
        if r.get("kind") != "pair" or not _truthy(r.get("is_gold")):
            continue
        w = r.get("worker_id", "")
        ga = (r.get("gold_answer") or "").upper()  # L / R / TIE
        outcome = pair_outcome(r)                  # 'L','R','tie'
        tot[w] += 1
        want = "tie" if ga == "TIE" else ga
        if outcome == want:
            hit[w] += 1
    return {w: (hit[w] / tot[w] if tot[w] else None) for w in tot}


def pair_outcome(r):
    """Normalise a pair judgment to 'L' (left item wins), 'R' (right), or 'tie'."""
    resp = (r.get("response") or "").lower()
    chosen = r.get("chosen_item") or ""
    side = (r.get("chosen_side") or "").upper()
    if resp == "tie" or side == "TIE" or chosen == "" and side == "":
        return "tie"
    li, ri = r.get("left_item", ""), r.get("right_item", "")
    if chosen and chosen == li:
        return "L"
    if chosen and chosen == ri:
        return "R"
    if side in ("L", "R"):
        return side
    return "tie"


def filter_workers(rows, gold_floor, drop_too_slow):
    acc = worker_gold_accuracy(rows)
    keep, dropped = set(), {}
    workers = {r.get("worker_id", "") for r in rows}
    for w in workers:
        a = acc.get(w)
        # if no gold seen for a worker, fall back to the console's gold_pass flag if present
        if a is None:
            gp = [r for r in rows if r.get("worker_id") == w and r.get("gold_pass") not in ("", None)]
            a = 1.0 if (gp and all(_truthy(x.get("gold_pass")) for x in gp)) else (0.0 if gp else 1.0)
        if a >= gold_floor:
            keep.add(w)
        else:
            dropped[w] = round(a, 3)
    out = []
    for r in rows:
        if r.get("worker_id", "") not in keep:
            continue
        if drop_too_slow and _truthy(r.get("too_slow")):
            continue
        out.append(r)
    return out, keep, dropped


# --------------------------------------------------------------------------- #
# Davidson–Bradley–Terry (tie-aware), ridge-regularised
# --------------------------------------------------------------------------- #
def fit_davidson_bt(I, J, O, n_items, lam=1.0, iters=600, lr=0.1):
    """I,J: int arrays of item indices; O: +1 left win, -1 right win, 0 tie.
    Returns (beta[n_items], nu). Gradient ascent on the ridge-penalised log-likelihood."""
    beta = np.zeros(n_items)
    t = 0.0  # log nu
    if len(I) == 0:
        return beta, 1.0
    for _ in range(iters):
        ai, aj = beta[I], beta[J]
        nu = np.exp(t)
        eij = np.exp(ai); eji = np.exp(aj); em = nu * np.exp((ai + aj) / 2.0)
        D = eij + eji + em
        pL = eij / D; pR = eji / D; pT = em / D
        # per-comparison partials of the log-likelihood
        isL = (O == 1); isR = (O == -1); isT = (O == 0)
        base_i = pL + 0.5 * pT
        base_j = pR + 0.5 * pT
        gi = isL * (1 - base_i) + isR * (-base_i) + isT * (0.5 - base_i)
        gj = isL * (-base_j) + isR * (1 - base_j) + isT * (0.5 - base_j)
        grad = np.zeros(n_items)
        np.add.at(grad, I, gi)
        np.add.at(grad, J, gj)
        grad -= lam * beta
        gt = np.sum(isT.astype(float) - pT)
        beta += lr * grad / max(1, len(I))
        beta -= beta.mean()               # fix location
        t += lr * gt / max(1, len(I))
        t = float(np.clip(t, -6, 6))
    return beta, float(np.exp(t))


def bt_accuracy(I, J, O, beta):
    """Fraction of non-tie comparisons whose winner matches the fitted order."""
    mask = O != 0
    if not mask.any():
        return ""
    pred = np.sign(beta[I[mask]] - beta[J[mask]])   # +1 left higher
    truth = O[mask]
    # ties in beta (pred==0) count as wrong
    return round(float(np.mean(pred == truth)), 4)


def aggregate_pairwise(rows, constructs, lam, n_boot, seed):
    out = {}   # construct -> {filename: (score, ci_low, ci_high, n)}
    agree = {}
    rng = np.random.default_rng(seed)
    for con in constructs:
        crows = [r for r in rows if r.get("kind") == "pair" and not _truthy(r.get("is_gold"))
                 and r.get("construct") == con]
        if not crows:
            continue
        items = sorted({r["left_item"] for r in crows} | {r["right_item"] for r in crows})
        idx = {f: k for k, f in enumerate(items)}
        I = np.array([idx[r["left_item"]] for r in crows])
        J = np.array([idx[r["right_item"]] for r in crows])
        O = np.array([{"L": 1, "R": -1, "tie": 0}[pair_outcome(r)] for r in crows])
        workers = np.array([r.get("worker_id", "") for r in crows])
        n_by_item = defaultdict(int)
        for r in crows:
            n_by_item[r["left_item"]] += 1; n_by_item[r["right_item"]] += 1

        beta, nu = fit_davidson_bt(I, J, O, len(items), lam=lam)
        agree[con] = bt_accuracy(I, J, O, beta)

        # cluster bootstrap over workers
        uw = np.unique(workers)
        boot = np.full((n_boot, len(items)), np.nan)
        for b in range(n_boot):
            pick = rng.choice(len(uw), size=len(uw), replace=True)
            sel = np.concatenate([np.where(workers == uw[p])[0] for p in pick]) if len(uw) else np.array([], int)
            if len(sel) == 0:
                continue
            bbeta, _ = fit_davidson_bt(I[sel], J[sel], O[sel], len(items), lam=lam, iters=300)
            boot[b] = bbeta
        lo = np.nanpercentile(boot, 2.5, axis=0)
        hi = np.nanpercentile(boot, 97.5, axis=0)
        out[con] = {f: (round(float(beta[k]), 4),
                        round(float(lo[k]), 4) if np.isfinite(lo[k]) else "",
                        round(float(hi[k]), 4) if np.isfinite(hi[k]) else "",
                        n_by_item[f]) for f, k in idx.items()}
    return out, agree


# --------------------------------------------------------------------------- #
# Likert
# --------------------------------------------------------------------------- #
def aggregate_likert(rows):
    """(item, likert_key) -> mean, 95% CI (normal approx), n."""
    acc = defaultdict(list)
    for r in rows:
        if r.get("kind") != "likert":
            continue
        try:
            v = float(r.get("response", ""))
        except ValueError:
            continue
        acc[(r.get("item", ""), r.get("likert_key", ""))].append(v)
    out = {}
    for (item, key), vals in acc.items():
        arr = np.array(vals, float)
        n = len(arr)
        m = float(arr.mean())
        se = float(arr.std(ddof=1) / np.sqrt(n)) if n > 1 else 0.0
        out[(item, key)] = (round(m, 4), round(m - 1.96 * se, 4), round(m + 1.96 * se, 4), n)
    return out


# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="console judgment CSV(s); globs ok")
    ap.add_argument("--out", default="corpus_L6/human_labels.csv")
    ap.add_argument("--gold-floor", type=float, default=0.67, help="min gold accuracy to keep a worker")
    ap.add_argument("--drop-too-slow", action="store_true")
    ap.add_argument("--lam", type=float, default=1.0, help="ridge strength (BT identifiability)")
    ap.add_argument("--n-boot", type=int, default=200)
    ap.add_argument("--constructs", default=",".join(CONSTRUCTS))
    ap.add_argument("--seed", type=int, default=20260723)
    a = ap.parse_args(argv)

    rows = load_rows(a.inputs)
    if not rows:
        print("no judgment rows loaded", file=sys.stderr); return 2
    kept_rows, keep, dropped = filter_workers(rows, a.gold_floor, a.drop_too_slow)
    constructs = [c.strip() for c in a.constructs.split(",") if c.strip()]

    pw, agree = aggregate_pairwise(kept_rows, constructs, a.lam, a.n_boot, a.seed)
    lik = aggregate_likert(kept_rows)

    out_rows = []
    for con, d in pw.items():
        for fn, (score, lo, hi, n) in sorted(d.items()):
            out_rows.append([fn, con, score, lo, hi, n, agree.get(con, "")])
    for (item, key), (m, lo, hi, n) in sorted(lik.items()):
        out_rows.append([item, f"likert:{key}", m, lo, hi, n, ""])

    import os
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["filename", "construct", "human_score", "ci_low", "ci_high", "n_judgments", "agreement"])
        w.writerows(out_rows)

    print(f"[agg] workers kept={len(keep)} dropped={len(dropped)} "
          f"{('(' + ', '.join(f'{k}:{v}' for k,v in list(dropped.items())[:6]) + ')') if dropped else ''}")
    for con in constructs:
        if con in pw:
            print(f"[agg] {con}: {len(pw[con])} items, BT order-accuracy={agree.get(con)}")
    if lik:
        print(f"[agg] likert: {len({k for _,k in lik})} keys over {len({i for i,_ in lik})} anchor items")
    print(f"[agg] wrote {a.out}  ({len(out_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
