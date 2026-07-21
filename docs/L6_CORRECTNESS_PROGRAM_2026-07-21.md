# L6 Computational-Correctness Program
### Checklist → Sprints → HITL/GUI → Crowdsourcing spec · 2026-07-21 (Cowork/Opus)

## 0. Framing
**Goal of record:** every registry attribute is a computational, effective procedure —
algorithmically faithful to its cited construct, stats-audited (M1′), honestly tiered — **AND
validated against what it claims to measure.** Current state (registry snapshot): **68 predicates,
19 GREEN (mechanically) / 49 AMBER, 15/68 emit M1′.** Mechanical correctness is essentially done
(the 07-20 reliable-A reconciliation closed the last honesty split). What remains splits into pure
engineering (faithful reimplementations, M1′ coverage, the Wave-3 detector, the scale anchor,
robustness) and the dominant lever: **construct validation + calibration on the L6 corpus, which is
human-in-the-loop.** GREEN today means *mechanically* green (deterministic + self-consistent), NOT
*construct-validated*; only the corpus campaign can promote an attribute to validated-green.

---

## PART A — The correctness checklist

| ID | Item | What "computationally correct" additionally requires | Queue / decision | Tier impact | HITL |
|----|------|------------------------------------------------------|------------------|-------------|------|
| **A1** | **Construct validation + calibration on the corpus** | Validate each attribute against human (and later biosignal) labels; fit gate thresholds and response constants to data; license the hedonic tags (currently UNLICENSED hypotheses). | DK-1 → L6 → CC-10 | Unblocks nearly all **49 AMBER** | **YES** — crowd ratings + expert panel |
| **A2** | **Faithful reimplementations** | V2 → the true 2-D Penacchio–Wilkins discomfort metric (today it's an honest radial-slope *proxy*); FC collapse ×4 upConv gain question; retire the uncorrelated V6/V7 proxies. | CC-6, CC-7, CC-8; DEC-2, DEC-3 | Fluency family AMBER→validated | Expert adjudication (small N) |
| **A3** | **Wave-3 detector-backed operators** | Pin one segmentation model → real vegetation / window-view / blue-space / material / sociopetal masks + art-content & text/signage VLM gates, replacing chromaticity heuristics. | CC-5; **DEC-1** (model choice) | De-AMBERs biophilia (V3/V12/V53) + partition gates | DEC-1 expert decision + negative-control review |
| **A4** | **Scale anchor + Wave-2 calibration** | W2.7 `room_scale_estimate` (door-leaf / seat-height anchors from the A3 detector) to un-cap the metric claims; calibrate W2.2 saturation + W2.3 double-height threshold on the POE atria pair. | CC-4 (done) → W2.7 | De-AMBERs geometry metrics | Threshold calibration uses A1 labels |
| **A5** | **M1′ coverage completion** | Sufficient-statistic bindings for the remaining **53** predicates (the geometry chain, the wave-2 ops, the layout criteria) so verify() can replay the *method*, not just the number, everywhere. | S0 extension | Audit completeness (not tier) | No |
| **A6** | **Robustness + cross-env replay** | Jittered-input stability test (the Tier-B chain amplifies pixel noise ~13% cell_m — the cap on everything riding the inferred plan); Mac↔sandbox exact-digest replay on the PNG corpus. | CC-9; L5 | Removes the Tier-B instability cap | No |

**Single biggest lever: A1.** A2/A3/A4/A5/A6 are finite engineering; A1 is what converts 49 "honest
procedures" into *validated measurements*, and it is the only item that needs people at scale.

---

## PART B — Sprint plan

Sequenced by dependency. Engineering sprints (S1, S2, S5-eng) run in parallel with the human track
(S0 corpus, S3 pilot, S4 campaign). Each sprint lists **exit criteria** — the gate to the next.

### S0 · Corpus assembly + integrity  *(IN FLIGHT)*
- **Goal:** ~200 licence-clean PNG interiors + ~80 A/B pairs + niche coverage, on Drive, with a
  trustworthy manifest.
- **Tasks:** finish MIT Indoor67 (`--min-px 512`) + SUN397 + Unsplash niche top-ups; **fix the two
  integrity issues found 07-20** — (a) manifest rows (401) ≫ provenance (232): purge the stale
  orphan rows left by the pre-fix collision run (audit via `verify_collector_fix.sh`); (b) only
  32/232 payloads on Drive: diagnose failed uploads (likely the retiring rclone shared client_id →
  create own client_id) and re-run idempotently to backfill `gdrive_path`.
- **Exit:** `--status` shows targets met; manifest rows ≈ provenance + pre-existing; 0 duplicate
  filenames; Drive PNG count ≈ provenance rows; all PNG (L5).
- **HITL:** none (curation of A/B "expected better" is light expert work, already tooled via `--make-pair`).

### S1 · Faithful code + M1′ coverage  *(engineering, parallel, no HITL)*
- **Goal:** close A2 and A5.
- **Tasks:** implement V2 2-D Penacchio–Wilkins (constants from the reference, [PORT] discipline);
  resolve FC ×4 gain (CC-7) + V6/V7 retirement (CC-6); add M1′ sufficient-statistic bindings for the
  53 uncovered predicates; adjudicate each new port vs a reference to ~1e-6 as with FC/SE.
- **Exit:** every scored predicate emits an M1′ block; V2 faithful passes reference adjudication;
  the proxy/faithful decision (DEC-3) is committed.

### S2 · Wave-3 detector + scale anchor  *(engineering + 1 expert decision)*
- **Goal:** close A3 and A4.
- **Tasks:** **DEC-1** — choose + pin the segmentation model (ADE20K-trained ONNX candidate),
  version-hashed, Codex-reviewed; build the vegetation/window-view/blue-space/material/sociopetal
  ops + art/text VLM gates with M1′ = `segmentation_mask` provenance; build W2.7 from detected door
  leaf (2.03 m) / seat height anchors; feed the scale into W2.2/W2.3.
- **Exit:** biophilia + partition gates ride real masks (negative controls pass: green paint ≠
  vegetation, indoor plant near window ≠ view greenery); W2.7 scores or abstains honestly.

### S3 · HITL labeling console + crowdsourcing pilot
- **Goal:** the rating GUI (Part C) + a **pilot** on ~20 images / ~10 A/B pairs to tune instructions,
  timing, gold items, and pay before spending at scale.
- **Tasks:** build the SPA; wire it to the manifest + Drive image URLs; run a 20-worker pilot on the
  primary venue; measure inter-rater reliability, completion time, gold accuracy.
- **Exit:** pilot inter-rater agreement acceptable (e.g., Krippendorff's α ≥ 0.6 on the anchored
  constructs); per-judgment time known; gold items discriminate; pay set to fair-hourly.

### S4 · Full validation campaign → calibration → tier promotions
- **Goal:** close A1. Collect the ratings at scale, aggregate to per-image/per-construct latent
  scores, and **fit the model to the humans**.
- **Tasks:** run the full campaign (Part D numbers); aggregate (Bradley–Terry for pairwise, mean+CI
  for Likert); build `corpus_L6/human_labels.csv`; for each attribute compute agreement with its
  construct (Spearman ρ; AUC for A/B direction); fit gate thresholds (ROC/Youden) and continuous
  response constants (isotonic/linear); license or reject each hedonic tag.
- **Exit:** every attribute carries a *measured* construct-validity number; promotion rule applied
  (e.g., ρ ≥ 0.5 AND A/B-AUC ≥ 0.70 → construct-validated GREEN; else AMBER **with the measured ρ
  recorded**, not a bare label). Panel signs the promotions.

### S5 · Robustness + cross-env + release
- **Goal:** close A6; final sign-off.
- **Tasks:** jittered-input stability (CC-9); Mac↔sandbox exact-digest replay on the PNG corpus;
  final GREEN promotions; MODEL_VERSION epoch bump; master-doc update.
- **Exit:** cross-env digests match within declared tolerance; robustness report committed; the
  registry's tier column reflects *validated* status with evidence.

**Critical path:** S0 → S3 → S4 (the human track) gates the tier promotions; S1/S2 run alongside and
feed S4 (more attributes to validate) and S5 (robustness needs the corpus). Rough calendar if the
corpus is done in ~1–2 weeks: S1/S2 engineering ≈ 2–4 weeks; S3 pilot ≈ 1 week; S4 campaign ≈ 1–2
weeks including turnaround; S5 ≈ 1 week. Human cost is small (Part D); engineering is the long pole.

---

## PART C — Human-in-the-loop tasks & GUI

### C0 · Two distinct HITL tracks
1. **Expert / panel (small N, high skill)** — DEC-1/2/3, tier-promotion review, faithful-port
   adjudication, hedonic-licensing sign-off. **Not** crowdsourced. Tooling: reuse the VIEW-2 function
   inspector + VIEW-3 composer + a committed decision log; no new GUI needed.
2. **Crowd raters (large N, perceptual judgments)** — the construct-validation labels. **This is the
   GUI build.** Everything below is this track.

### C1 · Task design — what the crowd does
Use **2-alternative forced choice (2AFC) pairwise** as the workhorse (more reliable and scale-free
than Likert for perceptual constructs, and it directly validates the A/B corpus), **anchored** by a
subset of absolute Likert ratings so the latent scale has an origin.

Constructs to rate (each maps to the attributes needing validation):

| Construct (question to the human) | Validates |
|---|---|
| "Which space looks **more restorative / calming**?" | biophilia (V19/V3/V12/V53), partition biophilic gate, spectral/fractal |
| "Which looks **more visually busy / cluttered**?" | FC, SE, complexity_partition, clutter stack |
| "Which would be **easier to find your way through**?" | C1–C4 integration/intelligibility/wayfinding, W2.4 blind-corner |
| "Which feels **more open vs enclosed**?" | prospect/refuge, enclosure, W2.2 ceiling openness |
| "Which feels **calmer vs more stressful**?" | glare, street-noise, thermal/affect |
| "Which do you **prefer overall**?" | global hedonic fluency→affect |

Each of the ~80 designed A/B pairs targets ONE construct (that's the manipulation), so those give
direct, clean validation. Global scaling across the 200 singletons uses a **balanced sparse pairwise
design** (~8–12 comparisons/image/construct) plus absolute Likert on all 200 for anchoring.

### C2 · The labeling console (SPA) — screen by screen
A single self-contained web app (recommended over survey builders, which are clumsy for image 2AFC).
It reads `manifest.csv` + a `design.json` (which items/pairs/constructs), serves items, records
responses. Screens:

1. **Consent + screening** — informed consent; confirm normal/corrected vision, fluent English,
   desktop/large screen. (Screening also enforced at the venue.)
2. **Instructions + worked examples** — one clear paragraph per construct + 2 examples showing the
   intended reading ("busy" = amount of stuff/detail, not "ugly").
3. **Qualification (3–5 gold trials)** — must pass to continue; filters bots/inattentives up front.
4. **Rating loop** — the core screen:
   - Pairwise: two images side-by-side, edge-to-edge, no scroll; the construct question as a fixed
     header; two big buttons (**Left / Right**) + optional "can't tell"; keyboard `←/→`; a confidence
     toggle (sure / unsure). Response time captured.
   - Absolute: one image + a 1–7 slider/labelled buttons for the construct.
   - Progress bar; ~40–80 items per session (~8–15 min); images preloaded to avoid latency bias.
   - **Attention/gold items** interspersed (~1 in 10): pairs with a consensus-obvious answer (bright
     daylit atrium vs dim cluttered basement → "more restorative").
5. **Submit + completion code** — returns the venue completion code; posts the session.

**Data schema** (one row per judgment, streamed to the backend / CSV):
`worker_id, session_id, item_id (or pair_id), construct, response (L/R/rating), confidence,
rt_ms, is_gold, gold_pass, ua_desktop, ts_utc`. Images referenced by the corpus filename → the app
resolves to a Drive public-read URL (or a CDN mirror).

**Hosting:** minimal static SPA + a thin backend (Flask/Cloud Run or even a Google Sheet/Apps Script
for the pilot); images from Drive public links or a cheap CDN. No PII stored; worker_id is the
venue's anonymised id.

### C3 · Aggregation → labels
Pairwise → **Bradley–Terry / TrueSkill** latent score per image per construct (with CIs); Likert →
mean + CI, used to anchor the BT scale. Output `corpus_L6/human_labels.csv`
(`filename, construct, human_score, ci_low, ci_high, n_judgments, agreement`). This file is the
validation target the calibration step (S4) fits every computed attribute against.

---

## PART D — Crowdsourcing spec (buying the raters online)

### D1 · Venue
- **Primary: [Prolific](https://www.prolific.com/).** The research-grade "post-MTurk" platform —
  multiple independent studies find it delivers materially better data quality than MTurk for
  online behavioural/perceptual work, with built-in screening, fair-pay enforcement, and clean
  consent/ethics handling. Best fit for a construct-validity study you may publish.
- **Alternative: [CloudResearch Connect](https://www.cloudresearch.com/).** A vetted MTurk-adjacent
  panel; comparable quality, sometimes cheaper/faster. Good A/B against Prolific in the pilot.
- **Scale-only fallback:** [Toloka](https://toloka.ai/) or [Appen](https://appen.com/) if you later
  want *hundreds of thousands* of pure labels (AI-data volume) rather than research-grade ratings.
  Plain **MTurk** only *through* CloudResearch filters — raw MTurk quality is the reason these
  platforms exist.

### D2 · Study design (illustrative numbers — tune in the pilot)
- Corpus: ~200 images, ~80 A/B pairs, 6 constructs.
- Redundancy: **K = 15 raters** per item (perceptual studies stabilise at ~10–20).
- **A/B validation:** 80 pairs × 1 target construct × 15 = **1,200 judgments.**
- **Absolute anchoring:** 200 images × 6 constructs × 15 = **18,000 judgments.**
- **Sparse global pairwise** (optional, for full scaling): ~1,500 comparisons × 15 ≈ 22,500 — do
  only the constructs that need a continuous scale; skip where the A/B + Likert suffice.
- Core campaign ≈ **~20,000 judgments** (A/B + anchoring). At ~10 s/judgment ≈ **~55 person-hours.**
- Sessioning: ~50–80 judgments/session (~10–15 min) → **~300–400 worker-sessions.**

### D3 · Quality control (non-negotiable)
- **Screening:** approval ≥ 95%, fluent English, normal/corrected vision, **desktop only** (image
  detail), and a **demographically balanced** sample — perceptual preference varies by culture, so a
  skewed panel bakes bias into the calibration; record demographics as covariates.
- **Gold standard:** ~10% consensus-obvious items with known answers; exclude workers below a gold
  accuracy floor (e.g., < 80%).
- **Attention/catch trials**, **minimum completion time**, and **inter-rater agreement filtering**
  (drop workers whose judgments correlate poorly with the consensus).
- **Consent + ethics:** informed consent screen; no PII; benign image content (interiors); if this
  feeds a publication, obtain IRB/ethics approval — Prolific's flow supports it.

### D4 · Pay + cost estimate
- Fair pay ≈ **$12/hr** (Prolific's enforced floor region; set to the task's measured time).
- Worker pay: ~55 hr × $12 ≈ **$660**; platform fee (~30–40%) → **~$850–950 total** for the core
  campaign; add a ~$100–150 pilot. **Budget ~$1,000–1,500** end-to-end — small relative to the
  engineering. Doubling K or adding the sparse global pairwise roughly doubles it.

### D5 · Data flow back into the corpus
`venue export (CSV)` → QC filter → **BT/mean aggregation** → `corpus_L6/human_labels.csv` (keyed by
corpus filename) → **S4 calibration**: per attribute compute ρ / AUC vs its construct, fit
thresholds/constants, apply the promotion rule, and record the *measured* validity number in the
registry note (never a bare tier). The manifest already carries `pair_id` + `pair_expected_better`,
so the A/B judgments slot straight in as the ground-truth check on those pairs.

---

## Appendix — what needs a human vs what doesn't
- **No human:** A2 (faithful ports — reference adjudication is deterministic), A5 (M1′), A6
  (robustness/replay), the entire collection pipeline (built), aggregation/calibration code.
- **Small expert panel:** DEC-1 (model), DEC-2 (FOV policy), DEC-3 (proxy retirement), tier-promotion
  sign-off, hedonic licensing, A/B "expected better" curation for the hand-made pairs.
- **Crowd (buy online):** the ~20,000 perceptual judgments in A1/S4 — the one place scale-of-humans
  is required, and the one place a purpose-built GUI (Part C) pays for itself in data quality.

*Sources for the venue recommendation:* Prolific vs MTurk/CloudResearch data-quality comparisons
(PLOS One 2023; Behavior Research Methods 2021); platform pages linked inline.
