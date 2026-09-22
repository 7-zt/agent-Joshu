# Python-specific code quality guidance

This reference collects Python-specific guidance for design principles, programming paradigms, and refactoring.

## Design principles

### Composition over Inheritance

Python supports multiple inheritance, and mixins are a common idiom: small classes that add a
slice of behavior to a host class. Used well, small, stateless, clearly named, depending only
on a documented interface of the host, they are reasonable. Used poorly they cause real
trouble:

- **Implicit state and initialization order.** A mixin that sets attributes or expects
  `super().__init__()` to be called in a particular order couples invisibly to the host and to
  other mixins. The method resolution order (MRO) determines what runs when, and a multi-mixin
  class can be hard to reason about.
- **Name collisions.** Several mixins defining or expecting the same attribute or method name
  interact in subtle ways through the MRO.

Keep mixins small, stateless, and named for what they add. If a mixin needs significant state
or a specific init sequence, that is a signal to use composition instead.

- Default to functions, constructor parameters, Protocols, strategy objects, and delegation for
  reuse and variation.
- Reserve inheritance for exception hierarchies, framework hooks, genuinely stable abstractions,
  and a few small, clear mixins.
- For shared code, prefer a module-level helper function or a composed collaborator over a base
  class whose only purpose is to hold the shared method.

### Domain-Driven Design Essentials

- Small projects can borrow just the ubiquitous language, value objects, and invariant thinking
  without the full layered architecture.
- Value objects map well to `dataclass(frozen=True)`, `attrs`, Pydantic models, or plain
  classes.
- An entity is not necessarily an ORM class. When persistence concerns distort the model,
  separate the domain model from the persistence model.
- Introduce repositories and unit of work only when you actually need a transaction boundary,
  a test double for storage, or isolation from the ORM, not by default.

### Deep Modules and Information Hiding

- Python has no hard `private`. Express boundaries with naming conventions (`_internal`), module
  structure, `__all__`, a deliberate public API, `property`, and `Protocol` rather than access
  modifiers.
- Prefer letting a module's internals be somewhat longer but locally clear over scattering logic
  across a dozen shallow helpers the reader must chase.
- An adapter layer is a natural deep module: it hides a third-party library's details behind a
  small interface, while still surfacing the errors and performance characteristics callers must
  account for. This is the structural basis of the anti-corruption layer and the
  Adapter pattern.

### Dependency Inversion and Dependency Injection

Python rarely needs the heavy apparatus that DIP acquired in other ecosystems. The lightweight
tools are usually enough:

- **Constructor and function parameters.** Pass the collaborator in. `def process(orders,
repository, clock):` inverts three dependencies with no ceremony.
- **`typing.Protocol`.** Define the narrow capability the policy needs structurally; any object
  with the right methods qualifies, without inheriting anything. This keeps interface conformance separate from
  inheritance.
- **Plain callables.** When the dependency is "a thing I call to get a value", a clock, an ID
  generator, a notifier, a function or `Callable` is a lighter abstraction than an interface
  object.
- **Default arguments for the common case.** `def fetch(url, client=httpx.get):` keeps the
  real default convenient while leaving a seam for tests to pass a fake.

Assemble the concrete wiring in one place: `main()`, a web app's startup, a framework entry
point. This _composition root_ is where high-level policy meets concrete detail; everywhere
else depends on abstractions.

- Prefer constructor parameters, function parameters, default arguments, small Protocols, and
  factory functions.
- Wire concrete dependencies in a single composition root.
- Wrap external clients in an adapter; let the core depend on a Protocol or callable.
- Manage dependency lifecycles (connections, files, locks) with context managers, kept out of
  the domain logic itself.

### DRY: Don't Repeat Yourself

- Deduplicate domain concepts, schemas, and protocols first, not local code shapes.
- For repeated schema/API/model definitions, use a single source of truth: `dataclass`, `TypedDict`, Pydantic, an OpenAPI spec, or code generation.
- For two functions with identical implementations but different business reasons, allow the duplication until the variation direction is clear.
- Prefer module-level functions, table-driven mappings, `Protocol`, and strategy functions over building a class hierarchy just to share code.
- Tables and dispatch maps are an excellent way to collapse genuinely repeated knowledge (one row per case) without inventing an inheritance tree.

### GRASP: General Responsibility Assignment Software Patterns

Behavior goes near the data that owns it (Information Expert). CLI and API handlers stay as thin Controllers, with rules in the core. Services, adapters, mappers, and policy functions are all reasonable Pure Fabrications. Once a variation point is genuinely identified, Protected Variations is realized with a `Protocol`, an adapter, or a deep module. Throughout, balance Low Coupling against High Cohesion rather than maximizing either alone.

### KISS: Keep It Simple

- Default to clear data structures, direct control flow, the standard library, and a small number of well-named functions.
- When complexity is unavoidable, isolate it inside a module, adapter, or deep module so callers stay simple.
- Don't create an abstraction for a single call site, and don't cram everything into one giant function either: both are failures of simplicity in opposite directions.
- Let formatters and linters handle style so human attention goes to boundaries and behavior.

### Law of Demeter

- Judge by structural knowledge and change propagation, not dot count.
- Give domain objects semantic queries: `order.shipping_postal_code()`,
  `invoice.is_overdue()`, rather than exposing nested fields for callers to walk.
- Let DTOs, dataclasses, and JSON-like data be traversed transparently.
- Treat deep mocks in tests as a signal: if a test must patch `a.b.c.d`, the production code
  probably knows too much about that path.

### Rule of Three

- First occurrence: write it inline and direct.
- Second occurrence: a little copy-paste is acceptable; resist the urge to extract.
- Third occurrence, or clear variation direction: extract. The result is often a module-level function with explicit parameters, a table-driven mapping, or a small `Protocol`, not necessarily a class.
- When you later realize you abstracted too early, prefer to inline / flatten / duplicate again, then look for the real axis of change. This is a normal refactoring move, not a failure.

### Test-Driven Development

- `pytest` suits small-step TDD well; keep fixtures direct and avoid building an invisible
  framework around them.
- For prototypes, UI, and complex external integrations, spike first, then backfill
  characterization or contract tests.
- `monkeypatch` is convenient but easy to overuse. Prefer passing fakes or stubs at the
  boundary over patching deep internals; the need to patch deep is a sign a dependency should
  have been injected.

### Tell, Don't Ask

- Give domain objects semantic command methods: `invoice.mark_paid()`, `order.cancel()`,
  `account.debit(amount)`. These maintain state transitions and invariants internally.
- Let data carriers, API schemas, ORM rows, and config objects expose attributes plainly.
- Use `property` to unify stored and derived values, but keep it cheap and side-effect free:
  do not hide I/O behind it.
- In a functional core, behavior need not be a method: a named function that takes the data and
  returns a decision (`def can_debit(account, amount) -> bool`) keeps logic and data together
  without forcing object-orientation. Tell, Don't Ask is about co-locating rules and data, not
  about insisting on methods.

### YAGNI: You Aren't Gonna Need It

- Satisfy the real call sites first with plain functions, explicit parameters, a `dataclass`, or a simple mapping.
- Wait for the second real point of variation before abstracting; before extracting, picture how cheap the future refactor would be: usually cheap enough to wait.
- For public APIs, persisted schemas, and external protocols, it is fine to stabilize the boundary early; that is not a speculative feature.
- Removing an unused extension point is _more_ aligned with YAGNI than keeping a "might be useful" abstraction.

## Programming paradigms

### Data-Oriented Design

- Prefer `dataclass` for plain data records; reach for `frozen=True` when the record is a value object with no identity (see the dataclass guidance in the stdlib references).
- Use `TypedDict` when data arrives as dicts (JSON, config) and you want shape-checking without converting to objects.
- Keep these structures as data: avoid attaching heavy business workflows to a dataclass; that is the "anemic by accident, then overloaded" antipattern. If real invariants appear, graduate to a class with methods.
- Establish a single source of truth for each schema rather than redeclaring the same shape in types, runtime validation, and docs.
- Transformations belong in module-level functions over the data, composable into pipelines, not in methods unless the behavior is intrinsic to the type.

### Declarative Programming

- Give each declarative structure a single source of truth. Do not write the schema once for the type checker, again for runtime validation, and a third time in the docs; derive or generate where possible.
- Parse external config into a typed object (`dataclass`, Pydantic model) at the boundary, then let the rest of the code work with concrete types instead of raw dicts.
- Complex rule tables still need tests. Declarative does not mean test-free; a transition table or permission matrix deserves coverage of its rows and its rejected cases.
- For declarative mechanisms that hide control flow, decorators, route registration, signal handlers, make sure the real execution path can still be traced so registration does not become invisible wiring.
- Keep an imperative escape hatch. The best declarative designs let the rare irregular case drop back to plain code instead of forcing every exception into the declaration's vocabulary. A routing table that maps paths to handlers stays declarative; a routing table that grows a `condition` mini-language to express "only on Tuesdays for premium users" has started reinventing a programming language badly. Declare the regular cases, and let an ordinary function handle the irregular one.

### Event-Driven Architecture

- In-process: a simple dict of `event_name -> list[callable]` is often all you need; do not pull in a message broker for local decoupling.

```python
from collections import defaultdict
from collections.abc import Callable

class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        self._subscribers[event].append(handler)

    def publish(self, event: str, payload: object) -> None:
        for handler in self._subscribers[event]:
            handler(payload)   # producer never names a consumer
```

This is the whole pattern at the smallest scale: the publisher knows the event name and the payload, never the handlers. Everything bigger, a broker, durability, async delivery, is the same shape with more infrastructure.

- Frameworks provide signals/hooks (Django signals, Flask signals, pytest hooks); prefer the framework's mechanism over a homegrown one when working inside it.
- Make event payloads plain data (`dataclass` / `TypedDict`) with a stable, versioned schema; this is the contract between producer and consumer.
- Design consumers to be idempotent and to log enough context (event ID, correlation ID) to trace failures.
- For async workflows, an emitted event usually becomes a task; retain ownership so its lifetime and failures are observed rather than firing and forgetting it.
- Keep the audit value honest: if events are your source of truth, treat the event schema with the same care as a database schema.
- Resist using events for flow that is really a direct request-response. If the producer needs the result, blocks on it, or only ever has one consumer, a plain function call is clearer than an event round-trip.

### Functional Core, Imperative Shell

- Entry layers may use argparse, Click, Typer, FastAPI, or Django, but core business functions should not depend on framework objects; pass plain data across the boundary.
- Carry boundary data in `dataclass`, `TypedDict`, a Pydantic model, or a plain dict, chosen by the project's complexity.
- Inject unstable dependencies, clock, randomness, filesystem, HTTP client, database session, as function arguments, constructor arguments, a small `Protocol`, or via the composition root, rather than reaching for them inside the core.
- The core should accept plain data and return plain data; the shell owns `with` / `async with` resource lifecycles.

### Imperative / Procedural Programming

- Carry imperative wiring in an explicit entry point, for example `main(argv: Sequence[str] | None = None) -> int`, and isolate it behind `if __name__ == "__main__":`.
- Let the entry layer parse arguments, load config, configure logging, build dependencies, and translate exceptions into exit codes. Core logic receives explicit parameters and stays importable and testable.
- Use `with` / `async with` for external resources rather than relying on garbage collection to release them.
- When a procedure grows past readability, split it by phase into named steps (`load_config()`, `build_client()`, `run_job()`) before reaching for a framework. Linear, well-named steps are a feature, not a smell.
- Resist the urge to wrap a simple three-line sequence in a class or a pipeline abstraction; straightforward imperative code is often the KISS-correct answer.

### Object-Oriented Programming

- Use `@dataclass` for simple data carriers; reach for a plain class when there are real invariants or a lifecycle to manage.
- For substitutability across a boundary, prefer a small `typing.Protocol` (structural typing) over a nominal base class. The collaborator just needs to provide the right methods.
- The **data model** (dunder methods) is how objects plug into the language: `__repr__`, `__eq__`, `__hash__` for value objects; `__iter__`, `__len__`, `__contains__` for containers; `__enter__`/`__exit__` for resources; `__call__` for callable strategies. Implement these only when the object genuinely has that semantic; do not invent undocumented dunders.
- `property` is for hiding storage differences or exposing a light derived value, not for hiding expensive side effects like I/O, a network call, or a database query.
- **Descriptors** (the protocol behind `property`, methods, ORM fields, validators) centralize attribute-access behavior. They are powerful and easy to overuse; keep them in framework/boundary code, not scattered through business logic. For plain field validation, prefer `__post_init__`, Pydantic, or a normal constructor.
- Keep mixins small, stateless, and clearly named. Multiple inheritance turns MRO into implicit complexity fast.

## Refactoring

### Duplicated Code

- For repeated schemas, API contracts, or models, establish a single source of truth: `dataclass`, `TypedDict`, Pydantic, an OpenAPI spec, or code generation, not three hand-maintained copies.
- Table-driven mappings and dispatch dicts collapse genuinely repeated knowledge (one row per case) without inventing a class hierarchy.
- Prefer extracting to a module-level function or a small strategy function over a base class whose only purpose is sharing code.
- Watch for the same domain rule appearing in a schema, a service, and a test fixture: a frequent agentic-coding pattern where three "copies" drift apart silently.

The transformation itself is usually Extract Function; the reverse, when you discover a wrong deduplication, is Inline Function.

### Long Function

- Extract phases into module-level functions or methods; the local variables they shared become parameters and return values, which often clarifies the data flow.
- Guard clauses (`if not valid: raise`) flatten nesting effectively and read well.
- Be mindful that each extracted function adds a call frame; in genuinely hot loops this is measurable, though for ordinary code clarity wins. Avoid extracting thin wrappers that add a frame without hiding complexity.
- A comprehension or generator can replace an accumulate-in-a-loop block, shortening the function without hiding anything.

### Primitive Obsession

- `dataclass(frozen=True)` is the default value object: immutable, comparable, cheap to define.
- `StrEnum` / `IntEnum` for fixed sets that also need a primitive representation at the boundary (serialization, storage).
- `TypedDict` when you must keep a dict shape (e.g. JSON at an API edge) but want the keys checked.
- `NewType` for a zero-overhead distinct alias when you want the type checker to stop `UserId` and `OrderId` from being interchangeable, without a runtime wrapper.
- Construct domain types at the system boundary (parsing input, reading the database) so the typed core never deals in raw primitives, mirroring the functional-core / imperative-shell split.

Primitive Obsession often co-occurs with Feature Envy (behavior that envies a primitive it cannot attach to) and Data Clumps; introducing the missing type frequently resolves several smells at once.

### Thin Wrapper / Trivial Helper

Function calls in Python are not free. Each call builds a frame, and the interpreter does real work for it. For most code this is irrelevant: clarity wins. But in hot paths and tight loops, a layer of thin wrappers around a per-element operation can show up in a profile. This is a secondary reason to avoid them, never the primary one: the main cost is always the cognitive overhead of indirection that buys nothing.
