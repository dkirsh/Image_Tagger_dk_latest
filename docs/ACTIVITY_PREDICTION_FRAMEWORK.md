# From Pixels to People — Predicting Activity from Annotation

How can constellations of physical attributes that we detect or infer
from image annotations support credible claims about what is likely to
happen where, for whom, and when?

---

## Part I: Activity Taxonomy

We need a structured list of activities before we can predict them.
The taxonomy below synthesizes Gehl (2011), Whyte (1980), Alexander
(1977), and environmental psychology into 24 activities across 5 tiers.

### Tier 0: Passage (necessary, brief, low sensitivity to environment)

| # | Activity | Duration | Group size | Gehl class |
|---|----------|----------|-----------|------------|
| A01 | **Walking through** | <1 min | 1 | Necessary |
| A02 | **Wayfinding / orienting** | 5–30s | 1 | Necessary |
| A03 | **Waiting (standing)** | 1–5 min | 1–2 | Necessary |

### Tier 1: Solitary dwelling (optional, moderate sensitivity)

| # | Activity | Duration | Group size | Gehl class |
|---|----------|----------|-----------|------------|
| A04 | **Solitary focused work** (reading, laptop) | 15–120 min | 1 | Optional |
| A05 | **Solitary contemplation** (sitting, thinking) | 5–30 min | 1 | Optional |
| A06 | **People-watching** | 5–60 min | 1 | Optional/Social |
| A07 | **Phone call** (private) | 2–15 min | 1 | Optional |
| A08 | **Eating alone** | 10–30 min | 1 | Optional |

### Tier 2: Dyadic social (social, high sensitivity)

| # | Activity | Duration | Group size | Gehl class |
|---|----------|----------|-----------|------------|
| A09 | **Intimate conversation** | 10–60 min | 2 | Social |
| A10 | **Professional meeting** (1-on-1) | 15–60 min | 2 | Social |
| A11 | **Chance encounter** (greeting, brief exchange) | 0.5–3 min | 2 | Social |
| A12 | **Collaborative desk work** (shoulder-to-shoulder) | 30–120 min | 2 | Social |

### Tier 3: Small-group social (social, very high sensitivity)

| # | Activity | Duration | Group size | Gehl class |
|---|----------|----------|-----------|------------|
| A13 | **Small group conversation** (3–5 people) | 10–45 min | 3–5 | Social |
| A14 | **Informal meeting / stand-up** | 5–15 min | 3–6 | Social |
| A15 | **Collaborative workshop** | 30–120 min | 4–8 | Social |
| A16 | **Shared meal** | 20–60 min | 3–8 | Social |
| A17 | **Presentation / lecture** (small) | 15–60 min | 5–20 | Social |

### Tier 4: Special modes

| # | Activity | Duration | Group size | Gehl class |
|---|----------|----------|-----------|------------|
| A18 | **Restorative pause** (stress recovery) | 5–20 min | 1 | Optional |
| A19 | **Creative brainstorm** | 15–60 min | 2–6 | Social |
| A20 | **Conflict / difficult conversation** | 10–30 min | 2–3 | Social |
| A21 | **Play** (children or adults) | 5–60 min | 2–10 | Social |
| A22 | **Meditation / mindfulness** | 5–30 min | 1 | Optional |
| A23 | **Napping / resting** | 15–60 min | 1 | Optional |
| A24 | **Performance / exhibition viewing** | 5–60 min | 1–many | Social |

---

## Part II: Physical Conditions for Each Activity

For each activity, what physical conditions does it *require*, *prefer*,
or *reject*? These are drawn from the literature and expressed as ranges
over the attributes we can compute.

### Legend

| Symbol | Meaning |
|--------|---------|
| ↑ | High value preferred (> 0.6) |
| ↓ | Low value preferred (< 0.3) |
| ∼ | Moderate / indifferent (0.3–0.6) |
| ✗ | Condition actively rejected |
| — | Not relevant |

### Condition signatures

| Activity | Enclosure | Prospect | Brightness | Glare | Warmth | Acoustics (absorption) | Saliency (distraction) | Sociopetal layout | Edge proximity |
|----------|-----------|----------|------------|-------|--------|----------------------|----------------------|-------------------|---------------|
| **A01 Walking through** | — | ↑ | ∼ | ✗ | — | — | ∼ | — | — |
| **A02 Wayfinding** | — | ↑ | ↑ | ✗ | — | — | ↑ (landmarks) | — | — |
| **A03 Waiting** | ∼ | ∼ | ∼ | ✗ | — | — | ∼ | — | ↑ (Whyte) |
| **A04 Focused work** | ↑ | ↓ | ↑ | ✗ | ∼ | ↑ (quiet) | ↓ | — | ↑ |
| **A05 Contemplation** | ↑ | ∼ | ∼ | ✗ | ↑ | ↑ (quiet) | ↓ | — | ↑ |
| **A06 People-watching** | ∼ | ↑ | ∼ | — | — | — | ↑ | — | ↑ |
| **A07 Phone call** | ↑ | ↓ | ∼ | — | — | ↑ (quiet) | ↓ | — | — |
| **A08 Eating alone** | ∼ | ∼ | ∼ | ✗ | ↑ | ∼ | ∼ | — | ↑ |
| **A09 Intimate conv.** | ↑ | ↓ | ↓ | ✗ | ↑ | ↑ (speech priv.) | ↓ | ↑ | ↑ |
| **A10 Professional mtg** | ↑ | ↓ | ↑ | ✗ | ∼ | ↑ (speech priv.) | ↓ | ↑ | ∼ |
| **A11 Chance encounter** | ↓ | ↑ | ∼ | — | — | ∼ | — | — | — |
| **A12 Collab desk work** | ∼ | ↓ | ↑ | ✗ | ∼ | ∼ | ↓ | ↑ | — |
| **A13 Small group conv.** | ∼ | ∼ | ∼ | ✗ | ↑ | ↑ (absorb) | ↓ | ↑ | — |
| **A14 Informal stand-up** | ↓ | ↑ | ↑ | ✗ | — | ∼ | ∼ | — | — |
| **A15 Workshop** | ∼ | ↓ | ↑ | ✗ | ∼ | ↑ | ↓ | ↑ | — |
| **A16 Shared meal** | ∼ | ∼ | ∼ | ✗ | ↑ | ∼ | ∼ | ↑ | — |
| **A17 Presentation** | ↑ | ↓ | ↑ (screen) | ✗ | — | ↑ | ↓ | ↓ (focal) | — |
| **A18 Restorative pause** | ∼ | ↑ | ∼ | ✗ | ↑ | ↑ (quiet) | ↓ | — | ↑ |
| **A19 Brainstorm** | ∼ | ∼ | ↑ | ✗ | ↑ | ∼ | ∼ | ↑ | — |
| **A20 Difficult conv.** | ↑ | ↓ | ↓ | ✗ | ∼ | ↑ (privacy!) | ↓ | ↑ | ↑ |
| **A21 Play** | ↓ | ↑ | ↑ | — | — | ↓ (lively ok) | ↑ | — | — |
| **A22 Meditation** | ↑ | ∼ | ↓ | ✗ | ↑ | ↑ (quiet!) | ↓ | — | ↑ |
| **A23 Napping** | ↑ | ↓ | ↓ | ✗ | ↑ | ↑ (quiet) | ↓ | — | ↑ |
| **A24 Exhibition viewing** | ↓ | ↑ | ↑ (on art) | ✗ | — | ∼ | ↑ (on exhibits) | — | ↑ (Whyte) |

### Literature sources for the signatures

| Condition | Basis | Citation |
|-----------|-------|----------|
| Enclosure ↑ for privacy activities | Introverts and private activities need lower arousal environments; enclosure reduces arousal | Mehrabian & Russell 1974; Stamps 2005 |
| Prospect ↑ for people-watching, passage | Appleton 1975 prospect-refuge; Whyte 1980 "people sit where there are places to see other people" | Appleton 1975; Whyte 1980 |
| Edge proximity ↑ for sitting activities | "The edges do the work" — people prefer to sit at edges, not centers | Whyte 1980 |
| Acoustics ↑ for private conversation | Speech privacy requires α > 0.3; conversation needs S/N > 15 dB | Kuttruff 2009; ASHRAE Standard 189.1 |
| Warmth ↑ for dwelling activities | Warm colour temperatures (< 3000K) are associated with longer dwell times and relaxation | Küller et al. 2006; Cajochen et al. 2005 |
| Glare ✗ for all seated activities | Discomfort glare disrupts any sustained visual task or social interaction | Wienold & Christoffersen 2006 (DGP) |
| Sociopetal ↑ for face-to-face activities | Osmond 1957 — sociopetal layout arranges seats to face each other; Hall 1966 social distance | Osmond 1957; Hall 1966 |
| Saliency ↓ for concentration | High visual distraction disrupts focused work | Kaplan 1995 (attention restoration); Mehrabian & Russell 1974 |
| Low brightness for intimacy/rest | Dim light signals relaxation, reduces alertness | Cajochen et al. 2011; Küller & Wetterberg 1993 |

---

## Part III: Personality Moderators

The same space affords different things to different people.

### Introvert–extrovert modulation

Per Mehrabian & Russell (1974) and optimal stimulation level theory
(Zuckerman 1979), introverts have a *lower threshold for arousal*:

| Attribute | Effect on introvert preference | Effect on extrovert preference |
|-----------|-------------------------------|-------------------------------|
| Enclosure | Shifts threshold UP (+0.15) — introverts prefer *more* enclosure | Shifts threshold DOWN (−0.15) — extroverts tolerate less enclosure |
| Prospect | Shifts threshold DOWN (−0.10) — too much openness is over-stimulating | Shifts threshold UP (+0.10) — extroverts seek stimulation |
| Brightness | Moderate preferred — too bright = over-arousing | Higher tolerance for bright, active environments |
| Saliency/distraction | Strong rejection (↓ strengthened) | Moderate tolerance |
| Acoustics | Strong preference for absorption (quiet) | More tolerance for reverberant / lively acoustics |

**Implementation:** Multiply the condition-signature arrows by a
personality weight vector `w_i = [1.15, 0.90, 0.95, 1.20, 1.10]` for
introverts, `w_e = [0.85, 1.10, 1.05, 0.80, 0.90]` for extroverts
(preliminary; needs empirical calibration).

### Chronotype / time-of-day modulation

Per circadian research (Cajochen et al. 2005, 2011):

| Time | Modulation |
|------|-----------|
| **Morning (06–10)** | Brightness preference ↑↑ (need cortisol-boosting light); warmth preference ↓ (cool-white light supports alertness); focused-work activities favored |
| **Midday (10–14)** | Baseline — no modulation |
| **Afternoon (14–17)** | Post-lunch dip — restorative pause (A18), contemplation (A05) favored; prospect ↑ for attention restoration (Kaplan 1995) |
| **Evening (17–21)** | Brightness preference ↓↓ (melatonin onset); warmth preference ↑↑ (warm dim light); social activities favored over focused work |

---

## Part IV: The Attribute → Activity Prediction Pipeline

### Step 1: Compute attribute constellation (we have this)

For each image, the annotation pipeline produces a feature vector:

```
x = [enclosure, prospect, brightness_variance, glare_risk,
     warmth_ratio, acoustic_absorption, landmark_salience,
     sociopetal_score, edge_fraction, ...]
```

### Step 2: Match against activity signatures (new)

For each activity $A_k$, the condition signature from Part II defines
a **profile vector** $p_k$ (with ↑ = 0.8, ∼ = 0.5, ↓ = 0.2, ✗ = 0.0)
and a **relevance mask** $m_k$ (1 if the attribute matters, 0 if "—").

Compute a **signature match score**:

$$\text{match}(x, A_k) = 1 - \frac{\sum_i m_{ki} \cdot |x_i - p_{ki}|}{\sum_i m_{ki}}$$

This gives a [0,1] score: how well the space's measured attributes match
the ideal conditions for activity $A_k$.

### Step 3: Apply moderators (new)

Adjust the match score for personality and time of day:

```
match_adj = match(x, A_k) × personality_weight(trait, A_k) × time_weight(hour, A_k)
```

### Step 4: Calibrate with Gemini (new — the VLM bridge)

The match score is a physical-conditions prediction. Gemini sees the
*image* and makes a semantic prediction. The two should agree.

**Prompt protocol for Gemini:**

```
You are rating the likelihood of specific activities occurring in
this architectural space. For each activity, rate:

  LIKELY    — you would expect to see this activity here
  POSSIBLE  — it could happen but isn't especially invited
  UNLIKELY  — the space seems wrong for this activity
  VERY_UNLIKELY — the space actively discourages this activity

Activities to rate:
  1. Solitary focused work (reading, laptop)
  2. Intimate conversation (2 people, personal topic)
  3. Small group meeting (3–5 people, professional)
  4. Phone call (private)
  5. People-watching
  6. Restorative pause (stress recovery)
  7. Play (children or adults)
  8. Chance encounter (greeting a stranger)
  [... full list of 24 ...]

For each, also state the ONE physical feature of the space that most
influences your rating (e.g., "the large window," "the enclosed alcove,"
"the hard floor surfaces").
```

**Why this works:** If our attribute constellation predicts "A09 intimate
conversation: LIKELY" but Gemini says "UNLIKELY because the space is too
open and echoey," we have a **disagreement signal** that either:
- Our attributes are wrong (miscomputed)
- Our condition signature is wrong (the literature doesn't match this case)
- Gemini is wrong (possible but less likely for obvious cases)

The disagreement is more informative than either prediction alone.

### Step 5: Cross-validate and learn (future)

Over many images:
1. Collect `(attribute_vector, activity, match_score, gemini_rating)` tuples
2. Train a lightweight model (logistic regression or random forest) to
   predict Gemini's rating from the attribute vector
3. Where the model diverges from the condition signatures, we learn which
   physical conditions actually matter (vs. which we assumed from theory)
4. Update the condition signatures with empirical evidence

This closes the loop: **theory → measurement → prediction → validation → theory**.

---

## Part V: What We Can't Detect Yet (Gaps)

| Missing attribute | Why it matters | How to get it |
|-------------------|---------------|---------------|
| **Seating count + arrangement** | Most social activities require seating; sociopetal score needs seat detection | Object detection (YOLO) or VLM |
| **Ceiling height** | Mehrabian-Russell arousal; prospect-refuge; Alexander Pattern 190 | Monocular depth + plane geometry, or VLM estimate |
| **Material texture** (soft vs hard) | Acoustic absorption; warmth perception; tactile affordance | Material segmentation model or VLM |
| **Greenery / biophilia** | Kaplan (1995) attention restoration; stress recovery (A18) | Segmentation (plants class) or VLM |
| **Signage / wayfinding cues** | Legibility; reduces anxiety in wayfinding (A02) | OCR + VLM |
| **People present** | Social density; Whyte's "people attract people" | Person detection (already L3) |
| **Sound** | We estimate absorption but can't measure actual SPL from an image | Inherent limitation of image-only annotation |
| **Smell** | Affects dwell time (coffee shops, bakeries vs. chemical plants) | Undetectable from images |

---

## Part VI: The Claim Structure

When the system produces a prediction, the claim must be structured:

```
CLAIM: Activity A09 (intimate conversation) is LIKELY in this space.

PHYSICAL EVIDENCE:
  enclosure = 0.82 (high, from wall/ceiling plane coverage)
  prospect = 0.15 (low, limited sightlines)
  acoustic_absorption = 0.41 (moderate-high, soft furnishings)
  sociopetal_score = 0.70 (two chairs facing each other)
  brightness_variance = 0.45 (moderate, not harsh)
  warmth_ratio = 0.62 (warm colour palette)

SIGNATURE MATCH: 0.81 (from condition table, A09 profile)

MODERATORS:
  Introvert adjustment: +0.06 (introverts especially drawn here)
  Evening adjustment: +0.04 (dim warm light favours intimate talk)

VLM CORROBORATION: Gemini rates A09 as LIKELY.
  Cited reason: "The enclosed alcove with warm lighting and
  facing seating arrangement invites private conversation."

CONFIDENCE: 0.73
  - enclosure from heuristic plane segmentation (conf 0.45)
  - acoustics from visual material proxy (conf 0.50)
  - sociopetal from manual seat boxes (conf 0.55)
  Weakest link governs: 0.45 × confidence_scaling

FAILURE MODES:
  - Acoustic estimate is visual, not measured
  - Sociopetal score requires seat detection (manual in this case)
  - Camera doesn't capture ambient noise level
```

This is the kind of output that can go in a paper. It's not "the AI
says people will chat here." It's: "the physical attributes measured
from the image form a constellation that, according to [list of
citations], is associated with intimate conversation, modulated by
personality and time of day, and independently corroborated by a VLM."

---

```
Document authored: 2026-07-14
```
