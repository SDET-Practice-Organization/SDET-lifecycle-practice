# SDET Roadmap

A practice plan for covering the whole QA lifecycle with TaskApp as the system under test.
Each phase builds on the previous one. Do them in order, but don't wait for one to be
perfect before starting the next.

**Rule for every phase:** when you add a feature, a test layer or a new kind of check,
also add an injected bug in `app/bugs.py` that only that layer can catch, and add it to
the `bug-detection` matrix in CI. A layer counts as done when CI shows it catching its bug.

Rough pace is 1–3 weeks per phase, part time.

---

## Phase 0: QA process (the parts that aren't code)

Interviews test this as much as automation. Practise it on TaskApp as if it were a
real product.

- [ ] **Requirements analysis**: write `docs/requirements.md` with user stories and
      acceptance criteria (Given/When/Then) for each endpoint. Find ambiguities: what
      happens with `limit=0`? Is title search accent-insensitive? Is whitespace trimmed?
- [ ] **Test strategy**: `docs/test-strategy.md` covering scope, risks, test levels
      (unit / API / UI / e2e / non-functional), environments, entry and exit criteria,
      and what you deliberately *won't* test.
- [ ] **Test design techniques**: write the cases before automating them, using
      equivalence partitioning, boundary values (title 0/1/200/201 chars, priority 0/1/5/6),
      decision tables (filter + search + pagination) and state transitions (task status).
- [ ] **Exploratory testing**: run three time-boxed charters (e.g. "explore PATCH with
      odd payloads for 30 min") and write session notes.
- [ ] **Defect reporting**: file the real bugs you find as GitHub Issues with a template
      (steps, expected/actual, severity vs priority, environment, evidence).
- [ ] **Traceability**: link requirements to tests to issues (a pytest marker like
      `@pytest.mark.req("TASK-3")` plus a small report script).

**Done when:** a stranger could read `docs/` and know what is tested, why and how.

---

## Phase 1: API framework ✅ (mostly done). Harden it

What's already in place: layered client, contracts, factories, parallel-safe data,
Docker, CI, bug detection. Gaps to close:

- [ ] **Coverage**: `pytest-cov` on the app while the API tests run; publish the report in
      CI and set a floor (e.g. 90%). Learn why 100% line coverage ≠ well tested.
- [ ] **Mutation testing**: `mutmut` on `app/`. It automates what `bugs.py` does by hand.
      Compare its survivors with your manual bug list.
- [ ] **Static quality**: `mypy --strict` on `framework/`, a `pre-commit` config
      (ruff, mypy, trailing whitespace) and a type-checked test codebase.
- [ ] **Reporting**: Allure (`allure-pytest`) with steps, attachments (request/response)
      and history trends published to GitHub Pages.
- [ ] **Flaky test handling**: write a test that's deliberately flaky, detect it with
      `pytest-rerunfailures` + reporting, then fix the root cause. Write down a
      quarantine policy.
- [ ] **Config and environments**: `--env=local|docker|staging` CLI option with
      per-env settings and secrets kept out of the repo.
- [ ] **Data-driven tests**: move boundary cases into parametrized tables / YAML.
- [ ] **New bugs to inject**: `title_not_trimmed`, `search_case_sensitive`,
      `wrong_total_count`.

**Done when:** coverage, mutation score and an Allure report show up on every PR.

---

## Phase 2: Persistence, test data and environments

The in-memory store hides a whole class of bugs. Replace it.

- [ ] Postgres + SQLAlchemy + **Alembic migrations** in the app.
- [ ] `docker-compose.yml`: app + db (+ later the UI), with healthchecks.
- [ ] **Testcontainers** (`testcontainers-python`) so integration tests start a real
      Postgres per session.
- [ ] **Test data management**: factories → DB seeding, cleanup strategies
      (transaction rollback vs truncate vs unique tagging) and when to use each.
- [ ] **DB-level assertions**: verify API writes directly in the DB; test migrations
      upgrade/downgrade on a populated DB.
- [ ] **Concurrency tests**: two PATCHes racing on the same task (add an `updated_at` /
      optimistic locking feature first).
- [ ] **New bugs**: `delete_soft_but_listed`, `migration_drops_column_default`,
      `lost_update`.

**Done when:** `docker compose up` gives you the full stack and CI uses the same file.

---

## Phase 3: Contract and property-based testing

- [ ] **Schemathesis** against `/openapi.json`: fuzz every endpoint and run it in CI.
- [ ] **OpenAPI breaking-change detection**: diff the spec against `main`'s
      (`oasdiff`) and fail the PR on a breaking change.
- [ ] **Build a CLI client** (`taskapp-cli`, Typer) that consumes the API, then:
  - [ ] CLI tests (`typer.testing.CliRunner` + subprocess e2e)
  - [ ] **Pact** consumer-driven contracts: the CLI as consumer, the API as provider,
        with provider verification in CI.
- [ ] **Hypothesis** for the store/business logic (stateful testing: `RuleBasedStateMachine`
      modelling create/update/delete).
- [ ] **New bugs**: a field rename the strict contracts must catch, and a CLI that
      parses an old response shape.

**Done when:** a breaking API change fails CI before any functional test runs.

---

## Phase 4: UI automation

- [ ] Build a small web UI (server-rendered Jinja + htmx is enough, or React if you
      want to practise SPA testing). Add `data-testid` attributes.
- [ ] **Playwright (pytest-playwright)**: page objects or screenplay, fixtures that
      seed data **through the API** (never through the UI), and auth state reuse.
- [ ] Traces, videos and screenshots on failure, uploaded as CI artifacts.
- [ ] Cross-browser matrix (chromium/firefox/webkit) and mobile viewport.
- [ ] **Network mocking**: `page.route` to test error states (500s, slow API).
- [ ] **Visual regression**: Playwright screenshot comparison, and how to manage baselines.
- [ ] **Accessibility**: `axe-playwright-python` checks in CI.
- [ ] Real **end-to-end** journeys (UI → API → DB) kept to a handful. Explain the
      test pyramid in your README using your own numbers.
- [ ] **New bugs**: `button_disabled_after_error`, `wrong_label_aria`, `ui_shows_stale_list`.

**Done when:** the UI suite runs sharded in CI in under 5 minutes with zero flakes over
20 consecutive runs.

---

## Phase 5: Non-functional testing

- [ ] **Performance**: k6 (or Locust) scripts for load, stress, spike and soak.
      Define SLOs (p95 < 200 ms at 50 rps), enforce them as thresholds and run a short
      perf smoke on PRs and a full run nightly.
- [ ] Add an injected `slow_search` bug (N+1 query / sleep) that only the perf test catches.
- [ ] **Security**:
  - [ ] SAST: `bandit`, plus `pip-audit` for dependencies
  - [ ] Container scanning: `trivy` on the image, with the build failing on HIGH/CRITICAL
  - [ ] DAST: OWASP ZAP baseline scan against the running container
  - [ ] Manual API security tests: auth bypass, IDOR (add users/ownership first),
        injection in `q`, oversized payloads, rate limiting (add it and test it)
- [ ] **Resilience / chaos**: Toxiproxy between app and DB (latency, dropped
      connections) and assertions about how the app degrades.

**Done when:** a nightly workflow publishes perf trends and a security report.

---

## Phase 6: CI/CD maturity

- [ ] Pipeline strategy: what runs on PR vs merge vs nightly vs release, and why.
- [ ] Test sharding, caching, `needs`-based parallel stages, reusable workflows /
      composite actions.
- [ ] **Quality gates**: branch protection with required checks; coverage/mutation
      thresholds; no merge with quarantined tests over N days old.
- [ ] **Release pipeline**: semantic versioning, changelog, image pushed to GHCR,
      image signing (cosign), SBOM.
- [ ] **Deploy and verify**: deploy to a staging environment, post-deploy smoke tests,
      automatic rollback on failure.
- [ ] **Test metrics**: track duration, pass rate and flakiness per test over time
      (parse JUnit XML into a small dashboard or use Allure history).
- [ ] Try the same pipeline in a second CI tool (GitLab CI or Jenkins in Docker). The
      concepts carry over, and interviewers ask about it.

**Done when:** a tag push produces a signed image, deploys it and verifies it with no
manual steps.

---

## Phase 7: Kubernetes and observability

- [ ] **kind** cluster in CI; a Helm chart for app + Postgres.
- [ ] Deploy the chart and run the API/UI suites against the cluster.
- [ ] **Ephemeral environments**: one namespace per PR, torn down on close.
- [ ] Readiness/liveness probes, and a test that kills a pod mid-suite.
- [ ] **Observability**: structured logs, Prometheus metrics and OpenTelemetry traces in
      the app. Have tests assert on them (e.g. "an error request increments
      `http_errors_total`") and attach trace IDs to failing test reports.
- [ ] Run the test suite itself as a Kubernetes Job.

**Done when:** every PR gets its own environment, a full test run and a link to the
traces of any failing test.

---

## Phase 8: AI in QA

- [ ] **Testing an LLM feature**: add e.g. "suggest priority from title" to TaskApp.
      Write evals (golden datasets, assertion-based and model-graded scoring), check
      for regressions between prompt versions, and test prompt injection.
- [ ] **MCP server** exposing the framework (create test data, run a suite, read a
      report) so an AI agent can use it. Write the agent rules.
- [ ] **AI-assisted test generation, measured**: have an agent write tests for a new
      endpoint, then score them with the bug-injection matrix and mutation testing
      against your hand-written ones. Write up the results honestly.

**Done when:** you have numbers, not opinions, on where AI helps your testing.

---

## Capstone: make it a portfolio

- [ ] A README that tells the story: the architecture diagram, the test pyramid with
      real counts, CI badges and links to live reports.
- [ ] `docs/decisions/`: short ADRs ("why Playwright over Selenium", "why API-seeded UI
      data", "why strict contracts are separate from app models").
- [ ] A 5-minute walkthrough you could give in an interview: one bug, how it was
      injected, which layer caught it and why the other layers didn't.

## Skills checklist

| Area | Covered in |
| --- | --- |
| STLC, test design, defect management | 0 |
| Framework design, Python, pytest internals | 1 |
| Databases, test data, Docker Compose | 2 |
| Contract, property-based, fuzz testing | 3 |
| UI automation, a11y, visual | 4 |
| Performance, security, resilience | 5 |
| CI/CD, release, quality gates, metrics | 6 |
| Kubernetes, observability | 7 |
| AI/LLM testing | 8 |
