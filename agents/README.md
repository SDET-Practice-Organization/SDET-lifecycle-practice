# Agents

Each file in this folder defines one role. They all follow the same structure:
**Role · When to use · Inputs · Outputs · Rules · Workflow · Definition of done · Hand-off**.
All of them also follow the shared rules in [rules/](rules/).

## Pipeline

```
requirements / code
        │
        ▼
 test-designer ──► test-reviewer ──► test-automator ──► test-reviewer ──► bug-injector
   (cases)          (case review)       (pytest)          (code review)     (proves the
        ▲                                                                    tests catch it)
        │
 exploratory-tester ──► defect-reporter
   (session notes)        (bug report; new cases go back to test-designer)
```

1. **test-designer** writes cases in `docs/<plan>/test-cases.md` using
   [the template](../docs/templates/test-case-template.md). Status: `Draft`.
2. **test-reviewer** reviews the cases. When accepted, status becomes `Ready`.
3. **test-automator** codes `Ready` cases and fills in their `Automation` field.
4. **test-reviewer** reviews the test code.
5. **bug-injector** adds a planted bug for the feature and shows CI catching it.

Side loop: **exploratory-tester** finds behaviour nobody wrote down. **defect-reporter**
turns each finding into a report, and the designer adds a case so it can't come back.

## Adding a new agent

Copy an existing file, keep the same section headings, and add it to the table in
[AGENTS.md](../AGENTS.md).
