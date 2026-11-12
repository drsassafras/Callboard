#!/usr/bin/env python3
"""The callboard UI's copy of Dionysus's themes (Plex Cache's: Classic and Dionysus, light and dark), taken again.

    python3 callboard/ui/refresh.py ~/Code/TrueNAS-Plex-Caching

The UI wears the app's themes, but callboard is its own project: it ships a copy (this folder), so it needs no Plex Cache
beside it. What's copied, from that checkout: the themes' CSS and the script that picks one (plexcache/themes.py's, as
the app serves them with no custom themes), the app's stylesheet, the script that draws the decorations and the fonts
(static/), and app.js's identicon. Run it when the app's look has moved on and the UI should follow; commit what changed.
"""

import importlib
import os
import re
import shutil
import sys


def main(args: list[str]) -> int:
    if len(args) != 1 or not os.path.isdir(os.path.join(args[0], "plexcache", "web")):
        print((__doc__ or "").split("\n\n")[1])
        return 2
    src = os.path.realpath(args[0])
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, src)
    themes = importlib.import_module("plexcache.themes")   # (that checkout's, on the path just above)
    web = os.path.join(src, "plexcache", "web")

    def write(name: str, text: str):
        with open(os.path.join(here, name), "w", encoding="utf-8") as fh:
            fh.write(text)
    write("themes.css", themes.css(None))
    write("theme.js", themes.script(None))
    with open(os.path.join(web, "app.js"), encoding="utf-8") as fh:
        got = re.search(r"\n( *)function stIdenticon\(id\) \{\n.*?\n\1\}\n", fh.read(), re.S)
    if got is None:
        print("app.js has no stIdenticon(id)")
        return 1
    write("identicon.js", got.group(0).strip() + "\n")
    static = os.path.join(here, "static")
    shutil.rmtree(static, ignore_errors=True)
    for name, path in {"static/app.css": os.path.join(web, "app.css"), **themes.files(web)}.items():
        os.makedirs(os.path.dirname(os.path.join(here, name)), exist_ok=True)
        shutil.copyfile(path, os.path.join(here, name))
    print(f"copied the themes from {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
