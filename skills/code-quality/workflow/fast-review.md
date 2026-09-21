# Fast Review: Code Quality

Default mode. A quick, high-signal self-check after development or on a small diff. Optimized for few, confident findings, not coverage. Bias toward leaving good-enough code alone.

## Trigger

- Default when no mode is specified.
- Daily development self-check.
- Small diff, single file, or focused PR.

## Preconditions

- Read-only. Do not modify code.
- Have a concrete target: a diff, a file, or a named set of files. If the scope is a whole repository or unclear, ask the user to narrow it or treat the request as a full review.

## Steps

1. Establish project facts. Read the nearest `AGENTS.md`/`CLAUDE.md` and skim the code around the change to understand existing structure and conventions.
2. Scan the diff or specified code. Prefer `git diff`, `git show`, `rg`, and `nl` over loading everything.
3. Check the target against:
    - Wrong abstractions, a generic helper, base class, or parameter set that does not match the real variation.
    - Thin wrappers, a function or class that renames one expression and adds no semantic boundary.
    - Knowledge duplication, the same _rule, schema, or decision_ in two places (not merely similar-looking code).
    - Obvious smells, long function mixing phases, scattered/global state, primitive obsession, shotgun surgery.
    - Pattern misuse, a named pattern applied where no variation point exists yet.
    - Refactoring without tests, behavior-changing restructuring on code with no test coverage.
4. Output 0-5 findings, highest signal first. Zero findings is a valid result.

## Output Format

Findings-first and compact. One block per finding:

```text
- [severity, confidence] path:line Title
  Fact: observable evidence.
  Impact: why it matters, change cost, readability, correctness, testability.
  Recommendation: smallest sufficient change.
```

Skip Open Questions and Notes unless they carry real signal. Do not pad to reach five.

## Stop Rules

- Do not invent findings to satisfy a principle. A clean diff gets zero findings.
- Do not recommend abstraction for DRY without proving the two sites share the same knowledge.
- Do not automatically refactor or restructure; report, don't rewrite.
- Do not escalate to full review, suggest it only if the diff clearly warrants deeper work.
- Cap at 5 findings; keep the most load-bearing.
- Skip anything a formatter or linter catches mechanically.
