# Test Cases: <Feature name>

> Copy this file into `docs/<test-plan-folder>/test-cases.md` and fill it in.
> Delete the guidance blockquotes once you're done.
>
> Section 4 is pushed to TestRail through the `testrail` MCP server. Every field it uses
> maps to one TestRail field (see the mapping in
> [agents/rules/testrail.md](../../agents/rules/testrail.md)), so keep the field names and
> table layouts exactly as they are here. Sections 1–3 and 5 stay in this repo only.

| Field            | Value                                            |
| ---------------- | ------------------------------------------------ |
| Feature          | <e.g. Create task (`POST /tasks`)>               |
| Requirements     | <REQ-IDs covered, e.g. REQ-TASK-01..05>          |
| TestRail section | <Project / Suite / Section path, or `S<id>`>     |
| Author           | <name>                                           |
| Created / Updated| <YYYY-MM-DD> / <YYYY-MM-DD>                      |
| Version          | <doc version, e.g. 1.0>                          |
| SUT version      | <app version / commit, e.g. TaskApp 0.1.0>       |
| Environment      | <local / docker / CI>                            |

## 1. Scope

**In scope:** <what behaviour these cases cover>

**Out of scope:** <what you deliberately don't test here, and why>

## 2. Test design

> List each rule, then the technique you applied and the classes/boundaries you derived.
> Every row should map to at least one case below. Unclear behaviour is answered by the
> PO/dev *before* it lands here: the answer becomes a rule, not an open question.

| Req      | Rule |
| -------- | ---- |
| <REQ-ID> | <exact rule: type, limits, default, status codes> |

| Input / rule | Technique | Valid classes / boundaries | Invalid classes / boundaries |
| ------------ | --------- | -------------------------- | ---------------------------- |
| <field>      | <EP / BVA / decision table / state transition / error guessing> | <...> | <...> |

## 3. Test data

> Shared data, accounts, keys and how data is created and cleaned up.

## 4. Test cases

> **Rules for writing a case**
> - One behaviour per case. If the title needs "and", split it.
> - Title format: `<action> <condition> <expected outcome>`. It becomes the TestRail title,
>   so it must make sense on its own (no "see above").
> - Expected results must be observable and specific: status code, fields, values.
>   Never write "works correctly" or "should succeed".
> - Cases are independent: each one creates its own data and cleans up. Cleanup is the
>   **last step** (TestRail has no postconditions field).
> - No conditional steps ("if 201, then..."). Split positive and negative cases instead.
> - ID format: `TC-<FEATURE>-<NNN>`. IDs are never reused, even after a case is deleted.
> - Priority: P1 = core flow / data loss, P2 = important validation, P3 = edge / cosmetic.
> - Status: Draft → Ready (reviewed). Only `Ready` cases are pushed. Run results
>   (Passed / Failed / Blocked) live in TestRail runs, not here.
> - Automation: `Automated → <path>::<test name>[<param id>]`, `Not automated` or `Won't automate (<why>)`.
> - TestRail: `C<id>` once pushed, otherwise `Not synced`.
> - `Defect: <link>` and `Notes:` lines under a case stay in the repo; they are not pushed.

### TC-<FEATURE>-001: <action> <condition> <expected outcome>

| Field       | Value                                        |
| ----------- | -------------------------------------------- |
| Requirement | <REQ-ID>                                     |
| Type        | <Functional / Negative / Security / ...>     |
| Technique   | <EP / BVA / ...>                             |
| Priority    | <P1 / P2 / P3>                               |
| Level       | <Unit / API / UI / E2E>                      |
| Automation  | <Automated → path::test / Not automated>     |
| TestRail    | <C1234 / Not synced>                         |
| Status      | <Draft / Ready>                              |

**Preconditions:** <state the system must be in>

**Test data:** <exact payload / params>

| # | Step   | Expected result |
| - | ------ | --------------- |
| 1 | <step> | <expected>      |
| 2 | <cleanup step> | <expected> |

---

> **Compact form for data-driven cases.** Use it when cases only differ by input and
> expected result. The shared steps use `{input}` and `{expected}` placeholders; each row
> is pushed as its own TestRail case with the placeholders filled in. All rows in one
> table share Type, Technique, Level, Preconditions and steps.

### <field>: <valid / invalid> values

| Field         | Value      |
| ------------- | ---------- |
| Type          | <...>      |
| Technique     | <EP / BVA> |
| Level         | <API>      |

**Preconditions:** <...>

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | <step using `{input}`> | `{expected}` |
| 2 | <cleanup step> | <expected> |

| ID               | Title   | Requirement | Input   | Expected        | Priority | Automation | Status | TestRail   |
| ---------------- | ------- | ----------- | ------- | --------------- | -------- | ---------- | ------ | ---------- |
| TC-<FEATURE>-0NN | <title> | <REQ-ID>    | <value> | <status / body> | P2       | <...>      | Draft  | Not synced |

## 5. Traceability

| Requirement | Test cases | Automated tests | Defects |
| ----------- | ---------- | --------------- | ------- |
| <REQ-ID>    | <TC-IDs>   | <test names>    | <links> |
