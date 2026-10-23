# Rule: every feature gets a planted bug

From [ROADMAP.md](../../ROADMAP.md): when you add a feature, a test layer or a new kind
of check, also add an injected bug that only that layer can catch.

- Bugs live in `app/bugs.py` (`KNOWN_BUGS`, one-line comment each) and are toggled in
  the app code with `bugs.enabled("<name>")`.
- Names are `snake_case` and describe the defect, e.g. `pagination_off_by_one`.
- The bug must be realistic: something a developer could actually ship, not a crash.
- Add the name to the `bug-detection` matrix in `.github/workflows/ci.yml`.
- With the bug off, the suite passes. With it on, at least one test fails, and the
  failure message makes the cause obvious.
- A layer counts as done only when CI shows it catching its bug.
