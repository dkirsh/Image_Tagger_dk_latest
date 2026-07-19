# SESSION RESUME — 2026-07-19 evening (Fable/Cowork restart point)

**Purpose**: paste-ready state transfer so a NEW session lands exactly where this one stopped.
**Repo**: `/Users/davidusa/REPOS/Image_Tagger_dk_latest` · branch `cnfa-algs-2026-07-14` · HEAD `d5fe276b` (VIEW-0/1/2 + CC-2 all committed).

## Absolute-path manifest (all verified on device this session)
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/TASKS.md` — THE sprint queue (COMP-CORRECT CC-1..10 + Sprint VIEW-0..5 + DEC + DK rows). Read FIRST.
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/CLAUDE.md` — repo rules incl. Cross-AI Artifact Contract and the NEW sandbox-commit lock-sweep protocol (sandbox commits WORK: mv stale `.git/*.lock` to `_to_delete/`, use `git --no-optional-locks`, sweep locks after).
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CODEX_ATTACK_TAX_PROMPT_2026-07-19.md` — CC-1 attack prompt (committed c391844c). David drops into Codex; verdict arrives at `/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CODEX_ATTACK_TAX_VERDICT_2026-07-19.md` — POLL for it, never ask for hand transfer.
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/viz/field_sidecars.py` — VIEW-0 COMPLETE (commit 7346ded7): fields_sink on annotate_image, same-pass deposit, npz+manifest+previews, 20 operator fields, determinism-tested, content-addressed.
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/viz/layered_viewer.py` — VIEW-1 BUILT + self-test PASSED, device-written; **git commit pending** (do first). Known issue: HTML is ~20 MB (21 base64 PNG overlays) — slim via paletted PNGs or downscaled overlay resolution before calling VIEW-1 done.
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/annotation_socket/annotator.py` — carries the fields_sink channel (committed 7346ded7).
- `/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/SESSION_TRANSFER_DOC_2026-07-19.md` — earlier full-day transfer doc (morning..afternoon threads).

## State (what is DONE today, evening segment)
1. TASKS.md sprint queue created + committed (fde0e2dc) — includes Sprint VIEW with the 8-layer-by-register design and the street-noise-on-foyer acceptance test for VIEW-3.
2. Complexity-partition 11-class taxonomy commit sealed (fde0e2dc).
3. CC-1 Codex attack prompt written + committed (c391844c) — WAITING on David to drop it (DK-2).
4. Sandbox-commit discovery: mount blocks unlink but allows rename → commits work with the lock-sweep protocol (documented in repo CLAUDE.md, 72cfbbdc).
5. VIEW-0 field sidecars: DONE, tested (20 fields, deterministic, round-trip digests), committed 7346ded7. Socket regression green (m1_prime, reliable_attrs, v9).
6. VIEW-1 layered viewer: built, self-test passed on unit 04d7e703eb98678e (sandbox demo image). NOT yet git-committed; size-slimming open.

## Immediate next actions (in order)
1. DONE this session: VIEW-1 slimmed (229640f0), VIEW-2 inspector (88e55989), CC-2 M1' classes (d5fe276b). Codex CC-1 attack DROPPED by David ~this hour — poll `/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CODEX_ATTACK_TAX_VERDICT_2026-07-19.md` and disposition FULLY when it lands (gates CC-4).
2. CC-3: C5–C23 declared-input VALUE bundles through input_values + full-socket fixtures (street_noise is the pattern: token+value+bundle binding in annotator).
3. Then CC-4 (post-attack), VIEW-3 question-driven composer (acceptance: street-noise-on-foyer), VIEW-4 A/B compare.
4. NOTE: Codex/ccode may be committing to the same repo — sweep ONLY zero-byte locks older than 120 s; defer commits when a live lock is present.

## Standing rules that bit us today (do not relearn)
- Sandbox mirror of the repo lives at `/home/claude/` (cnfa_algs/, annotation_socket/, viz/, committee/); Mac repo is the truth for git. Every ship = SendUserFile → device_commit_files → git commit via device_bash with lock-sweep.
- Never `git add -A`; add named files; `git add -f` for gitignored `*prompt*.md` docs.
- Tests run per-file with python3 (no pytest). Verification discipline: nothing ships untested; one example before scaling.
- Fields/viewer contract: viewer consumes ONLY records + sidecars, NEVER recomputes; LLM composer (VIEW-3) is advisory-only.
