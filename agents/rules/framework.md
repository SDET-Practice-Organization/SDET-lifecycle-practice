# Rule: using the test framework

- Tests never build URLs or headers. They go through `TasksApi` (`framework/client.py`).
  Use `api_client` directly only when the test is about raw HTTP (e.g. a non-JSON body).
- `TasksApi` returns raw `requests.Response` objects. **Tests own every assertion**;
  never add assertions or status checks inside the framework's domain clients.
- Assert status codes with `assert_status(response, <code>)` (`framework/assertions.py`)
  so failures print the request and response.
- Validate response shapes with the contracts in `framework/contracts.py`. Contracts are
  written separately from `app/models.py` on purpose: never import app models into tests
  or the framework.
- Build payloads with `framework/factories.py` (`task_payload(**overrides)`); don't hand-write
  full payloads.
- Every test creates its own data. Use the `create_task` fixture, which deletes what it
  created. If a test creates data some other way, it deletes it.
- Scope listing assertions with a `unique_tag()` in the title, so tests are safe to run in
  parallel (`pytest -n auto`) against a shared server.
- Tests must pass against both the auto-started local app and an external `API_BASE_URL`.
- New fixtures go in the nearest `conftest.py`; new reusable helpers go in `framework/`.
