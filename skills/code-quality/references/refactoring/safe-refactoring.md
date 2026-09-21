# Safe Refactoring

## Behavioral equivalence is the contract

The single promise of refactoring, as [fowler-refactoring.md](./fowler-refactoring.md) defines it, is that **external observable behavior does not change**. Same inputs produce same outputs; the side effects callers depend on still happen; errors that were raised are still raised. Internal structure is free to change however you like, as long as no one outside can tell the difference. Everything in this document exists to let you make structural changes while keeping that promise, and to _prove_ you kept it rather than hope.

"Observable" is doing real work in that definition. The exact sequence of private method calls is not observable. A return value, a written file, an emitted event, a raised exception, the contents of a log a consumer parses; those are. Before refactoring something near a boundary, get clear on what is actually observable, because that is the line you must not cross. For a public API, a serialization schema, or CLI arguments, the observable surface is wide and the constraint is tight.

## Tests before you touch structure

You cannot preserve behavior you cannot observe, and you cannot confirm preservation without a fast way to check. So the precondition for refactoring is a safety net: a test suite that exercises the behavior you are about to restructure, fast enough to run after every small step. If that suite exists and is green, refactoring is low-risk. If it does not, you build it first or you do not refactor.

This is not optional rigor. Restructuring code whose behavior is unverified is editing-and-hoping, and it is the most common way refactoring introduces bugs. The whole method depends on the feedback loop being trustworthy.

## Characterization tests

When you need to refactor code that has no tests, typically legacy code or something an agent generated quickly, you write **characterization tests** first. A characterization test does not assert what the code _should_ do; it pins down what it _currently_ does, including any quirks. You run the code, observe the output, and write a test asserting exactly that output. The test now characterizes the existing behavior.

The point is not correctness, the existing behavior might even be slightly wrong, the point is a tripwire. Once the current behavior is pinned, you can refactor freely, and any test that goes red tells you the restructuring changed something. If you later decide the old behavior was a bug, fixing it is a separate, deliberate behavior change with its own test update, not something that slips in under cover of refactoring. In Python, snapshot/approval testing and capturing representative outputs are practical ways to characterize transformation-heavy code quickly.

## Small reversible steps

Each step should be small enough to be obviously correct and easy to undo. Rename one symbol; run tests. Extract one function; run tests. Move it; run tests. The reasons this works:

- A failure localizes to the one change you just made, so debugging is trivial.
- You are continuously in a shippable state and can stop anytime.
- Reverting a single small step is cheap; reverting a tangled hour of changes is not.

Commit frequently. A clean commit per refactoring step, or per small group of related steps, means `git` itself is part of your rollback strategy.

## IDE and tool support

Automated refactorings (rename symbol, [extract function](./extract-function.md), [inline](./inline-function.md), [move](./move-function.md)) are safer than manual editing because the tool performs the transformation mechanically across all references, without the typos and missed call sites that manual edits introduce. Use them when available.

In Python, be aware the tooling is weaker than in statically typed languages. Dynamic dispatch, `getattr`, string-based references, monkeypatching, and duck typing mean a rename tool cannot find every reference with certainty. So Python refactoring leans harder on other checks: a type checker (mypy/pyright) to catch broken signatures, `rg` to find textual references the tool might miss, and the test suite as the final arbiter. Treat automated Python refactorings as a fast first pass, then verify, rather than as a guarantee.

## When manual refactoring is risky

Some situations defeat the usual safety mechanisms and call for extra care:

- **Reflection, dynamic attribute access, string-keyed dispatch.** Tools and greps both miss these. Search broadly and lean on runtime tests.
- **Public APIs and serialization formats.** The observable surface extends beyond your codebase to consumers you cannot test. Treat changes as behavior changes, not refactoring.
- **Concurrency and ordering.** Reordering operations can change behavior even when each step looks behavior-preserving in single-threaded tests.
- **Code with side effects you cannot easily reproduce in a test** (external services, time, randomness). Isolate the side effect behind a seam first so the core becomes testable.

## Rollback strategy

Refactoring should always have a clean exit. Before starting, ensure your working tree is committed so you have a known-good point to return to. Take small steps with frequent commits so the rollback unit is small. If a step fails and the cause is not immediately obvious, revert that step rather than trying to patch forward; the discipline is to return to green, not to accumulate fixes on top of a broken state. And if you discover mid-way that the abstraction you were moving toward is wrong, the right move is often to [inline](./inline-function.md) back to the previous structure and re-find the real seam, rather than pressing on. A refactoring you can cleanly abandon is a safe one.
