# Rule: git

- Never commit directly to `main`. Branch as `<type>/<short-name>`, e.g.
  `test/create-task-boundaries`, `feat/task-due-date`, `docs/test-strategy`.
- Small commits with imperative messages: `Add title boundary tests for POST /tasks`.
- Commit, push, open PRs or create GitHub issues **only when the user asks**.
- Never commit `.venv/`, `reports/`, caches, `.idea/` or secrets.
- Before proposing a commit, run `ruff check .` and `pytest`, and report the result honestly.
