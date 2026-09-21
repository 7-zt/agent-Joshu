# Glossary

These terms carry specific meanings within this Skill. When you need judgment rationale, derivations, or examples, use the routing table in [SKILL.md](./SKILL.md) to pick a reference document.

## Reasoning and judgment

**Fact**

Something directly observable in the current project's code, configuration, tests, or runtime behavior.

**Assumption**

A proposition temporarily accepted to move the reasoning forward but not yet confirmed by project evidence. Label it explicitly in output.

_Avoid: "premise" when you mean an unverified proposition._

**Recommendation**

A candidate direction offered for the current problem, based on facts and assumptions. The user ranks tradeoffs; a recommendation is not a decision.

_Avoid: "conclusion" before user confirmation._

**Quality attribute**

How well the system does its job: performance, availability, consistency. Distinct from functional requirements, which say what the system does.

_Avoid: "non-functional requirements"._

**Trade-off**

The part of a decision where you give up B to get A. A proposal with no visible cost is not perfect; it is not thought through.

**Constraint**

A boundary the design cannot cross: team size, time, budget, compliance, existing systems. Distinct from quality-attribute targets you aim for.

## Requirements and measurement

**Latency**

Time from issuing a single request to receiving its result.

**Throughput**

Request volume the system can process per unit of time.

**P99 latency**

The latency faster than 99% of requests. Tail latency reflects user experience better than the average.

**Read/write ratio**

The ratio of reads to writes; it decides whether the system leans toward read or write optimization.

**Back-of-the-envelope estimate**

A quick order-of-magnitude calculation (QPS, storage) with a few multiplications, used to find what will crush the system first.

**Availability**

The fraction of time the system serves correctly, commonly expressed in "nines". Each extra nine usually costs an order of magnitude more.

**Durability**

The probability that stored data is not lost.

**Error budget**

The unavailability allowance an SLO permits. Freezing releases when the budget is spent is a common budget policy; the policy is set separately from the budget amount itself.

## Data and consistency

**Transaction**

A unit of execution in which a group of operations either all succeed or none take effect.

**ACID**

The strong guarantee set of a transaction: atomicity, consistency, isolation, durability.

**Strong consistency**

A broad, imprecise umbrella term for models with demanding consistency. When it lands in a concrete design, name the specific model—linearizability, (strict) serializability, read-your-writes, or eventual consistency—because costs differ per model.

**Eventual consistency**

After a write and an inconsistency window, all reads eventually see the latest value. It buys availability and scalability.

**CAP theorem**

When a network partition occurs, consistency and availability cannot both hold.

**Idempotency**

Executing the same operation repeatedly produces the same result as executing it once. The precondition for safe retries.

**Stateless**

A component that keeps no cross-request state; it can be replicated and scaled horizontally at will.

**Stateful**

A component that keeps state. Replicating, migrating, and failing over state is the main source of distributed-system complexity.

## Scaling levers

**Vertical scaling**

Upgrading a single machine. Simple, but with a physical ceiling; whether the machine is a single point depends on redundancy design, and scaling up does not by itself remove redundancy.

**Horizontal scaling**

Adding machines. Stateless components replicate directly; stateful ones scale through replication, sharding, and rebalancing, at far higher cost and complexity.

**Replication**

Keeping multiple copies of data, mainly to scale reads and tolerate faults.

**Sharding**

Splitting data across nodes by rule, mainly to scale writes.

**Cache**

Holding hot data in a faster storage tier to cut latency and scale reads. The cost is consistency and invalidation management.

**Hotspot**

Disproportionate load concentrating on a single key or node, throwing sharding out of balance.

**Backpressure**

A slowdown signal propagated upstream when the downstream is overloaded, preventing unbounded queue growth.

## Architecture structure and evolution

**Monolith**

The style with a single deployment unit. Simple, and an underrated correct starting point.

**Microservices**

The style of many independently deployed small services. It mainly solves organization and independent-evolution problems, not performance.

**Event-driven**

A style that decouples components through publishing and subscribing to events.

**CQRS**

Separating the write model from read models; each optimizes for its own shape, and you pay to keep them in sync.

**Strangler Fig**

An evolution pattern that intercepts and replaces functionality around the old system until the old system retires.

**Branch by abstraction**

An evolution pattern that swaps implementations behind an abstraction layer while the trunk stays releasable.

**Anti-corruption layer**

A translating isolation layer between internal and external models that keeps external concepts from polluting internal boundaries.

**Fitness function**

Architectural constraints written as automated tests that continuously verify the system has not drifted from its goals.

**Evolution trigger signal**

Observable evidence in load, organization, or failure modes that the architecture needs an upgrade.

## Decisions and organization

**Architecture Decision Record (ADR)**

A document recording the candidates, tradeoffs, consequences, and re-review conditions of one architecture decision.

_Avoid: inventing a second project-specific decision-record format._

**Technical debt**

An expedient chosen deliberately for short-term delivery. What matters is bookkeeping it and paying it down on plan.

**Conway's Law**

System structure converges toward the communication structure of the organization that designs it.

**Inverse Conway maneuver**

Designing or adjusting the organization's communication structure first, to obtain the desired system boundaries.

**Cognitive load**

The mental effort a team needs to understand and maintain a subsystem. The real basis for splitting.

**Single Point of Failure (SPOF)**

A component whose failure takes down the whole path. Eliminate it with redundancy.

**Blast radius**

The maximum extent a mistake or failure can reach. Shrink it with isolation.

**Trust boundary**

A boundary where crossing data or requests changes the trust level. Security design revolves around it.

## Views

**C4 model**

A view model expressing systems in four levels: Context, Container, Component, Code.

**Context diagram**

The highest-level view, expressing the system's boundary against external actors and systems.
