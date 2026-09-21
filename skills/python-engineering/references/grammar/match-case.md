# Structural Pattern Matching

`match`/`case` (Python 3.10+, [PEP 634](https://peps.python.org/pep-0634/)) destructures a value by its _shape_ and binds names from the parts that match. It is a declarative way to take apart structured data, not a cosmetic replacement for `if`/`elif`.

## What It Is

A `match` statement compares a subject value against a series of patterns. The first pattern that matches runs its block; names inside the pattern are bound to the corresponding pieces of the subject. Unlike `switch` in many languages, the cases are not constant labels; they are patterns that can inspect type, structure, and contents at once.

```python
match command:
    case "quit":
        stop()
    case ["move", direction]:
        move(direction)
    case {"action": action, "target": target}:
        dispatch(action, target)
```

Patterns do not fall through. Exactly one block runs, or none if nothing matches and there is no catch-all.

## Syntax Forms

Literal pattern matches a constant by equality (`case 0:`, `case "quit":`, `case None:`). `True`, `False`, and `None` match by identity.

Capture pattern is a bare name; it always matches and binds the subject (`case x:`). A bare `case _:` is the wildcard; it matches anything and binds nothing, serving as the default.

Value pattern uses a dotted name so a named constant is read rather than rebound: `case Color.RED:`. A plain name would capture; the dot is what makes it a comparison.

Sequence pattern matches lists and tuples by length and position, with `*rest` absorbing the middle or tail: `case [first, *rest]:`. It matches any `Sequence` except `str`, `bytes`, and `bytearray`.

Mapping pattern matches selected keys and ignores the rest: `case {"action": action}:`. `**rest` captures remaining pairs. A missing key fails the match.

Class pattern matches type and attributes: `case Point(x=0, y=y):`. Positional sub-patterns like `Point(0, y)` rely on the class's `__match_args__`; keyword sub-patterns do not.

OR pattern tries alternatives left to right: `case "y" | "yes":`. Every alternative must bind the same names.

Guard adds a boolean condition that runs only after the pattern structurally matches: `case [x, y] if x == y:`. A failed guard moves on to the next case.

Patterns nest freely, so `case Response(status=200, body={"items": [first, *_]}):` matches type, an attribute value, a nested mapping key, and a non-empty sequence in one expression.

## When It Is Better Than if/elif

`match` earns its place when branching depends on the _structure_ of data rather than a single scalar:

- Parsing or walking heterogeneous trees (AST nodes, JSON-like documents, protocol messages).
- Dispatching on the shape of a result: a tuple of one length versus another, a mapping with certain keys, an instance of one class versus another.
- Algebraic-style handling where each variant is a different dataclass and each case extracts different fields.

In these cases the alternative is a stack of `isinstance` checks plus manual indexing and `.get()` calls. `match` collapses the type test, the structure test, and the extraction into one readable block, and it binds names only on the branch where they are valid.

## When It Is Not

`match` is the wrong tool more often than it looks. Reach for something simpler when:

- Dispatch is on a single value with a known set of outcomes. A dict mapping keys to handlers (`handlers[key]()`) is clearer, extensible at runtime, and testable in isolation. Use that instead of a long `match` of literal cases.
- The logic is a small boolean decision. Two or three ordinary conditions read better as `if`/`elif`; `match` adds ceremony without structure to exploit.
- You are modeling a state machine. A transition table such as `(state, event) -> next_state` keeps states and transitions as data you can enumerate, validate, and diagram. A `match` buries those transitions in control flow, where you cannot see the whole graph at once.

The rule of thumb: if there is no structure to destructure, `match` is probably the wrong reach.

## Exhaustiveness

Python does not enforce exhaustiveness at runtime; an unmatched subject simply falls through with no error, which can hide bugs. Two habits address this:

- Add an explicit `case _:` that raises when an unexpected value reaches it, turning a silent fall-through into a loud failure.
- Let a type checker reason about exhaustiveness. When matching over a closed set such as an `Enum` or a union of dataclasses, checkers can flag a missing case. Pairing the match subject with an `assert_never(unreachable)` in the default branch makes the intended exhaustiveness explicit and lets the checker prove it.

This pairing, closed type plus `assert_never`, is what turns `match` from a convenience into a checkable contract.

## Typical Uses

Good: destructuring a parsed message into command variants; handling each node type of a small AST; matching `(status, payload)` result shapes; unpacking nested config structures with mapping and sequence patterns.

Poor: replacing a dict lookup; expressing two-way boolean logic; encoding state transitions; matching on a value's runtime type purely to call a method that the objects could expose polymorphically.

A subtle cost: names bound in a `case` remain in scope after the `match` block, so over-broad capture patterns can leak surprising bindings. Prefer specific patterns and keyword sub-patterns over positional ones unless the positional order is a stable, documented part of the type's contract.
