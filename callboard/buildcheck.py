#!/usr/bin/env python3
"""Build Validation, as GitHub runs it: what builds and ships the app, checked — the shell script (ShellCheck on
bin/callboard), the workflows (actionlint on .github/workflows, with ShellCheck on each step's script) and the Dockerfile
(hadolint, .hadolint.yaml), each at its version in dev/tools.toml.

    callboard tool buildcheck

All three run through callboard/checks.py, the code every check tool shares: each fetched at its version the first time (into
~/.cache/plex-cache/tools/), what they find said one way (file:line:column - severity: message (Tool CODE)), then the
result line every dev tool says ("0 ShellCheck findings · 0 actionlint findings · 0 hadolint findings"). On callboard's board
(CALLBOARD_PROGRESS=feed: its Build Validation section) its bar is the files checked. Every finding counts, ShellCheck's
and hadolint's notes and style too: they're kept at zero, fixed in the code; a rule wrong for a line says so there
(``# shellcheck disable=SC… — why``), and a rule is only turned off (.hadolint.yaml) with the maintainer's say. Exit 0
clean, 1 something found, else one of them couldn't run.
"""

import os
import re
import sys

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # (the callboard install: its ``callboard`` package is this folder)
if HOME not in sys.path:
    sys.path.insert(0, HOME)
from callboard import home  # noqa: E402 — where the install is, and the project being checked

ROOT = home.on_path()   # (the project: the folder with the callboard.toml, the code a check reads)
from callboard import checks  # noqa: E402 — the check tools' shared code
from callboard.checks import Check, Finding, Outcome  # noqa: E402


def shell_scripts() -> list[str]:
    """Every shell script the project has: a file named .sh or .bash, or one whose first line says sh or bash runs it."""
    out = []
    for f in checks.project_files("*"):
        try:
            with open(os.path.join(ROOT, f), "rb") as fh:
                first = fh.readline(80)
        except OSError:
            continue
        if f.endswith((".sh", ".bash")) or re.match(rb"#!.*\b(ba)?sh\b", first):
            out.append(f)
    return out


SCRIPTS = shell_scripts()   # (the project's shell scripts, every one there is)
WORKFLOWS = os.path.join(".github", "workflows")
DOCKERFILES = checks.project_files("Dockerfile*")
HADOLINT_CONFIG = ".hadolint.yaml"
LEVELS = {"error": "error", "warning": "warning", "info": "information", "style": "information"}


def shellcheck_findings(got: dict) -> list[Finding]:
    return [Finding("ShellCheck", c.get("file", ""), int(c.get("line") or 0), int(c.get("column") or 0),
                    LEVELS.get(c.get("level", ""), "warning"), str(c.get("message", "")), f"SC{c.get('code')}")
            for c in got.get("comments") or []]


def shellcheck() -> Outcome:
    version = checks.version("shellcheck")
    cmd, why = checks.command("shellcheck")
    if not cmd:
        return Outcome("ShellCheck", version, None, why)
    got, run = checks.json_out([*cmd, "--format=json1", "--external-sources", *SCRIPTS])
    if not isinstance(got, dict) or run.returncode not in (0, 1):
        return Outcome("ShellCheck", version, None, f"ShellCheck didn't run: {checks.last_line(run)}")
    return Outcome("ShellCheck", version, shellcheck_findings(got))


def actionlint_findings(got: list) -> list[Finding]:
    return [Finding("actionlint", f.get("filepath", ""), int(f.get("line") or 0), int(f.get("column") or 0), "error",
                    str(f.get("message", "")), str(f.get("kind", ""))) for f in got]


def actionlint() -> Outcome:
    version = checks.version("actionlint")
    cmd, why = checks.command("actionlint")
    if not cmd:
        return Outcome("actionlint", version, None, why)
    sc, why = checks.command("shellcheck")   # (each step's script checked as ShellCheck checks bin/callboard)
    if not sc:
        return Outcome("actionlint", version, None, why)
    got, run = checks.json_out([*cmd, "-format", "{{json .}}", "-shellcheck", sc[0], "-pyflakes", ""])
    if not isinstance(got, list) or run.returncode not in (0, 1):
        return Outcome("actionlint", version, None, f"actionlint didn't run: {checks.last_line(run)}")
    return Outcome("actionlint", version, actionlint_findings(got))


def hadolint_findings(got: list) -> list[Finding]:
    return [Finding("hadolint", f.get("file", ""), int(f.get("line") or 0), int(f.get("column") or 0),
                    LEVELS.get(f.get("level", ""), "warning"), str(f.get("message", "")), str(f.get("code", ""))) for f in got]


def hadolint() -> Outcome:
    version = checks.version("hadolint")
    cmd, why = checks.command("hadolint")
    if not cmd:
        return Outcome("hadolint", version, None, why)
    config = ["--config", HADOLINT_CONFIG] if os.path.isfile(os.path.join(ROOT, HADOLINT_CONFIG)) else []
    got, run = checks.json_out([*cmd, *config, "--format", "json", "--no-color", *DOCKERFILES])
    if not isinstance(got, list) or run.returncode not in (0, 1):
        return Outcome("hadolint", version, None, f"hadolint didn't run: {checks.last_line(run)}")
    return Outcome("hadolint", version, hadolint_findings(got))


def main() -> int:
    workflows = checks.project_files("*.yml", "*.yaml", under=(WORKFLOWS,))
    # (each check only where the project has something for it: a project without a Dockerfile has no hadolint to run)
    todo = [Check("ShellCheck", shellcheck, lambda: list(SCRIPTS))] if SCRIPTS else []
    todo += [Check("actionlint", actionlint, lambda: workflows)] if workflows else []
    todo += [Check("hadolint", hadolint, lambda: list(DOCKERFILES))] if DOCKERFILES else []
    return checks.run(todo, bar="build", facts=None if todo else ["no shell script, workflow or Dockerfile to check"])


if __name__ == "__main__":
    sys.exit(main())
