# Rule: code style

- Python 3.12+, `ruff` config in `pyproject.toml` (line length 100, rules E F I B UP PT).
  Run `ruff check .` and `ruff format .` before finishing.
- Test names say what is checked: `test_<action>_<condition>_<expected>`, e.g.
  `test_create_rejects_invalid_payload`.
- Arrange / act / assert, separated by a blank line. One behaviour per test.
- Use `pytest.mark.parametrize` for data-driven cases and always give readable `ids`
  (`id="title-too-long"`); the ids show up in the test-case `Automation` field.
- Markers are strict (`--strict-markers`). Register new markers in `pyproject.toml`.
  `smoke` = fast core-flow checks, `contract` = response shape checks.
- No `time.sleep` in tests. Poll with a timeout if you have to wait.
- Match the surrounding code: comment only what isn't obvious, keep type hints in
  `framework/`.
