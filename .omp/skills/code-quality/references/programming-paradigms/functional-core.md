# Functional Core, Imperative Shell

## What it is

Functional Core, Imperative Shell is an architecture popularized by Gary Bernhardt. It splits a program into two layers with different rules. The _core_ holds pure decision logic: given input data, it computes output data and makes no side effects: no I/O, no clock reads, no randomness, no network, no database, no global mutation. The _shell_ is the thin imperative layer that talks to the outside world: it reads inputs, calls the core to decide what should happen, then performs the side effects the core asked for.

The insight is that what makes code hard to test and hard to reason about is almost never the arithmetic or the branching; it is the dependence on the environment. A function that decides _whether_ an order can ship is easy to test; a function that decides and also charges a card, writes a row, and sends an email is not. Push the environment to the edge and the interesting logic becomes pure, total, and trivially testable.

This is not an official Python concept, but it composes naturally with Python's multi-paradigm style and with the entry-point boundary discipline described in [imperative.md](./imperative.md).

## The assumption underneath

- The expensive-to-test part of a system is its side effects and environment coupling, not its calculations.
- Once side effects are pushed to the boundary, the core can be tested with plain data in, plain data out: no mocks, no fixtures, no patching the clock.
- The shell still needs real design effort, because transactions, retries, error handling, logging, and resource lifecycle all live there.

## Benefits

- **Testability.** Core tests are example-based: pass data, assert on returned data. No I/O setup, no mock framework, fast and deterministic. This is the single largest payoff.
- **Reasoning.** A pure function's behavior is fully determined by its arguments. You can understand it in isolation without tracing what global state or external service it touches.
- **Composability.** Pure functions compose cleanly: the output of one feeds the next without hidden ordering constraints. The shell sequences the impure steps once, explicitly.

## When to apply

Apply it wherever the interesting decision is separable from the act of carrying it out:

- Domain rules: pricing, eligibility, permission checks, state transitions (see [state-machine.md](./state-machine.md), where a `(state, event) -> new_state` reducer is a textbook functional core).
- Validation and normalization of input before it touches persistence.
- Data transformation pipelines where the transform rules are pure and only the read/write ends are impure.
- CLI and request handlers: the shell parses arguments or HTTP, assembles dependencies, and calls a pure planner; the core returns a decision or a description of work to do.

A useful shape is for the core to return a _description_ of side effects (a list of commands, an event, a typed result) and let the shell execute them. The core decides; the shell acts.

```python
# core: pure, no I/O; trivial to test with data in, data out
def plan_discount(cart: Cart, customer: Customer) -> DiscountPlan:
    if customer.tier == "gold" and cart.total > 100:
        return DiscountPlan(percent=15, reason="gold-large-order")
    return DiscountPlan(percent=0, reason="none")


# shell: imperative, owns I/O, transactions, logging
def apply_discount(cart_id: str, customer_id: str) -> None:
    cart = repo.load_cart(cart_id)          # I/O
    customer = repo.load_customer(customer_id)  # I/O
    plan = plan_discount(cart, customer)    # pure decision
    repo.save_discount(cart_id, plan)       # I/O
    logger.info("applied %s", plan.reason)  # I/O
```

The test for `plan_discount` constructs a `Cart` and `Customer`, calls the function, and asserts on the returned `DiscountPlan`: no database, no mocks, no patched clock. Every branch of the discount rule is reachable with a one-line setup. The shell, by contrast, is tested with a few integration tests or is thin enough to verify by reading.

## When strict purity is counterproductive

- **I/O-heavy glue code.** Code whose entire job is to move bytes between two systems has almost no pure decision to extract. Forcing a functional core onto it produces a hollow core and a fat shell that hides the real complexity.
- **Simple CRUD.** When the operation is "read row, update field, write row," there is no meaningful decision to isolate. A direct imperative function is clearer than an artificial split.
- **Copy-cost-heavy data.** Strict purity forbids mutation, so a naive core may copy large structures repeatedly. When that cost dominates, allow local mutation inside an otherwise-pure function, or relax purity at that seam.
- **Anemic cores.** If the split leaves you with a maze of tiny pure functions that no longer speak the domain language, you have traded clarity for dogma. Keep the core expressed in domain terms.

The failure mode to watch is a shell so thin that transactions, error handling, and observability have nowhere to live and leak back into framework callbacks. The shell is a real layer, not a wrapper.

## Where the boundary goes

Drawing the line well is the whole skill. The seam belongs exactly where a decision is made on the basis of data already in hand. Read everything the decision needs _first_, decide in the core, then act on the decision; do not interleave reads and decisions, because every read pulled into the middle of the logic drags the environment back into the core.

A common refinement is to make the core return data that _describes_ the effects rather than a bare value:

```python
# core returns a description of what should happen: still pure
def plan_effects(order: Order, now: datetime) -> list[Effect]:
    if order.is_overdue(now):
        return [ChargeLateFee(order.id), NotifyCustomer(order.id, "overdue")]
    return []


# shell interprets the descriptions: the only place effects actually fire
def process(order_id: str) -> None:
    order = repo.load(order_id)
    for effect in plan_effects(order, datetime.now(tz=UTC)):
        execute(effect)
```

Now even the _choice_ of which effects to perform is testable without performing any of them: assert on the returned list. The shell shrinks to a dumb interpreter, and the interesting branching is all in the core. This is the same shape a [state-machine.md](./state-machine.md) reducer takes when it returns `(next_state, actions)`.

The clock, `datetime.now(tz=UTC)`, is read in the shell and passed _into_ the core as `now`. That single move is what keeps time-dependent rules pure and deterministic to test.

## Interaction with other paradigms

- Builds directly on [imperative.md](./imperative.md): the shell _is_ the imperative orchestration layer, kept thin on purpose.
- The pure core is where [data-oriented.md](./data-oriented.md) thinking pays off: plain data in, plain data out.
- For lifecycle logic, a pure reducer in the core plus an effect-executing shell is the cleanest way to build a [state-machine.md](./state-machine.md).
