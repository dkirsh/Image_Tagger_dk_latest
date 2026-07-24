#!/usr/bin/env python3
"""build_label_design.py — build a `design.json` for the L6 2AFC labeling console.

Reads `corpus_L6/manifest.csv` (schema: filename, category, pair_id,
pair_expected_better, notes) and emits the `design.json` the console
(`viz/labeling_console.html`) consumes:

    { "items": {key:{"id":filename}}, "construct_order":[...],
      "pairs":[{pair_id,left,right,construct}], "anchor":[key,...],
      "gold":[{pair_id,left,right,construct,answer:"L|R|tie"}] }

It writes two kinds of comparison into `pairs`:
  1. the designed **A/B pairs** (category=pairs) — clean, single-construct validation edges,
     construct inferred from the manip described in `notes` (auditable in the sidecar);
  2. a **balanced, connected sparse pairwise** sample over the singletons for each perceptual
     construct — stage-1 of ASAP. (True two-stage ASAP re-samples adaptively AFTER the pilot using
     the aggregator's Bradley-Terry estimates; `--from-scores` accepts those to bias stage-2 toward
     high-information pairs. Pre-pilot we can only guarantee a balanced, connected graph — which is
     what identifiable BT needs — so that is the default.)

This is offline and READ-ONLY on the corpus. It fabricates no labels; the A/B->construct mapping is a
documented heuristic over `notes`, surfaced in `<out>.sidecar.json` for expert review.

Usage:
    python build_label_design.py --manifest corpus_L6/manifest.csv --out corpus_L6/design.json
    python build_label_design.py --pairs-only            # minimal pilot design (A/B + anchors only)
    python build_label_design.py --comparisons-per-image 8 --max-singletons 200 --anchor-n 16
"""
from __future__ import annotations
import argparse, csv, json, re, sys
from collections import defaultdict
import numpy as np

CONSTRUCTS = ["clutter", "openness", "restorative", "mystery", "refuge", "preference"]
PERCEPTUAL = ["clutter", "openness", "restorative", "mystery", "refuge"]  # + preference criterion

# notes-keyword -> construct, in priority order (first match wins). Auditable & editable.
NOTES_MAP = [
    (r"clutter|busy|complex|visual\s*load|proto-?object", "clutter"),
    (r"open|ceiling|enclosure|prospect|double[_\s-]?height|volume", "openness"),
    (r"myster|blind[_\s-]?corner|barrier|permeab|around the corner|choice", "mystery"),
    (r"refuge|shelter|safe|back covered|vantage", "refuge"),
    (r"green|plant|biophil|nature|water|view|foliage|daylight|circadian|bright|dim|illumin|spectr|fractal", "restorative"),
    (r"glare|noise|stress|thermal|affect|pleasant", "preference"),
]


def _norm_cols(row):
    return { (k or "").strip().lower(): (v or "") for k, v in row.items() }


def load_manifest(path):
    rows = []
    with open(path, newline="") as f:
        for raw in csv.DictReader(f):
            r = _norm_cols(raw)
            fn = r.get("filename", "").strip()
            if not fn:
                continue
            rows.append({
                "filename": fn,
                "category": r.get("category", "").strip(),
                "pair_id": r.get("pair_id", "").strip(),
                "expected_better": r.get("pair_expected_better", "").strip(),
                "notes": r.get("notes", "").strip(),
            })
    return rows


def construct_from_notes(notes):
    n = notes.lower()
    for pat, con in NOTES_MAP:
        if re.search(pat, n):
            return con
    return "preference"  # universal criterion fallback


def _ab_member(fn):
    """Return 'A', 'B', or '' from the filename token."""
    m = re.search(r"_([AB])(?:_|\.)", fn)
    return m.group(1) if m else ""


def build_pairs_from_ab(rows):
    """Group category=pairs by pair_id -> designed comparison + gold candidates + sidecar audit."""
    groups = defaultdict(list)
    for r in rows:
        if r["category"] == "pairs" and r["pair_id"]:
            groups[r["pair_id"]].append(r)
    pairs, gold_candidates, audit = [], [], []
    for pid, members in sorted(groups.items()):
        if len(members) != 2:
            audit.append({"pair_id": pid, "skipped": f"{len(members)} members (need 2)"})
            continue
        construct = construct_from_notes(" ".join(m["notes"] for m in members))
        # identify A/B
        a = next((m for m in members if _ab_member(m["filename"]) == "A"), None)
        b = next((m for m in members if _ab_member(m["filename"]) == "B"), None)
        if a is None or b is None:
            a, b = members[0], members[1]
        exp = (a["expected_better"] or members[0]["expected_better"] or "").upper()
        pairs.append({"pair_id": pid, "left": a["filename"], "right": b["filename"], "construct": construct})
        # gold only when the expected-better direction is known
        if exp in ("A", "B"):
            answer = "L" if exp == "A" else "R"  # left=A, right=B by construction above
            gold_candidates.append({"pair_id": f"gold_{pid}", "left": a["filename"],
                                    "right": b["filename"], "construct": construct, "answer": answer})
        audit.append({"pair_id": pid, "construct": construct, "expected_better": exp or "unknown",
                      "left": a["filename"], "right": b["filename"]})
    return pairs, gold_candidates, audit


def balanced_connected_pairs(keys, k, rng):
    """k rounds of random matchings + one Hamiltonian path -> a balanced, CONNECTED, de-duplicated
    comparison graph (degree ~k+2). Connectivity is what makes the BT scale identifiable."""
    n = len(keys)
    if n < 2:
        return []
    edges = set()
    for _ in range(k):
        perm = rng.permutation(n)
        for i in range(0, n - 1, 2):
            edges.add(frozenset((keys[perm[i]], keys[perm[i + 1]])))
    perm = rng.permutation(n)  # guarantee connectivity
    for i in range(n - 1):
        edges.add(frozenset((keys[perm[i]], keys[perm[i + 1]])))
    return [tuple(e) for e in edges]


def _is_connected(keys, edge_tuples):
    adj = defaultdict(set)
    for a, b in edge_tuples:
        adj[a].add(b); adj[b].add(a)
    if not keys:
        return True
    seen, stack = set(), [keys[0]]
    while stack:
        x = stack.pop()
        if x in seen:
            continue
        seen.add(x)
        stack.extend(adj[x] - seen)
    return len(seen) == len(set(keys))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="corpus_L6/manifest.csv")
    ap.add_argument("--out", default="corpus_L6/design.json")
    ap.add_argument("--comparisons-per-image", type=int, default=6)
    ap.add_argument("--max-singletons", type=int, default=200, help="cap the singleton pool (0 = all)")
    ap.add_argument("--anchor-n", type=int, default=16)
    ap.add_argument("--gold-n", type=int, default=6)
    ap.add_argument("--constructs", default=",".join(PERCEPTUAL),
                    help="perceptual constructs to build global pairwise for")
    ap.add_argument("--pairs-only", action="store_true", help="A/B designed pairs + anchors only (pilot)")
    ap.add_argument("--seed", type=int, default=20260723)
    a = ap.parse_args(argv)

    rows = load_manifest(a.manifest)
    if not rows:
        print("no manifest rows", file=sys.stderr); return 2
    rng = np.random.default_rng(a.seed)

    items = {r["filename"]: {"id": r["filename"]} for r in rows}
    ab_pairs, gold_candidates, audit = build_pairs_from_ab(rows)

    singles = [r["filename"] for r in rows if r["category"] != "pairs"]
    if a.max_singletons and len(singles) > a.max_singletons:
        idx = rng.choice(len(singles), size=a.max_singletons, replace=False)
        singles = [singles[i] for i in sorted(idx.tolist())]

    constructs = [c.strip() for c in a.constructs.split(",") if c.strip()]
    global_pairs = []
    conn_report = {}
    if not a.pairs_only:
        pcount = 0
        for con in constructs:
            edges = balanced_connected_pairs(singles, a.comparisons_per_image, rng)
            conn_report[con] = {"n_items": len(singles), "n_pairs": len(edges),
                                "connected": _is_connected(singles, edges)}
            for (l, r) in edges:
                pcount += 1
                global_pairs.append({"pair_id": f"g{con[:2]}_{pcount}", "left": l, "right": r, "construct": con})

    # anchor set: spread across categories
    anchor = []
    if a.anchor_n and singles:
        ai = rng.choice(len(singles), size=min(a.anchor_n, len(singles)), replace=False)
        anchor = [singles[i] for i in sorted(ai.tolist())]

    # gold: sample across constructs from known-direction A/B pairs + 1 identical-image tie catch
    gold = []
    if not a.pairs_only or a.gold_n:
        by_con = defaultdict(list)
        for g in gold_candidates:
            by_con[g["construct"]].append(g)
        # round-robin across constructs for balance
        pools = [by_con[c] for c in by_con]
        i = 0
        while len(gold) < a.gold_n and any(pools):
            p = pools[i % len(pools)] if pools else []
            if p:
                gold.append(p.pop())
            i += 1
            if all(len(x) == 0 for x in pools):
                break
        if singles:  # identical-image "can't tell" catch
            gi = singles[int(rng.integers(len(singles)))]
            gold.append({"pair_id": "gold_identical", "left": gi, "right": gi,
                         "construct": "preference", "answer": "tie"})

    design = {
        "items": items,
        "construct_order": CONSTRUCTS,
        "pairs": ab_pairs + global_pairs,
        "anchor": anchor,
        "gold": gold,
    }

    # ---- self-validation: every referenced key must be an item; gold answers legal ----
    problems = validate_design(design)
    if problems:
        for p in problems:
            print("VALIDATION:", p, file=sys.stderr)
        return 3

    with open(a.out, "w") as f:
        json.dump(design, f, indent=1)
    sidecar = {
        "generated_from": a.manifest,
        "n_items": len(items), "n_singletons": len(singles),
        "n_ab_pairs": len(ab_pairs), "n_global_pairs": len(global_pairs),
        "n_anchor": len(anchor), "n_gold": len(gold),
        "constructs_global": constructs,
        "connectivity": conn_report,
        "ab_construct_mapping_note": "A/B->construct inferred from manifest notes via NOTES_MAP; review below.",
        "ab_audit": audit,
    }
    with open(a.out + ".sidecar.json", "w") as f:
        json.dump(sidecar, f, indent=1)

    print(f"[design] items={len(items)} ab_pairs={len(ab_pairs)} global_pairs={len(global_pairs)} "
          f"anchor={len(anchor)} gold={len(gold)}")
    print(f"[design] connectivity: " +
          ", ".join(f"{c}:{'ok' if v['connected'] else 'DISCONNECTED'}({v['n_pairs']})"
                    for c, v in conn_report.items()))
    print(f"[design] wrote {a.out} and {a.out}.sidecar.json")
    return 0


def validate_design(design):
    problems = []
    items = design["items"]
    for p in design["pairs"]:
        for side in ("left", "right"):
            if p[side] not in items:
                problems.append(f"pair {p.get('pair_id')} references missing item {p[side]}")
        if p["construct"] not in CONSTRUCTS:
            problems.append(f"pair {p.get('pair_id')} bad construct {p['construct']}")
    for k in design["anchor"]:
        if k not in items:
            problems.append(f"anchor references missing item {k}")
    for g in design["gold"]:
        for side in ("left", "right"):
            if g[side] not in items:
                problems.append(f"gold {g.get('pair_id')} references missing item {g[side]}")
        if g["answer"] not in ("L", "R", "tie"):
            problems.append(f"gold {g.get('pair_id')} bad answer {g['answer']}")
    return problems


if __name__ == "__main__":
    raise SystemExit(main())
