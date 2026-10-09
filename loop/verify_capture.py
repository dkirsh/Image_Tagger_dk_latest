#!/usr/bin/env python3
"""loop/verify_capture.py — bind a human's screenshot to the exact packet it shows.

Lane: Image_Tagger_dk_latest (tanishq). Referent repair, approved by David Kirsh 2026-10-07.

The comparator (run_loop_compare.py) judges room.json and never opens room.html, so nothing
in the loop checks that a picture a person looked at is a picture of the judged room. This
tool does. `bind` records, in capture.json, the hashes of the packet's room.json,
camera.json and room.html, the packet's viewer_revision, the hash of any treatment
parameters, and the screenshot's own hash and pixel size. `verify` recomputes every one of
those and refuses on any mismatch. A human verdict that promotes a packet should cite a
capture.json that verifies.

What a verified capture certifies, and what it does not: it ties the screenshot to the
room, the viewer code and the treatment parameters. It does NOT certify the camera pose:
room.html draws a canonical cutaway, not the camera.json view, so camera.json is bound by
hash (a moved camera is refused) but the picture is not of that pose. `camera_bound` must
be false until a viewer renders from camera.json; a capture claiming otherwise is refused.

  python3 loop/verify_capture.py bind   --packet-dir D --image shot.png [--treatment T.json] --out capture.json
  python3 loop/verify_capture.py verify --packet-dir D --capture capture.json [--treatment T.json]

Exit codes: 0 bound / verified; 2 REFUSED (the message begins "REFUSED:").
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_loop_compare import (CONTRACT_VERSION, Refused, _strict_loads,  # noqa: E402
                              read_regular_bytes, sha256_bytes)

CAPTURE_VERSION = "referent-capture/v0"
PACKET_MEMBERS = (("render.png", "render_png"), ("room.json", "room_json"),
                  ("camera.json", "camera_json"), ("room.html", "room_html"))
BOUND_MEMBERS = ("room_json", "camera_json", "room_html")
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def _load_json(path: Path, label: str) -> Any:
    try:
        return _strict_loads(read_regular_bytes(path, label).decode("utf-8"), label)
    except (UnicodeDecodeError, ValueError) as e:
        raise Refused(f"{label} unparseable: {e}")


def canonical_sha(obj: Any) -> str:
    """Hash of a JSON value independent of key order and whitespace."""
    return sha256_bytes(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                   ensure_ascii=False).encode("utf-8"))


def treatment_sha(path: Optional[Path]) -> Optional[str]:
    return None if path is None else canonical_sha(_load_json(path, "treatment parameters"))


def png_size(data: bytes) -> tuple[int, int]:
    if len(data) < 24 or data[:8] != PNG_SIG or data[12:16] != b"IHDR":
        raise Refused("capture image is not a PNG")
    w, h = struct.unpack(">II", data[16:24])
    if w < 1 or h < 1:
        raise Refused("capture image has no pixels")
    return w, h


def packet_facts(packet_dir: Path) -> Dict[str, Any]:
    """Load packet.json and check every member against its manifest hash (room.html included)."""
    m = _load_json(packet_dir / "packet.json", "packet.json")
    if not isinstance(m, dict):
        raise Refused("packet.json must be a JSON object")
    if m.get("contract_version") != CONTRACT_VERSION:
        raise Refused(f"contract_version {m.get('contract_version')!r} != {CONTRACT_VERSION!r}")
    shas = m.get("sha256")
    if not isinstance(shas, dict):
        raise Refused("packet.json sha256 must be an object")
    if "room_html" not in shas:
        raise Refused("packet carries no room.html (sha256.room_html absent): "
                      "this producer predates the referent repair")
    vr = m.get("viewer_revision")
    if not (isinstance(vr, dict) and isinstance(vr.get("viewer_sources_sha256"), str)
            and vr["viewer_sources_sha256"]):
        raise Refused("packet.json viewer_revision.viewer_sources_sha256 missing")
    view = m.get("room_html_view")
    if not isinstance(view, str) or not view:
        raise Refused("packet.json room_html_view missing")
    actual: Dict[str, str] = {}
    for fname, key in PACKET_MEMBERS:
        digest = sha256_bytes(read_regular_bytes(packet_dir / fname, fname))
        if shas.get(key) != digest:
            raise Refused(f"packet integrity: sha256 mismatch for {fname} "
                          f"(manifest={shas.get(key)!r} actual={digest})")
        actual[key] = digest
    return {"hashes": actual, "viewer_revision": vr, "view": view}


def bind(packet_dir: Path, image: Path, out: Path, treatment: Optional[Path]) -> Dict[str, Any]:
    facts = packet_facts(packet_dir)
    data = read_regular_bytes(image, "capture image")
    w, h = png_size(data)
    try:
        image_ref = str(image.resolve().relative_to(out.resolve().parent))
    except ValueError:
        raise Refused("the capture image must sit in capture.json's folder or below it")
    capture = {
        "capture_version": CAPTURE_VERSION,
        "image": {"file": image_ref, "sha256": sha256_bytes(data), "width_px": w, "height_px": h},
        "bound": {**{k: facts["hashes"][k] for k in BOUND_MEMBERS},
                  "viewer_revision": facts["viewer_revision"],
                  "treatment_params_sha256": treatment_sha(treatment)},
        "view": facts["view"],
        "camera_bound": False,
    }
    out.write_text(json.dumps(capture, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return capture


def verify(packet_dir: Path, capture_path: Path, treatment: Optional[Path]) -> str:
    facts = packet_facts(packet_dir)
    cap = _load_json(capture_path, "capture.json")
    if not isinstance(cap, dict) or cap.get("capture_version") != CAPTURE_VERSION:
        raise Refused(f"capture.json is not {CAPTURE_VERSION}")
    bound = cap.get("bound")
    if not isinstance(bound, dict):
        raise Refused("capture.json bound must be an object")
    for key in BOUND_MEMBERS:
        if bound.get(key) != facts["hashes"][key]:
            raise Refused(f"capture is not of this packet: {key} differs "
                          f"(capture={bound.get(key)!r} packet={facts['hashes'][key]})")
    if bound.get("viewer_revision") != facts["viewer_revision"]:
        raise Refused("capture is not of this viewer: viewer_revision differs "
                      f"(capture={bound.get('viewer_revision')!r} "
                      f"packet={facts['viewer_revision']!r})")
    want_t = treatment_sha(treatment)
    if bound.get("treatment_params_sha256") != want_t:
        raise Refused("capture is not of these treatment parameters "
                      f"(capture={bound.get('treatment_params_sha256')!r} supplied={want_t!r})")
    if cap.get("view") != facts["view"]:
        raise Refused(f"capture view {cap.get('view')!r} != packet room_html_view {facts['view']!r}")
    if cap.get("camera_bound") is not False:
        raise Refused("camera_bound must be false: room.html draws a canonical cutaway, "
                      "not the camera.json pose, so no capture can certify the pose yet")
    img = cap.get("image")
    if not isinstance(img, dict) or not isinstance(img.get("file"), str):
        raise Refused("capture.json image.file missing")
    rel = Path(img["file"])
    if rel.is_absolute() or ".." in rel.parts:
        raise Refused("capture image path must be relative and inside capture.json's folder")
    data = read_regular_bytes(capture_path.parent / rel, "capture image")
    if img.get("sha256") != sha256_bytes(data):
        raise Refused("capture image bytes differ from the recorded sha256")
    if (img.get("width_px"), img.get("height_px")) != png_size(data):
        raise Refused("capture image pixel size differs from the recorded size")
    commit = facts["viewer_revision"].get("git_commit") or "uncommitted viewer sources"
    return (f"VERIFIED: capture {img['sha256'][:12]} shows room.json {facts['hashes']['room_json'][:12]}"
            f" in room.html {facts['hashes']['room_html'][:12]}, viewer {commit}, treatment "
            f"{(want_t or 'none')[:12]}. NOT certified: the camera.json pose "
            f"({facts['view']}).")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="bind / verify a referent capture (referent-capture/v0)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("bind")
    b.add_argument("--packet-dir", required=True)
    b.add_argument("--image", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--treatment")
    v = sub.add_parser("verify")
    v.add_argument("--packet-dir", required=True)
    v.add_argument("--capture", required=True)
    v.add_argument("--treatment")
    a = ap.parse_args(argv)
    t = Path(a.treatment) if a.treatment else None
    try:
        if a.cmd == "bind":
            out = Path(a.out)
            if out.exists():
                raise Refused(f"{out} already exists; a capture record is never overwritten")
            cap = bind(Path(a.packet_dir), Path(a.image), out, t)
            print(f"BOUND: {out} (image {cap['image']['sha256'][:12]}, camera_bound false)")
        else:
            print(verify(Path(a.packet_dir), Path(a.capture), t))
        return 0
    except Refused as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
