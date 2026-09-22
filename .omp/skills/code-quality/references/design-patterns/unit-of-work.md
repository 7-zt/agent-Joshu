# Unit of Work

The Unit of Work pattern maintains a list of objects affected by a business transaction and coordinates writing changes to the database in a single atomic operation. It tracks which objects are new, modified, or removed, and commits all changes together, or rolls everything back if any step fails.

The primary value is transactional consistency: multiple repository operations that must succeed or fail together are coordinated by the Unit of Work, rather than each repository independently committing.

## Structure

- **Unit of Work** (interface): declares `commit()`, `rollback()`, and provides access to repositories.
- **Concrete Unit of Work**: wraps a database session/connection, tracks changes, implements commit/rollback.
- **Repositories**: accessed through the Unit of Work; operate within its transaction scope.
- **Application/service layer**: creates a Unit of Work, performs operations through its repositories, then commits or rolls back.

## When The Pattern Fits

- A business operation touches multiple aggregates that must be persisted atomically.
- The application has explicit service-layer methods that orchestrate domain logic.
- Transaction boundaries need to be visible and testable at the application layer.
- Multiple [repositories](./repository.md) share a session/connection, and their writes must be coordinated.
- The architecture benefits from separating "what changed" from "when to persist."

## When The Pattern Does Not Fit

- Each operation is a single-entity CRUD with no cross-aggregate consistency needs. The ORM session or a simple `with db.transaction():` block suffices.
- The framework already manages transactions declaratively (e.g., Django's `@transaction.atomic` for simple cases).
- The application is read-heavy with minimal write coordination.
- Distributed transactions across multiple services: Unit of Work applies within a single database boundary; cross-service consistency needs saga patterns or eventual consistency.
- The overhead of tracking changes explicitly exceeds the benefit for simple applications.

## Common Implementation Issues

**Scope.** A Unit of Work should live for exactly one business operation. Creating one at application startup and sharing it across requests causes stale data and concurrency bugs. In web applications, scope to the request; in workers, scope to the job.

**ORM integration.** ORMs like SQLAlchemy already implement Unit of Work internally; the Session tracks dirty objects and flushes on commit. Wrapping the ORM session in an explicit Unit of Work class is about making the boundary visible and testable at the application layer, not reimplementing change tracking. If the ORM's built-in session management is already explicit enough for your needs, an additional wrapper may add ceremony without value.

**Nested transactions.** Avoid deeply nested Units of Work. If sub-operations need independent commit/rollback, use savepoints explicitly rather than nesting Units of Work.

**Error handling.** Rollback must happen on any exception path. Context managers (`with uow:`) are the natural fit because `__exit__` calls rollback if an exception is active. This is also how [resource lifecycle](../programming-paradigms/resource-lifecycle.md) patterns work: pair acquire with release.

**Testing.** The Unit of Work boundary is a natural seam for testing. Mock or in-memory implementations let service-layer tests verify orchestration behavior without a database.

## Python example

In Python, Unit of Work naturally takes the form of a context manager:

```python
with unit_of_work() as uow:
    order = uow.orders.get(order_id)
    order.confirm()
    uow.payments.add(payment)
    uow.commit()
```

If an exception occurs before `commit()`, the context manager's `__exit__` calls `rollback()`. This makes the transaction boundary explicit and guarantees teardown after unexpected exceptions.

## Relationship To Repository

[Repository](./repository.md) provides the collection-like API for individual aggregates. Unit of Work coordinates _when_ those changes are persisted. They compose naturally: the Unit of Work owns or provides access to repositories, and all repository operations within a Unit of Work share its transaction scope. See also [DDD aggregate boundaries](../design-principles/ddd.md) for deciding what constitutes an aggregate.
