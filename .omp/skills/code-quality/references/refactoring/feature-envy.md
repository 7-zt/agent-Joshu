# Feature Envy

## What it is

Feature Envy is a method that seems more interested in another object than the one it belongs to. It reaches into a second object, pulls out several pieces of its data, and does the calculation that the other object should have done itself. The method "envies" the features of the class it is operating on. The classic shape is a method on `A` that calls `b.x`, `b.y`, `b.z` and combines them, while barely touching `A`'s own state.

The smell matters because it puts behavior in the wrong place. The logic depends on another object's internals, so when those internals change, this distant method breaks; coupling that should not exist. And the object that owns the data is left anemic, a bag of fields with the operations that belong to it living elsewhere. This is the inverse of the principle that behavior should live with the data it needs (see [tell-dont-ask](../design-principles/tell-dont-ask.md) and GRASP's Information Expert in [grasp](../design-principles/grasp.md)).

## The signal

Look at a method and count whose data it touches. If it accesses another object's fields and methods more than its own, that is the envy. A reliable concrete signal is a sequence of `other.a`, `other.b`, `other.c` feeding a computation; especially when those accesses are the train-wreck chains of [law-of-demeter](../design-principles/law-of-demeter.md), where the caller is reaching through structure it should not know about.

```python
# Envious: the method lives on Order but is all about customer.address
class Order:
    def shipping_label(self) -> str:
        c = self.customer
        return f"{c.address.street}, {c.address.city} {c.address.postal_code}"
```

The computation is entirely about the address; it wants to live on `Address` (or `Customer`), not `Order`.

## What to do

The usual remedy is [move-function.md](./move-function.md): move the method to the object whose data it envies. If only part of the method is envious, first [extract-function.md](./extract-function.md) to isolate that part, then move the extracted piece. After the move, the original call site asks the right object to do the work (`address.formatted()`), and the dependency on internal structure disappears.

The guiding question is the Information Expert one: which object holds the data this logic needs? Put the logic there. The result is usually less coupling, a richer object, and call sites that read as requests rather than interrogations.

## When it is acceptable

Feature Envy is a heuristic, not a law. Several legitimate patterns look like envy and should be left alone:

- **Utility and pure functions.** A function whose entire job is to operate on data passed to it, a formatter, a serializer, a calculation over a value object, is _supposed_ to use that data. Moving it onto the data class is not always better, especially in a functional style where behavior lives in named functions that take data as input. The functional core deliberately separates data from the functions over it.
- **Cross-cutting concerns.** Logging, metrics, authorization, and transaction handling necessarily touch other objects' data to do their job. That is their nature, not a misplacement.
- **Data transfer and mapping.** A mapper that reads from object `A` and builds object `B` will, unavoidably, access a lot of `A`'s fields. That is the point of a mapper; it is not envy.
- **The data is a transparent record.** Pulling fields out of a `dataclass` or DTO that has no invariants is fine; there is no behavior being stranded, because the record was never meant to own behavior. The Tell-Don't-Ask exception for read models and DTOs applies here.
- **Moving would create worse coupling.** If the "owning" object is a stable third-party type or a class you do not want to bloat with one caller's concern, leaving the logic where it is may be the lesser cost.

The judgment is whether the behavior depends on another object's _internals_ (move it) or merely _consumes its public data as input_ (often fine). Pattern Primitive Obsession often hides envy: when behavior envies a primitive that cannot own methods, the real fix is to introduce a value object that can; see [primitive-obsession.md](./primitive-obsession.md).
