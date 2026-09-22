# Consistency

Consistency models, transaction boundaries, and conflict handling as engineering practice. Use for choosing approaches to cross-service data operations, fixing dual-write problems, and designing reliable events and state.

## The problem: the network cuts the transaction boundary

In the single-machine era, one `BEGIN…COMMIT` made "deduct stock, create order, issue coupon" all-succeed or all-fail. Once those three things sit in three services with three databases, no single local transaction can enclose them. Stock was deducted and the order created, but the coupon never went out—data half-done.

The scheme for re-enclosing three databases in one transaction is two-phase commit (2PC): a coordinator first asks all participants whether they are ready (voting); only on all-yes does it commit. The costs keep core paths away: between vote and commit, all participants lock their data and wait—one slow participant drags everyone; if the coordinator dies mid-commit-command, participants block in an in-doubt state until the coordinator recovers—persisted transaction logs and a recovered coordinator can complete the decision (PostgreSQL's prepared transactions are WAL-persisted and survive crashes, https://www.postgresql.org/docs/current/two-phase.html), and the coordinator service itself can be made redundant, but blocking and recovery dependence are its core risks; requiring all participants online serializes the availability of multiple services, in direct conflict with CAP's A.

2PC is not unusable: inside a single database or among a few tightly coupled resources (multiple shards of one database, say) it still has a place. Across multiple independent services under high concurrency, the mainstream answer is not a stronger transaction but giving up cross-service strong transactions for eventual-consistency schemes that tolerate intermediate states.

## Saga: a chain of local transactions plus compensation

Split the big transaction into a chain of local transactions, each step running only in its own service's database. On failure, there is no rollback—instead, compensation actions run in reverse to offset what was done: money already paid to the merchant is compensated by initiating a refund and logging a reverse entry; an email already sent cannot be unsent, so a correction email goes out; stock already deducted is added back—but by then someone else may have bought it, which is compensation's built-in trouble.

**Compensation is not a database rollback.** Rollback means the transaction never committed and the database acts as if nothing happened; compensation means the previous step already committed and may even have external side effects—history cannot be deleted, only counteracted with a reverse operation. Saga moves consistency from a database guarantee to a business-process guarantee: cross-service locks are saved, but a state machine must now be managed—at step ③ unfinished, the system truly sits in a "order created, stock deducted, unconfirmed" semantic lock window, and the business must answer what the user sees then, whether cancellation is allowed, and whether the half-finished order is visible to others.

Two chaining styles and how to choose:

- **Orchestration**: control flow concentrates in an orchestrator; the whole picture is visible, observability is strong, and one place shows which step is stuck. Fits critical long flows with many steps, complex compensation, and strong monitoring requirements; the risk is the orchestrator bloating into a god service.
- **Choreography**: control flow distributes across an event chain, with no center, but observability weakens and debugging feels like assembling a puzzle. Fits lightweight flows with few steps and few participants; the risk is that once steps multiply it turns into event spaghetti nobody can narrate.

A plain rule: when you must read through several services' logs to piece together what happened to one order, it is time for an orchestrator. Uber introduced its self-built persistent workflow platform in "Announcing Cadence 1.0" (2023-06-22, https://www.uber.com/us/en/blog/announcing-cadence/); DoorDash documented its practice of adopting Cadence as a fallback for reliable asynchronous flows in "Building Reliable Workflows: Cadence as a Fallback for Event-Driven Processing" (2022-10-21, https://careersatdoordash.com/blog/building-reliable-workflows-cadence-as-a-fallback-for-event-driven-processing/). Turning the Saga orchestrator into platform-level infrastructure is the shared route of both.

## Outbox: the transactional answer to dual writes

A service finishes handling a request and must both update its own database and emit a message. Those two actions live in two systems—a database and a message middleware—no transaction can enclose both. Write the database first, then send: a crash between the two loses the message. Send first, then write: a failed write births a phantom message. The insidious part: this almost never shows in test environments, yet keeps producing database-versus-downstream mismatches in production's long tail.

The fix is the Transactional Outbox: instead of sending a real message, insert a row into an outbox table in the same database, committed in the same local transaction as the business data—the two live and die atomically. Then an independent relay reads the table and actually sends:

- **Polling publisher.** Periodically SELECT unsent rows, send, mark sent. Simple, with polling delay.
- **Transaction-log tailing (CDC).** Read the database binlog/WAL directly; new commits to the outbox table are captured and sent at once (e.g., Debezium's Outbox Event Router)—zero polling, order preserved. The database's transaction log is itself the truth stream of what happened.

When you find yourself doing "update the database and also send a message", default to considering an Outbox or transaction-log CDC (rather than calling `kafka.send()` right after the write); if you have reasons not to (both actions on one transactional resource; native transactional messages), state them in the decision. Note the Outbox's guarantee is at-least-once (the relay may crash after sending but before marking, resending), so it must pair with idempotent consumption.

## The idempotency trio

Systems with external side effects usually choose at-least-once delivery, and with retries everywhere on the network, executing the same operation twice is the norm in distributed systems, not the exception. Idempotency: executing the operation once and N times leaves the system state identical. `SET balance = 100` is idempotent by nature; `balance = balance + 100` run twice adds twice—not idempotent by nature—and add/subtract, ship, pay, message are precisely the non-idempotent operations that must never go wrong.

The three-piece retrofit:

1. **Idempotency key.** Every operation carries a globally unique ID (e.g., `pay_order_12345`).
2. **Dedup table.** The consumer records processed keys.
3. **Same-transaction execution.** Processing the business and writing the key commit in the same local transaction. Execute first, write key after, split into two steps—a crash between them leaves "money deducted but key not recorded", and the retry deducts again.

**Retries and idempotency must appear in pairs.** Before writing "retry on failure", ask: is the retried operation idempotent? Non-idempotent plus automatic retry equals a random double-charge machine. Stripe makes `Idempotency-Key` a first-class request header in its API docs (https://docs.stripe.com/api/idempotent_requests) precisely because client networks will retry, so the server must be idempotent.

## Event sourcing and CQRS

Two heavy weapons; the vast majority of CRUD systems need neither, and forcing them on adds congestion. Knowing when they are warranted suffices.

**Event sourcing.** Store not the current state but the series of events that produced it: not "balance = 100", but "account opened +0, deposit 80, deposit 50, withdraw 30"—balance is computed by replay. Double-entry bookkeeping (the ledger appends, never edits; errors are corrected by contra entries) and Git (stores a commit sequence; checkout is time travel) both embody the idea. What it buys: complete audit (every state change an immutable event), time travel (replay to any moment), one event stream read many ways (new requirements write new projections, history untouched). The costs: querying is hard (you cannot WHERE an event stream—that is exactly the problem CQRS solves); event schema evolution is a hard battle (events are never edited or deleted; old events must replay under new code, backward-compatible across years); replay cost (periodic snapshots, like game save points). Fits domains where audit and traceability dominate and the business is naturally a series of events (ledger, order state machines, collaborative edit history). Ask first: do you truly need the complete history of every past moment? If not, store state and sleep well.

**CQRS.** One model for writes, another for reads, with read models continuously updated by event projection. Like a restaurant splitting kitchen from menu: the kitchen cooks and records accurately; the display layer shows things at a glance; each optimizes for itself, and the waiters keep them roughly in sync (the menu's sold-out tag may lag half a beat—eventual consistency). Its most practical use in microservices: with database-per-service, cross-service joins are impossible, so a read-view store subscribes to each service's events and pre-joins and flattens the data into it. The sweet: reads and writes optimize and scale independently (in read-heavy systems the read side clones replicas wildly while the write side stands still); one write model projects into any number of tailored read models; complex queries stop dragging the write store. The bitter: read models are eventually consistent (an order just placed may be missing from the list—the product must face this); component and ops complexity doubles; one more projection pipeline that must not lose or scramble. The worthy scenarios are narrow: severely asymmetric read/write load, or the same data queried in four ways—list, detail, search, report. A plain test: CQRS starts paying back when report queries force a pile of bizarre indexes onto the core write store and slow down ordering.

## Schema and contract evolution

Logic changes easily; data does not. In the event-driven world this is amplified: once a schema, event structure, or API contract has dependents (other services, three years of accumulated old events, un-upgraded old clients), it cannot change at will. During rolling upgrades, old and new code are online simultaneously: new code must read old data (backward compatibility), and old code ignoring new data must at least not crash (forward compatibility).

The safe-migration pattern is expand-contract (parallel change)—the intuition is building the new bridge beside the old one: both bridges open to traffic (Expand, old and new fields coexist), traffic moves onto the new bridge (Migrate, dual-write and backfill), then the old bridge comes down (Contract, old fields deleted). Never a moment of closure. The instant you RENAME/DROP a column directly, every un-upgraded old instance crashes together.

## Relationship to other documents

- The consistency spectrum and CAP/PACELC principles are in [Distributed systems](./08-distributed-systems.md).
- The resilience angle on retries and idempotency is in [Resilience](./10-resilience.md).
- The consistency dimension of storage selection is in [Data stores](./technology-selection/03-data-stores.md).
