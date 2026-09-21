# Thinking and Trade-offs

A framework for deriving architecture judgment from requirements, constraints, and quality attributes. Use it at the start of any architecture task: clarifying before design, cross-checking during review, positioning before selection.

## Where functional requirements end and quality attributes begin

Requirements come in two kinds. **Functional requirements** say what the system does: place orders, search, send messages. **Quality attributes** say how well it does it: how fast, how reliable, how cheap, how safe.

Functionality usually has standard answers. Want a shopping cart? Implementations barely differ across companies. Quality attributes are almost pure tradeoffs with no standard answers—that is where architecture judgment actually lives. Under the same features, "instant load + zero loss + a billion users" and "good enough for an internal tool" lead to two completely different architectures.

Functional requirements are usually explicit, written in product documents. Quality attributes are usually implicit; few people volunteer how many users the system must serve or which data must never be lost. So whenever you see "what", immediately ask "how well":

- How many people? A hundred users or a billion?
- How fast is enough? Instant, or is a three-second spinner acceptable?
- How long does data live? Forever, or expires in seven days?
- What happens on failure? Losing a bit of data is fine, or not one record?

The answers to these questions are the actual input to architecture. Looking only at features without quality attributes produces the wrong architecture.

## The judgment loop

Architecture judgment is a loop, not a one-shot pipeline:

requirements → constraints → quality attributes → candidate solutions → tradeoffs → decision

When the business changes or scale changes, constraints and quality targets shift with it; yesterday's optimum may stop being optimal, and the loop restarts. The reason architecture must evolve is that this loop never stops.

## Constraints come before solutions

Constraints are boundaries the design cannot cross. The difference from quality attributes: quality attributes are goals you pursue; constraints are givens.

| Constraint | How it narrows options |
| --- | --- |
| Team size | Architecture complexity cannot exceed what the team can operate. A three-person team running dozens of microservices drowns in ops alone. |
| Time | Ship next week versus a year of runway forces entirely different solutions. Under time pressure, pick what delivers now, not the theoretical optimum. |
| Budget | Determines machines, services, and headcount. An elegant plan you cannot afford is empty talk. |
| Compliance | Red lines like data-residency requirements. Violate and the design is void; no tradeoff space. |
| Existing systems | Most designs do not start from zero; they accommodate the interfaces and temper of what already runs. |
| Third-party dependencies | The capability ceiling and failures of an external gateway or cloud service become your ceiling. |

Constraints are helpers, not obstacles. Without constraints, a design problem has infinite options and nowhere to start; knowing it is a three-person team, three months, must-pass compliance kills most fancy options on the spot. Map the constraints before drawing anything, and you will usually beat the person who starts drawing immediately—faster and steadier.

## The quality-attribute checklist

Given a system, walk this checklist item by item. For each, ask two questions: does it matter to this system, and what is the target? Most items rating low is itself important information—it tells you not to over-engineer.

| Quality attribute | How to measure | Typical levers | Mainly conflicts with |
| --- | --- | --- | --- |
| Performance | Latency (how long one call takes), throughput (how many per second); watch P99, not the average | Caching, read/write splitting, async, CDN, indexes | Cost, consistency, simplicity |
| Availability | Nines; corresponding allowed downtime per year | Redundancy, eliminating SPOFs, fault-domain isolation, graceful degradation | Cost, consistency |
| Scalability | Whether N× load is absorbed smoothly by adding resources | Stateless design, horizontal scaling, replication, sharding | Consistency, simplicity, cost |
| Consistency | Where on the spectrum from strong to eventual | Transactions and coordination protocols (strong); async replication (eventual) | Performance, availability, scalability |
| Security | Attack surface; worst-case loss | Distrust input, least privilege, defense in depth, data classification | Performance, convenience, cost |
| Maintainability | How long a change takes; how fast a newcomer gets productive | Clear boundaries, low coupling, observability, recorded decisions | Extreme performance, short-term delivery speed |
| Cost | Unit cost: per user, per request, per order | The budget, in reverse, caps the targets of other attributes | Conflicts with nearly everything |

Cost deserves its own emphasis: it is the most overlooked attribute and often the real constraint. Redundancy costs money, caching costs money, strong consistency costs money because it is hard to scale. An inefficient design burns a few hundred extra yuan a month at ten thousand users—nobody notices—and millions a month at a hundred million, the same flaw amplified by scale. Strip most architecture arguments to the bottom and the dispute is not whether something is technically possible, but whether the money and people are worth it.

## No silver bullets, only tradeoffs

Almost every choice that makes a system better in one way makes it worse in another:

- Faster usually costs money (more cache, more machines) or consistency (stale reads).
- Stronger consistency usually costs performance and availability (waiting on all nodes).
- Higher scalability usually costs simplicity (distributed complexity).
- Faster shipping usually costs maintainability (technical debt).

From this comes an almost universal touchstone: **if a proposal is described as better in every way with no downsides, the proposal is not perfect—the thinking is unfinished.** Someone who has thought it through can say what the option buys, what it sacrifices, and why the sacrifice is worth it. When evaluating someone else's design or your own, look for its tradeoffs first; if you cannot find any, suspect unfinished thinking before believing in perfection.

## Six anchoring questions

Quality attributes and constraints are mostly implicit; they have to be asked out. These questions fit almost any system, and each anchors a class of decisions:

1. **What scale?** Users and data today, peak load. Decides whether to prepare for scaling.
2. **Read/write ratio?** Read-heavy or write-heavy. Decides which side to optimize, and shapes how data is stored.
3. **Consistency requirements?** Must a just-written value be read back immediately; how long an inconsistency window is tolerable. The classic tradeoff locus.
4. **Growth expectations?** Where will the scale be in a year; steady or spiky. Decides how much scaling headroom to leave.
5. **Cost of failure?** How bad is downtime or data loss. Decides reliability investment.
6. **What constraints?** Team, time, budget, compliance. The boundaries of the option space.

There is no best architecture, only the most fitting one under this set of answers. The same chat feature has wildly different answers for a three-person internal tool and a billion-user product; the difference is not engineer skill but different answers to the six questions. When the answers change, the optimum moves.

## Example: three features grow a quality-target table

Requirement: a URL shortener—long URLs to short codes, click to redirect, maybe click stats.

Only three features, almost no design space. Ask the six questions:

- Scale: mid-sized service, ten million new links per day.
- Read/write ratio: a link is created once and clicked countless times; 100:1 or even 1000:1.
- Consistency: a link becoming reachable a second or two after creation is tolerable.
- Growth: links accumulate forever.
- Failure cost: a broken redirect hurts experience but is not fatal; losing the mapping invalidates every shared link—a disaster.
- Constraints: small team, ship soon, limited budget.

Translate the answers into quality targets:

| Attribute | Target | From which answer |
| --- | --- | --- |
| Read latency | Redirect under 50ms | Lopsided read ratio; redirect is the core experience |
| Read scalability | Absorb massive read traffic | The peak is in reads |
| Durability | Short-link mappings must never be lost | Loss invalidates every shared link |
| Consistency | Eventual is fine | A second or two of delay is tolerable |
| Cost | Storage must stay cheap | Data accumulates forever on a limited budget |

This table is what every later decision leans on. Hash the code (simple, but handle collisions) or a global sequence service (clean, but a new moving part); absorb reads with a cache (fast; the price is stale data—acceptable once eventual consistency is confirmed); store mappings in a key-value store (the access shape is a simple key lookup). Every decision traces back to an answer from the six questions. That is the difference between architecture judgment and "just picked a database".

## Explaining tradeoffs to the business

The ranking of tradeoffs belongs to people who understand the business. Translate technical choices into money, risk, and ship dates—not technical parameters:

- Always attach costs to options, not just conclusions. Lay out what path A and path B each gain, give up, cost, and how long they take, so the business chooses informed.
- Quote in three currencies: money, risk, time. Almost any technical tradeoff converts into these.
- Tie quality attributes to business metrics. Not "four nines of availability" but "at our average order value, an hour down costs roughly this much, so this is what availability is worth".
- Separate the floor from nice-to-haves. Security compliance and money correctness are usually non-negotiable; shaving latency from 200ms to 100ms may be polish. Calling everything equally urgent destroys your credibility.

## Taste: choosing right among defensible options

Frameworks converge to a few candidates that all sound reasonable; choosing among them takes taste. Taste is not mysticism; it has operable facets:

- **Architecture has no standard answer.** Fowler argues to start with a monolith; Tilkov argued on the same site not to start with one; Stack Overflow ran on a monolith plus a few servers serving 200 million requests a day; Netflix runs hundreds of microservices. Both succeeded—the difference is constraints. Hence an iron rule: copying someone's architecture without copying their constraints is a disaster.
- **Simple before familiar.** Simple (unentangled structure) is not the same as easy (quick to pick up). Choosing what you already know often manufactures complexity you pay for later. When you see a design, ask how it could be simpler, not what else could be added.
- **Do not chase trends.** Amazon Prime Video moved its video-quality monitoring from microservices and Serverless back to a monolith and cut cost by about 90% (Prime Video Tech, 2023); Segment merged 140-plus microservices back into a monolith, turning half-day-outage deployments into minutes of work by one engineer (Segment engineering blog "Goodbye Microservices", 2020-07). The lesson is not that microservices are wrong—it is that following the crowd is wrong. When everyone shouts a word, ask only whether it fits the current constraints and whether you can pay the price.
- **Spend innovation sparingly.** Every team holds a limited number of innovation tokens; every immature new technology spends one stepping on pits nobody has mapped. Build the overwhelming bulk of the system with boring, mature, predictable technology; take risks only at genuinely differentiating points.
- **Know the rules before breaking them.** "Do not optimize prematurely" is a good rule, but when the read path is known to melt at launch, leaving a cache seam in advance is a justified exception. The danger is not the exception; it is breaking rules you never understood.
- **Small teams lean toward restraint by default.** Few people, tight deadlines, limited budget, load nowhere near global elasticity: prefer the monolith, boring technology, and an allergy to complexity. Move toward distribution only when constraints actually change—and by then you will know how to move.

Practice feeling the pain of complexity: before adding any component, service, or abstraction layer, answer "does anything die without it?" If nothing dies, do not add it yet.

## Relationship to other documents

- For the full design process, pair with [System design](./06-system-design.md).
- The data-consistency side of quality attributes expands in [Consistency](./09-consistency.md) and [Data and state](./05-data-and-state.md).
- How decisions are recorded is covered in [Architecture decisions](./07-architecture-decisions.md).
- For the general questions of selection scenarios, see [Selection principles](./technology-selection/01-principles.md).
