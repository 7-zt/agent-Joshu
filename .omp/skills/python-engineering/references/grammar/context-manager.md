# Context Managers

A context manager pairs a setup action with a teardown action and guarantees the teardown runs no matter how the block exits. The `with` statement (and `async with` for asynchronous resources) is how Python ties a resource's lifetime to a lexical scope.

## What Problem It Solves

Resources have a lifetime: a file must be closed, a lock released, a transaction committed or rolled back, a connection returned to a pool. Doing this with bare `try`/`finally` is correct but verbose and easy to get wrong; the cleanup drifts away from the acquisition, and nested resources produce deeply indented, fragile blocks.

```python
with open(path) as handle:
    process(handle)
# handle is closed here, even if process() raised
```

The `with` block makes the lifetime visible: acquisition at the top, scope in the body, and guaranteed release at the end. This document focuses on the language mechanism.

## The Protocol

A context manager is any object implementing two methods:

- `__enter__(self)` runs on entry. Its return value is bound to the `as` target. It often returns `self`, but it can return any handle (a file, a cursor, a connection).
- `__exit__(self, exc_type, exc, tb)` runs on exit, always. The three arguments are `None` on a clean exit, or describe the in-flight exception otherwise.

```python
class Transaction:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    def __enter__(self) -> Connection:
        self._conn.begin()
        return self._conn

    def __exit__(self, exc_type, exc, tb) -> bool:
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
        return False
```

## Exception Handling In `__exit__`

The return value of `__exit__` is a control-flow decision, and it is the single most misunderstood part of the protocol. Returning a falsy value (including `None`) lets any in-flight exception propagate normally. Returning a truthy value _suppresses_ the exception, as if it never happened.

Suppressing exceptions silently is almost always a bug. The transaction above returns `False` so a failed block still raises; it rolls back _and_ propagates. Only return `True` when swallowing the exception is the manager's explicit purpose (and even then, prefer [`contextlib.suppress`](../stdlib/contextlib.md) for clarity). A manager that cleans up should not also hide the failure that triggered the cleanup.

## Generator-Based Context Managers

For the common case where you do not need a class, `@contextlib.contextmanager` turns a generator into a context manager. Code before `yield` is the setup, the yielded value becomes the `as` target, and code after `yield` is the teardown:

```python
from contextlib import contextmanager

@contextmanager
def timed(label: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        log.info("%s took %.3fs", label, time.perf_counter() - start)
```

The `try`/`finally` is essential: without it, an exception in the body skips the teardown, because the exception is re-raised _at_ the `yield`. This and the other `contextlib` helpers are detailed in [the contextlib reference](../stdlib/contextlib.md).

## Async Resources

Asynchronous resources, connections, sessions, pools that must `await` during setup or teardown, implement `__aenter__` and `__aexit__` and are used with `async with`:

```python
async with pool.acquire() as conn:
    await conn.execute(query)
```

The semantics mirror the synchronous protocol, but entry and exit can suspend. Use `async with` whenever release involves I/O; never call a blocking close inside an `async` function when an async manager is available. The async equivalent of the generator helper is `@contextlib.asynccontextmanager`.

## Nested Contexts

Multiple resources can be managed in one statement. The parenthesized form (Python 3.10+) keeps long lists readable and produces clean diffs:

```python
with (
    open(src) as fin,
    open(dst, "w") as fout,
):
    fout.write(transform(fin.read()))
```

Managers enter left to right and exit right to left, so a resource that depends on an earlier one is released first. When the _set_ of resources is not known until runtime, such as a variable number of files or a dynamically built stack of managers, use [`contextlib.ExitStack`](../stdlib/contextlib.md) instead of nesting statements.

## When To Write Your Own

Write a custom context manager when there is a genuine acquire/release pair tied to your own resource or invariant: a domain lock, a temporary state change that must be restored, a transaction-like boundary, a metrics or tracing span. Prefer `@contextmanager` for simple linear setup/teardown; prefer a class when the manager carries named state, is reused as an object, or needs to be inspected.

Do not write your own when a stdlib helper already fits. `suppress`, `redirect_stdout`, `closing`, and `nullcontext` cover common needs, and a one-off `try`/`finally` is fine for a single local cleanup that will never be reused. Reaching for a custom class where a three-line `try`/`finally` would do adds indirection without benefit.
