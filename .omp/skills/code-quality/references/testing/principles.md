# Testing Principles

A test suite earns its keep two ways at once: it catches regressions, and it documents what the code is supposed to do. Both jobs are served by one discipline: **couple tests to behavior, decouple them from structure**. Kent Beck states the goal directly: a test should be sensitive to changes in _behavior_ and insensitive to changes in _structure_. Every principle below is a consequence of that one sentence.

This document is language-agnostic. It states the principles and the tradeoffs; the anti-patterns that violate them have their own catalog in [test-smells](./test-smells.md), and language-specific mechanics (pytest fixtures, parametrize, mocking) live in the relevant engineering skill.

## Test Behavior, Not Implementation

A test should assert on what a unit _does as seen from outside_, its return values, its raised errors, its recorded side effects, not on how it does it internally. The reason is economic: observable behavior is the contract you promised, so a test pinned to it fails only when you break a promise, and a refactor that preserves behavior leaves it green. A test pinned to internal calls, private fields, or the exact sequence of collaborator invocations fails on every refactor while proving nothing about correctness: it documents the implementation back to itself.

This is the direct answer to the most common complaint about agent-written tests: _"I change the code and have to rewrite a wall of tests, most of it over details that shouldn't be tested."_ That pain is almost always [Fragile Test](./test-smells.md#fragile-test) and [Change-Detector Test](./test-smells.md#change-detector-test); tests that mirror structure instead of behavior. The fix is not "write fewer tests"; it is "assert on outcomes, mock only at real boundaries."

**The boundary case.** Occasionally the behavior _is_ an internal choice; you must verify that a read went to the cache and not the database, or that a retry actually happened. Testing that is legitimate, but it should be rare and named for the guarantee ("serves repeated reads from cache"), not for the method. If most of your tests need to reach inside, the design is asking for dependencies to be injected as arguments rather than reached for internally.

## The Desiderata: What a Good Test Optimizes

Kent Beck's _Test Desiderata_ names twelve properties a test can have. They are not a checklist to satisfy all at once, several trade against each other, but a vocabulary for deciding what a given test should optimize:

- **Isolated**: tests don't affect each other; any order gives the same result.
- **Composable**: you can test one dimension independently of others.
- **Deterministic**: same code, same result, every run.
- **Fast**: cheap enough to run constantly.
- **Writable**: cheap to write relative to the code under test.
- **Readable**: a reader can see what's tested and why it matters.
- **Behavioral**: sensitive to changes in behavior (a bug should break a test).
- **Structure-insensitive**: a refactor that keeps behavior shouldn't break it.
- **Automated**: runs without human intervention.
- **Specific**: a failure points at one cause.
- **Predictive**: if it passes, the code is safe to ship.
- **Inspiring**: passing builds real confidence.

The properties conflict, and that is the point. _Predictive_ pulls toward realistic, full-stack tests; _Fast_ and _Specific_ pull toward small isolated ones. Programmer-facing unit tests deliberately give up some _Predictive_ and _Inspiring_ reach in exchange for _Writable_, _Fast_, and _Specific_; end-to-end tests make the opposite trade. Knowing which properties a test is _for_ stops you from demanding all twelve from every test.

## Coverage Is a Blind-Spot Finder, Not a Target

Line coverage measures which lines executed, not whether anything was checked; a test that calls a function and asserts nothing reports full coverage while verifying nothing. Fowler's position is the operational one: coverage is useful for the _negative_ signal (code that no test touches at all is a real gap) and misleading as a _positive_ target (a high percentage says nothing about assertion quality). The moment a coverage percentage becomes a goal, it manufactures low-value tests written to move the number.

The stronger signal is **mutation-based**: if you change a `+` to a `-`, flip a boundary, or delete a line, does a test go red? A surviving mutant is a real hole, a behavior no assertion pins down, in a way that a covered-but-unasserted line never reveals. You rarely need a mutation-testing tool to think this way; asking "which mutation would this test catch?" while writing it is enough to expose an assertion that checks nothing.

This reframes the goal from "cover every line" to "**pin every behavior that matters, with as few tests as achieve it.**" Two tests that exercise the same path through different surface data are often one test's worth of protection and two tests' worth of maintenance. When two cases kill the same mutants _and_ neither documents a distinct scenario the other misses, keep the clearer one and fold in the other; that is how you get equal coverage from fewer tests, which is exactly the reduction you're after. The check before merging is the same one below: matching mutation scores signal overlap, they do not by themselves prove the tests are interchangeable.

## Fewer, Stronger Tests

More tests is not more safety. A suite is an asset when each test pins a distinct behavior and a liability in proportion to the tests that don't. Three habits keep it lean:

- **One behavior per test.** A test that asserts one guarantee fails for one reason and names it in its title. A test that walks through five behaviors (an Eager Test, one form of [Obscure Test](./test-smells.md#obscure-test)) fails ambiguously and resists change. Prefer many small behavioral tests over few sprawling ones; but "small" means _narrow in behavior_, not _coupled to one function's internals_.
- **Parametrize equivalent cases.** When one behavior should hold across many inputs, express the cases as data, not as copy-pasted bodies. Each case reports separately, so a failure names the exact input, and the cases stay visible as a table. This is the right tool for boundary and equivalence-class testing; it is the wrong tool when cases need genuinely different setup or assertions: forcing those through one parametrized body just hides branching logic.
- **Delete dead weight: after proving it is dead.** A test that adds no protection any other test already provides is maintenance cost with no return. This happens: in one mutation-testing study of an LLM-generated suite (Bas Dijkstra's, n=23) 4 tests contributed nothing to line _or_ mutation coverage; a concrete case, not a fixed ratio to expect. But "kills the same mutants" is not proof of redundancy: before deleting, check that the test adds no distinct behavior documentation, no better failure localization, and no coverage of a mutant the others miss. Mutation tooling cannot enumerate every possible fault, so equal mutation scores are strong evidence of overlap, not a guarantee of it. Delete when the redundancy is established; do not delete on the strength of a matching score alone.

## DAMP Over DRY, in Tests Specifically

Production code leans DRY: remove duplicate _knowledge_ so a rule lives in one place. Test code leans the other way, **DAMP** (Descriptive And Meaningful Phrases), and this is deliberate, not sloppiness. The reason is that _tests have no tests_: their correctness is verified by a human reading them, so readability outranks deduplication. A test that inlines its setup and asserts its expectations directly can be checked at a glance; one that routes everything through shared helpers, loops, and a distant `setUp` forces the reader to assemble the scenario in their head before they can judge it.

This does not license copy-paste. The reconciliation is precise: eliminate duplication that hurts _maintenance_ (a value-object builder, a helper that removes noise), tolerate duplication that aids _reading_ (the specific inputs and expected outputs stated in the test body). Meszaros's [Test Code Duplication](./test-smells.md#test-code-duplication) smell targets structural duplication where one behavior change forces edits in many places; DAMP targets surface repetition that makes each test self-contained. They agree more than they conflict: both want a change to one behavior to touch few tests, and both want a reader to understand a test without leaving it.

## Isolation and Determinism Are Non-Negotiable

A test that passes or fails depending on order, timing, environment, or a previous test's leftovers doesn't just fail itself; it corrodes trust in the whole suite, and a suite people don't trust gets ignored, which is worse than having no suite. Fowler's rule is blunt: eradicate non-determinism, don't tolerate it. The recurring root causes are shared mutable state between tests, reliance on real external resources (network, clock, filesystem, remote services), unmanaged asynchrony, and unseeded randomness.

The disciplines that prevent it: give each test its own fresh state so any run order yields the same result; replace slow or nondeterministic dependencies at the system boundary with test doubles; control the clock and the seed rather than reading the real ones; and never let a flaky test sit in the main suite "to fix later": quarantine or fix it, because one flake teaches everyone to ignore red. Google's Small/Medium/Large test-size scheme operationalizes this by _forbidding_ the risky resources (network, sleep, multiple threads) in small tests, which is what makes them fast, parallelizable, and order-independent by construction.

## Don't Test the Framework, the Config, or Trivia

Every test costs attention forever, so a test only earns its place if it can catch a defect in _your_ logic. Three categories usually can't:

- **Framework and library behavior.** A test that a well-tested library sorts a list, or that an ORM saves a row, re-asserts someone else's guarantee and breaks when you upgrade. Test _your_ use of the library at the boundary, not the library.
- **Configuration and constants.** A test that reads a config value and asserts it equals the same literal, or that a settings object has the field you just declared, is a [Change-Detector Test](./test-smells.md#change-detector-test); it duplicates the source and fails whenever the source changes, catching nothing. Test the _behavior the config drives_ (does a `timeout` of 0 actually raise?), not the value.
- **Trivial mechanical code.** Getters, thin pass-through wrappers, and pure data holders that a formatter or type checker already guards rarely repay a dedicated test. If a helper has real logic worth testing, test it _through the behavior that uses it_ rather than in isolation; an isolated micro-test of a utility couples the suite to a detail the rest of the system may not even depend on.

The false-positive boundary matters here too: a utility with genuine, reused logic (a parser, a date-math function, a validation rule) _is_ worth testing directly, because a defect in it propagates widely. The anti-pattern is testing mechanically-guaranteed trivia and internal helpers _for coverage's sake_, not testing genuinely load-bearing logic wherever it lives.

## Tests as Documentation

A well-written test is among the most reliable documentation a project has, because it is hard for it to drift from the code without going red; a weak assertion, a wrong oracle, or a test edited in lockstep with the code it guards can still drift silently, so this is a strong tendency, not a guarantee. A reader who wants to know how to use a function should be able to open its tests and see realistic calls with expected results. This is a design target, not a side effect: **Arrange-Act-Assert** structure so each test reads as setup, action, expectation; one behavior per test so a failure points at one thing; names that state the guarantee (`rejects_expired_token`, not `test_validate_2`). Realistic data reinforces it: inputs like `"abc"` or `123` can pass a test that a real-world value would have failed, so use data that resembles production. Written this way, tests double as worked examples, which is the deep reason test-driven development produces both a design tool and living documentation in one pass.
