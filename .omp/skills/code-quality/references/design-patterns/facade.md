# Facade

## Intent

Provide a single, simple interface to a complex subsystem. A facade defines a higher-level entry point that makes the subsystem easier to use, without preventing callers that need finer control from reaching the underlying parts.

## Problem it solves

A subsystem accumulates many classes and steps that must be coordinated in the right order: fetch the customer, create an invoice from order lines, publish an event, update a ledger. If every caller orchestrates these steps itself, the coordination logic is duplicated, the calling code is coupled to internal structure, and changing the workflow means editing every call site. A facade names the common use case ("invoice this order") and owns the orchestration in one place.

## Structure and participants

- **Facade**: exposes a small set of high-level operations and delegates to subsystem objects, sequencing their interactions.
- **Subsystem classes**: the real work; they don't know about the facade and remain usable directly.

The facade adds no new functionality of its own; it composes existing pieces into a convenient surface. Callers depend on the facade; the facade depends on the subsystem.

## When to use

- A multi-step workflow or third-party SDK is used the same way in several places, and you want one named entry point.
- You want to decouple callers from the subsystem's internal structure so it can evolve behind a stable surface.
- You are layering a system and want each layer to present a minimal interface to the one above.

## When harmful

- **Hiding complexity callers genuinely need.** If callers must control retries, pagination, partial failure, or transaction boundaries, a facade that smooths these away forces them to bypass it or work around it. Expose what callers must reason about.
- **Shallow facade.** If it only forwards one call to one subsystem method, it adds a layer and a name without hiding anything. The cost (an extra hop, a place to look) exceeds the benefit.
- **God object.** A facade that grows to cover every operation in the system becomes a dumping ground, coupling unrelated use cases and accumulating dependencies on everything.

## Failure modes

- The facade leaks subsystem types in its signatures, so callers end up coupled to internals anyway and the abstraction is illusory.
- Error handling collapses distinct subsystem failures into one opaque exception, so callers can't respond appropriately.
- The facade becomes the only allowed path and blocks legitimate advanced use, instead of being the convenient default while direct access remains possible.

## Python example

A module is itself a natural facade: a package's `__init__.py` with a curated `__all__` exposes a few entry-point functions while the implementation lives in private submodules.

A client class works well when the use cases share state or dependencies:

```python
class BillingClient:
    def __init__(self, customers, invoices, events) -> None:
        self._customers = customers
        self._invoices = invoices
        self._events = events

    async def invoice_order(self, order: Order) -> Invoice:
        customer = await self._customers.get(order.customer_id)
        invoice = await self._invoices.create(customer, order.lines)
        await self._events.publish(InvoiceCreated(invoice.id))
        return invoice
```

A good facade is a _deep module_: a small interface in front of substantial internal complexity. That depth is what makes it worth having; it hides real work, not just a few lines.

## Relationship to other patterns

[adapter.md](./adapter.md) changes an interface to match what a caller expects; Facade defines a _new, simpler_ interface over many objects; Adapter wraps one thing to fit, Facade wraps many to simplify. A facade often fronts a [abstract-factory.md](./abstract-factory.md) or coordinates objects built by factories. The "deep module" idea behind a good facade connects to information-hiding principles in the design-principles references. Compare Mediator, which also centralizes interaction but lets the coordinated objects talk back through it, whereas a facade is a one-directional simplifying entry point.
