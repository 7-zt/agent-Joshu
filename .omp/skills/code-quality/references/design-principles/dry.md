# DRY: Don't Repeat Yourself

## What it is

DRY is one of the most misunderstood principles in software. The original formulation (Hunt and Thomas, _The Pragmatic Programmer_) is about _knowledge_: "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." It is not "no two pieces of code may look alike." The thing worth deduplicating is a domain rule, a schema, a protocol, a transformation, an error-handling policy; a decision that, if it changed, would have to change everywhere at once.

The danger DRY warns against is having the same knowledge in several places that can drift out of sync. When a tax rule, a permission check, a state transition, or a validation condition lives in three files, a future change is likely to miss one of them, and now the system contradicts itself.

## The assumption underneath

- When the same knowledge appears in multiple places, future edits will eventually update some and miss others.
- A single authoritative representation lets change happen in one place.
- But similar-looking code does not necessarily express the same knowledge. Two fragments can have the same shape today for entirely unrelated reasons, and be driven by different forces tomorrow.

That last point is what separates good DRY from bad DRY. The principle is about knowledge, not text.

## Duplicated knowledge vs coincidental similarity

Ask: if the requirement behind one copy changed, would the other copy _have_ to change too? If yes, they encode the same knowledge; deduplicate. If no, they merely resemble each other right now; leave them alone.

Examples of real knowledge duplication, worth removing:

- The same business rule (price calculation, eligibility, state machine transition) implemented in more than one place.
- A schema, API contract, or data model repeated across client, server, and tests.
- A retry or error-handling policy copy-pasted across call sites.
- A data-transformation rule expressed independently in several functions.

Examples of coincidental similarity, usually safe to keep separate:

- Two validation functions that happen to have the same structure but validate different concepts that will evolve independently.
- Two request handlers with parallel boilerplate whose business logic is unrelated.
- Test setup that looks repetitive but pins down distinct scenarios.

## When to abstract, when to tolerate repetition

Deduplicate immediately when the duplicated thing is genuinely one rule, especially for high-risk knowledge: security, permissions, money, protocol contracts, data consistency, and any single source of truth for a schema. For these, do not wait; the cost of divergence is too high. See [rule-of-three.md](./rule-of-three.md) for the exception structure.

Tolerate repetition when two fragments are similar but driven by different reasons to change, and the shared abstraction's shape is not yet clear. Premature unification picks the wrong seam. The "generic" function you extract from two cases tends to grow boolean flags, mode parameters, callbacks, special branches, and implicit preconditions as the third and fourth cases arrive, and now it is harder to maintain than the duplication ever was. This is the direct tension with [kiss.md](./kiss.md): an abstraction with many parameters and branches can carry more cognitive load than two clear, separate copies.

## Wrong DRY

Two failure modes dominate, and both are common in agent-generated code:

1. **Premature abstraction.** Unifying two coincidentally similar fragments before the variation direction is known. The result is a parametric monster. The fix when you discover this is to inline the abstraction, duplicate the code again, and wait for the real seam to reveal itself.

2. **Parametric / thin-wrapper proliferation.** Extracting one or two lines into many small wrapper functions in the name of "removing duplication." This rarely hides real complexity. It adds naming burden, jump cost, deeper call stacks, and, in Python, real per-call overhead because every call builds a frame. A wrapper that renames a single expression to a synonym is a shallow helper, not deduplication. See [`skills/code-quality/references/refactoring/thin-wrapper-function.md`](../refactoring/thin-wrapper-function.md) for how to recognize and unwind these.

Before extracting a helper, ask whether it provides a stable semantic boundary, hides genuine complexity, or carries a reusable policy. "It is used twice" is not enough. That is what the Rule of Three is for.

## Interaction with other principles

- [rule-of-three.md](./rule-of-three.md) is the brake on DRY: it delays abstraction of shape-similar code until the third instance, while still allowing immediate deduplication of confirmed knowledge.
- [deep-modules.md](./deep-modules.md): consolidating a domain rule behind a single clear interface satisfies DRY and information hiding at once.
- [yagni.md](./yagni.md): both push back on speculative structure, but DRY can also _push toward_ abstraction; let YAGNI and the Rule of Three temper it.
