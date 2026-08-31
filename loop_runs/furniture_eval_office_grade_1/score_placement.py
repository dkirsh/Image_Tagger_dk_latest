#!/usr/bin/env python3
"""score_placement.py — placement error of the pipeline room against the hand-placed room.

Evaluation-side scorer, deliberately NOT platform code: it lives with the eval it serves and
imports nothing but the standard library, so it can be read end to end in one sitting.

METHOD BLOCK (claim written first: PLACEMENT_ERROR_CLAIM_2026-08-31.md)
- FREEZE: reads room.json (pipeline, @6cd13533) and room.hand_edited.json (hand, @c61dc862).
  Neither is written to. Their geometry and apertures are byte-equal, so every difference
  between them is a furniture difference.
- CLAIM: matches furniture by `id` and reports, per object, the pipeline position, the hand
  position and the planar placement error, plus a mean over the objects the pipeline placed.
- REFUTATION: on the committed pair it must give reception_desk 0.99, built_in_shelving 1.64,
  sofa 2.94 metres, and report round_table and slat_divider as unplaced. Any other answer
  means this script is wrong, not the hand numbers. Also refuted if it invents an error for
  an unplaced object, drops an object present in either file, or is not reproducible.
- Determinism: no clock, no randomness, sorted keys. Two runs on one input pair are
  byte-identical, which is why nothing here stamps a time.

Planar distance only. Every object in both files sits at z_m 0.0, so a third term would add
nothing except a false suggestion that height is being scored.

The mean covers PLACED objects only. There is no honest error for an object the pipeline
never placed: zero would read as perfect and anything imputed would be invented. The count
of unplaced objects travels beside the mean so the mean cannot be read as covering them.

Usage: score_placement.py [pipeline_room.json hand_room.json [out.json]]
Exit 0 on success, 2 on a refusal (missing file, malformed room, absent furniture list).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CALIBRATION = "exploratory_uncalibrated"


def refuse(msg: str) -> None:
    print(f"REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(2)


def load_room(path: Path, label: str) -> dict:
    try:
        room = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        refuse(f"no {label} at {path}")
    except json.JSONDecodeError as exc:
        refuse(f"{label} at {path} is not valid JSON: {exc}")
    if not isinstance(room, dict):
        refuse(f"{label} at {path} is not a JSON object")
    if not isinstance(room.get("furniture"), list):
        refuse(f"{label} at {path} has no furniture list")
    return room


def by_id(room: dict, label: str) -> dict:
    out: dict[str, dict] = {}
    for item in room["furniture"]:
        if not isinstance(item, dict):
            refuse(f"{label} has a furniture entry that is not an object")
        oid = item.get("id")
        if not isinstance(oid, str) or not oid:
            refuse(f"{label} has a furniture entry without a usable id")
        if oid in out:
            refuse(f"{label} has duplicate furniture id {oid!r}; matching by id would be ambiguous")
        out[oid] = item
    return out


def coord(item: dict, oid: str, label: str) -> tuple[float, float]:
    xy = []
    for key in ("x_m", "y_m"):
        v = item.get(key)
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v or v in (
                float("inf"), float("-inf")):
            refuse(f"{label} object {oid!r} has no finite {key}")
        xy.append(float(v))
    return xy[0], xy[1]


def score(pipeline_path: Path, hand_path: Path) -> dict:
    pipe_room = load_room(pipeline_path, "pipeline room")
    hand_room = load_room(hand_path, "hand-edited room")
    pipe, hand = by_id(pipe_room, "pipeline room"), by_id(hand_room, "hand-edited room")

    objects, errors = [], []
    for oid in sorted(set(pipe) | set(hand)):
        p, h = pipe.get(oid), hand.get(oid)
        # Matching is by id; category is descriptive. The two files can name the same object
        # differently — o4 is "shelving" by hand and "built_in_shelving" in the pipeline,
        # which resolved it through an inventory alias. Report the reference name, and say so
        # explicitly when the pipeline disagrees rather than quietly choosing one.
        category = (h or p).get("category")
        row: dict = {"id": oid, "category": category}
        if p is not None and h is not None and p.get("category") != h.get("category"):
            row["pipeline_category"] = p.get("category")
            row["category_source"] = "hand reference; pipeline name differs and is given beside it"
        if p is not None and h is not None:
            px, py = coord(p, oid, "pipeline room")
            hx, hy = coord(h, oid, "hand-edited room")
            err = math.hypot(px - hx, py - hy)
            row.update({
                "status": "placed",
                "pipeline_x_m": px, "pipeline_y_m": py,
                "hand_x_m": hx, "hand_y_m": hy,
                "dx_m": round(px - hx, 6), "dy_m": round(py - hy, 6),
                "placement_error_m": round(err, 6),
            })
            errors.append(err)
        elif h is not None:
            hx, hy = coord(h, oid, "hand-edited room")
            row.update({
                "status": "unplaced_by_pipeline",
                "hand_x_m": hx, "hand_y_m": hy,
                "placement_error_m": None,
                "why": "the pipeline never placed this object, so no error is defined for it",
            })
        else:
            px, py = coord(p, oid, "pipeline room")
            row.update({
                "status": "absent_from_hand_reference",
                "pipeline_x_m": px, "pipeline_y_m": py,
                "placement_error_m": None,
                "why": "present in the pipeline room but not in the hand reference",
            })
        objects.append(row)

    placed = [o for o in objects if o["status"] == "placed"]
    unplaced = [o for o in objects if o["status"] == "unplaced_by_pipeline"]
    return {
        "calibration": CALIBRATION,
        "note": ("placement error of the pipeline room against a hand-placed reference; "
                 "planar distance in metres, matched by object id. Scores are "
                 "exploratory_uncalibrated — a difference between two files, not an error rate."),
        "inputs": {
            "pipeline_room": pipeline_path.name,
            "hand_room": hand_path.name,
            "shell_identical": (pipe_room.get("geometry") == hand_room.get("geometry")
                                and pipe_room.get("apertures") == hand_room.get("apertures")),
        },
        "objects": objects,
        "summary": {
            "objects_total": len(objects),
            "objects_placed": len(placed),
            "objects_unplaced_by_pipeline": len(unplaced),
            "unplaced_ids": [o["id"] for o in unplaced],
            "mean_placement_error_m": (round(sum(errors) / len(errors), 6) if errors else None),
            "mean_covers": ("placed objects only; the unplaced are counted here, never "
                            "averaged in as zero"),
            "max_placement_error_m": (round(max(errors), 6) if errors else None),
        },
    }


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    pipeline = Path(args[0]) if len(args) > 0 else HERE / "room.json"
    hand = Path(args[1]) if len(args) > 1 else HERE / "room.hand_edited.json"
    out = Path(args[2]) if len(args) > 2 else HERE / "placement_error.json"
    result = score(pipeline, hand)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    out.write_text(text, encoding="utf-8")
    s = result["summary"]
    for o in result["objects"]:
        if o["status"] == "placed":
            print(f'  {o["category"]:<20} {o["placement_error_m"]:.2f} m')
        else:
            print(f'  {o["category"]:<20} {o["status"]}')
    print(f'  mean over {s["objects_placed"]} placed: '
          f'{s["mean_placement_error_m"]:.2f} m ({s["objects_unplaced_by_pipeline"]} unplaced, '
          f'not averaged in)')
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
