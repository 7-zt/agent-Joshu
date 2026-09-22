# Fast Review: Python Engineering

Default mode. A quick, high-signal self-check after development or on a small diff. Optimized for low cost and few, confident findings, not coverage.

## Trigger

- Default when no mode is specified.
- Daily development self-check.
- Small diff, single file, or focused PR.

## Preconditions

- Read-only. Do not modify code.
- Have a concrete target: a diff, a file, or a named set of files. If the scope is a whole repository or unclear, ask the user to narrow it or treat the request as a full review.

## Steps

1. Establish project facts. Read `pyproject.toml` for `requires-python`, dependencies, and tool config. Glance at the directory layout (`git ls-files`, `find`) to classify project shape.
2. Scan the diff or specified files. Prefer `git diff`, `git show`, `rg`, and `nl` over loading everything.
3. Check the target against:
    - Version compatibility, syntax/stdlib use vs `requires-python`.
    - Dependency hygiene, new imports backed by a declared dependency, right group.
    - Layout clarity, file lands in a sensible place for the project shape.
    - Type boundary leaks, `Any`, unguarded `cast`, untyped public signatures at module edges.
    - Resource lifecycle, files, sockets, locks, clients opened without a context manager or guaranteed cleanup.
    - Data model clarity, dicts/tuples standing in for a stable record that wants a `dataclass`/`TypedDict`.
    - Unnecessary complexity, abstraction, indirection, or flags beyond what the change needs.
    - Tool-verifiable actions, name the command that would confirm a fix (test, type check), don't run it unprompted.
4. Output 0-5 findings, highest signal first. Zero findings is a valid result.

## Output Format

Findings-first and compact. One block per finding:

```text
- [severity] path:line Title
  Fact: observable code/config evidence.
  Impact: correctness, maintainability, readability, testability, runtime, or delivery cost.
  Recommendation: smallest sufficient change.
```

Skip Open Questions and Notes unless they carry real signal. Do not pad to reach five.

## Stop Rules

- Do not escalate to full review, suggest it only if the diff clearly warrants deeper work.
- Do not modify code.
- Do not run fixes, installs, or any command that writes files, creates `.venv`/cache, or alters the lockfile.
- Cap at 5 findings; keep the most load-bearing.
- Skip anything Ruff, ty, mypy, or pre-commit catches mechanically. Mention once in a Note only if it blocks the review.
