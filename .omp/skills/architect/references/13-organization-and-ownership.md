# Organization and Ownership

Using Conway's Law to explain how system shape relates to organization structure, guiding team division, service ownership, and the organizational judgment in splitting. Use when designing team structure, explaining "coupling that will not untangle", or deciding where service boundaries belong.

## Conway's Law: the system is the organization's print

Melvin Conway's 1968 observation: any organization designing a system will produce a design whose structure copies the organization's communication structure. Conway's own example: assign four groups to write a compiler and you get a four-pass compiler—the boundaries between groups naturally become compiler phase boundaries.

The mechanism is too plain to refute: for two modules to cooperate, the people designing them must communicate; that interface in the code is the fossilized communication in the system. When communication is cheap (same team, same room, same person), interfaces turn vague, casual, tightly coupled—always able to change and ask, no motive to define clean boundaries. When communication is expensive (cross-team, cross-department, cross-timezone), interfaces turn narrow, stable, loosely coupled—alignment costs so much that both sides are forced to settle once. The hardness of an interface is inversely proportional to the communication convenience of the two groups behind it.

**Direct use in architectural judgment**: when two modules cannot be cleanly decoupled no matter how you refactor, stop refactoring and check whether the two groups behind them are inherently inseparable (same person, same team, KPIs tied together). Many architectural problems disguised as technical ones are rooted in the organization; changing the organization cures what changing code cannot. Conversely, a service boundary you intend to defend, if the two sides are the same people sitting together with tied performance reviews, will sooner or later be stabbed through casually—the organization never backed it.

## The inverse Conway maneuver

Since the system will mirror the organization anyway, reverse it: design the team boundaries into the architecture shape you want, and let the organization force the architecture out.

Organizational boundaries are harder than code boundaries. A boundary drawn in code is pierced by one `import`; a boundary drawn in the organization (different teams, different owners, different release cadences) forces the code to grow the corresponding interfaces on its own.

The most common death: teams split by technical function (frontend team / backend team / DBA team) while expecting services cut along business verticals to emerge. Functional boundaries ≠ architecture boundaries; the result is a distributed monolith—one feature needs three teams to ship, services split but still releasing together. Want a vertically sliced architecture? First build vertically sliced teams.

## Cognitive load: the real basis for splitting

The system complexity one team can hold in its head has a hard ceiling (the core contribution of Skelton & Pais, _Team Topologies_, 2019, https://teamtopologies.com/key-concepts). Past the ceiling, the team degrades from proactive design to firefighting: nobody can explain the whole, and every one-line change is made trembling.

Cognitive load is not lines of code; it is the total of things that must be understood simultaneously and might need changing at any moment, in three kinds: intrinsic load (business-domain complexity—cannot be reduced), extraneous load (accidental complexity: homegrown CI, wrestling Kubernetes, assembling environments—what a platform should carry away for you), and switching load (writing payments in one hour, fixing search the next, context bouncing repeatedly—the price of badly cut boundaries). When the bucket is full, anything more spills over—that is the signal to split teams or services.

Team Topologies' four team types are, in essence, four organizational roles cut by cognitive load:

| Type | What it carries | In one sentence |
| --- | --- | --- |
| Stream-aligned | One end-to-end business value stream | The absolute main force: requirement to production, accountable to users directly |
| Platform | General accidental complexity | Self-service platforms so stream teams need not each chew through K8s/CI |
| Enabling | Temporary capability gaps | A touring coach: short-term embed to transfer skills then withdraw; not resident, not taking over |
| Complicated-subsystem | Hard problems needing deep specialization | Search ranking, video encoding, risk models—encapsulating that load for others |

The soul is the stream-aligned team as protagonist, the other three existing to unburden it. Ask first which team's cognitive load is about to overflow, then decide what to split—not eyeballing the technical map. The three interaction modes between teams (collaboration, X-as-a-Service, facilitating) are chosen by the nature of the work, not fixed defaults: exploring an unsettled new capability fits collaboration (side by side, fast convergence, but prone to adhesion—keep it short); mature capabilities fit X-as-a-Service (self-service, lowest communication cost—and not limited to network services: it can be a platform product, documented API, or library); missing skills fit facilitating (coach embeds then withdraws). Governing team interaction modes is designing the future's system interfaces.

## Microservices are an organizational scaling device first

The core problem microservices solve is not running faster but letting many teams work in parallel without blocking each other. Performance-wise, a monolith plus machines is often faster and cheaper. What microservices buy is team autonomy from deployment decoupling: each releases on its own, each runs its own on-call, and doubling the team count doubles the parallelism.

The price is voluntarily swallowing the whole mountain of distributed complexity (partial failure, eventual consistency, sharply higher observability demands). The trade pays only when its benefits exceed that complexity. With three to five people on one release line, splitting services solely for team autonomy is usually a loss: you pay the distributed-systems cost and gain little autonomy. The team-autonomy benefit of microservices grows with team count, so it is limited when few teams are involved. A module may still be worth extracting when it genuinely needs independent scaling, release cadence, or fault isolation.

## Scaling the big organization: small teams + stable contracts

Two-pizza teams (an Amazon principle, roughly 6–10 people): as a team grows, internal communication's O(n²) link count explodes and alignment alone eats the brain capacity. Small team = controllable internal communication = genuine autonomy.

Interfaces are contracts not to be broken casually (Bezos's 2002 API mandate): all teams communicate only through each other's public service interfaces; back doors like direct database connections and shared memory are forbidden. With contracts stable and taken seriously, team A can rewrite its internals without notifying team B—the contract buys freedom. API governance (versioning, backward compatibility, contract tests, deprecation process) is not bureaucracy; it is the foundation that makes autonomy possible. Once contracts rot, every team is forced into daily alignment, and microservices degrade back into a distributed monolith.

## Build or buy

The ruler: is this capability your differentiating core? If core (recommendation algorithms, search ranking): build it and staff a team—the cognitive load is worth it. If not (sending email, taking payments, monitoring): buy / use open source / outsource, and hold it outside the organizational boundary with a stable contract; do not couple deeply.

The cost of misjudging: outsourcing your differentiating core hands your lifeline to someone else; building every non-core in-house drowns the team's brain capacity in accidental complexity. When to split out a new team: when the cognitive load of some **core** capability exceeds the current team's bucket—not splitting on a whim, but when the bucket overflows.

## How AI rewrites the organizational judgment

Conway's Law has not expired, but two variables changed. AI agents are becoming virtual members of the team topology (reading legacy code, tending platforms, filling skill gaps). More notably, cognitive load may be shared with AI, enlarging the bucket's effective capacity: a small team plus AI might maintain systems that previously demanded a large team. **Note this is an unverified trend judgment, not an established law**: AI may equally add new cognitive load (reviewing AI output, understanding model behavior, new security and runtime concerns), and the net effect must be judged by the project's own evidence. If it does hold, the organizational rationale for splitting services weakens—do not split early to spread cognitive load; first see whether AI can enlarge the bucket, and the monolith can stay bigger longer.

A new question: where to cut the boundary between humans and AI. Which judgments must stay human (whether a boundary should exist, how much inconsistency to tolerate, correctness or uptime when things break), and which implementation goes to agents. The human–AI division line is becoming an architectural boundary as important as service boundaries. Systems will now grow to resemble the communication structure of a "human + AI collaborating organization".

## Cautionary tales

The Spotify model (squads/tribes/chapters/guilds) was deified and then debunked by its own people: Spotify insiders admitted it was largely aspiration rather than reality, never fully implemented. Copying the vocabulary without the underlying autonomy-and-trust culture gets old wine in new bottles. An organizational model is not a copyable structure; it is a communication style grown in a particular cultural soil—copy the shell, and the soul does not come along.

## Relationship to other documents

- The technical routes of splitting (modular monolith first, strangler) are in [Evolution and migration](./12-evolution-and-migration.md).
- Signals for when to split and how decisions are recorded are in [Architecture decisions](./07-architecture-decisions.md).
- The concrete costs of distributed complexity are in [Distributed systems](./08-distributed-systems.md).
