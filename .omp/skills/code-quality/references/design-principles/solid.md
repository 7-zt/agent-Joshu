# SOLID

SOLID is a set of five object-oriented design principles, Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion, collected by Robert C. Martin under the banner of _dependency management_. Their shared purpose is to control coupling and the direction of change so a system stays flexible, robust, and reusable as it grows.

Two framing points before the principles themselves. First, the unit of application is not always a class. A "module" here can be a function, module, package, or service object; Python rarely needs the class-per-concept density that Java SOLID examples assume. Second, these are review _questions_, not templates. The value is in asking "what changes here, what's the contract, where's the dependency boundary," not in mechanically producing interfaces and factories. Used as a template, SOLID produces class explosion and indirection that violate [kiss.md](./kiss.md).

## Single Responsibility Principle

SRP is usually stated as "a module should have only one reason to change." The reason-to-change framing matters more than the popular misreading "a class should do one thing." A responsibility is tied to a _source of change_, an actor, a stakeholder, a rule that evolves independently. The right granularity comes from cohesion, not from minimizing what each unit does.

The smell SRP catches: one module that mixes business rules, presentation formatting, persistence, and external-API adaptation, so that a change to any one of them risks the others. The mistake people make _applying_ SRP: shattering a cohesive object into many anemic helpers, which scatters logic and lowers cohesion. Ask "does this code respond to more than one kind of rule, role, or external system?", not "does this function do more than one small thing?" At an entry point, parsing, config, logging, and dependency wiring can sit together; business rules should move out to a core.

## Open/Closed Principle

OCP: a stable core should be open to extension but closed to modification; you add behavior by adding new implementations, strategies, or config, not by reopening and editing the core every time. The modern, practical reading is conditional: an extension point is worth building only when the _direction_ of variation is stable and the variation actually recurs.

This puts OCP in direct tension with [yagni.md](./yagni.md). Building a plugin architecture for a hypothetical second implementation is speculative generality. The resolution: start with a simple branch or mapping; introduce a registry, dispatch table, or Protocol only after a real second (ideally third; see [rule-of-three.md](./rule-of-three.md)) variation appears. In Python the extension mechanism is usually a registry, entry points, a config-to-function mapping, a `Protocol`, a decorator, or a strategy function, not necessarily an inheritance hierarchy, which tends to produce fragile base classes.

## Liskov Substitution Principle

LSP: a subtype must be usable anywhere its base type is expected, without breaking the program's expectations. The key word is _behavior_, not signature. Matching method names and types is necessary but not sufficient; the subtype must also honor the base's preconditions (not require more), postconditions (not promise less), invariants, and exception semantics.

Classic violations: a subclass that narrows what a method accepts, or turns an inherited method into a no-op or `raise NotImplementedError`, or subclasses purely to reuse code with no real _is-a_ relationship. In Python, duck typing and `Protocol` express only structure; the behavioral contract still lives in tests and documentation. When you only want to reuse an implementation, prefer composition, a small mixin, or a helper function over inheritance, so you never make a substitutability promise you can't keep (see [composition-over-inheritance.md](./composition-over-inheritance.md)).

## Interface Segregation Principle

ISP: clients should not be forced to depend on methods they do not use. A wide "god interface" couples every client to every change and forces test doubles to implement irrelevant methods. Split interfaces along what real callers actually need.

In Python this rarely means Java-style interface classes. Use small `Protocol`s, plain callables, module-level functions, or a parameter object that carries only the capability a caller needs. Don't manufacture an interface per function; an internal one-off call needs no declared interface: just have the function accept only the object it truly uses. A good heuristic: when a test double has to stub methods the code under test never calls, the interface is too wide.

## Dependency Inversion Principle

DIP: high-level policy should not depend on low-level detail; both depend on an abstraction, and the abstraction is defined by what the high-level code needs (not leaked up from the detail). This keeps business rules free of database, HTTP, filesystem, clock, randomness, and framework specifics. Dependency Injection is one _technique_ for achieving DIP: passing dependencies in from outside rather than constructing or looking them up internally. See [dependency-inversion.md](./dependency-inversion.md) for the full treatment.

The common error is equating DIP with a DI container, or inverting dependencies on stable standard-library code that will never need substitution. In Python, prefer constructor parameters, function parameters, small `Protocol`s, and a factory function, wiring concrete dependencies at a composition root (`main()`, app startup, framework entry).

## SOLID tensions and overuse

Each principle pulls toward more structure: more interfaces, more indirection, more injection points. Applied without judgment, the set produces exactly the over-engineered, hard-to-read code that [kiss.md](./kiss.md) and [yagni.md](./yagni.md) warn against. Specific tensions: OCP vs YAGNI (extension points vs speculation), ISP vs simplicity (interface count), DIP vs simple wiring (indirection vs traceability). The discipline is to apply SOLID where change is frequent and costly, long-lived business systems, libraries, frameworks, SDKs, plugin points, and to leave small scripts and stable modules alone. Treat SOLID as a set of review questions about change and coupling, and let Python's functions, Protocols, composition, and parameter injection be the default answers rather than ABCs and containers.
