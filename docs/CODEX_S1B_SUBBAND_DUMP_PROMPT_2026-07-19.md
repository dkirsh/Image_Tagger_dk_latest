# CODEX TASK S1B — per-subband entropy dump (localize the remaining SE divergence)
### 2026-07-19 · Repo /Users/davidusa/REPOS/Image_Tagger_dk_latest · PYTHONPATH=. · pyrtools already installed
### OUTPUT ARTIFACTS (commit exactly these): `docs/SUBBAND_DUMP_MAC_2026-07-19.json` + `docs/CODEX_S1B_NOTE_2026-07-19.md`

Status: after your adjudication, P2 (sqrt-2 binomial) is FIXED — all FC values now match. SE still
diverges (structured fixtures ~7-19% rel, sandbox HIGHER). To localize which mask is wrong in the
shim, dump the PER-SUBBAND entropy vector and per-subband coefficient statistics from REAL pyrtools
on the deterministic gradient fixture:

```python
# save as /tmp/subband_dump.py ; run: PYTHONPATH=. python3 /tmp/subband_dump.py
import json, sys, numpy as np
sys.path.insert(0, "cnfa_algs/_vendor")
import pyrtools as pt
H, W = 120, 160
grad = np.clip(np.stack([40 + 170*np.mgrid[0:H,0:W][1]/W]*3, -1), 0, 255).astype(np.uint8)
from visual_clutter.clutter import Vlc
clt = Vlc(grad[..., ::-1].copy(), numlevels=3)   # BGR->RGB flip as the harness does
out = {}
for name, ch in [("L", clt.L), ("a", clt.a), ("b", clt.b)]:
    S = pt.pyramids.SteerablePyramidFreq(ch, height=3, order=3).pyr_coeffs
    out[name] = {str(k): {"shape": list(np.asarray(v).shape),
                          "std": float(np.std(v)), "mean": float(np.mean(v)),
                          "entropy": float(clt.band_entropy(np.asarray(v), 3, 4) and 0) or None}
                 for k, v in S.items()}
    # entropies per band via the package's own entropy util:
    from visual_clutter.utils import entropy
    for k, v in S.items():
        out[name][str(k)]["entropy"] = float(entropy(np.asarray(v).ravel()))
json.dump(out, open("docs/SUBBAND_DUMP_MAC_2026-07-19.json", "w"), indent=1, sort_keys=True)
print("wrote docs/SUBBAND_DUMP_MAC_2026-07-19.json")
```

Then: also report (in the note doc) pyrtools' EXACT source expressions for (a) the level loop's
himask/lomask pointOp arguments INCLUDING when log_rad is incremented relative to each lookup,
(b) whether Xrcos shifts before or after the bands at each level, (c) the hi0/lo0 stage twidth.
Quote the few relevant lines (MIT license). Commit ONLY the two artifacts. No push.
