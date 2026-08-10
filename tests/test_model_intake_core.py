from __future__ import annotations

import copy
import json
import struct

import pytest

from model_intake_core.attestation import validate_readiness_attestation
from model_intake_core.digests import (
    build_artifact_manifest,
    canonical_json_bytes,
    package_digest,
    sha256_json,
)
from model_intake_core.glb_preflight import AuditLimits, audit_glb
from model_intake_core.scene_contract import validate_scene_semantics
from model_intake_core.sprint_ledger import ready_sprints, validate_ledger


def _pad(data: bytes, byte: bytes) -> bytes:
    return data + byte * ((-len(data)) % 4)


def _glb_bytes(document: dict, binary: bytes = b"\x00" * 12) -> bytes:
    document = copy.deepcopy(document)
    document["buffers"] = [{"byteLength": len(binary)}]
    json_chunk = _pad(json.dumps(document, separators=(",", ":")).encode(), b" ")
    binary_chunk = _pad(binary, b"\x00")
    body = (
        struct.pack("<II", len(json_chunk), 0x4E4F534A)
        + json_chunk
        + struct.pack("<II", len(binary_chunk), 0x004E4942)
        + binary_chunk
    )
    return struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + body


def _minimal_document() -> dict:
    return {
        "asset": {"version": "2.0", "generator": "test"},
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": 12}],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": 3,
                "type": "VEC3",
                "min": [0, 0, 0],
                "max": [1, 1, 0],
            }
        ],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
        "nodes": [{"mesh": 0}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }


def test_glb_preflight_accepts_structural_fixture_but_requires_review(tmp_path):
    source = tmp_path / "valid.glb"
    source.write_bytes(_glb_bytes(_minimal_document()))
    report = audit_glb(source)
    assert report.preflight_passed
    assert report.status == "REVIEW_REQUIRED"
    assert report.counts["triangles_estimated"] == 1
    assert len(report.profile_sha256) == 64
    assert {item.code for item in report.findings} >= {
        "PHYSICAL_SCALE_REQUIRES_CONFIRMATION",
        "ARCHITECTURAL_SEMANTICS_NOT_ESTABLISHED",
    }


def test_glb_preflight_rejects_wrong_magic(tmp_path):
    data = bytearray(_glb_bytes(_minimal_document()))
    data[:4] = b"NOPE"
    source = tmp_path / "renamed.glb"
    source.write_bytes(data)
    report = audit_glb(source)
    assert not report.preflight_passed
    assert "GLB_MAGIC_INVALID" in {item.code for item in report.findings}


def test_glb_preflight_rejects_truncated_chunk(tmp_path):
    data = _glb_bytes(_minimal_document())[:-2]
    data = data[:8] + struct.pack("<I", len(data)) + data[12:]
    source = tmp_path / "truncated.glb"
    source.write_bytes(data)
    report = audit_glb(source)
    assert not report.preflight_passed
    assert "GLB_CHUNK_TRUNCATED" in {item.code for item in report.findings}


def test_glb_preflight_rejects_external_image(tmp_path):
    document = _minimal_document()
    document["images"] = [{"uri": "https://example.invalid/texture.png"}]
    source = tmp_path / "external.glb"
    source.write_bytes(_glb_bytes(document))
    report = audit_glb(source)
    assert not report.preflight_passed
    assert "EXTERNAL_RESOURCE_REJECTED" in {item.code for item in report.findings}


def test_glb_preflight_rejects_unenabled_required_extension(tmp_path):
    document = _minimal_document()
    document["extensionsUsed"] = ["KHR_draco_mesh_compression"]
    document["extensionsRequired"] = ["KHR_draco_mesh_compression"]
    source = tmp_path / "draco.glb"
    source.write_bytes(_glb_bytes(document))
    rejected = audit_glb(source)
    accepted_profile = audit_glb(
        source, allowed_extensions={"KHR_draco_mesh_compression"}
    )
    assert "REQUIRED_EXTENSION_UNSUPPORTED" in {
        item.code for item in rejected.findings
    }
    assert accepted_profile.preflight_passed


def test_glb_preflight_enforces_triangle_limit(tmp_path):
    document = _minimal_document()
    document["accessors"][0]["count"] = 30
    source = tmp_path / "many.glb"
    source.write_bytes(_glb_bytes(document))
    report = audit_glb(source, limits=AuditLimits(max_triangles=5))
    assert not report.preflight_passed
    assert "TRIANGLES_ESTIMATED_LIMIT_EXCEEDED" in {
        item.code for item in report.findings
    }


def test_canonical_digest_is_order_independent_and_rejects_nan():
    assert sha256_json({"b": 2, "a": 1}) == sha256_json({"a": 1, "b": 2})
    with pytest.raises(ValueError):
        canonical_json_bytes({"bad": float("nan")})


def test_package_digest_changes_with_artifact_bytes(tmp_path):
    (tmp_path / "raw").mkdir()
    source = tmp_path / "raw" / "source.glb"
    source.write_bytes(b"first")
    first = package_digest(build_artifact_manifest(tmp_path, ["raw/source.glb"]))
    source.write_bytes(b"second")
    second = package_digest(build_artifact_manifest(tmp_path, ["raw/source.glb"]))
    assert first != second


def test_package_manifest_rejects_traversal_and_missing_file(tmp_path):
    with pytest.raises(ValueError):
        build_artifact_manifest(tmp_path, ["raw/../escape.glb"])
    with pytest.raises(FileNotFoundError):
        build_artifact_manifest(tmp_path, ["raw/missing.glb"])


def _attestation() -> dict:
    source_sha = "a" * 64
    scene_sha = "b" * 64
    profile_sha = "c" * 64

    def confirmation(kind: str, user: str) -> dict:
        return {
            "kind": kind,
            "user_id": user,
            "role_id": kind + "_reviewer",
            "confirmed_at": "2026-07-29T20:00:00+02:00",
            "scope": "single-level foyer isovist",
            "assistance_policy": "expert-debug-v0",
            "statement": "Reviewed the specified scope.",
            "source_sha256": source_sha,
            "effective_scene_sha256": scene_sha,
            "assurance_profile_sha256": profile_sha,
            "machine_suggestion_shown_before_judgment": False,
        }

    return {
        "schema_version": "model_readiness_attestation_v0",
        "attestation_id": "attestation-1",
        "state": "ACTIVE",
        "model_id": "model-1",
        "revision_id": "rev-1",
        "source_sha256": source_sha,
        "effective_scene_sha256": scene_sha,
        "package_manifest_sha256": "d" * 64,
        "assurance_profile": {
            "id": "single_level_isovist_v0",
            "sha256": profile_sha,
        },
        "gate_receipts": [
            {
                "gate_id": "glb-preflight",
                "status": "PASS",
                "receipt_sha256": "e" * 64,
                "validator": "model_intake_core.glb_preflight",
                "validator_version": "0.1",
                "checked_at": "2026-07-29T20:00:00+02:00",
                "negative_control": "wrong-magic fixture rejected",
            }
        ],
        "confirmations": [
            confirmation("technical_geometry", "tanishq"),
            confirmation("semantic_use_context", "stephan"),
        ],
        "derived_artifacts": [
            {
                "kind": "plan_grid",
                "path": "derived/plan_grid.npz",
                "sha256": "f" * 64,
            }
        ],
        "issued_by": {
            "checker_id": "independent-checker",
            "checker_not_author": True,
        },
        "issued_at": "2026-07-29T20:10:00+02:00",
        "limitations": ["Single level and eye-level visibility only."],
    }


def test_readiness_attestation_accepts_bound_independent_review():
    assert validate_readiness_attestation(_attestation()) == []


def test_readiness_attestation_rejects_stale_and_dual_role_confirmation():
    attestation = _attestation()
    attestation["confirmations"][1]["user_id"] = "tanishq"
    attestation["confirmations"][1]["effective_scene_sha256"] = "0" * 64
    codes = {
        item.code for item in validate_readiness_attestation(attestation)
    }
    assert codes >= {"DUAL_ROLE_CONFIRMATION", "CONFIRMATION_SCENE_STALE"}


def test_readiness_attestation_rejects_checker_confirmer_and_failed_gate():
    attestation = _attestation()
    attestation["issued_by"]["checker_id"] = "stephan"
    attestation["gate_receipts"][0]["status"] = "FAIL"
    codes = {
        item.code for item in validate_readiness_attestation(attestation)
    }
    assert codes >= {"CHECKER_IS_CONFIRMER", "GATE_NOT_PASSED"}


def _scene() -> dict:
    return {
        "revision_id": "rev-1",
        "status": "ANALYSIS_READY",
        "source": {"stored_path": "raw/source.glb"},
        "bounds_m": {"min": [0, 0, 0], "max": [5, 3, 5]},
        "coordinates": {"units_confirmed": True, "axes_confirmed": True},
        "levels": [{"id": "level-1"}],
        "elements": [
            {
                "id": "floor-1",
                "level_id": "level-1",
                "translation_m": [0, 0, 0],
                "rotation_xyzw": [0, 0, 0, 1],
                "scale": [1, 1, 1],
                "bounds_m": {"min": [0, 0, 0], "max": [5, 0.1, 5]},
            }
        ],
        "spaces": [
            {
                "id": "space-1",
                "level_id": "level-1",
                "boundary_element_ids": ["floor-1"],
            }
        ],
        "anchors": [
            {
                "id": "entrance-1",
                "level_id": "level-1",
                "element_id": "floor-1",
                "space_id": "space-1",
            }
        ],
        "walkability": {
            "walkable_element_ids": ["floor-1"],
            "obstruction_element_ids": [],
            "vertical_connection_element_ids": [],
        },
        "audit_findings": [],
        "annotations": [],
        "confirmations": [
            {"kind": "technical_geometry", "revision_id": "rev-1"},
            {"kind": "semantic_use_context", "revision_id": "rev-1"},
        ],
        "artifacts": [
            {"kind": "raw_source", "path": "raw/source.glb"},
            {"kind": "plan_grid", "path": "derived/plan_grid.npz"},
        ],
    }


def test_scene_semantics_accepts_consistent_analysis_scene():
    assert validate_scene_semantics(_scene()) == []


def test_scene_semantics_rejects_broken_reference_and_duplicate_id():
    scene = _scene()
    scene["anchors"][0]["id"] = "floor-1"
    scene["anchors"][0]["space_id"] = "missing-space"
    codes = {item.code for item in validate_scene_semantics(scene)}
    assert codes >= {"ID_NOT_UNIQUE", "SPACE_REFERENCE_INVALID"}


def test_scene_semantics_rejects_false_analysis_readiness():
    scene = _scene()
    scene["coordinates"]["units_confirmed"] = False
    scene["confirmations"] = scene["confirmations"][:1]
    scene["artifacts"] = scene["artifacts"][:1]
    scene["audit_findings"] = [
        {"id": "finding-1", "severity": "error", "state": "open"}
    ]
    codes = {item.code for item in validate_scene_semantics(scene)}
    assert codes >= {
        "READY_WITHOUT_UNITS",
        "READY_WITH_OPEN_ERRORS",
        "SEMANTIC_CONFIRMATION_MISSING",
        "PLAN_GRID_MISSING",
    }


def test_scene_semantics_rejects_transform_bounds_and_path_bypasses():
    scene = _scene()
    scene["source"]["stored_path"] = "raw/../escape.glb"
    scene["bounds_m"] = {"min": [5, 0, 0], "max": [1, 3, 5]}
    scene["elements"][0]["scale"] = [-1, 1, 1]
    scene["elements"][0]["rotation_xyzw"] = [0, 0, 0, 0]
    codes = {item.code for item in validate_scene_semantics(scene)}
    assert codes >= {
        "PACKAGE_PATH_UNSAFE",
        "BOUNDS_INVERTED",
        "SCALE_INVALID",
        "QUATERNION_NOT_UNIT",
    }


def test_scene_semantics_rejects_accepted_error_and_wrong_revision():
    scene = _scene()
    scene["audit_findings"] = [
        {"id": "finding-1", "severity": "error", "state": "accepted"}
    ]
    scene["confirmations"][0]["revision_id"] = "old-revision"
    codes = {item.code for item in validate_scene_semantics(scene)}
    assert codes >= {
        "READY_WITH_OPEN_ERRORS",
        "CONFIRMATION_REVISION_MISMATCH",
    }


def _evidence(negative: str = "bad fixture rejected") -> dict:
    return {
        "command": "pytest -q",
        "outcome": "pass",
        "verified_at": "2026-07-29T20:00:00+02:00",
        "negative_control": negative,
    }


def _ledger() -> dict:
    return {
        "schema_version": "model_intake_sprint_ledger_v0",
        "program_id": "model-intake",
        "sprints": [
            {
                "id": "MI-00",
                "status": "DONE",
                "depends_on": [],
                "preconditions": [
                    {
                        "id": "contract-written",
                        "state": "PASS",
                        "owner": "codex",
                        "required_result": "contract exists",
                        "evidence": _evidence("invalid schema rejected"),
                    }
                ],
                "acceptance_checks": [
                    {
                        "id": "contract-tested",
                        "state": "PASS",
                        "owner": "codex",
                        "required_result": "positive and negative fixtures",
                        "evidence": _evidence(),
                    }
                ],
            },
            {
                "id": "MI-01",
                "status": "PENDING",
                "depends_on": ["MI-00"],
                "preconditions": [
                    {
                        "id": "fixture-ready",
                        "state": "PASS",
                        "owner": "tanishq",
                        "required_result": "synthetic fixture exists",
                        "evidence": _evidence(),
                    }
                ],
                "acceptance_checks": [],
            },
        ],
    }


def test_sprint_ledger_accepts_evidenced_done_and_lists_ready():
    ledger = _ledger()
    assert validate_ledger(ledger) == []
    assert ready_sprints(ledger) == ["MI-01"]


def test_sprint_ledger_rejects_false_done_and_unmet_dependency():
    ledger = _ledger()
    ledger["sprints"][0]["acceptance_checks"][0]["state"] = "PENDING"
    ledger["sprints"][1]["status"] = "DONE"
    violations = validate_ledger(ledger)
    codes = {item.code for item in violations}
    assert codes >= {"DONE_WITHOUT_ACCEPTANCE", "DEPENDENCIES_NOT_DONE"}


def test_sprint_ledger_rejects_pass_without_negative_evidence():
    ledger = _ledger()
    del ledger["sprints"][0]["acceptance_checks"][0]["evidence"][
        "negative_control"
    ]
    assert "EVIDENCE_FIELD_MISSING" in {
        item.code for item in validate_ledger(ledger)
    }


def test_sprint_ledger_rejects_dependency_cycle():
    ledger = _ledger()
    ledger["sprints"][0]["status"] = "PENDING"
    ledger["sprints"][0]["depends_on"] = ["MI-01"]
    assert "DEPENDENCY_CYCLE" in {item.code for item in validate_ledger(ledger)}
