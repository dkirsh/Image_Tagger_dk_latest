"""
viz.field_sidecars — VIEW-0: persist every operator's field + zone table + extras as a
content-addressed sidecar, written FROM THE ANNOTATION PASS OF RECORD (fields_sink on
annotate_image). The viewer consumes ONLY records + sidecars; it never recomputes.

Outputs, for unit u under out_dir:
    fields/<u>.npz            — float32 arrays, compressed; keys = predicate ids (":sub" for
                                multi-field ops like street noise; "_plan.grid" for the plan)
    fields/<u>.manifest.json  — unit_id, image_sha256, model_version, per-array
                                {shape, dtype, sha256, layer_group}, tables (zone table),
                                extras (ALL declared operator params — the VIEW-2 feed),
                                render list
    fields/<u>/<layer>.png    — per-layer-group composite renders for quick human viewing
                                (the real layered viewer is VIEW-1; these are its previews)

Layer groups mirror the register structure decided in TASKS.md Sprint VIEW:
    semantic_zones | light | fluency_clutter | space_geometry | acoustics
(evidence + audit live in the RECORD, not here — the sidecar is fields only.)

Determinism contract: two runs on the same image + MODEL_VERSION must produce byte-identical
array digests (M1'-style honesty; self-test enforces it).
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/Users/davidusa/REPOS/Image_Tagger_dk_latest")
import numpy as np


# ------------------------------------------------------------------ layer-group mapping
def layer_group(key: str) -> str:
    if key.startswith("_plan"):
        return "space_geometry"
    if key.startswith("cnfa.acoustic."):
        return "acoustics"
    if key == "cnfa.fluency.complexity_partition":
        return "semantic_zones"
    if key.startswith("cnfa.light."):
        return "light"
    if key.startswith("cnfa.geometry.") or key.startswith("cnfa.arch.") or key.startswith("cnfa.spatial.") \
            or key.startswith("cnfa.plan.") or key.startswith("C1.") or key.startswith("C2.") \
            or key.startswith("C3.") or key.startswith("C4."):
        return "space_geometry"     # wave-2 geometry, spatial-syntax, plan metrics (CC-4)
    return "fluency_clutter"        # fluency.*, fractal, texture, orderliness, clutter stack


def _sanitize(obj, arrays: dict, prefix: str):
    """Make extras JSON-able WITHOUT losing data: numpy scalars -> python; small arrays
    (<=256 elems) -> lists; large arrays -> promoted into the npz under '<pid>:extras.<path>'
    and replaced by an {'__array_ref__': key} pointer."""
    if isinstance(obj, dict):
        return {str(k): _sanitize(v, arrays, f"{prefix}.{k}") for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize(v, arrays, f"{prefix}[{i}]") for i, v in enumerate(obj)]
    if isinstance(obj, np.ndarray):
        if obj.size <= 256:
            return obj.tolist()
        arrays[prefix] = obj.astype(np.float32)
        return {"__array_ref__": prefix}
    if isinstance(obj, np.generic):
        return obj.item()
    if isinstance(obj, frozenset):
        return sorted(obj)
    return obj


def _digest(a: np.ndarray) -> str:
    """Canonical array digest: dtype + shape + raw bytes (C-order)."""
    h = hashlib.sha256()
    h.update(str(a.dtype).encode()); h.update(str(a.shape).encode())
    h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


# ------------------------------------------------------------------ rendering (previews)
# 11-class categorical palette for the semantic-zones layer (BGR). Chosen for WCAG-visible
# contrast on interiors; junk_clutter deliberately hot. Index 0 = unassigned (transparent).
_ZONE_BGR = {
    0: None,                # unassigned — leave base image
    1: (80, 200, 80),       # biophilic_vegetation  green
    2: (200, 180, 90),      # ordered_structure     steel blue-cyan
    3: (60, 60, 230),       # junk_clutter          red
    4: (160, 160, 160),     # neutral               grey
    5: (90, 140, 220),      # biophilic_material    warm wood-tan
    6: (220, 160, 60),      # water                 blue
    7: (200, 90, 200),      # art_candidate         magenta
    8: (70, 120, 255),      # fire_hearth           orange
    9: (240, 220, 160),     # sky_daylight          pale cyan
    10: (140, 220, 220),    # organized_collection  khaki-yellow
    11: (180, 120, 160),    # ornament_pattern      violet
}


def _render_layer(base_bgr, keys, arrays, group: str, out_png: Path) -> None:
    """One composite preview PNG per layer group: categorical fill for zones, max-combined
    viridis heat overlay for continuous fields, nearest-upsampled to image size."""
    import cv2
    H, W = base_bgr.shape[:2]
    over = base_bgr.copy()
    if group == "semantic_zones":
        cm = np.rint(arrays[keys[0]] * 11.0).astype(np.int32)   # field = class_id/11
        cm = cv2.resize(cm.astype(np.float32), (W, H), interpolation=cv2.INTER_NEAREST).astype(np.int32)
        fill = base_bgr.copy()
        for cid, bgr in _ZONE_BGR.items():
            if bgr is not None:
                fill[cm == cid] = bgr
        over = cv2.addWeighted(fill, 0.45, base_bgr, 0.55, 0)
    else:
        acc = np.zeros((H, W), np.float32)
        for k in keys:
            a = np.nan_to_num(np.asarray(arrays[k], np.float32))
            rng = float(a.max() - a.min())
            a01 = (a - a.min()) / rng if rng > 1e-9 else np.zeros_like(a)
            acc = np.maximum(acc, cv2.resize(a01, (W, H), interpolation=cv2.INTER_LINEAR))
        heat = cv2.applyColorMap((acc * 255).astype(np.uint8), cv2.COLORMAP_VIRIDIS)
        mask = (acc > 0.05).astype(np.float32)[..., None] * 0.55
        over = (base_bgr * (1 - mask) + heat * mask).astype(np.uint8)
    cv2.imwrite(str(out_png), over)


# ------------------------------------------------------------------ the sidecar builder
def build_sidecar(image_path: str, out_dir: str,
                  unit_inputs=frozenset(), input_values=None) -> dict:
    """Annotate ONE unit with the sink attached; write npz + manifest + preview PNGs.
    Returns the manifest dict. Skips (returns existing manifest) when the content-addressed
    sidecar already exists for this image+MODEL_VERSION."""
    import cv2
    from annotation_socket.annotator import annotate_image, unit_id_for

    u = unit_id_for(image_path)
    root = Path(out_dir); root.mkdir(parents=True, exist_ok=True)
    man_path = root / f"{u}.manifest.json"
    if man_path.exists():                                    # content-addressed: already done
        return json.loads(man_path.read_text())

    sink: dict = {}
    rec = annotate_image(image_path, unit_inputs=unit_inputs,
                         input_values=input_values, fields_sink=sink)

    tables = sink.pop("_tables", {})
    extras = sink.pop("_extras", {})
    meta = sink.pop("_meta", {})
    plan = sink.pop("_plan", None)
    arrays = {k: np.asarray(v, np.float32) for k, v in sink.items()}
    if plan is not None:
        arrays["_plan.grid"] = plan["grid"].astype(np.float32)
    tables = _sanitize(tables, arrays, "_tables")
    extras = _sanitize(extras, arrays, "_extras")
    meta = _sanitize(meta, arrays, "_meta")

    np.savez_compressed(root / f"{u}.npz", **arrays)

    # previews per layer group
    base = cv2.imread(image_path)
    groups: dict = {}
    for k in arrays:
        groups.setdefault(layer_group(k), []).append(k)
    prev_dir = root / u; prev_dir.mkdir(exist_ok=True)
    renders = []
    for g, keys in sorted(groups.items()):
        if g == "space_geometry":            # plan grid is not image-space; render standalone
            import cv2 as _c
            gimg = ((arrays["_plan.grid"] > 0) * 255).astype(np.uint8)
            _c.imwrite(str(prev_dir / "space_geometry.png"),
                       _c.resize(gimg, (gimg.shape[1] * 8, gimg.shape[0] * 8),
                                 interpolation=_c.INTER_NEAREST))
        else:
            _render_layer(base, sorted(keys), arrays, g, prev_dir / f"{g}.png")
        renders.append(f"{u}/{g}.png")

    manifest = {
        "unit_id": u,
        "image_path": image_path,
        "image_sha256": rec["image_sha256"],
        "model_version": rec["model_version"],
        "arrays": {k: {"shape": list(a.shape), "dtype": str(a.dtype),
                       "sha256": _digest(a), "layer_group": layer_group(k)}
                   for k, a in sorted(arrays.items())},
        "tables": tables,                    # zone table (class/D/hypothesis per zone)
        "extras": extras,                    # ALL declared operator params — VIEW-2 feed
        "meta": meta,                        # method/scalar/confidence/failure_modes per predicate
        "sidecar_version_note": "meta added VIEW-2 2026-07-19",
        "plan_meta": ({"cell_m": plan["cell_m"], "grid_hash": plan["grid_hash"]}
                      if plan else None),
        "renders": renders,
        "coverage": rec["coverage"],
        "sidecar_version": 2,
    }
    man_path.write_text(json.dumps(manifest, indent=1, sort_keys=True))
    # VIEW-3 needs the full record (scores/tiers/abstentions) alongside the sidecar; write it once
    # here so consumers annotate ONCE. The record is the authoritative score source (composer reads
    # numbers only from here — never recomputes).
    (root / f"{u}.record.json").write_text(json.dumps(rec))
    return manifest


# ------------------------------------------------------------------ self-test (VERIFY rule 1)
if __name__ == "__main__":
    import shutil, tempfile
    img = "/home/claude/cnfa_demo/batch_outputs/_in_Industrial_open_concept_office_project_b.png"
    td = Path(tempfile.mkdtemp(prefix="viewfields_"))
    m1 = build_sidecar(img, str(td / "a"))
    n_arr = len(m1["arrays"])
    n_field = sum(1 for k in m1["arrays"] if not k.startswith("_plan"))
    assert n_field >= 10, f"expected >=10 operator fields, got {n_field}"
    assert "cnfa.fluency.complexity_partition" in m1["arrays"], "zone map missing"
    assert m1["tables"].get("cnfa.fluency.complexity_partition"), "zone table missing"
    assert m1["extras"].get("cnfa.fluency.feature_congestion", {}).get("params"), \
        "FC params missing from extras feed"
    npz = np.load(td / "a" / f"{m1['unit_id']}.npz")
    for k, meta in m1["arrays"].items():
        assert _digest(npz[k]) == meta["sha256"], f"round-trip digest mismatch: {k}"
    # determinism: an independent second pass must reproduce every digest
    m2 = build_sidecar(img, str(td / "b"))
    diff = [k for k in m1["arrays"]
            if m1["arrays"][k]["sha256"] != m2["arrays"].get(k, {}).get("sha256")]
    assert not diff, f"NONDETERMINISTIC fields: {diff}"
    # content-addressing: third call on dir a returns cached manifest without recompute
    m3 = build_sidecar(img, str(td / "a"))
    assert m3["unit_id"] == m1["unit_id"]
    # renders exist and are non-trivial
    for r in m1["renders"]:
        p = td / "a" / r
        assert p.exists() and p.stat().st_size > 5000, f"render missing/blank: {r}"
    print(f"OK field_sidecars: {n_arr} arrays ({n_field} operator fields), "
          f"{len(m1['tables'].get('cnfa.fluency.complexity_partition', []))} zones, "
          f"{len(m1['renders'])} layer renders, deterministic across passes")
    print("groups:", sorted({v['layer_group'] for v in m1['arrays'].values()}))
    shutil.rmtree(td)
