# Exception Groups

`ExceptionGroup` (Python 3.11+, PEP 654) lets a single raise carry _multiple_ unrelated exceptions at once, and `except*` lets a handler select and process the members it cares about while letting the rest propagate. This solves a problem ordinary exceptions cannot: when several operations run together and more than one fails, a normal `try`/`except` can only surface the first failure and loses the others.

## The Problem It Solves

Sequential code fails one cause at a time, so a single exception is enough. Concurrent and batch code is different. If five downloads run together and three fail with different errors, there is no single "the" exception: discarding four of them hides real information. `ExceptionGroup` wraps them so the full set travels up the stack together, each retaining its own traceback.

## Syntax

An `ExceptionGroup` is a real exception holding a message and a sequence of contained exceptions:

```python
raise ExceptionGroup("download failures", [TimeoutError(...), ConnectionError(...)])
```

`except*` matches by type against the _members_ of the group. Each `except*` clause runs at most once, receiving a subgroup of the matching members; non-matching members continue propagating:

```python
try:
    await fetch_all(urls)
except* TimeoutError as eg:
    schedule_retry(eg.exceptions)
except* ConnectionError as eg:
    report_unreachable(eg.exceptions)
```

Unlike ordinary `except`, several `except*` clauses can fire for one group, because a group may contain several types. The bound name is always a group, never a bare exception.

## When It Is Appropriate

The natural source is `asyncio.TaskGroup` (3.11+): when multiple child tasks fail, the group raises an `ExceptionGroup` of their errors. Other fits are batch operations where you want every failure (validating all fields and reporting them together, processing a list of items and collecting all errors) and closing multiple resources where more than one teardown can fail.

## When Not To Use It

Do not wrap a single sequential error in a group. Linear flow that fails one cause at a time should raise and catch plain exceptions; a group there adds a layer of unwrapping for no benefit. `except*` is also not a stylistic upgrade of `except`; mixing the two on the same `try` is a syntax error, so introducing `except*` is a deliberate commitment that this block handles aggregated failures.

## Interaction With Existing Handlers

A plain `except SomeError` does **not** catch a `SomeError` hiding inside an `ExceptionGroup`; the group's type is `ExceptionGroup`, not `SomeError`. Code that adopts `TaskGroup` must convert its `except` clauses to `except*` or explicitly catch `ExceptionGroup`, or failures will pass through uncaught. Conversely, `except*` can catch `ExceptionGroup` itself but the construct is built around matching member types.

## Nesting Behavior

Groups nest. Splitting a group with `except*` preserves structure: matching members come out in a group that mirrors the original nesting, and the unmatched remainder propagates as another group with its own structure and tracebacks intact. You rarely build nested groups by hand; they arise when groups propagate through several `TaskGroup` layers. `BaseExceptionGroup` is the variant that can hold `BaseException` subclasses such as `KeyboardInterrupt`; `ExceptionGroup` is restricted to `Exception` and is what application code normally uses.

For richer per-error context within a group, attach notes to individual members with `add_note()` before raising, so each retains its own explanation alongside its traceback.
