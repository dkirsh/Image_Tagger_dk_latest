"""
cnfa_algs.complexity_partition — REGIONALIZED, SEMANTICALLY-SIGNED visual complexity
(David's proposal, 2026-07-19: "partition visual complexity so we can identify which parts of a
room have that attribute to a negative level... rename regions by their semantics").

THE THEORY MOVE. Content-free complexity conflates hedonically opposite things: a D~1.4 fern and a
D~1.4 cable tangle carry the same statistic and opposite valence. Finding DT-1 (2026-07-19) showed
this empirically — the reference Feature Congestion ranks foliage-framed Farnsworth ABOVE a
genuinely cluttered office. The fix is NOT to suppress vegetation in the measure; it is to
PARTITION the complexity field by region content and assign hedonic sign per region:

  TAXONOMY (Kellert / Terrapin 14-Patterns grounded; expanded per David 2026-07-19 — materials,
  water, art are distinct classes, not omissions):
  region class            evidence gate (declared, heuristic -> AMBER)          hedonic HYPOTHESIS
  biophilic_vegetation    green chromaticity + fractal-organic D                positive (STRONG:
                          [Nature-in-Space: Visual Connection w/ Nature]        restoration literature)
  biophilic_material      NOT green; natural-material signature: warm-neutral   mildly positive
                          or desaturated hue + real micro-texture + color-      (wood/stone interior
                          homogeneous (wood grain / stone / cloth / textile)    studies: Fell, Ikei —
                          [Natural Analogues: Material Connection w/ Nature]    weaker evidence grade)
  water                   blue hue band + smooth/low-texture + horizontal       positive (blue-space
                          coherence [Nature-in-Space: Water]                    literature)
  art_candidate           SPECIAL CLASS, outside biophilic-proper: a complex    unknown, CONTENT-
                          zone with rectangular footprint embedded in an        DEPENDENT (Ulrich:
                          ordered surround (frame-on-wall signature)            nature-depicting art
                          [content unresolvable without semantics -> VLM-tier   restorative; abstract
                          gate upgrades it to analogue-or-not]                  art mixed)
  ordered_structure       low edge density, regular                             neutral
  junk_clutter            complex but matching NO nature/material/art gate      negative (search cost)
  neutral                 none of the above                                     unknown
  (recognized, NOT yet detectable from stills: biomorphic-ephemeral — incense smoke coils, steam,
  moving water texture; and art CONTENT classification. Both are VLM-tier future gates; recorded
  here so the taxonomy is complete even where detection is deferred.)

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

# TAX-0 fix (Codex attack 2026-07-19): support direct `python3 cnfa_algs/<file>.py` invocation.
# PEP 366: bootstrap the package context so ALL relative imports (top-level and function-level)
# resolve identically to `python3 -m cnfa_algs.<file>`.
if __package__ in (None, ""):
    import sys as _sys, pathlib as _pl
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
    import cnfa_algs                     # initialize the package
    __package__ = "cnfa_algs"
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

# natural-material signature (wood/stone/cloth/textile): warm-neutral or desaturated hue,
# REAL micro-texture, color-homogeneous (few hues — junk piles are polychrome)
WOOD_HUE = (5, 30)          # OpenCV hue: browns/tans
MAT_SAT_MAX = 0.55          # natural materials are not saturated plastic colors
MAT_TEXTURE_MIN = 0.015     # 5x5 local-range mean floor (real grain/weave, not paint)
MAT_HUE_STD_MAX = 14.0      # color-homogeneity: hue dispersion low within the tile
WATER_HUE = (95, 130)       # OpenCV hue: blue band
WATER_TEXTURE_MAX = 0.02    # water reads smooth at tile scale
WATER_ROW_MIN_FRAC = 0.45   # CP-2: water tiles must sit in the lower frame (walls fill it all)
WATER_SPEC_DELTA = 0.25     # CP-2: specular glint = pixels this far above tile mean luminance
WATER_SPEC_FRAC = (0.003, 0.15)   # CP-2: glint fraction band (flat paint ~0; a bright oval >0.15)
ART_MAX_TILES_FRAC = 0.15   # an artwork zone is compact, not a wall of chaos
ART_FILL_MIN = 0.75         # zone tiles fill >=75% of their bbox (rectangular footprint)

# classes added on own initiative (2026-07-19), each with a declared deterministic gate:
FIRE_HUE = (0, 25)          # flame/ember warm band
FIRE_SAT_MIN = 0.40
FIRE_LUM_MIN = 0.40         # warm-dominated + flickery; the SATURATED-WARM fraction is the
FIRE_STD_MIN = 0.12         # main discriminator (flat orange fabric fails the flicker floor)
SKY_LUM_MIN = 0.72          # sky/daylight through glazing: bright + smooth + cool/desaturated
SKY_TEX_MAX = 0.025
PERIODIC_PEAK_MIN = 0.45    # autocorr off-center peak: organized_collection (has extra gates)
ORNAMENT_PEAK_MIN = 0.58    # ornament stands on periodicity ALONE, so its bar is higher
ART_FRAME_EDGE_MIN = 0.45   # fraction of the zone bbox perimeter lying on Canny edges (the FRAME)
COHERENCE_MIN = 0.55        # orientation coherence for organized collections (parallel spines)


def complexity_partition(img_bgr) -> AttributeResult:
    """TILE-then-MERGE partition: classify feature tiles (edge density, green fraction, local
    box-count D) by the declared gates, then merge adjacent same-class tiles into semantic ZONES.
    Statistics-first regionalization — a foliage mass is one zone even though it is hundreds of
    color regions (the v1 mean-shift-zone approach shattered it; fixture caught it).
    Headline scalar = NEGATIVE-signed complexity area fraction ('which parts hurt')."""
    img_bgr = np.asarray(img_bgr)
    if img_bgr.ndim == 3 and img_bgr.shape[2] == 4:      # CS-3 (Codex attack): declared alpha
        img_bgr = img_bgr[:, :, :3]                      # policy — alpha is DROPPED, not blended
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
    CLASS_ID = {"biophilic_vegetation": 1, "ordered_structure": 2, "junk_clutter": 3,
                "neutral": 4, "biophilic_material": 5, "water": 6, "art_candidate": 7,
                "fire_hearth": 8, "sky_daylight": 9, "organized_collection": 10,
                "ornament_pattern": 11}
    tclass = np.zeros((nty, ntx), np.uint8)
    tile_D = np.full((nty, ntx), np.nan)
    # micro-texture field (5x5 local range on luminance), for the material/water gates
    k5 = np.ones((5, 5), np.uint8)
    g01 = g8.astype(np.float32) / 255.0
    rngf = cv2.dilate(g01, k5) - cv2.erode(g01, k5)
    # CP-2: water smoothness is judged on MEDIAN-filtered luminance — isolated specular
    # glints are the water SIGNATURE, they must not fail the smoothness gate they license
    g_med = cv2.medianBlur(g8, 5).astype(np.float32) / 255.0
    rngf_med = cv2.dilate(g_med, k5) - cv2.erode(g_med, k5)
    for ty in range(nty):
        for tx in range(ntx):
            ys, xs = ty * T, tx * T
            e = edges[ys:ys + T, xs:xs + T]
            n_edge = int((e > 0).sum())
            edge_density = n_edge / float(T * T)
            green_frac = float(green[ys:ys + T, xs:xs + T].mean())
            th = hue[ys:ys + T, xs:xs + T]; ts_ = sat[ys:ys + T, xs:xs + T]
            tex = float(rngf[ys:ys + T, xs:xs + T].mean())
            hue_std = float(th[ts_ > 0.08].std()) if (ts_ > 0.08).sum() > 20 else 99.0
            mean_sat = float(ts_.mean())
            wood_frac = float(((th >= WOOD_HUE[0]) & (th <= WOOD_HUE[1]) & (ts_ > 0.08)).mean())
            blue_frac = float(((th >= WATER_HUE[0]) & (th <= WATER_HUE[1]) & (ts_ > 0.12)).mean())
            tlum = float(g01[ys:ys + T, xs:xs + T].mean())
            tlum_std = float(g01[ys:ys + T, xs:xs + T].std())
            warm_frac = float(((th >= FIRE_HUE[0]) & (th <= FIRE_HUE[1]) & (ts_ >= FIRE_SAT_MIN)).mean())
            # orientation coherence (doubled angles, magnitude-weighted) — parallel structure
            gxs = cv2.Sobel(g01[ys:ys + T, xs:xs + T], cv2.CV_32F, 1, 0, 3)
            gys = cv2.Sobel(g01[ys:ys + T, xs:xs + T], cv2.CV_32F, 0, 1, 3)
            mgm = np.sqrt(gxs * gxs + gys * gys).ravel() + 1e-12
            th2 = (np.arctan2(gys, gxs) * 2.0).ravel()
            coherence = float(np.hypot((mgm * np.cos(th2)).sum(), (mgm * np.sin(th2)).sum()) / mgm.sum())
            # periodicity: normalized autocorrelation off-center peak (FFT)
            tt = g01[ys:ys + T, xs:xs + T] - tlum
            F = np.fft.rfft2(tt)
            ac = np.fft.irfft2(F * np.conj(F), s=tt.shape)
            ac0 = max(float(ac[0, 0]), 1e-9)
            acn = np.fft.fftshift(ac) / ac0
            cy, cx = np.array(acn.shape) // 2
            acn[cy - 2:cy + 3, cx - 2:cx + 3] = 0          # kill the trivial center peak
            periodicity = float(acn.max())
            D, R2 = (None, None)
            if n_edge >= MIN_EDGE_PX_REGION:
                D, R2 = _boxcount_D_r2(e)
                tile_D[ty, tx] = D
            # vegetation gate: green + GENUINELY FRACTAL (D >= band floor, clean scaling); the
            # Taylor/Hagerhall band is a FLAG, not a gate (photographed canopy runs D~1.8-1.9)
            is_fractal_organic = D is not None and D >= D_BAND[0] and (R2 or 0) >= R2_MIN
            # natural-material gate (wood/stone/cloth): warm-neutral or desaturated,
            # REAL micro-texture, color-homogeneous — polychrome fragment piles fail hue_std
            # two material paths: WOOD-HUED (browns/tans — varnished wood runs saturated, cap
            # 0.75) or DESATURATED (stone/concrete/undyed textile, sat<0.20); both need real
            # micro-texture + homochromy (polychrome piles fail hue_std)
            is_material = (green_frac < GREEN_FRAC_GATE and tex >= MAT_TEXTURE_MIN
                           and hue_std <= MAT_HUE_STD_MAX
                           and ((wood_frac > 0.30 and mean_sat <= 0.75) or mean_sat < 0.20))
            # CP-2 fix (Codex attack 2026-07-19): a blue painted WALL is blue+smooth too.
            # Indoor water needs BOTH a lower-frame position (pools/fountains/basins sit low;
            # a blue wall fills the frame top-to-bottom) AND a specular glint signature
            # (bright outliers well above tile mean — flat paint has none). Declared limit:
            # mid-frame aquaria without glints will read as not-water (failure mode below).
            spec_frac = float((g01[ys:ys + T, xs:xs + T] > tlum + WATER_SPEC_DELTA).mean())
            tex_med = float(rngf_med[ys:ys + T, xs:xs + T].mean())
            is_water = (blue_frac > 0.40 and tex_med <= WATER_TEXTURE_MAX
                        and (ty + 0.5) / nty >= WATER_ROW_MIN_FRAC
                        and WATER_SPEC_FRAC[0] <= spec_frac <= WATER_SPEC_FRAC[1])
            if green_frac >= GREEN_FRAC_GATE and is_fractal_organic:
                c = "biophilic_vegetation"
            elif is_water:
                c = "water"
            elif tex <= SKY_TEX_MAX and ((blue_frac > 0.20 and tlum >= SKY_LUM_MIN)
                                          or tlum >= 0.88):
                c = "sky_daylight"          # smooth + (blue-bright OR near-blown): glazing view.
                                            # desaturated-but-merely-bright alone is a WALL, not
                                            # sky (v1 gate stole plain walls; fixture caught it)
            elif warm_frac > 0.35 and tlum >= FIRE_LUM_MIN and tlum_std > FIRE_STD_MIN:
                c = "fire_hearth"           # bright warm saturated + flicker-contrast
            elif is_material:
                c = "biophilic_material"    # BEFORE the ordered gate: wood grain is low-Canny
                                            # but real-texture (v1 order let 'ordered' steal it);
                                            # homochromy (hue_std) keeps polychrome shelves out
            elif edge_density < 0.03:
                c = "ordered_structure"
            elif periodicity >= PERIODIC_PEAK_MIN and edge_density >= EDGE_DENSE \
                    and coherence >= COHERENCE_MIN and hue_std > MAT_HUE_STD_MAX:
                c = "organized_collection"  # periodic + parallel + polychrome: shelves/spines
            elif periodicity >= ORNAMENT_PEAK_MIN and tex >= MAT_TEXTURE_MIN:
                c = "ornament_pattern"      # periodic decorative pattern: rug/tile/weave (bar is
                                            # higher than collections: periodicity is its ONLY gate)
            elif edge_density >= EDGE_DENSE:
                c = "junk_clutter"
            else:
                c = "neutral"
            tclass[ty, tx] = CLASS_ID[c]

    HYP = {"biophilic_vegetation": "positive", "ordered_structure": "neutral",
           "junk_clutter": "negative", "neutral": "unknown",
           "biophilic_material": "mildly_positive", "water": "positive",
           "art_candidate": "unknown_content_dependent",
           "fire_hearth": "positive", "sky_daylight": "positive",
           "organized_collection": "mildly_positive", "ornament_pattern": "unknown_positive_leaning"}
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
            # fire is POINT-LIKE by nature (a hearth is one tile) — floor of 1 for it alone
            floor = 1 if cname == "fire_hearth" else min_tiles
            if n_tiles < floor:
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
    # ART RECLASS PASS: a compact junk/neutral zone with a rectangular tile footprint
    # embedded in ordered surround reads as a framed artwork -> special class (content
    # unresolvable without semantics; VLM-tier gate upgrades later)
    for z in zones:
        if z["class"] in ("junk_clutter", "neutral"):
            bx, by, bw, bh = z["bbox_px"]
            bbox_tiles = max(1, (bw // T) * (bh // T))
            fill = z["n_tiles"] / bbox_tiles
            if (z["area_frac"] <= ART_MAX_TILES_FRAC and fill >= ART_FILL_MIN
                    and z["n_tiles"] >= min_tiles
                    and bx > 0 and by > 0 and bx + bw < W and by + bh < H):
                # THE FRAME TEST (v2 — a compact junk pile passed the geometry checks; the
                # discriminator is the literal frame): a high fraction of the bbox perimeter
                # must lie on edges. Piles have ragged borders; framed art has a rectangle.
                band = 3
                per_edges, per_total = 0, 0
                for (ys_, ye_, xs_, xe_) in [(by, by + band, bx, bx + bw),
                                             (by + bh - band, by + bh, bx, bx + bw),
                                             (by, by + bh, bx, bx + band),
                                             (by, by + bh, bx + bw - band, bx + bw)]:
                    seg = edges[max(0, ys_):ye_, max(0, xs_):xe_]
                    # count perimeter COLUMNS/ROWS covered by at least one edge pixel
                    if seg.shape[0] <= band * 2:
                        cov = (seg.max(axis=0) > 0)
                    else:
                        cov = (seg.max(axis=1) > 0)
                    per_edges += int(cov.sum()); per_total += int(cov.size)
                frame_cov = per_edges / max(per_total, 1)
                if frame_cov >= ART_FRAME_EDGE_MIN:
                    z["class"] = "art_candidate"
                    z["hedonic_hypothesis"] = HYP["art_candidate"]
                    z["frame_edge_coverage"] = round(frame_cov, 3)
    frac = lambda cname: sum(z["area_frac"] for z in zones if z["class"] == cname)
    neg = frac("junk_clutter")
    bio = frac("biophilic_vegetation") + frac("biophilic_material") + frac("water")
    zones.sort(key=lambda z: (z["class"] != "junk_clutter", -z["area_frac"]))
    return AttributeResult(
        key="cnfa.fluency.complexity_partition",
        scalar=float(np.clip(neg, 0, 1)),
        field=class_map.astype(np.float32) / 11.0, confidence=0.5,
        method="tile-classify (edge/green/box-count D) -> merge to semantic zones -> class + "
               "hedonic HYPOTHESIS (unlicensed) (M1)",
        extras={"zones": zones[:20], "n_zones": len(zones), "tile_px": T,
                "area_fracs": {"biophilic_vegetation": round(frac("biophilic_vegetation"), 4),
                               "biophilic_material": round(frac("biophilic_material"), 4),
                               "water": round(frac("water"), 4),
                               "art_candidate": round(frac("art_candidate"), 4),
                               "ordered_structure": round(frac("ordered_structure"), 4),
                               "junk_clutter": round(neg, 4),
                               "neutral": round(frac("neutral"), 4),
                               "fire_hearth": round(frac("fire_hearth"), 4),
                               "sky_daylight": round(frac("sky_daylight"), 4),
                               "organized_collection": round(frac("organized_collection"), 4),
                               "ornament_pattern": round(frac("ornament_pattern"), 4),
                               "biophilic_total": round(bio, 4)},
                "class_ids": CLASS_ID,
                "constants": {"min_zone_frac": MIN_ZONE_FRAC, "green_hue": list(GREEN_HUE),
                              "green_sat_min": GREEN_SAT_MIN, "green_frac_gate": GREEN_FRAC_GATE,
                              "d_band": list(D_BAND), "r2_min": R2_MIN, "edge_dense": EDGE_DENSE,
                              # CP-1 (Codex attack 2026-07-19): EVERY tuned gate constant declared
                              "wood_hue": list(WOOD_HUE), "mat_texture_min": MAT_TEXTURE_MIN,
                              "mat_hue_std_max": MAT_HUE_STD_MAX,
                              "mat_wood_frac_min": 0.30, "mat_wood_sat_max": 0.75,
                              "mat_desat_max": 0.20,
                              "water_hue": list(WATER_HUE),
                              "water_texture_max": WATER_TEXTURE_MAX,
                              "water_row_min_frac": WATER_ROW_MIN_FRAC,
                              "water_spec_delta": WATER_SPEC_DELTA,
                              "water_spec_frac": list(WATER_SPEC_FRAC),
                              "fire_hue": list(FIRE_HUE), "fire_sat_min": FIRE_SAT_MIN,
                              "fire_lum_min": FIRE_LUM_MIN, "fire_std_min": FIRE_STD_MIN,
                              "sky_lum_min": SKY_LUM_MIN, "sky_tex_max": SKY_TEX_MAX,
                              "sky_blown_lum": 0.88,
                              "periodic_peak_min": PERIODIC_PEAK_MIN,
                              "ornament_peak_min": ORNAMENT_PEAK_MIN,
                              "coherence_min": COHERENCE_MIN,
                              "art_frame_edge_min": ART_FRAME_EDGE_MIN,
                              "merge_connectivity": 4}},   # CP-8: 4-adjacency tile merge, declared
        failure_modes=["biophilic gate is chromaticity+D-band, NOT true vegetation (AMBER; the "
                       "Wave-3 segmentation model upgrades the gate, architecture unchanged)",
                       "hedonic hypotheses are UNLICENSED pending corpus (Taylor/Hagerhall "
                       "inverted-U was established on natural patterns; per-region transfer is "
                       "exactly what the corpus must test)",
                       "green paint / green furniture can pass the vegetation gate (declared limit)",
                       "the material gate is ABSORBENT on real photos: brown/desaturated textured "
                       "surfaces read as material wholesale, shrinking junk_clutter (industrial "
                       "office smoke: junk 0.60 pre-taxonomy -> 0.0 post) — gate PRECISION is the "
                       "corpus's first calibration target for this operator",
                       "tile gates are declared engineering thresholds pending corpus refit",
                       # Codex attack 2026-07-19 dispositions (CP-2/3/4 fixtures):
                       "water gate needs lower-frame position + glint band: mid-frame aquaria "
                       "without specular glints read as not-water (declared limit)",
                       "mirrors/framed reflective surfaces confound the art frame test and can "
                       "scatter across material/sky/ornament (CP-3; real fix is the Wave-3 "
                       "detector + VLM art-content gate, CC-5)",
                       "bright HIGH-TEXTURE ceilings can read junk_clutter (CP-4): the "
                       "sky/ceiling/junk boundary is threshold-tuned, corpus-refit target"])


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
    bio_zones = [z for z in r.extras["zones"] if z["class"] == "biophilic_vegetation"]
    assert bio_zones, "the green organic mass must classify as biophilic_vegetation"
    print(f"  biophilic zone: D={bio_zones[0]['D']} green={bio_zones[0]['green_frac']} "
          f"area={bio_zones[0]['area_frac']}")

    # NEW-CLASS FIXTURES (2026-07-19 taxonomy expansion): wood material, fire, sky, collection
    def classes_of(im):
        rr = complexity_partition(im)
        return rr.extras["area_fracs"], {z["class"] for z in rr.extras["zones"]}

    # wood: brown base + horizontal grain streaks + fine noise (warm-neutral, textured, homochrome)
    wood = np.zeros((H, W, 3))
    wood[..., 0] = 40; wood[..., 1] = 80; wood[..., 2] = 140          # brown (BGR)
    rs2 = np.random.RandomState(11)
    for yy_ in range(0, H, 6):
        cv2.line(wood, (0, yy_ + rs2.randint(-2, 3)), (W, yy_ + rs2.randint(-2, 3)),
                 (30, 60, 110), 1)
    wood += rs2.randn(H, W, 3) * 6
    wf, wc = classes_of(np.clip(wood, 0, 255).astype(np.uint8))
    assert wf["biophilic_material"] > 0.5, (wf, "wood grain must read as biophilic_material")
    print(f"wood-grain fixture -> biophilic_material {wf['biophilic_material']:.2f}  OK")

    # fire: dark room + flickery warm-orange blob
    fire = np.full((H, W, 3), 25.0)
    cv2.circle(fire, (160, 120), 34, (10, 120, 250), -1)
    fire[86:154, 126:194] += rs2.randn(68, 68, 3) * 45                # flicker contrast
    ff, fcs = classes_of(np.clip(fire, 0, 255).astype(np.uint8))
    assert ff["fire_hearth"] > 0, (ff, "warm flickery source must read as fire_hearth")
    print(f"fire fixture -> fire_hearth {ff['fire_hearth']:.2f}  OK")

    # sky: near-blown smooth region beside a normal wall
    sky = np.full((H, W, 3), 150.0); sky[:, :W // 2] = 246.0
    sf, scs = classes_of(np.clip(sky + rs2.randn(H, W, 3) * 1.5, 0, 255).astype(np.uint8))
    assert sf["sky_daylight"] > 0.3, (sf, "near-blown smooth half must read as sky_daylight")
    print(f"sky fixture -> sky_daylight {sf['sky_daylight']:.2f}  OK")

    # organized collection: periodic polychrome vertical 'spines'
    shelf = np.full((H, W, 3), 60.0)
    for xx_ in range(0, W, 8):
        col = [int(c) for c in rs2.randint(40, 255, 3)]
        col[1] = min(col[1], max(col[0], col[2]) - 10) if max(col[0], col[2]) > 50 else col[1] // 3
        cv2.rectangle(shelf, (xx_, 0), (xx_ + 6, H), tuple(col), -1)   # non-green-dominant spines
        # (the green-paint-passes-the-gate limit is DECLARED for the vegetation class; this
        # fixture tests the COLLECTION gate, so its palette avoids that known confound)
    cf, ccs = classes_of(np.clip(shelf + rs2.randn(H, W, 3) * 3, 0, 255).astype(np.uint8))
    assert cf["organized_collection"] + cf["ornament_pattern"] > 0.5, \
        (cf, "periodic polychrome spines must read as organized/ornament, NOT junk")
    assert cf["junk_clutter"] < 0.2, (cf, "the bookshelf false-positive must not read as junk")
    print(f"shelf fixture -> organized {cf['organized_collection']:.2f} + "
          f"ornament {cf['ornament_pattern']:.2f}, junk {cf['junk_clutter']:.2f}  OK")

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
        assert out["farnsworth"]["biophilic_total"] > out["industrial"]["biophilic_total"], \
            "Farnsworth's complexity must be more biophilic-signed than the office's"
        print(f"DT-1 resolution: Farnsworth biophilic {out['farnsworth']['biophilic_total']:.3f} > "
              f"industrial {out['industrial']['biophilic_total']:.3f}  "
              f"({time.time()-t0:.1f}s)  OK")
    print("-" * 60 + "\ncomplexity_partition self-test: PASS")
