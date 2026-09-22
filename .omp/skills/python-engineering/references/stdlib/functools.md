# functools

`functools` provides higher-order helpers: tools that take or return functions. They reduce boilerplate around dispatch, partial application, memoization, and decorator authoring. Each helper below addresses a different need; reach for them when the manual alternative is more error-prone, not by default.

## singledispatch

`@singledispatch` turns a function into a generic function that picks an implementation by the runtime type of its _first_ argument. Register type-specific variants with `.register`:

```python
from functools import singledispatch

@singledispatch
def render(value: object) -> str:
    raise TypeError(f"no renderer for {type(value).__name__}")

@render.register
def _(value: int) -> str:
    return f"int:{value}"

@render.register
def _(value: list) -> str:
    return "[" + ", ".join(render(v) for v in value) + "]"
```

Since Python 3.11 the registered annotation may be a union (`int | float`), covering a type family in one registration. `singledispatch` fits open extension where new types add handlers without editing a central function; a lightweight visitor. It does _not_ dispatch on the second argument, on field values, or on combinations; those need explicit branching, `match`, or a dispatch map. Use `singledispatchmethod` for methods. Keep the base implementation meaningful (a sensible default or a clear error), because it runs whenever no registered type matches.

## partial

`partial` binds some arguments of a callable, producing a new callable that needs only the rest. It captures context without a wrapping `lambda` or closure:

```python
from functools import partial

def connect(host: str, port: int, *, timeout: float) -> Connection: ...

connect_local = partial(connect, "localhost", timeout=5.0)
conn = connect_local(8080)
```

Prefer `partial` over `lambda` when you are only fixing arguments; it is picklable, introspectable (`.func`, `.args`, `.keywords`), and reads as intent. Type checkers infer `partial` results imperfectly for complex signatures, so annotate the binding site when the inferred type is unclear. Use it for callbacks, dependency wiring, and configuring generic functions for a specific call site; avoid stacking many partials into an opaque chain.

## lru_cache / cache

`@lru_cache(maxsize=...)` memoizes results keyed by arguments; `@cache` (3.9+) is `lru_cache(maxsize=None)`: an unbounded memo. They speed up pure, repeatedly called functions with hashable arguments:

```python
from functools import cache

@cache
def factorial(n: int) -> int:
    return 1 if n <= 1 else n * factorial(n - 1)
```

The cache is correct only when the function is referentially transparent: same inputs, same output, no observable side effects. Caching impure functions (reading files, clocks, mutable globals) hides staleness bugs. Two further hazards: an unbounded `@cache` on a long-lived process is a memory leak, and a cache on a method or any function holding a reference to an object keeps that object alive. Arguments must be hashable, so unhashable inputs like lists or dicts cannot be cached without conversion. Bound the size with `lru_cache(maxsize=...)` when input variety is large, and expose `.cache_clear()` for tests.

## reduce

`reduce` folds a binary function over an iterable into a single value. It is readable for genuine accumulations that have no built-in:

```python
from functools import reduce
from operator import or_

merged = reduce(or_, dict_list, {})  # union of many dicts
```

Prefer a plain `for` loop or a built-in (`sum`, `math.prod`, `any`, `all`, `"".join`) when one exists; they are clearer to most readers. `reduce` earns its place only for associative combinations where naming the running accumulator in a loop adds no clarity. A nested `lambda` inside `reduce` is usually a signal to switch back to an explicit loop.

## wraps

`@wraps(func)` copies a wrapped function's identity (`__name__`, `__doc__`, `__module__`, `__qualname__`, `__annotations__`, and `__wrapped__`) onto a wrapper. Every hand-written decorator that returns an inner function should apply it:

```python
from functools import wraps

def logged(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

Without `wraps`, introspection, documentation tooling, `help()`, and test reporting all see the wrapper's identity instead of the original. `__wrapped__` also lets tools unwrap to the underlying function. See [`decorator`](../grammar/decorator.md) for the broader decorator mechanics this supports.
