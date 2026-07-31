# Image_Tagger — Program Roadmap

*Whole-repo upgrade plan. Last updated 2026-07-31 by cowork. Lives at
`docs/PROGRAM_ROADMAP.md`. This is the map; the coordination mechanics live in
`docs/validation/coordination/COORDINATION.md`.*

## What this program is trying to become

The tagger started as an image-only measurer. The goal now is a **multi-register
reader of spaces**: given an image (later, a 3D intake) of a room or scene, it
emits graded, evidence-backed hypotheses about how that space is likely to act on
the people in it — cognitively, affectively, and for health/wellbeing — and it
knows what it does *not* know.

Three sources of knowledge feed it, and we should be explicit about which is which:

1. **What others already know** — the literature. Systematic, evidence-graded
   review (firm / framework / contested). This is the materials encyclopedia, the
   social-presence strand, the acoustics and biophilic-restoration bodies. Cheap,
   fast, and it stops us re-deriving settled science.
2. **What you can know by looking well** — the tagger intelligently exploring the
   images we already hold. Image-only measures (the null model) plus per-species
   hypotheses. This is where the tagger earns its keep and where its *residual*
   (what image stats miss) becomes a measurement, not an embarrassment.
3. **What only people can tell us** — the HITL studies. Human judgement on the
   cases the first two can't settle: species presence/degree, the late/observer
   component, preference. Expensive, so spent only where 1 and 2 leave real doubt.

The roadmap below is organised by **strand** (what we're building) and then by
**sequence** (what order, who owns it). The ordering principle: exhaust cheap
knowledge (1) before expensive knowledge (3), and never let the tagger's own
outputs (2) masquerade as an answer key.

---

## Strands

### A. Clutter / perceived-complexity species  *(lead strand, furthest along)*
The tagged facet vector: `surface_density`, `arrangement_disorder`, `variety`,
`textural_discomfort`, `semantic_incongruity`, `concealed_order` — each tagged with
its operation / processing stage / channel (cognitive-effort vs affective-stress).
Reference image measures are the null model; the tagger residual measures the
late/observer component.
- **Done:** theory manuscript, reference measures, teaching sets, facet 2AFC study,
  canonical naming (`arrangement_disorder`, higher = more disordered).
- **Open:** corpus replay (Codex) → review-pack viewer (cowork) → human review →
  species-gated HITL instrument. `arrangement_disorder` measure still AMBER
  (conflates texture with layout) — improved version in parallel.

### B. Materials encyclopedia  *(new, seeded)*
Physical properties × human impacts, doubly indexed (per-material entries +
per-mediating-property index). Seeded at `docs/materials_encyclopedia/` with
README, MEDIATORS (10-property index), and four graded entries (wood, concrete,
acoustic textile, glass).
- **Open:** elaborate via the materials × mediators × impact matrix — one evidence
  query per cell → graded claim → citation. RAG tools do the heavy lifting here
  (see "Tooling" below). Then wire material recognition into the tagger so it can
  *propose* a material register from an image (firm labels only where recognition
  is reliable; abstain otherwise).

### C. Social presence / occupancy  *(new topic, answer below)*
The effect of a space is modulated by **who else is in it**. This is a real and
sizeable literature, and it changes the tagger's job: the same room "means"
something different empty, at working density, and crowded. Short version of what's
known:
- **Social facilitation / inhibition (Zajonc 1965; Bond & Titus 1983 meta):** the
  mere presence of others reliably raises arousal, which *helps* simple/well-learned
  tasks and *hurts* complex/novel ones. Firm, one of social psychology's most
  replicated effects.
- **Crowding vs density (Stokols 1972; Evans; Epstein 1981):** *density* is people
  per area (physical); *crowding* is the stress experience, which depends on density
  **plus** control, predictability, and meaning. High density → physiological stress,
  worse task performance, and social withdrawal — but only when it reads as crowding.
  Firm.
- **Social buffering of stress (Kikusui; Hostinar & Gunnar):** the *supportive*
  presence of others dampens stress response — the opposite sign to crowding. So
  "other people" is not one variable; it splits into threat/competition-for-resource
  (costs) and support/affiliation (benefits). Framework→firm.
- **Proxemics & personal space (Hall 1966):** effects are distance- and
  culture-scaled; the same headcount in the same room is fine or intolerable
  depending on interpersonal distance and cultural norms. Framework.
- **Territoriality & control (Altman):** perceived control over the space and over
  interaction mediates whether presence is stressful. Framework.
- **What this means for the tagger:** occupancy is a *modulator*, not a fixed
  property of the image. The right move is to make the tagger read **occupancy cues**
  (headcount, density relative to area, personal-distance violation, queue/gathering
  structure) as a register, and to treat every other register's output as
  *conditional on* occupancy. Proposed home: `docs/space_effects/social_presence/`
  as its own graded knowledge base, mirroring the materials encyclopedia's format.

### D. Activity / space-use
What the space is *for* and what's happening in it (working, waiting, dining,
circulating). Conditions everything else — a "cluttered" workshop is not a
"cluttered" waiting room. Later strand; depends on scene/attribute recognition (see
image DBs).

### E. 3D / richer intake
Move beyond single images to RGBD scans, panoramas, and synthetic photoreal
interiors with ground-truth geometry/materials/lighting. Lets isovist/visibility
work (the isovist strand) run on real geometry instead of proxies.

### F. Affect / wellbeing outputs
The output layer that turns registers into graded predictions about stress,
restoration, attention, memory, and neurodiverse sensory load — always with the
evidence grade attached, never a bare score.

### G. Papers / governance / coordination  *(cross-cutting)*
The manuscript(s), the evidence ledger, RULE 0 (no destructive ops on unique data),
one-committer discipline, and the agent-coordination protocol. This is the
connective tissue, not a phase.

---

## Image databases to collect

Direct answer to "what additional image DBs do I need?" Split into **off-the-shelf**
(download, cite, use) and **purpose-built** (we must construct because no public set
isolates the variable our *novel* claims need).

### Off-the-shelf — get these
**Scenes & attributes (feeds A, C, D):**
- **Places365** (MIT) — 1.8M scene images, 365 categories. The scene backbone.
- **ADE20K** — full scene parsing (objects + materials + parts). Gold for
  `surface_density` / `arrangement_disorder` ground truth from segmentation.
- **SUN Attributes** — 102 scene attributes incl. "cluttered," "open area,"
  "natural." Directly relevant human attribute labels.
- **MIT Indoor67 / LSUN rooms** — indoor scene coverage.

**Materials & texture (feeds B):**
- **MINC — Materials in Context** (Bell et al.) — 3M samples, 23 material classes.
  The material-recognition standard.
- **OpenSurfaces** — segmented surfaces with material *and reflectance/gloss* labels
  (maps straight onto MEDIATORS §2).
- **DTD — Describable Textures Dataset** — 47 texture attributes (feeds fractal /
  textural_discomfort measures).
- **FMD / GTOS** — smaller material/terrain sets for cross-checking.

**Aesthetics / affect / preference (feeds F):**
- **AVA** — 250k images with aesthetic ratings + attributes.
- **OASIS** — 900 images, open, with valence/arousal norms (use instead of IAPS,
  which is access-restricted). Anchors the affective-stress channel.

**Occupancy / crowd (feeds C):**
- **ShanghaiTech / JHU-CROWD++ / UCF-QNRF** — crowd-counting sets = density ground
  truth. Use for the occupancy-cue reader, not for meaning.

**3D / geometry (feeds E):**
- **Hypersim** — synthetic photoreal interiors with ground-truth geometry, material,
  lighting. **Matterport3D / ScanNet / Structured3D** — real & synthetic RGBD
  interiors. These make the isovist/visibility work run on real geometry.

### Purpose-built — we must construct these
Our headline claims are about *isolated* variables, and no public set holds one facet
fixed while varying another. These are small, high-value, and the studies fail
without them:
- **Facet-isolation pairs** — same scene, one species varied (surface_density held,
  arrangement varied, etc.). Tests operation-indexed complexity. Build by editing /
  re-staging real interiors.
- **Gestalt-refund pairs** — Mooney-type or occlusion scenes that *resolve* on
  closure vs scenes whose disorder is statistically baked in. Tests the
  transient-vs-enduring stress prediction (the manuscript's sharpest claim).
- **Occupancy series** — the *same* space photographed empty / working-density /
  crowded. Tests strand C. Sourceable from time-lapse/webcam archives or a short
  purpose shoot; almost nothing public holds the space constant while varying people.
- **Neurodiverse-relevant sensory sets** — curated glare / echo / high-variety
  scenes for the sensory-load claims, since generic sets don't tag for this.

Priority order to collect: **ADE20K + SUN Attributes** (unblocks A immediately),
then **MINC + OpenSurfaces** (unblocks B), then build the **facet-isolation and
gestalt-refund pairs** (unblock the manuscript's experiments), then **occupancy
series** (unblocks C). Places365 and the 3D sets are backbone/infrastructure — get
them staged but they're not on any single study's critical path.

---

## Tooling — how the cheap knowledge gets gathered
Literature strands (B, C, F) are RAG-driven. Recommended, in order:
- **PubMed** (free, no auth) — health/cognition mechanisms; enable first.
- **Scite** — evidence grading (supporting vs contrasting citations) — exactly our
  firm/framework/contested need.
- **Elicit** — systematic extraction + reports across a question; best for filling a
  whole matrix row.
- **Consensus / Google Scholar** — quick claim checks and coverage.

None are enabled in this chat yet — David enables them in claude.ai (Connectors),
then cowork drives them. Until then, cowork can draft the exact queries per matrix
cell so no time is lost.

---

## Sequence (who does what, in what order)
This is the orderly path. Full mechanics + artifact contracts in
`docs/validation/coordination/COORDINATION.md`; that file, not this one, is the
handoff channel.

1. **Now — Codex:** corpus replay (540 images → per-species hypotheses + queues),
   emit the Phase-1 artifact contract under `docs/validation/review_pack/`. Sole
   committer; sweeps `git add -- docs/` so cowork's placed files (encyclopedia,
   roadmap) get committed too.
2. **Now — cowork:** elaborate materials encyclopedia (matrix + queries), stand up
   the social-presence knowledge base, finish manuscript cleanup. Places files;
   Codex commits.
3. **Next — cowork:** review-pack viewer over Codex's Phase-1 artifacts.
4. **Then — david/stephan:** human accept/reject → objections.
5. **Then — codex:** science-run integration + platform seam to ccode.
6. **Then — cowork:** species-gated HITL instrument consuming real hypotheses.
7. **Parallel throughout:** collect the off-the-shelf image DBs above; build the
   purpose-built pairs; RAG-fill the encyclopedia as connectors come online.

## Insulation from the AE-pipeline repair
This program touches only `docs/` and the tagger's measure/species code. It does not
depend on the AE pipeline being healthy, so the chaos there does not block us. The
one seam is Phase 5 (platform hand-off to ccode); everything before it is
self-contained.
