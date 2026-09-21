# Selection Principles

The unified decision framework for technology selection: whether to introduce, which stage you are in, where it dies first, whether the team can sustain it, and whether you can exit. Use for any "should we adopt X" judgment; it is the overview of the other seven documents in this directory.

## The root node is not A versus B

The first question of selection is never "PostgreSQL or MongoDB", "REST or gRPC", "PaaS or K8s", but: **do we actually need to introduce new technology?**

If the existing stack can solve the problem within the target performance, cost, reliability, and delivery window, default to keeping it. Any new technology brings learning cost, integration cost, operations cost, and future migration cost. This is the same restraint as "monolith unless you must not", "workflow unless you must not", "managed API before self-built GPUs". Read selection as: **paying a definite cost for a definite problem.**

## First cut: which stage are you in

The same system has completely different answers at different stages:

| Stage | Main contradiction | The resulting lean |
| --- | --- | --- |
| MVP | Validation speed | Fewer components the better; mainstream stack, managed first; migration cost not yet a concern |
| Growth | Controllable growth | Add observability and gradual rollout first; draw boundaries; scale locally |
| Scale | Efficiency and cost | Only now worth deep per-unit-cost optimization and platformization |
| Critical | Stability and compliance | Audit, isolation, disaster recovery, SLOs, and incident process become hard requirements |

A technology that is the right answer at maturity may be over-engineering at MVP. Validating demand: fewest components; sustaining growth: controllability; optimizing at scale: only then is complexity worth paying for unit cost and deep customization.

## Second cut: where does the system die first

Once the existing stack is confirmed insufficient, do not reach for a tool immediately—locate the failure mode first:

| Which failure you fear most | Where to look first |
| --- | --- |
| Data corruption, states disagreeing everywhere | Check whether the data model matches transaction boundaries; idempotency and Outbox in place; reconciliation as backstop |
| Concentrated read traffic burning the primary store | Evaluate a cache tier, read-model isolation, CDN offload, ingress rate limiting |
| Instantaneous write floods crushing the backend | Introduce queue buffering, backpressure propagation, peak shaving, asynchronization of non-critical paths |
| Deep call chains amplifying tail latency | Examine API boundary division, per-layer timeout budgets, degradation means, trace-based localization |
| Every release a heart-stopper | Build deployment-platform capability, gradual rollout, fast rollback, config governance |
| Incidents taking half a day to diagnose | Check metrics, logging, tracing coverage; whether SLO alerts point at the responsible party |
| AI output quality quietly degrading | Build eval baselines, trace observation, RAG retrieval evaluation, model-routing fallbacks |
| Teams constantly waiting on and blocking each other | Draw module boundaries; evaluate platform-engineering investment; sort out service ownership |

**Tools are only the shell of the answer; the failure mode is the actual question of selection.**

## Third cut: can the team sustain it

Many technologies look great in benchmarks but the team may not afford the upkeep: can they deploy it? Debug it? Is there monitoring? Who fixes it at 3 a.m.? Will version upgrades explode? Are there enough people who understand it?

A "higher-performing system nobody can repair" routinely loses in production to a "sufficient-performance system the team knows well". Selection is not a lab contest; it is a long-term operations contract. Leave operability and key-person risk out of the judgment, and what you selected is not a technology but a future incident.

## Fourth cut: can you exit

A mature selection always has an exit plan: how is the new database's data migrated, how is dual-write verified, rolled back to where? Can the model vendor's API be adapted; can prompts and evals be reused? Is business logic swallowed by the framework; can it be layered away? How do a message system's topics/schemas/consumer offsets migrate? Can the cloud platform's images, configs, secrets, storage, and networks be moved out?

A selection without an exit route ties the future down. Before an important technology enters production, at minimum have a spike, a gradual-rollout plan, a rollback plan, and a decision record.

## The unified decision tree

Should we introduce a new technology?

1. The existing stack meets the targets → keep it, with local optimization.
2. It cannot, but we are at MVP → fewest components, fastest validation, low migration cost.
3. What is the failure mode? Data/consistency → storage and transaction boundaries first; latency/throughput → caching, batching, scaling approach first; availability/failure → redundancy, degradation, isolation first; AI quality → eval, RAG, model routing first; team collaboration → module boundaries and platform capability first.
4. Can the team sustain the candidates, and can you exit? No → pick something lighter. Yes → spike to verify → write the decision record → adopt gradually.

## What a selection decision record needs

The record's point is not format but writing "why chosen" and "how to retreat if wrong" clearly: context (current state and pain, ideally with numbers), goal (the failure mode to solve), candidates (at least two, each with its cost), choice and what was given up (what was gained, what was paid), re-review conditions (which signals trigger re-evaluation), exit plan (how to move it out).

## The "ask first" of the seven domains

| Domain | Do not ask first | Ask first |
| --- | --- | --- |
| Language/framework | Which language is more advanced | Do team, ecosystem, runtime, and business complexity match |
| Database/storage | Which database is strongest | Who is the source of truth, and what is the query shape |
| Cache/queue/events | Should we get Kafka | Is it a read hotspot, a time mismatch, or a business-fact broadcast |
| API/communication | REST or gRPC | Sync/async, internal/external, contract strength |
| Deployment platform | Should we get K8s | Does the team need platform capability, and can it sustain it |
| Observability/reliability | Which monitoring tool | What is the user SLO, and how do incidents end |
| AI infrastructure | Should we self-host GPUs | Is the scarce resource the model, context, cost, quality, or controllability |

## Relationship to other documents

- The general writing of decision records (ADRs) is in [Architecture decisions](../07-architecture-decisions.md).
- Stage-judgment signals are in [Evolution and migration](../12-evolution-and-migration.md).
- The other seven documents in this directory expand each domain: [Languages and frameworks](./02-languages-and-frameworks.md), [Data stores](./03-data-stores.md), [Caching, messaging, and events](./04-cache-messaging-and-events.md), [API and communication](./05-api-and-communication.md), [Cloud and deployment](./06-cloud-and-deployment.md), [Observability and reliability](./07-observability-and-reliability.md), [AI infrastructure](./08-ai-infrastructure.md).
