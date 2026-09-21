# Imperative / Procedural Programming

## What it is

Imperative programming describes a computation as a sequence of statements that change state: read input, mutate a variable, call an external system, handle an error, write output. Procedural programming is the same model organized into procedures (functions) that are called in order. This is the oldest and most direct way to express a program, and it maps closely to how the machine actually executes.

It is easy to dismiss imperative code as low-level or unsophisticated. That is a mistake. The real world is full of ordered side effects, open a file, read it, transform the contents, write it back, commit the transaction, and imperative style is the honest, readable way to express that sequence. The goal is not to eliminate imperative code but to keep it where it belongs and to stop business rules from getting tangled up in it.

## The assumption underneath

- Some logic is inherently sequential: each step depends on the effect of the previous one.
- Side effects should be _visible_, laid out in order, not hidden behind layers of abstraction.
- For short scripts, entry points, and wiring layers, a direct linear flow is usually more maintainable than premature architecture.

## When it fits

- CLI entry points, one-off scripts, migrations, operational tooling.
- Application startup: dependency wiring, config loading, logger initialization.
- I/O orchestration: coordinating a transaction, calling several external systems in a required order, sequencing reads and writes.
- The outer layer of almost any program; the part that has to actually _do_ things in the world.

A healthy imperative entry point reads like a recipe; each step names a phase, and the side effects are visible in order:

```python
def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config(args.config_path)
    configure_logging(config.log_level)
    client = build_client(config)
    try:
        result = run_job(client, config)  # decision logic lives here, takes plain data
    except JobError as exc:
        logging.getLogger(__name__).error("job failed: %s", exc)
        return 1
    write_report(result, args.output)
    return 0
```

Notice what the entry point does _not_ do: it does not compute the result itself. It sequences I/O and delegates the actual decision to `run_job`, which can be tested without a real client.

## When it becomes a problem

- Core business rules and I/O are interleaved in one long function, so you cannot test the rule without a database, a clock, or a network.
- Complex state changes have no boundary and leak through every layer via globals or a mutable dict passed everywhere.
- Error handling is scattered through the flow, impossible to reuse or reason about as a unit.
- The function has grown past what a reader can hold in their head, and the only structure is top-to-bottom order.
- "Just one more flag" parameters accumulate until the procedure has a dozen booleans steering hidden branches; a sign distinct operations have been merged into one sequence.

When you see these signs, the issue is usually not "too imperative" but "imperative in the wrong place": decision logic that should have been pulled out into something testable. The fix is rarely to make the code less imperative overall; it is to separate the part that _decides_ from the part that _acts_.

Consider a function that interleaves the two:

```python
def process(order_id: int) -> None:
    row = db.fetch_order(order_id)          # I/O
    if row.status == "paid" and row.total > 100:   # decision
        discount = row.total * 0.1          # decision
        db.apply_discount(order_id, discount)   # I/O
        mailer.send(row.email, "discount applied")  # I/O
```

The rule (paid orders over 100 get 10% off) cannot be tested without a database and a mailer. Pull the decision out, and it becomes a pure function you can test with a plain value, while the imperative shell keeps only the I/O:

```python
def compute_discount(order: Order) -> Decimal:   # pure, trivially testable
    if order.status == "paid" and order.total > 100:
        return order.total * Decimal("0.1")
    return Decimal(0)

def process(order_id: int) -> None:              # thin imperative shell
    order = db.fetch_order(order_id)
    discount = compute_discount(order)
    if discount:
        db.apply_discount(order_id, discount)
        mailer.send(order.email, "discount applied")
```

## Procedural decomposition

Procedural style is not just "one long function." Its discipline is decomposing a flow into named procedures, each at a single level of abstraction. A good procedure reads as a sequence of calls whose names tell the story; you can understand the flow without descending into any of them. When you find yourself adding a comment to label a block (`# now validate the records`), that block usually wants to become a named function (`validate_records(...)`) instead. The comment rots; the function name is checked by the reader every time.

Keep each procedure at one level of abstraction. Mixing high-level orchestration (`run_job`) with low-level byte-twiddling in the same function forces the reader to constantly shift altitude. Push the details down into their own procedures and let the caller stay a readable summary.

## Relationship to functional core / imperative shell

The cleanest resolution is to keep imperative style but confine it to a thin outer layer. This is the imperative shell of [functional-core.md](./functional-core.md): the shell sequences I/O, transactions, retries, and logging; the core takes plain data, applies the rules, and returns plain data. The shell stays imperative on purpose; that is where ordered side effects live. What you move out is the decision-making, not the orchestration.

This also connects to [data-oriented.md](./data-oriented.md) (the data the shell passes to the core) and [resource-lifecycle.md](./resource-lifecycle.md) (how the shell acquires and releases the resources it sequences).
