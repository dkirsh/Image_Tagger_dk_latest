# The Image Tagger — An Introduction

*A machine that reads a room from a photograph — and says so out loud when it cannot.*

**For a person, not an agent.** If you are about to change code here, read
[`REPO_STATE_MODEL_AND_PLAN.md`](REPO_STATE_MODEL_AND_PLAN.md) instead — it answers *what will I break*.
**Audience:** a cognitive-science graduate student. No architecture or computer-vision background assumed.
**Provenance convention:** **[verified]** = read out of this repository or produced by a command recorded
in the state model. **[open]** = intended, not yet built. No number appears here without one of those tags.

- `STATE_AS_OF: 2026-08-05T23:40Z`
- `HEAD: 49fac503`
- `STALE_AFTER_DAYS: 30`
- `JUDGED_REVIEWED: 2026-08-05`
- `JUDGED_REVIEW_INTERVAL_DAYS: 90`

---

## 1 · What the machine is for

A building can be described two ways. The **physical code** says what is geometrically there: wall
positions, ceiling height, lux at the desk, square metres per person. It is occupant-independent, and it
is what building regulations certify.

The **cognitive code** says what the space affords, means, and does to the people in it: whether you can
see far enough to feel safe, whether the layout tells you where you are, whether the visual field is
cluttered enough to cost you attention. It is a description of the **building–occupant relation**, not
of the object.

This repository exists to compute as much of the second as the evidence honestly permits, from a
photograph or a floor plan — **and to refuse to invent the rest** **[verified — this framing is the
founding vision document's]**.

The organising theory is the **register model** **[verified]**: any reading of a space is a move within
one or more registers — metric, morphological, luminous, tectonic, perceptual, affective, affordance,
configurational, semantic, evaluative, comparative. The founding claim is that the interesting knowledge
lives *between* registers, because that is where an architect's own critique lives. Filling the registers
is the annotation problem; computing their tensions is the intelligence problem.

---

## 2 · The ladder, and why every rung is validated

The method is a three-rung climb, and the discipline is that **every rung is operational and every
composition is validated** **[verified]**:

```
RUNG 3   COGNITIVE / NEURO-ARCHITECTURE CONSTRUCTS
         restoration · affect · wayfinding effectiveness · activity fit · beauty
              ▲  composed from rung 2, validated against human judgement
              │
RUNG 2   PERCEPTUAL & TECTONIC ATTRIBUTES
         enclosure · prospect · refuge · reverberation · complexity · legibility
              ▲  composed by a STATED FORMULA from rung 1, checked against people
              │
RUNG 1   OPERATIONAL PRIMITIVES
         quantities computed directly from pixels, depth, segmentation
```

**Figure 1.** The direction of travel matters more than the levels. Most systems that claim to score a
space for "restoration" jump straight to rung 3 and calibrate against a preference rating — which makes
the construct unfalsifiable, because nothing below it is separately checkable. Here each rung is a
computed quantity with a name, and each composition upward is a formula someone can dispute. A wrong
answer at rung 3 can be traced to the rung it came from.

For a cognitive scientist the shape is familiar: this is operationalisation with the construct-validity
argument left visible instead of collapsed into a fitted score.

---

## 3 · The thing that makes it unusual: it is allowed to abstain

**The failure this repository is built against is not a wrong number. It is a *confident* wrong
number** **[verified]**.

So the engine's stated objective is not accuracy. It is this **[verified]**:

> produce a per-image, per-predicate value whose derivation can be re-executed by someone who does not
> trust the person who produced it — and which says ABSTAINED, loudly and with evidence, whenever it
> cannot.

Three mechanisms implement that:

- **Abstention with evidence.** A predicate may return no value, and must say what was missing. Concretely
  **[verified]**: `blind_corner_index` needs a morphological skeleton, which needs the `skimage` library.
  Without it the result is `scalar=None`, `reason="skimage_unavailable"`, and a named failure mode. **That
  is the system working.** A newcomer who reads it as a crash will "fix" the wrong thing.
- **Tiers.** Every result is graded GREEN (firm), AMBER (supported, but disclose the assumption), or RED.
  Most of the current predicate set is AMBER **[verified]** — which is not weakness but the mechanism by
  which the engine reports honest uncertainty instead of false confidence.
- **An audit spine that can fail.** Every run is checked against an eight-class audit; tampering or
  fabricated inputs flip the result to RED rather than producing a plausible number. In a recorded
  three-image run the engine **rejected a deliberately fabricated control** and replayed idempotently
  **[verified]**.

**The paradox worth remembering**, and the sharpest idea in the repository **[verified]**: a self-test
suite exercised only on a fully-equipped machine cannot execute any abstention path — so *the
better-equipped your laptop, the blinder the governance tests you run on it*. Abstention is the product,
and only the deprived environment tests it.

---

## 4 · The structural fact that will cost you a day

**There are two independent attribute engines in this repository, and they are not connected to each
other** **[verified]**.

| | **Engine A** — the research core | **Engine B** — the production app |
|---|---|---|
| Where | `cnfa_algs/` + `annotation_socket/` | `Image_Tagger_3.4.74_vlm_lab_TL_runbook_full/` |
| What | 68 predicates: ~40 image attributes + 28 plan metrics | React/FastAPI/Postgres web app, Dockerised |
| Vocabulary | `annotation_socket/registry.py` | `contracts/attributes.yml` — *different namespace, different keys* |
| Who uses it | the science | students, and the pilot |

Told "work on the tagger's attributes," you have roughly even odds of editing the engine that has nothing
to do with the outcome you were asked to change. The heuristic **[verified]**: predicates, registry,
abstention, tiers, audit, verification → **Engine A**. Upload, payload, segmentation model, latency, front
end → **Engine B**.

Engine A currently runs *parallel to* the app; making it the app's canonical science-run is named, open
work **[verified]**.

---

## 5 · Where this sits in the wider programme

- **The cognitive-code argument** it computes against lives in `Post_Occupancy_Evals`
  (`POE_Cognitive_Code_v1_2026-07-09.md`) **[verified]**. Say it this way: *that repository holds the
  argument; this one holds the instrument.* The operational POE pilot — protocol, sensor list, IRB outline —
  is in **this** repository's `docs/`, not that one.
- **Article_Eater / Knowledge_Atlas** are the literature-grounding layer. The intended tie is that every
  attribute's literature anchor is grounded in the corpus. **The mechanical pipe does not exist yet**
  **[verified]** — the tagger does not auto-query the Atlas for its citations.
- **BN_graphical** is a *conceptual* connection: the computed attributes are meant to become the feature
  vector for image → psychology prediction. **There is no code or document reference to `BN_graphical`
  anywhere in this repository** **[verified]**. Do not describe it as a working pipe.

---

## 6 · The epistemic problem the programme has not solved

Worth knowing early, because it shapes what a validation study here can mean **[verified]**:

> the engine's measures are *theory-laden* — a speech-transmission reading "means" degraded comprehension
> only because we accept the speech-intelligibility science and have entrenched it. But our
> post-occupancy tests are themselves based on the engine. So a POE cannot be a clean test of the science
> it presupposes — that would be circular.

The proposed resolution is Quinean rather than foundational: separate the applied register from the
declared instrument-conformance register, treat POE as fixed-IV/measured-DV observational data, and record
prediction-versus-observation divergences in a **challenge ledger** as first-class objects with
entrenchment-aware routing. The ledger is specified and self-tested but **not yet wired to the engine**
**[open]**.

---

## 7 · Honest limits

- **No human or biosignal construct validation has been done, for any predicate** **[verified]**. Rung-2
  and rung-3 claims are therefore *candidate measures and hypothesis generators, not validated occupant
  outcomes* — the panel reclassified them exactly that way.
- **The audit evidence is builder-run, not certified** **[verified]**: the same author wrote both the
  annotator and the verifier. The repository says so itself.
- **No CI exists** **[verified]**. Every check is manual.
- **The calibration corpus is only partly identity-checked** **[verified]**: of 538 catalogued images, 369
  carry a SHA-256; the **164-image A/B pair set — the images grounding every comparative "this one is
  better" claim — has no content hash in either manifest.**
- **The comparative and evaluative registers do not exist** **[verified]**. The system describes; it does
  not yet critique or search by similarity — the founding document's "central near-term build" is still
  unbuilt.

**What it is designed to be bad at.** It will not certify anything about a real building. It will tell you
what can be computed from an image, how firmly, by what formula, and where it refused to answer.

### Who owns each of these, and what unblocks it

None of the limits above is an oversight; each is tracked work with a named home. If you want to help,
this is the table to read — and the blocking condition tells you whether you *can*.

| Limit | Owner | Blocked on |
|---|---|---|
| No human/biosignal construct validation | David — it needs subjects | An approved protocol. The pilot design already exists in `docs/POE_Pilot_Kit_Protocol_Instruments_IRB_ZHA_2026-07-21.md`; IRB is a separate gate |
| Audit evidence is builder-run, not certified | a reviewer who is **not** the author | Nothing technical — it needs a different mind to re-run the socket and countersign |
| No CI | repo maintainer | Nothing; there is no `.github/workflows` and adding one is unblocked work |
| A/B pair set (164 images) has no content hash | repo maintainer | Nothing — the hash column exists in `_provenance.csv` for the other 369; the curated set simply never got one. This is the cheapest real improvement available here |
| Comparative + evaluative registers absent | the programme (the founding doc's "central near-term build") | Sequencing, not capability — it has been deferred behind engine work since July |
| Challenge ledger not wired to the engine | the programme | Engine A becoming the app's canonical science-run first |
| No Atlas pipe for literature anchors | cross-repo | Article_Eater's own repair programme, which is under separate ownership |

**Ask David** about anything involving subjects, IRB, or which construct matters. **Ask the repo
maintainer** about the corpus, the registry, and the two engines. **Do not** ask an agent to certify its
own output — that is the one thing the audit design forbids.

---

## 8 · Traps, in the order they will bite

1. **Editing the wrong engine** (§4).
2. **Reading an abstention as a failure** (§3) — check `reason` and `failure_modes` first.
3. **The repository is not self-contained** **[verified]** — the audit spine imports from a sibling
   `_control/` directory by absolute path, and 13 tracked Python files hard-code `/Users/davidusa`. An audit
   apparatus that runs only on the audited person's machine is not yet an audit apparatus.
4. **A clean clone does not carry the rules** **[verified]** — `.gitignore` blocks `CLAUDE.md` and every
   `*PROMPT*.md`. You will be working without the operating rules and will not know it.
5. **Working in the wrong repository** **[verified]** — a sibling `image-tagger/` from April looks like this
   project. Check `governance.json` for `"canonical": true` before you start, every time.
6. **Trusting a green test run on a well-equipped machine** (§3).
7. **Quoting a corpus result without checking the corpus is present** **[verified]** — code reading the
   manifest will run happily over zero images and report a clean result. A pass on an empty corpus is the
   purest form of the failure this repository is about.

---

## 9 · Where to go next

| You want | Read |
|---|---|
| the founding vision and the register model | `docs/VISION_AND_DIRECTION_2026-07-14.md` |
| what has actually been built since, with honesty tags | `docs/VISION_AND_DIRECTION_2026-07-30.md` |
| the current programme and the epistemics section | `docs/PROGRAM_STATE_AND_DIRECTION_2026-08-01.md` |
| to change code without breaking something | [`REPO_STATE_MODEL_AND_PLAN.md`](REPO_STATE_MODEL_AND_PLAN.md) |
| the whole system this serves | `Article_Eater_PostQuinean_v1_recovery/docs/ATLAS_SYSTEM_DESCRIPTION_AND_WORKPLAN_2026-07-21.md` and its appendices in `docs/Describing_the_System/` |

---

## Provenance

The physical-code/cognitive-code contrast, the register model and the three-rung ladder are from
`docs/VISION_AND_DIRECTION_2026-07-14.md`. The built-since account, the 68 predicates, the tiers and the
fabricated-control rejection are from `docs/VISION_AND_DIRECTION_2026-07-30.md` and
`annotation_socket/SOCKET_CONFORMANCE.md`. The stated objective, the confident-wrong-number framing, the
two-engine fact, the abstention example, the well-equipped-machine paradox and the trap list are from
`docs/REPO_STATE_MODEL_AND_PLAN.md` (§§1, 5, 7) with the `blind_corner_index` behaviour read in
`cnfa_algs/wave2_geometry.py`. The theory-ladenness passage and the challenge ledger are from
`docs/PROGRAM_STATE_AND_DIRECTION_2026-08-01.md` §3.7 and
`docs/validation/CHALLENGE_LEDGER_SPEC_2026-08-01.md`. The corpus and hash figures are from
`corpus_L6/manifest.csv` and `_provenance.csv`. The absence of a `BN_graphical` reference was established by
search, not assumed. **No claim is made here about how this system compares to others, because no such
comparison has been run in this repository.** Structure and the `[verified]`/`[open]` convention follow
`Article_Eater_PostQuinean_v1_recovery/docs/ATLAS_SYSTEM_DESCRIPTION_AND_WORKPLAN_2026-07-21.md`.
