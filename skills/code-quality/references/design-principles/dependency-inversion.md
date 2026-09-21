# Dependency Inversion and Dependency Injection

Two related but distinct ideas, often confused:

- **Dependency Inversion Principle (DIP):** high-level policy should not depend on low-level
  detail; both should depend on an abstraction. The abstraction is defined by what the high-level
  code needs, not by what the low-level code happens to provide.
- **Dependency Injection (DI):** a technique where an object or function receives its
  dependencies from the outside rather than constructing or looking them up itself. DI is one
  way to achieve DIP, and it is also the main lever for testability and boundary isolation.

DIP is the design goal; DI is a mechanism. You can follow DIP without an elaborate framework,
and you can use DI without any "DI container" at all.

## High-level modules depend on abstractions

The problem DIP addresses: business rules that directly call a database driver, an HTTP client,
the system clock, or `random` are welded to those details. The policy can no longer be read,
tested, or reused without dragging the infrastructure along, and a change in the low-level
detail ripples up into the high-level rules.

Inverting the dependency means the high-level code states its need as an abstraction, "I need
something I can ask for the current time", "I need somewhere to save an order", and the
concrete implementation conforms to that need. The abstraction belongs to the
high-level side. It is shaped by what the policy requires, not by the full surface of the
low-level library. This is the same instinct as [Interface Segregation](./solid.md): keep the
seam narrow.

## When DI containers are justified vs overkill

A DI container (a framework that builds and wires your object graph from configuration or
annotations) solves a problem most Python projects do not have. Constructor injection and a
small composition root scale a long way. Containers earn their cost only when the object graph
is genuinely large and dynamic: many interchangeable implementations, complex lifecycle and
scoping requirements, configuration-driven wiring across many modules.

For typical applications, an explicit composition root is easier to read, debug, and trace than
a container. A global _service locator_ (a registry that code reaches into to fetch
dependencies) is worse than either: it hides the dependencies it satisfies, turning DI's
explicitness back into implicit global coupling. Prefer passing dependencies in.

## The testing benefit

DI is the cleanest path to testable code. When a function takes its clock, its repository, and
its HTTP client as parameters, a test passes in fakes or stubs directly: no monkeypatching of
module internals, no patching deep into implementation. This keeps tests coupled to the
boundary (the abstraction) rather than to the implementation, so refactoring the internals does
not break the tests. Over-mocking and deep `patch` targets are usually a symptom of dependencies
that were _not_ injected; fixing the seam fixes the test smell. See also
[tdd](./tdd.md).

## When NOT to invert

Inverting every dependency is its own kind of over-engineering. Do not invert:

- **Stable standard-library dependencies and pure functions.** Code that calls `json.dumps` or
  a pure helper does not need that hidden behind a Protocol; there is no varying implementation
  and nothing to fake.
- **Things that never vary and never need a test double.** An abstraction with exactly one
  implementation and no test seam is speculative ([YAGNI](./yagni.md)).

Invert the unstable, impure, or substitutable boundaries: external systems, time, randomness,
filesystem, network. Leave the stable core direct.
