"""loop/tests/test_verify_capture.py — the referent binding and its tamper controls.

A genuine capture of a packet must verify. Each tampered variant must be refused, and each
tamper is applied CONSISTENTLY: the packet is rebuilt with a correct manifest, so packet
integrity alone cannot catch it and only the capture's binding can. The five controls are
the ones David Kirsh approved on 2026-10-07: a moved aperture, the camera moved 1 cm, a
different viewer_revision, a swapped room.html, and a changed treatment parameter.

Synthetic packets (no cross-repo dependency), tmp_path, stdlib-runnable.

Run:  PYTHONPATH=. python3 -m pytest loop/tests/test_verify_capture.py -v
  or: PYTHONPATH=. python3 loop/tests/test_verify_capture.py
"""
from __future__ import annotations

import copy
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "loop"))

import verify_capture as vc  # noqa: E402
from run_loop_compare import Refused  # noqa: E402

ROOM = {"schema_version": "0.3-semantic", "room": {"id": "office-grade-1"},
        "geometry": {"width_m": 6.0, "depth_m": 5.0, "ceiling_height_m": 2.8},
        "apertures": [{"id": "ap0", "kind": "glazed_wall", "wall": "east"},
                      {"id": "ap1", "kind": "door", "wall": "north"}],
        "furniture": [{"id": "desk-1", "category": "desk", "_source_bbox": [0.4, 0.5, 0.6, 0.8]}]}
CAMERA = {"position_m": [3.0, 1.6, 4.5], "look_at_m": [3.0, 1.6, 0.0],
          "fov_deg": 70, "image_wh": [1280, 720]}
VIEWER = {"git_commit": "a" * 40, "viewer_sources_sha256": "b" * 64}
VIEW = "canonical_cutaway_not_camera_pose"
TREATMENT = {"parameter": "ceiling_height_m", "control": 2.8, "treatment": 3.4}


def _png(w: int, h: int, rgb: bytes = b"\x80\x80\x80") -> bytes:
    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c))
    raw = b"".join(b"\x00" + rgb * w for _ in range(h))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def _html(room: dict) -> str:
    return f"<!doctype html><title>{room['room']['id']} — canonical cutaway</title>{json.dumps(room, sort_keys=True)}"


def write_packet(d: Path, room=ROOM, camera=CAMERA, viewer=VIEWER, html=None) -> Path:
    """A well-formed v0.7 packet with room.html; the manifest always matches the files."""
    d.mkdir(parents=True, exist_ok=True)
    files = {"render.png": _png(1, 1),
             "room.json": (json.dumps(room, sort_keys=True) + "\n").encode(),
             "camera.json": (json.dumps(camera, sort_keys=True) + "\n").encode(),
             "room.html": (html if html is not None else _html(room)).encode("utf-8")}
    for name, b in files.items():
        (d / name).write_bytes(b)
    sha = {k: hashlib.sha256(files[f]).hexdigest() for f, k in vc.PACKET_MEMBERS}
    (d / "packet.json").write_text(json.dumps({
        "contract_version": "render-verdict/v0.7", "run_id": "t", "iter": 1,
        "target_image_id": "office-grade-1", "produced_utc": "unspecified",
        "render_kind": "structural_placeholder_v0", "room_html_view": VIEW,
        "viewer_revision": viewer, "sha256": sha}, sort_keys=True))
    return d


def genuine(tmp_path: Path):
    """A packet, a treatment file, a screenshot and a capture bound to all three."""
    pkt = write_packet(tmp_path / "packet")
    t = tmp_path / "treatment.json"
    t.write_text(json.dumps(TREATMENT))
    rec = tmp_path / "record"
    rec.mkdir()
    (rec / "shot.png").write_bytes(_png(4, 3))
    cap = rec / "capture.json"
    vc.bind(pkt, rec / "shot.png", cap, t)
    return pkt, cap, t


def refused(fn, *args) -> str:
    try:
        fn(*args)
    except Refused as e:
        return str(e)
    raise AssertionError("expected a refusal, got a pass")


def test_genuine_capture_verifies(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    msg = vc.verify(pkt, cap, t)
    assert msg.startswith("VERIFIED")
    assert "NOT certified: the camera.json pose" in msg   # the honest caveat is always printed


def test_tamper_a_moved_aperture_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    room = copy.deepcopy(ROOM)
    room["apertures"][0]["wall"] = "south"
    write_packet(pkt, room=room)                          # consistent manifest, new room
    assert "room_json differs" in refused(vc.verify, pkt, cap, t)


def test_tamper_b_camera_moved_1cm_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    cam = copy.deepcopy(CAMERA)
    cam["position_m"][0] = round(cam["position_m"][0] + 0.01, 3)
    write_packet(pkt, camera=cam)
    assert "camera_json differs" in refused(vc.verify, pkt, cap, t)


def test_tamper_c_different_viewer_revision_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    write_packet(pkt, viewer={"git_commit": "c" * 40, "viewer_sources_sha256": "b" * 64})
    assert "viewer_revision differs" in refused(vc.verify, pkt, cap, t)
    write_packet(pkt, viewer={"git_commit": "a" * 40, "viewer_sources_sha256": "d" * 64})
    assert "viewer_revision differs" in refused(vc.verify, pkt, cap, t)


def test_tamper_d_swapped_room_html_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    other = copy.deepcopy(ROOM)
    other["room"]["id"] = "another-room"
    write_packet(pkt, html=_html(other))                  # same room.json, another room's page
    assert "room_html differs" in refused(vc.verify, pkt, cap, t)


def test_tamper_e_changed_treatment_parameter_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    t.write_text(json.dumps({**TREATMENT, "treatment": 3.5}))
    assert "treatment parameters" in refused(vc.verify, pkt, cap, t)


def test_treatment_omitted_or_added_at_verify_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    assert "treatment parameters" in refused(vc.verify, pkt, cap, None)


def test_treatment_key_order_does_not_matter(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    t.write_text(json.dumps(dict(reversed(list(TREATMENT.items()))), indent=3))
    assert vc.verify(pkt, cap, t).startswith("VERIFIED")


def test_edited_member_without_manifest_fails_packet_integrity(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    (pkt / "room.html").write_text("<p>edited by hand</p>")
    assert "packet integrity" in refused(vc.verify, pkt, cap, t)


def test_replaced_screenshot_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    shot = cap.parent / "shot.png"
    replacement = _png(4, 3, rgb=b"\x10\x20\x30")         # same size, different pixels
    assert replacement != shot.read_bytes()
    shot.write_bytes(replacement)
    assert "image bytes differ" in refused(vc.verify, pkt, cap, t)


def test_capture_claiming_camera_bound_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    c = json.loads(cap.read_text())
    c["camera_bound"] = True
    cap.write_text(json.dumps(c))
    assert "camera_bound must be false" in refused(vc.verify, pkt, cap, t)


def test_pre_repair_packet_without_room_html_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    m = json.loads((pkt / "packet.json").read_text())
    del m["sha256"]["room_html"]
    (pkt / "packet.json").write_text(json.dumps(m))
    assert "predates the referent repair" in refused(vc.verify, pkt, cap, t)


def test_capture_image_outside_record_folder_refused(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    c = json.loads(cap.read_text())
    c["image"]["file"] = "../packet/render.png"
    cap.write_text(json.dumps(c))
    assert "inside capture.json's folder" in refused(vc.verify, pkt, cap, t)


def test_cli_refuses_with_exit_2_and_never_overwrites(tmp_path):
    pkt, cap, t = genuine(tmp_path)
    assert vc.main(["verify", "--packet-dir", str(pkt), "--capture", str(cap),
                    "--treatment", str(t)]) == 0
    assert vc.main(["verify", "--packet-dir", str(pkt), "--capture", str(cap)]) == 2
    before = cap.read_bytes()
    assert vc.main(["bind", "--packet-dir", str(pkt), "--image", str(cap.parent / "shot.png"),
                    "--out", str(cap)]) == 2
    assert cap.read_bytes() == before


def _run_all_without_pytest() -> int:
    import inspect
    import tempfile
    import traceback
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        with tempfile.TemporaryDirectory() as td:
            kwargs = {"tmp_path": Path(td)} if \
                "tmp_path" in inspect.signature(fn).parameters else {}
            try:
                fn(**kwargs)
                print(f"PASS {name}")
            except Exception:
                failed += 1
                print(f"FAIL {name}")
                traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    if pytest is not None:
        raise SystemExit(pytest.main([__file__, "-v"]))
    raise SystemExit(_run_all_without_pytest())
