"""Where things are: the callboard install (this folder's parent), the project being worked on, and its cache.

callboard is installed once on a computer (a checkout, its ``bin/callboard`` on the PATH) and used by every project that
has a ``callboard.toml`` at its root. So nothing here is found from a tool's own file: a tool's code is the install's,
and the code it checks is the project's.

    HOME        the install (the folder with bin/ and callboard/)
    LIB         its Python (the ``callboard`` package: this folder)
    project()   the project: CALLBOARD_PROJECT when it names a folder, else the nearest folder from here up that has a
                callboard.toml (no higher than the repository's top), else the repository's top, else this folder.
                callboard runs each check in the code it checks (a copy from git has its own callboard.toml), so a
                check's project is the copy.
    cache()     where the project's tools keep what they fetched and saved: CALLBOARD_CACHE, else ~/.cache/<name>, the
                name callboard.toml's [config] cache ("callboard" when it doesn't say)
"""

from __future__ import annotations

import os
import subprocess
import sys

LIB = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.dirname(LIB)
SCRIPT = os.path.join(HOME, "bin", "callboard")
FILE = "callboard.toml"


def version() -> str:
    """The install's version (bin/callboard's CALLBOARD_VERSION)."""
    import re
    try:
        with open(SCRIPT, encoding="utf-8") as fh:
            m = re.search(r'^CALLBOARD_VERSION="([^"]+)"', fh.read(), re.M)
    except OSError:
        return ""
    return m.group(1) if m else ""


def _top(here: str) -> str:
    try:
        got = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=here, capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return os.path.realpath(got.stdout.strip()) if got.returncode == 0 and got.stdout.strip() else ""


def project(start: str | None = None) -> str:
    named = os.environ.get("CALLBOARD_PROJECT", "")
    if named and start is None and os.path.isdir(named):
        return os.path.realpath(named)
    here = os.path.realpath(start or os.getcwd())
    top = _top(here)
    d = here
    while True:
        if os.path.isfile(os.path.join(d, FILE)):
            return d
        if d == top or os.path.dirname(d) == d:
            return top or here
        d = os.path.dirname(d)


def on_path(root: str | None = None) -> str:
    """The install and the project on Python's path (the install first: ``callboard`` is its package; the project's own
    tools are ``dev.…``, its schemas among them). The project."""
    root = root or project()
    if HOME not in sys.path:
        sys.path.insert(0, HOME)
    if root not in sys.path:
        sys.path.insert(1, root)
    return root


def setting(name: str, root: str | None = None) -> str:
    """callboard.toml's [config] ``name`` as text ("" when it isn't set, or there's no file to read)."""
    import tomllib
    path = os.environ.get("CALLBOARD_CONFIG", "")
    if not (path.endswith(".toml") and os.path.isfile(path)) or root is not None:
        path = os.path.join(root or project(), FILE)
    try:
        with open(path, "rb") as fh:
            got = tomllib.load(fh).get("config", {}).get(name, "")
    except (OSError, tomllib.TOMLDecodeError):
        return ""
    return got if isinstance(got, str) else ""


def cache(root: str | None = None) -> str:
    named = os.environ.get("CALLBOARD_CACHE", "")
    if named:
        return named
    name = setting("cache", root)
    if not name or os.sep in name or name.startswith("."):
        name = "callboard"
    return os.path.join(os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"), name)


def env() -> dict[str, str]:
    """What a block's command is given so the project's own tools reach this install: CALLBOARD_HOME, the install on
    Python's path (``from callboard import …``) and its bin first on PATH (``callboard tool …``)."""
    path = os.environ.get("PYTHONPATH", "")
    return {"CALLBOARD_HOME": HOME, "PYTHONPATH": HOME + (os.pathsep + path if path else ""),
            "PATH": os.path.join(HOME, "bin") + os.pathsep + os.environ.get("PATH", "")}
