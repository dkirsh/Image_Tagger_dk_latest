# Human Review Protocol — Phase-1 species hypotheses

*How David and Stephan drive the review-pack viewer. One page. Lives at
`docs/validation/review_pack/REVIEW_PROTOCOL.md`. Pairs with `viewer.html`.*

## What you are doing (and not doing)
You are judging whether the tagger's **hypothesis** for an image matches your perception — *is this species
present, and roughly to this degree?* You are **not** grading the exact number. The scores are **uncalibrated
provisional severity** (the viewer says so in the banner); read them as low / medium / high, not as truth.
The tagger's outputs are hypotheses to be confirmed or objected to, never an answer key.

## The three lead species (operational definitions)
- **surface_density** — how much stuff covers surfaces per unit area (local-object density). High = a
  junk-covered desk. *Independent of how the big furniture is arranged.*
- **arrangement_disorder** — how disordered the placement of the **large** elements is (anchor-level layout).
  Higher = more disordered. A tidy but junk-covered room is high surface_density, low arrangement_disorder;
  three chairs knocked askew in an empty room are the reverse.
- **textural_discomfort** — visual "grating" discomfort: departure from natural 1/f statistics (dense stripes,
  buzzing patterns). This is the fast affective channel, not a semantic judgment.

If you find yourself wanting to move a case to a *different* species, that is a signal — log it as
`species-misdefined` (see below). Those are the most valuable objections.

## How to sample (use the bins)
For each of the three species, work the bins in this order, not the whole set at once:
1. **boundary** — the tagger's own uncertain cases. Most informative; do these first.
2. **low**, then **high** — check the extremes read correctly.
3. **intermediate** — the messy middle.
Aim for a fixed budget per session (e.g. ~30 per species) rather than exhausting one bin.

## The decision (three buttons)
- **Accept** — the hypothesis matches what you see.
- **Reject** — it doesn't. Then pick an **objection category** and add a one-line note:
  - `wrong-presence` — species is absent (or present) and the tagger says the opposite.
  - `wrong-degree` — right species, wrong severity.
  - `species-misdefined` — the case exposes a problem with the species itself (overlaps another, ill-defined).
  - `image-quality` — the image is unusable (crop, artifact) — not the tagger's fault.
  - `ambiguous-exemplar` — a genuinely borderline example worth keeping as a boundary case.
  - `other` — anything else; explain in the note.
- **Uncertain** — you genuinely can't tell. This is a real answer, not a cop-out; it flags a case for the
  disagreement queue.

Judge each case **on its own** (discrimination), don't rank the whole set against each other.

## Two reviewers → one signal
David and Stephan review **independently first**, then compare. Cases where you disagree become the
**disagreement queue** and get priority in the next corpus round. Do not reconcile by discussion before both
have logged — the disagreement itself is data.

## When done
Click **Export reviews ↓** (top right). It downloads `review_decisions.json` **without touching the source
replay** — send that file back. Cowork ingests it, reports the objection patterns, and the rejected/uncertain
set drives the next active-corpus selection.

## What happens to your decisions
- `species-misdefined` / dropping / redefining a species → **decision reserved for you and Stephan** (per
  the coordination protocol); cowork drafts, you decide.
- `wrong-degree` on a systematic pattern → **measure fix** (Codex, tagger lane).
- accepted exemplars → **teaching-set updates** (cowork), which feed the HITL instrument.
Nothing here changes the tagger automatically; review produces objections, and objections are triaged by lane.
