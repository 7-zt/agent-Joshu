# Architecture Styles

Comparing the applicability conditions and tradeoffs of common architecture styles. Use when choosing the overall structure for a new system, evaluating the evolution direction of an existing one, or reviewing whether a style choice matches the constraints.

## Patterns are tools, not goals

The same problems recur across countless systems, and proven solutions settle into patterns. The value of learning patterns: you hold cards when a problem arrives instead of inventing from zero, and communication gets a shared vocabulary—one word saves half an hour of explanation.

But patterns have no high or low, only fitting and unfitting. A well-used monolith outranks a misused microservice system. Evaluating any style means answering three things: what problem it solves, what it looks like, and what it costs. If you cannot see the cost, you have not learned the pattern.

## Applicability and cost per style

**Layered.** Cut the system horizontally by concern; each layer talks only to its neighbors: presentation, business, data. Solves "do not stir everything into one pot"—the plainest form of separation of concerns, almost always applicable. The cost is pass-through: a simple query crosses every layer, generating boilerplate that only forwards data. Note that layering is code organization; it does not mean each layer is an independently deployed service. Do not mistake layering for distribution.

**Monolith.** The whole application is one deployment unit; modules call each other through functions, not the network. Solves "ship something at the lowest coordination and operations cost". A monolith can and should be modular inside (the modular monolith); monolith does not mean ball of mud—it means modules deploying together. Costs: any change republishes everything; no per-module scaling; one module's crash takes down the process; unclear boundaries rot into a big ball of mud. These are mostly growing pains that arrive after the product succeeds; paying for them before validating that anyone uses the product is over-engineering.

**Microservices.** Many small services, independently developed, deployed, and scaled, each owning its data. It solves an organization problem first and a technical problem second: when multiple teams trip over each other in one monolith and every release queues company-wide, microservices give each team its own service and release cadence. The cost is turning function calls into network calls and importing an entire mountain of distributed complexity: timeouts, retries, idempotency; cross-service transactions become nearly impossible; operational complexity explodes (service discovery, tracing, unified logging, orchestration); local debugging starts many services at once. Three preconditions should hold before considering it: the organization is large enough that teams block each other; there is a concrete independent-deployment need; platform capability (monitoring, CI/CD, orchestration) already exists. A five-person team splitting into a dozen microservices and spending every day debugging why services cannot reach each other is not advancement; it is self-inflicted torture.

**Event-driven.** Components cooperate through "what happened" rather than "go do this" commands. The order service broadcasts "order paid"; SMS, points, and logistics each subscribe; the publisher does not know who is listening. Solves decoupling and fan-out: each new downstream action changes a subscriber, not the checkout code. Costs: the overall flow becomes invisible, logic scatters across subscribers, and debugging feels like detective work; plus duplicate events, ordering, loss, and brief inconsistency from eventual consistency. Forcing event-driven onto a simple flow with clear call relations turns a straight road into a maze; synchronous scenarios needing immediate results do not fit either.

**Message queue / async processing.** A buffer pool between producers and consumers: shaving peaks, decoupling asynchronously (long jobs do not make humans wait), reliable delivery (the task survives consumer crashes). Costs: one more critical infrastructure piece that must be maintained and must not die; users lose immediate results, so the product needs a "processing" state; messages may be consumed twice, so consumption must be idempotent; queue backlog itself becomes a new thing to monitor. Small workloads without peak pressure gain only ops burden from a queue.

**CQRS (separate read/write).** Split write and read into two models: the write model is rule-strict and strongly consistent; read models are pre-optimized for queries, possibly denormalized and cached. Fits read-dominated systems with severely asymmetric read/write demands (a product page: one edit, ten million views). Costs: doubled complexity—two models plus a sync channel that must be reliable; the sync is usually asynchronous, so a read right after a write may see stale data. The vast majority of systems do not need CQRS; it is the heavy weapon after conventional means are squeezed dry.

**Pub/Sub.** The key difference from a queue is delivery semantics: a queue gives each message to one consumer (work distribution); pub/sub gives every subscriber its own copy (broadcast). Solves "notify many parties about one thing without the notifier knowing who they are". Costs: the global flow becomes hard to trace; fan-out cost grows with subscribers; delivery semantics (at-least-once, at-most-once) must be decided deliberately.

**BFF (backend for frontend).** A dedicated backend per frontend, trimming and aggregating scattered backend data into the shape most convenient for that client. Fits multiple, very different frontends over a multi-service backend. Costs: one more middleman; small teams end up duplicating code across BFFs; a BFF can itself bloat into a small monolith. With one frontend or uniform needs, a general API suffices. The orchestration layer of an AI chat product is in a sense a heavyweight BFF, trimming inference, retrieval, tools, and session into the streaming conversation the frontend wants.

**Pipeline.** Split processing into chained stages; one stage's output is the next stage's input; each stage develops, tests, replaces, and scales independently. Fits linear data processing (ETL, media transcoding, RAG's retrieve-rerank-generate). Costs: the whole pipeline runs at the slowest stage's pace; one stage's failure needs a thought-through rollback for the whole chain; serialization between stages costs; logic requiring back-and-forth interaction between stages does not fit.

**Microkernel / plugin.** A minimal stable kernel plus pluggable extensions; the kernel provides only base capability and the extension contract. Fits systems with a stable core, variable periphery, and third-party extension (browsers, IDEs). Costs: the plugin contract is nearly impossible to change once set; plugin quality varies and can drag the kernel down, requiring isolation or sandboxing; designing the extension points is itself hard. Plugin architecture without an external-extension need is over-engineering.

## Selection order

1. **Prefer not using one.** Can the simplest layered monolith solve it? If yes, stop there.
2. **Match the symptom, not the fashion.** Code tangled into a soup—layering/modularity. One event fanning out to many parties—event-driven/pub-sub. Long jobs or peak shaving—message queue. Severely asymmetric reads/writes—CQRS. Very different frontends—BFF. Linear processing—pipeline. Stable core needing external extension—microkernel. Multiple teams blocking each other—microservices, carefully.
3. **Adopt only what you can pay for.** If the cost is unaffordable or the problem has not actually appeared, write a note "may need this later" instead of prepaying complexity.

Three rules of thumb: start simple and let real pain drive evolution; patterns compose—real systems are almost all layered-monolith foundations with local event-driven and async sections; always be able to name what a pattern took away when you introduced it—if the cost is unspeakable, you are probably following the crowd.

## Reversal cases as calibrators

Amazon Prime Video moved its video-quality monitoring from microservices and Serverless back to a monolith and cut cost by about 90% (Prime Video Tech blog, 2023-03); Segment merged 140-plus microservices back into a monolith, going from an outage roughly every other day to deployments one engineer finishes in minutes (Segment engineering blog, "Goodbye Microservices", 2020-07). The lesson is not that microservices are wrong (Netflix uses them well); it is that following the crowd is wrong. Whether a style fits always comes back to the current project's answers to the six questions and its constraints—not industry volume.

## Relationship to other documents

- The organizational basis for splitting microservices expands in [Organization and ownership](./13-organization-and-ownership.md).
- The eventual consistency and cross-service transaction problems these styles introduce expand in [Consistency](./09-consistency.md) and [Distributed systems](./08-distributed-systems.md).
- Selection details for events, queues, and caches are in [Caching, messaging, and events](./technology-selection/04-cache-messaging-and-events.md).
