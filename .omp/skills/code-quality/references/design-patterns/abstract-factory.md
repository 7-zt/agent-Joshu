# Abstract Factory

## Intent

Create families of related objects that must be used together, without coupling callers to the concrete classes. The caller picks one factory; everything it produces is guaranteed to belong to the same matching set.

## Problem it solves

Some objects only make sense in combination. An S3 reader pairs with an S3 writer; a dark-theme button pairs with a dark-theme menu; a Postgres connection pairs with a Postgres dialect and migration runner. If callers assemble these pieces individually, nothing stops them from mixing a Postgres reader with a SQLite writer. Abstract Factory makes the family the unit of choice: select the backend once, and every product it hands back is consistent.

This is the distinguishing constraint. [factory.md](./factory.md) answers "which one concrete class do I build?" Abstract Factory answers "which whole _set_ of classes do I build, such that they fit together?"

## Structure and participants

- **Abstract factory**: declares creation methods for each product in the family (`make_reader`, `make_writer`).
- **Concrete factories**: one per family (`S3Storage`, `LocalStorage`), each producing products from its own variant.
- **Abstract products**: the interfaces callers depend on (`Reader`, `Writer`).
- **Concrete products**: family-specific implementations.

The caller holds an abstract factory and calls its creation methods; it never names a concrete product.

## When to use

- A whole set of products must switch together: UI toolkit themes, database backends, cloud-provider clients, transport stacks.
- Several objects must share the same configuration, credentials, or lifecycle, and mixing variants would be a bug.
- Tests need to swap an entire group of dependencies (a fake storage family) for a real one.

## When NOT to use

- There is only one product, or one family. Then you only need a [factory.md](./factory.md), or a plain constructor.
- The "family" constraint isn't real; the products don't actually have to match. Grouping them adds ceremony without preventing any mistake.
- It quietly grows into a general service locator that builds anything on request, losing the family guarantee that justified it.

## Failure modes

- A factory object, abstract product, and concrete product tree built for a single family: pure overhead.
- Blurred family boundaries, so the factory accumulates unrelated creation methods and becomes a god object.
- Products that secretly reach for global state instead of the factory's shared config, breaking the consistency guarantee the pattern exists to enforce.

## Python example

A `Protocol` plus a selector function usually expresses the whole pattern without an interface forest:

```python
class StorageBackend(Protocol):
    def make_reader(self) -> Reader: ...
    def make_writer(self) -> Writer: ...


def build_storage(profile: StorageProfile) -> StorageBackend:
    if profile.kind == "s3":
        return S3Storage(profile)
    return LocalStorage(profile)
```

Other idiomatic shapes:

- **Module as factory**: a `s3_backend` module and a `local_backend` module, each exposing `make_reader`/`make_writer`, selected by importing the right one in the composition root.
- **Dataclass profile**: bundle the family's shared config in one frozen object and pass it to each product.
- **Composition root**: assemble the matching set once at startup and inject it, rather than scattering factory calls.

Use duck typing or `Protocol` when the factory contract needs static checking; neither requires nominal inheritance.

## Relationship to other patterns

Abstract Factory is a [factory.md](./factory.md) scaled up from one product to a coordinated family. Its products are often configured via [builder.md](./builder.md) when individual construction is complex. The factory choice frequently coincides with selecting a [strategy.md](./strategy.md) for the whole subsystem. When the family of objects also needs a simplified combined entry point, wrap it behind a [facade.md](./facade.md).
