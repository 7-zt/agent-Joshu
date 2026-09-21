# Inline Function

## What it is

Inline Function is the inverse of [extract-function.md](./extract-function.md): it replaces a call with the function's body and deletes the function. Where Extract Function pulls a concept out into a name, Inline Function folds a function back in when the name no longer earns its place: when the body says as much as the call, or says it more clearly.

```python
# before
def get_rating(driver):
    return 2 if more_than_five_late_deliveries(driver) else 1

def more_than_five_late_deliveries(driver):
    return driver.late_deliveries > 5

# after
def get_rating(driver):
    return 2 if driver.late_deliveries > 5 else 1
```

## When to inline

- **A misleading name.** When the function name describes the body worse than the body describes itself, the indirection actively misleads. Inlining removes a wrong signpost.
- **Trivial delegation.** A function that does nothing but forward to another; the thin wrapper described in [thin-wrapper-function.md](./thin-wrapper-function.md). When there is no boundary, no test seam, and no unstable dependency behind it, inline it.
- **The body is clearer than the call.** Sometimes a one-line function obscures a simple expression that every reader already understands. The call forces a jump to confirm something obvious; inlining keeps the reader's eyes in one place.
- **Reversing premature extraction.** When an earlier refactoring (often agent-generated) chopped code into many small helpers along the wrong seams, inlining several of them back together lets you see the real shape and re-extract along better boundaries. Fowler's advice: when indirection is unhelpful, inline first, then re-extract.

## Safety checks before inlining

- **Polymorphism and overrides.** Do not inline a method that is overridden in subclasses, or one whose dispatch matters: inlining collapses behavior the type system was selecting between.
- **Recursion and multiple call sites.** Recursive functions cannot be inlined naively. With many callers, inlining everywhere may be a large change; consider whether the function is actually pulling its weight before doing so, and inline call site by call site.
- **Side effects and evaluation order.** Make sure folding the body in does not change when expressions are evaluated, especially if arguments have side effects or the body reads mutable shared state.
- **Behavior preservation.** As with all refactoring, run the tests after each inline. See [safe-refactoring.md](./safe-refactoring.md). IDEs offer "Inline Method," which handles the mechanical substitution and updates all call sites.

## When NOT to inline

Keep the function when it provides a stable interface over an unstable implementation, creates a test seam, names a genuine domain concept that aids searching and comprehension, or hides real complexity. Shortness alone is never a reason to inline; a small, well-named function at a clear boundary is good design, not a smell. The question is whether the name and boundary add meaning, not how many lines sit behind them.
