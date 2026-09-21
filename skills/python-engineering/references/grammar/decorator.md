# Decorators

A decorator is syntactic sugar for a higher-order function: `@d` above a definition means `f = d(f)`. The definition is passed to `d` at definition time, and the name is rebound to whatever `d` returns. Everything a decorator does could be written as an explicit call; the syntax exists to put the transformation where the reader sees the thing being transformed.

## Simple Decorators

A decorator with no arguments takes one callable and returns a replacement. The replacement is usually a wrapper closure that adds behavior around the original:

```python
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def traced(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        log.debug("enter %s", func.__name__)
        try:
            return func(*args, **kwargs)
        finally:
            log.debug("exit %s", func.__name__)

    return wrapper
```

`ParamSpec` and `TypeVar` let the wrapper preserve the wrapped signature for type checkers, so callers still see the original parameters and return type.

## functools.wraps And Signature Preservation

Without help, the wrapper closure replaces the original's identity: `__name__`, `__doc__`, `__module__`, `__qualname__`, `__annotations__`, and `__wrapped__` all describe `wrapper`, not `func`. This breaks introspection, documentation generation, logging that prints function names, and some frameworks that read metadata.

`functools.wraps` (itself a decorator applied to the inner wrapper) copies that metadata across. Always apply it. It also sets `__wrapped__`, which lets tools unwrap to the original. Note that `wraps` copies `__annotations__` but cannot make a type checker understand a wrapper whose call signature differs from the original; that is what `ParamSpec` is for.

## Decorators With Arguments

A decorator that takes configuration is a factory: a function that returns a decorator. This adds one level of nesting; the outer call captures the arguments, the middle function is the actual decorator, and the inner closure is the wrapper:

```python
def retry(*, attempts: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last: Exception | None = None
            for _ in range(attempts):
                try:
                    return func(*args, **kwargs)
                except TransientError as exc:
                    last = exc
            raise RetryExhausted from last

        return wrapper

    return decorate
```

Used as `@retry(attempts=3)`. Note that `@retry` without the call would pass the function in as `attempts`, a common mistake. Keep parameters few and keyword-only; many options usually signal the behavior wants an explicit policy object instead.

## Class Decorators

A decorator can be applied to a class. It receives the class object and returns a class (often the same one, mutated). This is how `@dataclass` works: it inspects annotations and synthesizes `__init__`, `__repr__`, and others. Class decorators suit registration, attaching framework metadata, or small post-processing. They become dangerous when they alter construction, inheritance, or attributes in ways type checkers and readers cannot follow.

## Decorator Classes

A class whose instances are callable via `__call__` can serve as a decorator. Reach for this when the wrapper needs named state, setup beyond a single closure variable, or a clearer object boundary:

```python
class RateLimited:
    def __init__(self, limiter: Limiter) -> None:
        self._limiter = limiter

    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            self._limiter.acquire()
            return func(*args, **kwargs)

        return wrapper
```

Distinguish a _decorator class_ (its `__call__` takes a function) from a class used to wrap an _instance_. The former decorates; the latter is plain composition.

## Stacking And Execution Order

Stacked decorators apply bottom-up at definition time and the resulting wrappers execute top-down at call time:

```python
@cache
@retry(attempts=3)
def fetch(key: str) -> bytes: ...
```

Here `retry` wraps `fetch` first, then `cache` wraps that. At call time `cache` runs outermost, so a cache hit skips retry entirely. Order changes behavior, so when two decorators interact (caching and retry, authorization and logging) the order is a real decision worth a comment.

## Type Preservation Challenges

A wrapper erases type information unless you preserve it deliberately. Use `ParamSpec` plus a return `TypeVar` for signature-preserving wrappers. Decorators that _change_ the signature, adding an injected argument, changing the return type, cannot be expressed by simple `ParamSpec` passthrough and need a hand-written return type or `typing.overload`. A decorator that turns a function into a different kind of object (a descriptor, a registered handler) should annotate that new type so callers are not misled.

## When Decorators Help And When They Hurt

Decorators are the right tool for stable, cross-cutting concerns where the name says exactly what changes: registration, routing, caching (`@cache`), retry or timeout policy, authorization, metrics, tracing, and deprecation markers. The standard library ships several you should recognize: `@property`, `@staticmethod`, and `@classmethod` shape attribute and method binding; `@functools.cached_property` memoizes per instance; `@dataclass` generates boilerplate; `@typing.overload` declares multiple signatures; `@functools.singledispatch` provides type-based dispatch.

They hurt when they hide control flow a reader needs to follow, smuggle business logic into a place no one inspects, change return types or swallow exceptions invisibly, or make debugging harder by burying the real call behind layers of wrappers. The test: if understanding the function's behavior requires reading the decorator's source, the behavior probably belonged in an explicit call or a context manager instead.
