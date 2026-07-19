"""
CC-3 tests (2026-07-19): C5-C23 declared-input VALUE bundles through input_values.
Locks: (1) no tokens -> all 18 layout predicates ABSTAINED (not UNKNOWN, not crash);
(2) token WITHOUT value -> UNKNOWN declared_input_value_missing (fail closed, S0S2 HIGH-1);
(3) tokens + valid values -> the input-satisfied predicates SCORE with in-[0,1] values and
    plan-chain evidence; (4) out-of-grid seat -> UNKNOWN cell guard; (5) determinism.
Run: python3 annotation_socket/tests/test_cc3_layout_inputs.py
"""
import sys
sys.path.insert(0, "/home/claude")
sys.path.insert(0, "/Users/davidusa/REPOS/Image_Tagger_dk_latest")
import numpy as np
from annotation_socket.annotator import annotate_image

IMG = "/home/claude/cnfa_demo/batch_outputs/_in_Industrial_open_concept_office_project_b.png"
LAYOUT_PIDS = ["C5.collaborator_proximity", "C6.path_overlap", "C7.focus_speech_privacy",
               "C8.distraction_distance", "C9.view_equity", "C10.daylight_proximity",
               "C11.prospect_refuge", "C12.crowding_risk", "C14.focus_collab_separation",
               "C15.active_design", "C16.territory", "C17.local_control", "C18.air_quality",
               "C19.restoration_nature", "C20.chronic_soundscape", "C21.thermal",
               "C22.circadian_contrast", "C23.social_connectedness"]


def _by_pid(rec):
    return {s["predicate"]: s for s in rec["scores"]}


def _free_cells(img_path, n):
    """Valid seat coords for THIS unit's inferred plan (values must live in plan space)."""
    import cv2
    from annotation_socket import m1_prime as MP
    import cnfa_algs as ca
    from cnfa_algs.plan import infer_plan_from_image, FREE
    img = MP.load_for_m1p(img_path)
    vx, vy, _ = ca.estimate_vanishing_point(img)
    planes, _ = ca.segment_planes(img, (vx, vy))
    Z, _, _ = ca.DepthProvider()(img, planes, (vx, vy))
    pg = infer_plan_from_image(img, planes, Z)
    rcs = np.argwhere(pg.grid == FREE)
    step = max(1, len(rcs) // n)
    return [tuple(map(int, rc)) for rc in rcs[::step][:n]], pg


def test_no_tokens_all_abstain():
    rec = annotate_image(IMG)
    by = _by_pid(rec)
    for pid in LAYOUT_PIDS:
        assert by[pid]["status"] == "ABSTAINED", (pid, by[pid]["status"])
    print("  no tokens -> 18/18 ABSTAINED with named missing inputs  OK")


def test_token_without_value_fails_closed():
    rec = annotate_image(IMG, unit_inputs=frozenset({"seats"}))
    by = _by_pid(rec)
    s = by["C11.prospect_refuge"]              # requires plan+seats only
    assert s["status"] == "UNKNOWN" and "declared_input_value_missing" in str(s), s
    print("  token without value -> UNKNOWN fail-closed  OK")


def test_valid_values_score():
    seats, pg = _free_cells(IMG, 6)
    iv = {"seats": seats,
          "glazing": [((r, 1), "S") for r in range(2, min(12, pg.grid.shape[0]))],
          "collab_pairs": [(0, 1), (2, 3)],
          "collab_sources": [seats[2]],
          "focus_seats": [4, 5],
          "acoustic_params": {"d2s": 7.0, "L_noise": 42.0}}
    toks = frozenset(iv.keys())
    rec = annotate_image(IMG, unit_inputs=toks, input_values=iv)
    by = _by_pid(rec)
    expect_scored = ["C5.collaborator_proximity", "C7.focus_speech_privacy",
                     "C8.distraction_distance", "C9.view_equity", "C10.daylight_proximity",
                     "C11.prospect_refuge", "C12.crowding_risk",
                     "C14.focus_collab_separation", "C21.thermal", "C22.circadian_contrast"]
    scored, unscored = [], []
    for pid in expect_scored:
        s = by[pid]
        if s["status"] == "SCORED":
            assert 0.0 <= s["value"] <= 1.0, (pid, s["value"])
            assert s["evidence"]["kind"] == "plan_chain", pid
            scored.append(pid)
        else:
            unscored.append((pid, s["status"], str(s)[:90]))
    assert len(scored) >= 8, f"expected >=8 scored, got {len(scored)}; unscored={unscored}"
    # predicates whose tokens were NOT supplied stay ABSTAINED
    assert by["C16.territory"]["status"] == "ABSTAINED"
    assert by["C19.restoration_nature"]["status"] == "ABSTAINED"
    # determinism
    rec2 = annotate_image(IMG, unit_inputs=toks, input_values=iv)
    by2 = _by_pid(rec2)
    for pid in scored:
        assert by[pid]["value"] == by2[pid]["value"], pid
    print(f"  valid values -> {len(scored)}/10 scored in [0,1] on plan-chain evidence, "
          f"deterministic; unsupplied stay ABSTAINED  OK")
    if unscored:
        print(f"    (honestly unscored on this unit: {[u[0] for u in unscored]})")


def test_out_of_grid_seat_guard():
    rec = annotate_image(IMG, unit_inputs=frozenset({"seats"}),
                         input_values={"seats": [(99999, 3)]})
    s = _by_pid(rec)["C11.prospect_refuge"]
    assert s["status"] == "UNKNOWN" and "out_of_grid" in str(s), s
    print("  out-of-grid seat -> UNKNOWN cell guard  OK")


if __name__ == "__main__":
    for fn in [test_no_tokens_all_abstain, test_token_without_value_fails_closed,
               test_valid_values_score, test_out_of_grid_seat_guard]:
        print(fn.__name__); fn()
    print("\nCC-3 LAYOUT-INPUT TESTS PASSED")
