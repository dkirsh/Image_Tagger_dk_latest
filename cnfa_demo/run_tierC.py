#!/usr/bin/env python3
"""Tier C demo: the SAME isovist/prospect/refuge field code running on a
supplied floor plan (precise), proving the one-code-path / three-tiers strategy.
Plan: two offices + corridor + open studio with a nook, doorways connecting.
"""
import sys
sys.path.insert(0, "/home/claude")
import numpy as np, cv2
import cnfa_algs as ca

# ---- draw a floor plan: walls black on white, 600x600 px = 12x12 m
S = 600
plan = np.full((S, S, 3), 255, np.uint8)
def wall(x1, y1, x2, y2, t=6):
    cv2.rectangle(plan, (x1, y1), (x2, y2), (0, 0, 0), -1) if abs(x2-x1) < 20 or abs(y2-y1) < 20 \
        else cv2.rectangle(plan, (x1, y1), (x2, y2), (0, 0, 0), t)

# outer shell
cv2.rectangle(plan, (20, 20), (S-20, S-20), (0, 0, 0), 8)
# corridor walls (horizontal corridor y 260..340)
cv2.rectangle(plan, (20, 256), (S-20, 264), (0, 0, 0), -1)   # top corridor wall
cv2.rectangle(plan, (20, 336), (S-20, 344), (0, 0, 0), -1)   # bottom corridor wall
# doorway gaps in corridor walls
cv2.rectangle(plan, (120, 250), (170, 350), (255, 255, 255), -1)   # door to office A
cv2.rectangle(plan, (430, 250), (480, 350), (255, 255, 255), -1)   # door to studio
# upper zone: two offices split by a wall
cv2.rectangle(plan, (296, 20), (304, 260), (0, 0, 0), -1)
cv2.rectangle(plan, (296, 100), (304, 160), (255, 255, 255), -1)   # interior door between offices
# lower zone: open studio with a refuge nook (alcove) bottom-left
cv2.rectangle(plan, (20, 460), (160, 468), (0, 0, 0), -1)
cv2.rectangle(plan, (152, 460), (160, S-20), (0, 0, 0), -1)
cv2.rectangle(plan, (152, 500), (160, 540), (255, 255, 255), -1)   # nook entrance
# a freestanding column in the studio
cv2.rectangle(plan, (380, 430), (410, 460), (0, 0, 0), -1)

cv2.imwrite("/home/claude/cnfa_demo/outputs/tierC_plan_input.png", plan)

pg = ca.plan_from_floorplan_image(plan, cell_m=12.0 / 220)
fields = ca.isovist_fields(pg, n_rays=72, stride=2)
tiles = [
    ca.render_plan_topo(pg, fields["openness"], "Tier C precise: isovist openness (supplied plan)"),
    ca.render_plan_topo(pg, fields["prospect"], "prospect field"),
    ca.render_plan_topo(pg, fields["refuge"], "refuge (enclosure) field"),
    ca.render_plan_topo(pg, fields["prospect_refuge"], "prospect-refuge seat-choice map"),
    ca.render_plan_topo(pg, fields["compactness"], "isovist compactness (roomness vs corridorness)"),
]
cv2.imwrite("/home/claude/cnfa_demo/outputs/tierC_plan_fields.png", ca.gallery(tiles, cols=3))
print("Tier C done: outputs/tierC_plan_fields.png")
print(f"grid cells free={int((pg.grid==1).sum())} wall={int((pg.grid==2).sum())} conf={pg.confidence}")
