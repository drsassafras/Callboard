# callboard

One command that checks a project's code — its tests and check tools, all at once on a live board — and, for an app
on a TrueNAS, copies the code there and restarts it. The same checks are the project's **gates** (push, merge,
release), run by hand, by a git hook or on GitHub, and a **UI** in your browser shows each run and what every tool found.

callboard was part of [Plex Cache](https://github.com/drsassafras/TrueNAS-Plex-Caching) (its `dev/` folder, where it was
called devtools, and tnsync before that) and is its own project from version 4.0.0, so every project can use one install.
It needs Python 3.15 and bash; nothing from PyPI. A computer set up for devtools keeps working: its
`~/.config/devtools/config`, its run records and a project's `.devtools` are still read.

The name: a callboard is the notice board by a theatre's stage door, the one place the whole company checks before the
show — who has signed in, the day's calls, the stage manager's notes. Nothing goes on until the board says so.

## Install (once on a computer)

```sh
git clone https://github.com/drsassafras/callboard ~/Code/callboard
mkdir -p ~/bin
ln -sf ~/Code/callboard/bin/callboard ~/bin/callboard   # ~/bin must be on your PATH
```

A project finds the install by `CALLBOARD_HOME` (callboard sets it for every check it runs), else by the `callboard` on
your PATH. `callboard home` prints where it is.

## Use it in a project

```sh
cd ~/Code/my-project
callboard init            # writes callboard.toml (the checks and their rules) and .callboard (this computer's settings)
callboard                 # the checks, on the board
callboard ui              # the same in your browser
callboard gate push       # the checks as the push gate holds them (merge, release likewise)
callboard config show     # every integration's rules as they stand for this code
callboard tool typecheck  # one of callboard's own tools, in the project you're in (buildcheck, coverage…)
```

`callboard.toml`, at the project's root and committed, is the one place that says what's checked and what each finding
is held as (a failure, a warning, a note, or off), by the branch's role and the release phase. `[config]` also names the
project's Python package (`package`, for Coverage), its version file and its cache folder (`cache`: `~/.cache/<name>`).

## What's here

| Path | What it is |
|------|------------|
| `bin/callboard` | The command: the sync to a TrueNAS app, and the run of the checks. |
| `callboard/policy.py`, `starter.toml` | `callboard.toml`, read: the integrations, the roles, each rule. The starter file `callboard init` writes. |
| `callboard/plan.py`, `board.py`, `progress.py` | The plan of a run, the board that draws it, the progress bar and result line every tool shares. |
| `callboard/gate.py` | The gates, and what GitHub runs of them. |
| `callboard/checks.py`, `tools.toml` | What every check tool shares: each tool at one pinned version (a project's own `dev/tools.toml` wins), fetched once, its findings said one way. |
| `callboard/typecheck.py`, `buildcheck.py`, `coverage.py` | Python Validation (pyright, Ruff), Build Validation (ShellCheck, actionlint, hadolint), Coverage. |
| `callboard/devui.py`, `devui.html`, `devui.css`, `devpage.py` | The UI, and what the dev tools' pages share (this computer only, the browser that opened it only). |
| `callboard/notes.py` | Change notes and manual release items: what the Gates page shows and ticks. |
| `callboard/schemas.py` | The rules of the kinds of check a project brings itself (its tests, its release checks…), for when its tool isn't there to say them. |
| `callboard/ui/` | The UI's copy of Dionysus's themes (Plex Cache's look): `refresh.py <Plex Cache checkout>` takes it again. |

## What a project still brings

Its tests (any command), and the tools that are about the project itself. Plex Cache's are in its `dev/`: the
dependency check, the future tests, the translations, the style guide, the release checks and the security audits, each
built on `callboard/checks.py` and `policy.py`. callboard's own tests are still in Plex Cache's suite for now.

## On GitHub

A workflow fetches callboard beside the code, then runs the same commands:

```yaml
- run: |
    git clone --quiet --depth 1 --branch main https://github.com/drsassafras/callboard "$RUNNER_TEMP/callboard"
    echo "CALLBOARD_HOME=$RUNNER_TEMP/callboard" >> "$GITHUB_ENV"
    echo "$RUNNER_TEMP/callboard/bin" >> "$GITHUB_PATH"
- run: callboard gate push --ci
```

## Licence

See `LICENSE`.
