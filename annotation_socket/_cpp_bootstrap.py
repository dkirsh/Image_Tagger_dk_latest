"""
annotation_socket._cpp_bootstrap — the ONE place this repository resolves its external
provider contracts, fail-closed.

Image_Tagger is a CONSUMER of two things it does not own, both published by the `_control`
provider checkout:

  CPP         `cpp/locate.py` + `cpp/stage.py` — the Controller-Pipeline Protocol reference
              (queue/claims/events/quarantine/verdicts/accepted, the `[W:]` role boundary).
  SUPERVISOR  `supervisor/trusted_derivation.py` (the UNKNOWN trust sentinel) and
              `supervisor/supervisor.py` (death classification / progress watchdog).

These are two SEPARATE contracts. `cpp/` is not self-contained at runtime: `cpp/worker_shim.py`
reuses the supervisor's classification primitives, and this repo's `derivation.py` takes its
UNKNOWN sentinel from `supervisor/trusted_derivation.py`. A future `cnfa-cpp` wheel that ships
only `cpp/` would therefore satisfy the CPP contract and NOT the supervisor contract; the two
are reported and diagnosed independently here so that gap can never be papered over.

RESOLUTION ORDER (explicit, ordered, testable — see tests/test_cpp_bootstrap.py):

  1. PACKAGED       `import cpp` already works (installed distribution, or an embedder that
                    put the provider on sys.path). Highest precedence, and we then perform NO
                    sys.path surgery at all.
  2. CONTROL_ROOT   an explicit `CONTROL_ROOT` environment variable. Honored STRICTLY: when it
                    is set it is the ONLY candidate. A wrong explicit value fails loudly and
                    never falls through to a guess — a silent fallback past an operator's
                    declared root is precisely the failure mode this module exists to remove.
  3. DERIVED LOCAL  bounded local-development candidates derived from where THIS file lives
                    (and from the process cwd): `<ancestor>/_control` and
                    `<ancestor>/_control_deps`, nearest ancestor first, at most
                    ASCENT_LIMIT levels up. No user name, no host path, no container path is
                    embedded anywhere in this module.
  4. FAIL CLOSED    if the required contract is still unsatisfied, raise ONE CppBootstrapError
                    naming the missing contract, what was searched, and the supported remedies.

A candidate is accepted only on CONTENT (`cpp/locate.py` and `cpp/stage.py` are real files),
never on mere directory existence.

Once a provider root is resolved we hand off to the provider's own sanctioned entry point,
`cpp.locate.bootstrap()`, rather than re-implementing its semantics. The provider's helper
cannot be imported until the provider is first reachable, so exactly one seed step is
unavoidable: put the resolved root on sys.path, import `cpp.locate`, then let it act. We also
pin `CONTROL_ROOT` to the root we resolved BEFORE calling it, so the provider's own built-in
default root can never fire behind our back and re-introduce a host path.
"""
from __future__ import annotations

import importlib
import importlib.util
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Optional, Sequence, Tuple

__all__ = [
    "CppBootstrapError", "Resolution",
    "CPP_CONTRACT", "SUPERVISOR_CONTRACT", "CONTROL_ROOT_ENV",
    "CONSUMER_ROOT", "CONTROL_DIR_NAMES", "ASCENT_LIMIT",
    "CPP_MARKERS", "SUPERVISOR_MARKERS",
    "candidate_roots", "resolve", "bootstrap", "supervisor_dir",
    "import_stage", "import_supervisor", "trusted_unknown",
    "ensure_consumer_root_importable", "worker_env",
]

# --------------------------------------------------------------------------- contract names
CPP_CONTRACT = "cpp — Controller-Pipeline Protocol reference (cpp/locate.py + cpp/stage.py)"
SUPERVISOR_CONTRACT = ("supervisor — trusted-derivation chokepoint "
                       "(supervisor/trusted_derivation.py, supervisor/supervisor.py)")

CPP_MARKERS: Tuple[str, ...] = ("cpp/locate.py", "cpp/stage.py")
SUPERVISOR_MARKERS: Tuple[str, ...] = ("supervisor/trusted_derivation.py",)

CONTROL_ROOT_ENV = "CONTROL_ROOT"

#: Directory names a provider checkout is conventionally placed under, beside a consumer
#: checkout. Names only — the containing directory is always DERIVED, never written down.
CONTROL_DIR_NAMES: Tuple[str, ...] = ("_control", "_control_deps")

#: How far above a starting directory the derived scan may walk. Bounded on purpose: an
#: unbounded walk to `/` would happily adopt an unrelated provider from a stranger's tree.
ASCENT_LIMIT = 6

#: The directory that must be importable for `import annotation_socket` / `import cnfa_algs`
#: to work — i.e. this repository checkout. Derived from this file, so it is correct in the
#: primary checkout, in any git worktree, and in a sandbox copy alike.
CONSUMER_ROOT: Path = Path(__file__).resolve().parents[1]

_PATH_LIST_SEP = os.pathsep


class CppBootstrapError(RuntimeError):
    """Fail-closed provider-contract failure. Carries ONE complete diagnostic."""

    def __init__(self, message: str, *, contract: str) -> None:
        super().__init__(message)
        self.contract = contract


@dataclass(frozen=True)
class Resolution:
    """What the resolver decided, and on what evidence. Purely descriptive — building a
    Resolution never mutates sys.path or the environment."""

    cpp_mode: str                       # packaged | control_root_env | derived_local | unresolved
    control_root: Optional[Path]        # provider checkout root, if one was located
    root_source: str                    # env | derived | none
    searched: Tuple[str, ...]           # every candidate examined, in order
    env_control_root: Optional[str]     # raw CONTROL_ROOT as the process received it
    packaged_cpp: bool                  # `import cpp` worked without any help from us

    def as_dict(self) -> Dict[str, object]:
        return {
            "cpp_mode": self.cpp_mode,
            "control_root": None if self.control_root is None else str(self.control_root),
            "root_source": self.root_source,
            "searched": list(self.searched),
            "env_control_root": self.env_control_root,
            "packaged_cpp": self.packaged_cpp,
        }


# --------------------------------------------------------------------------- marker helpers
def _is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def _missing_markers(root: Optional[Path], markers: Sequence[str]) -> List[str]:
    """Which of `markers` are NOT present under `root`. Empty list == contract satisfiable."""
    if root is None:
        return list(markers)
    return [m for m in markers if not _is_file(root.joinpath(*m.split("/")))]


def _has_markers(root: Optional[Path], markers: Sequence[str]) -> bool:
    return not _missing_markers(root, markers)


def _resolved(path: Path) -> Path:
    try:
        return path.expanduser().resolve()
    except OSError:
        return path.expanduser()


# --------------------------------------------------------------------------- candidate scan
def _ascend(start: Path, limit: int = ASCENT_LIMIT) -> List[Path]:
    """`start` and up to `limit` of its ancestors, nearest first."""
    start = _resolved(Path(start))
    return [start, *list(start.parents)[:limit]]


def candidate_roots(*, consumer_root: Optional[Path] = None,
                    cwd: Optional[Path] = None) -> List[Path]:
    """Bounded, derived local-development provider candidates, best first.

    Every candidate is `<ancestor of this checkout or of the cwd>/<control dir name>`. The
    ancestors are computed at run time, so this function contains no user, host, or container
    path — moving the checkout anywhere (including a directory whose name contains spaces)
    keeps it correct.
    """
    starts: List[Path] = [Path(consumer_root) if consumer_root is not None else CONSUMER_ROOT]
    if cwd is not None:
        starts.append(Path(cwd))
    else:
        try:
            starts.append(Path.cwd())
        except OSError:                      # cwd deleted out from under the process
            pass

    out: List[Path] = []
    seen = set()
    for start in starts:
        for ancestor in _ascend(start):
            for name in CONTROL_DIR_NAMES:
                cand = ancestor / name
                key = str(cand)
                if key not in seen:
                    seen.add(key)
                    out.append(cand)
    return out


def _packaged_cpp_available() -> bool:
    """True when `import cpp` already resolves without us touching sys.path."""
    if "cpp" in sys.modules:
        return True
    try:
        return importlib.util.find_spec("cpp") is not None
    except (ImportError, ValueError):
        return False


# --------------------------------------------------------------------------- the resolver
_RESOLUTION: Optional[Resolution] = None


def resolve(*, refresh: bool = False) -> Resolution:
    """Decide where the provider is, without changing anything. Cached per process.

    The packaged probe is taken on the FIRST call, before any seed insert of ours could make
    `cpp` importable — otherwise every later call would misreport itself as `packaged`.
    """
    global _RESOLUTION
    if _RESOLUTION is not None and not refresh:
        return _RESOLUTION

    packaged = _packaged_cpp_available()
    env_raw = os.environ.get(CONTROL_ROOT_ENV)
    searched: List[str] = []

    root: Optional[Path] = None
    root_source = "none"

    if env_raw is not None and env_raw.strip():
        # Explicit beats derived, and explicit is FINAL: no fallthrough to a guess.
        root = _resolved(Path(env_raw))
        root_source = "env"
        searched.append(str(root))
    else:
        partial: Optional[Path] = None
        for cand in candidate_roots():
            searched.append(str(cand))
            if _has_markers(cand, CPP_MARKERS):
                root, root_source = cand, "derived"
                break
            if partial is None and _has_markers(cand, SUPERVISOR_MARKERS):
                # Carries the supervisor half only. Remember it so the *supervisor* contract
                # can still be satisfied and the CPP failure stays precise.
                partial = cand
        if root is None and partial is not None:
            root, root_source = partial, "derived"

    if packaged:
        cpp_mode = "packaged"
    elif _has_markers(root, CPP_MARKERS):
        cpp_mode = "control_root_env" if root_source == "env" else "derived_local"
    else:
        cpp_mode = "unresolved"

    _RESOLUTION = Resolution(cpp_mode=cpp_mode, control_root=root, root_source=root_source,
                             searched=tuple(searched), env_control_root=env_raw,
                             packaged_cpp=packaged)
    return _RESOLUTION


# --------------------------------------------------------------------------- diagnostics
_REMEDIES = {
    "cpp": (
        "install the provider as a distribution so `import cpp` works "
        "(target state: the `cnfa-cpp` package pinned in this repo's requirements)",
        "export CONTROL_ROOT=<provider checkout containing cpp/ and supervisor/>",
        "place the provider checkout beside this repository as <ancestor>/_control",
    ),
    "supervisor": (
        "install/expose the provider's supervisor package so `import trusted_derivation` works",
        "export CONTROL_ROOT=<provider checkout containing supervisor/trusted_derivation.py>",
        "place the provider checkout beside this repository as <ancestor>/_control",
    ),
}


def _diagnostic(contract: str, key: str, missing: Sequence[str], res: Resolution,
                cause: Optional[BaseException] = None) -> str:
    """The single fail-closed diagnostic: what is missing, where we looked, what to do."""
    root = "(none located)" if res.control_root is None else str(res.control_root)
    lines = [
        f"annotation_socket: required provider contract unavailable — {contract}",
        f"  missing        : {', '.join(missing) if missing else '(import failed)'}",
        f"  provider root  : {root}   [source: {res.root_source}]",
        f"  CONTROL_ROOT   : {res.env_control_root!r}",
        f"  packaged `cpp` : {res.packaged_cpp}",
        f"  consumer root  : {CONSUMER_ROOT}",
    ]
    if cause is not None:
        lines.append(f"  underlying     : {type(cause).__name__}: {cause}")
    lines.append("  searched       :")
    lines.extend(f"      {c}" for c in (res.searched or ("(no candidates)",)))
    lines.append("  remedies       :")
    lines.extend(f"      {i}. {r}" for i, r in enumerate(_REMEDIES[key], 1))
    if res.root_source == "env":
        lines.append("  note           : CONTROL_ROOT was set explicitly, so it was the only "
                     "candidate — this resolver never falls through to a guess.")
    return "\n".join(lines)


# --------------------------------------------------------------------------- CPP bootstrap
_BOOTSTRAPPED = False


def ensure_consumer_root_importable() -> Path:
    """Make this checkout importable (`annotation_socket`, `cnfa_algs`) irrespective of cwd.

    Appended, not prepended: running from the repository root already works via the cwd entry,
    so this is a safety net for out-of-tree invocation and must not silently outrank whatever
    the operator put earlier on sys.path.
    """
    root_s = str(CONSUMER_ROOT)
    if root_s not in sys.path:
        sys.path.append(root_s)
    return CONSUMER_ROOT


def bootstrap(*, refresh: bool = False) -> Resolution:
    """Make `from cpp import ...` work, or fail closed with one diagnostic. Idempotent."""
    global _BOOTSTRAPPED
    res = resolve(refresh=refresh)
    ensure_consumer_root_importable()

    if _BOOTSTRAPPED and not refresh:
        return res

    if res.cpp_mode == "packaged":
        # The provider is already importable. Deliberately no sys.path surgery and no call to
        # cpp.locate.bootstrap(): with CONTROL_ROOT unset that helper would append the
        # provider's OWN default root, which is exactly the host path this module removes.
        _BOOTSTRAPPED = True
        return res

    missing = _missing_markers(res.control_root, CPP_MARKERS)
    if missing:
        raise CppBootstrapError(_diagnostic(CPP_CONTRACT, "cpp", missing, res),
                                contract=CPP_CONTRACT)

    root = res.control_root
    assert root is not None                       # implied by the empty `missing` above
    # Pin CONTROL_ROOT to the root WE resolved before handing control to the provider, so the
    # provider's built-in default can never fire. Then seed sys.path just enough that its own
    # bootstrap helper is importable, and let the provider define bootstrap semantics.
    os.environ[CONTROL_ROOT_ENV] = str(root)
    root_s = str(root)
    if root_s not in sys.path:
        sys.path.insert(0, root_s)
    try:
        from cpp import locate as _cpp_locate      # noqa: E402  (only importable post-seed)
        booted = Path(_cpp_locate.bootstrap())     # the provider's sanctioned entry point
    except Exception as exc:                       # provider present but unusable
        raise CppBootstrapError(
            _diagnostic(CPP_CONTRACT, "cpp", ["cpp.locate.bootstrap() failed"], res, cause=exc),
            contract=CPP_CONTRACT) from exc

    if _resolved(booted) != _resolved(root):
        raise CppBootstrapError(
            _diagnostic(CPP_CONTRACT, "cpp",
                        [f"cpp.locate.bootstrap() returned {booted}, expected {root}"], res),
            contract=CPP_CONTRACT)

    _BOOTSTRAPPED = True
    return res


def import_stage():
    """The CPP stage module. Bootstraps first; fail-closed on anything unusable."""
    bootstrap()
    res = resolve()
    try:
        from cpp import stage                      # noqa: E402  (post-bootstrap by contract)
    except Exception as exc:
        raise CppBootstrapError(
            _diagnostic(CPP_CONTRACT, "cpp", ["cpp.stage import failed"], res, cause=exc),
            contract=CPP_CONTRACT) from exc
    if not hasattr(stage, "ensure_stage"):
        raise CppBootstrapError(
            _diagnostic(CPP_CONTRACT, "cpp",
                        ["cpp.stage.ensure_stage (imported `cpp` is not the CPP reference)"], res),
            contract=CPP_CONTRACT)
    return stage


# --------------------------------------------------------------------------- supervisor half
def supervisor_dir() -> Path:
    """Directory holding the provider's supervisor modules, or fail closed."""
    res = resolve()
    missing = _missing_markers(res.control_root, SUPERVISOR_MARKERS)
    if missing:
        raise CppBootstrapError(_diagnostic(SUPERVISOR_CONTRACT, "supervisor", missing, res),
                                contract=SUPERVISOR_CONTRACT)
    assert res.control_root is not None
    return res.control_root / "supervisor"


def _load_provider_module(module_name: str, required_attr: str):
    """Import a provider module, preferring an already-importable one — but only if it really
    carries the attribute the contract is about.

    The guard matters: `supervisor` is also the name of an unrelated PyPI process manager, and
    silently accepting it would satisfy the import while breaking the contract. When the
    ambient module fails the check we load the provider's file directly under a private,
    namespaced module name rather than mutating `sys.modules[module_name]` out from under
    whoever else imported it.
    """
    ambient = sys.modules.get(module_name)
    if ambient is None:
        try:
            ambient = importlib.import_module(module_name)
        except Exception:
            ambient = None
    if ambient is not None and hasattr(ambient, required_attr):
        return ambient

    private_name = f"{__name__}._provider_{module_name}"
    cached = sys.modules.get(private_name)
    if cached is not None and hasattr(cached, required_attr):
        return cached

    directory = supervisor_dir()                    # fail-closed
    path = directory / f"{module_name}.py"
    res = resolve()
    if not _is_file(path):
        raise CppBootstrapError(
            _diagnostic(SUPERVISOR_CONTRACT, "supervisor", [f"supervisor/{module_name}.py"], res),
            contract=SUPERVISOR_CONTRACT)

    # Sibling provider modules import each other by bare name; make the directory reachable.
    dir_s = str(directory)
    if dir_s not in sys.path:
        sys.path.insert(0, dir_s)
    try:
        spec = importlib.util.spec_from_file_location(private_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"no loader for {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[private_name] = module
        spec.loader.exec_module(module)
    except Exception as exc:
        sys.modules.pop(private_name, None)
        raise CppBootstrapError(
            _diagnostic(SUPERVISOR_CONTRACT, "supervisor",
                        [f"supervisor/{module_name}.py failed to load"], res, cause=exc),
            contract=SUPERVISOR_CONTRACT) from exc

    if not hasattr(module, required_attr):
        raise CppBootstrapError(
            _diagnostic(SUPERVISOR_CONTRACT, "supervisor",
                        [f"supervisor/{module_name}.py has no `{required_attr}`"], res),
            contract=SUPERVISOR_CONTRACT)
    return module


def import_supervisor():
    """The provider's supervisor module (death classification / progress watchdog)."""
    return _load_provider_module("supervisor", "classify_result")


def trusted_unknown() -> str:
    """The UNKNOWN sentinel, taken from the provider's trusted_derivation chokepoint.

    There is deliberately NO local fallback. Inventing a private `"UNKNOWN"` string when the
    provider is missing forks the trust vocabulary into two sentinels that merely happen to
    compare equal today — and the whole point of the chokepoint is that one authority defines
    it. Absent provider => hard failure, not a lookalike.
    """
    module = _load_provider_module("trusted_derivation", "UNKNOWN")
    value = getattr(module, "UNKNOWN", None)
    if not isinstance(value, str) or not value.strip():
        raise CppBootstrapError(
            _diagnostic(SUPERVISOR_CONTRACT, "supervisor",
                        [f"trusted_derivation.UNKNOWN is {value!r}, expected a non-empty str"],
                        resolve()),
            contract=SUPERVISOR_CONTRACT)
    return value


# --------------------------------------------------------------------------- subprocess env
_UNSET = object()


def worker_env(base_env: Optional[Mapping[str, str]] = None, *,
               consumer_root: Optional[Path] = None,
               control_root=_UNSET,
               extra: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
    """Environment for a child process that must `import annotation_socket` (and `cpp`).

    This is the portable replacement for embedding a source-tree path inside a `python -c`
    string: the child receives PYTHONPATH and CONTROL_ROOT, so the code it runs carries no
    path at all and the layout is a property of the environment, not of the source.

    Limitation, stated rather than hidden: PYTHONPATH is `os.pathsep`-delimited, so a checkout
    whose path contains `os.pathsep` (`:` on POSIX) cannot be expressed. Spaces are fine.
    """
    env: Dict[str, str] = dict(os.environ if base_env is None else base_env)

    root = resolve().control_root if control_root is _UNSET else control_root
    consumer = Path(consumer_root) if consumer_root is not None else CONSUMER_ROOT

    parts: List[str] = [str(consumer)]
    if root is not None:
        parts.append(str(root))
        env[CONTROL_ROOT_ENV] = str(root)

    for existing in (env.get("PYTHONPATH") or "").split(_PATH_LIST_SEP):
        if existing:
            parts.append(existing)

    ordered: List[str] = []
    seen = set()
    for part in parts:
        if part not in seen:
            seen.add(part)
            ordered.append(part)
    env["PYTHONPATH"] = _PATH_LIST_SEP.join(ordered)

    if extra:
        env.update({str(k): str(v) for k, v in extra.items()})
    return env


# --------------------------------------------------------------------------- CLI diagnostic
def _main() -> int:
    import json
    res = resolve()
    report = {"resolution": res.as_dict(), "consumer_root": str(CONSUMER_ROOT),
              "candidates": [str(c) for c in candidate_roots()]}
    for name, fn in (("cpp", lambda: bool(import_stage())),
                     ("supervisor", lambda: bool(import_supervisor())),
                     ("trusted_unknown", trusted_unknown)):
        try:
            report[name] = fn()
        except CppBootstrapError as exc:
            report[name] = f"FAIL: {exc}"
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(_main())
