from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TAXONOMY_PATH = ROOT / "datasets" / "signage_seed" / "signage_taxonomy_seed_2026-07-21.csv"
CONTRACT_PATH = ROOT / "docs" / "SIGNAGE_ANNOTATION_CONTRACT_2026-07-21.md"
SOCIAL_PATH = ROOT / "docs" / "SOCIAL_INTERACTION_ATTRIBUTE_TAXONOMY_2026-07-21.md"
SPRINT_PATH = ROOT / "docs" / "S2_SIGNAGE_AND_SOCIAL_SPRINT_CONTRACT_2026-07-21.md"

REQUIRED_COLUMNS = {
    "building_type",
    "sign_category",
    "sign_type",
    "examples",
    "typical_placement",
    "navigation_role",
    "interaction_role",
    "priority",
    "notes",
}

REQUIRED_BUILDINGS = {"hospital", "office"}
REQUIRED_SIGN_TYPES = {
    "exit_sign",
    "toilet_sign",
    "room_number",
    "meeting_room_display",
    "floor_directory",
    "department_direction",
}


def main() -> None:
    assert TAXONOMY_PATH.exists(), f"Missing {TAXONOMY_PATH}"
    assert CONTRACT_PATH.exists(), f"Missing {CONTRACT_PATH}"
    assert SOCIAL_PATH.exists(), f"Missing {SOCIAL_PATH}"
    assert SPRINT_PATH.exists(), f"Missing {SPRINT_PATH}"

    with TAXONOMY_PATH.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert rows, "Taxonomy CSV has no rows"
    assert REQUIRED_COLUMNS.issubset(rows[0].keys()), f"Missing columns: {REQUIRED_COLUMNS - set(rows[0].keys())}"
    assert len(rows) >= 25, f"Expected at least 25 signage taxonomy rows, got {len(rows)}"

    buildings = {r["building_type"] for r in rows}
    sign_types = {r["sign_type"] for r in rows}

    assert REQUIRED_BUILDINGS.issubset(buildings), f"Missing required buildings: {REQUIRED_BUILDINGS - buildings}"
    assert REQUIRED_SIGN_TYPES.intersection(sign_types), "Expected at least one required prototype sign type"

    priorities = {r["priority"] for r in rows}
    assert "critical" in priorities, "Expected at least one critical sign"
    assert "high" in priorities, "Expected at least one high priority sign"

    print("Signage taxonomy seed validation passed")
    print(f"Rows: {len(rows)}")
    print(f"Buildings: {sorted(buildings)}")
    print(f"Priorities: {sorted(priorities)}")


if __name__ == "__main__":
    main()
