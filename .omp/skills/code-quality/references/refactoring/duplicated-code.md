# Duplicated Code

## What it is

Duplicated Code is the smell of the same thing expressed in more than one place. It is listed among the dispensables because removing genuine duplication usually makes code clearer and cheaper to change. But it is also the smell most often misread, because the surface symptom, two fragments that look alike, does not tell you whether there is a real problem. The entire judgment hinges on one distinction.

## Knowledge duplication vs coincidental similarity

This is the critical distinction, and getting it wrong in either direction causes damage.

**Knowledge duplication** is the same _decision_ expressed in multiple places: a business rule, a validation condition, a schema, a protocol detail, a tax calculation, a state transition. The test is counterfactual: _if the requirement behind one copy changed, would the others have to change too?_ If yes, they encode one piece of knowledge, and having it in several places means a future edit will update some and miss others, leaving the system contradicting itself. This is worth removing.

**Coincidental similarity** is code that looks alike today for unrelated reasons and is driven by different forces. Two validators with the same structure that check different concepts; two handlers with parallel boilerplate but unrelated logic; test setup that resembles other test setup while pinning distinct scenarios. If the requirement behind one changed, the others would not move. These fragments are not duplication in the meaningful sense, they merely rhyme, and unifying them couples things that should evolve independently.

The mistake of deduplicating coincidental similarity is more insidious than leaving real duplication, because it actively introduces coupling and a wrong abstraction that future changes have to fight. See [duplicated-code.md](./duplicated-code.md)'s sibling [dry](../design-principles/dry.md) for the principle this rests on: DRY is about knowledge, not text.

## When to extract

Extract when you have confirmed the fragments encode one piece of knowledge. For **high-risk knowledge**, security, permissions, money, protocol contracts, data consistency, a schema's single source of truth, extract on sight, even at the second occurrence. The cost of divergence in these areas is too high to wait.

For ordinary code where you are fairly sure but the variation direction is not yet clear, the **Rule of Three** is the brake: write it once, tolerate it twice, and extract on the third occurrence or when the variation direction becomes clear. By the third instance you can usually see what genuinely varies and what stays fixed, which means you pick the right seam instead of guessing. See [rule-of-three](../design-principles/rule-of-three.md).

## When to leave it

Leave duplication when the fragments are coincidentally similar, or when they are genuinely-but-not-yet-clearly related and you have not reached the third instance. Premature unification picks the wrong abstraction, and a wrong abstraction is more expensive than the duplication it replaced, you pay to build it, then pay again to dismantle it when the cases diverge. Tolerating two copies for a while is cheap and reversible; an unwanted abstraction is neither.

## Abstraction stability requirement

Before extracting, the shape of the abstraction must be reasonably stable. If you cannot yet name the extracted thing cleanly, or if you can already foresee that the next case will need a different parameter or branch, the seam is not ready. A good extraction has a clear name, few parameters, a single reason to change, and hides real complexity. If the candidate fails those, the duplication is telling you the underlying concept has not stabilized: wait.

## Wrong deduplication

The common failure, especially in agent-assisted code, is the **parametric wrapper that is harder to read than the duplication**. You extract two similar fragments into one function, but they were not identical, so the function grows a boolean flag to switch behavior, then a mode parameter, then a callback for the part that really differs, then a special branch for an edge case. The result is a function nobody can read, configured by call sites nobody can follow: strictly worse than the two honest copies. When you find one of these, the fix is to inline it, duplicate the code back, and re-find the real variation axis. A flag parameter that selects between two behaviors is often a sign the function should have stayed two functions.
