# Adapter

## Intent

Convert the interface of an existing object into the interface a caller expects, so two things that were not designed to work together can collaborate without either side changing.

## Problem it solves

You depend on a class, a third-party SDK, a legacy module, an external service client, a raw database row, whose interface does not match what your code needs. You could rewrite your callers to speak the foreign interface, but that spreads the dependency everywhere and couples your domain to a shape you do not control. Adapter confines the mismatch to one wrapping object. Callers see a stable interface you own; the adapter does the translation.

This is the runtime expression of the Dependency Inversion Principle: high-level code depends on an abstraction it defines, and the adapter makes a concrete external thing satisfy it.

## Structure and participants

- **Target**: the interface the client wants to use (in Python, usually a `Protocol` or an informal duck-typed contract).
- **Adaptee**: the existing object with the incompatible interface.
- **Adapter**: an object that implements Target and forwards to the Adaptee, translating data and errors across the boundary.
- **Client**: code that uses Target and never sees the Adaptee.

The classic distinction is **object adapter** versus **class adapter**. An object adapter _holds_ the adaptee as an attribute and delegates to it; a class adapter _inherits_ from both the target and the adaptee. Object adapters are favored almost everywhere because they compose rather than entangle inheritance, work with adaptee instances you did not create, and can adapt several adaptees. Class adapters need multiple inheritance and bind you to the adaptee's class at definition time. In Python, prefer the object adapter; reach for inheritance only when you genuinely need to be a subtype of the adaptee.

## When to use

- Isolating a third-party SDK, legacy API, or external service so the rest of the code depends on your interface, not theirs.
- Normalizing several different backends (payment providers, storage drivers, notification channels) behind one contract.
- Converting data representations at a system boundary, wire formats, ORM rows, protocol messages, into domain types.

## When NOT to use

- The interfaces already match, or duck typing makes the object usable as-is. A wrapper that only renames methods is pure overhead.
- You actually want a _new_ interface designed around your needs, not a translation of an existing one; then write that interface directly rather than dressing up the old one.
- The adaptee is yours and you can change it. Fix the source instead of permanently wrapping it.

## Failure modes

- **Leaky or pass-through adapters** that forward calls one-to-one with no translation, adding a hop and a file to navigate for nothing.
- **Over-hiding**: swallowing the adaptee's errors, retries, timeouts, and performance characteristics so callers cannot react correctly. An adapter should translate failure semantics, not erase them. Map `StripeError` to a domain `PaymentDeclined`; do not return `None`.
- **Fat adapters** that accumulate business logic. An adapter translates; once it makes decisions, it has become something else and should be named accordingly.

## Python example

Hold the adaptee and translate at the boundary:

```python
class PaymentGateway(Protocol):
    async def charge(self, order: Order) -> PaymentResult: ...


class StripeGateway:
    def __init__(self, client: StripeClient) -> None:
        self._client = client

    async def charge(self, order: Order) -> PaymentResult:
        try:
            response = await self._client.create_charge(order.total_cents)
        except StripeError as exc:
            raise PaymentDeclined(order.id) from exc
        return PaymentResult.from_stripe(response)
```

Adapters need not be classes. A thin function that maps a foreign dict into a domain `dataclass` is an adapter. Duck typing also removes the need for many adapters: if an object already has the methods you call, you do not need a wrapper just to satisfy a nominal interface.

## Relationship to other patterns

Adapter changes an interface without changing behavior; [decorator.md](./decorator.md) keeps the interface and adds behavior; a [facade.md](./facade.md) defines a new simpler interface over many objects rather than translating one. Adapter and [strategy.md](./strategy.md) often appear together: the `Protocol` an adapter satisfies is frequently the same abstraction strategies plug into. For type-driven translation of values, `functools.singledispatch` can serve as a lightweight adapter dispatch.
