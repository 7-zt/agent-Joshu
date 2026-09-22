# Decorator Pattern

This document covers the Gang of Four _structural_ Decorator pattern: wrapping an object to add behavior.

## Intent

Attach additional responsibilities to an object dynamically by wrapping it in another object that shares the same interface. Decorators provide a flexible alternative to subclassing for extending behavior, and they can be composed and stacked at runtime.

## Problem it solves

You have a component and several optional, independent behaviors you might add to it: buffering, compression, encryption, metrics, retries. Subclassing every combination explodes: `BufferedCompressedStream`, `BufferedEncryptedStream`, and so on. Decorator lets each behavior be its own wrapper that conforms to the component's interface and delegates to the wrapped object. You compose the behaviors you want at runtime by nesting wrappers, in whatever order and combination the situation needs.

## Structure and participants

- **Component**: the interface shared by raw objects and their decorators.
- **Concrete component**: the base object being decorated.
- **Decorator**: holds a Component, implements Component, and delegates to the wrapped object, adding behavior before or after delegation.
- **Concrete decorators**: each adds one responsibility.

Because every decorator implements the same Component interface and holds a Component, decorators and base objects are interchangeable and can nest arbitrarily. `Compress(Encrypt(FileStream(path)))` is itself a `Component`.

## When to use

- You need to compose independent behaviors at runtime, in varying combinations or order.
- The behaviors are cross-cutting and stable: logging, caching, retry, auth, validation, metrics, transaction boundaries.
- Subclassing for every combination would explode the class count.

## When NOT to use

- There is one fixed behavior to add and no runtime composition; a plain `@decorator` function, or just inlining the behavior, is simpler than an object-decorator hierarchy.
- The added behavior needs resource lifecycle (acquire/release). A context manager expresses setup and teardown far more clearly than a decorator.
- You are reaching for decorators to add real business logic. Decorators should stay thin; business rules belong in the component.

## Failure modes

- **Hidden control flow**: stacked decorators obscure the order of execution, where exceptions are caught, and where time is spent. Deep stacks become hard to debug.
- **Lost metadata**: forgetting `functools.wraps` breaks `__name__`, docstrings, and signatures.
- **Behavior drift**: a decorator that subtly changes the component's contract (return types, raised errors) so wrapped and unwrapped objects are no longer substitutable.
- **Performance surprise**: each layer adds a call frame and possibly I/O; a metrics-plus-retry-plus-cache stack can cost more than the operation.

## Python example

Python treats functions as first-class objects and has dedicated `@decorator` syntax, so a function decorator expresses the same wrapping idea directly:

```python
def with_metrics(handler: Handler) -> Handler:
    @functools.wraps(handler)
    async def wrapped(request: Request) -> Response:
        with timer("handler.duration"):
            return await handler(request)
    return wrapped

@with_metrics
async def handle_request(request: Request) -> Response:
    return await process(request)
```

## Relationship to other patterns

[adapter.md](./adapter.md) changes an interface. Decorator keeps the same interface and adds behavior. Proxy also wraps with the same interface but controls _access_ such as lazy loading or permissions rather than enriching behavior. The structures are nearly identical and differ in intent. Chained decorators resemble a pipeline; for sequential request handling, see Chain of Responsibility. When the behavior is resource lifecycle, prefer a context manager over a decorator.
