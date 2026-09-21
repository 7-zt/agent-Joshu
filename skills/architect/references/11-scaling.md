# Scaling

Identifying bottlenecks from load evidence and choosing how to scale. Use for capacity planning, overload analysis and repair, and scalability design review.

## Adding machines is not one uniform action

"Cannot handle the load? Add machines" has two paths: vertical scaling (a beefier single machine) is simple, needs no code change, but has a physical ceiling, a single point, and an unprofitable premium; horizontal scaling (a pile of ordinary machines) has a much higher capacity ceiling, but the price is managing a flock instead of one machine—and it is not unlimited either: shared bottlenecks, coordination overhead, and shard-count ceilings all impose limits, and adding nodes does not by itself equal having redundancy and correct failure handling. Vertical scaling is buying time: while the system is small, upgrading one machine is always cheaper than re-architecting—no rush to go distributed.

The key watershed: stateless scales easily, stateful scales painfully. Adding 10 machines to the stateless tier (Web/API) is a one-line config change; adding one machine to the stateful tier (database/cache) can mean re-sharding, moving TB-scale data, and a weeks-long migration window. The first move of scaling is always squeezing state out of the computation so the bottleneck lands almost always on the remaining stateful part after the squeeze. When someone says "just add machines", ask first: which tier?

## Sharding strategies

Two schools: range sharding cuts by key interval—range queries stay efficient (time series, time-ordered paging) but hotspots form easily (with time-based sharding, today's data piles onto one shard); hash sharding cuts by hash(key)—uniform distribution naturally prevents hotspots, but range queries are dead (adjacent keys scatter across shards). The choice follows the query shape, not which is better.

Naive hashing `hash(key) % N` has a fatal flaw: the node count is baked into the formula. Add one machine, N changes, and nearly every key's home changes (going from N to N+1 moves about N/(N+1) of the data on average—about 80% when going from 4 to 5), and the cluster gets paralyzed by rebalancing traffic.

**Consistent hashing** solves it: picture the hash space as a clock face; nodes and data both hash onto the face, and a key belongs to the first machine found clockwise. Adding one machine inserts one new tick, and only the small arc of data between the new tick and the previous one changes hands. Adding or removing a node moves only about 1/N of the data on average—turning "whole-cluster earthquake" into "local adjustment"—and it is the foundation of smooth expansion in large-scale distributed storage.

Naive consistent hashing still suffers uneven node distribution (one node dies and its whole load lands on its clockwise neighbor). The fix is **virtual nodes**: each physical node places hundreds of avatars on the ring; the law of large numbers smooths out randomness, one death's load scatters across all others, and heterogeneous machines get avatar counts proportional to their strength. Choosing hash sharding plus elastic expansion—consistent hashing with virtual nodes is close to standard.

## Hotspots

Sharding's premise is uniform load, and real load follows a power law: a few keys carry the overwhelming majority of traffic. The terror of hotspots is that **sharding came to save you, and the hotspot defeats it**—add all the machines you like; the traffic still lands on the one machine holding that hot key (a top influencer posting, a single flash-sale item, breaking news).

Detection relies on monitoring the per-key traffic distribution, not just totals. The core idea of spreading has one move: turn a point into a field:

| Lever | How | Fits |
| --- | --- | --- |
| Salting | Split a hot key into `key#1`…`key#N` scattered across shards; aggregate on read | Write hotspots (counters) |
| Local cache | Cache a copy in the application process; most reads never leave the machine | Read hotspots (config, popular content) |
| Read replicas | Extra replicas for hot data to share reads | Read-mostly hotspots |
| Request coalescing | Of N simultaneous requests, let only one hit the backend; the rest await its result | Cache breakdown |

Twitter's write-time fan-out (a tweet pushed into every follower's timeline cache) meets a top influencer with tens of millions of followers and it is a disaster (one tweet equals tens of millions of writes). The fix is a hybrid: ordinary users get write-time fan-out; a handful of mega-influencers get read-time pull. For hotspots, spreading the write across tens of millions of places at write time trades for pulling from one place at read time.

## Multi-tier caching and stampedes

Real large-scale systems are multi-tier: CDN → edge → application-local → distributed cache → DB, each tier absorbing a batch of traffic. More tiers, less pressure on the DB—but each additional replica adds one more consistency problem (the DB changed; how do five tiers invalidate coherently?).

The most treacherous is the **cache stampede**: the instant a super-hot key expires, ten thousand concurrent requests discover "gone" simultaneously and surge into the DB to rebuild the same value—the DB instantly takes the same query ten thousand times. It is more insidious than cache failure: the cache did not break; the cache expiring normally became a synchronized flood under high concurrency. Three lines of defense:

1. **Request coalescing (single-flight).** Concurrent rebuilds of the same key admit only the first to query the DB; the rest subscribe to its result. Ten thousand queries collapse into one (Discord engineering blog, "How Discord Stores Trillions of Messages", 2023-03-06, https://discord.com/blog/how-discord-stores-trillions-of-messages).
2. **Randomized TTL jitter.** Never let a batch of keys expire in the same second.
3. **Logical expiry / early async refresh.** The key is never truly deleted; a background job refreshes it near expiry, and readers always hit.

Good cache design is half hit rate and half "when invalidation happens, do not let everyone pounce on the DB at once".

## Tail latency and fan-out amplification

Average latency dilutes the few extremely slow requests into nothing, and that 1% is precisely the experience that matters most. Latency is a distribution, not a number; external promises and internal SLOs use p99/p999.

The real killer is **fan-out amplification**: one user request fans out into dozens or hundreds of sub-calls, and the request completes only when the slowest returns—like a table of 100 diners whose meal starts only when the last dish arrives. A single sub-call has only a 1% chance of being p99-slow, but the probability of all 100 sub-calls being fast is (99%)^100 ≈ 36.6%—a 63% chance the whole request hits at least one slow sub-call. **In a high-fan-out system, the overall p99 approaches the sub-calls' p999 or even p9999.** The intuition "an occasionally slow sub-component does not matter" is simply wrong in the face of fan-out.

Hedged requests treat tail latency: send the same request to two replicas and use whichever returns first. Doubling everything doubles load; the smart version is the delayed hedge—send to replica A first, and only if A has not answered within p95 time send to B. Only the slowest 5% of requests get a second copy, roughly 5% extra load, and a large chunk of the tail is gone.

## Queueing: why approaching saturation explodes

The system is fine at 70% utilization; add a little traffic to 95% and latency suddenly spikes tenfold. Because request arrivals are random (peaks and valleys), a highly utilized system has no headroom to absorb bursts: a peak arrives, requests queue, the queue slows down everything behind it—positive feedback. Queueing theory gives the intuition (assuming simplified models like M/M/1; real systems deviate, but the trend direction holds): average queueing time is proportional to 1/(1−ρ)—at ρ=50% the factor is 2, at 90% it is 10, at 99% it is 100, and the curve rises nearly vertically as it approaches 100%.

**Headroom is design, not waste.** Servers idling at 30% buy the ability to absorb bursts and controllable tail latency; the machine money saved by squeezing utilization gets repaid tenfold as an avalanche at the first spike. Systems whose launch moment is a flood must provision for the peak, not the average.

Little's Law (requests in system = arrival rate × average residence time) derives latency from concurrency/throughput or estimates capacity. One final bucket of cold water on scaling by adding machines: the overhead of machines aligning state and coordinating with each other grows with scale (USL), with diminishing and even negative returns—like stuffing cooks into a kitchen: past some point they start fighting over the stoves, and more cooks means slower cooking. Stateless, low-coordination designs scale nearly linearly; heavily coordinated, strongly consistent designs hit a wall at some scale. The architect's job is minimizing the parts that need coordination: make the machines you add speak to each other as little as possible.

## Relationship to other documents

- The foundations of replication, sharding, and caching are in [Data and state](./05-data-and-state.md).
- Load shedding and backpressure under overload are in [Resilience](./10-resilience.md); the flip side of the queueing explosion is refusing early.
- Deployment shapes and region choice are in [Cloud and deployment](./technology-selection/06-cloud-and-deployment.md).
