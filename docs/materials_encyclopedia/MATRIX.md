# Materials Matrix — the working spine

*The grid the encyclopedia fills in. Two matrices (physical properties, then human
impacts) over an expanded material set, plus a per-cell RAG fill queue. Rows here
that lack an `entries/<name>.md` file are stubs to be written; the four with entries
are marked ✓. Last updated 2026-07-31 by cowork. Lives at
`docs/materials_encyclopedia/MATRIX.md`.*

Legend: **H/M/L** = high/medium/low · **↑/↓** = raises/lowers the impact ·
**~** = neutral or mixed · **—** = no strong pathway · grades: **[F]** firm ·
**[K]** framework · **[C]** contested. Mediator numbers (§1–§10) are the
`MEDIATORS.md` index.

---

## Matrix 1 — Materials × physical properties (the mediator profile)
This is mostly materials science, so it can be filled with confidence; the human
impacts (Matrix 2) hang off these columns.

| material | §1 acoustic abs. | §2 gloss/reflect. | §3 fractal D | §4 warm–cold (effusivity) | §5 hard/rough | §6 VOC | §7 natural gestalt |
|---|---|---|---|---|---|---|---|
| Wood, solid ✓ | L–M | matte–satin | **mid (preferred)** | warm | mod | low | **strong** |
| Engineered wood / composite | L–M | matte–satin | mid | warm | mod | **H (formaldehyde)** | moderate |
| Concrete ✓ | **very L (reflective)** | matte, mid–low | low | **cold** | very hard | very low | weak |
| Brick / fired clay | L (reflective) | matte | mid (coursing/texture) | cool–neutral | hard, rough | very low | moderate |
| Natural stone (marble/granite) | very L | **often high gloss** | low–mid (veining) | **cold** | very hard | very low | moderate |
| Glass / glazing ✓ | very L | **specular (glare)** | ~0 | cold | very hard, smooth | low (coatings vary) | absent |
| Metal (steel/alu) | very L | **high/specular** | ~0 | **cold** | very hard | low | absent |
| Ceramic tile | very L | glossy–matte | low | cold | very hard | low | weak |
| Gypsum plaster / painted drywall | L | matte | low | neutral | mod, smooth | **paint-dependent** | weak |
| Acoustic textile / carpet / drape ✓ | **H (absorptive)** | matte, diffuse | soft mid | warm | soft | **variable** | moderate (wool/felt) |
| Cork | **M–H** | matte | mid | warm | soft | low | moderate–strong |
| Plastic laminate / vinyl | L | often glossy | low | neutral–warm | mod, smooth | **variable (phthalates)** | absent |
| Leather | L–M | matte–satin | mid (grain) | warm | soft | low–mod | moderate |
| Living plants / greenery | M (foliage scatters) | matte | **high, natural** | — | soft | low (improves air) | **strongest** |

Notes: §8 sensory-load is a *composite* of §1+§2+§5 (low load = absorptive + matte +
soft-predictable), read off this table, not a separate column. §9 semantic and §10
degradation are context/culture-bound and live in each entry's prose, not the grid.

---

## Matrix 2 — Materials × human impacts (direction + evidence grade)
The payload. Cells give the dominant direction and the grade; the *pathway* is the
mediator that produces it (cross-ref Matrix 1 / `MEDIATORS.md`). Empty-ish rows are
where the encyclopedia most needs RAG (see queue below).

| material | speech/comms (§1) | attn & memory (§1) | cog load / perf (§1,§6) | stress / restoration (§3,§7) | affect / mood (§4,§7,§9) | neurodiverse load (§8) | health (§6) | preference (§9) |
|---|---|---|---|---|---|---|---|---|
| Wood, solid ✓ | ~ | ~ | ~ **[C]** (perf mixed) | **↓ arousal [K→F]** | ↑ warmth **[K→F]** | ↓ load **[K]** | good if low-VOC **[F]** | high **[K]** |
| Engineered wood | ~ | ~ | **↓ if off-gassing [F]** | ↓ (looks like wood) [K] | ↑ [K] | ↓ [K] | **risk: formaldehyde [F]** | high [K] |
| Concrete ✓ | **↓ reverberant [F]** | **↓ [F]** | ↑ effortful listening **[F]** | ~–↓ **[K]** | cool/austere [K] | acoustic risk **[K]** | inert, low-VOC **[F]** | polarising [K] |
| Brick | ↓ (reflective) [F] | ↓ [F] | ↑ if untreated [F] | ~ / mild ↑ (texture) [K] | "warm, traditional" [K] | ~ | inert [F] | generally liked [K] |
| Natural stone | ↓ reverberant [F] | ↓ [F] | ↑ if untreated [F] | ~ (cold touch) [K] | luxury/prestige or cold [K] | glare risk if polished [K] | inert; radon(granite) niche [C] | high (status) [K] |
| Glass ✓ | ↓ large glazed rooms [F] | ↓ [F] | ~ | surface ~–↓; **view↑↑ [F, separate]** | clean/modern or cold [K] | **↑ load (glare) [K]** | watch glare/heat [F] | high (transparency) [K] |
| Metal | ↓ reverberant [F] | ↓ [F] | ↑ if untreated [F] | ~–↓ (cold) [K] | sleek/industrial [K] | glare + cold risk [K] | inert [F] | context-dependent [K] |
| Ceramic tile | ↓ reverberant [F] | ↓ [F] | ↑ if untreated [F] | ~ | clean/hygienic or cold [K] | glare + echo risk [K] | inert, cleanable [F] | ~ [K] |
| Gypsum/paint | ~ (neutral) | ~ | **↓ if high-VOC paint [F]** | ~ | neutral ground [K] | ~ | **paint-VOC dependent [F]** | neutral [K] |
| Acoustic textile ✓ | **↑↑ [F]** | **↑ (children) [F]** | **↑ (less speech intrusion) [F]** | ↓ (quiet/soft/warm) [K] | ↑ comfort/quiet [K] | **↓↓ core autism move [K]** | good if low-VOC; carpet allergen [F/mixed] | warm but "institutional" [K] |
| Cork | **↑ (absorptive) [F]** | ↑ [F] | ↑ [F] | ↓ (warm, natural) [K] | warm, tactile [K] | ↓ load [K] | low-VOC, renewable [F] | liked, "eco" [K] |
| Plastic laminate | ~ | ~ | ~ / ↓ if off-gassing [C] | ~ | "cheap" or "clean" [K] | glare if glossy [K] | **phthalate/VOC watch [K]** | low ("fake") [K] |
| Leather | L–M abs [K] | ~ | ~ | ↓ (warm, tactile) [K] | luxury, comfort [K] | ↓ load (matte, soft) [K] | tanning-chem watch [C] | high (quality) [K] |
| Living plants | M abs [K] | **↑ attention restoration [K→F]** | ↑ (ART) **[K→F]** | **↓↓ strongest restoration [F]** | ↑↑ mood [F] | ~ / calming [K] | **↑ air quality [K]** | very high [F] |

Reading it: the **firmest column is acoustic (§1)** — absorptive materials help
cognition, reflective ones hurt it, and that flips the sign of concrete/stone/glass/
metal vs textile/cork. The **biggest health lever is §6 VOC** (engineered wood,
paint, some plastics). **Plants** and **acoustic textile** are the two clearest
net-positives; **glass** needs the surface (costs) kept separate from the view
(large benefit).

---

## RAG fill queue — the thin cells, with the query ready
One row per cell that is a stub, weak, or grade-worthy-of-upgrade. When connectors
are on, run the query, extract, grade, and drop the citation into the entry + update
the grade here. Ordered by value.

1. **Plants → cognition/attention (upgrade [K→F]?).** Elicit report: *"Does indoor
   vegetation / green walls improve attention, memory, and task performance? RCTs and
   field studies, effect sizes."* Scite claim: *"indoor plants improve cognitive
   performance."*
2. **Wood → cognitive performance (resolve [C]).** Elicit: *"Effect of visual wood
   surfaces in interiors on cognitive performance vs autonomic/affective outcomes —
   which is supported?"* This is the cell wood marketing overreaches on; pin it.
3. **Cork (new entry).** Consensus: *"Does cork flooring/wall improve room acoustics
   and comfort?"* + PubMed for any health/IAQ. Write `entries/cork.md`.
4. **Natural stone (new entry) + polished-stone glare.** Scite: *"polished stone /
   glossy floors and discomfort glare."* PubMed: *"granite radon indoor"* (grade the
   niche health claim honestly — likely [C]).
5. **Brick, metal, ceramic tile (new entries).** Mostly inherit acoustic §1 [F] and
   §2 gloss — cheap to write from the mediator index; RAG only the semantic/preference
   cell (§9) per material.
6. **Engineered wood VOC (quantify [F]).** PubMed: *"formaldehyde emission engineered
   wood cognition / respiratory."* Tighten the direction and threshold.
7. **Plastic laminate / vinyl health (resolve [C]).** PubMed/Scite: *"phthalate
   emissions vinyl flooring health children."*
8. **Leather (new entry, thin).** Consensus for affect/preference; PubMed for
   tanning-chemical exposure — grade [C] unless evidence is firmer than expected.
9. **§10 degradation → prosociality/aggression (keep [C], find the ceiling).** Scite:
   *"broken windows theory material disorder — replications and failures."* Do not
   upgrade past contested without strong support.

New materials get an `entries/<name>.md` on the schema in `README.md §Entry schema`,
pointing every claim at a `MEDIATORS.md` §. If a new mediating property appears, add
it to `MEDIATORS.md` first, then reference it here.
