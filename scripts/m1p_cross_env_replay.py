#!/usr/bin/env python3
"""
m1p_cross_env_replay — L5 cross-environment replay (methodology P4, Sprint COMP-CORRECT).

Emits the M1' sufficient-statistic digest for EVERY bound predicate over a fixed image list and
writes them to a JSON file tagged with the environment. Run on BOTH machines over byte-identical
images, then diff the two JSONs: any digest mismatch is a genuine environment sensitivity that must
be fixed (coarser canonical rounding for that statistic) BEFORE any GREEN conversation.

Mac usage (from the repo root):
    cd /Users/davidusa/REPOS/Image_Tagger_dk_latest
    PYTHONPATH=. python3 scripts/m1p_cross_env_replay.py --env mac \
        --out docs/M1P_DIGESTS_MAC_2026-07-19.json
Sandbox usage:
    cd /home/claude && python3 scripts/m1p_cross_env_replay.py --env sandbox \
        --out committee/M1P_DIGESTS_SANDBOX_2026-07-19.json
Compare:
    python3 scripts/m1p_cross_env_replay.py --compare A.json B.json
"""
import argparse, hashlib, json, sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, "/home/claude")

SMOKE_SET = [  # repo-relative; byte-identity is checked via sha256 of the file itself
    "Example Images/50-day-street-offices-norwalk-1200x1165-compact.jpg",
    "Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg",
    "Example Images/korridor.jpg",
    "Example Images/Office-Grade-1-1536x838.jpg",
    "Example Images/bede-offices-sofia-6-1200x800-compact.jpg",
    "Example Images/heb-digital-and-favor-delivery-eastside-tech-hub-austin-6.jpg",
    "Example Images/UPCycle-Gensler-5-889x592-1.jpg",
]


def emit_all(env: str, out_path: str):
    from annotation_socket import m1_prime as MP
    result = {"env": env, "stats_version": MP.STATS_VERSION, "images": {}}
    for rel in SMOKE_SET:
        p = Path(rel)
        if not p.exists():
            result["images"][rel] = {"error": "missing"}
            continue
        img_sha = hashlib.sha256(p.read_bytes()).hexdigest()
        img = MP.load_for_m1p(str(p))
        digests, stats = {}, {}
        for pid, (ac, params) in sorted(MP.M1P_BINDINGS.items()):
            try:
                blk = MP.emit(ac, img, **params)
                digests[pid] = blk["digest"]
                stats[pid] = blk["stats"]          # full stats so mismatch DELTAS are quantifiable
            except Exception as e:
                digests[pid] = f"ERROR:{type(e).__name__}"
        # decode fingerprint: catches libjpeg version differences (decoded PIXELS differing while
        # file bytes match — the korridor.jpg L5 finding, 2026-07-19)
        import hashlib as _h
        decode_sha = _h.sha256(np.ascontiguousarray(img).tobytes()).hexdigest()
        result["images"][rel] = {"image_sha256": img_sha, "decoded_sha256": decode_sha,
                                 "digests": digests, "stats": stats}
    Path(out_path).write_text(json.dumps(result, indent=1, sort_keys=True))
    n = sum(len(v.get("digests", {})) for v in result["images"].values())
    print(f"[{env}] wrote {n} digests over {len(SMOKE_SET)} images -> {out_path}")


def compare(a_path: str, b_path: str) -> int:
    A, B = json.loads(Path(a_path).read_text()), json.loads(Path(b_path).read_text())
    bad = 0
    for rel in sorted(set(A["images"]) | set(B["images"])):
        ia, ib = A["images"].get(rel, {}), B["images"].get(rel, {})
        if ia.get("image_sha256") != ib.get("image_sha256"):
            print(f"BYTES DIFFER (not comparable): {rel}")
            bad += 1
            continue
        if ia.get("decoded_sha256") and ib.get("decoded_sha256") and \
                ia["decoded_sha256"] != ib["decoded_sha256"]:
            print(f"DECODE DIFFERS (libjpeg/platform): {rel} — all downstream mismatches expected")
        for pid in sorted(set(ia.get("digests", {})) | set(ib.get("digests", {}))):
            da, db = ia.get("digests", {}).get(pid), ib.get("digests", {}).get(pid)
            if da != db:
                bad += 1
                deltas = ""
                sa, sb = ia.get("stats", {}).get(pid), ib.get("stats", {}).get(pid)
                if sa and sb:
                    ds = []
                    for k in sa:
                        va, vb = sa.get(k), sb.get(k)
                        if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and va != vb:
                            ds.append(f"{k}: {va} vs {vb}")
                    deltas = ("  deltas: " + "; ".join(ds[:5])) if ds else "  (list/array-level diff)"
                print(f"DIGEST MISMATCH: {rel} :: {pid}\n{deltas}")
    print("L5 RESULT:", "FAIL — environment sensitivity found" if bad else
          "PASS — all digests identical across environments")
    return bad


# Per-stat cross-environment tolerances (set 2026-07-19 from the MEASURED Mac-arm64 vs sandbox-x86
# deltas on byte-identical decodes: entropy ~1e-4, D ~2e-4, R2 ~3e-5, edge counts <=0.15% rel).
# STRICT digest equality remains the same-machine rule (verify.py); these apply ONLY to
# cross-machine L5 comparison. A stat outside its tolerance = genuine environment sensitivity.
CROSS_ENV_TOL = {
    "entropy_norm": 0.005, "D": 0.005, "R2": 0.002, "slope": 0.005, "intercept": 0.01,
    "r2": 0.002, "mean_mag_on_edges": 0.002, "global_bpp": 0.001, "global_mean": 0.01,
    "global_std": 0.01, "bright_fraction": 0.001, "integration_norm": 0.02,
    "connectivity_norm": 0.02, "cell_m": 0.005, "mismatch_rel_count": 0.005,  # 0.5% for counts
}
COUNT_KEYS = {"n_edge_px", "edge_px", "free_cells", "n_tiles"}


def compare_tolerant(a_path: str, b_path: str) -> int:
    """Cross-machine verdict: strict-digest pass OR every differing numeric stat within its
    declared tolerance -> WITHIN_TOL; anything beyond -> EXCEEDS (a real sensitivity)."""
    A, B = json.loads(Path(a_path).read_text()), json.loads(Path(b_path).read_text())
    exceeds = 0
    for rel in sorted(set(A["images"]) & set(B["images"])):
        ia, ib = A["images"][rel], B["images"][rel]
        if ia.get("image_sha256") != ib.get("image_sha256"):
            print(f"BYTES DIFFER: {rel}"); exceeds += 1; continue
        decode_ok = ia.get("decoded_sha256") == ib.get("decoded_sha256")
        for pid in sorted(set(ia.get("digests", {})) & set(ib.get("digests", {}))):
            if ia["digests"][pid] == ib["digests"][pid]:
                continue
            sa, sb = ia.get("stats", {}).get(pid), ib.get("stats", {}).get(pid)
            if not (sa and sb):
                print(f"EXCEEDS (no stats to compare): {rel} :: {pid}"); exceeds += 1; continue
            over = []
            for k in sa:
                va, vb = sa.get(k), sb.get(k)
                if not (isinstance(va, (int, float)) and isinstance(vb, (int, float))):
                    continue
                if k in COUNT_KEYS:
                    rel_d = abs(va - vb) / max(abs(va), 1)
                    if rel_d > CROSS_ENV_TOL["mismatch_rel_count"]:
                        over.append(f"{k}: {va} vs {vb} (rel {rel_d:.4f})")
                elif k in CROSS_ENV_TOL:
                    if abs(va - vb) > CROSS_ENV_TOL[k]:
                        over.append(f"{k}: {va} vs {vb} (|d|={abs(va-vb):.5g} > {CROSS_ENV_TOL[k]})")
            tag = " [decode-differs]" if not decode_ok else ""
            if over:
                exceeds += 1
                print(f"EXCEEDS TOL{tag}: {rel} :: {pid}\n    " + "; ".join(over[:4]))
            else:
                print(f"within tol{tag}: {rel} :: {pid}")
    print("L5 TOLERANT RESULT:", f"{exceeds} genuine sensitivities" if exceeds
          else "PASS — all cross-env deltas within declared tolerances")
    return exceeds


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--compare", nargs=2, metavar=("A", "B"))
    ap.add_argument("--compare-tol", nargs=2, metavar=("A", "B"))
    args = ap.parse_args()
    if args.compare:
        sys.exit(1 if compare(*args.compare) else 0)
    if args.compare_tol:
        sys.exit(1 if compare_tolerant(*args.compare_tol) else 0)
    if not (args.env and args.out):
        ap.error("need --env and --out (or --compare A B)")
    emit_all(args.env, args.out)
