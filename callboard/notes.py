"""A project's change notes and manual release items: what the UI's Gates page shows and ticks, and what a project's
release tool checks. One place, so the page and the tool read and write the same files:

* the change notes: the .md files added under the notes folder ([release] notes_dir, "changes") since the last release
  tag, committed or not;
* the manual items: what's ticked of callboard.toml's [release] manual_items for a version, kept beside the notes as
  ``manual-<version>.json``.

Nothing here reads the environment or callboard.toml: the caller says which repository, which folder and which tag.
"""
import json
import os
import subprocess


def git(repo: str, *args: str) -> str | None:
    """git's words for that repository, None when it failed (or isn't there)."""
    try:
        got = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return got.stdout if got.returncode == 0 else None


def change_notes(repo: str, where: str, tag: str) -> list[str]:
    """The change notes written since the last release: the .md files added under the notes folder since the release tag
    (committed or not), in name order."""
    added: set[str] = set()
    if tag:
        got = git(repo, "diff", "--name-only", "--diff-filter=A", f"{tag}..HEAD", "--", where) or ""
    else:
        got = git(repo, "ls-files", "--", where) or ""
    added |= {ln.strip() for ln in got.splitlines() if ln.strip()}
    got = git(repo, "ls-files", "--others", "--exclude-standard", "--", where) or ""
    added |= {ln.strip() for ln in got.splitlines() if ln.strip()}
    return sorted(a for a in added if a.endswith(".md"))


def manual_file(repo: str, where: str, version: str) -> str:
    return os.path.join(repo, where, f"manual-{version}.json")


def manual_state(repo: str, where: str, version: str) -> dict[str, bool]:
    """What's ticked of the manual release items for that version."""
    try:
        with open(manual_file(repo, where, version), encoding="utf-8") as fh:
            got = json.load(fh)
        return {str(k): bool(v) for k, v in got.items()} if isinstance(got, dict) else {}
    except (OSError, ValueError):
        return {}


def tick(repo: str, where: str, version: str, item: str, done: bool = True) -> str:
    """A manual release item ticked (or unticked) for that version, written; what to say of it."""
    state = manual_state(repo, where, version)
    state[item] = done
    path = manual_file(repo, where, version)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=1, sort_keys=True)
    return f"{item}: {'done' if done else 'to do'} for {version} ({os.path.relpath(path, repo)})"
