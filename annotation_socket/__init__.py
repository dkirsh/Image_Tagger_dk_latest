"""
annotation_socket — the vision-annotation pipeline as a night-nurse CONTROLLER SOCKET.

One image = one unit, pulled from a controller-written queue; every predicate value routed
through the trust chokepoint (derivation.py: SCORED-with-evidence / ABSTAINED-with-named-
missing-inputs / UNKNOWN-fail-closed); gated by an independent mechanical-primary verify()
(replay + evidence + dependency + abstention-audit + coverage); content-addressed.

Run from the repo root (/Users/davidusa/REPOS/Image_Tagger_dk_latest):
    python3 -m annotation_socket.run_stage <stage_dir> <img1> <img2> <img3>
Depends on the shared CPP library at /Users/davidusa/REPOS/_control/cpp (adopted, not
reimplemented) and cnfa_algs/ in this repo. See SOCKET_CONFORMANCE.md.
"""
