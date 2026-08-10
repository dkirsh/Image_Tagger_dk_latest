# HITL Validation Harness + Adaptive-Preference Loop — design & first slice

## 2026-07-30 · a working design for the highest-value next target

*This proposes the human-in-the-loop (HITL) credibility harness for the image tagger, the first
predicate slice to run through it, and — per David's prompt — how to tie the judgment collection to the
existing adaptive-preference engine so that eliciting the judgments and validating the predicates become
one loop rather than two projects. It is a design to critique, not a finished contract. State claims are
grounded in the tagger current-state docs, the `Experiment_Maker/adaptive_preference/` system
(v3.5.11 + the 11 July attribute layer), and the 29 July QA/panel material. Nothing here changes another
lane's code; the platform pieces are consumed as contracts, not edited.*

---

## 0. The one-paragraph idea

Every predicate the tagger computes is currently a **candidate measure** — the 29 July panel said so
explicitly, and until each one is checked against something outside the tagger it cannot be spoken of as
a real claim. The harness is the machinery that does that checking and records the verdict. It splits the
work honestly: predicates with **objective ground truth** (geometry, reference implementations) are
validated now, with no human in the loop; predicates that are **perceptual or evaluative** (perceived
clutter, "welcoming", "good for meeting") need human judgment, and the most efficient, least-biased way
to get that judgment is the adaptive 2AFC preference engine we already have. The number the harness
emits per attribute — a measured tagger↔human correlation `r` — is exactly the number the
adaptive-preference attribute layer needs to warm-start future studies. So the harness feeds the
preference engine, and the preference engine feeds the harness. We build the loop once.

---

## 1. Why this is worth building even before we can make the judgments ourselves

Three returns, in order of certainty:

1. **The infrastructure is required no matter who judges.** Label ingestion, pairing an engine output to
   a human response, computing agreement, and writing an auditable verdict are needed for any validation,
   by anyone, ever. None of it is wasted.
2. **Designing the judgment task is itself the scientific act.** To validate "shared-focal-surface
   access" you must write down what a competent rater is shown and asked, and what counts as ground
   truth. Doing that *operationalizes the construct*. If we cannot write a clean question for a
   predicate, that is a first-class finding: the construct is under-specified, and now we know precisely
   what to sharpen. The harness is a construct-clarification engine as much as a validation engine.
3. **You are the protocol designer, not the rater.** The expert judgment you supply goes into *what gets
   asked*, not into every individual answer. A subject-matter expert, a panel, or (for the simple
   perceptual items) a small crowd supplies the answers. And we can dry-run the entire loop with a VLM
   standing in as the rater before spending one minute of scarce human attention — so when the SME
   arrives, the machinery is already proven and their time goes only to judgments.

---

## 2. The harness pipeline

```
corpus subset (DK-1 / S3)                      tagger engine (CNFA socket, versioned)
        │                                                 │
        ▼                                                 ▼
   stimulus set  ───────────────►  predicate values per stimulus  (with M1' tier + digest)
        │                                                 │
        ▼                                                 │
  elicitation  ──►  human responses  ──►  human latent scale per attribute (with CIs)
   (objective check  OR  adaptive 2AFC)                   │
        │                                                 │
        └──────────────►  AGREEMENT  ◄─────────────────────┘
                              │
                              ▼
                    VALIDATION LEDGER  (one immutable record per predicate × corpus × engine-version)
                              │
                              ▼
                  verdict ∈ { validated · candidate · failing }  +  the attribute r that seeds §4
```

Everything the harness emits is digest-bound to the exact engine version, corpus subset, and elicitation
run — the same audit discipline the engine already uses internally (M1′), now applied to the validation
itself. A verdict is never a status string; it carries its evidence.

---

## 3. The first slice — split by what "ground truth" means

The slice is deliberately small and chosen so that half of it validates immediately with no human, and
the other half exercises the adaptive-preference tie-in on constructs that matter for architectural
reading and for the ZHA direction.

### 3A. Objective-ground-truth predicates — validate now, no human

| Predicate | Ground truth checked against | What "validated" means |
|---|---|---|
| Isovist / eye-level visibility | Measured geometry from a Structured3D fixture (known plan) | Computed isovist matches the geometric isovist within tolerance |
| View-equity / sightline distribution | Same known geometry | Equity metric reproduces the hand-computed distribution |
| Faithful visual clutter — *computation* | The vendored Rosenholtz reference (already adjudicated vs `pyrtools` ~1e-7) | Implementation fidelity (already essentially done — formalize it as a ledger entry) |
| Selected plan metrics (from the 28) | Hand-measured plan quantities | Metric equals the measured quantity |

These give us a batch of genuinely validated predicates on day one, and they establish the ledger format
before any human judgment is involved. Note the clutter split: the *computation* is objective and nearly
done; whether the faithful measure tracks *human perceived* clutter is a separate, perceptual question —
which lives in 3B.

### 3B. Perceptual / evaluative predicates — need judgment (→ adaptive 2AFC, §4)

| Attribute (2AFC `key`) | Subject question | Why it needs a human |
|---|---|---|
| `perceived_clutter` | "Which room looks more cluttered?" | Tests whether the faithful clutter number tracks human perception, not just the reference math |
| `welcoming` | "Which entrance feels more welcoming?" | Affective; no geometric ground truth exists |
| `good_for_meeting` | "Which space looks better for a small meeting?" | Evaluative affordance; bridges to the space-use priorities |

Two or three is the right width for a first pass. Each maps directly onto the adaptive-preference
`AttributeSpec` (`key`, `question`), so no new elicitation UI is invented.

---

## 4. The adaptive-preference tie-in — and the one trap to avoid

### 4.1 What already exists (do not rebuild)

`Experiment_Maker/adaptive_preference/` is a verified Bayesian adaptive 2AFC system (v3.5.11): it shows a
participant two images, chooses the most *informative* next pair (information-gain sampling), and fits a
latent scale — recovering a known 10-item ranking at Spearman ρ ≈ 0.99, ~98% pairwise accuracy. On
11 July an **attribute layer** was added (`backend/attribute_layer.py`): a study is *about* a named
attribute, and `warm_start_state()` seeds the sampler's prior from the tagger — prior mean `= r · z(tagger)`,
prior variance `= 1 − r²`. `attribute_prior_benefit.py` shows a validated tagger at `r = 0.7` reaches a
reliable ranking in ~36% fewer comparisons, while a *calibrated* useless tagger (`r = 0`) collapses to
the flat prior — safe by construction. The single trust knob `r` is meant to come from "the validation
correlation the Knowledge-Atlas validation gives us." **That `r` is the harness's output.** The loop was
anticipated; what is missing is closing it with real data.

### 4.2 The trap: don't validate a tagger using a study the tagger seeded

If the tagger score seeds the prior of the very human study you then use to *measure* tagger↔human
agreement, the human posterior is contaminated by the tagger and the correlation is circular — you would
be grading the tagger against an echo of itself. This is the one methodological error that would quietly
invalidate everything, so the harness runs in **two explicit modes** and never blurs them:

- **Validation mode (tagger-blind).** Human 2AFC with a **flat prior** — the sampler is not warm-started
  from the tagger. The resulting human latent scale is independent of the tagger. `r` = correlation
  (tagger predicate, independent human scale). *This is the number that promotes a predicate from
  candidate to validated.*
- **Production/efficiency mode (tagger-as-prior).** Once `r` is measured and honest, *future* studies
  warm-start from the tagger to save human comparisons. This is the payoff, and it is only sound after
  validation mode has run.

Same engine, same UI, one flag. Keeping the modes distinct is the same ≠-mind discipline the program
already enforces between the LLM and the scores.

### 4.3 Why 2AFC rather than rating scales

For perceptual/evaluative constructs, "which is more X?" is more reliable than "rate X from 1–7":
forced choice sidesteps scale-use bias, anchoring, and drift, and it is the psychophysically standard
instrument. It also yields a *calibrated latent scale* (utilities with credible intervals), which is a
stronger thing to correlate a predicate against than a pile of ratings. And the adaptive sampler spends
human comparisons where they are most informative — which, usefully, is often exactly at the boundary
where the tagger and humans might disagree. So the preference engine doubles as an **active auditor** of
the predicate, hunting its failure boundary rather than sampling blindly.

### 4.4 The sampling caveat, and its fix

Adaptive (information-gain) sampling does not produce a random sample of image space, so a naive
tagger↔human correlation over adaptively-chosen pairs is a biased estimate. Fix: reserve a **random-sampled
hold-out** comparison set for the unbiased validation estimate, and use adaptive sampling for efficiency
and for probing the failure boundary. The ledger records which regime produced which number.

---

## 5. The seam — one small contract, no code coupling

The harness (in `Image_Tagger`) emits, and the adaptive-preference attribute layer (in `Experiment_Maker`)
consumes, a single per-attribute **validation record**. That is the entire interface; neither repo imports
the other's modules.

```json
{
  "attribute_key": "welcoming",
  "tagger_predicate_id": "<engine predicate>",
  "tagger_model_version": "<MODEL_VERSION hash>",
  "corpus_subset": "<DK-1 subset id>",
  "elicitation": { "mode": "validation-flat-prior", "engine": "adaptive_2afc@v3.5.11",
                   "n_subjects": 0, "n_comparisons": 0, "sampling": "random-holdout" },
  "human_scale": { "<stimulus_id>": { "utility": 0.0, "ci95": [0.0, 0.0] } },
  "agreement": { "spearman_r": 0.0, "r_ci95": [0.0, 0.0], "pairwise_accuracy": 0.0, "n_stimuli": 0 },
  "verdict": "candidate",
  "provenance": { "run_id": "", "created_utc": "", "audit_digest": "" }
}
```

`warm_start_state()` already wants exactly `r` (→ prior mean `r · z(tagger)`, variance `1 − r²`), so the
record is a drop-in. This also means the harness is useful to the platform *without* the platform lane
having to change anything until it chooses to.

---

## 6. Ownership & lanes (so nothing steps on another agent)

The **harness lives in `Image_Tagger`** (it consumes the CNFA socket outputs and owns the ledger). The
**adaptive-preference engine + attribute layer live in `Experiment_Maker`** (David's repo) and its
`platform_port/` targets `experiment-platform` — the `ccode` one-committer lane, which receives
**findings, not edits**. The seam in §5 is a data contract, so the tagger side can be built and exercised
independently; any change the platform needs is delivered as a findings note, never a direct edit. The
first slice needs no platform change at all — the 2AFC engine already runs standalone.

---

## 7. First-session plan (what "together, now" looks like)

1. **Freeze the ledger format** (§3 table + §5 record) and write the two objective-truth entries — isovist
   and view-equity against the existing Structured3D fixture — so we have *validated* predicates and a
   working ledger before any human step. *(No human; doable immediately.)*
2. **Formalize the clutter computation entry** from the existing pyrtools adjudication — a near-free
   validated entry that also sets up the perceived-clutter study in 3B.
3. **Draft the three 2AFC protocols** (`perceived_clutter`, `welcoming`, `good_for_meeting`) as
   `AttributeSpec`s, each with its subject question, the tagger predicate it will be correlated against,
   and the stimulus set from a DK-1 subset.
4. **VLM dry-run** of the full loop in validation mode (flat prior), VLM as stand-in rater, over a random
   hold-out set — proving label-ingestion → pairing → latent-scale fit → agreement → ledger end-to-end.
5. **Read out** which predicates are validated, which remain candidate, and — for each judgment attribute
   — the exact protocol an SME would run to produce the real `r`. That read-out *is* "what we need to
   know," made concrete.

Steps 1–2 produce real validated predicates with no human. Steps 3–4 stand the judgment loop up and prove
it without spending human time. Step 5 hands you (and an eventual SME) a ready-to-run protocol and a
precise list of open construct questions.

---

## 8. Honest cautions

- **Circularity (§4.2)** is the load-bearing caution — validation studies must be tagger-blind.
- **Small-N first.** Keep the first slice to ~2–3 judgment attributes and a modest stimulus set; the VLM
  dry-run keeps us from building ahead of what we can exercise.
- **A predicate may fail.** That is the point, not a setback — a failing verdict is a true result and
  redirects effort away from a measure that does not track what we thought.
- **VLM ≠ human.** The VLM dry-run proves the *plumbing*, and can be a *third* comparison signal, but it
  does not substitute for the human `r` on a perceptual/evaluative attribute.
- **Scope is David's.** Which attributes matter, and which verdicts gate downstream use, are science
  decisions, not harness decisions.

---

*Prepared 2026-07-30 as a proposal. Grounded in the tagger current-state docs, the
`Experiment_Maker/adaptive_preference` system (v3.5.11 + 11 July attribute layer, verified ρ ≈ 0.99),
and the 29 July QA-architecture/panel material. No other lane's code is modified; platform pieces are
consumed as contracts.*
