# Rule of Three

## What it is

The Rule of Three is a heuristic for _when_ to abstract: write the thing directly the first time, tolerate a limited duplication the second time, and only on the third occurrence, or once the direction of variation is clearly understood, extract a shared abstraction. It is the practical brake on [dry.md](./dry.md).

The number three is not magic. The real signal is "I now understand how these cases vary." Two instances rarely tell you that. Three usually do, because the third point reveals which parts are stable and which parts differ, and therefore where the seam belongs.

## Why wait

With only two examples, you cannot see the axis of variation. Any abstraction you extract is a guess about what will change, and guesses about the future are usually wrong. When you guess wrong, the shared function survives by growing flags, mode parameters, callbacks, and special-case branches; each new requirement bolting another knob onto a structure that was never shaped for it. The code ends up worse than the duplication it replaced, and you eventually have to unwind it: inline the abstraction, restore the duplication, and re-derive the real seam from three concrete cases.

Three concrete instances let you extract a parameter set that reflects actual variation rather than imagined variation. The abstraction's shape is discovered, not invented.

## Relationship to DRY: complementary, not contradictory

On the surface DRY and the Rule of Three look opposed: DRY says remove duplication, the Rule of Three says wait. They are reconciled by remembering what each one targets.

- DRY targets _knowledge_ duplication: the same rule expressed in several places.
- The Rule of Three delays abstraction of _shape_ similarity; code that looks alike but may not share knowledge.

So they do not actually conflict. DRY still demands you collapse a genuinely duplicated domain rule immediately. The Rule of Three only governs the harder case: fragments that resemble each other but whose common essence is not yet proven. In that case, waiting for the third instance protects you from a wrong abstraction.

## When to override it

Do not mechanically wait for three when the knowledge is both clearly identical and high-risk. Override the Rule of Three when:

- The duplicated thing is a security check, permission rule, monetary calculation, protocol contract, data-consistency invariant, or the single source of truth for a schema. Divergence here is dangerous, and you already know it is one rule.
- The pattern is obvious and stable; a well-known idiom where the variation axis is clear from the first or second instance, with no realistic chance of the cases diverging.

In short: wait when the commonality is uncertain; act when it is certain and the cost of drift is high.

## Interaction with other principles

- [dry.md](./dry.md): the Rule of Three is the safety valve that keeps DRY from producing premature, over-parameterized abstractions.
- [yagni.md](./yagni.md): both resist building structure before it is needed; the Rule of Three is the version specific to deduplication.
- [kiss.md](./kiss.md): waiting often keeps the code simpler, because two clear copies beat one tangled generic function.
