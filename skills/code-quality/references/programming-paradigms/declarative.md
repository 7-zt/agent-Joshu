# Declarative Programming

## What it is

Declarative programming describes _what_ you want, the goal, the constraint, the shape of the data, and leaves the _how_ to a framework, library, or engine. Instead of writing the steps, you write a description and let something else execute it. SQL is the canonical example: you state the result set you want and the query planner decides how to produce it. Configuration files, schemas, routing tables, CLI argument definitions, validation rules, and rule engines are all declarative.

In a Python project, declarative style shows up far more than people notice: `pyproject.toml`, a `dataclass` field list, a `TypedDict`, an `argparse` parser, a web framework's route decorators, a permission table, a state machine's transition table. Each of these is data that some engine interprets, not code you step through.

## The assumption underneath

- Some structures are easier to check, compose, and document as _data_ than as imperative code.
- A framework or library can own the repetitive execution logic, so your code only expresses what differs from the default.
- When the rules are stable and the execution model is well understood, declaring them removes boilerplate and centralizes the source of truth.

## When it fits

- Project and tooling configuration: `pyproject.toml`, Ruff, pytest, pre-commit.
- Schema and type definitions: `dataclass` fields, `TypedDict`, Pydantic / FastAPI models, serialization metadata.
- Structural definitions the framework executes: CLI arguments, web routes, permission tables, mapping tables, transition tables.
- Queries and transformations: SQL, query builders, declarative data mappings.

The common thread: a stable structure, a well-defined execution engine, and a benefit from having a single inspectable source of truth.

A small example of the imperative-to-declarative shift. Imperative dispatch:

```python
def handle(event: str) -> None:
    if event == "submit":
        do_submit()
    elif event == "pay":
        do_pay()
    elif event == "cancel":
        do_cancel()
    else:
        raise ValueError(event)
```

Declarative dispatch; the mapping _is_ the logic, and a tiny engine applies it:

```python
HANDLERS: dict[str, Callable[[], None]] = {
    "submit": do_submit,
    "pay": do_pay,
    "cancel": do_cancel,
}

def handle(event: str) -> None:
    try:
        HANDLERS[event]()
    except KeyError:
        raise ValueError(event) from None
```

The declarative form makes the full set of cases visible in one place, is trivial to extend, and can be inspected, counted, and tested as data. The cost is that "what runs when" is now one indirection away: which is exactly the tradeoff the next section is about.

## When it becomes a problem

- There is real control flow hidden behind the declaration, but the order of execution and the location of an error are invisible. When a declarative pipeline fails, the stack trace points into framework internals, not your intent.
- Configuration grows until it is effectively a programming language: conditionals, loops, and templating expressed in YAML or TOML, with none of a language's tooling.
- A DSL or extension point is built "for flexibility" but has exactly one call site. That is speculative structure; see [yagni](../design-principles/yagni.md).
- Debugging requires understanding the engine's evaluation model, and that model is poorly documented or surprising.

Declarative style trades explicit control flow for conciseness. That trade is worth it when the engine is trustworthy and the structure is stable, and harmful when you need to see and step through what actually happens.

A practical test: if a newcomer asks "what happens when this runs?" and the honest answer requires explaining the engine's evaluation model before you can answer, the declaration may have absorbed too much logic. Declarations should describe _facts and structure_; the moment they start describing _sequence and decisions_, the imperative form is usually clearer.

## Relationship to other paradigms

- A [state-machine.md](./state-machine.md) transition table is declarative: the legal moves are data, and a small engine applies them.
- Declarative config feeds the imperative shell ([imperative.md](./imperative.md)), which reads it and acts.
- Declarative and data-oriented design overlap heavily: both treat structure as inspectable data rather than behavior. The difference is emphasis: declarative is about handing execution to an engine, data-oriented is about modeling the data itself well.
- "More declarative" is never the goal in itself. The goal is to make rules and data shapes central, inspectable, and documentable. When a declaration stops being readable as a fact and starts hiding a decision, that is the signal to step back toward explicit code.
