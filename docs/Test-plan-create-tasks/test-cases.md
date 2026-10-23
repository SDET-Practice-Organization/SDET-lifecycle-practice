# Test Cases: Create task (`POST /tasks`)

| Field             | Value                                   |
| ----------------- | --------------------------------------- |
| Feature           | Create task (`POST /tasks`)             |
| Requirements      | REQ-CREATE-01..06 (see section 2)       |
| TestRail section  | Lifecycle / Master / Tasks API / Create task (POST /tasks) (`S2`) |
| Author            | gabrielAOR                              |
| Created / Updated | 2026-10-23 / 2026-10-23 (pushed to TestRail 2026-10-23) |
| Version           | 1.2                                     |
| SUT version       | TaskApp 0.1.0                           |
| Environment       | local (`uvicorn app.main:app`) / docker |

## 1. Scope

**In scope:** creating a task through `POST /tasks`: field validation, defaults, response
shape, persistence (the task can be read back) and authentication.

**Out of scope:** listing/search/pagination, `PATCH` and `DELETE` (separate test plans),
performance and concurrency (Phase 5 of the roadmap).

## 2. Test design

Requirement IDs are provisional until `docs/requirements.md` exists. They are derived from
`app/models.py::TaskCreate`, the README and the PO answers of 2026-10-23.

| Req           | Rule |
| ------------- | ---- |
| REQ-CREATE-01 | A valid request returns `201` with the created task (id, timestamps, all fields) |
| REQ-CREATE-02 | `title` is required, string, 1–200 characters (not bytes) after trimming surrounding whitespace; duplicate titles are allowed |
| REQ-CREATE-03 | `description` is optional, nullable, max 2000 chars; whitespace-only becomes `null` |
| REQ-CREATE-04 | `priority` is optional integer 1–5, default `3` |
| REQ-CREATE-05 | `status` is optional, one of `todo`, `in_progress`, `done` (any casing, stored lowercase), default `todo`; a task can be created as `done` |
| REQ-CREATE-06 | Unknown fields are rejected; requests without a valid `X-API-Key` get `401` |

| Input / rule  | Technique              | Valid                                         | Invalid                                       |
| ------------- | ---------------------- | --------------------------------------------- | --------------------------------------------- |
| `title`       | EP + BVA               | 1, 2, 199, 200 chars (ASCII, accented, emoji); padded with spaces; duplicate | missing, 0 chars, whitespace only, 201 chars, non-string |
| `description` | EP + BVA               | missing, `null`, 0, 2000 chars, whitespace only (→ `null`) | 2001 chars                       |
| `priority`    | EP + BVA               | missing, 1, 3, 5                              | 0, 6, `"high"`                                |
| `status`      | EP (enum)              | missing, `todo`, `in_progress`, `done`, any casing (`"TODO"`, `"In_Progress"`) | `"blocked"`               |
| body          | Error guessing         | JSON object                                   | form-encoded body, unknown field              |
| `X-API-Key`   | EP                     | correct key                                   | missing, wrong                                |

## 3. Test data

- API key: `dev-key` locally (`TASKAPP_API_KEY`), `ci-key` in CI.
- Titles use a unique tag (e.g. `task t-1a2b3c4d5e`) so cases don't collide on a shared server.
- Every case deletes the tasks it created (`DELETE /tasks/{id}`).

## 4. Test cases

### TC-CREATE-001: Create task with all valid fields returns 201 and echoes them

| Field       | Value |
| ----------- | ----- |
| Requirement | REQ-CREATE-01 |
| Type        | Functional |
| Technique   | Equivalence partitioning |
| Priority    | P1 |
| Level       | API |
| Automation  | Automated → `tests/Python/api/test_tasks_crud.py::test_create_task_returns_201_and_echoes_fields` |
| TestRail    | C1 |
| Status      | Ready |

**Preconditions:** API running, valid `X-API-Key`.

**Test data:**
```json
{"title": "task t-1a2b3c", "description": "created by test", "priority": 5, "status": "in_progress"}
```

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` with the payload | `201 Created` |
| 2 | Inspect the body | `title`, `description`, `priority`, `status` equal the payload; `id` is an integer; `created_at == updated_at` |
| 3 | `GET /tasks/{id}` | `200`, same body as step 2 |
| 4 | `DELETE /tasks/{id}` | `204 No Content` |

**Notes:** catches injected bug `create_returns_200`.

---

### TC-CREATE-002: Create task with only a title applies defaults

| Field       | Value |
| ----------- | ----- |
| Requirement | REQ-CREATE-03, REQ-CREATE-04, REQ-CREATE-05 |
| Type        | Functional |
| Technique   | Equivalence partitioning |
| Priority    | P1 |
| Level       | API |
| Automation  | Automated → `tests/Python/api/test_tasks_crud.py::test_create_applies_defaults` |
| TestRail    | C2 |
| Status      | Ready |

**Preconditions:** API running, valid `X-API-Key`.

**Test data:** `{"title": "only a title"}`

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` with the payload | `201 Created` |
| 2 | Inspect the body | `status = "todo"`, `priority = 3`, `description = null` |
| 3 | `DELETE /tasks/{id}` | `204 No Content` |

---

### TC-CREATE-003: Create task with padded title stores the trimmed title

| Field       | Value |
| ----------- | ----- |
| Requirement | REQ-CREATE-02 |
| Type        | Functional |
| Technique   | Error guessing |
| Priority    | P2 |
| Level       | API |
| Automation  | Automated → `tests/Python/api/test_tasks_crud.py::test_create_strips_title_whitespace` |
| TestRail    | C3 |
| Status      | Ready |

**Preconditions:** API running, valid `X-API-Key`.

**Test data:** `{"title": "  padded  "}`

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` with the payload | `201 Created` |
| 2 | Inspect the body | `title = "padded"` |
| 3 | `DELETE /tasks/{id}` | `204 No Content` |

---

### TC-CREATE-024: Create two tasks with the same title returns two distinct tasks

| Field       | Value |
| ----------- | ----- |
| Requirement | REQ-CREATE-02 |
| Type        | Functional |
| Technique   | Error guessing |
| Priority    | P2 |
| Level       | API |
| Automation  | Not automated |
| TestRail    | Not synced |
| Status      | Draft |

**Preconditions:** API running, valid `X-API-Key`.

**Test data:** `{"title": "task t-1a2b3c dup"}`, sent twice.

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` with the payload | `201 Created`, id `A` |
| 2 | `POST /tasks` with the same payload | `201 Created`, id `B`, `B != A` |
| 3 | `GET /tasks?q=t-1a2b3c dup` | `200`, `total = 2` |
| 4 | `DELETE /tasks/A` and `DELETE /tasks/B` | `204 No Content` for both |

---

### `title`: valid values

| Field     | Value |
| --------- | ----- |
| Type      | Functional |
| Technique | Boundary value analysis |
| Level     | API |

**Preconditions:** API running, valid `X-API-Key`.

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` with `{"title": {input}}` | `{expected}` |
| 2 | `GET /tasks/{id}` | `200`, same `title` as step 1 |
| 3 | `DELETE /tasks/{id}` | `204 No Content` |

| ID            | Title | Requirement | Input | Expected | Priority | Automation | Status | TestRail |
| ------------- | ----- | ----------- | ----- | -------- | -------- | ---------- | ------ | -------- |
| TC-CREATE-007 | Create task with a 1-character title returns 201 | REQ-CREATE-02 | `"a"` | `201`, `title = "a"` | P2 | Not automated | Ready | C6 |
| TC-CREATE-008 | Create task with a 200-character title returns 201 | REQ-CREATE-02 | 200 × `"x"` | `201`, `title` is the input | P2 | Not automated | Ready | C7 |
| TC-CREATE-011 | Create task with a padded 200-character title returns 201 with the trimmed title | REQ-CREATE-02 | `" "` + 200 × `"x"` + `" "` | `201`, `title` = 200 × `"x"` | P3 | Not automated | Ready | C8 |
| TC-CREATE-025 | Create task with a 200-character accented title returns 201 | REQ-CREATE-02 | 200 × `"é"` (400 bytes UTF-8) | `201`, `title` is the input | P2 | Not automated | Draft | Not synced |
| TC-CREATE-027 | Create task with a 200-emoji title returns 201 | REQ-CREATE-02 | 200 × `"😀"` (800 bytes UTF-8) | `201`, `title` is the input | P3 | Not automated | Draft | Not synced |

---

### `title`: invalid values

| Field     | Value |
| --------- | ----- |
| Type      | Negative |
| Technique | Boundary value analysis |
| Level     | API |

**Preconditions:** API running, valid `X-API-Key`.

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` with `{input}` | `422`, `detail` contains location `["body", "title"]` |

| ID            | Title | Requirement | Input | Expected | Priority | Automation | Status | TestRail |
| ------------- | ----- | ----------- | ----- | -------- | -------- | ---------- | ------ | -------- |
| TC-CREATE-004 | Create task without a title returns 422 | REQ-CREATE-02 | `{"description": "no title"}` | `422` | P1 | Automated → `test_tasks_validation.py::test_create_rejects_invalid_payload[missing-title]` | Ready | C9 |
| TC-CREATE-005 | Create task with an empty title returns 422 | REQ-CREATE-02 | `{"title": ""}` | `422` | P2 | Automated → `...[empty-title]` | Ready | C10 |
| TC-CREATE-006 | Create task with a whitespace-only title returns 422 | REQ-CREATE-02 | `{"title": "   "}` | `422` | P2 | Automated → `...[blank-title]` | Ready | C11 |
| TC-CREATE-009 | Create task with a 201-character title returns 422 | REQ-CREATE-02 | `{"title": 201 × "x"}` | `422` | P2 | Automated → `...[title-too-long]` | Ready | C12 |
| TC-CREATE-010 | Create task with a non-string title returns 422 | REQ-CREATE-02 | `{"title": 123}` | `422` | P3 | Automated → `...[title-not-string]` | Ready | C13 |
| TC-CREATE-026 | Create task with a 201-character accented title returns 422 | REQ-CREATE-02 | `{"title": 201 × "é"}` | `422` | P2 | Not automated | Draft | Not synced |

---

### `priority`, `status`, `description`: valid values

| Field     | Value |
| --------- | ----- |
| Type      | Functional |
| Technique | Equivalence partitioning + boundary value analysis |
| Level     | API |

**Preconditions:** API running, valid `X-API-Key`.

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` with `{"title": "task t-1a2b3c"}` plus `{input}` | `{expected}` |
| 2 | `DELETE /tasks/{id}` | `204 No Content` |

| ID            | Title | Requirement | Input | Expected | Priority | Automation | Status | TestRail |
| ------------- | ----- | ----------- | ----- | -------- | -------- | ---------- | ------ | -------- |
| TC-CREATE-013 | Create task with priority 1 returns 201 | REQ-CREATE-04 | `"priority": 1` | `201`, `priority = 1` | P2 | Not automated | Ready | C14 |
| TC-CREATE-014 | Create task with priority 5 returns 201 | REQ-CREATE-04 | `"priority": 5` | `201`, `priority = 5` | P2 | Automated → `test_create_task_returns_201_and_echoes_fields` | Ready | C15 |
| TC-CREATE-017 | Create task with status done returns 201 | REQ-CREATE-05 | `"status": "done"` | `201`, `status = "done"` | P2 | Not automated | Ready | C16 |
| TC-CREATE-028 | Create task with a whitespace-only description stores null | REQ-CREATE-03 | `"description": "   "` | `201`, `description = null` | P2 | Not automated | Draft | Not synced |
| TC-CREATE-029 | Create task with an uppercase status stores it lowercase | REQ-CREATE-05 | `"status": "TODO"` | `201`, `status = "todo"` | P2 | Not automated | Draft | Not synced |
| TC-CREATE-030 | Create task with a mixed-case status stores it lowercase | REQ-CREATE-05 | `"status": "In_Progress"` | `201`, `status = "in_progress"` | P3 | Not automated | Draft | Not synced |

**Defect (TC-CREATE-028):** pending. Code review suggests TaskApp 0.1.0 returns `description = ""`.
**Defect (TC-CREATE-029, 030):** pending. Code review suggests TaskApp 0.1.0 returns `422` (status is case-sensitive).

---

### `priority`, `status`, `description`: invalid values

| Field     | Value |
| --------- | ----- |
| Type      | Negative |
| Technique | Equivalence partitioning + boundary value analysis |
| Level     | API |

**Preconditions:** API running, valid `X-API-Key`.

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` with `{"title": "task t-1a2b3c"}` plus `{input}` | `{expected}` |

| ID            | Title | Requirement | Input | Expected | Priority | Automation | Status | TestRail |
| ------------- | ----- | ----------- | ----- | -------- | -------- | ---------- | ------ | -------- |
| TC-CREATE-012 | Create task with priority 0 returns 422 | REQ-CREATE-04 | `"priority": 0` | `422`, location `["body", "priority"]` | P2 | Automated → `...[priority-below-min]` | Ready | C17 |
| TC-CREATE-015 | Create task with priority 6 returns 422 | REQ-CREATE-04 | `"priority": 6` | `422`, location `["body", "priority"]` | P2 | Automated → `...[priority-above-max]` | Ready | C18 |
| TC-CREATE-016 | Create task with a non-integer priority returns 422 | REQ-CREATE-04 | `"priority": "high"` | `422`, location `["body", "priority"]` | P3 | Automated → `...[priority-not-int]` | Ready | C19 |
| TC-CREATE-018 | Create task with an unknown status returns 422 | REQ-CREATE-05 | `"status": "blocked"` | `422`, location `["body", "status"]` | P2 | Automated → `...[unknown-status]` | Ready | C20 |
| TC-CREATE-019 | Create task with a 2001-character description returns 422 | REQ-CREATE-03 | `"description"`: 2001 × `"x"` | `422`, location `["body", "description"]` | P3 | Automated → `...[description-too-long]` | Ready | C21 |

---

### TC-CREATE-020: Create task with an unknown field is rejected

| Field       | Value |
| ----------- | ----- |
| Requirement | REQ-CREATE-06 |
| Type        | Negative |
| Technique   | Error guessing |
| Priority    | P2 |
| Level       | API |
| Automation  | Automated → `tests/Python/api/test_tasks_validation.py::test_create_rejects_invalid_payload[unknown-field]` |
| TestRail    | C4 |
| Status      | Ready |

**Preconditions:** API running, valid `X-API-Key`.

**Test data:** `{"title": "task t-1a2b3c", "owner": "me"}`

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` with the payload | `422 Unprocessable Entity` |
| 2 | Inspect the body | `detail` contains location `["body", "owner"]` |
| 3 | `GET /tasks?q=t-1a2b3c` | `total = 0`: nothing was created |

---

### TC-CREATE-021: Create task without an API key returns 401

| Field       | Value |
| ----------- | ----- |
| Requirement | REQ-CREATE-06 |
| Type        | Security |
| Technique   | Equivalence partitioning |
| Priority    | P1 |
| Level       | API |
| Automation  | Automated → `tests/Python/api/test_auth.py::test_missing_api_key_is_rejected[POST-/tasks]` |
| TestRail    | C5 |
| Status      | Ready |

**Preconditions:** API running.

**Test data:** `{"title": "x"}`, no `X-API-Key` header.

| # | Step | Expected result |
| - | ---- | --------------- |
| 1 | `POST /tasks` without the header | `401 Unauthorized` |
| 2 | Inspect the body | `{"detail": "Invalid or missing API key"}` |

> Practice: write TC-CREATE-022 (wrong API key) and TC-CREATE-023 (form-encoded body)
> yourself in the full format, then automate the "Not automated" rows above.

## 5. Traceability

| Requirement   | Test cases                         | Automated tests | Defects |
| ------------- | ---------------------------------- | --------------- | ------- |
| REQ-CREATE-01 | TC-CREATE-001                      | `test_create_task_returns_201_and_echoes_fields` | — |
| REQ-CREATE-02 | TC-CREATE-003..011, 024..027       | `test_create_strips_title_whitespace`, `test_create_rejects_invalid_payload` | — |
| REQ-CREATE-03 | TC-CREATE-002, 019, 028            | `test_create_applies_defaults`, `test_create_rejects_invalid_payload` | pending (TC-CREATE-028) |
| REQ-CREATE-04 | TC-CREATE-002, 012..016            | `test_create_applies_defaults`, `test_create_rejects_invalid_payload` | — |
| REQ-CREATE-05 | TC-CREATE-002, 017, 018, 029, 030  | `test_create_applies_defaults`, `test_create_rejects_invalid_payload` | pending (TC-CREATE-029, 030) |
| REQ-CREATE-06 | TC-CREATE-020, 021                 | `test_create_rejects_invalid_payload`, `test_missing_api_key_is_rejected` | — |
