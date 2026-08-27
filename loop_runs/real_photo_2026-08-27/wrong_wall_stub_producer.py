#!/usr/bin/env python3
"""wrong_wall_stub_producer.py — NEGATIVE CONTROL producer for run B.

Emits a render-verdict/v0.7 packet that is deliberately WRONG in exactly one way: the
glazed_wall is placed on the NORTH (far) wall instead of the EAST (right) wall.

That specific error is not arbitrary. It is the error David's own critique of
Office-Grade-1-1536x838.jpg identified as a blocker — "The glazing is on the RIGHT (side)
wall, not the far wall where all openings were placed" — and the error the platform's wall
rule was written to fix. So run B reproduces the ORIGINAL defect on purpose, giving the
human reviewer something concretely and recognisably wrong to reject, rather than noise.

This is a stub: it does not reconstruct anything. It writes a room.json by hand. It exists
only to produce a wrong render, and it is committed alongside the run so the rejection is
reproducible and its wrongness is inspectable.

Same CLI as the real producer, so the orchestrator's command template is unchanged.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

CONTRACT_VERSION = "render-verdict/v0.7"


def placeholder_png() -> bytes:
    def chunk(t: bytes, d: bytes) -> bytes:
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c))
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(b"\x00\x80\x80\x80")) + chunk(b"IEND", b""))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="wrong-wall negative-control stub producer")
    ap.add_argument("--scene", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--iter", type=int, required=True)
    ap.add_argument("--produced-utc", default="unspecified")
    a = ap.parse_args(argv)

    scene_path = Path(a.scene)
    scene = json.loads(scene_path.read_text(encoding="utf-8"))

    # THE DELIBERATE ERROR: everything on the far (north) wall, which is the pre-fix
    # behaviour DK flagged. Aperture ids still follow the platform spelling so the
    # comparator runs in exact identity mode and the disagreement is about the WALL,
    # not about identity being unverifiable.
    apertures = []
    for i, op in enumerate(scene.get("openings") or []):
        apertures.append({"id": f"ap{i}", "kind": str(op.get("kind")), "wall": "north",
                          "u_m": 0.0, "width_m": 2.0, "sill_m": 0.0, "height_m": 2.0})
    room = {
        "schema_version": "0.3",
        "room": {"id": str(scene.get("image_id", "stub")), "archetype": "gallery", "seed": 1},
        "geometry": {"width_m": 8.0, "depth_m": 12.0, "ceiling_height_m": 3.2,
                     "wall_thickness_m": 0.15, "floor_elevation_m": 0.0},
        "apertures": apertures,
        "furniture": [],
        "_provenance": "NEGATIVE CONTROL STUB: all openings forced onto the far (north) "
                       "wall, reproducing the pre-fix defect DK flagged. Not a reconstruction.",
    }
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    png = placeholder_png()
    room_b = (json.dumps(room, sort_keys=True) + "\n").encode()
    cam_b = (json.dumps({"position_m": [4.0, 1.6, 11.5], "look_at_m": [4.0, 1.6, 0.0],
                         "fov_deg": 70, "image_wh": [1280, 720]}, sort_keys=True) + "\n").encode()
    (out / "render.png").write_bytes(png)
    (out / "room.json").write_bytes(room_b)
    (out / "camera.json").write_bytes(cam_b)
    sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
    (out / "packet.json").write_text(json.dumps({
        "contract_version": CONTRACT_VERSION,
        "run_id": a.run_id, "iter": a.iter,
        "target_image_id": str(scene.get("image_id", scene_path.stem)),
        "produced_utc": a.produced_utc,
        "render_kind": "structural_placeholder_v0",
        "_negative_control": "wrong_wall — glazing forced to north; see module docstring",
        "sha256": {"render_png": sha(png), "room_json": sha(room_b),
                   "camera_json": sha(cam_b)},
    }, indent=1, sort_keys=True), encoding="utf-8")
    aps = ", ".join(f"{x['id']}:{x['kind']}->{x['wall']}" for x in apertures)
    print(f"NEGATIVE-CONTROL packet iter={a.iter} run={a.run_id}: [{aps}] -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
