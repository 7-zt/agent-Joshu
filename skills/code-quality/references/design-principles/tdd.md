# Test-Driven Development

Test-Driven Development (TDD) is a workflow in which tests drive the development feedback loop.
You sketch a list of behaviors, pick one, write a small runnable test that fails, write just
enough code to make it pass, then refactor. Martin Fowler summarizes the loop as
**Red-Green-Refactor** and stresses that the refactor step is not optional decoration. It is
where design improves.

TDD is not primarily a testing technique. It is a design technique that happens to leave tests
behind. The act of writing the test first forces you to use the interface before it exists,
which surfaces awkward signatures and unclear responsibilities early.

## The Red-Green-Refactor cycle

1. **Red.** Write a test for one small behavior and watch it fail. The failure confirms the test
   actually exercises something and is not silently passing.
2. **Green.** Write the simplest code that makes the test pass. Not the elegant version: the
   sufficient one. Cutting corners here is allowed; the next step cleans up.
3. **Refactor.** With the test green and protecting behavior, improve the structure: rename,
   extract, remove duplication. The test stays green throughout.

The discipline is to keep steps small and to run the tests between each. A common failure is
collapsing the cycle: writing a large batch of code under one test, or smuggling a big
structural change into the green step where behavior is not yet stable.

## What TDD gives you

- **Design feedback.** Writing the test first means consuming the API before implementing it.
  Painful setup, too many parameters, or hard-to-construct collaborators show up as test pain,
  which is a signal about the design itself. This connects to
  [dependency-inversion](./dependency-inversion.md): hard-to-test code is often code whose
  dependencies were not injected.
- **A behavior specification.** The test suite documents what the code is supposed to do, in
  executable form that cannot drift out of date silently.
- **Regression protection.** Once a behavior is pinned by a test, future changes that break it
  fail loudly. This protection is what makes aggressive [refactoring](../refactoring/safe-refactoring.md)
  and [YAGNI](./yagni.md) safe. You can defer abstraction and reshape later without fear.

## When TDD is valuable

TDD pays off most where behavior is enumerable and the cost of a wrong answer is real:

- Pure functions, parsers, transformation and serialization logic.
- Domain rules with clear inputs and expected outputs: pricing, validation, state transitions.
- Bug fixes: write the failing test that reproduces the bug first, then fix it. The test becomes
  a permanent regression guard.
- API design, where using the interface first reveals whether it is pleasant to call.

## When strict TDD is counterproductive

TDD assumes you know enough about the desired behavior to write a test. When you do not, strict
test-first becomes friction:

- **Exploratory code and spikes.** When the interface and even the requirements are still
  unknown, write a spike to learn, then add characterization or contract tests once the shape
  settles. Forcing test-first here tests guesses.
- **UI and visual layout.** Much of the value is in appearance and interaction, which unit tests
  capture poorly. Test the logic behind the UI, not pixel placement.
- **Glue code.** Thin wiring that mostly delegates to well-tested libraries gains little from a
  test that just re-asserts the library's behavior.

Treat TDD as a high-value feedback strategy, not a moral obligation for every line. The goal is
working, well-designed software with adequate behavior coverage, not a test-first ritual or a
coverage-percentage trophy. A test with no meaningful assertion adds coverage and nothing else.

## Relationship to "test after" and behavior coverage

Writing tests after the code is not a sin; the important property is that behavior is covered
and the tests assert something real. What TDD adds over test-after is the design pressure of the
red step. Many teams mix the two: TDD for core logic and bug fixes, test-after for code that was
explored first. Both should target observable behavior at sensible boundaries rather than
internal implementation detail, so the tests survive refactoring. See
[law-of-demeter](./law-of-demeter.md) and [dependency-inversion](./dependency-inversion.md) for
why tests that reach deep into internals (deep mocks, patched privates) are a smell about the
design, not just the test.
