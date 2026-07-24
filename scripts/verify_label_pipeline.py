#!/usr/bin/env python3
"""verify_pipeline.py — end-to-end check of the label pipeline with NO real corpus.

1. Synthesise a manifest.csv shaped like the real one (interiors + A/B pairs with notes).
2. Run build_label_design.py -> design.json; assert schema is valid and console-consumable
   (every pair/anchor/gold key is an item; graphs connected; gold answers legal).
3. Simulate crowd judgments from a KNOWN latent ground truth (good workers + gold-failing bad
   workers + ties) in the console's CSV schema.
4. Run aggregate_labels.py -> human_labels.csv; assert:
     - bad workers are dropped by gold QC,
     - recovered BT scores correlate strongly with the ground truth (Spearman rho),
     - Likert means recover the planted anchor means,
     - output schema matches corpus_L6/human_labels.csv.

Exit 0 = all checks pass.
"""
import os, sys, csv, json, tempfile, subprocess, random, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FAILS = []


def check(cond, msg):
    print(("  ok  " if cond else " FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def spearman(a, b):
    ar = np.argsort(np.argsort(a)); br = np.argsort(np.argsort(b))
    ar = ar - ar.mean(); br = br - br.mean()
    return float((ar @ br) / (np.sqrt(ar @ ar) * np.sqrt(br @ br) + 1e-12))


def synth_manifest(path, n_interiors=60, n_pairs=20):
    rng = random.Random(1)
    rows = [["filename", "category", "pair_id", "pair_expected_better", "notes"]]
    for i in range(n_interiors):
        rows.append([f"interiors/int_{i:03d}.png", "interiors", "", "unknown",
                     "canonical PNG smoke sample interior"])
    manips = [("daylight brightness", "restorative"), ("clutter busy complexity", "clutter"),
              ("ceiling openness volume", "openness"), ("blind corner barrier mystery", "mystery"),
              ("refuge shelter vantage", "refuge")]
    for p in range(n_pairs):
        pid = f"pair_{p:04d}"
        note, _ = manips[p % len(manips)]
        better = rng.choice(["A", "B"])
        rows.append([f"pairs/pp_{p:04d}_A_base.png", "pairs", pid, better, f"A/B A of {pid}: manip={note}"])
        rows.append([f"pairs/pp_{p:04d}_B_mod.png", "pairs", pid, better, f"A/B B of {pid}: manip={note}"])
    with open(path, "w", newline="") as f:
        csv.writer(f).writerows(rows)


def davidson_p(di, dj, nu):
    eij, eji = math.exp(di), math.exp(dj)
    em = nu * math.exp((di + dj) / 2)
    D = eij + eji + em
    return eij / D, eji / D, em / D  # pL, pR, pT


def simulate_judgments(design, out_csv, seed=3):
    rng = random.Random(seed)
    items = list(design["items"].keys())
    # ground-truth latent theta per construct per item
    constructs = design["construct_order"]
    theta = {c: {it: rng.gauss(0, 1) for it in items} for c in constructs}
    cols = ["worker_id", "session_id", "platform", "study_id", "kind", "pair_id", "construct",
            "left_item", "right_item", "display_flip", "chosen_side", "chosen_item", "response",
            "confidence", "rt_ms", "fast_attempts", "too_slow", "is_gold", "gold_answer",
            "gold_pass", "item", "likert_key", "ua_desktop", "ts_utc"]
    rows = []
    n_good, n_bad = 24, 4
    nu = 0.3
    # planted Likert means per key (constant across items for a checkable target)
    likert_keys = {"prs_away": 5.0, "prs_fascin": 4.0, "affect_val": 5.5, "affect_aro": 3.0}

    def emit_pair(worker, p, is_gold=False, gold_answer=""):
        c = p["construct"]; li, ri = p["left"], p["right"]
        if worker_is_bad[worker]:
            out = rng.choice(["L", "R", "tie"])  # random -> fails gold
        elif is_gold:
            # gold items are consensus-obvious: a good worker answers correctly ~95%
            ga = (gold_answer or "").upper()
            correct = "tie" if ga == "TIE" else ("L" if ga == "L" else "R")
            out = correct if rng.random() < 0.95 else rng.choice([x for x in ["L", "R", "tie"] if x != correct])
        else:
            pL, pR, pT = davidson_p(theta[c][li], theta[c][ri], nu)
            out = np.random.choice(["L", "R", "tie"], p=[pL, pR, pT])
        chosen = li if out == "L" else (ri if out == "R" else "")
        rows.append({**{k: "" for k in cols}, "worker_id": worker, "kind": "pair",
                     "pair_id": p.get("pair_id", ""), "construct": c, "left_item": li, "right_item": ri,
                     "chosen_side": out.upper() if out != "tie" else "TIE",
                     "chosen_item": chosen, "response": out, "rt_ms": "2500",
                     "is_gold": "1" if is_gold else "", "gold_answer": gold_answer,
                     "ua_desktop": "1", "ts_utc": "2026-07-23T00:00:00Z"})

    worker_is_bad = {}
    workers = [f"w{g}" for g in range(n_good)] + [f"b{g}" for g in range(n_bad)]
    for w in workers:
        worker_is_bad[w] = w.startswith("b")

    real_pairs = [p for p in design["pairs"]]
    golds = design["gold"]
    for w in workers:
        # each worker does a sample of pairwise trials + all golds + likert on anchors
        sample = rng.sample(real_pairs, min(len(real_pairs), 140))
        for p in sample:
            emit_pair(w, p)
        for g in golds:
            emit_pair(w, {"pair_id": g["pair_id"], "construct": g["construct"],
                          "left": g["left"], "right": g["right"]},
                      is_gold=True, gold_answer=g["answer"].upper())
        for it in design["anchor"]:
            for key, mu in likert_keys.items():
                val = max(1, min(7, round(rng.gauss(mu, 1.0)))) if not worker_is_bad[w] else rng.randint(1, 7)
                rows.append({**{k: "" for k in cols}, "worker_id": w, "kind": "likert",
                             "item": it, "likert_key": key, "response": str(val),
                             "ua_desktop": "1", "ts_utc": "2026-07-23T00:00:00Z"})
    with open(out_csv, "w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=cols); wr.writeheader()
        for r in rows:
            wr.writerow(r)
    return theta, likert_keys


def main():
    tmp = tempfile.mkdtemp(prefix="label_pipeline_verify_")
    manifest = os.path.join(tmp, "manifest.csv")
    design_path = os.path.join(tmp, "design.json")
    judgments = os.path.join(tmp, "judgments.csv")
    labels = os.path.join(tmp, "human_labels.csv")

    print("== build design ==")
    synth_manifest(manifest)
    rc = subprocess.run([sys.executable, os.path.join(HERE, "build_label_design.py"),
                         "--manifest", manifest, "--out", design_path,
                         "--comparisons-per-image", "8", "--max-singletons", "0",
                         "--anchor-n", "10", "--gold-n", "5"], capture_output=True, text=True)
    print(rc.stdout.strip()); print(rc.stderr.strip(), file=sys.stderr)
    check(rc.returncode == 0, "build_label_design exits 0")
    design = json.load(open(design_path))
    # schema checks
    items = design["items"]
    check(all(p["left"] in items and p["right"] in items for p in design["pairs"]),
          "all pair keys exist in items")
    check(all(k in items for k in design["anchor"]), "all anchor keys exist in items")
    check(all(g["answer"] in ("L", "R", "tie") for g in design["gold"]), "gold answers legal")
    check(design["construct_order"] == ["clutter", "openness", "restorative", "mystery", "refuge", "preference"],
          "construct_order matches console")
    sidecar = json.load(open(design_path + ".sidecar.json"))
    check(all(v["connected"] for v in sidecar["connectivity"].values()),
          "every construct's comparison graph is connected")

    print("\n== simulate + aggregate ==")
    theta, likert_keys = simulate_judgments(design, judgments)
    rc = subprocess.run([sys.executable, os.path.join(HERE, "aggregate_labels.py"), judgments,
                         "--out", labels, "--gold-floor", "0.75", "--n-boot", "80"],
                        capture_output=True, text=True)
    print(rc.stdout.strip()); print(rc.stderr.strip(), file=sys.stderr)
    check(rc.returncode == 0, "aggregate_labels exits 0")

    # QC: all 4 bad workers dropped (good workers may occasionally miss the floor by chance)
    import re as _re
    m = _re.search(r"kept=(\d+) dropped=(\d+)", rc.stdout)
    kept_n, dropped_n = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    bad_all_dropped = all(f"b{g}:" in rc.stdout for g in range(4))
    check(bad_all_dropped and kept_n >= 20 and dropped_n >= 4,
          f"gold QC dropped all bad workers (kept={kept_n}, dropped={dropped_n})")

    # load labels, check recovery per construct
    lab = list(csv.DictReader(open(labels)))
    header_ok = set(["filename", "construct", "human_score", "ci_low", "ci_high", "n_judgments", "agreement"])
    check(set(lab[0].keys()) == header_ok, "human_labels header matches schema")

    rhos = []
    for con in ["clutter", "openness", "restorative", "mystery", "refuge"]:
        crows = [r for r in lab if r["construct"] == con]
        if len(crows) < 5:
            continue
        gt = np.array([theta[con][r["filename"]] for r in crows])
        est = np.array([float(r["human_score"]) for r in crows])
        rho = spearman(gt, est)
        rhos.append((con, rho))
        check(rho > 0.6, f"{con}: recovered scores track ground truth (rho={rho:.2f})")

    # Likert recovery
    lik = [r for r in lab if r["construct"].startswith("likert:")]
    ok_lik = True
    for key, mu in likert_keys.items():
        vals = [float(r["human_score"]) for r in lik if r["construct"] == f"likert:{key}"]
        if vals:
            m = np.mean(vals)
            if abs(m - mu) > 0.7:
                ok_lik = False
                print(f"    likert {key}: recovered {m:.2f} vs planted {mu}")
    check(ok_lik, "Likert means recover planted anchor means (±0.7)")

    print("\n" + ("ALL CHECKS PASSED" if not FAILS else f"{len(FAILS)} CHECK(S) FAILED"))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
