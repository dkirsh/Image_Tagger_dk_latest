"""
Portable CPP/supervisor consumer-boundary tests (CLAUDE-M1-BUILD, 2026-08-06).

What these lock, one test per clause of the resolution contract in
`annotation_socket/_cpp_bootstrap.py`:

  1. an arbitrary temporary directory layout containing NO David/Claude path resolves
  2. an explicit CONTROL_ROOT overrides the derived scan — and never falls through to a guess
  3. an ambient module cannot impersonate the packaged or explicitly selected provider
  4. a missing CPP provider fails closed with one diagnostic naming the contract + remedies
  5. a missing `supervisor/trusted_derivation.py` fails closed as a SEPARATE contract
  6. a worker subprocess imports from a checkout whose path contains spaces
  7. a source census: the six runtime modules embed no `/home/claude` or `/Users/davidusa`

Every path-resolution case runs in a real child process against a synthetic provider tree, so
what is exercised is the actual import machinery rather than a mock of it. The synthetic
`cpp/locate.py` writes a sentinel file when its `bootstrap()` is called, which is how these
tests prove the consumer DELEGATES to the provider's sanctioned entry point instead of
re-implementing it.

Run: PYTHONPATH=. python3 annotation_socket/tests/test_cpp_bootstrap.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from collections import namedtuple
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = REPO_ROOT / "annotation_socket"
BOOTSTRAP_SRC = PKG_DIR / "_cpp_bootstrap.py"

#: The six runtime modules the charge scopes the census to.
RUNTIME_MODULES = ("annotator.py", "verify.py", "controller_drive.py",
                   "run_stage.py", "controller.py", "derivation.py")

FORBIDDEN_LITERALS = ("/home/claude", "/Users/davidusa")

sys.path.insert(0, str(REPO_ROOT))


# --------------------------------------------------------------------- synthetic provider
_LOCATE_SRC = '''\
"""Synthetic stand-in for the provider's cpp/locate.py (same env-driven semantics)."""
import os, sys
from pathlib import Path

DEFAULT_CONTROL_ROOT = Path(__file__).resolve().parents[1]
SENTINEL = Path(__file__).resolve().parent / "_bootstrap_called.txt"


def control_root():
    return Path(os.environ.get("CONTROL_ROOT", str(DEFAULT_CONTROL_ROOT))).expanduser().resolve()


def bootstrap():
    root = control_root()
    root_s = str(root)
    if root_s not in sys.path:
        sys.path.insert(0, root_s)
    SENTINEL.write_text(root_s)          # proof the consumer delegated here
    return root


def supervisor_path(name):
    return control_root() / "supervisor" / name
'''

_TRUSTED_DERIVATION_SRC = 'UNKNOWN = "UNKNOWN"\n'
_SUPERVISOR_SRC = 'def classify_result(exit_code, stdout, stderr):\n    return "ok"\n'

World = namedtuple("World", "base control repo site")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def _make_provider(root: Path, *, with_cpp: bool = True, with_supervisor: bool = True,
                   stage_marker: str = "stage@control") -> Path:
    """A synthetic `_control`-shaped provider checkout."""
    root.mkdir(parents=True, exist_ok=True)
    if with_cpp:
        _write(root / "cpp" / "__init__.py", "")
        _write(root / "cpp" / "locate.py", _LOCATE_SRC)
        _write(root / "cpp" / "stage.py",
               f"MARKER = {stage_marker!r}\n\n\ndef ensure_stage(*a, **k):\n    return None\n")
    if with_supervisor:
        _write(root / "supervisor" / "trusted_derivation.py", _TRUSTED_DERIVATION_SRC)
        _write(root / "supervisor" / "supervisor.py", _SUPERVISOR_SRC)
    return root


def _make_consumer(repo: Path) -> Path:
    """A synthetic checkout carrying the REAL `_cpp_bootstrap.py` under test."""
    pkg = repo / "annotation_socket"
    _write(pkg / "__init__.py", '"""synthetic consumer package for bootstrap tests"""\n')
    shutil.copy2(BOOTSTRAP_SRC, pkg / "_cpp_bootstrap.py")
    return repo


def _make_world(base: Path, *, control_name: str = "_control", with_cpp: bool = True,
                with_supervisor: bool = True, stage_marker: str = "stage@control",
                packaged_marker: str | None = None,
                packaged_verified: bool = False) -> World:
    base.mkdir(parents=True, exist_ok=True)
    control = _make_provider(base / control_name, with_cpp=with_cpp,
                             with_supervisor=with_supervisor, stage_marker=stage_marker)
    repo = _make_consumer(base / "repo")
    site = None
    if packaged_marker is not None:
        site = base / "site"
        _write(site / "cpp" / "__init__.py", "")
        _write(site / "cpp" / "locate.py", _LOCATE_SRC)
        _write(site / "cpp" / "stage.py",
               f"MARKER = {packaged_marker!r}\n\n\ndef ensure_stage(*a, **k):\n    return None\n")
        if packaged_verified:
            info = site / "cnfa_cpp-1.0.dist-info"
            _write(info / "METADATA",
                   "Metadata-Version: 2.1\nName: cnfa-cpp\nVersion: 1.0\n")
            _write(info / "top_level.txt", "cpp\n")
    return World(base=base, control=control, repo=repo, site=site)


# --------------------------------------------------------------------- child-process probe
_PROBE = textwrap.dedent('''
    import json
    out = {}
    from annotation_socket import _cpp_bootstrap as B
    out["resolution"] = B.resolve().as_dict()
    out["candidates"] = [str(c) for c in B.candidate_roots()]
    try:
        B.bootstrap()
        from cpp import stage as S
        out["stage_marker"] = getattr(S, "MARKER", None)
        out["cpp_ok"] = True
    except Exception as exc:
        out["cpp_ok"] = False
        out["cpp_error_type"] = type(exc).__name__
        out["cpp_error"] = str(exc)
    try:
        out["unknown"] = B.trusted_unknown()
        out["sup_ok"] = True
    except Exception as exc:
        out["sup_ok"] = False
        out["sup_error_type"] = type(exc).__name__
        out["sup_error"] = str(exc)
    print("PROBE_JSON " + json.dumps(out))
''')

_STRIP_ENV = ("PYTHONPATH", "CONTROL_ROOT", "PYTHONHOME", "PYTHONSTARTUP")


def _clean_env() -> dict:
    return {k: v for k, v in os.environ.items() if k not in _STRIP_ENV}


def _run_probe(repo: Path, *, control_root: Path | None = None,
               pythonpath: tuple = (), cwd: Path | None = None) -> dict:
    env = _clean_env()
    env["PYTHONPATH"] = os.pathsep.join([str(repo), *(str(p) for p in pythonpath)])
    if control_root is not None:
        env["CONTROL_ROOT"] = str(control_root)
    proc = subprocess.run([sys.executable, "-c", _PROBE], cwd=str(cwd or repo), env=env,
                          capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, f"probe crashed:\n{proc.stdout}\n{proc.stderr}"
    lines = [ln for ln in proc.stdout.splitlines() if ln.startswith("PROBE_JSON ")]
    assert lines, f"no probe output:\n{proc.stdout}\n{proc.stderr}"
    return json.loads(lines[-1][len("PROBE_JSON "):])


def _tmpbase(td: str, *parts: str) -> Path:
    """Resolved base dir — macOS /var is a symlink to /private/var and the resolver resolves."""
    return Path(td).resolve().joinpath(*parts)


def _sentinel(provider: Path) -> Path:
    return provider / "cpp" / "_bootstrap_called.txt"


# ============================================================ 1. arbitrary derived layout
def test_derived_resolution_in_arbitrary_layout():
    """No CONTROL_ROOT, no packaged cpp, no David/Claude path anywhere: the bounded ancestor
    scan finds `<ancestor>/_control` and the provider's own bootstrap() is what runs."""
    with tempfile.TemporaryDirectory() as td:
        w = _make_world(_tmpbase(td, "some", "arbitrary", "place"))
        out = _run_probe(w.repo)

        assert out["cpp_ok"], out.get("cpp_error")
        assert out["resolution"]["cpp_mode"] == "derived_local", out["resolution"]
        assert out["resolution"]["root_source"] == "derived"
        assert out["resolution"]["control_root"] == str(w.control)
        assert out["resolution"]["packaged_cpp"] is False
        assert out["stage_marker"] == "stage@control"
        assert out["sup_ok"] and out["unknown"] == "UNKNOWN"

        # delegation, not duplication: the provider's sanctioned bootstrap() actually ran
        assert _sentinel(w.control).read_text() == str(w.control)

        blob = json.dumps(out)
        for literal in FORBIDDEN_LITERALS:
            assert literal not in blob, f"{literal} leaked into a synthetic-layout resolution"
    print("  derived local scan resolves an arbitrary layout; provider bootstrap() delegated  OK")


def test_derived_scan_is_bounded_and_named():
    """Candidates are derived and bounded — an unbounded walk to / would adopt a stranger's
    provider checkout."""
    from annotation_socket import _cpp_bootstrap as B
    deep = Path("/a/b/c/d/e/f/g/h/i")                              # 9 levels below /
    cands = B.candidate_roots(consumer_root=deep, cwd=deep)
    assert cands, "no candidates generated"
    assert all(c.name in B.CONTROL_DIR_NAMES for c in cands), cands
    assert len(cands) <= 2 * (B.ASCENT_LIMIT + 1) * len(B.CONTROL_DIR_NAMES)
    assert cands[0] == deep / "_control"                           # nearest ancestor first
    assert Path("/a/b/c/_control") in cands                        # exactly ASCENT_LIMIT up
    assert Path("/a/b/_control") not in cands                      # one past the bound
    assert Path("/_control") not in cands                          # bounded: never reaches /
    print(f"  candidate scan bounded to {B.ASCENT_LIMIT} levels x {len(B.CONTROL_DIR_NAMES)} "
          f"names, nearest ancestor first  OK")


# ============================================================ 2. CONTROL_ROOT override
def test_control_root_override_wins_over_derived():
    with tempfile.TemporaryDirectory() as td:
        base = _tmpbase(td, "world")
        w = _make_world(base, stage_marker="stage@derived")
        explicit = _make_provider(base / "elsewhere" / "provider", stage_marker="stage@explicit")

        out = _run_probe(w.repo, control_root=explicit)

        assert out["cpp_ok"], out.get("cpp_error")
        assert out["resolution"]["cpp_mode"] == "control_root_env"
        assert out["resolution"]["root_source"] == "env"
        assert out["resolution"]["control_root"] == str(explicit)
        assert out["stage_marker"] == "stage@explicit"
        assert out["resolution"]["searched"] == [str(explicit)], \
            "an explicit CONTROL_ROOT must be the ONLY candidate examined"
        assert _sentinel(explicit).exists() and not _sentinel(w.control).exists()
    print("  explicit CONTROL_ROOT overrides the derived scan and is the only candidate  OK")


def test_explicit_control_root_never_falls_through_to_a_guess():
    """The R1 defect class: a bad explicit root must fail loudly, not silently adopt the
    perfectly good provider sitting next door."""
    with tempfile.TemporaryDirectory() as td:
        base = _tmpbase(td, "world")
        w = _make_world(base, stage_marker="stage@derived")
        bogus = base / "not" / "a" / "provider"

        out = _run_probe(w.repo, control_root=bogus)

        assert out["cpp_ok"] is False
        assert out["cpp_error_type"] == "CppBootstrapError"
        assert "stage_marker" not in out, "a stage module was imported despite the bad root"
        assert out["resolution"]["control_root"] == str(bogus)
        assert not _sentinel(w.control).exists(), "fell through to the derived provider"
        assert "never falls through to a guess" in out["cpp_error"]
    print("  a wrong explicit CONTROL_ROOT fails closed instead of guessing  OK")


# ============================================================ 3. packaged precedence
def test_unverified_ambient_cpp_cannot_outrank_derived_provider():
    """Importability alone is not package provenance."""
    with tempfile.TemporaryDirectory() as td:
        w = _make_world(_tmpbase(td, "world"), stage_marker="stage@control",
                        packaged_marker="stage@packaged")

        out = _run_probe(w.repo, pythonpath=(w.site,))

        assert out["cpp_ok"], out.get("cpp_error")
        assert out["resolution"]["cpp_mode"] == "derived_local"
        assert out["resolution"]["packaged_cpp"] is False
        assert out["stage_marker"] == "stage@control"
        assert _sentinel(w.control).exists()
        assert out["sup_ok"] and out["unknown"] == "UNKNOWN"
    print("  unverified ambient cpp cannot impersonate the declared package  OK")


def test_verified_packaged_cpp_is_accepted_without_syspath_surgery():
    with tempfile.TemporaryDirectory() as td:
        w = _make_world(_tmpbase(td, "world"), stage_marker="stage@control",
                        packaged_marker="stage@packaged", packaged_verified=True)

        out = _run_probe(w.repo, pythonpath=(w.site,))

        assert out["cpp_ok"], out.get("cpp_error")
        assert out["resolution"]["cpp_mode"] == "packaged"
        assert out["resolution"]["packaged_cpp"] is True
        assert out["stage_marker"] == "stage@packaged"
        assert not _sentinel(w.control).exists()
        assert out["sup_ok"] and out["unknown"] == "UNKNOWN"
    print("  distribution-owned packaged cpp is accepted without sys.path surgery  OK")


def test_explicit_control_root_outranks_ambient_cpp_and_trusted_derivation():
    with tempfile.TemporaryDirectory() as td:
        base = _tmpbase(td, "world")
        explicit = _make_provider(base / "provider", stage_marker="stage@explicit")
        repo = _make_consumer(base / "repo")
        ambient = base / "ambient"
        _write(ambient / "cpp" / "__init__.py", "")
        _write(ambient / "cpp" / "stage.py",
               "MARKER='stage@poison'\ndef ensure_stage(*a, **k): pass\n")
        _write(ambient / "trusted_derivation.py", "UNKNOWN='POISONED_UNKNOWN'\n")

        out = _run_probe(repo, control_root=explicit, pythonpath=(ambient,), cwd=ambient)

        assert out["cpp_ok"], out.get("cpp_error")
        assert out["resolution"]["cpp_mode"] == "control_root_env"
        assert out["resolution"]["searched"] == [str(explicit)]
        assert out["stage_marker"] == "stage@explicit"
        assert out["unknown"] == "UNKNOWN"
    print("  explicit CONTROL_ROOT rejects ambient cpp and trusted-derivation shadows  OK")


# ============================================================ 4. missing CPP
def test_missing_cpp_fails_closed_with_one_diagnostic():
    with tempfile.TemporaryDirectory() as td:
        base = _tmpbase(td, "world")
        w = _make_world(base, with_cpp=False)          # supervisor present, cpp absent

        out = _run_probe(w.repo, control_root=w.control)

        assert out["cpp_ok"] is False
        assert out["cpp_error_type"] == "CppBootstrapError"
        msg = out["cpp_error"]
        assert "Controller-Pipeline Protocol" in msg, msg
        assert "cpp/locate.py" in msg and "cpp/stage.py" in msg, msg
        assert "remedies" in msg and "CONTROL_ROOT" in msg, msg
        assert "cnfa-cpp" in msg, "the diagnostic must name the packaged target state"
        assert "<ancestor>/_control" in msg, "the diagnostic must name the local-layout remedy"
        assert msg.count("required provider contract unavailable") == 1, "one diagnostic only"

        # the OTHER contract is unaffected — they are independent
        assert out["sup_ok"] and out["unknown"] == "UNKNOWN"
    print("  missing CPP -> one fail-closed diagnostic naming the contract + 3 remedies  OK")


# ============================================================ 5. missing supervisor
def test_missing_trusted_derivation_fails_closed_separately():
    with tempfile.TemporaryDirectory() as td:
        base = _tmpbase(td, "world")
        w = _make_world(base, with_supervisor=False)   # cpp present, supervisor absent

        out = _run_probe(w.repo, control_root=w.control)

        assert out["cpp_ok"], out.get("cpp_error")     # CPP half is fine
        assert out["sup_ok"] is False
        assert out["sup_error_type"] == "CppBootstrapError"
        msg = out["sup_error"]
        assert "trusted-derivation chokepoint" in msg, msg
        assert "supervisor/trusted_derivation.py" in msg, msg
        assert "remedies" in msg, msg
        assert "unknown" not in out, "no UNKNOWN may be produced without the provider"
    print("  missing supervisor/trusted_derivation.py -> its OWN fail-closed diagnostic  OK")


def test_derivation_has_no_local_unknown_fallback():
    """Structural, not textual: UNKNOWN must be bound by CALLING the provider chokepoint, never
    to a literal. Checked on the parse tree so a comment describing the removed fallback (which
    necessarily quotes it) cannot pass or fail this test by accident."""
    import ast

    src = (PKG_DIR / "derivation.py").read_text()
    bindings = []
    for node in ast.walk(ast.parse(src)):
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) else [])
        for target in targets:
            if isinstance(target, ast.Name) and target.id == "UNKNOWN":
                bindings.append(node.value)
    assert len(bindings) == 1, f"expected exactly one UNKNOWN binding, found {len(bindings)}"
    value = bindings[0]
    assert not isinstance(value, ast.Constant), \
        "UNKNOWN is bound to a literal — the local sentinel fallback is back"
    assert isinstance(value, ast.Call) and getattr(value.func, "id", None) == "trusted_unknown", \
        f"UNKNOWN must come from trusted_unknown(), got {ast.dump(value)[:120]}"
    assert "sys.path" not in src
    print("  derivation.py binds UNKNOWN only via trusted_unknown(), no literal fallback  OK")


# ============================================================ 6. spaces in the checkout path
def test_worker_subprocess_imports_from_path_with_spaces():
    """The portable worker-startup contract: PYTHONPATH + argv carry the layout, the `-c`
    source carries nothing. Exercised on a checkout whose path contains spaces."""
    from annotation_socket import _cpp_bootstrap as B

    with tempfile.TemporaryDirectory() as td:
        base = _tmpbase(td, "dir with spaces", "a b")
        w = _make_world(base, stage_marker="stage@spaced")
        stage_dir = base / "stage dir with spaces"
        stage_dir.mkdir(parents=True, exist_ok=True)

        env = B.worker_env(_clean_env(), consumer_root=w.repo, control_root=w.control)
        parts = env["PYTHONPATH"].split(os.pathsep)
        assert str(w.repo) in parts and str(w.control) in parts, env["PYTHONPATH"]
        assert " " in str(w.repo)                                   # the case is real
        assert env["CONTROL_ROOT"] == str(w.control)

        child = ("import json, sys; "
                 "from annotation_socket import _cpp_bootstrap as B; B.bootstrap(); "
                 "from cpp import stage; "
                 "print(json.dumps({'marker': stage.MARKER, 'argv1': sys.argv[1]}))")
        for literal in FORBIDDEN_LITERALS:
            assert literal not in child
        proc = subprocess.run([sys.executable, "-c", child, str(stage_dir)],
                              env=env, capture_output=True, text=True, timeout=180)
        assert proc.returncode == 0, f"{proc.stdout}\n{proc.stderr}"
        got = json.loads(proc.stdout.strip().splitlines()[-1])
        assert got["marker"] == "stage@spaced"
        assert got["argv1"] == str(stage_dir)
    print("  worker_env + argv start a child from a spaced checkout, no path in the source  OK")


def test_controller_drive_worker_code_carries_no_path():
    """Static contract on the spawn string itself (importing controller_drive would drag in
    the whole vision stack, so this reads the source instead)."""
    src = (PKG_DIR / "controller_drive.py").read_text()
    start = src.index("WORKER_CODE = (")
    body = src[start:src.index("\n\n", start)]
    assert "sys.path" not in body, body
    assert "sys.argv[1]" in body, body
    assert "{stage_dir" not in body, "the stage dir must not be interpolated into the source"
    for literal in FORBIDDEN_LITERALS:
        assert literal not in body
    assert "env=worker_env()" in src, "the spawn must use the controlled environment"
    print("  controller_drive WORKER_CODE embeds no source-tree path  OK")


# ============================================================ 7. source census
def test_runtime_modules_contain_no_host_or_container_paths():
    offenders = []
    for name in (*RUNTIME_MODULES, "_cpp_bootstrap.py"):
        path = PKG_DIR / name
        assert path.is_file(), f"missing runtime module {path}"
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            for literal in FORBIDDEN_LITERALS:
                if literal in line:
                    offenders.append(f"{name}:{lineno}: {literal}  |  {line.strip()[:90]}")
    assert not offenders, "hardcoded host/container paths:\n" + "\n".join(offenders)
    print(f"  census: {len(RUNTIME_MODULES)} runtime modules + the helper, "
          f"0 literal {' / '.join(FORBIDDEN_LITERALS)}  OK")


def test_runtime_modules_have_no_manual_syspath_bootstrap():
    """One helper owns resolution; a module doing its own sys.path surgery re-forks it."""
    offenders = [name for name in RUNTIME_MODULES
                 if "sys.path" in (PKG_DIR / name).read_text()]
    assert not offenders, f"modules still bootstrapping by hand: {offenders}"
    print("  no runtime module performs its own sys.path bootstrap  OK")


# ============================================================ real provider (this machine)
def test_real_provider_contract_is_satisfied_here():
    """Against the ACTUAL provider checkout, in this process: both contracts resolve, and
    derivation's UNKNOWN is the provider's object rather than a local lookalike."""
    from annotation_socket import _cpp_bootstrap as B

    res = B.resolve()
    stage = B.import_stage()
    assert hasattr(stage, "ensure_stage")
    unknown = B.trusted_unknown()
    assert unknown == "UNKNOWN"

    sup = B.import_supervisor()
    assert hasattr(sup, "classify_result")

    from annotation_socket import derivation as D
    assert D.UNKNOWN == unknown
    assert D.UNKNOWN is not None and D.UNKNOWN not in (D.SCORED, D.ABSTAINED)

    provider = B.supervisor_dir() / "trusted_derivation.py"
    assert provider.is_file(), provider
    print(f"  real provider: mode={res.cpp_mode} root={res.control_root} UNKNOWN={unknown!r}  OK")


TESTS = [
    test_derived_resolution_in_arbitrary_layout,
    test_derived_scan_is_bounded_and_named,
    test_control_root_override_wins_over_derived,
    test_explicit_control_root_never_falls_through_to_a_guess,
    test_unverified_ambient_cpp_cannot_outrank_derived_provider,
    test_verified_packaged_cpp_is_accepted_without_syspath_surgery,
    test_explicit_control_root_outranks_ambient_cpp_and_trusted_derivation,
    test_missing_cpp_fails_closed_with_one_diagnostic,
    test_missing_trusted_derivation_fails_closed_separately,
    test_derivation_has_no_local_unknown_fallback,
    test_worker_subprocess_imports_from_path_with_spaces,
    test_controller_drive_worker_code_carries_no_path,
    test_runtime_modules_contain_no_host_or_container_paths,
    test_runtime_modules_have_no_manual_syspath_bootstrap,
    test_real_provider_contract_is_satisfied_here,
]


if __name__ == "__main__":
    for fn in TESTS:
        print(fn.__name__)
        fn()
    print(f"\nCPP BOOTSTRAP TESTS PASSED ({len(TESTS)})")
