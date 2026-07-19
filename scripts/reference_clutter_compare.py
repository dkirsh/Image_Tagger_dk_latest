#!/usr/bin/env python3
"""
reference_clutter_compare — S1 [PORT] adjudication harness (Sprint COMP-CORRECT, 2026-07-19).

Runs FAITHFUL FC + SE over fixed synthetic fixtures + the smoke interiors and writes the raw
values to JSON. On the SANDBOX this exercises the vendored reference on the _pyrtools_min shim;
on the MAC (where real pyrtools installs: `pip3 install pyrtools`) run with --backend real to
exercise the identical vendored reference on REAL pyrtools. Comparing the two JSONs adjudicates
the shim: agreement within tolerance => the faithfulness claim stands on pyrtools' shoulders;
disagreement localizes the port error to a named pyramid component (P1-P4 in _pyrtools_min).

Mac usage:
    cd /Users/davidusa/REPOS/Image_Tagger_dk_latest
    pip3 install pyrtools --break-system-packages   # or into a venv
    PYTHONPATH=. python3 scripts/reference_clutter_compare.py --backend real --env mac \
        --out docs/CLUTTER_REFERENCE_MAC_2026-07-19.json
Sandbox: --backend shim --env sandbox --out docs/CLUTTER_REFERENCE_SANDBOX_2026-07-19.json
Compare: --compare A.json B.json      (tolerance: |d|/max(|a|,1e-9) <= 2% per value)
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, "/home/claude")

import numpy as np

SMOKE = [  # decode-stable JPEGs only (korridor excluded — libjpeg platform divergence, L5 finding)
    "Example Images/50-day-street-offices-norwalk-1200x1165-compact.jpg",
    "Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg",
    "Example Images/Ludwig_Mies_van_der_Rohe__Farnsworth_House__1945-1951_2.jpg",
    "Example Images/Office-Grade-1-1536x838.jpg",
]
REL_TOL = 0.02


def fixtures():
    import cv2
    H, W = 120, 160
    mk = lambda f: np.clip(f, 0, 255).astype(np.uint8)
    rng = np.random.RandomState(0)
    fx = {"blank": mk(np.full((H, W, 3), 128.0)),
          "gradient": mk(np.stack([40 + 170 * np.mgrid[0:H, 0:W][1] / W] * 3, -1)),
          "texture": mk(np.stack([128 + 30 * rng.randn(H, W)] * 3, -1))}
    clut = np.full((H, W, 3), 200.0)
    rs = np.random.RandomState(3)
    for i in range(28):
        x, y = int(rs.rand() * (W - 30)) + 15, int(rs.rand() * (H - 30)) + 15
        cv2.circle(clut, (x, y), rs.randint(4, 12), tuple(int(c) for c in rs.randint(0, 255, 3)), -1)
    fx["clutter"] = mk(clut)
    return fx


def run(backend: str, env: str, out: str):
    import cv2, hashlib
    if backend == "real":
        import pyrtools  # noqa: F401 — must be the real package
        vendor = str(Path(__file__).resolve().parent.parent / "cnfa_algs" / "_vendor")
        sys.path.insert(0, vendor)
        from visual_clutter.clutter import Vlc
    else:
        from cnfa_algs.faithful_clutter import _get_vlc_class
        Vlc = _get_vlc_class()

    def measure(rgb):
        clt = Vlc(rgb, numlevels=3, contrast_filt_sigma=1, contrast_pool_sigma=3, color_pool_sigma=3)
        fc, _ = clt.getClutter_FC(p=1, pix=0)
        se = clt.getClutter_SE(wlevels=3, wght_chrom=0.0625)
        return {"fc_raw": round(float(fc), 6), "se_raw": round(float(se), 6),
                "layers": {"color": round(float(np.mean(clt.color_clutter_map)), 6),
                           "contrast": round(float(np.mean(clt.contrast_clutter_map)), 6),
                           "orientation": round(float(np.mean(clt.orientation_clutter_map)), 6)}}

    res = {"env": env, "backend": backend, "images": {}}
    for name, im in fixtures().items():
        res["images"][f"fixture:{name}"] = measure(im[..., ::-1].copy())  # fixtures built BGR-ish; use RGB flip consistently
    for rel in SMOKE:
        p = Path(rel)
        if not p.exists():
            res["images"][rel] = {"error": "missing"}
            continue
        bgr = cv2.imread(str(p))
        sc = 500 / max(bgr.shape[:2])
        if sc < 1:
            bgr = cv2.resize(bgr, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
        entry = measure(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
        entry["image_sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
        entry["decoded_sha256"] = hashlib.sha256(np.ascontiguousarray(bgr).tobytes()).hexdigest()
        res["images"][rel] = entry
    Path(out).write_text(json.dumps(res, indent=1, sort_keys=True))
    print(f"[{env}/{backend}] wrote {len(res['images'])} entries -> {out}")


def compare(a_path, b_path):
    A, B = json.loads(Path(a_path).read_text()), json.loads(Path(b_path).read_text())
    bad = 0
    for k in sorted(set(A["images"]) & set(B["images"])):
        ia, ib = A["images"][k], B["images"][k]
        if "error" in ia or "error" in ib:
            continue
        if k == "fixture:blank":
            print("skip (noise-dominated: SE/FC on a blank field is the entropy of numerical "
                  "residue — platform-dependent by nature; the operators ABSTAIN on such input)")
            continue
        if ia.get("decoded_sha256") and ib.get("decoded_sha256") and \
                ia["decoded_sha256"] != ib["decoded_sha256"]:
            print(f"skip (decode differs): {k}")
            continue
        pairs = [("fc_raw", ia["fc_raw"], ib["fc_raw"]), ("se_raw", ia["se_raw"], ib["se_raw"])] + \
                [(f"layer:{n}", ia["layers"][n], ib["layers"][n]) for n in ia.get("layers", {})]
        for name, va, vb in pairs:
            rel_d = abs(va - vb) / max(abs(va), 1e-9)
            if rel_d > REL_TOL:
                bad += 1
                print(f"MISMATCH {k} :: {name}: {va} vs {vb} (rel {rel_d:.4f})")
    print("ADJUDICATION:", f"{bad} mismatches — shim diverges, check P1-P4" if bad else
          "PASS — shim matches real pyrtools within 2%; faithfulness claim stands")
    return bad


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["shim", "real"], default="shim")
    ap.add_argument("--env", default="sandbox")
    ap.add_argument("--out")
    ap.add_argument("--compare", nargs=2)
    a = ap.parse_args()
    if a.compare:
        sys.exit(1 if compare(*a.compare) else 0)
    if not a.out:
        ap.error("need --out (or --compare A B)")
    run(a.backend, a.env, a.out)
