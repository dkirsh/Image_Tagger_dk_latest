"""loop/tests/test_run_loop_compare.py — T1.2 comparator tests (contract v0.7).

Deterministic, tmp_path-based, stdlib-runnable (pytest optional). The negative controls
encode the Codex review's executed attacks across three rounds: A1 permutation, A2
invented aperture (round 1); moved-object, NaN, manifest typing, ap00 spelling (round
2); R3-1 target-side bbox asymmetry and R3-2 type-coerced identity (round 3); V04-1
null-as-absent, V04-2 category coercion, V04-3 the $-vs-\\Z regex trap (round 4) — plus
the malformed-input fail-closed sweep. The round-4 additions are exactly the coverage
gaps Codex named: object_bbox null, the long-list bbox, render category type, and
aperture-id trailing whitespace. Round 5 (F2 fallback-multiset purity, F3 strict
RFC 8259 input, F1 marker non-collision pinned) is covered in its own section.
Honest bound: all fixtures synthetic; the
one-real-image run is a separately recorded step (passes_on_synthetic_only stays open
until then).

Run:  PYTHONPATH=. python3 -m pytest loop/tests/test_run_loop_compare.py -v
  or: PYTHONPATH=. python3 loop/tests/test_run_loop_compare.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

try:
    import pytest
except ImportError:
    pytest = None

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "loop"))

import run_loop_compare as rlc  # noqa: E402


TARGET_SCENE = {
    "image_id": "fixture-reception-01", "primary_room_type": "reception",
    "openings": [
        {"kind": "glazed_wall", "bbox_xywh": [0.86, 0.5, 0.26, 0.92]},   # 0: right -> east
        {"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]},         # 1: centre -> north
    ],
    "objects": [
        {"id": "o1", "category": "chair", "evidence": {}},
        {"id": "o2", "category": "desk", "evidence": {}},
    ],
}

GOOD_ROOM = {
    "schema_version": "0.3",
    "apertures": [{"id": "ap0", "kind": "glazed_wall", "wall": "east"},
                  {"id": "ap1", "kind": "door", "wall": "north"}],
    "furniture": [{"id": "o1", "category": "chair"}, {"id": "o2", "category": "desk"}],
}

# A1 (Codex attack, executed + reproduced): two same-kind openings, walls permuted.
A1_TARGET = {
    "image_id": "a1", "openings": [
        {"kind": "window", "bbox_xywh": [0.10, 0.5, 0.1, 0.3]},   # 0 -> west
        {"kind": "window", "bbox_xywh": [0.90, 0.5, 0.1, 0.3]},   # 1 -> east
    ]}
A1_ROOM_SWAPPED = {"schema_version": "0.3",
                   "apertures": [{"id": "ap0", "kind": "window", "wall": "east"},
                                 {"id": "ap1", "kind": "window", "wall": "west"}],
                   "furniture": []}
A1_ROOM_SWAPPED_NO_IDS = {"schema_version": "0.3",
                          "apertures": [{"kind": "window", "wall": "east"},
                                        {"kind": "window", "wall": "west"}],
                          "furniture": []}

# A2 (Codex attack): render invents an aperture the target never had.
A2_TARGET = {"image_id": "a2",
             "openings": [{"kind": "window", "bbox_xywh": [0.10, 0.5, 0.1, 0.3]}]}
A2_ROOM_EXTRA = {"schema_version": "0.3",
                 "apertures": [{"id": "ap0", "kind": "window", "wall": "west"},
                               {"id": "ap7", "kind": "window", "wall": "north"}],
                 "furniture": []}


def make_packet(tmp: Path, room: dict, tamper: bool = False,
                contract_version: str = rlc.CONTRACT_VERSION,
                manifest_override: dict | None = None) -> Path:
    pdir = tmp / "render"
    pdir.mkdir(parents=True, exist_ok=True)
    render_png = b"\x89PNG\r\n\x1a\nFIXTURE-NOT-A-REAL-IMAGE"
    room_b = (json.dumps(room, sort_keys=True) + "\n").encode()
    cam_b = (json.dumps({"position_m": [4, 1.6, 11], "look_at_m": [4, 1.6, 0],
                         "fov_deg": 70, "image_wh": [1280, 720]}) + "\n").encode()
    (pdir / "render.png").write_bytes(render_png)
    (pdir / "room.json").write_bytes(room_b)
    (pdir / "camera.json").write_bytes(cam_b)
    sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
    manifest = {
        "contract_version": contract_version, "run_id": "fixture-run-001", "iter": 0,
        "target_image_id": "fixture", "produced_utc": "2026-08-20T00:00:00+00:00",
        "sha256": {"render_png": sha(render_png), "room_json": sha(room_b),
                   "camera_json": sha(cam_b)},
    }
    if manifest_override:
        manifest.update(manifest_override)
    if tamper:
        (pdir / "room.json").write_bytes(room_b + b" ")
    (pdir / "packet.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return pdir


def write_target(tmp: Path, scene: dict = TARGET_SCENE) -> Path:
    p = tmp / "target_scene.json"
    p.write_text(json.dumps(scene, indent=1), encoding="utf-8")
    return p


def verdict_of(tmp: Path):
    return json.loads((tmp / "verdict" / "verdict.json").read_text())


# ------------------------------------------------------------------ agreement path

def test_good_render_agrees(tmp_path):
    code, msg = rlc.run(write_target(tmp_path), make_packet(tmp_path, GOOD_ROOM),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["wall_layout_diff"]["opening_mismatches"] == []
    assert v["wall_layout_diff"]["extra_render_apertures"] == []
    assert v["identity"] == {"mode": "exact", "unverifiable_kinds": [],
                             "objects_mode": "exact", "position_unverified": []}
    assert v["discrepancy"]["score"] == 0.0
    assert v["verdict"] == "BELOW_THRESHOLD"


# ------------------------------------------------------------------ Codex attack A1

def test_a1_permutation_detected_in_exact_mode(tmp_path):
    """Two same-kind openings with walls swapped MUST both mismatch (v0.1 reported
    agreement here — the false_agreement Codex executed)."""
    code, msg = rlc.run(write_target(tmp_path, A1_TARGET),
                        make_packet(tmp_path, A1_ROOM_SWAPPED),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    mm = v["wall_layout_diff"]["opening_mismatches"]
    assert len(mm) == 2
    assert {m["expected_wall"] for m in mm} == {"west", "east"}
    assert v["discrepancy"]["score"] > 0.0
    assert v["verdict"] == "CONTINUE"


def test_a1_without_ids_never_claims_agreement(tmp_path):
    """No aperture ids -> fallback mode. The multiset matches, so no mismatch is
    provable — but agreement must NOT be claimed for a kind with >=2 openings."""
    code, msg = rlc.run(write_target(tmp_path, A1_TARGET),
                        make_packet(tmp_path, A1_ROOM_SWAPPED_NO_IDS),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["mode"] == "multiset_fallback"
    assert v["identity"]["unverifiable_kinds"] == ["window"]
    assert v["verdict"] == "CONTINUE"          # never BELOW_THRESHOLD when unverifiable


# ------------------------------------------------------------------ Codex attack A2

def test_a2_invented_aperture_is_scored(tmp_path):
    code, msg = rlc.run(write_target(tmp_path, A2_TARGET),
                        make_packet(tmp_path, A2_ROOM_EXTRA),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert len(v["wall_layout_diff"]["extra_render_apertures"]) == 1
    assert v["discrepancy"]["components"]["extra_aperture_frac"] == 0.5
    assert v["discrepancy"]["score"] > 0.0
    assert v["verdict"] == "CONTINUE"


# ------------------------------------------------------------------ classic wrong wall

def test_wrong_wall_render_must_not_report_agreement(tmp_path):
    room = {"schema_version": "0.3",
            "apertures": [{"id": "ap0", "kind": "glazed_wall", "wall": "north"},
                          {"id": "ap1", "kind": "door", "wall": "north"}],
            "furniture": [{"id": "o1", "category": "chair"}, {"id": "o2", "category": "desk"}]}
    code, msg = rlc.run(write_target(tmp_path), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    mm = v["wall_layout_diff"]["opening_mismatches"]
    assert len(mm) == 1 and mm[0]["expected_wall"] == "east" \
        and mm[0]["rendered_wall"] == "north"
    assert v["verdict"] == "CONTINUE"


def test_missing_aperture_reported(tmp_path):
    room = {"schema_version": "0.3",
            "apertures": [{"id": "ap1", "kind": "door", "wall": "north"}],
            "furniture": []}
    code, _ = rlc.run(write_target(tmp_path), make_packet(tmp_path, room),
                      tmp_path / "verdict", None)
    assert code == 0
    v = verdict_of(tmp_path)
    assert any(m["rendered_wall"] == "MISSING"
               for m in v["wall_layout_diff"]["opening_mismatches"])
    assert v["object_diff"]["missing_in_render"] == ["chair", "desk"]


# ------------------------------------------------------------------ wall-rule mirror

def test_wall_rule_and_zone_fallback_match_platform():
    """Mirror of reconstruct.py _center_x/_wall_for @ 3fe1d505. If this breaks, the
    platform rule moved: bump the contract + announce, never silently adapt."""
    assert rlc.wall_for(rlc.center_x({"bbox_xywh": [0.10, 0.5, 0.2, 0.9]})) == "west"
    assert rlc.wall_for(rlc.center_x({"bbox_xywh": [0.86, 0.5, 0.26, 0.92]})) == "east"
    assert rlc.wall_for(rlc.center_x({"bbox_xywh": [0.34, 0, 0.1, 0]})) == "north"
    assert rlc.wall_for(rlc.center_x({"bbox_xywh": [0.66, 0, 0.1, 0]})) == "north"
    # zone fallback, first "_"-token, default 0.5
    assert rlc.wall_for(rlc.center_x({"zone": "left"})) == "west"
    assert rlc.wall_for(rlc.center_x({"zone": "right_third"})) == "east"
    assert rlc.wall_for(rlc.center_x({"zone": "middle"})) == "north"   # unknown -> 0.5
    assert rlc.wall_for(rlc.center_x({})) == "north"                   # no bbox, no zone
    # malformed bbox falls back like the platform, it does not crash or refuse
    assert rlc.wall_for(rlc.center_x({"bbox_xywh": 5})) == "north"
    assert rlc.wall_for(rlc.center_x({"bbox_xywh": ["x", 0, "y", 0]})) == "north"


def test_out_of_range_center_refused(tmp_path):
    scene = {"image_id": "bad", "openings": [{"kind": "window",
                                              "bbox_xywh": [2.0, 0.5, 0.1, 0.3]}]}
    code, msg = rlc.run(write_target(tmp_path, scene),
                        make_packet(tmp_path, GOOD_ROOM), tmp_path / "verdict", None)
    assert code == 2 and "out of [0,1]" in msg


def test_non_structural_kind_skipped_not_missing(tmp_path):
    scene = {"image_id": "ns", "openings": [
        {"kind": "window", "bbox_xywh": [0.10, 0.5, 0.1, 0.3]},
        {"kind": "artwork", "bbox_xywh": [0.50, 0.5, 0.1, 0.3]},   # platform skips this
    ]}
    room = {"schema_version": "0.3",
            "apertures": [{"id": "ap0", "kind": "window", "wall": "west"}],
            "furniture": []}
    code, msg = rlc.run(write_target(tmp_path, scene), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["wall_layout_diff"]["opening_mismatches"] == []
    assert v["wall_layout_diff"]["target_openings"] == 1
    assert v["verdict"] == "BELOW_THRESHOLD"


# ------------------------------------------------------------------ fail-closed sweep

def test_malformed_inputs_refused_not_traceback(tmp_path):
    cases = []
    # openings as an object, not a list
    cases.append({"image_id": "x", "openings": {"kind": "window"}})
    # an opening that is not a mapping
    cases.append({"image_id": "x", "openings": [5]})
    # empty kind
    cases.append({"image_id": "x", "openings": [{"kind": "", "bbox_xywh": [0.1, 0, 0, 0]}]})
    for i, scene in enumerate(cases):
        t = tmp_path / f"s{i}.json"
        t.write_text(json.dumps(scene), encoding="utf-8")
        code, msg = rlc.run(t, make_packet(tmp_path / f"p{i}", GOOD_ROOM),
                            tmp_path / f"v{i}", None)
        assert code == 2, f"case {i}: expected refusal, got {code}: {msg}"

    # sha256 as a scalar in the manifest
    p = make_packet(tmp_path / "psha", GOOD_ROOM, manifest_override={"sha256": "nope"})
    code, msg = rlc.run(write_target(tmp_path), p, tmp_path / "vsha", None)
    assert code == 2 and "sha256" in msg
    # apertures as an object in room.json
    p = make_packet(tmp_path / "pap", {"schema_version": "0.3", "apertures": {"a": 1}})
    code, msg = rlc.run(write_target(tmp_path), p, tmp_path / "vap", None)
    assert code == 2
    # duplicate aperture ids
    p = make_packet(tmp_path / "pdup", {"schema_version": "0.3",
                                        "apertures": [{"id": "ap0", "kind": "door",
                                                       "wall": "north"},
                                                      {"id": "ap0", "kind": "door",
                                                       "wall": "north"}]})
    code, msg = rlc.run(write_target(tmp_path), p, tmp_path / "vdup", None)
    assert code == 2 and "duplicate" in msg


def test_tampered_packet_refused(tmp_path):
    code, msg = rlc.run(write_target(tmp_path),
                        make_packet(tmp_path, GOOD_ROOM, tamper=True),
                        tmp_path / "verdict", None)
    assert code == 2 and "sha256 mismatch" in msg
    assert not (tmp_path / "verdict" / "verdict.json").exists()


def test_wrong_contract_version_refused(tmp_path):
    code, msg = rlc.run(write_target(tmp_path),
                        make_packet(tmp_path, GOOD_ROOM,
                                    contract_version="render-verdict/v0.1"),
                        tmp_path / "verdict", None)
    assert code == 2 and "contract_version" in msg


def test_empty_target_refused(tmp_path):
    t = tmp_path / "empty.json"
    t.write_text("{}", encoding="utf-8")
    code, msg = rlc.run(t, make_packet(tmp_path, GOOD_ROOM), tmp_path / "verdict", None)
    assert code == 2 and "nothing to compare" in msg


# ------------------------------------------------------------------ determinism

def test_byte_identical_reruns(tmp_path):
    t = write_target(tmp_path)
    p = make_packet(tmp_path, GOOD_ROOM)
    rlc.run(t, p, tmp_path / "v1", 0.0)
    rlc.run(t, p, tmp_path / "v2", 0.0)
    b1 = (tmp_path / "v1" / "verdict.json").read_bytes()
    b2 = (tmp_path / "v2" / "verdict.json").read_bytes()
    assert b1 == b2
    assert hashlib.sha256(b1).hexdigest() == hashlib.sha256(b2).hexdigest()




# ------------------------------------------------------------------ Codex round-2 regressions

MOVED_TARGET = {"image_id": "r2", "openings": [
    {"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
    "objects": [{"id": "o1", "category": "chair",
                 "object_bbox": [0.10, 0.6, 0.1, 0.2], "evidence": {}}]}


def _moved_room(src_bbox):
    return {"schema_version": "0.3",
            "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
            "furniture": [{"id": "o1", "category": "chair", "x_m": 1.0, "y_m": 1.0,
                           "_source_bbox": src_bbox}]}


def test_r2_moved_object_never_agrees(tmp_path):
    """Codex round-2 HIGH: chair crossed the room -> v0.2 said agreement. Dead in v0.3."""
    code, msg = rlc.run(write_target(tmp_path, MOVED_TARGET),
                        make_packet(tmp_path, _moved_room([0.90, 0.6, 0.1, 0.2])),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    mv = v["object_diff"]["moved"]
    assert len(mv) == 1 and mv[0]["object_id"] == "o1"
    assert mv[0]["offset_norm"] == 0.8
    assert v["discrepancy"]["components"]["object_moved_frac"] == 1.0
    assert v["verdict"] == "CONTINUE"


def test_r2_matching_source_bbox_agrees(tmp_path):
    code, msg = rlc.run(write_target(tmp_path, MOVED_TARGET),
                        make_packet(tmp_path, _moved_room([0.10, 0.6, 0.1, 0.2])),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["object_diff"]["moved"] == []
    assert v["verdict"] == "BELOW_THRESHOLD"


def test_r2_position_claim_without_echo_blocks_agreement(tmp_path):
    """Target claims a bbox; furniture omits _source_bbox -> unverifiable, no agreement."""
    room = {"schema_version": "0.3",
            "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
            "furniture": [{"id": "o1", "category": "chair"}]}
    code, msg = rlc.run(write_target(tmp_path, MOVED_TARGET), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["position_unverified"] == ["o1"]
    assert v["verdict"] == "CONTINUE"


def test_r2_nan_iter_refused_not_serialized(tmp_path):
    """Since v0.6 (F3) the refusal happens at PARSE: NaN in the manifest is a non-RFC
    8259 document and never reaches the iter type check. Refusal either way."""
    p = make_packet(tmp_path, GOOD_ROOM, manifest_override={"iter": float("nan")})
    code, msg = rlc.run(write_target(tmp_path), p, tmp_path / "verdict", None)
    assert code == 2 and ("non-finite" in msg or "iter" in msg)
    assert not (tmp_path / "verdict" / "verdict.json").exists()


def test_r2_manifest_type_sweep_refused(tmp_path):
    for override, frag in (({"iter": "zero"}, "iter"),
                           ({"produced_utc": None}, "produced_utc"),
                           ({"run_id": 7}, "run_id")):
        d = tmp_path / frag
        p = make_packet(d, GOOD_ROOM, manifest_override=override)
        code, msg = rlc.run(write_target(tmp_path), p, d / "v", None)
        assert code == 2, f"{override}: expected refusal, got {code}: {msg}"


def test_r2_ap00_not_labelled_exact(tmp_path):
    room = {"schema_version": "0.3",
            "apertures": [{"id": "ap00", "kind": "glazed_wall", "wall": "east"},
                          {"id": "ap1", "kind": "door", "wall": "north"}],
            "furniture": [{"id": "o1", "category": "chair"},
                          {"id": "o2", "category": "desk"}]}
    code, msg = rlc.run(write_target(tmp_path), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["mode"] == "multiset_fallback"   # ap00 is not platform spelling
    assert v["verdict"] == "CONTINUE"                     # strict: no unverified agreement


def test_r2_idless_single_opening_strict_vs_lenient(tmp_path):
    """David's design question, mechanized: strict default never agrees without ids;
    the explicit flag permits it for stub producers."""
    scene = {"image_id": "s1",
             "openings": [{"kind": "window", "bbox_xywh": [0.10, 0.5, 0.1, 0.3]}]}
    room = {"schema_version": "0.3",
            "apertures": [{"kind": "window", "wall": "west"}], "furniture": []}
    t = write_target(tmp_path, scene)
    code, _ = rlc.run(t, make_packet(tmp_path, room), tmp_path / "v_strict", 0.0)
    assert code == 0
    v = json.loads((tmp_path / "v_strict" / "verdict.json").read_text())
    assert v["verdict"] == "CONTINUE" and v["agreement_policy"] == "strict"
    code, _ = rlc.run(t, make_packet(tmp_path / "p2", room), tmp_path / "v_lenient", 0.0,
                      allow_unverified=True)
    assert code == 0
    v = json.loads((tmp_path / "v_lenient" / "verdict.json").read_text())
    assert v["verdict"] == "BELOW_THRESHOLD" and v["agreement_policy"] == "allow_unverified"


def test_r2_category_mismatch_on_matched_id(tmp_path):
    room = {"schema_version": "0.3",
            "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
            "furniture": [{"id": "o1", "category": "sofa",
                           "_source_bbox": [0.10, 0.6, 0.1, 0.2]}]}
    code, msg = rlc.run(write_target(tmp_path, MOVED_TARGET), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["object_diff"]["missing_in_render"] == ["chair"]
    assert v["object_diff"]["extra_in_render"] == ["sofa"]
    assert v["verdict"] == "CONTINUE"




def test_vacuous_objects_reported_not_dressed_as_exact(tmp_path):
    """Round-3 finding from the real smoke: no objects + no furniture must say vacuous."""
    scene = {"image_id": "v", "openings": [{"kind": "door", "bbox_xywh": [0.5, 0.5, 0.1, 0.3]}]}
    room = {"schema_version": "0.3", "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
            "furniture": []}
    code, msg = rlc.run(write_target(tmp_path, scene), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["objects_mode"] == "vacuous"
    assert v["identity"]["mode"] == "exact"
    assert v["verdict"] == "BELOW_THRESHOLD"     # nothing claimed = nothing unverified


def test_vacuous_openings_reported(tmp_path):
    scene = {"image_id": "v2",
             "objects": [{"id": "o1", "category": "chair", "evidence": {}}]}
    room = {"schema_version": "0.3", "apertures": [],
            "furniture": [{"id": "o1", "category": "chair"}]}
    code, msg = rlc.run(write_target(tmp_path, scene), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["mode"] == "vacuous"
    assert v["identity"]["objects_mode"] == "exact"
    assert v["verdict"] == "BELOW_THRESHOLD"


# ------------------------------------------------------------------ Codex round-3 regressions

def _r3_room(furn):
    return {"schema_version": "0.3",
            "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
            "furniture": furn}


_R3_ECHO = [{"id": "o1", "category": "chair", "_source_bbox": [0.10, 0.6, 0.1, 0.2]}]


def test_r3_malformed_target_bbox_blocks_agreement(tmp_path):
    """R3-1: a target bbox that is PRESENT but unreadable is a claim that cannot be
    verified — position_unverified + CONTINUE, symmetric with an unreadable echo.
    v0.3 silently skipped these and agreed."""
    bad_bboxes = ("0.1,0.6,0.1,0.2",              # string, not a list
                  [0.10, 0.6, 0.1],               # too short
                  [0.10, 0.6, 0.1, 0.2, 0.5],     # too long (round-4 named gap)
                  [0.10, 0.6, 0.1, "x"],          # non-numeric entry
                  [0.10, 0.6, 0.1, True],         # bool is not a number here
                  {"x": 0.1, "y": 0.6},           # mapping, not a sequence
                  None)                           # V04-1: present null is NOT absent
    for i, bb in enumerate(bad_bboxes):
        scene = {"image_id": f"r3a{i}",
                 "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
                 "objects": [{"id": "o1", "category": "chair", "object_bbox": bb,
                              "evidence": {}}]}
        t = tmp_path / f"s{i}.json"
        t.write_text(json.dumps(scene), encoding="utf-8")
        code, msg = rlc.run(t, make_packet(tmp_path / f"p{i}", _r3_room(_R3_ECHO)),
                            tmp_path / f"v{i}", threshold=0.0)
        assert code == 0, f"bbox case {i}: {msg}"
        v = json.loads((tmp_path / f"v{i}" / "verdict.json").read_text())
        assert v["identity"]["position_unverified"] == ["o1"], f"bbox case {i}"
        assert v["verdict"] == "CONTINUE", f"bbox case {i}: agreed on unreadable claim"


def test_r3_miskeyed_bbox_xywh_on_object_blocks_agreement(tmp_path):
    """R3-1: bbox_xywh is the OPENINGS spelling; on an object it is a mis-keyed claim,
    not an absent one — unverifiable, never silently ignored."""
    scene = {"image_id": "r3k",
             "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
             "objects": [{"id": "o1", "category": "chair",
                          "bbox_xywh": [0.10, 0.6, 0.1, 0.2], "evidence": {}}]}
    code, msg = rlc.run(write_target(tmp_path, scene),
                        make_packet(tmp_path, _r3_room(_R3_ECHO)),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["position_unverified"] == ["o1"]
    assert v["verdict"] == "CONTINUE"


def test_r3_genuinely_absent_bbox_owes_nothing(tmp_path):
    """R3-1 boundary: no object_bbox AND no bbox_xywh = no position claim was made, so
    nothing is owed and identity agreement stands."""
    scene = {"image_id": "r3n",
             "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
             "objects": [{"id": "o1", "category": "chair", "evidence": {}}]}
    code, msg = rlc.run(write_target(tmp_path, scene),
                        make_packet(tmp_path, _r3_room(_R3_ECHO)),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["position_unverified"] == []
    assert v["verdict"] == "BELOW_THRESHOLD"


def test_r3_nonstring_target_identity_refused(tmp_path):
    """R3-2: the scene schema requires string ids/categories; v0.3's str() coercion let
    id 7 and id "7" collide as the same object. Fail-closed now."""
    cases = ([{"id": 7, "category": "chair", "evidence": {}}],
             [{"id": None, "category": "chair", "evidence": {}}],
             [{"id": "", "category": "chair", "evidence": {}}],
             [{"id": "o1", "category": 7, "evidence": {}}],
             [{"id": "o1", "category": "", "evidence": {}}])
    for i, objs in enumerate(cases):
        scene = {"image_id": f"r3t{i}",
                 "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
                 "objects": objs}
        t = tmp_path / f"s{i}.json"
        t.write_text(json.dumps(scene), encoding="utf-8")
        code, msg = rlc.run(t, make_packet(tmp_path / f"p{i}", _r3_room(_R3_ECHO)),
                            tmp_path / f"v{i}", None)
        assert code == 2, f"case {i}: expected refusal, got {code}: {msg}"
        assert "non-empty string" in msg, f"case {i}: {msg}"


def test_r3_nonstring_render_id_falls_back_not_exact(tmp_path):
    """R3-2 render side: furniture id 7 is the PRODUCER's defect — the comparator must
    not coerce it into a match. Degrade to multiset_fallback; strict never agrees."""
    scene = {"image_id": "r3r",
             "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
             "objects": [{"id": "7", "category": "chair", "evidence": {}}]}
    room = _r3_room([{"id": 7, "category": "chair"}])
    code, msg = rlc.run(write_target(tmp_path, scene), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["objects_mode"] == "multiset_fallback"
    assert v["verdict"] == "CONTINUE"


# ------------------------------------------------------------------ Codex round-4 regressions

def test_v04_1_null_object_bbox_blocks_agreement(tmp_path):
    """V04-1 (round-4 HIGH): object_bbox: null is a PRESENT claim that cannot be read
    — key-presence test, not value-shape enumeration. v0.4 agreed here."""
    scene = {"image_id": "v04n",
             "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
             "objects": [{"id": "o1", "category": "chair", "object_bbox": None,
                          "evidence": {}}]}
    code, msg = rlc.run(write_target(tmp_path, scene),
                        make_packet(tmp_path, _r3_room(_R3_ECHO)),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["position_unverified"] == ["o1"]
    assert v["verdict"] == "CONTINUE"


def test_v04_null_containers_refused(tmp_path):
    """Null policy (decided once, round 4): a present-null CONTAINER is a malformed
    document, exit 2 — on either side of the seam. Only a missing key is absent."""
    # target side
    for i, scene in enumerate((
            {"image_id": "n0", "openings": None,
             "objects": [{"id": "o1", "category": "chair", "evidence": {}}]},
            {"image_id": "n1", "objects": None,
             "openings": [{"kind": "door", "bbox_xywh": [0.5, 0.5, 0.1, 0.3]}]})):
        t = tmp_path / f"s{i}.json"
        t.write_text(json.dumps(scene), encoding="utf-8")
        code, msg = rlc.run(t, make_packet(tmp_path / f"p{i}", _r3_room(_R3_ECHO)),
                            tmp_path / f"v{i}", None)
        assert code == 2 and "null" in msg, f"target case {i}: {code} {msg}"
    # render side
    for j, room in enumerate((
            {"schema_version": "0.3", "apertures": None, "furniture": []},
            {"schema_version": "0.3",
             "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
             "furniture": None})):
        p = make_packet(tmp_path / f"pr{j}", room)
        code, msg = rlc.run(write_target(tmp_path), p, tmp_path / f"vr{j}", None)
        assert code == 2 and "null" in msg, f"render case {j}: {code} {msg}"


def test_v04_2_render_category_type_never_matches(tmp_path):
    """V04-2 (round-4 HIGH): target "7" must NOT match render 7; target "None" must
    NOT match render null. No str() coercion on the category path."""
    for i, (tcat, rcat, marker) in enumerate((
            ("7", 7, "<unreadable-category:int>"),
            ("None", None, "<unreadable-category:NoneType>"),
            ("True", True, "<unreadable-category:bool>"))):
        scene = {"image_id": f"v042-{i}",
                 "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
                 "objects": [{"id": "o1", "category": tcat, "evidence": {}}]}
        room = _r3_room([{"id": "o1", "category": rcat,
                          "_source_bbox": [0.10, 0.6, 0.1, 0.2]}])
        t = tmp_path / f"s{i}.json"
        t.write_text(json.dumps(scene), encoding="utf-8")
        code, msg = rlc.run(t, make_packet(tmp_path / f"p{i}", room),
                            tmp_path / f"v{i}", threshold=0.0)
        assert code == 0, f"case {i}: {msg}"
        v = json.loads((tmp_path / f"v{i}" / "verdict.json").read_text())
        assert v["object_diff"]["missing_in_render"] == [tcat], f"case {i}"
        assert v["object_diff"]["extra_in_render"] == [marker], f"case {i}"
        assert v["verdict"] == "CONTINUE", f"case {i}: coerced category agreed"


def test_v04_2_marker_string_cannot_false_match(tmp_path):
    """The marker is display-only: a target category LITERALLY equal to the marker
    text still cannot match a non-string render category."""
    scene = {"image_id": "v042m",
             "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
             "objects": [{"id": "o1", "category": "<unreadable-category:int>",
                          "evidence": {}}]}
    room = _r3_room([{"id": "o1", "category": 7,
                      "_source_bbox": [0.10, 0.6, 0.1, 0.2]}])
    code, msg = rlc.run(write_target(tmp_path, scene), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["object_diff"]["matched"] == []
    assert v["verdict"] == "CONTINUE"


def test_v04_3_aperture_id_trailing_newline_not_exact(tmp_path):
    """V04-3 (round-4 MEDIUM-HIGH): 'ap0\\n' defeated the ^...$ spelling gate because
    Python $ matches before a trailing newline. \\Z closes it: fallback, never exact."""
    for i, bad_id in enumerate(("ap0\n", "ap0\t", "ap0 ")):
        room = {"schema_version": "0.3",
                "apertures": [{"id": bad_id, "kind": "glazed_wall", "wall": "east"},
                              {"id": "ap1", "kind": "door", "wall": "north"}],
                "furniture": [{"id": "o1", "category": "chair"},
                              {"id": "o2", "category": "desk"}]}
        p = make_packet(tmp_path / f"p{i}", room)
        code, msg = rlc.run(write_target(tmp_path), p, tmp_path / f"v{i}",
                            threshold=0.0)
        assert code == 0, f"case {i}: {msg}"
        v = json.loads((tmp_path / f"v{i}" / "verdict.json").read_text())
        assert v["identity"]["mode"] == "multiset_fallback", f"case {i}: {bad_id!r}"
        assert v["verdict"] == "CONTINUE", f"case {i}"


def test_v04_4_negative_iter_refused(tmp_path):
    p = make_packet(tmp_path, GOOD_ROOM, manifest_override={"iter": -1})
    code, msg = rlc.run(write_target(tmp_path), p, tmp_path / "verdict", None)
    assert code == 2 and "iter" in msg
    assert not (tmp_path / "verdict" / "verdict.json").exists()


# ------------------------------------------------------------------ Codex round-5 regressions

def test_f3_nonfinite_constants_refused_at_parse(tmp_path):
    """F3: NaN/Infinity/-Infinity refuse exit 2 at the door on every PARSED input
    document (target scene, room.json, packet.json). camera.json is an
    integrity-checked opaque sidecar — hashed, never parsed (round-6 wording scope)."""
    # target scene
    t = tmp_path / "nan_scene.json"
    t.write_text('{"image_id": "x", "openings": [{"kind": "door", '
                 '"bbox_xywh": [NaN, 0.5, 0.1, 0.3]}]}', encoding="utf-8")
    code, msg = rlc.run(t, make_packet(tmp_path / "p0", GOOD_ROOM), tmp_path / "v0", None)
    assert code == 2 and "non-finite" in msg
    # room.json (rewrite bytes + fix the sha so integrity passes and parsing is reached)
    p = make_packet(tmp_path / "p1", GOOD_ROOM)
    room_b = ('{"schema_version": "0.3", "apertures": [{"id": "ap0", "kind": "door", '
              '"wall": "north"}], "furniture": [], "x": Infinity}\n').encode()
    (p / "room.json").write_bytes(room_b)
    mf = json.loads((p / "packet.json").read_text())
    mf["sha256"]["room_json"] = hashlib.sha256(room_b).hexdigest()
    (p / "packet.json").write_text(json.dumps(mf))
    code, msg = rlc.run(write_target(tmp_path), p, tmp_path / "v1", None)
    assert code == 2 and "non-finite" in msg
    # packet.json manifest
    p2 = make_packet(tmp_path / "p2", GOOD_ROOM)
    mtext = (p2 / "packet.json").read_text().replace('"iter": 0', '"iter": -Infinity')
    (p2 / "packet.json").write_text(mtext)
    code, msg = rlc.run(write_target(tmp_path), p2, tmp_path / "v2", None)
    assert code == 2 and "non-finite" in msg


def test_f2_unreadable_aperture_never_enters_fallback_multiset(tmp_path):
    """F2: a fallback-mode aperture with a non-string kind or wall must be reported as
    an unreadable extra, never matched — and a target kind that literally equals the
    marker text still finds nothing to match."""
    scene = {"image_id": "f2",
             "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}]}
    room = {"schema_version": "0.3",
            "apertures": [{"kind": "door", "wall": "north"},     # readable, no id
                          {"kind": 7, "wall": "north"},          # unreadable kind
                          {"kind": "window", "wall": None}],     # unreadable wall
            "furniture": []}
    code, msg = rlc.run(write_target(tmp_path, scene), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["mode"] == "multiset_fallback"
    extras = v["wall_layout_diff"]["extra_render_apertures"]
    assert "<non-string:int>->north" in extras
    assert "window-><non-string:NoneType>" in extras
    assert v["wall_layout_diff"]["opening_mismatches"] == []     # the readable door matched
    assert v["verdict"] == "CONTINUE"                            # fallback never agrees


def test_f1_generated_marker_cannot_collide_with_literal(tmp_path):
    """F1 (round 5, examined, no defect): pinned as a regression. A target category
    that IS the marker text does not match a render category that GENERATES it."""
    scene = {"image_id": "f1",
             "openings": [{"kind": "door", "bbox_xywh": [0.50, 0.55, 0.06, 0.35]}],
             "objects": [{"id": "o1", "category": "<unreadable-category:int>",
                          "evidence": {}}]}
    room = {"schema_version": "0.3",
            "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
            "furniture": [{"id": "o1", "category": 7,
                           "_source_bbox": [0.1, 0.6, 0.1, 0.2]}]}
    code, msg = rlc.run(write_target(tmp_path, scene), make_packet(tmp_path, room),
                        tmp_path / "verdict", threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["object_diff"]["matched"] == []
    assert v["verdict"] == "CONTINUE"
    # and both sides genuinely claiming the same literal string IS agreement
    room2 = {"schema_version": "0.3",
             "apertures": [{"id": "ap0", "kind": "door", "wall": "north"}],
             "furniture": [{"id": "o1", "category": "<unreadable-category:int>"}]}
    code, msg = rlc.run(write_target(tmp_path, scene), make_packet(tmp_path / "p2", room2),
                        tmp_path / "v2", threshold=0.0)
    assert code == 0, msg
    v2 = json.loads((tmp_path / "v2" / "verdict.json").read_text())
    assert v2["object_diff"]["matched"] == ["<unreadable-category:int>"]
    assert v2["verdict"] == "BELOW_THRESHOLD"


def test_f3_overflow_inf_bbox_caught_by_value_check(tmp_path):
    """The stated F3 bound, exercised: 1e999 parses as a plain (infinite) number in any
    JSON parser, so the PARSER cannot refuse it — _finite must, via _bbox_ok."""
    t = tmp_path / "inf_scene.json"
    t.write_text('{"image_id": "inf", '
                 '"openings": [{"kind": "door", "bbox_xywh": [0.5, 0.55, 0.06, 0.35]}], '
                 '"objects": [{"id": "o1", "category": "chair", '
                 '"object_bbox": [1e999, 0.6, 0.1, 0.2], "evidence": {}}]}',
                 encoding="utf-8")
    room = _r3_room(_R3_ECHO)
    code, msg = rlc.run(t, make_packet(tmp_path, room), tmp_path / "verdict",
                        threshold=0.0)
    assert code == 0, msg
    v = verdict_of(tmp_path)
    assert v["identity"]["position_unverified"] == ["o1"]
    assert v["verdict"] == "CONTINUE"


# ------------------------------------------------------------------ Codex round-6 regression

def test_fresh1_packet_member_as_directory_refused(tmp_path):
    """FRESH-1 (round-6 HIGH, the only accepted finding): a packet member that is a
    directory must REFUSE exit 2, never traceback — symmetric with the target side,
    which already refused cleanly. v0.6 raised IsADirectoryError through run()."""
    for member in ("packet.json", "room.json", "render.png", "camera.json"):
        p = make_packet(tmp_path / member.replace(".", "_"), GOOD_ROOM)
        victim = p / member
        victim.unlink()
        victim.mkdir()                      # the file is now a DIRECTORY
        code, msg = rlc.run(write_target(tmp_path), p,
                            tmp_path / f"v_{member.replace('.', '_')}", None)
        assert code == 2, f"{member}: expected refusal, got {code}: {msg}"
        assert msg.startswith("REFUSED"), f"{member}: {msg}"
    # control: target-as-directory refused cleanly before and still does
    tdir = tmp_path / "target_as_dir"
    tdir.mkdir()
    code, msg = rlc.run(tdir, make_packet(tmp_path / "ok", GOOD_ROOM),
                        tmp_path / "v_t", None)
    assert code == 2 and "REFUSED" in msg


# ------------------------------------------------------------------ stdlib runner

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
