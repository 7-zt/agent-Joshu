# Distributed Systems

The hard constraints that networks, time, concurrency, and partial failure impose on design. Use for any architectural judgment involving cooperation across machines, services, or processes—these constraints decide which approaches are simply not viable.

## Three luxuries of the single machine

Three things taken for granted in single-machine programs all vanish once you cross to a second machine:

| Single-machine world | Distributed world |
| --- | --- |
| Function calls always arrive | The network is unreliable: loss, reordering, duplication, delay, partition |
| One "now" for the whole world | No global clock: every machine's watch disagrees; "simultaneous" is an illusion |
| Either success or failure | Partial failure: some nodes succeed, some fail, some are of unknown status |

Partial failure is the deadliest. You send a request to another machine and hear nothing for two seconds: did it not receive it? Is it computing? Did the reply get lost? Or is the whole machine down? **You cannot distinguish it being dead from it being slow** (gray failure). The only weapon is the timeout, and a timeout is inherently a guess: guess short, and you misjudge a merely-slow node as dead while retries pile on; guess long, and failure recovery turns sluggish. Distributed reliability design is, to a large extent, wrestling with "cannot tell dead from slow".

The mental flip: in the single-machine era, calls are assumed to succeed; in the distributed era, assume every cross-network call may fail, time out, or arrive twice—then ask "what happens to my system in that case". That is the watershed between beginner and intermediate.

## Consistency is a spectrum, each step with a price list

Between strong and eventual consistency sit intermediate steps; each step stronger costs latency and availability:

| Step | Guarantee | Fits |
| --- | --- | --- |
| Linearizability | Anyone reading any node immediately sees the latest value, as if one machine existed | ATM balances, uniqueness allocation |
| Sequential consistency | Everyone sees the same order, though possibly not in real time | Configuration rollout |
| Causal consistency | Causally related operations keep their order; unrelated concurrent ones are not forced into order | Group chat, comments |
| Eventual consistency | Converges eventually; during the window, everyone sees their own view | Like counts, view counts |

Causal consistency is a practical middle step: you replied to my message—causally related operations appear in the same order for everyone; two strangers posting independently—whose came first does not matter. It is far cheaper than linearizability yet avoids the absurdity of seeing a reply before the original post.

The judgment is not "as strong as possible" but "how strong does this data deserve". Spend the precious strong-consistency quota where things actually break.

## PACELC: the bill you pay every day

CAP says that under partition you choose C or A. PACELC fills in the missing half: most of the time the network is fine—what are you paying then?

- Under partition (PACELC's PAC): correctness (C) or being online (A).
- Without partition (the EL part, 99% of the time): low latency (L) or strong consistency (C).

Even with the network perfectly healthy, strong consistency still costs: making all replicas agree on one value requires inter-node round trips. Consistency is not accidental insurance you pay when disaster strikes; it is a utility bill you pay daily—every decision whether to wait for all replicas is trading latency for consistency.

## No global clock? Use causality

Every machine's physical clock skews, network delay is uncertain, and judging who came first by comparing two watches is unreliable (the watches themselves disagree). The way out is abandoning physical time for causal relationships: not asking what time it happened, only whether it happened because of that other thing.

Logical clocks carry the sender's counter on every message; the receiver pushes its own counter higher, and causal order is nailed down. Lamport clocks order all events totally but cannot distinguish a true reply from a coincidence of concurrency; vector clocks identify concurrent-write conflicts (two people edit the same row simultaneously; the system knows they collided and lets a human decide); hybrid logical clocks (HLC) stitch physical time and logical counters together—modern distributed databases commonly use them for consistent snapshots.

Most business systems never need logical clocks; do not adopt them to look advanced. But when the system must guarantee causal correctness they are unavoidable: merge order in real-time collaborative documents, message ordering in instant messaging, consistent snapshots in distributed databases.

## Consensus is the most expensive—do not squander it

A group of machines reaching ironclad agreement on something (who is the primary, what the 100th log entry is, who owns the lock) relies on consensus protocols (Raft/Paxos). What it buys is hardcore: with a minority of nodes down, the surviving majority still reaches a unique decision—the closest thing to a single authoritative truth in the distributed world.

The cost is equally blunt: every decision takes a majority vote round trip—latency; at least three or five nodes; write throughput capped by the single leader; membership changes are subtle and error-prone. Consensus is a board vote: suited to important decisions, not daily chatter.

Use it only in the few places that truly need one authoritative order: leader election, cluster metadata, distributed locks, replicated logs. A system that pushes every business write through a consensus group is paying dearly for global uniqueness nobody asked for. The anti-pattern is treating a Raft cluster as a general-purpose database.

## End-to-end exactly-once cannot ride on the message transport alone

Exactly-once delivery for arbitrary external side effects is not something the transport layer can guarantee: you sent a message and got no ack—only two choices exist: resend (at-least-once, possibly duplicate) or do not resend (at-most-once, possibly lost). That is not a product defect; it is physics.

Under bounded conditions the transport can offer exactly-once semantics: Kafka, within the consume-process-produce boundary, uses idempotent producers, transactions, atomic offset commit, and the read_committed consumer isolation to provide exactly-once in the stream-processing sense (official Kafka design doc, https://kafka.apache.org/43/design/design/). But that covers only the boundary it governs—once consumption writes to an external database or calls a third-party API, those side effects may still duplicate or vanish.

The real solution across external side effects moves the guarantee elsewhere: **at-least-once delivery + consumer-side idempotency = exactly-once in business effect.** Idempotency usually means giving the operation an idempotency key; the consumer records processed keys in a dedup table, and duplicates simply skip. Do not expect transport-level exactly-once to cover external side effects—sink the correctness into the consumer.

## Case: a 43-second partition scrambled GitHub for 24 hours

In 2018, a fiber replacement cut a US-East datacenter off from the network hub for 43 seconds (GitHub Engineering blog, "October 21 post-incident analysis", 2018-10-30, https://github.blog/2018-10-30-oct21-post-incident-analysis/). During the cut, US-East kept accepting writes (it was not dead, merely unreachable—gray failure); the Raft-based orchestrator followed majority consensus and automatically failed the primary over to US-West; when the network healed, both coasts held data the other lacked—two diverged clusters each believing itself primary. Automatic reconciliation risked data loss, so repair was manual and the service stayed degraded for 24 hours.

Lessons: partial failure means you cannot tell dead from slow; consensus can reach agreement within a majority yet, under partition, perfectly by the rules steer the system into a catastrophic topology. The stronger the automation, the more you must think through what it will decide in extreme conditions. Afterward GitHub forbade the orchestrator from promoting primaries across regions—an automatic failover designed for single-node failure made, in the face of a whole-region partition, a decision the application layer could not absorb.

## Relationship to other documents

- Concrete consistency engineering along the spectrum (Saga, Outbox, event sourcing) is in [Consistency](./09-consistency.md).
- Timeout, retry, and idempotency details are in [Resilience](./10-resilience.md).
- Message-system selection is in [Caching, messaging, and events](./technology-selection/04-cache-messaging-and-events.md).
