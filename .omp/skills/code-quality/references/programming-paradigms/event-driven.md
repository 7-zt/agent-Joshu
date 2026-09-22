# Event-Driven Architecture

## What it is

Event-driven architecture treats events as first-class facts: something happened, and that fact is recorded and published rather than directly triggering a known piece of code. A producer emits an event (`OrderPaid`, `FileUploaded`, `user.signup`) without knowing or caring who consumes it. Consumers subscribe to the events they care about. The coupling between them is the event schema, not a direct function call.

This shows up at many scales: in-process signals and hooks (Django signals, pytest hooks, Qt signals), pub/sub within an application, and message queues or event buses across services (Kafka, RabbitMQ, SQS, Redis streams). The unifying idea is the same: invert the dependency so the thing that _causes_ a state change does not hold a reference to everything that must _react_ to it.

## The assumption underneath

- Producers and consumers change for different reasons and should be deployable, testable, and reasoned about independently.
- "Something happened" is a more durable interface than "call this specific handler." New reactions can be added without touching the producer.
- For some systems the event log itself is valuable: an append-only record of facts is a natural audit trail and a basis for replay.

## When appropriate

- **Decoupling producers from consumers.** One action needs to trigger several unrelated reactions (send email, update analytics, invalidate cache) and you do not want the originating code to know about all of them.
- **Audit trails and event sourcing.** The sequence of events _is_ the source of truth; current state is a projection. This gives replay, temporal queries, and a built-in audit history.
- **Asynchronous workflows.** Work that should not block the request path, notifications, indexing, downstream processing, is naturally expressed as "emit event, let a worker handle it."
- **Extension points.** Plugins and hooks let third parties react to lifecycle events without modifying core code.

## Risks

Event-driven systems trade explicit control flow for decoupling, and that trade has real costs:

- **Hidden control flow.** You cannot read a producer and know what happens next; the reactions are elsewhere. This is the same debugging difficulty noted in [declarative.md](./declarative.md), amplified; the call graph is assembled at runtime through subscriptions.
- **Ordering and delivery.** Events may arrive out of order, be delivered more than once, or be lost. Consumers usually must be idempotent (processing the same event twice causes no extra effect); the same property a [state-machine.md](./state-machine.md) needs for repeated events.
- **Error context.** When a consumer fails, the failure is far from the producer in both code and time. Reconstructing "what led to this" requires correlation IDs and good event metadata.
- **Event storms / cascades.** One event triggers handlers that emit more events, which trigger more handlers. Without care this fans out unboundedly or forms cycles.

## Consumer failure and delivery guarantees

A direct function call has one obvious failure path: the caller sees the exception. An event has none of that clarity, so consumer failure needs an explicit policy. Three questions decide the design:

- **What happens when a consumer raises?** In a synchronous in-process bus, one failing handler can abort the others unless each is isolated. Decide whether a failing reaction should block its siblings or be contained.
- **What are the delivery semantics?** At-most-once (fire and drop on failure), at-least-once (retry until acknowledged, so consumers may see duplicates), or exactly-once (usually a fiction at the transport layer, approximated with idempotent consumers plus deduplication). Most durable brokers give at-least-once, which is why idempotency is not optional.
- **Where do poison messages go?** An event that always fails its consumer must not block the queue forever. A dead-letter queue captures repeatedly-failing events for inspection rather than retrying them infinitely.

The throughline: with direct calls the failure contract is implicit and obvious; with events you must design it deliberately, because the producer has walked away by the time anything goes wrong.

## Relationship to the Observer pattern

The Observer pattern is the smallest, in-process instance of event-driven design: a subject keeps a list of observers and notifies them on change. Event-driven architecture generalizes this; the "subject" becomes an event bus or broker, notification becomes publish, and observers become subscribers that may live in other processes or services. The same inversion of dependency applies; the difference is the transport, durability, and whether delivery is synchronous. When the decoupling is local and synchronous, plain Observer (or a simple callback list) is enough; reach for a broker only when you need cross-process delivery, durability, or async processing.

## Events vs commands

A distinction worth keeping clear: a _command_ tells a specific handler to do something (`SendEmail`, `ChargeCard`) and expects it to happen; an _event_ announces that something already happened (`OrderPaid`, `EmailSent`) and makes no demand about who reacts. Commands are directed and usually have exactly one handler; events are broadcast and may have zero, one, or many. Confusing the two, naming an event like a command, or treating a published event as if a particular consumer must handle it, quietly reintroduces the coupling event-driven design was meant to remove. Name events in the past tense as facts; if you find yourself caring _which_ consumer runs, you probably wanted a direct call or a command, not an event.

## Synchronous vs asynchronous delivery

A choice that changes the whole character of an event system is whether `publish` blocks until handlers finish (synchronous) or hands off and returns immediately (asynchronous). Synchronous in-process delivery is simple to reason about, the producer's call stack still includes the handlers, exceptions propagate back, and ordering is deterministic, but it couples the producer's latency and failure to its consumers, which partly defeats the decoupling. Asynchronous delivery (a queue, a broker, a background task) restores the decoupling but introduces every distributed-systems concern: at-least-once delivery, ordering, partial failure, and the need for idempotent consumers. Pick synchronous when the reactions are cheap, local, and must complete before the producer continues; pick asynchronous when reactions are slow, remote, or genuinely independent of the producer's success.
