# Resource Lifecycle Design

A resource is anything that must be acquired and later released: a file handle, a socket, a lock, a database connection or transaction, a temporary directory, a thread or task, a subprocess. Resource lifecycle design is about answering, for each one, who creates it, who closes it, and how it is released on every path out, including the exception path. Most resource leaks and "connection pool exhausted" incidents are lifecycle questions that were never explicitly answered.

## Ownership

Every resource needs exactly one owner: the code responsible for releasing it. Ambiguous ownership is the root of both leaks (everyone assumed someone else would close it) and use-after-close bugs (one holder closed it while another still needed it).

The clearest rule is that the code which creates a resource owns it and closes it, and it does so within a scope it controls. When a function needs a resource only for its own duration, it should create, use, and release it locally. When a resource must outlive a single function, ownership moves up to a longer-lived holder, an application object, a context, a pool, and that holder's lifecycle becomes the resource's lifecycle. Passing an open resource into a function that does _not_ own it is fine, as long as the convention is clear: the callee uses it, the caller closes it.

A function signature can make ownership explicit. A function that accepts an already-open resource borrows it; a function that opens its own resource owns it. Mixing the two, sometimes opening, sometimes accepting, is where ownership becomes ambiguous and resources leak.

```python
def write_report(out: TextIO, rows: list[Row]) -> None:
    # borrows out: the caller opened it and the caller closes it
    for row in rows:
        out.write(format_row(row))


def save_report(path: str, rows: list[Row]) -> None:
    # owns the file: opens it, uses it, releases it, all in one scope
    with open(path, "w") as out:
        write_report(out, rows)
```

The borrowing function never calls `out.close()`; that would release a resource it does not own and surprise the caller. Keeping borrow-versus-own consistent across an interface is what makes leaks easy to reason about.

## RAII and context managers

RAII (Resource Acquisition Is Initialization) ties release to the end of a scope rather than to a manual cleanup call you might forget. Python expresses this with the context manager protocol and `with` / `async with`: the resource is acquired on entry and released on exit, whether the block returns normally or raises.

```python
with open(path) as f:
    data = f.read()
# f is closed here, even if read() raised
```

Do not rely on `__del__` or CPython reference counting to release files, locks, transactions, or connections. Destructor timing varies across implementations, breaks under reference cycles, and is unreliable on the exception path. Make release explicit and scope-bound.

## Scope-bound vs dynamic resource sets

For a fixed, statically known set of resources, nested `with` statements (or a single `with` with multiple managers) are the clearest expression. When the _number_ of resources is dynamic, opening one file per input path, acquiring a variable set of connections, use `contextlib.ExitStack` (or `AsyncExitStack`) instead of hand-writing a nested cleanup stack:

```python
from contextlib import ExitStack


def read_all(paths: list[str]) -> list[str]:
    with ExitStack() as stack:
        files = [stack.enter_context(open(p)) for p in paths]
        return [f.read() for f in files]
```

`ExitStack` guarantees every entered resource is released in reverse order, even if one acquisition partway through fails.

## The exception path

Cleanup must run when things go wrong, which is exactly when it is most often missed. Prefer `with` over manual `try/finally` because the manager encapsulates the cleanup once and correctly. When you do write `try/finally`, the release goes in `finally`, not after the `try` block. A custom context manager's `__exit__` must not swallow exceptions unless suppression is its explicit, documented purpose: returning a truthy value from `__exit__` silently hides errors.

## Async resource ownership

Async resources (connections, sessions, async generators) follow the same ownership rules but use `async with` and `__aenter__` / `__aexit__`. Two extra hazards: an async generator that holds a resource may be suspended and never resumed, so use `contextlib.aclosing()` to guarantee its cleanup runs; and a resource owned by a task is only released if that task is properly awaited or cancelled, so background tasks need explicit lifecycle management (see [async-concurrency.md](./async-concurrency.md)).

## Application startup and shutdown

The longest-lived resources, connection pools, clients, thread pools, caches, are owned by the application itself. Acquire them during startup and release them during shutdown, in reverse order. Framework lifespan hooks (ASGI lifespan, app factories, dependency-injection scopes) are the right place. Avoid acquiring these at import time: import-time side effects make modules unsafe to import for testing or tooling and tie resource lifecycle to import order rather than application lifecycle (see [imperative.md](./imperative.md) on entry-point structure).

## Partial initialization and release order

A subtle failure mode appears when several resources are acquired in sequence and one of the later acquisitions fails. The resources already opened must still be released, in reverse order, even though setup never completed. Hand-written code tends to get this wrong; the cleanup path for "we got halfway" is the path least likely to be tested.

This is the other reason to prefer `with` and `ExitStack` over manual setup: they release exactly the resources that were successfully entered, in reverse order, regardless of where setup failed. Acquire in dependency order (the connection before the transaction that rides on it) and the automatic reverse-order release tears down correctly: transaction first, then connection. When you must order release explicitly, the rule is last-acquired-first-released, because later resources may depend on earlier ones still being alive during their own cleanup.

## Pooling and lease patterns

When acquisition is expensive (database connections, HTTP sessions), a pool owns a set of long-lived resources and _leases_ them to callers for the duration of a unit of work. The lease, not the resource, is what the caller acquires and releases: typically via a context manager that checks the resource out on entry and returns it to the pool on exit. The discipline is identical: the leased resource has a clear scope, and it returns to the pool on every path out, including exceptions. A leaked lease is worse than a leaked file, because it permanently shrinks the pool until exhaustion.

```python
def handle_request() -> Result:
    with pool.connection() as conn:   # lease on entry, return on exit
        return run_query(conn)
```

The same RAII discipline scales from a single file handle to an application-wide pool: name the scope, make release automatic, and never depend on the garbage collector to do it for you.
