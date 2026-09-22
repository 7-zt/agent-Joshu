# Repository

The Repository pattern provides a collection-like interface over a persistence mechanism, isolating domain logic from storage details. It mediates between the domain model and the data-mapping layer, offering methods like `get`, `add`, `remove`, and query methods that return domain objects.

The core value is that domain code works with domain objects through a clean interface, without knowing whether data comes from a database, file system, API, cache, or in-memory collection. This makes domain logic testable without real infrastructure and allows changing storage technology without modifying business rules.

## Structure

- **Repository interface** (Protocol or ABC): defines collection-like methods (`get_by_id`, `add`, `remove`, `list_by_criteria`).
- **Concrete Repository**: implements the interface using a specific technology (SQLAlchemy session, raw SQL, HTTP client, file system).
- **Domain objects**: pure domain entities or aggregates returned by the repository.
- **Application/service layer**: uses the repository interface, not the concrete implementation.

The dependency direction flows inward: domain code depends on the repository _interface_, and the concrete implementation depends on the domain objects it persists. This is [dependency inversion](../design-principles/dependency-inversion.md) applied to persistence.

## When The Pattern Fits

- Domain logic is complex enough that isolating it from persistence improves clarity and testability.
- Multiple storage backends are possible or likely (production database, test in-memory store, migration from one ORM to another).
- The application follows layered or hexagonal architecture with explicit boundaries.
- Business rules should be testable without database fixtures.
- The team benefits from a consistent, discoverable API for data access.

## When The Pattern Does Not Fit

- The application is a thin CRUD layer with minimal domain logic. Adding a Repository over an ORM adds indirection without reducing complexity.
- The ORM already provides a clean enough abstraction (e.g., Django's Manager/QuerySet for simple apps).
- Only one storage technology will ever be used, and the domain logic is trivial.
- Queries are highly dynamic or analytical. The Repository interface becomes a leaky abstraction over complex SQL: in such cases, a dedicated query service or CQRS separation serves better.
- The project is a script or small tool with a single data source.

## Common Implementation Issues

**Interface bloat.** Repositories that grow dozens of query methods lose their abstraction value. Keep the interface focused on [domain](../design-principles/ddd.md) operations, not a generic query builder.

**Leaky abstraction.** Methods that expose ORM-specific concepts (sessions, flush, lazy loading, query builders) defeat the purpose. Return fully-loaded domain objects. If callers need to page, filter, or sort, design those as repository parameters, not as ORM query chains leaking out.

**Transaction boundary.** Repositories typically do not own transactions. Transaction boundaries belong at the application/service layer or in a [Unit of Work](./unit-of-work.md). A repository that commits internally makes it impossible to coordinate writes across multiple aggregates.

**Eager vs lazy loading.** If the ORM loads related objects lazily, accessing them outside the repository boundary may fail or trigger unexpected queries. Decide the loading strategy at the repository boundary so that returned objects are complete for their intended use case.

**Testing.** Provide an in-memory implementation for unit tests of domain logic. Integration tests still need real database repositories to verify queries, constraints, and migrations.

## Relationship To Unit Of Work

Repository handles individual aggregate persistence through a collection-like API. [Unit of Work](./unit-of-work.md) handles transactional consistency across multiple repositories. They are complementary: Repository provides the collection interface, Unit of Work provides the commit/rollback boundary. Together they give the application layer control over both _what to persist_ and _when to persist_.

## Relationship To Facade

A repository is a domain-facing [Facade](./facade.md) over the persistence subsystem. The difference is intent: Facade simplifies a complex subsystem for any consumer; Repository specifically mediates between domain objects and storage. If your "repository" is really just simplifying a complex external API without domain objects, Facade may be the better name.
