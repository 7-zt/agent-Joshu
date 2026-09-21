# Views

Choosing views and abstraction levels, and expressing a system's boundaries, relationships, and data flow with diagrams. Use for design communication, review materials, and architecture expression in documents.

## The point of a diagram is alignment

The goal of drawing is not beauty or obligation; it is making everyone see the same system. A system that is clear in one head, undrawn, becomes three slightly different versions in product, backend, and frontend—a common root of project chaos. Diagrams turn individual judgment into shared understanding. That is a core architect job, not an accessory skill.

Drawing is also thinking. When you try to put the system on paper, "which of these calls which" and "where exactly is this boundary" surface on their own. Where the diagram will not draw is usually where the thinking is unfinished.

## Four diseases of bad diagrams

- **No boundaries.** Boxes laid flat with no distinction of which share a process, a machine, a trust domain.
- **Arrows without direction or meaning.** A line is just a line; you cannot tell whether A calls B or B calls A, or whether the line carries calls, data, or events.
- **Mixed abstraction levels.** The whole payment system and one utility function on the same sheet; readers cannot tell what granularity to think in. The most hidden and most fatal disease.
- **Too many boxes.** Forty squares crammed into one page; readers give up.

## C4: layers as zoom levels

The C4 model splits diagrams into four zoom levels, like a map app zooming in:

| Level | What you draw | Audience |
| --- | --- | --- |
| Context | The whole system as one box, surrounded by user roles and external systems | Everyone, including non-technical roles |
| Container | The independently runnable, independently deployable chunks inside the system and their communication | Technical teams, architects, ops |
| Component | The module composition inside one container | Engineers working on it |
| Code | Classes and functions | Almost never drawn; leave it to the IDE |

Container does not mean Docker. It means a unit that starts and deploys on its own: a frontend app, a backend service, a database, a cache. The test is "is this an independently runnable process or store".

The first two levels carry the daily value. Context aligns the system's relationship with the outside world—it should contain no technical nouns at all and be readable by non-technical people. Container maps directly onto deployment and ops units and is where architectural judgment is densest: how many services to split, how data divides, whether to add a cache—all visible on this sheet.

The Code level is usually skipped. The code itself and the IDE's generated relationship views are the most accurate Code view; a hand-drawn one is stale the moment code changes. Do not hand-maintain documents destined to rot; spend the effort on the relatively stable levels that need communicating.

## Beyond static structure: pick the view that answers the question

C4 expresses static structure; it cannot answer every question. Choose by question:

| Question | View | Minimal example |
| --- | --- | --- |
| Structure: what exists, what connects to what | C4 Context/Container | Frontend → gateway → order service → inventory service |
| Timing: how one request or a Saga flows, failure branches included | Sequence diagram | Checkout happy path plus the compensation branch when stock is short |
| Data: how facts flow to read models, how stale they get | Data-flow diagram | Primary store → CDC → read model (about 1 minute behind) |
| Runtime: nodes, regions, failure domains, deployment topology | Deployment diagram | Two regions each running a full stack, primary-standby async replication |

A common misuse is answering timing or data-flow questions with a Container diagram—a structure sheet shows who connects to whom, not who times out first or how compensation runs when something fails. In reviews, match the view to the question type; do not compete on drawing everything.

## Three basic elements

- **Box.** A thing with a responsibility; it can answer "what are you for". All boxes in one sheet should share a scale.
- **Arrow.** A relationship; it must have a direction (who initiates) and a meaning (call, data, event). Lines without direction or meaning are the number-one source of bad diagrams.
- **Boundary.** A dividing line enclosing what belongs together. It may be a deployment boundary (same cluster), a trust boundary (inside trusted; outside input not trusted), or a system boundary (what is ours).

Newcomers most often skip boundaries, yet boundaries carry the most architectural thinking. Any data entering the system from outside is untrusted; on the diagram that is a trust boundary separating the system from external input. Where the boundary sits is often where security and deployment decisions live.

## Rules that improve a diagram immediately

1. **One abstraction level per sheet.** All big chunks or all modules; no mixing.
2. **Label arrows with direction and meaning.** An unlabeled line is an unexamined dependency.
3. **Keep boxes to 7±2.** Beyond nine boxes, abstract up a level or split into two sheets.
4. **Top-down.** Draw the Context first to confirm alignment on the system and its surroundings, then descend into Container. Diving into component detail first is seeing trees and missing the forest.
5. **Draw for the reader.** A Context for an executive contains no jargon; a Container for engineers does not omit key data flows for tidiness.

## ASCII diagram practice

Plain-text diagrams render anywhere, drop straight into Markdown and code comments, and diff like text—unglamorous but practical:

- Enclose boxes with `┌ ┐ └ ┘ ─ │`; mark direction with `──▶`, `◀──`; distinguish boundaries with dashed frames against solid concrete things.
- Write a few words beside the arrow saying what the line does: `A ──calls API──▶ B`.
- Sketch the layout on a draft before inking. ASCII diagrams are awkward to edit; think first, draw second.
- Align boxes at the same level horizontally; leave vertical whitespace. Crammed ASCII readability falls off a cliff.
- Do not chase pixel perfection. The goal is making structure and relationships clear, not producing art.

## Relationship to other documents

- When analyzing existing systems, use the four-step method of [System analysis](./02-system-analysis.md): read diagrams first, then redraw.
- When designing new systems, diagrams serve the derivation in [System design](./06-system-design.md); the Context-then-Container order matches.
- Where boundaries are trust boundaries, the topic expands in [Security and tenancy](./14-security-and-tenancy.md).
