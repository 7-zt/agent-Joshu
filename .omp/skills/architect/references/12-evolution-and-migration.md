# Evolution and Migration

Planning splits, migrations, rollbacks, and retirement based on evolution trigger signals and technical-debt evidence. Use for modifying running systems: breaking up a monolith, replacing components, migrating data, decommissioning old implementations.

## The big rewrite is almost always doomed

Every engineer inheriting a mess has nursed the "tear it down and rewrite" thought, and it is almost always wrong—not because the old code is good, but because the rewrite physically cannot win: the old system will not pause and wait; it keeps taking bug fixes and features while being rewritten, so the target moves. The dirty, weird code holds years of pit-hardened tacit knowledge (a baffling `if` works around one customer's dirty data; a retry loop absorbs a third party's seizures)—one rewrite and the scar tissue resets to zero, and the same pits get stepped in again.

The biggest cost of rewriting is not writing the code again; it is stepping into the same pits while slowing current delivery. Netscape rewrote the browser from scratch and shipped no usable new version for nearly three years while IE devoured the market. For a running system that is still evolving, default to incremental replacement: old and new coexist; old blocks shrink; new blocks grow; every step can stop, roll back, and keep the system online. A rewrite can still be reasonable when the system is small, has no live traffic yet, or its total replacement cost is demonstrably lower than an incremental migration.

## Trigger signals: measure before moving

Upgrading the architecture is "a decision triggered by real signals and backed by evidence", not "a scheduled refactoring ritual". The numbers are experience-based heuristics (rough orders of magnitude from common engineering practice, not verified on this project)—not iron laws. The real basis is always some quality attribute capped by a real, measured bottleneck, attributed to a concrete workload (which query class, which path)—not jumping from a CPU number to a solution:

| Signal class | Observable signals | Common remedies |
| --- | --- | --- |
| Data tier | Primary CPU persistently above 70%, read queueing; cache hit rate falling below 90%; single-table rows exceeding ten million and approaching one hundred million, single-database volume past hundreds of GB; write QPS approaching the single-database ceiling | Attribute queries first (wait events, slow queries, callers, read/write split); the common findings are missing indexes, report scans, or lock contention. Read replicas and cache tuning are options after evidence points at the read path; sharding is the last resort after attribution to write capacity with other levers exhausted (choose the shard key with care) |
| Latency | P99 persistently over target while P50 is fine; synchronous operations leaving users waiting seconds; regular spikes | Treat tail latency; async to shave peaks; elastic scale |
| Availability | Availability requirements stepping up; one component's death paralyzing everything (SPOF); incidents with wide reach and slow recovery | Redundancy, failure-domain isolation, rate limiting, degradation, circuit breaking |
| Organizational efficiency | One change dragging a whole area, releases slowing; multiple teams blocking each other in one codebase; onboarding taking weeks | Clarify module boundaries first (service extraction not required); this is the true microservices signal, but check team boundaries first |

Discipline: measure before judging—talking about upgrades without monitoring data is guessing; solve one bottleneck at a time, never a big-bang refactor; write one decision record per upgrade, the context column full of signals; do not move without a trigger—upgrading without signals is nine-times-out-of-ten over-engineering or fashion-chasing.

## Strangler Fig: intercepting around the old system

Put a facade/router around the old system and gradually shift traffic to the new implementation: the routing table's "go to new" entries grow, the old monolith gets hit less and less, until it receives no traffic at all and is strangled offline.

The fundamental difference from the big rewrite: old and new always coexist; traffic switches block by block; each block switched is one small, rollback-able release—not one giant version betting the system's life. The pattern's vital point is the facade: all external requests must pass through it before anyone can decide old-or-new. Without it, you do not even have the switch to quietly move one function onto the new implementation. The strangler does not chase speed—two implementations often coexist for a while—but it splits the one-shot mega-risk of betting the whole system into a sequence of controllable risks, one block at a time.

## Branch by abstraction: swapping implementations behind an abstraction

When the replacement target is a core component called from countless places inside the system (the cache layer, the ORM, the model provider), you cannot intercept from outside. The novice instinct is to hide in a long-lived feature branch for two months of changes—the longer the branch lives, the further it drifts from the trunk, the final merge is a disaster, and the trunk cannot ship that part the whole time.

Branch by abstraction flips it: no long-lived branch; all changes on the trunk, with an abstraction layer letting old and new coexist. Five steps: ① insert an abstract interface in front of the component to replace; ② migrate all callers to depend on the abstraction (behavior unchanged); ③ write the new implementation behind the abstraction (flag-controlled, no traffic yet); ④ flip the flag gradually, flipping back whenever problems appear; ⑤ once the new implementation is stable, delete the old one. "Open a branch and change slowly" is the most expensive anti-pattern for large-scale refactors—it manufactures a merge bomb with a fuse of unknowable length. The cost of one more abstraction layer buys the safety of stopping, shipping, and rolling back at any moment.

The typical AI-system application: gather model calls behind a `ModelClient` abstraction, and behind it switch from direct provider calls to an AI gateway. Model swaps are a high-frequency event in the AI era; this seam must exist.

## Parallel run: let real traffic be the judge

Strangler and branch-by-abstraction give you the switch, but before flipping it, on what grounds do you believe the new implementation is correct? Unit tests never cover real traffic's devious distributions, and AI systems have no assertable right answer at all.

Parallel run (shadow traffic / dark launch): old and new run simultaneously on the same real requests; the old implementation's result returns to the user (unnoticed), while the new implementation's result is silently compared and differences logged. Only when the divergence rate (or quality-degradation rate) drops low enough do you actually cut traffic. Discipline: the old implementation's result always returns to the user; the candidate's exceptions are all swallowed (never let experiment code break production); randomize execution order to expose order dependencies.

The greatest fear in refactoring a critical path is "I thought it was equivalent, but it was not". The parallel run turns fear into quantified data—real traffic as judge, not confidence as judge. It fits critical computations with complex logic, high error costs, and unknowable boundary cases (billing, permissions, risk control). The cost is running two systems at once; it is a critical-path heavy weapon, not a daily tool. GitHub's open-sourced Scientist library from its permission-check refactor is a living template (GitHub Engineering blog, 2016-02-03, https://github.blog/2016-02-03-scientist/); in the AI era its value rises instead of falling: AI produces new implementations fast, and the parallel run judges their correctness with data—speed to the model, confidence to the data.

## Zero-downtime data migration

Data is the hardest to change: code can blue-green roll back; data has one copy, and a botched change is unrecoverable. When swapping databases, changing table structure, or splitting stores, follow the expand-contract five steps, each rollback-able:

1. **Dual-write.** New data is written to both old and new stores; reads still go to the old. Exit: stop writing to the new store.
2. **Backfill.** Bulk-move historical data into the new store. Exit: a batch job writing only the new store, stoppable anytime. The AI-specific cost: backfilling a vector store means re-embedding every historical document—costly in both money and time; plan it in batches with rate limits, budgeted as a cost line.
3. **Shadow-read verification.** Reads hit both stores; the old store's copy still returns to the user; compare old versus new for agreement (this is the parallel run). Exit: compare without switching.
4. **Switch reads.** Once the agreement rate is high enough, switch reads to the new store—still dual-writing. Exit: reads switch back to the old store, which dual-writing has kept fresh.
5. **Cleanup.** After a stable observation period, stop dual-writing and retire the old store. The only irreversible step—do it last, with a generous observation window.

Through the first four steps the old store remains authoritative and fresh, so you can retreat instantly at any point. Data-migration disasters almost all come from one-shot cuts: stop service at midnight, run the migration script, deploy, pray.

## Splitting the monolith: modularize first, extract services on demand

Treating microservice extraction as progress itself is the novice's most common error. The correct strategic order:

ball-of-mud monolith → modular monolith (one deployment unit, enforced internal module boundaries) → extract microservices only where a real bottleneck exists.

First draw the boundaries inside the process (changing boundaries costs nearly zero; redraw if wrong); once the seams have been hammered stable by real business, pay the distributed-system price only for the part that genuinely needs independent scaling, release cadence, or failure isolation—and leave the rest in the modular monolith, which is a fine destination. The modular monolith decouples "boundary design" from "distributed deployment": take microservices' most valuable part (clean boundaries) first, and defer the most expensive part (distributed ops) until it is unavoidable.

Find seams along natural business-capability boundaries (DDD bounded contexts), not technical layers. Choosing which block to extract first: which one most needs independent scaling, independent release, or failure isolation? Service count is never a goal; it is a price paid for a specific quality attribute.

Segment's warning bell: they split for failure isolation until the system was over-fragmented (one worker per destination, a week to change a shared library) and finally retreated to a monolith. Over-splitting is as deadly as blind splitting.

When new and old models fight, use an anti-corruption layer: build a translating isolation wall between the new services and the old system; the new services talk only to cleanly translated interfaces, and the old model's rot cannot seep in.

## Preventing rot: fitness functions

How do you keep the boundaries you worked hard to draw from being kneaded back into mud by the next few hundred commits? Write architectural constraints as tests that run automatically, fail, and block CI: dependency checks (the orders module must not import billing internals; in AI systems, "all model calls must go through the abstraction layer" is likewise a dependency check), performance tests (fail when p99 exceeds target), contract tests (fail on breaking API changes).

Architecture is not a statue finished when the diagram is drawn; it is a living system that needs continuous maintenance, and a living thing without an immune system inevitably rots. Fitness functions are the architecture's immune system: they do not stop the system from growing; they only stop it from rotting as it grows. Without them, every boundary drawn with effort today is just waiting for one rushed afternoon to be stabbed through.

## Relationship to other documents

- The rulers for when to upgrade and how decisions are recorded are in [Architecture decisions](./07-architecture-decisions.md).
- The relation between organizational boundaries and splitting is in [Organization and ownership](./13-organization-and-ownership.md).
- The consistency engineering of dual-write and backfill in migrations is in [Consistency](./09-consistency.md).
- Full phased-evolution cases (MVP to scale) are in upstream chapters 20 and 21.
