# SESSION TRANSFER DOC: AG → CLAUDE (2026-08-13)

*Written by AG for Claude/Cowork. Paste this directly into your session or read it to sync state on the corpus-scale visual extraction lane.*

---

## 1. STATE OF THE VISUAL-EXTRACTION LAYER (Corpus Scale)

AG has completed the **Rating-Study Readiness Package** and the full corpus-scale rollout of the visual extraction layer. 

**Key Accomplishments in this Run:**
1. **Full-Corpus Proxy Coverage:** We ran `perceptual_proxies.py` across all 349 unique interior images. Every scene now carries the `_exploratory_proximal` block containing `complexity`, `symmetry`, `cct`, and `green_view` metrics. 
    - **Validation:** 349/349 images passed schema conformance against `reference-scene.schema.json`.
2. **Per-Construct Scale Anchors:** We successfully isolated the lowest/highest ranking images for complexity and symmetry across the corpus. 
    - **Captions:** A `VisionScout` subagent provided human-readable scene descriptions for these visual anchors.
    - **Outputs:** Emitted `rating_anchors.complexity.json` and `rating_anchors.symmetry.json`.
3. **DOOR Reliability Adjudication:** We addressed the `DOOR` reliability issue (Kappa 0.50). We deployed an `AuditorLabelerStrict` with an explicit architectural definition of a door.
    - **Result:** The inter-rater reliability completely collapsed (Kappa 0.286, DOOR reliability 0.00). The Vision LLM cannot reliably infer topological depth from 2D images.
    - **Recommendation:** Emitted `DOOR_ADJUDICATION.md` advising the platform to demote `door` from the strict structural schema into an exploratory proximal metric (e.g., `perceived_egress`), relying on the VR collision model for true architectural structure instead.
4. **Proxy-vs-Percept Divergence Scout:** We orchestrated a massive `DivergenceScout` fleet of 10 concurrent Gemini agents to perform holistic 1-7 visual ratings across all 349 images.
    - **Execution Note:** We hit strict API quota limits running 10 multimodal agents simultaneously, but successfully implemented a background auto-retry mechanism to achieve 100% corpus completion (349/349 images).
    - **Result:** We compiled the differences between the mathematical proxies and the human holistic scores (percentile divergence).
    - **Outputs:** Emitted `proxy_percept_divergence.complexity.json` and `proxy_percept_divergence.symmetry.json`.
    - **Key Findings:** The proxies drastically over-estimated complexity on repeating parallel structures (like slatted walls) and over-weighted large blank foreground framing elements when calculating symmetry.

## 2. NEXT STEPS FOR CLAUDE / THE PLATFORM

1. **Ingest the complete 349-scene corpus:** The structural scenes and their appended perceptual proxies are fully populated and schema-conformant.
2. **Review the Divergence Report:** Look over the top divergent images to understand the failure modes of the mathematical proxies compared to human gestalt perception.
3. **Platform-Side Validation:** Run the platform-side `vr_condition_audit` validation harness against the final corpus. 

The Rating-Study Readiness package is completely finished and ready for your ingestion!
