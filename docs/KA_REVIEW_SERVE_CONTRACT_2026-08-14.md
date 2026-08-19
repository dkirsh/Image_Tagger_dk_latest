# KA Feature-Review page — serve contract (T3.1), v2

*STATUS: **DRAFT v2 — needs Stephan's ⬜ fills, then review.** Tanishq hosts and serves;
Stephan owns the page and its code in `Knowledge_Atlas`. v2 answers findings 9–12 of a
non-author review (separation: same-model-fresh-context). Contract version:
**ka-serve/v0.1** — every deploy records the version it was built against (§2), and any
breaking change to this contract is announced on the `_control` ledger before it lands.*

**Prerequisites, stated plainly (v1 overstated runnability):** `Knowledge_Atlas` is NOT
cloned on Tanishq's machine, and no sample packet directory exists here yet. Acceptance
items 1–3 are blocked until (a) Stephan fills every ⬜ and supplies the sample directory,
and (b) a KA bundle (not source) or run artifact is handed over. Live data stays BLOCKED
on Codex 1a; everything here builds against the sample.

## 1 · What Stephan's lane hands off (the deployable)

- ⬜ Artifact form: deployable bundle (dir/tarball) or run command against a KA checkout?
- ⬜ Run command, verbatim
- ⬜ Port (or "reads $PORT")
- ⬜ Env vars: name, purpose, example value, secret y/n — an UNDOCUMENTED-but-required
  var is the `contract_implicit` failure this contract exists to prevent
- ⬜ Data mount: `verification_packets.py` output layout + migration-024 annotations
  store — exact paths/globs read at runtime
- ⬜ SAMPLE packet directory (required; the dry-run acceptance runs against it)
- ⬜ Health check: URL path + expected response
- ⬜ Bundle version signal: how a new bundle announces itself (tag/path/message), and the
  version string a deploy can record

## 2 · What Tanishq provides (hosting)

- ☑ Host + reverse proxy + TLS + DNS (recorded here once stood up: host ___ , url ___ )
- ☑ JWT in front of the page; secret env-injected at deploy, never in any repo
  (`secret_in_public_repo`)
- ☑ Uptime + restart-on-boot (service unit named here)
- ☑ Data-sync job: source ___ → mount ___ , schedule ___ , one log line per sync
- ☑ **Dependency check:** each deploy records `{ka_serve_contract: "ka-serve/v0.1",
  bundle_version: <from Stephan's ⬜ signal>, deployed_utc}` in the deploy artifact dir —
  so "which bundle is live, built against which contract" is answerable on command
- ☑ Deploy artifacts (proxy config, unit, sync script) live in `Image_Tagger_dk_latest`
  (Tanishq's lane). No commit ever lands in `Knowledge_Atlas`.

## 3 · Acceptance

1. Contract completeness: every ⬜ filled; no step requires editing KA source.
2. Dry-run: documented command + sample directory → page up on documented port, renders
   the sample packets, health check answers.
3. JWT: unauthenticated refused; authenticated passes.
4. Lane cleanliness — split by enforcement kind (a monitor is not an enforcer, and
   neither is a human doing a machine's job):
   a. **Mechanically enforced:** no commit into `Knowledge_Atlas` from the tanishq lane —
      the lane guard refuses it (`Knowledge_Atlas: "stephan"` in `lanes.json`, whole-repo).
      Evidence: guard installed + proven 2026-08-19 (ledger sprint0.1).
   b. **Human-inspected (no guard covers this):** no KA *source* copied into
      `Image_Tagger_dk_latest`, and no secret in any commit — reviewed by a non-author
      reader; target separation level: different-lineage or source-blind-human (state
      which was achieved, per method card step 6).

## 4 · Method block

- **Claim:** with only this document + the sample directory, someone who has never spoken
  to Stephan can bring the page up on a clean machine.
- **Refutation:** any question they must ask Stephan mid-deploy = a ⬜ this contract
  missed (`contract_implicit`).
- **Negative control:** remove one documented env var and run: the page must fail loudly
  at startup naming it; a half-working page means the contract documents decoration, not
  dependencies.

*v1→v2: added contract version + dependency check and breaking-change protocol (finding
10); split acceptance 4 into enforced vs inspected halves (finding 9); stated the
not-runnable-here prerequisites honestly (finding 11); named the review separation rungs
(finding 12). RECORD: commit this file before citing it.*
