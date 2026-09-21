# Type Hints

Type annotations in modern Python are not decoration and not a runtime enforcement mechanism; they are the machine-checkable part of an interface contract. A signature like `def fetch(url: str, timeout: float) -> Response` tells a caller, a type checker, and an editor what the function accepts and returns without anyone reading the body. The whole value of typing comes from treating annotations as contracts at boundaries, and from being honest about where the contract is strong (public APIs) and where it is deliberately loose (the messy edges where external data arrives).

## Type Annotations As Interface Contracts

The highest-value place to type is the public surface: module-level functions, class methods, dataclass fields, and anything imported across module boundaries. A typed signature is documentation that cannot drift from the code, an IDE autocomplete source, and a checkpoint where the type checker catches a misuse before it runs. The payoff scales with distance; the further a caller is from the implementation, the more the annotation is doing, because the caller will not read the body.

Inside a function, local variables mostly do not need annotations; the checker infers them, and `count = 0` gains nothing from `count: int = 0`. Annotate a local only when inference genuinely fails, when the variable carries an important domain concept worth naming in types, or when you need to stop an `Any` from propagating. Over-annotating locals adds noise without adding contract.

The practical consequence is a priority order. Type the public API completely and precisely. Type the cross-module seams. Type complex return values and data-model fields. Leave obvious locals to inference. This is what "full type coverage" should mean in practice, every boundary carries a contract, rather than a mechanical annotation on every binding.

## Type Parameters

Generics let a function or class be written once and stay type-safe across many concrete types. Python 3.12's PEP 695 syntax makes them a first-class language feature: `def first[T](items: Sequence[T]) -> T` and `class Box[T]:` declare type parameters inline, with no `TypeVar` import and no `Generic` base class. The annotation now says exactly what the old boilerplate said, the output type tracks the input type, but reads as plain syntax.

```python
def first[T](items: Sequence[T]) -> T:
    return items[0]


class Box[T]:
    def __init__(self, value: T) -> None:
        self._value = value

    def get(self) -> T:
        return self._value
```

The same code on a pre-3.12 floor must spell out the machinery explicitly:

```python
from typing import Generic, TypeVar

T = TypeVar("T")


def first(items: Sequence[T]) -> T:
    return items[0]


class Box(Generic[T]):
    ...
```

Generics earn their place when a real type relationship needs preserving: a container that should return what you put in, a function whose return type depends on its argument type. They hurt when reached for reflexively. If a function takes one concrete type and returns another, it is not generic; spelling it with a type parameter only obscures the actual types. The test is whether the parameter expresses a relationship the caller relies on: if removing it loses no information the caller uses, it was ceremony.

Bounds and constraints sharpen a generic when the type is not truly arbitrary. A `T` bound to a `Comparable` protocol (`def maximum[T: Comparable](items: Iterable[T]) -> T`) says "any orderable type" rather than "literally anything," which lets the body use `<` and the checker reject a type that does not support it. Reach for a bound when the generic body actually depends on a capability; leave the parameter unbounded when it genuinely does not care.

Note the hard version gate: PEP 695 syntax is a `SyntaxError` below 3.12. A project with a 3.11 floor must still use `TypeVar`/`Generic`. See [python-version](../project/python-version.md) for how the floor constrains available syntax.

## Type Aliases

A type alias gives a name to a type expression. Python 3.12's `type` statement makes this explicit:

```python
type UserId = int
type Handler = Callable[[Request], Awaitable[Response]]
type Json = dict[str, "Json"] | list["Json"] | str | int | float | bool | None
```

An alias adds clarity when a type expression is long, repeated, or carries domain meaning a bare structure hides. `type Handler = Callable[[Request], Awaitable[Response]]` tells a reader what the callable is _for_ in a way the raw signature does not, and a recursive alias like `Json` would be unreadable inlined at every use site.

The failure mode is an alias that hides structure the reader needs. Aliasing `int` to `Count` rarely helps: the reader gains a name but loses the knowledge that it is an `int` they can do arithmetic on, and the checker treats them as identical anyway, so it catches nothing. Use an alias when the name carries information the structure does not; avoid it when it merely renames something already clear.

When you want a _distinct_ type the checker enforces, so a `UserId` cannot be passed where an `OrderId` is expected even though both are `int` underneath, that is `NewType`, not an alias:

```python
from typing import NewType

UserId = NewType("UserId", int)
OrderId = NewType("OrderId", int)
```

`NewType` costs an explicit wrap at construction (`UserId(42)`) and buys a real checking benefit: mixing the two becomes a type error. An alias is a readability tool with zero checking effect; `NewType` is a safety tool with a small ergonomic cost. Choose by which one you actually need.

## Gradual Typing Strategy

Python's type system is gradual by design: typed and untyped code coexist, and `Any` is the seam between them. A sound strategy is not "type everything to the maximum" but "make the boundaries strict and contain the looseness." Public signatures and module edges should be fully and precisely typed. The messy interior, parsing arbitrary JSON, bridging an untyped third-party library, is where `Any` legitimately lives, and the goal is to _contain_ it: convert external data into a typed shape as early as possible, so `Any` does not leak past the adapter layer into the rest of the code.

```python
def load_config(raw: object) -> Config:
    # `raw` arrived from json.load and is effectively Any-shaped.
    # Validate and convert at the boundary; everything downstream
    # works with the typed Config, never the raw payload.
    data = _validate(raw)
    return Config(host=data["host"], port=data["port"])
```

The danger of `Any` is that it is contagious: any expression touching an `Any` value becomes `Any`, silently switching off checking for everything downstream. A single un-contained `Any` at the top of a call chain can disable the contract for an entire subsystem. Containment, narrowing it to a typed shape at the first opportunity, is what keeps the rest of the code honest.

`cast` is the explicit escape hatch for when you know more than the checker can prove: asserting a type after a runtime check the checker cannot follow, or narrowing a value the checker sees as broad. It generates no runtime check; it simply tells the checker "trust me here." That makes it a precision tool, not a way to silence errors in bulk: each `cast` is a small unchecked assertion, and a function full of them has lost the contract it was supposed to provide. Prefer a runtime check the checker _can_ follow over a `cast` whenever one exists:

```python
# Prefer this: the checker follows the narrowing itself:
if not isinstance(value, str):
    raise TypeError(value)
reveal_type(value)  # str

# Over this: an unchecked assertion the checker cannot verify:
value = cast(str, value)
```

## Protocol And Structural Subtyping

`Protocol` formalizes duck typing. A class satisfies a `Protocol` by having the right methods and attributes, with no explicit inheritance; the same "if it has `.read()`, it's file-like" reasoning Python always used, now made checkable.

```python
from typing import Protocol


class Readable(Protocol):
    def read(self, size: int = -1) -> bytes: ...


def consume(source: Readable) -> bytes:
    return source.read()
```

Any object with a matching `read` satisfies `Readable`, a file, a socket wrapper, an in-memory buffer, without any of them importing or subclassing it.

Choose `Protocol` when you want to accept anything matching a shape, especially types you do not own and cannot make inherit from your base. Choose an abstract base class (ABC) when you own the hierarchy, want to share implementation, and want explicit, registered membership. The rule of thumb: `Protocol` for accepting external shapes structurally; ABC for defining a closed hierarchy you control. Protocols also keep the dependency arrow pointing the right way; the _consumer_ defines the narrow interface it needs, instead of every producer being forced to import and subclass a base class. This is the typed expression of "depend on abstractions," and it is why a well-placed `Protocol` decouples modules that an ABC would have coupled.

## TYPE_CHECKING And Runtime Isolation

Some imports exist only to satisfy annotations and have no business running at import time; they may be heavy, or they would create a circular import. The `typing.TYPE_CHECKING` constant (always `False` at runtime, `True` to a type checker) isolates them:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import User


def load(user_id: int) -> "User": ...
```

The checker sees the import and validates the annotation; the interpreter never runs it. This is the preferred tool for breaking annotation-only import cycles and deferring expensive imports, and it is the right answer to most situations where `from __future__ import annotations` is reached for; it solves the forward-reference and cycle problem locally, without committing the whole module to stringized-annotation semantics. The one caveat: a name imported under `TYPE_CHECKING` does not exist at runtime, so any code that _reads_ annotations at runtime (frameworks, ORMs, serializers, DI containers) cannot resolve it the naive way. When runtime introspection matters, the version-specific behavior in [python-version](../project/python-version.md) governs how annotations should be read.

## collections.abc For Interface Boundaries

When typing what a function _accepts_, prefer the abstract types in `collections.abc` over concrete ones. A function that only iterates should take `Iterable[T]`, not `list[T]`; one that only looks things up should take `Mapping[K, V]`, not `dict[K, V]`:

```python
from collections.abc import Iterable


def total(values: Iterable[int]) -> int:
    return sum(values)
```

Typed as `Iterable[int]`, `total` accepts a list, a tuple, a generator, a set, or any custom iterable, and the signature simultaneously _promises_ it will only iterate, never index or mutate. Typing the parameter as `list[int]` would reject all those callers and over-claim what the function may do internally.

Use the concrete `list`/`dict` types for return values and for fields you own, where the caller benefits from knowing the exact type they are getting back. The principle mirrors interface design generally: accept the least specific type that supports what you need, return the most specific type you can commit to. Prefer the `collections.abc` forms (`Iterable`, `Sequence`, `Mapping`, `Callable`) over the deprecated `typing` aliases.

## Static Type Checking

Static type checkers read the annotations without running the code, catching contract violations before execution. They are the default "type checking" most projects mean, and several exist: pick one as the gate rather than running all of them by default.

- **mypy**: the mature, widely adopted checker with the deepest ecosystem and a strong strict mode. It is the mainstream choice, especially for libraries and external collaboration. Some projects run mypy alongside pyright to combine mypy's deep inference with pyright's faster, stricter feedback.
- **pyright**: Microsoft's fast, strict type checker. It is also the engine behind **Pylance**, the VS Code Python language server, so many editors surface pyright's results live as you type.
- **basedpyright**: a stricter, opinionated fork of pyright, useful as a strict cross-check. It and **ty** can both serve as the LSP in editors like Zed.
- **ty**: a fast, LSP-integrated checker built for a tight edit-feedback loop and CI. It is newer, so expect occasional behavior changes as it matures; treat adoption as a deliberate, watched choice.

A project picks one as its gate; a second may be enabled temporarily for a migration, a release, or to reconcile a tricky inference difference. The detailed selection and configuration tradeoffs live in the tooling references ([mypy](../tooling/mypy.md), [basedpyright](../tooling/basedpyright.md), [ty](../tooling/ty.md)). What matters at the spec level is that the _annotations_ are written to a single, coherent contract; the checker choice is a separate, project-level decision layered on top. Well-typed code does not bind itself to one checker; it expresses one clear contract that any conformant checker can verify.

## Runtime Type Checking

Static checking stops where untrusted data enters: JSON payloads, request bodies, config files, network responses. Runtime type checkers validate and convert that data into a typed shape at the boundary, so the rest of the code works with checked values rather than `Any`. Libraries like **Pydantic** and **msgspec** are the common representatives: you declare a model with annotated fields, pass the raw data in, and get back a validated instance (or a rejection with precise errors). The check runs when data crosses the boundary, not on every call.

This is complementary to static typing, not a replacement: the model definitions are themselves annotated, so a static checker still reasons about the fields, while the runtime check guarantees that the actual incoming data conforms. Use it at the edges where external data arrives; don't sprinkle it through internal code that is already statically typed and trusted.
