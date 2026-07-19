"""
cnfa_algs.complexity_partition — REGIONALIZED, SEMANTICALLY-SIGNED visual complexity
(David's proposal, 2026-07-19: "partition visual complexity so we can identify which parts of a
room have that attribute to a negative level... rename regions by their semantics").

THE THEORY MOVE. Content-free complexity conflates hedonically opposite things: a D~1.4 fern and a
D~1.4 cable tangle carry the same statistic and opposite valence. Finding DT-1 (2026-07-19) showed
this empirically — the reference Feature Congestion ranks foliage-framed Farnsworth ABOVE a
genuinely cluttered office. The fix is NOT to suppress vegetation in the measure; it is to
PARTITION the complexity field by region content and assign hedonic sign per region:

  region class            evidence gate (declared, heuristic -> AMBER)          hedonic HYPOTHESIS
  biophilic_fractal       green chromaticity + mid-band D (Taylor/Hagerhall     positive (restorative
                          1.15-1.70, R2>=0.90) + organic (non-compact) boundary  inverted-U evidence)
  ordered_structure       low edge density OR strong regularity, any color      neutral->mildly positive
  junk_clutter            complex (high edge/texture) but NOT green-fractal-    negative (search cost,
                          organic: off-band D, broken scaling, or dense micro-  Rosenholtz mechanism)
                          fragments
  neutral                 none of the above                                     unknown

HEDONIC LICENSING: the per-region tags are HYPOTHESES (descriptive), NOT licensed hedonic values —
they do not enter hedonics.py or any aggregate until corpus calibration (the V7 lesson). The global
licensed fractal inverted-U (hedonics: cnfa.fractal_dimension, peak 1.4) is unchanged; this module
gives it a SPATIAL, content-conditioned refinement to be validated at L6.

UPGRADE PATH: the biophilic gate is chromaticity+geometry (deterministic, honest AMBER). When the
Wave-3 pinned segmentation model lands, the gate swaps to true vegetation masks; the architecture
(regionalize -> per-region D -> sign) is unchanged.

Self-test: python3 -m cnfa_algs.complexity_partition
"""
from __future__ import annotations
from typing import Dict, List
import numpy as np
import cv2

try:
    from .attributes import AttributeResult, normalize01, _boxcount_D_r2
    from .clutter_stack import MS_SPATIAL_R, MS_COLOR_R, QUANT_STEP
except Exception:
    from attributes import AttributeResult, normalize01, _boxcount_D_r2  # type: ignore
    from clutter_stack import MS_SPATIAL_R, MS_COLOR_R, QUANT_STEP  # type: ignore

# ---- declared constants (all consumer-visible in extras; corpus refit expected) ----
MIN_ZONE_FRAC = 0.01        # a semantic ZONE is >=1% of the image (bigger than proto-objects)
GREEN_HUE = (35, 90)        # OpenCV hue band for vegetation-green
GREEN_SAT_MIN = 0.15
GREEN_FRAC_GATE = 0.35      # region counts as green-dominated above this fraction
D_BAND = (1.15, 1.70)       # Taylor/Hagerhall-informed mid-band (global licensed peak 1.4)
R2_MIN = 0.90               # below this the box-count scaling is broken -> no fractal claim
EDGE_DENSE = 0.10           # region edge-pixel fraction above which it is "complex"
COMPACT_ORGANIC = 1.8       # boundary roughness (perimeter / equivalent-circle) above = organic
MIN_EDGE_PX_REGION = 60     # below this, D is undefined for the region


def complexity_partition(img_bgr) -> AttributeResult:
    """TILE-then-MERGE partition: classify feature tiles (edge density, green fraction, local
    box-count D) by the declared gates, then merge adjacent same-class tiles into semantic ZONES.
    Statistics-first regionalization — a foliage mass is one zone even though it is hundreds of
    color regions (the v1 mean-shift-zone approach shattered it; fixture caught it).
    Headline scalar = NEGATIVE-signed complexity area fraction ('which parts hurt')."""
    H, W = img_bgr.shape[:2]
    g8 = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    if float(g8.std()) < 2.0:
        return AttributeResult(key="cnfa.fluency.complexity_partition", scalar=None, confidence=0.0,
                               method="ABSTAIN: near-blank image (nothing to partition)",
                               extras={"std_dn": round(float(g8.std()), 3)},
                               failure_modes=["undefined on blank input"])
    edges = cv2.Canny(g8, 60, 160)
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    hue = hsv[..., 0].astype(int); sat = hsv[..., 1].astype(np.float32) / 255.0
    green = ((hue >= GREEN_HUE[0]) & (hue <= GREEN_HUE[1]) & (sat >= GREEN_SAT_MIN))

    T = max(32, (int(np.hypot(H, W)) // 24 // 16) * 16)   # tile size, multiple of 16 (box-count needs divisibility)
    nty, ntx = H // T, W // T
    if nty < 3 or ntx < 3:
        return AttributeResult(key="cnfa.fluency.complexity_partition", scalar=None, confidence=0.0,
                               method="ABSTAIN: image too small to partition (needs >=3x3 tiles)",
                               failure_modes=["undefined on tiny input"])
    CLASS_ID = {"biophilic_fractal": 1, "ordered_structure": 2, "junk_clutter": 3, "neutral": 4}
    tclass = np.zeros((nty, ntx), np.uint8)
    tile_D = np.full((nty, ntx), np.nan)
    for ty in range(nty):
        for tx in range(ntx):
            ys, xs = ty * T, tx * T
            e = edges[ys:ys + T, xs:xs + T]
            n_edge = int((e > 0).sum())
            edge_density = n_edge / float(T * T)
            green_frac = float(green[ys:ys + T, xs:xs + T].mean())
            D, R2 = (None, None)
            if n_edge >= MIN_EDGE_PX_REGION:
                D, R2 = _boxcount_D_r2(e)
                tile_D[ty, tx] = D
            # biophilic gate: green + GENUINELY FRACTAL (D>=band floor, clean scaling). The
            # upper band edge is NOT a gate: photographed dense canopy measures D~1.8-1.9
            # (2-D edge box-count) while Taylor/Hagerhall's preferred band came from contour
            # fractals — the band membership is a separate per-zone FLAG (in_preferred_band).
            is_fractal_organic = D is not None and D >= D_BAND[0] and (R2 or 0) >= R2_MIN
            if green_frac >= GREEN_FRAC_GATE and is_fractal_organic:
                c = "biophilic_fractal"
            elif edge_density < 0.03:
                c = "ordered_structure"
            elif edge_density >= EDGE_DENSE and not (green_frac >= GREEN_FRAC_GATE and is_fractal_organic):
                c = "junk_clutter"
            else:
                c = "neutral"
            tclass[ty, tx] = CLASS_ID[c]

    HYP = {"biophilic_fractal": "positive", "ordered_structure": "neutral",
           "junk_clutter": "negative", "neutral": "unknown"}
    zones: List[Dict] = []
    class_map = np.zeros((H, W), np.uint8)
    min_tiles = max(2, round(MIN_ZONE_FRAC * nty * ntx))     # zone >= ~1% of the tile grid
    for cname, cid in CLASS_ID.items():
        m = (tclass == cid).astype(np.uint8)
        if not m.any():
            continue
        nz, zl, zstats, _ = cv2.connectedComponentsWithStats(m, connectivity=4)
        for zi in range(1, nz):
            n_tiles = int(zstats[zi, cv2.CC_STAT_AREA])
            if n_tiles < min_tiles:
                continue
            tx0, ty0, tw, th = [int(v) for v in zstats[zi, :4]]
            zmask_tiles = (zl == zi)
            # aggregate D over the ZONE's union edge set (better statistics than per-tile)
            ys0, xs0 = ty0 * T, tx0 * T
            zone_edge = np.zeros((th * T, tw * T), np.uint8)
            for (tty, ttx) in zip(*np.nonzero(zmask_tiles)):
                zone_edge[(tty - ty0) * T:(tty - ty0 + 1) * T, (ttx - tx0) * T:(ttx - tx0 + 1) * T] = \
                    edges[tty * T:(tty + 1) * T, ttx * T:(ttx + 1) * T]
            if (zone_edge > 0).sum() >= MIN_EDGE_PX_REGION:
                Dz, R2z = _boxcount_D_r2(zone_edge)
            else:
                Dz, R2z = None, None
            gsum, tsum = 0.0, 0
            for (tty, ttx) in zip(*np.nonzero(zmask_tiles)):
                gsum += float(green[tty * T:(tty + 1) * T, ttx * T:(ttx + 1) * T].mean()); tsum += 1
            for (tty, ttx) in zip(*np.nonzero(zmask_tiles)):
                class_map[tty * T:(tty + 1) * T, ttx * T:(ttx + 1) * T] = cid
            zones.append({"bbox_px": [xs0, ys0, tw * T, th * T],
                          "area_frac": round(n_tiles / float(nty * ntx), 4),
                          "class": cname, "hedonic_hypothesis": HYP[cname],
                          "D": None if Dz is None else round(float(Dz), 3),
                          "R2": None if R2z is None else round(float(R2z), 3),
                          "green_frac": round(gsum / max(tsum, 1), 3),
                          "in_preferred_band": (None if Dz is None else
                                                bool(D_BAND[0] <= Dz <= D_BAND[1] and (R2z or 0) >= R2_MIN)),
                          "n_tiles": n_tiles})
    if not zones:
        return AttributeResult(key="cnfa.fluency.complexity_partition", scalar=None, confidence=0.0,
                               method="ABSTAIN: no zone above the size floor",
                               extras={"tiles": [int(nty), int(ntx)]},
                               failure_modes=["over-fragmented tile classes"])
    frac = lambda cname: sum(z["area_frac"] for z in zones if z["class"] == cname)
    neg, bio = frac("junk_clutter"), frac("biophilic_fractal")
    zones.sort(key=lambda z: (z["class"] != "junk_clutter", -z["area_frac"]))
    return AttributeResult(
        key="cnfa.fluency.complexity_partition",
        scalar=float(np.clip(neg, 0, 1)),
        field=class_map.astype(np.float32) / 4.0, confidence=0.5,
        method="tile-classify (edge/green/box-count D) -> merge to semantic zones -> class + "
               "hedonic HYPOTHESIS (unlicensed) (M1)",
        extras={"zones": zones[:20], "n_zones": len(zones), "tile_px": T,
                "area_fracs": {"biophilic_fractal": round(bio, 4),
                               "ordered_structure": round(frac("ordered_structure"), 4),
                               "junk_clutter": round(neg, 4),
                               "neutral": round(frac("neutral"), 4)},
                "class_ids": CLASS_ID,
                "constants": {"min_zone_frac": MIN_ZONE_FRAC, "green_hue": list(GREEN_HUE),
                              "green_sat_min": GREEN_SAT_MIN, "green_frac_gate": GREEN_FRAC_GATE,
                              "d_band": list(D_BAND), "r2_min": R2_MIN, "edge_dense": EDGE_DENSE}},
        failure_modes=["biophilic gate is chromaticity+D-band, NOT true vegetation (AMBER; the "
                       "Wave-3 segmentation model upgrades the gate, architecture unchanged)",
                       "hedonic hypotheses are UNLICENSED pending corpus (Taylor/Hagerhall "
                       "inverted-U was established on natural patterns; per-region transfer is "
                       "exactly what the corpus must test)",
                       "green paint / green furniture can pass the gate (declared limit)",
                       "tile gates are declared engineering thresholds pending corpus refit"])


# --------------------------------------------------------------------------- self-test
if __name__ == "__main__":
    import glob, time
    print("complexity_partition self-test\n" + "-" * 60)
    H, W = 240, 320
    mk = lambda f: np.clip(f, 0, 255).astype(np.uint8)
    rng = np.random.RandomState(0)

    # fixture 1: synthetic 'foliage' zone (green, textured, organic boundary) on plain wall
    img = np.full((H, W, 3), 190.0)
    rs = np.random.RandomState(5)
    for _ in range(260):                          # many overlapping green blobs -> organic mass
        x = int(rs.normal(90, 34)); y = int(rs.normal(120, 40))
        if 5 < x < W - 5 and 5 < y < H - 5:
            gcol = (int(rs.randint(20, 70)), int(rs.randint(120, 220)), int(rs.randint(20, 90)))
            cv2.circle(img, (x, y), rs.randint(3, 10), gcol, -1)
    # fixture 1b: a 'junk pile' zone (dense multicolor small fragments, not green)
    for _ in range(220):
        x = int(rs.normal(250, 22)); y = int(rs.normal(170, 30))
        if 5 < x < W - 5 and 5 < y < H - 5:
            col = tuple(int(c) for c in rs.choice([200, 30, 120, 240, 60], 3))
            cv2.rectangle(img, (x, y), (x + rs.randint(2, 7), y + rs.randint(2, 7)), col, -1)
    img = mk(img)

    r = complexity_partition(img)
    af = r.extras["area_fracs"]
    print(f"synthetic: zones={r.extras['n_zones']} fracs={af}")
    top = r.extras["zones"][0]
    print(f"  top zone: {top['class']} D={top['D']} green={top['green_frac']} tiles={top['n_tiles']}")
    classes = {z["class"] for z in r.extras["zones"]}
    assert "junk_clutter" in classes, "the fragment pile must be found as negative-signed complexity"
    bio_zones = [z for z in r.extras["zones"] if z["class"] == "biophilic_fractal"]
    assert bio_zones, "the green organic mass must classify as biophilic_fractal"
    print(f"  biophilic zone: D={bio_zones[0]['D']} green={bio_zones[0]['green_frac']} "
          f"area={bio_zones[0]['area_frac']}")

    # blank abstains
    assert complexity_partition(mk(np.full((H, W, 3), 128.0))).scalar is None
    print("blank -> abstain  OK")

    # determinism
    r2 = complexity_partition(img)
    assert r2.scalar == r.scalar and r2.extras["area_fracs"] == r.extras["area_fracs"]
    print("determinism x2  OK")

    # THE DT-1 RESOLUTION TEST: on real interiors, the partition should separate what the
    # content-free measure conflated — Farnsworth's complexity should be substantially
    # biophilic/positive-signed; the industrial office's should not be.
    ind = cv2.imread("Example Images/Industrial-open-concept-office-project-by-Decorilla-1024x819.jpeg")
    far = cv2.imread("Example Images/Ludwig_Mies_van_der_Rohe__Farnsworth_House__1945-1951_2.jpg")
    if ind is not None and far is not None:
        t0 = time.time()
        out = {}
        for name, im in [("industrial", ind), ("farnsworth", far)]:
            sc = 700 / max(im.shape[:2])
            if sc < 1:
                im = cv2.resize(im, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
            rr = complexity_partition(im)
            out[name] = rr.extras["area_fracs"]
            print(f"{name}: {out[name]}  (neg-complexity scalar {rr.scalar})")
        assert out["farnsworth"]["biophilic_fractal"] > out["industrial"]["biophilic_fractal"], \
            "Farnsworth's complexity must be more biophilic-signed than the office's"
        print(f"DT-1 resolution: Farnsworth biophilic {out['farnsworth']['biophilic_fractal']:.3f} > "
              f"industrial {out['industrial']['biophilic_fractal']:.3f}  "
              f"({time.time()-t0:.1f}s)  OK")
    print("-" * 60 + "\ncomplexity_partition self-test: PASS")
