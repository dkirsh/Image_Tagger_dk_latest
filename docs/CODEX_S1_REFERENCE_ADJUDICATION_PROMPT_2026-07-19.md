# CODEX TASK — S1 faithful-clutter adjudication: real pyrtools vs the sandbox shim
### 2026-07-19 · Repo /Users/davidusa/REPOS/Image_Tagger_dk_latest (branch cnfa-algs-2026-07-14) · PYTHONPATH=.
### OUTPUT ARTIFACT (commit exactly these): `docs/CLUTTER_REFERENCE_MAC_2026-07-19.json` + `docs/CODEX_S1_ADJUDICATION_2026-07-19.md`

Context: the faithful V6/V7 port (Sprint COMP-CORRECT S1) runs the VENDORED Rosenholtz reference
(`cnfa_algs/_vendor/visual_clutter/`, unmodified, MIT) on a pyrtools shim
(`cnfa_algs/_pyrtools_min.py`) because the sandbox cannot install pyrtools. Your job: run the SAME
vendored reference on REAL pyrtools and adjudicate the shim numerically. Divergences localize to the
shim's PORT-CHECK items P1–P4 (documented in its header).

1. `pip3 install pyrtools --break-system-packages` (or a venv). Report the installed version.
2. `PYTHONPATH=. python3 scripts/reference_clutter_compare.py --backend real --env mac --out docs/CLUTTER_REFERENCE_MAC_2026-07-19.json`
3. `python3 scripts/reference_clutter_compare.py --compare docs/CLUTTER_REFERENCE_MAC_2026-07-19.json docs/CLUTTER_REFERENCE_SANDBOX_2026-07-19.json`
   (the sandbox JSON is committed). Report the ADJUDICATION line verbatim and every MISMATCH row.
4. If mismatches: identify which pyramid component is responsible by comparing the LAYER means
   (color/contrast/orientation split localizes FC errors; se_raw isolates the steerable pyramid).
   Inspect real pyrtools' GaussianPyramid filter + edge handling and upConv gain against the shim's
   P1–P3 notes, and SteerablePyramidFreq's rcosFn/pointOp against P4. Recommend the exact shim fix.
5. Also verify DT-1 (recorded in `cnfa_algs/faithful_clutter.py` self-test): on real pyrtools, does
   FC/SE still rank Farnsworth (foliage) above the cluttered industrial office? Report the numbers.
6. Write `docs/CODEX_S1_ADJUDICATION_2026-07-19.md` with executed evidence, verdict
   (SHIM CONFIRMED / SHIM DIVERGES + where), and the DT-1 confirmation. Commit ONLY the two output
   artifacts. Do not modify batch files. No push.
