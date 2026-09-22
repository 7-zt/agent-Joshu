# Domain-Driven Design Essentials

Domain-Driven Design (DDD) is an approach to modeling complex business domains around the
language and boundaries of the domain itself, rather than around database tables or framework
folders. This document covers the concepts that most improve code organization and naming. It
is not a substitute for the full body of DDD literature, and most projects only need a subset.

The central premise: in genuinely complex business software, the hard part is not the
technology but the domain: its vocabulary, its rules, its invariants, and the boundaries
between subdomains. Code that mirrors those concepts is easier to discuss, change, and keep
correct.

## Ubiquitous language

A single, shared vocabulary used consistently by domain experts, code, tests, and conversation.
If the business says "settlement", the class is `Settlement`, not `PaymentRecord`. The payoff is
reduced translation cost: when the word in the meeting matches the word in the code, fewer
misunderstandings survive into production. This is the most portable piece of DDD: even a small
project benefits from naming things the way the domain names them.

## Bounded contexts

A bounded context is a boundary within which a model and its language are consistent. The same
word can mean different things in different contexts: a "Customer" in billing (an account with
payment terms) is not the same model as a "Customer" in support (a person with a ticket
history). Forcing them into one shared model creates a tangle that serves neither. Bounded
contexts let each subdomain keep its own coherent model, with explicit translation at the
seams. This aligns with [Single Responsibility](./solid.md): a context has one source of change
because it answers to one part of the business.

## Entities and value objects

Two ways to model domain data, distinguished by identity:

- **Entity.** Has a distinct identity that persists through changes to its attributes. A `User`
  is the same user even after changing name and email; identity (not field values) defines
  equality. Entities have a lifecycle.
- **Value object.** Defined entirely by its attributes, with no identity of its own. A `Money`
  amount, a `DateRange`, an `Address`: two value objects with equal fields are
  interchangeable. Value objects are naturally immutable, which removes a large class of
  aliasing bugs.

Modeling something as a value object instead of bare primitives is one of the most useful DDD
moves. Replacing `dict[str, Any]` or a loose `(amount, currency)` tuple with a `Money` value
object fixes [primitive obsession](../refactoring/primitive-obsession.md) and gives the invariants a home.

## Aggregates

An aggregate is a cluster of entities and value objects treated as a single unit for changes,
with one entity as the **aggregate root**. External code references only the root; the root
enforces the invariants that span the cluster and is the transactional boundary. For example, an
`Order` aggregate owns its `LineItem`s; you do not modify a line item directly, you go through
the order, which can enforce rules like "total must not exceed the credit limit". Aggregates are
where [Tell, Don't Ask](./tell-dont-ask.md) and the [Information Expert](./grasp.md) heuristic
become concrete; the rule lives with the data it governs.

## Domain events

A domain event records that something meaningful happened in the domain: `OrderPlaced`,
`PaymentReceived`. Events make side effects and cross-context reactions explicit and decoupled:
the order context announces `OrderPlaced` without knowing that shipping and analytics both
listen. Use them when reactions genuinely span boundaries; do not turn every state change into
an event for its own sake.

## Anti-corruption layer

When integrating with an external system or a legacy model whose concepts do not match yours, an
anti-corruption layer (ACL) translates between the two so the foreign model does not leak into
your clean domain. It is a domain-focused application of the [Adapter](../design-patterns/adapter.md)
pattern: the ACL speaks your ubiquitous language on the inside and the external system's
language on the outside. This protects the core model from being corrupted by external naming
and structure.

## When NOT to apply DDD

DDD's full machinery, aggregates, repositories, domain services, unit of work, is expensive
and justified only by real domain complexity. Applying it to simple CRUD, scripts, or small
tools is over-engineering ([YAGNI](./yagni.md)). Two common failure modes:

- **Folder cosplay.** Creating `domain/`, `application/`, `infrastructure/` directories does not
  make a design domain-driven; it just relocates the same logic.
- **Anemic models.** Entities that are bare field bags with all the rules living in service
  classes. This is the opposite of DDD's intent and forfeits the main benefit.
