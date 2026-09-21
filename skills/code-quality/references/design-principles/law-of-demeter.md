# Law of Demeter

The Law of Demeter (LoD), also called the Principle of Least Knowledge, says that a unit
should only talk to its immediate friends and avoid reaching through one object to operate
on objects it returns. A method should interact with: its own object, objects passed to it as
arguments, objects it creates, and its direct components. It should not navigate a long chain
of intermediate objects to get at a distant target.

The point is not the number of dots in an expression. The point is how much a caller is
forced to know about the internal structure of objects it does not own. When a caller walks
`a.b.c.d`, it has hard-coded knowledge of three layers of structure, and any change to that
structure ripples outward to every caller that walked the same path.

## What problem it solves

Structural coupling. When code reaches through objects, it depends not just on its immediate
collaborator but on the shape of everything that collaborator exposes. A change deep in the
graph, renaming a field, inserting an intermediate object, changing a type, propagates to
distant, seemingly unrelated call sites. This is the classic symptom of shotgun surgery: a
small structural change forces edits in many places.

LoD pushes you to give your immediate collaborator a method that expresses _what you want_,
so the collaborator (which owns the structure) decides _how_ to get it. The knowledge of the
structure stays where the structure lives.

## The train wreck

A "train wreck" is a long chain of accessors strung together like coupled rail cars:

```python
zip_code = order.customer.address.zip_code        # train wreck
tax_rule = order.customer.account.region.tax_rule # train wreck
```

The calling code now knows that an order has a customer, a customer has an address, and an
address has a zip code. If `Address` is later split, or `Customer` gains an indirection, every
chain like this breaks. The fix is to ask the nearest object for the answer in domain terms:

```python
zip_code = order.shipping_zip_code()
needs_review = order.requires_tax_review()
```

The order now owns the traversal. Callers express intent; the structure stays hidden. This
connects directly to [Tell, Don't Ask](./tell-dont-ask.md): instead of pulling data out across
several hops to make a decision externally, you give the data owner a method that answers the
question.

## When it matters

- Domain objects whose chained access drives business rules
  (`order.customer.address.zip_code` deciding tax behavior).
- Callers that reach through a repository, client, or response object into its internal
  structure, coupling themselves to that internal layout.
- Tests that monkeypatch deep into an object graph: deep mocks are a smell that the code
  under test knows too much about distant structure.

In these cases, a structural change has a wide blast radius, and LoD is a useful lens for
finding where to add a semantic method.

## When it is overly strict

LoD becomes noise when applied mechanically as "count the dots, then ban them."

- **Fluent interfaces and builders.** `query.filter(...).order_by(...).limit(10)` is a
  designed chain. Each call returns the same conceptual object, not a deeper internal one.
- **Data traversal libraries.** Pandas, SQLAlchemy queries, and `pathlib.Path` chaining are
  idiomatic. `path.parent.parent / "config.toml"` is not a coupling problem.
- **Transparent data carriers.** Reading `response.json()["items"][0]["id"]` from a DTO or a
  JSON-like structure is plain data access, not structural coupling to behavior. A dataclass
  used purely as a data holder can be traversed directly.

The discriminator is always: _does the caller now know something about internal structure
that, if changed, would break it?_ If the chain is over a stable interface or transparent
data, there is no violation. If the chain encodes the private layout of objects that own
behavior and invariants, that is where LoD earns its keep.

## Forcing it the wrong way

The cure can be worse than the disease. Wrapping every chain in a forwarding method produces
a pile of trivial pass-through methods (`def zip_code(self): return self._address.zip_code`)
that add no semantics and just relocate the coupling one layer in. That is a shallow wrapper:
see [the deep modules discussion](./deep-modules.md). Only introduce a method when it expresses
a meaningful domain question, not merely to remove a dot.

## Related principles

LoD pairs naturally with [information hiding](./deep-modules.md): both reduce how much the
outside world depends on internal structure, and both limit how far a change can travel. It
also overlaps with [Tell, Don't Ask](./tell-dont-ask.md) and the GRASP
[Information Expert](./grasp.md) heuristic: all three push behavior toward the object that
holds the data it needs.
