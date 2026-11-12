"""The schemas of the kinds of integration whose tool a project brings itself: what their settings are called, and what
kind each is, for a project that has no tool of its own for that kind yet (and for callboard.toml to be read at all
where the tool isn't at hand).

A kind's schema is its tool's SCHEMA (callboard/policy.py's ``schema``): the tool that's running, else the project's own
(tests/run.py, dev/<tool>.py), else the one this install ships (callboard/checks.py, callboard/coverage.py), else the one
here. These are as Plex Cache's tools have them, where they came from; a project's own tool's SCHEMA always wins.
"""

from callboard.policy import Schema, Setting

TESTS = Schema("tests", "Tests", {
    "failures": Setting("level", "a test that failed (or errored)"),
    "warnings": Setting("level", "a warning the run printed"),
    "skipped": Setting("level", "a test skipped"),
}, "A run of the test suite.")

AUDIT = Schema("audit", "Security Audit", {
    "grace_days": Setting("window", "code no audit has seen may wait this many days", unit="days"),
    "grace_share": Setting("threshold", "…or until it's this share of the app code", unit="%"),
    "unaudited": Setting("level", "code no audit has seen, past its grace (and sensitive code, at once)"),
    "findings": Setting("level", "an open finding"),
    "config": Setting("level", "the private rules.toml's requirements missing or unreadable"),
    "release_rules": Setting("level", "the release rules (a full audit accepted and fresh, the candidate soaked, nothing open that blocks)", full_only=True),
    "unknown": Setting("level", "a rule that needs the private audits repo, where there isn't one"),
    "changed": Setting("level", "changed lines no audit has seen (diff mode)"),
}, "Which app code the security audits have seen, and the release rules.")

I18N = Schema("i18n", "Translations", {
    "targets": Setting("targets", "each language's share of the texts translated (a code, a group, or \"*\" for the rest)", unit="%"),
    "unused": Setting("level", "catalog entries the code no longer uses, and texts the catalogs haven't got yet (what sync fixes)"),
    "present": Setting("level", "a text added since the gate's base not translated in every catalog (diff mode)"),
}, "How far the translation catalogs are, and whether they're in step with the code.")

RELEASE = Schema("release", "Release checks", {
    "version": Setting("level", "the version a new X.Y.0 above what's released, not tagged yet"),
    "translations": Setting("level", "every text translated in every language"),
    "mqtt_settings": Setting("level", "every setting a control over MQTT, or listed as kept off it"),
    "mqtt_docs": Setting("level", "the README's MQTT topics and commands the ones the code has"),
    "coverage": Setting("level", "the coverage bars of the release role met", full_only=True),
    "audits": Setting("level", "the security audits' release rules met", full_only=True),
    "looks": Setting("level", "every look approved into the style guide"),
    "change_notes": Setting("level", "a change note (a file under notes_dir) written since the last release"),
    "manual": Setting("level", "every manual release item (manual_items) ticked, on the UI's Gates page"),
    "manual_items": Setting("list", "what a person does for a release, each ticked in the UI before it goes"),
    "notes_dir": Setting("text", "where the change notes are written as the work goes (changes)"),
}, "What has to be true before the code is released.")

UPKEEP = Schema("upkeep", "Dependencies", {
    "behind": Setting("level", "new versions upstream"),
    "cves": Setting("level", "CVEs to act on"),
    "stale_days": Setting("window", "days a CVE may go without a fix (or a fix without reaching us) before it's ours to act on", unit="days"),
    "dormant_days": Setting("window", "days without an upstream release: no fix is coming", unit="days"),
    "debian_grace_days": Setting("window", "days after a Debian fix before an image without it is shown", unit="days"),
    "review_days": Setting("window", "days a decision on a CVE stands before it's shown again", unit="days"),
    "move": Setting("text", "what upkeep moves itself here: all, minor or none"),
}, "The dependencies: what's current, what's behind, and the CVEs.")

STYLE = Schema("style", "Wardrobe", {
    "waiting": Setting("level", "looks not in the style guide, waiting for approval"),
}, "The looks the app wears, against the style guide.")

BY_KIND = {s.kind: s for s in (TESTS, AUDIT, I18N, RELEASE, UPKEEP, STYLE)}
