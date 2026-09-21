# Extract Function

## What it is

Extract Function takes a fragment of code and turns it into its own named function, replacing the fragment with a call. It is the most common refactoring and the primary cure for [long-function.md](./long-function.md). Fowler's guiding rule is about _intention_: if you have to spend effort working out what a block of code does, extract it into a function named after the _what_, not the _how_. The name then carries the meaning, and the body holds the mechanism.

```python
# before
def print_owing(invoice):
    outstanding = 0
    for order in invoice.orders:
        outstanding += order.amount
    print(f"name: {invoice.customer}")
    print(f"amount: {outstanding}")

# after
def print_owing(invoice):
    outstanding = calculate_outstanding(invoice)
    print_details(invoice, outstanding)
```

## When to extract

- **A coherent phase.** A block that does one identifiable step of a larger sequence: validate input, compute a total, format output. Pulling each phase out turns a wall of code into a readable summary. This pairs with Split Phase.
- **A named concept.** A condition or calculation that has a domain meaning worth naming: `is_overdue(invoice)` reads better than the raw date comparison, and the name becomes searchable.
- **A policy.** Logic that may vary or be reused, such as a scoring rule or retry policy, benefits from being a function you can pass around or swap. See Strategy in `skills/code-quality/references/design-patterns`.
- **Mixed abstraction levels.** When high-level intent and low-level mechanics sit side by side, extracting the mechanics restores a consistent level in the caller.

## Naming the extracted function

The name is the point of the refactoring. Name it after the result or intent: `calculate_outstanding`, not `loop_orders`. If you cannot find a good name, that is a signal the fragment is not a coherent unit; either you have grabbed the wrong boundary, or the code needs rethinking before extraction. A good name makes the call site read like a sentence.

## Parameter decisions

Pass in what the function needs, return what it produces. Prefer a small parameter list. If you find yourself passing many values that always travel together, that is a Data Clump; consider introducing a small object (see `primitive-obsession.md`) rather than a long signature. Avoid passing a flag that makes the function do one of two things; that usually means two functions are hiding inside one.

## Preserving behavior

Extraction must not change observable behavior. Watch for variables modified inside the fragment and used afterward; those become return values or, if there are several, a signal that the boundary is wrong. Watch for early returns, `break`, and `continue` that no longer make sense once the code is in a separate function. Run the tests after extracting; see [safe-refactoring.md](./safe-refactoring.md). IDE "Extract Method" handles much of this mechanically and safely.

## When NOT to extract

- The code is already clear inline and reads at a single abstraction level.
- Extraction would produce a [thin-wrapper-function.md](./thin-wrapper-function.md): a function whose name merely restates one expression, with a single caller and no boundary.
- The fragment is tangled with surrounding state such that the extracted signature would have many parameters and many return values. Untangle first, or reconsider the seam.

Extraction is reversible: if a later reading shows the extraction obscured rather than clarified, use [inline-function.md](./inline-function.md) to fold it back.
