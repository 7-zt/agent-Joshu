# Data and State

State ownership, data lifecycles, and storage boundaries. Use for any architectural judgment involving "where data lives, how consistent it stays, how it scales"—the hardest and most worthwhile part of system design to think through early.

## State is the hard part, and the value

Split what lives in a system into two kinds:

- **Stateless.** Remembers nothing: input in, output out, forget on completion. To scale, copy instances; distribute traffic however.
- **Stateful.** Remembers and changes over time: balances, carts, presence. Copying it means answering how two memories stay consistent—the root of all the trouble.

This yields a recurring architectural move: squeeze state out of the computation and concentrate it in a few places that specialize in managing it (databases, caches); keep everything else stateless and freely copyable. Most of the system scales horizontally with ease; the difficult state is corralled into a few controllable spots that get dedicated care.

State is also where the product's entire value lives: user data, orders, relationships, memory. The architect's job is not eliminating state (impossible) but managing it cleanly: where it sits, how strong its consistency is, how it scales, and how it neither gets lost nor corrupted on failure.

## Choose storage for the access shape

"I'll use the database I know for everything" is a common trap. The right move is looking at what the data looks like and how it is accessed:

| Storage type | Fits which access shape |
| --- | --- |
| Relational | Structured, heavily related, transaction-and-strong-consistency core data (users, orders, accounts) |
| Document | Flexible structure, self-contained, fetched and stored whole by ID (articles, configs, session records) |
| Key-value | Minimal key-to-value lookup with speed demands (sessions, counters, caches) |
| Columnar | Analytical aggregation over massive data (reports, statistics) |
| Graph | Where the relationship network itself is the point (social, fraud links, knowledge graphs) |
| Vector | Semantic similarity retrieval (embeddings, RAG, recommendations) |
| Object storage | Large, immutable, fetched whole by ID (images, video, model weights, backups) |
| Search engine | Full-text search and complex filter/sort (product search, log retrieval) |
| Time-series | Timestamped, append-only, aggregated by time (monitoring metrics, billing records) |

Polyglot persistence is a cost forced out by evidence, not a maturity badge: each additional store brings another sync path, consistency boundary, and ops object. Start from one relational database by default; introduce a dedicated store only when a data class's access shape clearly departs from what the primary store is good at and real load evidence proves it cannot cope. Three questions to ask: what is this data's read/write shape; how strong must its consistency be; how big will it grow and how often is it accessed (which decides whether replication and sharding enter the picture). Selection details are in [Data stores](./technology-selection/03-data-stores.md).

## The consistency spectrum

"Strong consistency" is a broad umbrella term, not a precise one: when it lands in a concrete design, write down which model you actually mean—linearizability (all operations appear to take effect instantly in some global order), serializability (concurrent transaction results are equivalent to some serial execution order), strict serializability (serializability plus respect for real-time ordering), read-your-writes (your own writes are immediately visible to you), or eventual consistency (values converge after an inconsistency window). Saying "strongly consistent" in conversation is fine; landing it in a design or acceptance criterion requires naming the model. See [Consistency](./09-consistency.md).

CAP in plain words: when a network failure splits the system into two halves that cannot reach each other (partitions will happen eventually—not your choice), you pick one of two things—keep serving but possibly return inconsistent data (pick A), or refuse service rather than return wrong answers (pick C).

Which data needs stronger guarantees is a business judgment, not a technical one, with a single criterion: **which business invariant would brief inconsistency break?**

- Write the invariant first, then pick the mechanism: the account-balance invariant is "never negative, and ledger entries conserve"—guarding it can mean transactions, conditional updates (debit with WHERE balance >= x), serializable isolation, or after-the-fact reconciliation; no need to presuppose a consistency term. The inventory invariant is "no overselling"; a uniqueness constraint is itself an invariant.
- Eventual consistency is fine for: like counts, view counts (seconds of lag bother no one), social feeds (followers seeing a post a few seconds late is acceptable), notifications and read states.

Strong consistency is expensive; spend the quota where things actually break. Building global strong consistency for like counts means paying steep performance and availability prices for rigor nobody needed. The systematic treatment of consistency models is in [Consistency](./09-consistency.md).

## Transactions and design postures: ACID, BASE, CAP each govern one layer

When several operations must all succeed or all fail, you need a transaction. Debiting A by 100 and crediting B by 100 must never half-happen. ACID (atomicity, consistency, isolation, durability) describes the execution and recovery guarantees of a single transaction; BASE (basically available, soft state, eventually consistent) is a family of design postures favoring availability and scale; CAP describes the observable guarantees a distributed service can offer between consistency and availability under network partition. The three sit at different layers and do not map onto each other: there is no "ACID leans CP, BASE leans AP" conversion; a single-machine ACID database never faces CAP's choice at all, and a distributed system can offer ACID transactions on some operations and eventual consistency on others. They compose: core transactions go through local ACID transactions; statistics, notifications, and streaming data go eventual; cross-service composition is stitched with the Saga and Outbox patterns from [Consistency](./09-consistency.md).

## The three cards for scaling data

| Lever | What it solves | Cost |
| --- | --- | --- |
| Replication (primary-standby) | Scales reads; redundancy for fault tolerance as a bonus | Primary-standby lag (stale reads); writes do not scale; the primary is the write SPOF with complex failover |
| Sharding | Scales writes and storage capacity | Cross-shard transactions and joins are mostly gone; a wrong shard key creates hot shards; re-sharding moves mountains of data |
| Cache | Cuts read latency and database read pressure | Consistency problems; a new component to maintain; cold start dumps traffic onto the database |

One line to separate them: **replication scales reads, sharding scales writes, caching cuts latency and scales reads**. Do not expect adding replicas to fix a write bottleneck—that is sharding's job.

Shard as late as possible and only after thinking it through. The shard key is close to irreversible once set: shard by region with 80% of users in one region, and one machine melts while the rest idle; adding machines means changing the rule and moving already-laid data in bulk.

## The three cache traps

Caching trades consistency for speed, and three traps catch nearly everyone:

1. **Invalidation and consistency.** The database changed; the cache still holds the old value. The common approach—update the database, then delete the cache so the next read reloads—has subtle ordering gaps under high concurrency. There is no perfect solution, only tradeoffs: adopting a cache means accepting some inconsistency; the job is keeping the window inside business tolerance (a sensible TTL, for instance).
2. **Penetration, breakdown, avalanche.** The cache's mission is shielding the database; the moment that wall leaks, the flood hits the database directly. Penetration (many requests for nonexistent keys, often malicious) is blocked with negative caching or a Bloom filter; breakdown (a hot key expiring while massive traffic hits the database at once) with lock-on-rebuild letting only one request through; avalanche (mass simultaneous expiry or total cache failure) with randomized TTL jitter and making the cache itself highly available.
3. **The nature of replicas.** The first two traps both point at one thing: a cache is a second copy of the data, and any copy carries the risk of two versions disagreeing. Same in kind as primary-standby lag and shard inconsistency—**replicating data for performance and scale turns consistency into a cost you must manage. There is no free scaling.**

## The data model is the hardest decision to change

Logic is easy to change; data is not. Logic is stateless: fix a bug, redeploy, and the old code vanishes without a trace. Data has state and inertia: once the data model (entity division, relationships, shard key, consistency level) is set, mountains of real data lie in its shape and grow daily. Changing it means designing old/new coexistence, writing migration scripts, keeping the service running throughout, and being able to roll back even though half the data may already be rewritten. It is measured in weeks or months—industry-recognized high-risk surgery.

The resulting priority: **be lazy where laziness is safe—logic can be rough first and refined later; be rigorous where rigor pays—the data model deserves the earliest deep thinking.** In the derivation from requirements, constraints, and quality attributes, how data is modeled, where it lives, how consistent it stays, and how it scales should be the earliest and most serious part. Not as future prepayment, but because a decision that costs a hundred times more to change than code deserves extra whiteboard time.

## The data lifecycle

Beyond "where it lives", answer for the data's whole life: how it is born, who reads and writes it, how long it is kept, how it is archived and deleted. Compliance (GDPR's right to erasure) and cost (ever-growing object-storage bills) both hang on this timeline. In AI systems the lifecycle gains two links: training data needs versioning (or experiments cannot be reproduced), and evaluation sets must evolve with the business (or you are grading against stale targets). See [Evaluation-driven architecture](./ai/05-evaluation-driven-architecture.md).
