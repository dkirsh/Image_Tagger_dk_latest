#!/usr/bin/env python3
"""Run the full cnfa_algs pipeline on an interior image.
Outputs: gallery PNGs (Tier A overlays, plane/depth diagnostics, Tier B plan
topo-maps) + results.json.
"""
import sys, os, json
sys.path.insert(0, "/home/claude")
import numpy as np
import cv2
import cnfa_algs as ca
from cnfa_algs import attributes as A

def run(img_path: str, outdir: str, seats=None, upscale=2):
    os.makedirs(outdir, exist_ok=True)
    name = os.path.splitext(os.path.basename(img_path))[0]
    img = cv2.imread(img_path)
    if upscale != 1:
        img = cv2.resize(img, None, fx=upscale, fy=upscale, interpolation=cv2.INTER_CUBIC)
    H, W = img.shape[:2]
    print(f"[{name}] {W}x{H}")

    # ---- geometry
    vx, vy, vconf = ca.estimate_vanishing_point(img)
    planes, pconf = ca.segment_planes(img, (vx, vy))
    depth = ca.DepthProvider()
    Z, disp01, dconf = depth(img, planes, (vx, vy))
    print(f"  vp=({vx:.0f},{vy:.0f}) conf={vconf:.2f}; planes conf={pconf:.2f}; depth {depth.method} conf={dconf:.2f}")

    diag = [
        ca.annotate_title(img, f"{name}: input"),
        ca.annotate_title(ca.mask_overlay(img, planes, ca.PLANE_PALETTE, legend=ca.PLANE_LEGEND),
                          "plane segmentation (heuristic)", f"conf={pconf:.2f}"),
        ca.annotate_title(ca.heatmap_overlay(img, disp01, contours=5),
                          "depth / disparity", depth.method),
    ]
    cv2.imwrite(f"{outdir}/{name}_0_diagnostics.png", ca.gallery(diag, cols=3))

    # ---- Tier A attributes
    results = []
    tiles = []
    def add(res, base=img):
        results.append(res)
        if res.field is not None:
            im = ca.heatmap_overlay(base, res.field)
        else:
            im = base.copy()
        if res.regions:
            im = ca.region_overlay(im, res.regions)
        s = "" if res.scalar is None else f"={res.scalar:.3f} "
        tiles.append(ca.annotate_title(im, f"{res.key} {s}", f"conf={res.confidence:.2f} {res.method[:58]}"))

    add(A.brightness_variance(img))
    add(A.edge_clarity(img))
    add(A.symmetry_horizontal(img))
    add(A.palette_entropy(img))
    add(A.processing_load(img))
    add(A.fractal_dimension_local(img))
    add(A.glare_risk(img))
    add(A.warmth_ratio(img))
    add(A.vertical_illuminance_proxy(img, planes))
    add(A.enclosure_index(img, planes, Z))
    add(A.prospect(img, planes, Z))
    add(A.landmark_salience(img))
    add(A.acoustic_absorption(img, planes, Z))
    if seats:
        add(A.sociopetal_seating(img, seats, Z))

    cv2.imwrite(f"{outdir}/{name}_1_tierA.png", ca.gallery(tiles, cols=4))

    # ---- Tier B: inferred plan + fields
    pg = ca.infer_plan_from_image(img, planes, Z)
    fields = ca.isovist_fields(pg, n_rays=48, stride=2)
    iso = ca.camera_isovist_polygon(pg)
    plan_tiles = [
        ca.render_plan_topo(pg, fields["openness"], "isovist openness (inferred plan)", iso),
        ca.render_plan_topo(pg, fields["prospect"], "prospect field"),
        ca.render_plan_topo(pg, fields["refuge"], "refuge (enclosure) field"),
        ca.render_plan_topo(pg, fields["prospect_refuge"], "prospect-refuge seat-choice map"),
    ]
    cv2.imwrite(f"{outdir}/{name}_2_tierB_plan.png", ca.gallery(plan_tiles, cols=2))

    # plan-derived scalars -> results
    from cnfa_algs.core import AttributeResult
    free = pg.grid == 1
    results.append(AttributeResult(
        key="cnfa.spatial.prospect_to_refuge_ratio",
        scalar=float(np.nanmean(fields["prospect"][free]) /
                     (np.nanmean(fields["prospect"][free]) + np.nanmean(fields["refuge"][free]) + 1e-9)),
        confidence=round(0.85 * pg.confidence, 2),
        method="mean prospect vs refuge over inferred-plan free cells (M2.5)",
        failure_modes=["single-view plan covers visible region only", "depth fallback quality"],
        extras={"plan_method": pg.method, "plan_conf": pg.confidence}))
    results.append(AttributeResult(
        key="spatial.isovist_openness_plan",
        scalar=float(np.nanmean(fields["openness_raw_m"][free])),
        confidence=round(0.85 * pg.confidence, 2),
        method="mean isovist radial (m-ish) over inferred plan (M2.5)",
        failure_modes=["scale from assumed camera height/FOV"]))

    ca.save_results_json(results, f"{outdir}/{name}_results.json",
                         meta={"image": img_path, "depth": depth.method,
                               "vp_conf": vconf, "plane_conf": pconf})
    print(f"  wrote {outdir}/{name}_[0,1,2]*.png + results.json  ({len(results)} attributes)")
    return results


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/cnfa_demo/inputs/angular_modern.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "/home/claude/cnfa_demo/outputs"
    # manual seat boxes for the sociopetal demo on angular_modern (2x upscale coords)
    seats = None
    if "angular_modern" in inp:
        seats = [
            {"bbox": [508, 190, 300, 200], "facing_deg": 200, "label": "sofa"},
            {"bbox": [246, 128, 90, 90],  "facing_deg": 20,  "label": "armchair L"},
            {"bbox": [360, 120, 80, 84],  "facing_deg": 90,  "label": "armchair R"},
        ]
    run(inp, out, seats=seats)
