#!/usr/bin/env python3
"""run_loop_compare.py — T1.2: the render↔verdict comparator (photo→VR production loop).

Contract: render-verdict/v0.6. Contract owner: Tanishq.

PROCESS RULE (adopted after round 3 was invalidated by a mid-review edit): the review
subject is a COMMITTED HASH. This file is committed to tanishq/loop-comparator BEFORE any
Codex round runs; the round's verdict binds to that hash; any fix is a NEW commit and a
NEW round. A commit is a record, not a promotion.

Review lineage (checker ≠ author, different lineage = Codex/gpt-5.5):
  v0.1 BROKEN (round 1, artifact ae160481): A1 same-kind permutation false agreement;
       A2 invented apertures unscored; malformed-input tracebacks; wall-rule divergences.
  v0.2 BROKEN (round 2, artifact d50d9fb1): moved object reported agreement (moved:[]
       declared-but-unscored since v0.1); NaN accepted into "canonical" JSON; manifest
       types untyped-checked; lax ap<i> spelling labelled "exact". Round 2 also CONFIRMED
       both v0.1 false agreements dead, all five mirror divergences closed, and the
       narrow fallback guarantee holding everywhere tested.
  v0.3 answered round 2, but was amended mid-round-3 (vacuous modes + producer entry
       point) — a freeze violation, owned in the v0.4 announcement. Round 3 (artifact
       ad6c8037) returned BROKEN against the pre-amendment bytes; two findings survive
       the amendment and are fixed here.
  v0.4 = v0.3 + vacuous modes + round-3 fixes; the first version reviewed as a
       committed hash (60d938df). Round 4 (artifact 95c071af) returned BROKEN with three
       strict false agreements — the protocol held (worktree unchanged, zero drift).
  v0.5 = v0.4 + round-4 fixes + the null policy. Round 5 (the second hash-pinned
       round, against cc21164d) returned BROKEN on two claim-vs-code findings — for the
       first time, NO false agreement was reachable; the code's claims about itself were
       the defect. F1 (marker collision) was examined and did NOT reproduce.
  v0.6 (this file) = v0.5 + round-5 fixes; claims now match code by construction.

Lane: Image_Tagger_dk_latest (tanishq). Never imports New_VR_Platform code.

METHOD BLOCK (Method Card v0.1)
- FREEZE: mirrors from New_VR_Platform @ 3fe1d505 — _center_x (reconstruct.py:64-69),
  _wall_for (:72-73), bad_center refusal (:136-137), _STRUCTURAL_KINDS (:38-39),
  aperture ids "ap<i>" = source opening index (:148); furniture identity: id = source
  object id and _source_bbox = the image bbox placement derived from
  (place_furniture.py:115-120).
- CLAIM: the verdict re-runs byte-identically; reports every opening whose rendered wall
  or kind differs from the target; reports every matched object whose placement source
  differs from the target's bbox; scores invented apertures; and NEVER claims agreement
  where identity or position could not be verified (strict default).
- REFUTATION: a wrong render (wall, kind, permutation, invented aperture, or moved
  object) that yields BELOW_THRESHOLD under strict mode; a malformed input that
  tracebacks instead of exiting 2; a verdict.json a strict RFC 8259 parser rejects; or
  two runs differing byte-wise.
- NEGATIVE CONTROLS (tests): moved-chair fixture MUST produce a moved entry and never
  agree; iter:NaN MUST be refused, not serialized; ap00 MUST NOT be labelled exact.
- STATED BOUNDS: (a) fixtures synthetic — one real photo run outstanding
  (passes_on_synthetic_only); (b) x_m/y_m consistency with _source_bbox is NOT verified
  here — that is platform placement math, verified by the platform's own tests, not
  re-implemented across the seam; (c) the discrepancy score is EXPLORATORY and
  uncalibrated — never evidence.
- DESIGN DECISION FOR DAVID (flagged, default chosen): strict mode (default) refuses
  BELOW_THRESHOLD whenever identity or position went unverified — an id-less packet can
  therefore never "agree" even with one opening per kind. --allow-unverified-agreement
  relaxes this for stub/foreign producers. Recommended default: strict, since the real
  producer (the platform) always emits ids and _source_bbox.

v0.2 -> v0.3 (round-2 findings answered):
  R2-1 moved objects: matched by source object id; _source_bbox compared to the target's
       object_bbox (epsilon 1e-6); mismatch -> moved entry {object_id, bbox_target,
       bbox_render_source, offset_norm} + object_moved_frac component. A matched pair
       whose position CANNOT be checked (missing _source_bbox while the target claims a
       bbox) lands in position_unverified and blocks agreement (strict).
  R2-2 NaN: canonical() uses allow_nan=False; any non-finite number anywhere in the
       verdict is a refusal, not a malformed artifact.
  R2-3 manifest typing: run_id/target_image_id must be strings, iter a non-bool finite
       int, produced_utc a string when present.
  R2-4 ap<i> spelling: ^ap(0|[1-9][0-9]*)$ — ap00/ap01 are NOT the platform's spelling
       and fall to multiset_fallback rather than wearing the "exact" label.
  R2-5 (label nicety, accepted): gapped/out-of-range ids remain "exact" — round 2 itself
       established gaps are legitimate (non-structural kinds keep their indices); extras
       are flagged and scored, which is the load-bearing part.

v0.3 -> v0.4 (round-3 findings + the amendment, versioned properly):
  AMEND vacuous: identity.mode and objects_mode are tri-state exact | multiset_fallback |
       vacuous — "nothing claimed on that axis by either side", allowed to agree, never
       dressed as "exact". Producer switched to place_furniture (photo_to_vr never places
       furniture, so requirement (3) was structurally unmeetable before).
  R3-1 target-side bbox symmetry: a target object_bbox that is PRESENT but malformed
       (wrong length, non-finite, non-numeric) or MIS-KEYED (bbox_xywh on an object) is a
       claim that cannot be read -> position_unverified, blocking strict agreement —
       exactly as the render side already behaved. Only a genuinely ABSENT claim is
       "nothing owed".
  R3-2 type-strict identity: target object id/category must be non-empty strings (the
       scene schema requires it) -> otherwise REFUSED, fail-closed; render furniture ids
       must be strings -> otherwise multiset_fallback. No str() coercion anywhere in
       identity: 7 never matches "7", and null never matches null.

v0.4 -> v0.5 (round-4 findings, artifact 95c071af @ commit 60d938df):
  V04-1 null bbox: v0.4 tested "is the value absent" instead of "is the key present", so
       object_bbox: null collapsed to "no claim" and agreed unchecked. Fixed as Codex
       prescribed — a KEY-PRESENCE test ends the shape-enumeration arms race: if either
       bbox key is present, whatever its value, the claim must be readable or it lands in
       position_unverified.
  NULL POLICY (the judgement call, decided once, David may override): a present JSON null
       is NEVER "absent". On a leaf claim (object_bbox) it is an unreadable claim ->
       position_unverified. On a container (target openings/objects, room
       apertures/furniture) it is a malformed document -> REFUSED exit 2. Only a MISSING
       KEY is absent. This also closes the objects:null -> vacuous boundary Codex flagged.
  V04-2 category coercion: str() removed from BOTH render category paths (exact-branch
       compare and fallback multiset) and from the openings kind/wall compares — the
       "no coercion" claim now matches the code. A non-string render category can never
       match; it is reported as a typed marker <unreadable-category:T> (markers are
       display-only: they are never entered into the match multiset, so a target category
       that happens to equal a marker string still cannot false-match).
  V04-3 ap<i> anchor: ^...$ with re.match accepts a trailing newline (Python $ matches
       before \\n). Anchored with \\Z; "ap0\\n" now falls to multiset_fallback.
  V04-4 (consistency): iter must be >= 0, matching render-packet.schema.json's minimum —
       the comparator no longer consumes a packet its own schema calls invalid.

v0.5 -> v0.6 (round-5 findings against cc21164d):
  F2 claim-vs-code: v0.5's openings fallback fed _disp() markers straight into the `have`
       MATCHING multiset while _disp's docstring said "never used for matching" — the
       V04-2 disease (claim broader than code) recurring one layer up. No false agreement
       was reachable (a marker can never equal a STRUCTURAL_KINDS kind or a wall_for()
       wall — verified by both lineages), but the claim is now true BY CONSTRUCTION: an
       aperture whose kind or wall is not a usable string never enters any matching
       structure; it is reported among the extras as an unreadable claim.
  F3 RFC 8259 on INPUT: python's json.loads accepts NaN/Infinity/-Infinity, so the
       "strict RFC 8259" claim held only for output. All three input documents (target
       scene, room.json, packet.json) are now parsed with a parse_constant refusal —
       a non-finite constant is refused exit 2 at the door. Stated bound: overflow
       spellings (1e999 -> inf) parse as ordinary numbers past any JSON parser; the
       _finite value checks remain the second line of defence and catch them.
  F1 examined, no change: a GENERATED marker cannot collide with a LITERAL one
       (target="<unreadable-category:int>" vs render category 7 -> CONTINUE, matched=[]);
       both sides literally claiming the same string is correct agreement. Regression
       test added so the property stays pinned.
  Hygiene: docstring escapes doubled; compiles clean with invalid-escape warnings
       promoted to errors (the v0.5 SyntaxWarning at import is gone).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

CONTRACT_VERSION = "render-verdict/v0.6"
_EPS = 1e-6

STRUCTURAL_KINDS = frozenset({"window", "door", "glazed_wall", "glass_partition",
                              "skylight", "clerestory", "opening_unclassified"})
_ZONE_CX = {"left": 0.17, "center": 0.5, "right": 0.83}
_AP_ID = re.compile(r"^ap(0|[1-9][0-9]*)\Z")    # \Z not $: $ matches before a trailing
                                                # newline (round-4 V04-3)


class Refused(Exception):
    """Fail-closed refusal: malformed or unproven input is refused, never guessed at."""


def _strict_loads(s: str, what: str):
    """RFC 8259-strict input parsing (round-5 F3): python's json.loads accepts
    NaN/Infinity/-Infinity; we refuse them at the door. Overflow spellings (1e999)
    parse as numbers in any JSON parser — the _finite value checks catch those."""
    def _no_const(name: str):
        raise Refused(f"{what}: non-finite JSON constant {name} refused (RFC 8259)")
    return json.loads(s, parse_constant=_no_const)


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _finite(x) -> bool:
    return _num(x) and x == x and x not in (float("inf"), float("-inf"))


def center_x(op: Dict) -> float:
    bb = op.get("bbox_xywh")
    if isinstance(bb, Sequence) and not isinstance(bb, (str, bytes)) and len(bb) == 4 \
            and _num(bb[0]) and _num(bb[2]):
        return float(bb[0])
    zone = op.get("zone")
    if zone:
        return _ZONE_CX.get(str(zone).split("_")[0], 0.5)
    return 0.5


def wall_for(cx: float) -> str:
    return "west" if cx < 0.34 else "east" if cx > 0.66 else "north"


def canonical(obj) -> str:
    """Canonical JSON, RFC 8259-strict: sorted keys, minimal separators, trailing LF,
    and NO NaN/Infinity — a non-finite number raises (converted to Refused upstream)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False) + "\n"


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


# ---------------------------------------------------------------- ingestion (fail-closed)

def load_packet(packet_dir: Path) -> Dict:
    pj = packet_dir / "packet.json"
    if not pj.exists():
        raise Refused(f"packet.json missing in {packet_dir}")
    try:
        manifest = _strict_loads(pj.read_text(encoding="utf-8"), "packet.json")
    except ValueError as e:
        raise Refused(f"packet.json unparseable: {e}")
    if not isinstance(manifest, dict):
        raise Refused("packet.json must be a JSON object")

    cv = manifest.get("contract_version")
    if cv != CONTRACT_VERSION:
        raise Refused(f"contract_version {cv!r} != {CONTRACT_VERSION!r} — refusing rather "
                      f"than guessing (breaking changes are announced, not absorbed)")
    # R2-3: type-validate the manifest against its own schema, not just key presence
    for k in ("run_id", "target_image_id"):
        if not isinstance(manifest.get(k), str) or not manifest.get(k):
            raise Refused(f"packet.json {k} must be a non-empty string")
    it = manifest.get("iter")
    if isinstance(it, bool) or not isinstance(it, int):
        if not (_finite(it) and float(it).is_integer()):
            raise Refused("packet.json iter must be a finite integer")
    if it < 0:
        raise Refused("packet.json iter must be >= 0 "
                      "(render-packet.schema.json minimum — round-4 V04-4)")
    pu = manifest.get("produced_utc")
    if not isinstance(pu, str) or not pu:
        raise Refused("packet.json produced_utc must be a non-empty string "
                      "(required by render-packet.schema.json)")
    shas = manifest.get("sha256")
    if not isinstance(shas, dict):
        raise Refused("packet.json sha256 must be an object of name->hex digest")

    contents: Dict[str, bytes] = {}
    for fname, key in (("render.png", "render_png"), ("room.json", "room_json"),
                       ("camera.json", "camera_json")):
        p = packet_dir / fname
        if not p.exists():
            raise Refused(f"{fname} missing from packet")
        b = p.read_bytes()
        claimed = shas.get(key)
        if not isinstance(claimed, str) or claimed != sha256_bytes(b):
            raise Refused(f"sha256 mismatch for {fname}: manifest={claimed!r} "
                          f"actual={sha256_bytes(b)} — packet integrity failed")
        contents[fname] = b

    try:
        room = _strict_loads(contents["room.json"].decode("utf-8"), "room.json")
    except ValueError as e:
        raise Refused(f"room.json unparseable: {e}")
    if not isinstance(room, dict):
        raise Refused("room.json must be a JSON object")
    for field in ("apertures", "furniture"):
        if field in room and room[field] is None:      # null policy: present null is
            raise Refused(f"room.json {field} is null — a present null is malformed, "
                          f"not absent (omit the key instead)")
        v = room.get(field, [])
        if not isinstance(v, list) or any(not isinstance(x, dict) for x in v):
            raise Refused(f"room.json {field} must be a list of objects")
    return {"manifest": manifest, "room": room}


def load_target(target_path: Path) -> Dict:
    try:
        scene = _strict_loads(target_path.read_text(encoding="utf-8"), "target scene")
    except (OSError, ValueError) as e:
        raise Refused(f"cannot read target scene: {e}")
    if not isinstance(scene, dict):
        raise Refused("target scene must be a JSON object")
    if not (scene.get("openings") or scene.get("objects")):
        raise Refused("target scene has neither openings nor objects — nothing to compare")
    for field in ("openings", "objects"):
        if field in scene and scene[field] is None:    # null policy: present null is
            raise Refused(f"target scene {field} is null — a present null is malformed, "
                          f"not absent (omit the key instead)")
        v = scene.get(field)
        if v is not None and (not isinstance(v, list)
                              or any(not isinstance(o, dict) for o in v)):
            raise Refused(f"target scene {field} must be a list of objects")
    return scene


def expected_openings(scene: Dict) -> List[Dict]:
    out = []
    for i, op in enumerate(scene.get("openings") or []):
        kind = op.get("kind")
        if not (isinstance(kind, str) and kind):
            raise Refused(f"opening {i} needs a non-empty kind (platform bad_kind)")
        if kind not in STRUCTURAL_KINDS:
            continue  # platform reconstruct skips non-structural kinds (:133-134)
        cx = center_x(op)
        if not (0.0 <= cx <= 1.0):
            raise Refused(f"opening {i} centre-x {cx} out of [0,1] (platform bad_center)")
        out.append({"index": i, "kind": kind, "wall": wall_for(cx)})
    return out


# ---------------------------------------------------------------- comparison core

def _multiset(items: List[str]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for it in items:
        out[it] = out.get(it, 0) + 1
    return out


def _disp(v) -> str:
    """Display-only rendering of a value that SHOULD be a string. Never enters ANY
    matching structure — true by construction since v0.6: round-5 F2 caught v0.5
    feeding _disp output into the openings fallback multiset (no false agreement was
    reachable, but the claim was broader than the code — the V04-2 disease again)."""
    return v if (isinstance(v, str) and v) else f"<non-string:{type(v).__name__}>"


def _render_cat(f: Dict):
    """The furniture entry's category if it is a usable string, else None (no str()
    coercion — a non-string category can never match anything)."""
    v = f.get("category", f.get("element"))
    return v if (isinstance(v, str) and v) else None


def _cat_marker(f: Dict) -> str:
    v = f.get("category", f.get("element"))
    return f"<unreadable-category:{type(v).__name__}>"


def _bbox_ok(bb) -> bool:
    return (isinstance(bb, Sequence) and not isinstance(bb, (str, bytes))
            and len(bb) == 4 and all(_finite(v) for v in bb))


def _compare_openings(expected: List[Dict], apertures: List[Dict]):
    if not expected and not apertures:          # nothing claimed: VACUOUS, say so
        return "vacuous", [], [], []
    ids = [(_AP_ID.match(str(a.get("id", ""))), a) for a in apertures]
    exact_mode = all(m is not None for m, _ in ids) if apertures else True
    mismatches: List[Dict] = []
    extra: List[str] = []
    unverifiable_kinds: List[str] = []

    if exact_mode:
        by_index: Dict[int, Dict] = {}
        for m, a in ids:
            idx = int(m.group(1))
            if idx in by_index:
                raise Refused(f"duplicate aperture id ap{idx} — malformed render packet")
            by_index[idx] = a
        expected_idx = {e["index"] for e in expected}
        for e in expected:
            a = by_index.get(e["index"])
            if a is None:
                mismatches.append({"opening_id": f"target_opening_{e['index']}_{e['kind']}",
                                   "expected_wall": e["wall"], "rendered_wall": "MISSING"})
            elif a.get("kind") != e["kind"] or a.get("wall") != e["wall"]:
                # direct comparison, no str(): a non-string kind/wall can only MISmatch
                mismatches.append({"opening_id": f"target_opening_{e['index']}_{e['kind']}",
                                   "expected_wall": e["wall"],
                                   "rendered_wall": _disp(a.get("wall", "unknown")),
                                   "expected_kind": e["kind"],
                                   "rendered_kind": _disp(a.get("kind", "unknown"))})
        extra = sorted(f"ap{i}:{_disp(a.get('kind', 'unknown'))}->"
                       f"{_disp(a.get('wall', 'unknown'))}"
                       for i, a in by_index.items() if i not in expected_idx)
    else:
        want: Dict[str, List[str]] = {}
        for e in expected:
            want.setdefault(e["kind"], []).append(e["wall"])
        have: Dict[str, List[str]] = {}
        unreadable: List[str] = []
        for a in apertures:
            k, w = a.get("kind", "unknown"), a.get("wall", "unknown")
            if isinstance(k, str) and k and isinstance(w, str) and w:
                have.setdefault(k, []).append(w)
            else:
                # F2 (round 5): an aperture whose kind or wall is not a usable string
                # is an unreadable claim — it never enters the matching multiset
                # (_disp's docstring holds by construction now) and is reported extra.
                unreadable.append(f"{_disp(k)}->{_disp(w)}")
        for kind in sorted(want):
            walls = want[kind]
            if len(walls) >= 2:
                unverifiable_kinds.append(kind)
            avail = have.get(kind, [])
            for j, w in enumerate(sorted(walls)):
                if w in avail:
                    avail.remove(w)
                elif avail:
                    mismatches.append({"opening_id": f"target_{kind}_{j}",
                                       "expected_wall": w,
                                       "rendered_wall": sorted(avail)[0]})
                else:
                    mismatches.append({"opening_id": f"target_{kind}_{j}",
                                       "expected_wall": w, "rendered_wall": "MISSING"})
            have[kind] = avail
        extra = sorted([f"{k}->{w}" for k, ws in have.items() for w in ws]
                       + unreadable)
    return ("exact" if exact_mode else "multiset_fallback"), mismatches, extra, \
        sorted(unverifiable_kinds)


def _compare_objects(scene: Dict, room: Dict):
    """Match by SOURCE OBJECT ID (place_furniture echoes it, with _source_bbox =
    the image bbox placement derived from). Position check: _source_bbox vs the target's
    object_bbox. Verifies the room was built from the right source positions; x_m/y_m
    consistency with _source_bbox is platform math, out of this lane (stated bound)."""
    t_objs = scene.get("objects") or []
    r_furn = room.get("furniture") or []
    if not t_objs and not r_furn:      # nothing claimed on either side: VACUOUS, not
        return ("vacuous", [], [], [], [], [], 0)   # "exact" — say so (round-3 amendment)
    moved: List[Dict] = []
    position_unverified: List[str] = []

    for j, o in enumerate(t_objs):        # scene schema: id + category are non-empty strings
        if not (isinstance(o.get("id"), str) and o.get("id")):
            raise Refused(f"target object {j} id must be a non-empty string (scene schema)")
        if not (isinstance(o.get("category"), str) and o.get("category")):
            raise Refused(f"target object {j} category must be a non-empty string (scene schema)")
    t_ids = [o["id"] for o in t_objs]
    r_ids_raw = [f.get("id") for f in r_furn]
    r_ids_ok = all(isinstance(i, str) and i for i in r_ids_raw)
    r_ids = [i for i in r_ids_raw if isinstance(i, str)]
    objects_exact = (bool(t_objs) and len(set(t_ids)) == len(t_ids)
                     and r_ids_ok and len(set(r_ids)) == len(r_ids))

    if objects_exact:
        t_by = {o["id"]: o for o in t_objs}
        r_by = {f["id"]: f for f in r_furn}
        matched = sorted(i for i in t_by if i in r_by)
        missing = [t_by[i]["category"] for i in t_by if i not in r_by]
        extra_o = [_render_cat(r_by[i]) or _cat_marker(r_by[i])
                   for i in r_by if i not in t_by]
        matched_cats = []
        for i in matched:                     # category must also agree on a matched id
            tc = t_by[i]["category"]          # validated non-empty string above
            rc = _render_cat(r_by[i])         # None unless a usable string (V04-2:
            if rc is None or tc != rc:        # no str() — 7 never matches "7")
                missing.append(tc)
                extra_o.append(rc if rc is not None else _cat_marker(r_by[i]))
            else:
                matched_cats.append(tc)
        matched_cats, missing, extra_o = sorted(matched_cats), sorted(missing), sorted(extra_o)
        for i in matched:
            tobj = t_by[i]
            if "object_bbox" not in tobj and "bbox_xywh" not in tobj:
                continue    # V04-1: KEY-PRESENCE test — only a missing key is absent.
            tb, rb = tobj.get("object_bbox"), r_by[i].get("_source_bbox")
            if not _bbox_ok(tb):
                # R3-1/V04-1: a PRESENT claim that cannot be read (null, malformed, or
                # mis-keyed bbox_xywh) — same epistemic state as an unreadable echo
                position_unverified.append(i)
                continue
            if not _bbox_ok(rb):
                position_unverified.append(i)  # claim exists, echo absent -> unverifiable
                continue
            off = max(abs(float(a) - float(b)) for a, b in zip(tb, rb))
            if off > _EPS:
                moved.append({"object_id": i, "bbox_target": [float(v) for v in tb],
                              "bbox_render_source": [float(v) for v in rb],
                              "offset_norm": round(off, 6)})
        return ("exact", matched_cats, missing, extra_o, moved,
                sorted(position_unverified), len(matched))

    # fallback: category multisets; every matched category is position-unverifiable.
    # V04-2: only usable STRING categories enter the render multiset — a non-string
    # category is counted as an extra (typed marker, display-only) and can never match.
    t_cats = sorted(o["category"] for o in t_objs)   # validated non-empty strings above
    r_cat_vals = [_render_cat(f) for f in r_furn]
    rm = _multiset([c for c in r_cat_vals if c is not None])
    unreadable = [_cat_marker(f) for f, c in zip(r_furn, r_cat_vals) if c is None]
    tm = _multiset(t_cats)
    matched_cats = sorted(c for c in tm for _ in range(min(tm[c], rm.get(c, 0))))
    missing = sorted(c for c in tm for _ in range(max(0, tm[c] - rm.get(c, 0))))
    extra_o = sorted([c for c in rm for _ in range(max(0, rm[c] - tm.get(c, 0)))]
                     + unreadable)
    return ("multiset_fallback", matched_cats, missing, extra_o, [],
            sorted(set(matched_cats)), len(matched_cats))


def compare(scene: Dict, room: Dict) -> Dict:
    expected = expected_openings(scene)
    apertures = room.get("apertures") or []
    openings_mode, mismatches, extra, unverifiable_kinds = \
        _compare_openings(expected, apertures)
    (objects_mode, matched, missing, obj_extra, moved,
     position_unverified, n_matched) = _compare_objects(scene, room)

    t_count = len(scene.get("objects") or [])
    r_count = len(room.get("furniture") or [])
    components = {
        "opening_wall_mismatch_frac": round(len(mismatches) / max(1, len(expected)), 6),
        "extra_aperture_frac": round(len(extra) / max(1, len(apertures)), 6),
        "object_missing_frac": round(len(missing) / max(1, t_count), 6),
        "object_extra_frac": round(len(obj_extra) / max(1, r_count), 6),
        "object_moved_frac": round(len(moved) / max(1, n_matched), 6),
    }
    score = round(sum(components.values()) / len(components), 6)

    return {
        "wall_layout_diff": {
            "target_openings": len(expected),
            "render_apertures": len(apertures),
            "opening_mismatches": mismatches,
            "extra_render_apertures": extra,
        },
        "object_diff": {"matched": matched, "missing_in_render": missing,
                        "extra_in_render": obj_extra, "moved": moved},
        "identity": {
            "mode": openings_mode,               # exact | multiset_fallback | vacuous
            "unverifiable_kinds": unverifiable_kinds,
            "objects_mode": objects_mode,        # exact | multiset_fallback | vacuous
            "position_unverified": position_unverified,
        },
        "discrepancy": {"score": score, "components": components,
                        "calibration": "exploratory_uncalibrated"},
    }


def _fully_verified(body: Dict) -> bool:
    """Everything CLAIMED was verified. vacuous = nothing claimed on either side, which
    is verified-by-emptiness and reported as such rather than dressed up as "exact"."""
    ident = body["identity"]
    return (ident["mode"] in ("exact", "vacuous") and not ident["unverifiable_kinds"]
            and ident["objects_mode"] in ("exact", "vacuous")
            and not ident["position_unverified"])


def build_verdict(scene: Dict, packet: Dict, threshold: Optional[float],
                  allow_unverified: bool = False) -> Dict:
    body = compare(scene, packet["room"])
    m = packet["manifest"]
    state = "CONTINUE"
    if threshold is not None and body["discrepancy"]["score"] <= threshold \
            and (allow_unverified or _fully_verified(body)):
        state = "BELOW_THRESHOLD"
    return {"contract_version": CONTRACT_VERSION,
            "built_against": m.get("contract_version"),
            "run_id": m.get("run_id"), "iter": m.get("iter"),
            "target_image_id": m.get("target_image_id"),
            "input_sha256": m.get("sha256"),
            "agreement_policy": "allow_unverified" if allow_unverified else "strict",
            **body, "verdict": state}


def validate_verdict(v: Dict) -> List[str]:
    problems = []
    for k in ("contract_version", "built_against", "run_id", "iter", "target_image_id",
              "input_sha256", "agreement_policy", "wall_layout_diff", "object_diff",
              "identity", "discrepancy", "verdict"):
        if k not in v:
            problems.append(f"missing field {k}")
    if v.get("contract_version") != CONTRACT_VERSION:
        problems.append("wrong contract_version")
    if v.get("verdict") not in ("CONTINUE", "BELOW_THRESHOLD", "CAP_REACHED_FLAGGED"):
        problems.append("verdict not in enum")
    if v.get("discrepancy", {}).get("calibration") != "exploratory_uncalibrated":
        problems.append("discrepancy must be labeled exploratory_uncalibrated")
    ident = v.get("identity", {})
    if v.get("verdict") == "BELOW_THRESHOLD" and \
            v.get("agreement_policy") == "strict" and \
            (ident.get("unverifiable_kinds") or ident.get("position_unverified")
             or ident.get("mode") not in ("exact", "vacuous")
             or ident.get("objects_mode") not in ("exact", "vacuous")):
        problems.append("strict BELOW_THRESHOLD claimed with unverified identity/position")
    return problems


# ---------------------------------------------------------------- CLI

def run(target: Path, packet_dir: Path, out_dir: Path, threshold: Optional[float],
        allow_unverified: bool = False) -> Tuple[int, str]:
    try:
        scene = load_target(target)
        packet = load_packet(packet_dir)
        verdict = build_verdict(scene, packet, threshold, allow_unverified)
        text = canonical(verdict)          # R2-2: non-finite anywhere -> ValueError
    except Refused as e:
        return 2, f"REFUSED: {e}"
    except (TypeError, ValueError, KeyError, AttributeError, IndexError) as e:
        return 2, f"REFUSED (malformed input): {type(e).__name__}: {e}"
    problems = validate_verdict(verdict)
    if problems:
        return 1, "verdict failed self-validation: " + "; ".join(problems)
    if canonical(json.loads(text)) != text:
        return 1, "nondeterministic_run: canonical round-trip diverged"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "verdict.json"
    out.write_text(text, encoding="utf-8")
    n_mm = len(verdict["wall_layout_diff"]["opening_mismatches"])
    n_ex = len(verdict["wall_layout_diff"]["extra_render_apertures"])
    n_mv = len(verdict["object_diff"]["moved"])
    return 0, (f"verdict {verdict['verdict']} score={verdict['discrepancy']['score']} "
               f"opening_mismatches={n_mm} extra_apertures={n_ex} moved_objects={n_mv} "
               f"identity={verdict['identity']['mode']}/"
               f"{verdict['identity']['objects_mode']} "
               f"policy={verdict['agreement_policy']} "
               f"sha256={sha256_bytes(text.encode())} -> {out}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="render<->verdict comparator (T1.2, v0.6)")
    ap.add_argument("--target", required=True)
    ap.add_argument("--packet", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threshold", type=float, default=None)
    ap.add_argument("--allow-unverified-agreement", action="store_true",
                    help="permit BELOW_THRESHOLD without verified identity/position "
                         "(stub producers only; the platform always emits ids)")
    a = ap.parse_args(argv)
    code, msg = run(Path(a.target), Path(a.packet), Path(a.out), a.threshold,
                    a.allow_unverified_agreement)
    print(msg, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
