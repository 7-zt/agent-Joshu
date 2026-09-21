# Full Review: Python Engineering

A systematic, evidence-driven Python engineering review. It reads in stages, verifies high-severity findings, and reports recommendations directly. Risky changes require authorization before execution. Run only when the user asks for a full review.

## Trigger

User explicitly says "full review", "complete review", "systematic review", or "architecture review". Do not enter this mode on your own.

## Preconditions

- Read-only by default. Modify code only when the user asks for fixes.
- Confirm scope before reading widely: which package, module, or subsystem, and what the review is for (release, handoff, refactor decision).

## Steps

1. Context intake. Sort the work into four buckets before reading code:
    - Must read, files the review cannot be correct without.
    - Should read, adjacent code, tests, and config that inform judgment.
    - Already known, facts established earlier in the conversation; do not re-derive.
    - Uncertain, open questions to resolve by reading or by asking the user.
2. Read in stages, not all at once.
    - Project facts: `pyproject.toml` (`requires-python`, dependencies, groups, tool config), `.pre-commit-config.yaml`, CI, test config, Makefile.
    - Relevant code and tests, pulled in by the review matrix below, load each category as you reach it.
3. Work the review matrix. For each, gather evidence before judging:
    - Version & dependencies, syntax/stdlib vs `requires-python`; declared deps, correct groups, no undeclared imports.
    - Layout, entry points, workspace, project shape, package boundaries, script/console entry points, workspace member coherence.
    - Type coverage, public signatures typed, `Any`/`cast` justified, Protocol/generics used where they earn their cost.
    - Docstrings & API docs, public surface documented, information placed where readers look.
    - Testing, behavior coverage over line coverage, fixture and parametrize structure, meaningful assertions.
    - Custom lint, project-specific mechanical rules respected; candidates for a new rule noted.
    - Grammar choices, `match`/`case`, context managers, exception groups, decorators used where they fit, not as ornament.
    - Stdlib usage, `functools`, `itertools`, `contextlib`, `pathlib`, `enum`, `dataclasses`, `logging` used instead of hand-rolled equivalents.
    - Tooling config, uv, Ruff, ty/mypy/basedpyright, pytest, coverage, pre-commit configured coherently and not contradicting each other.
4. Self-verify every high-severity finding. Re-read the evidence, consider a plausible false-positive reading, and state confidence. Downgrade or drop anything you cannot support.
5. Execution approval. Report recommendations directly; obtain the required authorization before carrying out:
    - Unsafe fixes or commands that modify reviewed files, create `.venv`/cache, or alter the lockfile.
    - Bulk suppressions or sweeping config changes.
    - Cross-file refactoring or dependency changes.
    - Behavior changes.

## Output Format

Structured findings grouped by matrix category. One block per finding:

```text
- [severity, confidence] path:line Title
  Fact: observable code/config evidence.
  Impact: correctness, maintainability, readability, testability, runtime, or delivery cost.
  Judgment: Python engineering category.
  Evidence: support, counter-evidence, and remaining uncertainty.
  Recommendation: smallest sufficient change.
  Verification: command to run, or why none is needed.
```

End with:

```text
Open Questions
- Items needing user or project confirmation.

Notes
- Downgraded, tool-handled, or intentionally unreported items.
```

## Stop Rules

- Do not modify code without an explicit request for fixes.
- Obtain authorization before carrying out unsafe fixes, bulk edits, cross-file refactoring, dependency changes, or behavior changes.
- Do not report what Ruff, ty, mypy, or pre-commit catch mechanically, note once if it affects the review, then move on.
- Keep facts, inferences, judgments, and recommendations separate.
