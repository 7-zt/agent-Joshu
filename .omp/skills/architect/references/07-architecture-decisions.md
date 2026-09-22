# Architecture Decisions

How to record candidates, tradeoffs, consequences, and re-review conditions. Use after making an important architecture decision, and when judging whether an existing decision still holds.

## What gets lost first is always the why

Code and architecture diagrams tell you what the system is: which modules, which calls, how data flows. All of that is readable from the system itself at any time. But why it was chosen this way, what was given up at the time, what was being traded for what—code cannot say. It lives only in the head of whoever decided.

Reasons explained in meetings evaporate after three meetings, two departures, and one year. When needed later, what remains is an inexplicable-looking design and a group of people afraid to touch it. A successor facing a system with no "why" has only two mistakes to choose between: dare not touch it (not knowing whether touching it breaks something—the system ossifies), or touch it blindly (delete the seemingly redundant dual-write; three weeks later production explodes, because there was a regulatory requirement back then to write to immutable storage).

Hence a principle: **good documentation does not repeat what the code does, because the code says that itself; good documentation explains why the code is this way, because the code never will.** Spend the effort of recording on what, once lost, can never be recovered.

## What to record

One architecture decision record answers six things:

| Column | What goes in | What its absence costs |
| --- | --- | --- |
| Title | One sentence saying what the decision is | Enables retrieval |
| Status | Draft / accepted / deprecated / superseded | Tells readers whether it still counts |
| Context | What problem and constraints were faced then | What successors lack most is the situation at the time |
| Decision | What was finally decided | Visible in code too, but writing it down completes the record |
| Alternatives | What else was considered and why it lost | Recording what was given up is the value records uniquely hold |
| Tradeoffs and consequences | Benefits, costs, known debt | Lets successors inherit the deliberate tradeoff with eyes open |

Three disciplines:

- **One decision per record, keep it light.** Only a few minutes' read gets read.
- **Append, never rewrite.** When a decision changes, write a new record and mark the old one superseded. How the team used to think and why it changed is itself valuable information—preserve history, do not erase it.
- **Keep it with the code.** Versioned with the code, searchable, reviewable—not rotting in a wiki corner.

**Follow the project's existing recording convention.** Different projects already have their own decision-record mechanisms; this Skill covers the recording method, not a new format. Map the six fields above to the project's existing record type, status vocabulary, and ownership fields rather than introducing a parallel format.

## Bookkeeping technical debt

Technical debt borrows from finance: to obtain value faster now, deliberately choosing an expedient that must be repaid later. Borrowing is not the sin; the sin is not knowing you borrowed, or never planning to repay.

Two kinds of debt:

- **Conscious debt (healthy).** "Ship the simplest version to make the release; it is recorded, and we refactor next quarter." A rational business tradeoff, written as a decision record with repayment scheduled.
- **Unconscious debt (dangerous).** "I don't know why it is written this way; it runs." That is loss of control—debt accrued unknowingly, with zero preparation for the day it detonates.

MVP debt taken deliberately is often correct: the first version of a shortener trading single-store, single-machine code generation for fast validation is a good deal. The error is not knowing the debt exists, not recording it, and only ever borrowing. Three repayment disciplines: borrow consciously (state explicitly that this is an expedient); write it down (one debt is one decision record, context explaining why it is temporary for now); schedule repayment (fix a trigger "repay when X happens" rather than "when we have time").

## When to re-review a decision

Whether the architecture should move is decided neither by feeling ("this code looks ugly" is not a reason; ugliness that harms no quality attribute can be tolerated) nor by fashion (other people's bottlenecks are not yours; copying a big company's maturity-stage architecture onto your growth-stage system is the number-one over-engineering). Measure with two rulers:

1. **Bottleneck.** Is some quality attribute now genuinely capped by the architecture: the database smoking from reads that no cache can suppress; one module's changes always dragging a whole area, releases slowing down. Only real, measured bottlenecks are upgrade signals.
2. **Changed quality targets.** The business's "how well" requirement stepped up: availability from 99% to 99.99%; user volume entering the next order of magnitude.

Upgrade not because the architecture is old or ugly, but because a quality attribute you truly care about is capped by the current architecture and the cap has been measured. Every upgrade is itself a major decision to record: context writes which bottleneck forced the move; decision writes what it was upgraded to; alternatives write what else could have absorbed the pressure; tradeoffs write what was paid.

## Relationship to other documents

- The derivation behind decisions is in [Thinking and tradeoffs](./01-thinking-and-tradeoffs.md) and step ⑧ of [System design](./06-system-design.md).
- Execution patterns for upgrades and migrations are in [Evolution and migration](./12-evolution-and-migration.md); its trigger signals share the same source as this page's re-review rulers.
- How organizational constraints shape decisions is in [Organization and ownership](./13-organization-and-ownership.md).
- The decision frame for selection scenarios is in [Selection principles](./technology-selection/01-principles.md).
