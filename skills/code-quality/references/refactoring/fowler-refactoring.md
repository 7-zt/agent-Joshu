# Fowler-Style Refactoring

## What it is

Refactoring, in Martin Fowler's precise sense, is **restructuring existing code without changing its external observable behavior**. The inputs produce the same outputs; the side effects a caller depends on are preserved. What changes is the internal structure: names get clearer, responsibilities move to better owners, long functions split into named phases, duplicated knowledge collapses to one place.

This is narrower than the casual "I refactored the code" that often means "I rewrote it and changed some behavior along the way." When the observable behavior changes, it is not refactoring; it is a feature change, a bug fix, or a performance optimization. Keeping these activities separate is the whole discipline.

Fowler's _Refactoring_ pairs a catalog of **code smells** (symptoms that suggest a structural problem) with a catalog of **named refactorings** (small, behavior-preserving transformations that address them). The smells tell you _where_ to look; the refactorings tell you _how_ to fix it in controlled steps. See [code-smells.md](./code-smells.md) for the smell side and the individual technique documents like [extract-function.md](./extract-function.md) for the transformation side.

## The discipline: small steps, one thing at a time

The defining practice is the size of each step. A refactoring is a sequence of tiny transformations, each one small enough that it is obviously correct, and after each one the tests are green again. You rename a variable, run the tests. You extract a function, run the tests. You move it to another class, run the tests. If a step breaks something, you know exactly which change caused it, because you only made one.

This is the opposite of "let me restructure this whole module and then see if it still works." Large unverified restructuring is where refactoring goes wrong: when the tests fail at the end, you cannot tell whether you introduced one bug or five, and the safe move becomes throwing the work away. Small steps keep you continuously in a working state, so you can stop at any point and still have shippable code.

One thing at a time also means **never mixing refactoring with feature changes in the same step**. Fowler describes wearing "two hats": when adding a feature, you do not also clean up structure; when refactoring, you do not add capability. You switch hats deliberately and often, but you always know which one you are wearing. Mixing them is dangerous because a green test after a combined change tells you nothing; you cannot attribute the result to either activity. In practice this means refactoring and behavior changes belong in separate commits, or at minimum are called out separately. See [safe-refactoring.md](./safe-refactoring.md) for the safety mechanics.

## When to refactor

Refactoring is not a separate phase you schedule for later. It is woven into ordinary work, and there are three natural moments for it:

- **Preparatory refactoring.** Before adding a feature, reshape the code so the feature fits cleanly. "Make the change easy, then make the easy change." If a function needs a new parameter and three of its callers would each need awkward handling, first refactor so the seam exists, then add the feature through it. This is the highest-value moment because the restructuring pays off immediately.
- **Comprehension refactoring.** When you finally understand a confusing piece of code, fold that understanding back into it: rename the misleading variable, extract the unnamed concept, add the missing structure. You were going to spend the effort understanding it anyway; capturing the result means the next reader does not have to.
- **Cleanup refactoring.** When you touch code that is more tangled than it needs to be, leave it a little better than you found it. The boy-scout rule. This is bounded by judgment: clean up what is in your way, not the entire module.

## When NOT to refactor

- **No tests and no other safety net.** Refactoring depends on a fast way to confirm behavior is preserved. Without tests, characterization tests, type checking, or some repeatable verification, you are not refactoring; you are editing and hoping. Either add the safety net first (see [safe-refactoring.md](./safe-refactoring.md)) or do not touch the structure.
- **Deadline pressure without a safety net.** Under a real deadline, large speculative restructuring is a bad bet. Small, safe steps are fine and even helpful; a risky reshape that might not finish is not.
- **Code you are about to delete or replace wholesale.** Polishing structure you will throw away next week is wasted effort. YAGNI applies to cleanup too.
- **When it would change behavior you cannot verify.** If the code touches a public API, a serialization schema, or CLI arguments, "just tidying" can break consumers silently. Define the observable contract first, or treat the work as a behavior change rather than a refactoring.

## Smells point, refactorings cut

The relationship between the two catalogs is diagnostic. A smell, a long function, duplicated code, a feature-envious method, is a _symptom_, not a verdict. It tells you to look closely, not to act mechanically. Once you have confirmed the underlying structural problem, you pick a named refactoring that addresses it and apply it in small steps. The smell is the question; the refactoring is one possible answer. This keeps you from "fixing" things that are not actually broken and from reaching for a heavy transformation when a rename would do.

In agent-assisted development the smell-then-refactor loop matters more, not less: code accumulates faster, so structural problems appear faster, and the temptation to rewrite rather than transform is stronger. The discipline of behavior-preserving small steps is what keeps fast-moving code from drifting into states no one can verify.
