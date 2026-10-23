# Rule: syncing test cases with TestRail

Agents reach TestRail through the `testrail` MCP server configured in
[.mcp.json](../../.mcp.json). Credentials live in `.env` (gitignored; template in
[.env.example](../../.env.example)), which the server loads itself. Agents never read `.env`.

- The markdown in `docs/` is the **source of truth**. TestRail mirrors it, never the
  other way round. If the two disagree, report it; don't silently overwrite either side.
- Each case links to TestRail through its `TestRail` field (`C<id>`, or `Not synced`).
- **Reading** is always allowed: projects, suites, sections, cases.
- **Pushing** (create or update) is allowed only for cases with status `Ready`, and only
  after showing the user what will be sent (new cases, changed fields) and getting a yes.
  After pushing, write the TestRail ID back into the case's `TestRail` field.
- **Never delete** anything in TestRail (cases, sections, runs) through an agent.
  `deleteCase` and `deleteSection` are also denied in `.claude/settings.json`.
- The server passes parameters straight to the TestRail API without validating them.
  Call `getCaseFields` (and `getCaseTypes`) before the first push in a session so the
  payload matches the project's template and required custom fields; a 400 usually means
  a missing or wrong field.
- Never print, log or commit the TestRail URL credentials or API key.

## Markdown → TestRail field mapping

Cases use the "Test Case (Steps)" template (`template_id = 2`). Project: Lifecycle (`1`),
suite: Master (`1`), single-suite mode. One markdown case = one TestRail case; each
row of a compact table is its own case, with `{input}` / `{expected}` filled into the
shared steps.

| Markdown                      | TestRail field              | Notes |
| ----------------------------- | --------------------------- | ----- |
| Header `TestRail section`     | `section_id`                | Resolve the path with `getSections`; create missing sections only after confirmation |
| Case title (after `TC-…:`)    | `title`                     | Compact form: the `Title` column |
| Case ID `TC-…`                | `refs` (with Requirement)   | `refs = "TC-CREATE-001, REQ-CREATE-01"`: lets an update find the case again |
| `Requirement`                 | `refs`                      | Comma-separated |
| `Type`                        | `type_id`                   | Match by name with `getCaseTypes`. No "Negative" type exists: use Functional (6); Security is 10 |
| `Priority`                    | `priority_id`               | P1 → Critical, P2 → High, P3 → Medium (default IDs 4 / 3 / 2; check the instance) |
| `Preconditions` + `Test data` | `custom_preconds`           | Test data and the automated test path appended as `**Test data:**` / `**Automated test:**` lines |
| Steps table                   | `custom_steps_separated`    | `[{"content": Step, "expected": Expected result}]` |
| `Automation`                  | `custom_case_is_automated`  | Checkbox: `true` for `Automated → …`, else `false`. The test path goes in `custom_preconds` (`refs` is too short). `custom_automation_type` is not used (only None / Ranorex) |
| `Technique`, `Level`, `Status`, `Defect` | (not pushed)     | Repo-only |

Updating a case that already has a `TestRail` ID uses `updateCase` with that ID. A case
with `Not synced` uses `addCase`, then the new `C<id>` goes back into the markdown.
- If the `testrail` tools aren't available (server not connected, missing env vars),
  say so and carry on with the markdown only. Don't work around it with raw HTTP calls.
