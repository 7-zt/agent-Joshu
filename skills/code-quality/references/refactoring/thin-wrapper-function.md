# Thin Wrapper / Trivial Helper

## What it is

A thin wrapper is a function whose entire body forwards to another function, renames a call, or wraps a single expression, without adding any semantic value. It does not hide complexity, establish a boundary, or enforce an invariant. It just adds a name and a layer.

```python
def get_user_name(user):
    return user.name  # adds nothing the caller couldn't see

def fetch_data(url):
    return requests.get(url)  # renames one call, hides nothing
```

The smell is not "this function is short." Plenty of short functions are excellent; a well-named one-liner that captures a domain concept (`is_eligible_for_refund`) earns its keep. The smell is the _absence of added meaning_: the wrapper costs a name, a jump, and a stack frame, and returns nothing in exchange.

This smell shows up heavily in agent-generated code, where the reflex to "remove duplication" or "improve readability" produces a sprawl of one-line helpers that each forward a single call. The result is code you have to chase across many definitions to understand, where reading the original inline expression would have been clearer. It is closely tied to the wrong-DRY failure mode described in `duplicated-code.md` and [`skills/code-quality/references/design-principles/dry.md`](../design-principles/dry.md).

## When wrappers ARE valuable

A wrapper earns its place when it does real work beyond forwarding:

- **A stable interface over an unstable implementation.** If the wrapped library, API, or internal module is likely to change, the wrapper localizes that change. This is the Adapter idea; see `skills/code-quality/references/design-patterns`. A thin-looking wrapper here is a deep module with a small interface.
- **A test seam.** A function that exists so callers can be tested against a fake, or so a dependency can be injected, provides a substitution boundary even if its body is trivial. See [`skills/code-quality/references/design-principles/dependency-inversion.md`](../design-principles/dependency-inversion.md).
- **A cross-cutting concern.** Wrappers that add logging, retry, caching, metrics, or a transaction boundary do add behavior. These are decorators, not thin wrappers.
- **A named domain concept.** `requires_tax_review(order)` wrapping a boolean expression makes the rule searchable and gives it one home. The name _is_ the value.

## When they're noise

- A single caller and no abstraction boundary: inline it.
- The wrapper name is a synonym of the wrapped call (`fetch_data` for `requests.get`), adding no domain meaning.
- It forwards arguments unchanged to a function with an equally clear name.
- It exists only because a style rule said "extract functions," not because a reader benefits.

The cure is [inline-function.md](./inline-function.md): fold the body back into the caller and delete the wrapper.

## How to judge

Ask: if I deleted this function and inlined its body at every call site, would the code be harder to understand or harder to change? If the answer is no, it is a thin wrapper. If removing it would expose callers to an unstable dependency, scatter a domain rule, or break a test seam, it is doing real work; keep it. The test is the boundary it protects, not its line count.
