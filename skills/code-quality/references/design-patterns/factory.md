# Factory Method

## Intent

Decouple object creation from the code that uses the object. Callers ask for a product by intent ("give me a parser for this format") without naming a concrete class or knowing how it is assembled.

## Problem it solves

Construction logic tends to leak into callers: which concrete class to pick, how to validate inputs, how to wire dependencies, what defaults to apply. When the same `if kind == ...: return SomeClass(...)` block appears in several places, a change to construction means editing every call site. Factory Method centralizes that decision in one place and gives it a name.

## Structure

In the classic Gang of Four form, a `Creator` declares a factory method that returns a `Product`, and subclasses override it to decide the concrete product. The participants are the abstract creator, concrete creators, the product interface, and concrete products.

In Python this full hierarchy is rarely the right shape. The "creator" is usually a plain function, a `classmethod`, or a registry lookup. The subclass-overrides-a-method form only earns its place when a framework defines the creation step as an extension point and your subclass genuinely needs to override it.

## When to use

- Concrete type depends on a runtime value: file format, protocol name, config entry, plugin name.
- Construction involves validation, dependency wiring, or default-strategy selection you don't want duplicated at call sites.
- There are multiple real implementations today, or a confirmed extension point (plugins, entry points).

## When NOT to use

- There is a single implementation and construction is trivial: just call the constructor.
- A one-line `if` or direct instantiation would do. Wrapping it in an abstract-creator hierarchy adds indirection for no variation.
- Everything that builds an object gets named `Factory`, diluting the concept until it means nothing.

## Failure modes

- A Java-style abstract creator / concrete creator tree where a function would do, forcing readers through layers of subclasses to find one `return`.
- Factory functions that quietly swallow unknown kinds and return a default, hiding configuration errors. Raise a clear domain error instead.
- Factories that grow side effects (logging, I/O, registration) so construction is no longer pure or predictable.

## Python example

Prefer a plain factory function:

```python
def make_parser(kind: str) -> Parser:
    match kind:
        case "json":
            return JsonParser()
        case "yaml":
            return YamlParser()
        case _:
            raise UnknownParserError(kind)
```

For configuration- or plugin-driven creation, a registry keeps the factory open to extension without editing the dispatch:

```python
_PARSERS: dict[str, Callable[[], Parser]] = {}

def register_parser(kind: str, factory: Callable[[], Parser]) -> None:
    _PARSERS[kind] = factory

def make_parser(kind: str) -> Parser:
    try:
        return _PARSERS[kind]()
    except KeyError as exc:
        raise UnknownParserError(kind) from exc
```

`classmethod` alternative constructors (`Model.from_dict`, `datetime.fromtimestamp`) are Python's most common factory form: the class owns named ways to build itself.

## Relationship to other patterns

[abstract-factory.md](./abstract-factory.md) extends this idea to whole families of products that must vary together. [builder.md](./builder.md) addresses complex step-by-step construction rather than which-class-to-pick. When the product is selected by a runtime value that also drives later behavior, the choice may really belong with [strategy.md](./strategy.md). `functools.singledispatch` is a related Python mechanism when creation varies by argument type.
