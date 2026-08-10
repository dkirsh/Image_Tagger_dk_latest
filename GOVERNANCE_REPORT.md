# Governance Report — Image_Tagger_dk_latest
*tier: full · findings: 6*

| sev | check | path | detail |
|---|---|---|---|
| RED | G4 | /Users/davidusa/REPOS/Image_Tagger_dk_latest/Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/infra/cloud/full_stack_vm_setup.sh | destructive op in tracked script: `rm -rf` (RULE 0 — quarantine, don't delete; allowlist in governance.json g4_allow if legitimate) |
| RED | G4 | /Users/davidusa/REPOS/Image_Tagger_dk_latest/install_cognitive_code.sh | destructive op in tracked script: `rm -rf` (RULE 0 — quarantine, don't delete; allowlist in governance.json g4_allow if legitimate) |
| AMBER | G6 | /Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CODEX_PROMPT_gdrive_and_fixes_2026-07-14.md | 1 bare repo-relative path line(s) in a handoff/prompt doc (Complete Verified File Paths rule) |
| AMBER | G6 | /Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CODEX_S1_REFERENCE_ADJUDICATION_PROMPT_2026-07-19.md | 2 bare repo-relative path line(s) in a handoff/prompt doc (Complete Verified File Paths rule) |
| AMBER | G6 | /Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/CODEX_S1B_SUBBAND_DUMP_PROMPT_2026-07-19.md | 2 bare repo-relative path line(s) in a handoff/prompt doc (Complete Verified File Paths rule) |
| AMBER | G6 | /Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/validation/CODEX_TAGGER_SPECIES_HANDOFF_DECISION_2026-07-30.md | 1 bare repo-relative path line(s) in a handoff/prompt doc (Complete Verified File Paths rule) |

*govern v1.1 — no violations detected means NOT-DETECTED-BY-V1-CHECKS, never compliance. Reports are detectors, not attestations (design §9; llm_cheating_corpus drivers 1-6).*