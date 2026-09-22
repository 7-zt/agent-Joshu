# Async and Concurrency

Concurrency lets a program make progress on several things at once. Async concurrency in Python (`async`/`await`, `asyncio`) is one model among several; it interleaves many I/O-bound tasks on a single thread by suspending at `await` points. It is not parallelism, and it is not free: it splits your code into a coloured world where async functions can only be awaited from other async functions. The central design question is not "how do I make this async" but "does every concurrent task have a clear owner, a lifecycle, and an error-handling policy."

## Structured concurrency

The most important idea in modern async design is structured concurrency: a group of related tasks shares a single scope, and that scope does not exit until every task in it has finished. `asyncio.TaskGroup` (Python 3.11+) is the canonical tool, and the structural analogue of "nurseries" in Trio.

```python
async def fetch_all(urls: list[str]) -> list[Response]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(u)) for u in urls]
    return [t.result() for t in tasks]
```

The `async with` block does not complete until all child tasks complete. If any task raises, the group cancels the rest and propagates the error. This gives concurrent code the same guarantee a normal block has: when you leave the scope, nothing you started is still running in the background. Tasks have a clear owner (the group) and a clear lifetime (the block).

## Cancellation and timeouts

Cancellation is delivered as a `CancelledError` raised inside the task at its next `await`. It is part of the control-flow mechanism, not an ordinary error to swallow. If you catch it to run cleanup, re-raise it afterward: suppressing it breaks timeouts, `TaskGroup` shutdown, and cancellation propagation throughout the system.

```python
try:
    await do_work()
except asyncio.CancelledError:
    await cleanup()
    raise  # always re-raise
```

Timeouts are expressed with `asyncio.timeout()` (3.11+) or `wait_for`, which cancel the wrapped operation when the deadline passes. Design long-running operations so they reach an `await` point regularly, or cancellation cannot take effect.

## Error propagation

In a `TaskGroup`, multiple tasks can fail at once, so errors surface as an `ExceptionGroup`. Handle them with `except*`:

```python
try:
    async with asyncio.TaskGroup() as tg:
        ...
except* ValueError as eg:
    ...
```

For ordinary linear flow you do not need `except*`; a single awaited coroutine raises a single exception normally. Reach for exception groups only where genuine concurrent failure is possible.

## Backpressure

When a producer outpaces a consumer, unbounded queuing turns into unbounded memory growth. Backpressure is the mechanism that slows the producer to the consumer's rate. Use bounded queues (`asyncio.Queue(maxsize=...)`) so a full queue blocks the producer, or a semaphore to cap concurrent in-flight work. Designing for backpressure is what separates a fan-out that degrades gracefully under load from one that exhausts memory or downstream connection limits.

```python
sem = asyncio.Semaphore(10)  # at most 10 requests in flight at once


async def fetch_limited(url: str) -> Response:
    async with sem:
        return await fetch(url)


async def fetch_all(urls: list[str]) -> list[Response]:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch_limited(u)) for u in urls]
    return [t.result() for t in tasks]
```

Without the semaphore, a list of 100,000 URLs would open 100,000 sockets at once and exhaust file descriptors or the remote server's limits. The cap turns "all at once" into "ten at a time," which is what backpressure buys you.

## Async resource ownership

A resource acquired inside a task is released only if the task completes or is cancelled cleanly, so async resources must be owned with `async with` and cleaned up on the cancellation path too. Async generators that hold resources need `contextlib.aclosing()` to guarantee their finalization, because a suspended generator may otherwise never resume. This is the async face of [resource-lifecycle.md](./resource-lifecycle.md).

## When async helps, when it hurts

Async is the right tool for I/O-bound work with many concurrent operations: network requests, database queries, many simultaneous connections, fan-out to several services. The single thread spends its time waiting on I/O, and async lets it overlap that waiting.

Async adds cost without benefit when the work is CPU-bound: heavy computation blocks the single event loop and starves every other task; use processes or threads for that. It is also overhead for simple sequential scripts: if there is no concurrency to exploit, async only adds the coloured-function constraint and a runtime to manage. Do not make a codebase async because async is fashionable; make it async because it has real I/O concurrency to exploit.

## Common mistakes

- **Fire-and-forget.** Calling `create_task()` without keeping a reference and without a group. The task can be garbage-collected mid-flight, and its exceptions vanish. Every task needs an owner.
- **Unhandled task exceptions.** A bare task whose exception is never retrieved fails silently. `TaskGroup` solves this by design; lone tasks need explicit `add_done_callback` handling or awaiting.
- **Blocking the event loop.** Calling synchronous blocking I/O (`requests.get`, `time.sleep`, a blocking DB driver) inside a coroutine freezes every other task. Use async equivalents, or push the blocking call to a thread with `asyncio.to_thread()`.
- **Swallowing `CancelledError`**: covered above; it quietly breaks the whole cancellation system.

The throughline: concurrency is manageable when every task has an owner and a scope. Structured concurrency, honest cancellation, and backpressure are how you keep "many things at once" from becoming "many things you can no longer account for."
