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
        digests = {}
        for pid, (ac, params) in sorted(MP.M1P_BINDINGS.items()):
            try:
                digests[pid] = MP.emit(ac, img, **params)["digest"]
            except Exception as e:
                digests[pid] = f"ERROR:{type(e).__name__}"
        result["images"][rel] = {"image_sha256": img_sha, "digests": digests}
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
        for pid in sorted(set(ia.get("digests", {})) | set(ib.get("digests", {}))):
            da, db = ia.get("digests", {}).get(pid), ib.get("digests", {}).get(pid)
            if da != db:
                print(f"DIGEST MISMATCH: {rel} :: {pid}\n  {A['env']}: {da}\n  {B['env']}: {db}")
                bad += 1
    print("L5 RESULT:", "FAIL — environment sensitivity found" if bad else
          "PASS — all digests identical across environments")
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--env", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--compare", nargs=2, metavar=("A", "B"))
    args = ap.parse_args()
    if args.compare:
        sys.exit(1 if compare(*args.compare) else 0)
    if not (args.env and args.out):
        ap.error("need --env and --out (or --compare A B)")
    emit_all(args.env, args.out)
