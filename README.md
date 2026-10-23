# QA Lifecycle Lab

End-to-end test automation project: a system under test, a layered Python test
framework, API/contract tests and a CI/CD pipeline. It is built in phases to cover the
full test lifecycle (API → CLI → UI → Kubernetes → AI agents).

## The system under test: TaskApp

A small FastAPI task tracker (`app/`) designed to be tested:

| Endpoint              | Notes                                                     |
| --------------------- | --------------------------------------------------------- |
| `GET /health`         | No auth                                                   |
| `GET /tasks`          | `?status=`, `?q=` (title search), `?limit=`, `?offset=`   |
| `POST /tasks`         | Validation: title 1–200 chars, priority 1–5, status enum  |
| `GET /tasks/{id}`     | 404 when missing                                          |
| `PATCH /tasks/{id}`   | Partial update, rejects nulls and unknown fields          |
| `DELETE /tasks/{id}`  | 204, empty body                                           |

All `/tasks` routes need an `X-API-Key` header (`TASKAPP_API_KEY`, default `dev-key`).
Interactive docs: http://127.0.0.1:8000/docs

### Bug injection

Start the app with `TASKAPP_BUGS=<name>[,<name>]` (or `all`) to plant real defects:
`create_returns_200`, `patch_ignores_status`, `delete_not_persisted`, `filter_ignored`,
`pagination_off_by_one`. CI runs the suite against each one and **fails if the suite
doesn't catch it**. That job tests the tests. When you add a feature, add a bug for it too.

## Framework layout

```
app/                 system under test
framework/
  config.py          settings from env (API_BASE_URL, API_KEY, API_TIMEOUT)
  client.py          ApiClient (HTTP + logging) and TasksApi (domain wrapper)
  contracts.py       strict pydantic models for the expected API contract
  assertions.py      assert_status with request/response context on failure
  factories.py       test data builders
  server.py          starts a local app instance when no API_BASE_URL is given
tests/
  unit/              app logic, no HTTP
  api/               black-box API tests (CRUD, listing, validation, auth, contract)
```

Design rules:
- Tests never build URLs or headers; they go through `TasksApi`.
- Domain clients return raw responses, so the tests own every assertion.
- Every test creates its own data (`create_task` cleans up after itself) and scopes
  listings with a unique tag, so tests are safe to run in parallel against a shared server.
- Contracts are defined separately from the app's models. If the app's models were
  reused, a breaking change would update both sides and the tests would still pass.

## Running locally (Windows / PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt

pytest                        # everything; the API tests start the app automatically
pytest tests/api -m smoke     # smoke only
pytest -n auto                # parallel
pytest --html=reports/report.html --self-contained-html

# Against an already running instance
uvicorn app.main:app --reload            # terminal 1
$env:API_BASE_URL = "http://127.0.0.1:8000"; pytest tests/api   # terminal 2

# Watch the suite catch a bug
$env:TASKAPP_BUGS = "pagination_off_by_one"; pytest tests/api; Remove-Item Env:TASKAPP_BUGS
```

## AI agents and TestRail

Agent roles and rules are in [AGENTS.md](AGENTS.md). Agents can read and push test cases
to TestRail through [`@bun913/mcp-testrail`](https://github.com/bun913/mcp-testrail),
configured in `.mcp.json` (pinned version, started with `npx`, so it needs Node.js ≥ 20.18).
To enable it, copy `.env.example` to `.env` (gitignored) and fill in your TestRail URL,
username and API key (TestRail → My Settings → API Keys). The server loads `.env` when it
starts. Then run `/mcp` in Claude Code to check that `testrail` is connected.

## CI pipeline (`.github/workflows/ci.yml`)

`lint` → `unit` → in parallel:
- `api`: builds the Docker image, runs it, then runs smoke tests and the full suite over
  HTTP and uploads JUnit and HTML reports
- `bug-detection`: a matrix job, one run per injected bug; each run must fail

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full phased plan (QA process → API → data →
contracts → UI → non-functional → CI/CD → Kubernetes → AI).
