# Resilience

Timeout, retry, idempotency, isolation, and degradation design. Use for any system depending on external services, needing to survive failures and overload, and for hardening after incident retrospectives.

## From MTBF to MTTR

High availability is not praying that nothing happens. Disks fail, cables get dug up, dependencies time out, someone's shaky hand runs the wrong command—failure cannot be eliminated. So the center of measurement shifts:

- **MTBF** (mean time between failures): how often it breaks; bigger is better.
- **MTTR** (mean time to recover): how long until it is well again; smaller is better.

Pushing MTBF from 30 days to 60 days costs money and effort that grow exponentially and still meets surprises; cutting MTTR from 30 minutes to 30 seconds relies on engineerable, drillable means: automatic detection, automatic failover, blast-radius isolation. The availability lever presses overwhelmingly on the MTTR side. A system with daily small glitches that self-heals in seconds has far higher availability than one that runs clean for half a year and then drops dead for a day. Resilience is not never falling; it is getting up at once when you fall, with only a scrape.

## Cascading failure: slow is deadlier than dead

Major production incidents are rarely caused directly by one component dying; almost all of them start with one component slowing down and triggering a chain reaction that drags healthy parts down. The classic script: the database slows; calls rise from 50ms to 5 seconds; B's threads block waiting on the database and the pool fills; A calling B starts timing out too, and A's pool drains; clients begin retrying, so request volume rises instead of falling; the whole chain exhausts its resources and the site 503s. One slow database drags the whole platform down in ten minutes.

Three amplifiers:

1. **Resource exhaustion.** A slow call is a request holding threads and connections for a long time, like a soaked sponge sucking the whole pool dry. Failing fast at least returns the resources immediately.
2. **Retry storm.** The moment the system slows, upstream's well-meaning retries multiply request volume several-fold in an instant. The fatal blow in many incidents is the retry storm.
3. **Stacked timeouts.** Every layer sets the same long timeout; when the innermost layer stalls, all outer layers wait together, and healthy requests cannot squeeze in and die alongside.

Slow is more insidious and deadlier than down: a down service fails fast and releases resources at once; a slow one holds resources while dying gradually, infecting the call chain node by node. More than half of resilience engineering is stopping slowness from propagating: either fail fast or cage it.

## Isolating the blast radius

The first line of defense is not eliminating failure but controlling the blast radius: any single point's failure may destroy only one small cell.

**Bulkheads.** Like a ship's watertight compartments, split resource pools by downstream: pool P (20 threads) for payment calls, pool R (10) for recommendations, pool S (10) for search. Payment dies—at worst its 20 threads are used up; recommendations and search are untouched. Share one pool, and a slow dependency X fills it entirely, leaving no threads even for calls to healthy dependency Y.

**Cell-based architecture.** Isolation one level up: replicate the entire service stack into multiple mutually isolated cells, each serving a subset of users. One cell burning to the ground affects only the users inside it.

**Shuffle sharding.** Assign each customer a random group of nodes (like dealing cards); when a toxic customer takes down its few nodes, almost nobody holds the exact same combination, so collateral damage approaches zero.

The isolation judgment starts with the failure-domain boundary: what must die together, and what must never drag each other. The most important bulkhead is always core versus non-core—do not let a dead "you may also like" take checkout and payment with it. Isolation is not free (more idle resources, more complex capacity planning); spend isolation granularity on the critical paths that must not be dragged down.

## Active self-protection

**Circuit breaker.** When a dependency's failure rate crosses a threshold, trip: subsequent calls fail fast without being sent—protecting the barely-alive downstream while releasing your own resources immediately. Three states: closed (normal pass-through) → open (tripped; everything fails fast) → half-open (after cooling, one probe request goes through; only on success does it close). The half-open state is the soul: no blind recovery—confirm the downstream is truly alive first.

**Timeout budget.** Give the whole chain one total deadline, decreasing layer by layer: the user tolerates 3 seconds; the gateway gives service A 2.5s, A gives B 1.5s, B gives the database 0.8s—each layer keeps margin for itself. The anti-pattern is every layer setting 30 seconds: the innermost stalls and all outer layers stand punished together.

**Backpressure and load shedding.** When request volume exceeds processing capacity, admitting everything ends with unbounded queue growth, minute-level latency, universal timeouts, and total collapse. Shed load actively: reject the excess immediately (429/503) so that the requests admitted all receive normal, fast service. Gracefully refusing a portion beats pretending to carry everything and collapsing together. That is the watershed between optimism and maturity.

## Retrying intelligently

Safe retry needs all four, none optional:

1. **Exponential backoff.** After failure wait 1s → 2s → 4s → 8s, giving the downstream breathing room.
2. **Jitter.** A thousand clients with the same backoff cadence will retry in perfect unison at seconds 1, 2, and 4—a synchronized shockwave that repeatedly flattens a downstream that is just recovering. Add randomness to scatter the retry moments. A one-line change improves stability by orders of magnitude.
3. **Retry budget.** Cap retries as a share of total requests (say 10%); stop beyond it, strangling retry storms at the root.
4. **Idempotency precondition.** The retried operation must be idempotent; otherwise a request that timed out but actually succeeded executes again as a duplicate charge.

Bare retry (`retry(3)`) is the most dangerous form: without backoff and jitter, retries become the storm that crushes the downstream; without a budget, the storm has no ceiling; without idempotency, retries corrupt the data.

## Graceful degradation

When the downstream simply will not recover, the last line of defense: losing a part is far better than losing everything. The core judgment must be made in advance: tier features by "dying without it" versus "tolerable without it". During an e-commerce sale the recommendation service dies: in a system without degradation, the recommendation error drags down the whole product page and users cannot even order; in a system with degradation, "you may also like" shows a default hot list while detail, cart, checkout, and payment run as usual.

The engineering lever is the degradation switch (feature flag): every non-core function is one-click disableable, so that in an incident its CPU, connections, and downstream quota are ceded to the critical path. Common forms: degrade to cache or defaults (when real-time stock cannot be fetched, show in-stock and verify at the backend); degrade feature richness (during a sale, switch off personalization and show everyone the same list); degrade to async (accept the request into a queue and return "processing"). Degradation plans must be finished while the sea is calm—never improvised at the incident scene. Without plans, an overloaded system has only full-on and full-off; with plans it holds a whole row of pressure-relief valves that can be loosened step by step.

## SLI / SLO / SLA and the error budget

- **SLI** (indicator): the measured number, e.g., successful responses / total requests over the past 5 minutes.
- **SLO** (objective): the internal passing line set on the SLI, e.g., success rate ≥ 99.9%.
- **SLA** (agreement): the line written into the contract with penalties for breach, usually looser than the SLO as a safety cushion.

The error budget brings the three to life: with the SLO at 99.9%, the 0.1% is the allowed failure quota (about 43 minutes a month). While budget remains, ship boldly and experiment; once it burns out, a common policy freezes non-reliability releases and turns everyone onto stability until the budget is rebuilt—the specific freeze window, exceptions, and recovery conditions are set by each team. It turns the dev-versus-SRE tug-of-war over stability and iteration speed from whoever shouts loudest into a shared number, and it exposes a counterintuitive truth: chasing 100% reliability is wrong—it means never daring to release or experiment, while users cannot tell 99.9% from 100%. The choice of nines returns to the business question: every additional nine is bought with iteration speed and real money.

## Recovery design: RPO and RTO

High availability is not disaster recovery, and backup is not recoverability. Three concepts habitually conflated: high availability (HA) eliminates single points with online redundancy, countering component failure; disaster recovery (DR) counters the loss of an entire region or datacenter; backup is the final backstop, countering the logic errors and mistaken deletions the first two cannot stop. RPO (recovery point objective) is the maximum data-rollback time window the business can tolerate; RTO (recovery time objective) is the maximum tolerable downtime—both are business-given targets. Backup and replication frequency, data size, dependency order, recovery-runbook automation, and drill maturity jointly determine actual recovery capability, and actual capability must cover the targets.

Derive from business loss: first ask "how much does an hour of lost data cost, and an hour of downtime", derive RPO/RTO, then work backward to the scheme: near-zero RPO usually requires a write to be persisted in an independent failure domain before acknowledging the client (synchronous replication is the common means); minute-level RPO tolerates asynchronous replication; hour-level RPO fits scheduled backup with off-site storage. Synchronous replication still cannot stop logic errors and malicious tampering—those risks need point-in-time recovery (PITR) or immutable backups as the backstop. Multi-region deployment is DR's premium option, at the highest cost—not a default.

Four iron laws: **recovery tooling must not depend on the system being recovered** (in Meta's 2021 outage, the normal means of accessing the data centers were unavailable, and getting engineers onsite was delayed); **recovery order must be predefined** (DNS first or database first—wrong order causes a second incident); **backups must be verified through regular restore drills**—an unverified backup does not equal recoverability; **point-in-time recovery (PITR) is the key capability against logic errors**—backing up only current state means mistaken deletions and tampering are faithfully replicated into the backups too.

## Chaos engineering: proving resilience

The code paths triggered only by failure (breaker logic, degradation branches, failover switching) are precisely the ones that run least and are tested thinnest in normal times—the most likely to rot silently. Only when a real incident arrives do you discover the degradation switch died three months ago. An undrilled disaster-recovery plan is roughly equivalent to none.

Chaos engineering injects failures into production actively and controllably, exposing weaknesses early in small controlled explosions (Netflix's Chaos Monkey kills production instances at random, forcing every team to assume instances can die at any moment until redundancy and self-healing become default habits). Its essence is the scientific method: define steady-state metrics, hypothesize (killing one instance should not drop the success rate), inject the fault and test, and fix what fails. It turns "hope it holds" into "verified that it holds". Strict preconditions: monitoring that can see the impact, blast-radius control for timely abort, one-click stop. Injecting faults into production without guardrails is not chaos engineering; it is an incident.

## Case: how a shaky hand took down half the internet

**AWS S3 (2017).** An engineer ran a documented command to take servers offline and mistyped the parameter, hitting a large batch of machines supporting the index and placement subsystems. Restarting the index subsystem and validating the integrity of its metadata took far longer than expected; much of the internet depending on us-east-1 S3 was down about 4 hours (official AWS post-incident report, "Summary of the Amazon S3 Service Disruption", 2017-03-02). Lessons: shaky hands are the norm ("everything fails" includes people); a command able to hit that wide a range means the blast radius is out of control; the post-incident hardening was precisely adding guardrails to dangerous operations.

**Meta (2021).** A command assessing backbone capacity accidentally withdrew all backbone connections, and a bug in the audit tool failed to stop it. DNS servers detected the disconnection and proactively withdrew their BGP route announcements, and Facebook vanished from the internet for about 6 hours (Janardhan, "More details about the October 4 outage", 2021-10). Normal means of accessing the data centers were unavailable because their networks were down, and the facilities' physical and system security protocols slowed getting engineers onsite—MTTR stretched badly. Lessons: a textbook cascade (a local action amplified into global disaster through the health-check to route-withdrawal chain); recovery tooling must not depend on the system being recovered—an easy circular dependency to overlook.

## Relationship to other documents

- The correctness basis of retries and idempotency is in [Consistency](./09-consistency.md).
- The capacity view of overload and bottlenecks is in [Scaling](./11-scaling.md).
- How observability tooling supports failure detection is in [Observability and reliability](./technology-selection/07-observability-and-reliability.md).
