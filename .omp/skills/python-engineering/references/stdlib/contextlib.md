# contextlib

`contextlib` provides helpers for building and combining context managers without writing a full `__enter__`/`__exit__` class. It complements the [`with` protocol](../grammar/context-manager.md): the grammar document covers what the protocol is and when to use it; this document covers the standard tools for producing context managers cheaply.

## @contextmanager and @asynccontextmanager

`@contextmanager` turns a generator into a context manager. Code before `yield` runs on entry, the yielded value becomes the `as` target, and code after `yield` runs on exit. To handle exceptions you wrap the `yield` in `try`/`finally`:

```python
from contextlib import contextmanager

@contextmanager
def acquired(resource):
    resource.open()
    try:
        yield resource
    finally:
        resource.close()
```

The generator must yield exactly once. An exception raised inside the `with` body is re-raised _at_ the `yield` point, which is why cleanup belongs in `finally` rather than after a bare `yield`. `@asynccontextmanager` is the coroutine equivalent, driven by `async with`, with `await` allowed around the `yield`.

This decorator form is the right default for sequential setup/teardown logic. Reach for a full class only when you need reuse as an instance, multiple methods, or reentrancy.

## ExitStack and AsyncExitStack

`ExitStack` manages a _dynamic_ set of context managers: when the number of resources is not known at parse time, or resources are acquired in a loop:

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]
    process(files)
# every file closes here, in reverse order, even if one raises
```

`enter_context` registers an already-created context manager; `callback` registers an arbitrary cleanup function; `push` registers an `__exit__`-style callable. A useful pattern is partial-initialization safety: build resources onto the stack, then `stack.pop_all()` to transfer ownership out once construction fully succeeds, so a failure midway still unwinds everything acquired so far. `AsyncExitStack` is the `async with` counterpart with `enter_async_context` and async callbacks.

## suppress

`suppress(*exceptions)` ignores the named exceptions raised in its block; a clear replacement for `try/except SomeError: pass`:

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    path.unlink()
```

Keep the body to the single operation whose failure you mean to ignore. Wrapping several statements lets a later, unrelated failure of the same type slip through silently.

## redirect_stdout and redirect_stderr

These temporarily rebind `sys.stdout` / `sys.stderr` to any file-like object for the duration of the block. They suit capturing output from code you do not control:

```python
import io
from contextlib import redirect_stdout

buffer = io.StringIO()
with redirect_stdout(buffer):
    legacy_function_that_prints()
```

They are process-global and not thread-safe, so confine them to narrow scopes rather than leaving them active across large regions.

## nullcontext

`nullcontext(value)` is a context manager that does nothing on exit and yields `value` on entry. It removes branching when a resource may or may not need management:

```python
from contextlib import nullcontext

cm = open(path) if path else nullcontext(sys.stdout)
with cm as out:
    write_report(out)
```

This keeps one `with` block instead of duplicating the body across an `if`/`else`.

## closing and aclosing

`closing(thing)` calls `thing.close()` on exit, adapting objects that have a `close()` method but do not implement the context-manager protocol themselves. `aclosing(thing)` (3.10+) calls `await thing.aclose()` and is the recommended way to deterministically finalize async generators.

## Common Mistake: Swallowing Exceptions

The recurring contextlib error is silently discarding exceptions during cleanup. A generator-based manager returns control after `yield`; if its teardown raises or if `__exit__` returns a truthy value, the original error can be masked. `suppress` makes this explicit and intentional, which is fine, but an over-broad `suppress`, a `finally` that raises, or an `__exit__` that returns `True` by accident hides real failures. Suppress only the specific exception you understand, keep the suppressed region minimal, and never let cleanup code swallow the error that triggered it.
