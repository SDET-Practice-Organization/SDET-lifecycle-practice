# AGENTS.md

Instructions for AI coding assistants working in this repo (Claude Code, Copilot, Cursor,
Codex, ...). Plain markdown on purpose, so it works with any tool.

## Project

QA Lifecycle Lab: a practice project covering the whole SDET lifecycle.
- `app/`: TaskApp, the FastAPI system under test (see README for the endpoints).
- `framework/`: the test framework (`ApiClient`, `TasksApi`, contracts, factories, assertions).
- `tests/Python/`: `unit/` and `api/` pytest suites.
- `docs/`: test plans, test cases and templates. `ROADMAP.md` lists the phases.

This is a **learning project**. Explain the reasoning behind test-design and framework
decisions, and prefer leaving practice items to the user when a doc marks them as such.

## Commands (Windows / PowerShell)

```powershell
.venv\Scripts\Activate.ps1
pytest                                   # all tests; API tests start the app themselves
pytest tests/Python/api -m smoke         # smoke only
ruff check . ; ruff format --check .     # lint (CI fails on either)
$env:TASKAPP_BUGS = "<bug>"; pytest tests/Python/api; Remove-Item Env:TASKAPP_BUGS
```

## Shared rules (every agent follows these)

- [agents/rules/framework.md](agents/rules/framework.md): how tests use the framework
- [agents/rules/bug-injection.md](agents/rules/bug-injection.md): every feature gets a planted bug
- [agents/rules/code-style.md](agents/rules/code-style.md): Python/pytest style
- [agents/rules/git.md](agents/rules/git.md): branches, commits, what needs permission
- [agents/rules/testrail.md](agents/rules/testrail.md): reading and pushing cases to TestRail

## MCP servers

Configured in [.mcp.json](.mcp.json) (project scope). Check them with `/mcp` in Claude Code.

| Server | Used for | Needs |
| ------ | -------- | ----- |
| `testrail` ([@bun913/mcp-testrail](https://github.com/bun913/mcp-testrail)) | Read cases; push `Ready` cases (with confirmation) | Node.js ≥ 20.18; `TESTRAIL_URL`, `TESTRAIL_USERNAME`, `TESTRAIL_API_KEY` in `.env` |

## Agents

Each agent is a role with its own inputs, outputs and definition of done. To use one,
say: *"Act as the agent in `agents/<file>.md` for `<target>`"*.

| Agent | Use it to |
| ----- | --------- |
| [test-designer](agents/test-designer.md) | Build test cases from requirements / code |
| [test-automator](agents/test-automator.md) | Code test cases as pytest tests |
| [test-reviewer](agents/test-reviewer.md) | Review test cases or test code |
| [exploratory-tester](agents/exploratory-tester.md) | Run a time-boxed exploratory charter |
| [defect-reporter](agents/defect-reporter.md) | Write a bug report from a failure or finding |
| [bug-injector](agents/bug-injector.md) | Plant a defect and prove the suite catches it |

How they hand work to each other: [agents/README.md](agents/README.md).

If no agent is named, follow the shared rules and pick the role that fits the request.
