# Strategy

## Intent

Define a family of interchangeable algorithms behind a stable interface, so the algorithm can be selected and swapped, at configuration time or at runtime, without changing the code that uses it.

## Problem it solves

When a single operation has several variant algorithms (ways to sort, score, price, route, retry, compress), embedding them as a growing `if/elif` block couples the caller to every variant and makes adding a new one an edit to shared code. Strategy isolates each algorithm so the caller depends only on "something that scores an item", not on the specific scoring rule.

## Structure and participants

The classic form has a **context** that holds a reference to a **strategy** interface, with **concrete strategies** implementing it. The context delegates the variable part of its work to the injected strategy. The context owns the stable workflow; the strategy owns the part that varies.

## When to use

- There are multiple real algorithms today and the caller should not know which one runs.
- The algorithm must be selectable at runtime (user choice, config, A/B) or replaced in tests.
- The variation is along one clear axis ("how to score") with a small, stable interface.

## When NOT to use

- There is one algorithm, or a single `if` covers the two cases. Pre-emptive "strategy-fication" adds an interface for no benefit.
- The strategy interface is so wide that callers must assemble a complex object just to vary one decision; the abstraction is mis-cut.
- The "strategies" actually differ in _what_ data they need, not just _how_ they compute; they may not share a coherent interface.

## Failure modes

- A `Strategy` class with one method and one implementation, where a function would say the same thing with less ceremony.
- An over-broad interface that forces every concrete strategy to implement methods only one of them uses.
- Strategy selection scattered across the codebase instead of resolved in one place (a factory or dispatch map), so adding a variant means hunting for every selection site.

## Python example

Python functions are first-class, so the simplest way to implement Strategy is to accept a function parameter. There is usually no need for a strategy class:

```python
def rank_items(items: list[Item], score: Callable[[Item], float]) -> list[Item]:
    return sorted(items, key=score, reverse=True)

def priority_score(item: Item) -> float:
    return item.priority

rank_by_priority = partial(rank_items, score=priority_score)
```

Forms in rough order of weight:

- **A plain function or `lambda`** passed as an argument: the lightest strategy.
- **A closure** to capture a little stable configuration, or `functools.partial` to pre-bind arguments into a narrower callable.
- **A `Protocol` or callable object** when the strategy needs state, multiple related methods, or a name that documents intent.
- **`functools.singledispatch`** when the strategy is chosen by the _type_ of the input rather than a config value.
- **A dispatch map / `match`** when selection depends on a config value or several conditions.

## Relationship to other patterns

[factory.md](./factory.md) often _chooses_ which strategy to use. [command.md](./command.md) is structurally similar (a behavior as an object) but its intent is to capture a request for later execution, not to vary an algorithm. The [state.md](./state.md) pattern looks like Strategy but its variants change _themselves_ in response to events rather than being selected by the caller. `functools.singledispatch` and pattern matching are the Python mechanisms that most often absorb Strategy.
