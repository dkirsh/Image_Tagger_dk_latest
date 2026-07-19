# CNfA OPERATOR SPEC — street-noise intrusion + masking-privacy field (C7-ext / C-STREET)
### Image_Tagger / CNfA · 2026-07-19 (Cowork) · DRAFT for Codex to attack · **Tier: AMBER (declared-input, parametric)**

*Written in the C01/C29 spec style so it enters the construction table and Codex can attack it. Grounds
every number in a sandbox prototype run (`street_noise_prototype.py`, 2026-07-19) that is NOT in the repo
code tree — this doc is the contract; the prototype is the evidence, delivered separately to David.*

---

## 0. Absolute-path manifest (all verified this session unless marked)
- Spec (this doc, to be committed): `/Users/davidusa/REPOS/Image_Tagger_dk_latest/docs/STREET_NOISE_ACOUSTIC_OPERATOR_SPEC_2026-07-19.md`
- Reuses (existing, verified): `/home/claude/cnfa_algs/acoustics_plan.py` (sandbox mirror of the repo module `cnfa_algs/acoustics_plan.py`) — `sti_from_snr`, `speech_level`, `D2S_DEFAULT=7.0`, `L_SPEECH_1M_DEFAULT=57.4`, `chronic_stress_soundscape` (C20), `sti_field` (C7), `focus_zone_privacy` (C7).
- Prototype evidence (sandbox-only, delivered to David, **NOT** committed to the repo): `/home/claude/committee/street_noise_prototype.py`
- Feeds/adjacent operators: C7 focus-zone privacy, C8 ISO 3382-3 single numbers, C20 chronic soundscape, and the compound C04 huddle_shelter_viability.

---

## 1. What the operator is, in one paragraph
Given (a) a plan/region geometry with a **street facade** and its apertures, and (b) two **declared inputs** —
the outdoor free-field level `Leq_out` (dB(A)) at the facade and the facade sound-reduction index `R'`
(dB) per facade segment — the operator produces two spatial fields over the interior: **`noise_spl_field`**,
the intruding street-noise SPL per cell (which zones are loud vs quiet), and **`huddle_suitability`**, the
cost/resource duality — street noise is a *cost* for focus but a *resource* that masks a confidential
conversation from a nearby eavesdropper, bounded above because too much noise makes the pair themselves
strain. It is the spatial-noise sibling of the existing C7 speech-privacy pack: C7 asks "can a bystander
follow a talker's speech?"; this asks "does the *street* raise the floor enough to mask that speech —
and where is it still comfortable?" It reuses the identical ISO 3382-3 `sti_from_snr` law.

## 2. Why it is worth building (construct link)
Street/traffic noise intruding through a facade is a documented environmental stressor (chronic arousal,
cortisol — the C20 construct) AND, in the huddle reading, a *masking resource*: raising the ambient floor
lowers eavesdropper STI (the ISO 3382-3 privacy mechanism, run in reverse). The novel, defensible claim is
the **inverted-U**: confidential-conversation suitability peaks at *moderate* intrusion — enough to mask,
not so much the pair strain. This gives design a spatial answer to "where do I put the quiet-focus seats vs
the discreet-huddle nook relative to the noisy facade?" — which the current operators do not answer because
they take ambient noise as a single scalar, not a facade-driven field.

## 3. Inputs / outputs (the socket contract)
**Declared inputs (ABSTAIN if absent — never fabricated):**
- `Leq_out` dB(A): outdoor free-field level at the facade (design value or measurement). No default that
  masquerades as data; if unknown the operator returns ABSTAINED naming `Leq_out`.
- `R'` dB per facade segment: facade sound-reduction index (EN 12354-3 / glazing spec / open-aperture ~6–12 dB).
- Geometry: facade row + aperture columns + interior WALL/FREE grid + absorption map `alpha` (reuse the
  PlanGrid the C7/C20 operators already consume).
**Outputs (`AttributeResult`):**
- `field["noise_spl_field"]`: dB(A) per FREE cell.
- `field["huddle_suitability"]`: 0..1 per FREE cell = `privacy * within_pair_ok`.
- `scalar`: a headline — e.g. fraction of floor area below a focus-comfort threshold (≤45 dB(A)), OR the
  best attainable `huddle_suitability`. (Choose one at build; do not emit both as "the" scalar.)
- `extras`: `L_rev_dBA`, `noise_min/max`, `best_huddle_cell`, `quietest_cell`, declared `Leq_out`, `R'` map,
  and every constant below (so replay is exact).
- `method`: `"parametric facade-transmission energy model (EN12354-3 R' + Sabine diffuse floor + Maekawa-ish
  diffraction) x ISO 3382-3 STI masking — DESIGN-TIME ZONING, not measured SPL"`.

## 4. The algorithm (pure, deterministic — as prototyped)
1. Per facade cell `c`: transmitted interior-face level `L_facade[c] = Leq_out - R'[c]`.
2. **Reverberant (Sabine diffuse) floor** — one global level:
   `W_in = Σ_c 10^(L_facade[c]/10) * cell_area` (cell AREA folded in — omitting it inflates the floor ~20 dB,
   the v1 prototype bug), `L_W = 10log10(W_in)`, `A = Σ alpha*cell_area`, `R_room = A/(1-amean)`,
   `L_rev = L_W + 10log10(4/R_room)`.
3. **Direct field** — each facade patch a hemispherical point source anchored to `L_facade[c]` at `d0=0.5 m`,
   `L_dir(d) = L_facade[c] - 20log10(d/d0)`, minus `diffraction_db` (default 12) when a WALL blocks LOS
   (supercover LOS, same as `cnfa_algs/los.py`). Energy-sum all patches + the reverberant floor →
   `noise[r,c] = 10log10(Σ 10^(lvl/10) + 10^(L_rev/10))`.
4. **Privacy (masking)**: eavesdropper at `R_EAVES=2.5 m` hears `speech_at_eaves = L_SPEECH_1M - D2S*log2(R_EAVES)`
   (~48 dB(A)); `snr = speech_at_eaves - noise`; `privacy = 1 - sti_from_snr(snr)` (the SAME law as C7).
5. **Within-pair comfort**: `within_ok = clip(1 - max(0, noise - COMFORT_MAX)/15, 0, 1)`, `COMFORT_MAX=50`.
6. `huddle_suitability = privacy * within_ok` (the inverted-U).

**Constants (all declared, all replay-critical):** `L_SPEECH_1M=57.4`, `D2S=7.0`, `R_EAVES_M=2.5`,
`COMFORT_MAX_DBA=50.0`, `D0_M=0.5`, `diffraction_db=12.0`. These become boundary-tested thresholds (§7).

## 5. Prototype run evidence (2026-07-19, synthetic 10×15 m foyer, `Leq_out=68`, glazing `R'=33`, 1 m door `R'=12`)
- Reverberant floor `L_rev = 42.8 dB(A)`; noise range `42.9 .. 62.1 dB(A)` — realistic quiet-foyer floor,
  loud at the door, as expected.
- **Duality confirmed:** quietest cell `42.9 dB(A)` → best for FOCUS but privacy only `0.33` (no masking);
  best-huddle cell at `50.0 dB(A)` → `huddle=0.56` (moderate noise masks the eavesdropper without killing
  within-pair hearing); the open door at `61.9 dB(A)` → privacy `0.96` but `huddle=0.20` (too loud for the pair).
  This is the inverted-U, spatially resolved.
- **Determinism:** `max|Δ|` across two runs `= 0.00e+00`.

## 6. Honest limitations (why this is AMBER, not GREEN)
- **Declared-input operator:** consumes `Leq_out` and `R'`; those are design values/measurements, not read
  from the image. By tiering rule 3 (needs-declared-input) and rule "rides parametric geometry", ceiling is AMBER.
- **Single global Sabine floor:** local absorption (the alcove `alpha=0.75`) raises total `A` and lowers the
  floor *for everyone*; it does NOT create a *local* quiet pocket in this diffuse model — in the run the
  absorptive alcove and the behind-screen cell both read `43.0 dB(A)` (the floor), their quiet coming from
  LOS-blocked *direct* field + distance, not local reverberant suppression. A per-zone reverberant model or
  a measured-RIR tier (pyroomacoustics, see `adapters/acoustics_sim.py`) is the GREEN-path upgrade.
- **Parametric, not measured:** Maekawa diffraction is a single flat penalty, no reflection/flanking paths,
  no spectrum (A-weighted broadband only). Same scope caveat as the C7/C8 pack it extends.
- **Construct validity of the inverted-U is asserted, not yet calibrated:** `COMFORT_MAX=50` and the `/15`
  slope need the labeled corpus (§ testing) before any GREEN claim.

## 7. Tests required before it loses the AMBER/NEEDS-VERIFICATION mark (the §1 recipe)
- **Pure-core / determinism:** field recompute `max|Δ|==0` (shown ×2; require ×3 in the suite).
- **Ordering invariants (synthetic):** raising `Leq_out` monotonically raises every cell's noise; raising `R'`
  lowers it; a barrier column strictly lowers noise behind it (LOS penalty); the best-`huddle` cell's noise
  lies strictly between the quietest cell's noise and the door's noise (the inverted-U, as a test).
- **Negative control:** call with `Leq_out=None`/`R'=None` → MUST return ABSTAINED naming the missing input,
  never a number. A fabricated all-equal facade with a claimed barrier must NOT show a shielded zone.
- **Boundary tests:** `COMFORT_MAX_DBA`, `D0_M`, `diffraction_db`, `R_EAVES_M` each locked like `test_f7_ridge_boundary.py`.
- **M1 / M1′:** emit + replay the sufficient statistics — `L_rev`, the facade `L_facade[]` vector, and the
  `(quietest, best_huddle, door)` triple — and re-derive them independently in `verify.py` (keyed by audit_class).
- **Cross-environment:** Mac↔sandbox exact replay of `L_rev` and both fields.
- **Construct (blocked on corpus):** against interiors with known street exposure + labeled focus/huddle zones.

## 8. Where it plugs in
- **Consumes** the same PlanGrid + `los` supercover + `sti_from_snr` as C7/C8/C20 (~80% reuse of `acoustics_plan.py`).
- **Feeds** C04 huddle_shelter_viability (adds the acoustic-masking dimension to visual shelter), and augments
  C7 (street floor as the `L_noise` term instead of a flat scalar) and C20 (facade as a chronic source).
- **Never** summed into the hedonic aggregate directly (compound double-count rule); emits its own field.

## 9. Definition of done
Unit + M1 + M1′ + negative + boundary tests pass (run); `run_stage` SCORED-or-ABSTAINED + traceable on ≥5
plans with declared inputs; determinism ×3; Mac↔sandbox exact replay; survives one external adversarial
attack (Codex). Only then does it lose NEEDS-FINAL-VERIFICATION; it stays AMBER until the labeled-corpus
construct check for the inverted-U is done.
