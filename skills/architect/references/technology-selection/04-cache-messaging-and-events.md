# Caching, Messaging, and Events

The semantic distinctions and selection among three middleware kinds: caches only accelerate and never usurp; queues shave peaks and turn sync into async; events propagate facts. Use for pressure analysis of read hotspots, write floods, and cross-boundary collaboration.

## Three things constantly conflated

Many architecture diagrams run App → Redis → MQ → Kafka → Worker in one chain and call it advanced: we have cache, queue, event-driven. The real questions: is what sits in Redis a disposable cache or business state that must not be lost? Is the MQ for peak shaving or for making two services collaborate asynchronously? Are the Kafka messages commands (telling others to do) or events (telling others what happened)? What happens on consumption failure, duplicate consumption, reordering, backlog?

**The value of middleware lies not in its name but in which quality attributes it changes**: latency, throughput, availability, coupling, consistency, recovery cost. They address three different pressures: read hotspots, write floods, cross-boundary collaboration.

## Cache: accelerate only, never usurp

Fits read hotspots. The three most common errors: treating the cache as the source of truth (cache lost, data lost); no invalidation strategy (users see stale, dirty data); all requests penetrating together (the primary store gets crushed).

| Error | Correct posture |
| --- | --- |
| Cache as source of truth | The primary store is the source of truth; the cache is rebuildable |
| No invalidation strategy | TTL, active invalidation, versioning |
| Cache penetration | Negative caching, request coalescing, rate limiting, warming |

Cache types by data shape: local caches fit config, dictionaries, infrequently changing data (watch multi-instance inconsistency); distributed caches (Redis) fit hot objects, sessions, counters, rate limiting (watch network overhead, capacity, eviction policy); CDN fits images, video, static assets, public pages (watch invalidation delay).

The test sentence: **if the cache is lost, the system should become slower, not wrong. If it becomes wrong, you have smuggled business state into the cache.**

## Message queue: turning must-do-now into can-queue

The most common value is peak shaving: instantaneous pressure becomes controllable queuing. Typical scenes: ticket-notification after locking a seat, coupon/SMS/email after an order succeeds, parse-and-index after document upload, transcoding after video upload.

But once a queue enters, the synchronous world becomes asynchronous, and five new questions must be answered: duplicate messages (is the consumer idempotent? what happens when the same message is processed twice?); lost messages (how is the produce-store-ack chain guaranteed?); message ordering (does one business key need in-order processing?); backlog (what does the user see? how does the system degrade?); dead letters (where do failed messages go? who fixes them?).

A queue does not stabilize by existing; it converts the problem from request latency into **async consistency and recovery**.

## Event systems: recording what happened, not commanding what to do

| Category | What it means | Examples | Who owns the outcome |
| --- | --- | --- | --- |
| Command | Please do something | `CreateOrder`, `SendEmail` | The receiver must succeed or fail |
| Event | Something has happened | `OrderPaid`, `TicketLocked` | Subscribers react as needed |

Events fit propagating facts across boundaries: the order service publishes `OrderPaid`; inventory confirms deduction, notifications send SMS, the data platform updates reports, risk control logs behavior—and the order service need not know all its downstreams. The costs: once an event schema is published, downstreams depend on it and upgrades must stay compatible; when a downstream handler fails, the fact has already happened and cannot simply roll back; events too fine drown the system, too coarse fail to express; long event chains make debugging hard—tracing is mandatory.

## Product selection: semantics before names

First sort into four semantics, then pick a product:

- **Task queue** (RabbitMQ, Celery, Sidekiq types): like dispatching work to workers; each message is done once consumed. Background jobs, email sending, image processing.
- **Log-style event stream** (Kafka, Pulsar types): like a replayable fact log with resettable consumption offsets. Event bus, data sync, audit, stream processing.
- **Lightweight messaging/streaming** (Redis Streams, NATS types): like a simple, fast async channel with light ops. Small-to-mid-scale async, low-latency internal messaging.
- **Cloud-managed queues** (SQS, Pub/Sub types): like a reliable queue with the operations outsourced. Cloud businesses, teams that do not want to self-operate.

Four questions when selecting: do messages need to be **replayable** (if yes, lean event stream)? Do you need complex routing and delivery confirmation (task queue fits better)? Can the team operate the cluster (if not, managed)? Are messages core audit facts (if so, take persistence, retention, and schema governance seriously)?

## Outbox: do not split writing facts from emitting events

The classic pit: the order write succeeds and the `OrderCreated` send fails—the order sits in the primary store and downstream never knows; or the reverse, the message goes out and the order write fails—downstream receives an order that does not exist.

The Outbox pattern: in one local transaction, write the business table + the outbox table; a background relay scans the outbox, sends, and marks delivered. It prevents the two-step split of writing facts and emitting events. The cost is one more table, one relay, and idempotency-plus-retry logic; what it buys is controllable cross-service consistency.

## Relationship to other documents

- The full engineering of Outbox and eventual consistency is in [Consistency](../09-consistency.md).
- Backlog degradation and backpressure are in [Resilience](../10-resilience.md).
- The mechanics of flood shaving are in [Scaling](../11-scaling.md).
- The unified selection decision tree is in [Selection principles](./01-principles.md).
