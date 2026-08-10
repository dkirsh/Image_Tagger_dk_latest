# SPRINT — FOYER-HITL-1

*2026-08-01, cowork. The lead sprint from the direction doc (§5.2 Sprint A), made runnable. ~2–3 weeks.
Lives at `docs/validation/SPRINT_FOYER_HITL_1_2026-08-01.md`. Builds on: the review-pack viewer, the
phase-scramble/Mooney generators, `HITL_STUDY_DESIGN_NOTE`, `CHALLENGE_LEDGER_SPEC`, the CNFA acoustics
operator, and the materials encyclopedia (absorption coefficients).*

## Goal
A **runnable foyer HITL instrument** that tests the engine's predictions against human judgment two ways:
- **Stage 1 (silent-visual):** validate per-construct predictions on a foyer corpus (agree/disagree/VAS).
- **Multimodal MVP (audio-visual-social):** one foyer, a small factorial of position × noise × occupancy,
  `pyroomacoustics`-auralized over headphones, 2AFC — the first test of the acoustic/proxemic constructs.
Every disagreement/reversal writes a record to the **challenge ledger**.

## Exit criteria (definition of done)
1. Foyer corpus (~30–60 images) + manifest exist.
2. CNFA engine predictions emitted for the corpus **and** for the one MVP 3D foyer (incl. position-dependent
   acoustics).
3. Stage-1 viewer runs and collects human agree/disagree/VAS on foyer predictions (≥2 reviewers on a pilot set).
4. Multimodal MVP: ≥1 foyer, ≥12 audio-visual-social cells, auralized, a 2AFC/position-choice harness that
   runs on headphones, dry-run on a handful of people.
5. `challenge_ledger.jsonl` populated with the first prediction-vs-judgment records.

## Tracks & tasks (owner · depends-on · deliverable)
### T1 — Foyer corpus (data)
1. **Assemble the corpus** — pull `lobby / entrance_hall / reception / foyer` from SUN397 + Places365 (subset of
   the acquisition list) + any ZHA renders; ~30–60 PNGs; manifest. **Tanishq/Stephan · needs the priority
   datasets (Sprint B/#7) or a quick web-sourced starter set · `Image_Collections/foyer_corpus/`.**
2. **Pick one 3D foyer** for the MVP — a Structured3D interior with a lobby-like space (we hold the
   annotations), or a ZHA model if one is in hand. **cowork/Tanishq · Structured3D on Drive · one model + its
   material list.**

### T2 — Engine predictions (the thing being tested)
3. **Run the tagger on the corpus** → per-construct predictions (arrival-orientation support, wayfinding-to-
   reception, visual openness, glare, clutter), emitted as Phase-1-style hypothesis rows. **Codex/Fable · T1.1
   · `foyer_hypotheses.jsonl`.**
4. **Run the acoustics operator on the MVP foyer** (ISO 3382-3) for each MVP station → STI / RT60 / direct-
   reverberant + a speech-privacy read. **Codex/Fable · T1.2 · position-indexed acoustic predictions.**

### T3 — Stage-1 instrument (silent-visual; reuse what's built)
5. **Point the review-pack viewer at the foyer predictions** (agree/disagree/can't-tell + VAS per construct).
   **cowork · T2.3 · a foyer build of `viewer.html`.**
6. **Foyer review protocol** — adapt `REVIEW_PROTOCOL.md` to the foyer constructs. **cowork · — · md.**

### T4 — Multimodal MVP (the new build)
7. **Auralizer** — a `pyroomacoustics` script: 3D foyer geometry + **material absorption from the materials
   encyclopedia (§1)** + source positions → per-station **binaural IRs**; convolve dry sources → per-cell WAVs.
   **cowork (I can prototype now) · T1.2 · `foyer_auralize.py` + rendered audio cells.**
8. **Dry audio assets** — street noise, reception babble, a scripted **target-talker** (for "overheard?").
   **Tanishq · — · WAVs, level-calibrated.**
9. **Visual station renders** — first-person views from each standing position, with occupant/group configs
   (empty / queue / cluster) composited. **cowork/Tanishq · T1.2 · PNGs per cell.**
10. **Cell factorial** — e.g. 3 positions × 2 noise levels × 2 occupancy configs = 12 cells, each audio+visual
    matched; each carries the engine's prediction. **cowork · T7,T8,T9 · a cell manifest.**
11. **2AFC / position-choice harness** — a single-file HTML (like the viewer) that plays a cell (image +
    headphone audio) and logs the response; exports JSON. **cowork · T10 · `foyer_hitl.html`.**

### T5 — Challenge ledger
12. **Stand up `challenge_ledger.jsonl`** per the spec; wire Stage-1 disagreements and 2AFC reversals to emit
    challenge records against the engine predictions. **cowork/Codex · T2,T3,T4 · populated ledger.**

### T6 — Pilot run
13. **Dry-run** the Stage-1 viewer + the multimodal MVP on ~5 people (lab); check the audio convinces and the
    responses discriminate; log first challenges. **David + participants · T3,T4,T5 · a short findings note.**

## Critical path
T1.2 (pick 3D foyer) → T2.4 (acoustics) + T7 (auralizer) → T10 (cells) → T11 (harness) → T13 (run). The
Stage-1 track (T1.1→T2.3→T3) runs in parallel and can finish first — it needs no audio, so **it's the fastest
first result** and de-risks the whole sprint.

## Decisions reserved for David (gate a few tasks)
- **3D foyer for the MVP:** use a Structured3D lobby now, or wait for a ZHA model? (Recommend: start on
  Structured3D so we don't block; swap in ZHA when it lands.)
- **Which constructs first:** speech-privacy + where-to-stand (multimodal) vs glare/clutter/openness
  (silent-visual)? (Recommend: run both tracks in parallel — silent for the visual constructs, MVP for the
  acoustic ones.)
- **Participants for the dry-run:** how many, and lab logistics/headphones.

## What cowork starts on immediately (no input needed)
- Prototype **`foyer_auralize.py`** (pyroomacoustics per-position BRIR from geometry + encyclopedia absorption)
  on a synthetic shoebox foyer, to prove the audio pipeline end-to-end.
- Prototype **`foyer_hitl.html`** (the 2AFC/position-choice harness) against fixture cells.
- Stand up the **`challenge_ledger.jsonl`** writer + a tiny validator.
These three unblock T7/T11/T12 and need nothing from anyone.
