# Data-Oriented Design

## What it is

Data-oriented design starts from the data, not from the behavior. Instead of asking "what objects exist and what can they do," it asks "what is the shape of the data, how does it flow through the system, and what transformations does it undergo." The structures you reach for are plain: schemas, tables, records, typed dicts, dataclasses used as data and nothing more. Behavior lives in functions that take data in and return data out, rather than in methods bound to the data.

In its origin (game engines, high-performance systems) the term carries strong claims about memory layout and cache locality. In ordinary application code the more useful sense is broader and quieter: model the data explicitly and let its shape drive the structure of the program. Most ETL jobs, API boundaries, configuration systems, and batch processors are fundamentally data pipelines, and they are clearest when written that way.

## The assumption underneath

- The data has a shape, and that shape is the most stable thing about the program: endpoints, rules, and UIs change more often than the core record.
- Separating data (inert structures) from behavior (functions over them) makes both easier to inspect, serialize, version, and test.
- For pipeline-shaped problems, "what transformations does this data pass through" is a more honest decomposition than "what objects collaborate."

## When appropriate

- **ETL and data pipelines.** Records flow through parse, validate, transform, aggregate, and write stages. Each stage is a function from data to data; this is data-oriented design and [functional-core.md](./functional-core.md) describing the same system from two angles.
- **API boundaries.** Request and response bodies are data. Model them as schemas (dataclass, TypedDict, Pydantic) with a single source of truth, and keep handler logic as transformations over that data.
- **Configuration.** Config is declarative data (see [declarative.md](./declarative.md)); parse it into a typed structure at the boundary, then pass that structure inward.
- **Batch processing.** Per-record rules are pure functions over plain records; the surrounding loop, checkpointing, and I/O are the imperative shell.

## Relationship to functional style

Data-oriented design and functional programming are close allies. Functional style says "prefer pure functions over data"; data-oriented design says "make the data explicit and let it lead." Together they produce the same architecture: immutable-ish records flowing through pure transformations, with side effects pushed to the edge. The difference is emphasis, one starts from functions, the other from the shape of the records, and in practice they converge.

## When objects with behavior are better

The data-oriented stance weakens precisely when the data has invariants that must hold at all times. Plain records are inert: nothing stops a caller from putting them into an illegal combination. When a concept has rules about which field combinations are valid, a lifecycle, or behavior that must stay consistent with its state, an object that encapsulates that state and guards its invariants is the better model; see [object-oriented.md](./object-oriented.md).

Signs you have pushed plain data too far:

- Validation logic for the same record is copy-pasted across every function that touches it, because no single place owns the invariant.
- Callers can construct combinations of fields that should be impossible (the [state-machine.md](./state-machine.md) "boolean flag soup" smell).
- The "data" is starting to grow behavior that several functions need to share and keep consistent.

At that point, encapsulate. Plain data is for records whose validity is a property of the boundary that produced them; objects are for concepts whose validity must be maintained continuously.

## A concrete shape

A data-oriented pipeline reads as a sequence of transformations over explicit records, with each stage a pure function from data to data:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class RawRow:
    name: str
    amount: str


@dataclass(frozen=True)
class Charge:
    name: str
    cents: int


def parse(row: RawRow) -> Charge:
    return Charge(name=row.name.strip(), cents=round(float(row.amount) * 100))


def charges(rows: list[RawRow]) -> list[Charge]:
    return [parse(r) for r in rows]
```

The records carry no behavior; the functions carry no state. Reading, writing, and checkpointing happen in the surrounding imperative shell, not in these functions. That separation is what makes each stage testable with literal data and composable into a longer pipeline.

## Make illegal data hard to represent

A quieter benefit of taking the data seriously is that a well-chosen shape removes whole classes of bugs before any logic runs. If a field can only be one of three values, model it as an enum, not a free string. If two fields must appear together or not at all, put them in a nested record rather than two independent optionals. If a list must be non-empty, that is worth encoding or checking once at the boundary. The discipline is to push validity into the shape of the data so that downstream functions can trust their inputs instead of re-checking them. This is the same instinct as a [state-machine.md](./state-machine.md) refusing to let boolean flags encode states; the type is the first line of defense.

The boundary is where this work happens. Parse untrusted input (JSON, config, request bodies) into a typed structure once, validating as you go, and let everything inward operate on the trusted shape. This is "parse, don't validate": convert raw data into a structure whose existence guarantees its validity, rather than passing raw data around with validation checks sprinkled everywhere.
