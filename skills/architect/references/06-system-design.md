# System Design

The process of deriving a complete, verifiable system design from requirements. Use for designing new systems, rehearsing the design of major features, and building the "how it should have been derived" reference for reviews.

## Architecture is squeezed out of constraints

A novice handed a design task grabs a pen and draws boxes: servers, a database, then stalls. A senior spends the first minutes drawing nothing and only asking: who uses it, how many, how fast, can data be lost. Without the constraints clear, anything you draw is blind drawing.

The design process is not a mystical formula; it is putting the judgment order in line: requirements and constraints first, then size estimation, then boundaries, then data, then diagrams, then component depth, then bottlenecks, and finally a look back at tradeoffs. It works the same for real design and design drills—the underlying moves are identical.

## The eight steps

The steps are not a straight line but a loop that doubles back; when a problem surfaces, return to any step and redo it.

**① Clarify requirements and scope.** Ask questions first, turning vague into explicit. Three kinds: functional boundaries (what the MVP does and does not do—explicitly fencing out the not-doing matters more than listing the doing); users and scale (who, how many, how fast it grows); quality and constraints (how fast, is brief unavailability acceptable, can data be lost, any compliance red lines). The goal is not satisfying every requirement but confirming which requirements do not actually matter. Every chunk cut from scope simplifies the architecture by an order of magnitude.

**② Estimate scale.** Back-of-the-envelope: not precise, just the right order of magnitude. Anchor numbers: a day has about 10^5 seconds; 10 million DAU at 10 actions each ≈ 1000 QPS average; peak is usually 2–5× the average; social content starts around 10:1 read/write. Example: a 10-million-DAU posting app, one post and 50 views per user per day—100 writes/s, 5000 reads/s, a 50:1 ratio, 3.6 TB/year plain text versus 1.8 PB/year with images: a 500× difference that completely changes the storage design. The estimate's value is not numerical precision but forcing you to find what crushes the system first: reads, writes, storage, or bandwidth—different answers change everything downstream. AI systems add a token-cost line here (see below).

**③ Define core use cases and API boundaries.** Treat the system as a black box, list the actions the outside world can take, and pick one or two main channels (the highest-frequency actions that best express what the system is). With boundaries clear, every internal module gets a target: which use case does it serve? A module serving no use case is over-engineering.

**④ Design the data model.** Once use cases are clear, design data immediately—not services first. Two things: draw the conceptual model (core entities and relationships, no DDL yet); assign each data class a storage shape (by access shape; see [Data and state](./05-data-and-state.md)). Get data modeling right and the rest mostly flows; get it wrong and no amount of cache saves you.

**⑤ Draw the high-level architecture.** In C4 order, Context then Container (see [Views](./03-views.md)). The first sheet should be five or six boxes with arrows in broad strokes, enough to explain how data flows. Opening with twenty boxes is using drawing diligence to disguise unfinished thinking.

**⑥ Go deep on key components.** Pick one or two soul components and drill in—not every box. Identifying them loops back to step ②: whatever scale will crush first is the one. If reads explode, the soul component is the read path; if compute explodes (AI products), it is inference serving. Here architecture patterns earn their keep: event-driven for decoupling, CQRS when read and write shapes diverge sharply, a message queue for absorbing spikes. Patterns answer specific questions; they are not for showing off.

**⑦ Find bottlenecks and scale surgically.** Ask: at 100× load, what breaks first? Then second, then third. Tie every bottleneck to the concrete system's numbers, not generic "add cache, add shards". If the bottleneck is reads, do not optimize writes; if it is bandwidth, leave the CPU alone. Hammering where it does not hurt is the most common waste.

**⑧ Review tradeoffs; list risks and open questions.** Look back at every decision and put the costs on the table: what each choice gave up; which assumption, if wrong, collapses the design; what remains unresolved and needs flagging. Being able to name your design's weaknesses is precisely the proof you have thought it through. These tradeoff rationales should become decision records (see [Architecture decisions](./07-architecture-decisions.md)).

## Example highlights: URL shortener

Running the shortener through the eight steps, a few key derivations:

- Estimation: ten million new links daily, a 100:1 read/write ratio—about 10k read QPS, 100 write QPS. Conclusion: extremely read-heavy; the architecture's center of gravity is the read path and the cache is its lifeline. 9 TB over five years is unremarkable—no need to shard on day one. 18 billion links need collision-free codes; 7 characters over a 62-symbol alphabet gives about 3.5 trillion combinations, ample headroom. The code length is computed from the estimate, not guessed.
- Data model: one core entity (short code → original URL + expiry), a pure key lookup. A small team defaults to a relational database (one table plus a unique index covers transactions and operational familiarity); when read/write volume or latency demands actually arrive, migrate to a KV store (pure key-lookup shape, replaceable smoothly). Both steps are right; the difference is only the evidence.
- Main channel: redirects carry 100× the traffic of creation; every design decision serves that path first.

## Full case: should the Rails monolith be split into microservices?

A realistically shaped task showing how the steps combine across documents.

Background: a six-person team maintains a three-year-old Rails monolith (B2B SaaS). The primary database CPU sits above 70% for long stretches; monthly reports keep getting slower; two teams block each other's releases in one codebase. Someone proposes "split into microservices".

Six actions, folded from the eight-step frame:

1. **Clarify and constrain (01).** Constraints: six people, Rails skills, no platform engineering. Quality-attribute status: transactional P99 acceptable; reports drag the primary store down; release blocking is the top pain. Suspend the pre-decided conclusion "split into microservices".
2. **Gather evidence, don't guess (02).** Pull primary-store wait events and slow queries: the CPU bulk is month-end report table scans, not transactional writes; read/write ratio 9:1; the two teams' blocking concentrates on shared tables and shared callbacks in the order and billing modules. The evidence rejects the "write capacity" hypothesis and points at two real problems: an unisolated reporting read model and unclear module boundaries.
3. **Split the read model first (tech-selection/03).** The transactional store remains the source of truth; Outbox/CDC syncs data into an analytical store; reports query only the analytical store, and the report share of primary CPU disappears. Minute-level freshness suffices—no real-time chase, sync lag acceptable.
4. **Then clean module boundaries (12, 13).** Split orders, billing, and the rest into enforced-boundary modules inside the process (dependency checks in CI) with explicit owners and release responsibilities. This reduces blocking from shared tables, callbacks, and code changes (a modular monolith still shares a deployment unit and release pipeline); verify the effect with both teams' lead time and conflict counts. If remaining blocking comes from the shared release pipeline itself, module boundaries cannot fix it.
5. **Reasons not to split now (04, 12, 13).** The team has no platform-engineering capacity; multi-service operations costs lack anyone to absorb them. Both real problems (report isolation, release blocking) have cheaper solutions; there is no evidence yet that microservice benefits exceed costs; there is no independent-scaling need. The one future signal that could trigger extracting a service: a module genuinely needing independent scaling or its own release cadence, with cross-team blocking costs persistently exceeding distributed-system costs. Record the re-review conditions.
6. **Record the decision (07).** Candidates (split to microservices / isolate the read model only / modularize only / do nothing), tradeoffs, assumptions (report load will not grow tenfold), and re-review conditions, written as an ADR.

The case's takeaways: evidence before solutions; read-model isolation and modularization are the high-value intermediate states before any service extraction; the conclusion is "not now", not "never".

## What AI systems add

AI systems run the same eight steps with three additions:

**Step ② gains a token account.** Example: one million DAU consulting, six turns each, about 2000 input and 400 output tokens per turn—about $0.0072 per turn at mid-tier pricing, roughly $43,000/day over six million turns. This account sets the architecture's center of gravity on the spot: cost is the number-one constraint, not an optimization item, so cost levers (model routing, prompt caching, leaner RAG context, semantic caching) enter the design at version one. High-frequency conversation and low-frequency high-stakes actions (refunds, say) have completely different failure costs and must be split into separately served paths.

**Step ⑥ gains a gate that keeps uncertainty away from side effects.** When a hallucination-capable model touches money, the golden rule: the model proposes, deterministic code executes, and the model never touches money. The execution layer is a purely deterministic service: verify ownership and state; block duplicate requests with idempotency keys (models re-propose, networks resend); route large amounts to human approval; drive a state machine, commit transactions, and reconcile periodically as the backstop. Not one line of AI belongs inside that gate. Hallucination defense is structural, not prayer: force retrieval-grounded answers, force citations, hand off to humans when retrieval confidence is low (staying silent beats guessing).

**Step ⑦ reorders bottlenecks.** The first bottleneck in an AI system is usually exploding token cost (the bill crashes before the servers do); the second is inference queuing inflating time-to-first-token; the third is retrieval-quality decay breeding hallucination complaints. The responses to these problems all depend on the estimate in step ②. The earlier the token account is done, the clearer the downstream design.

## Checking the design output

Self-check on completion: can you name the use case every box serves; does every line have direction and meaning; can every storage choice in the data model cite its access-shape rationale; is the main channel identifiable; are the biggest risks and most important open questions listed. Where you cannot answer is where the thinking is not done.
