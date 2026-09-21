# State Machine / Finite-State Model

A state machine models a process as a finite set of named states, a set of events, and the rules governing movement between them. It answers concrete questions: which states can the system be in, which events does it accept, which transitions are legal, how are illegal transitions rejected, and which side effects run during a transition. This model is useful because many everyday bugs are illegal-state bugs.

It is not a synonym for the GoF State pattern. That pattern is one _object-oriented implementation_ of a state machine. The model is broader and can be expressed as a transition table, an `Enum` plus dispatch, a `match` statement, a pure reducer function, or state objects.

## Concept

A state machine captures a workflow as data: the modes a thing can occupy, the triggers that move it, and the policy for everything that is not allowed. Making the legal moves explicit turns "we forgot to handle the case where a cancelled order gets paid" from a latent production bug into a single missing table entry you can see and review.

## Core Model

- **State**: a named, mutually exclusive mode the system occupies (`draft`, `submitted`, `paid`). At any moment it is in exactly one.
- **Event**: a named trigger that may cause a transition (`submit`, `pay`, `cancel`). Events are facts or commands arriving from outside the machine.
- **Transition**: a legal movement from one state to another in response to an event: `(state, event) -> next_state`.
- **Guard**: a precondition on a transition. Even if a transition exists, the guard can block it: sufficient balance, valid permission, resource still present.
- **Action**: a side effect performed when a transition is taken: write the database, send a message, emit an event, record an audit entry.
- **Invalid transition handling**: the explicit policy for an event the current state does not accept: raise, reject, or no-op. This is a decision, never an unhandled branch that silently does nothing.

## When Appropriate

- The states are finite and can be named, and the events are finite and can be named.
- Invalid transitions matter: moving from `cancelled` to `shipped` must be impossible, not merely unlikely.
- Lifecycle correctness is part of the domain: orders, approvals, subscriptions, protocol/connection state, job and worker lifecycles.
- You need to audit _why_ `A -> B` is allowed and `A -> C` is not, often for compliance.
- The process interacts with persistence, retry, or concurrency, where a precise notion of "current state" prevents corruption.

## When Not Appropriate

- A simple linear flow with no branching and no notion of an illegal step.
- Tiny, obvious branching where a boolean field or a single `if` already reads clearly.
- No real concept of an invalid state: any value can follow any other without harm.
- Pre-building a class per state for a two-state problem; that is class explosion, not modeling.

## Typical Implementations

- **Enum + transition table**: a `dict[(State, Event), State]`. The clearest default when rules are stable. Reviewable at a glance, trivially testable.
- **Pure reducer**: a function `(state, event) -> new_state` with no side effects, so the imperative shell performs actions. Pairs naturally with [functional-core.md](./functional-core.md).
- **`match`/`case`**: good for local, structured transitions with modest branching. It is a syntax for expressing transitions, not the state machine itself.
- **Dispatch map**: `dict[Event, Callable]` when each event carries distinct handling logic.
- **State objects (GoF State)**: when each state genuinely has substantial differentiated behavior (connection states, editor modes, protocol phases).
- **Library / workflow engine**: when you need persistence, visualization, or dynamic configuration and have a real need for it, not speculation.

## State Design

- States must be **mutually exclusive**. If two can be true at once, they are not states of one machine; they are two machines or two dimensions.
- Name states in **domain terms** (`awaiting_payment`), not implementation terms (`flag2_set`).
- **Avoid boolean combinations** as implicit state. `is_active`, `is_locked`, `has_failed`, `is_retrying` as four independent booleans encode 16 combinations, most of them illegal and none of them defined. Collapse them into one named state enum.
- Model **events as verbs or facts** (`pay`, `OrderPaid`), distinct from states. Confusing the two ("the `paying` event") is a sign the model is muddy.

## Transition Table / Diagram

Every non-trivial workflow deserves an explicit transition table or diagram. It can be code (a literal dict the program executes) or documentation (a Markdown table or a state diagram). The code form is best because it cannot drift from behavior. The point is that someone can see the whole legal-move set in one place and ask "is this complete? is this correct?" without tracing scattered conditionals across the codebase.

```python
from enum import StrEnum


class Order(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PAID = "paid"
    CANCELLED = "cancelled"


class Event(StrEnum):
    SUBMIT = "submit"
    PAY = "pay"
    CANCEL = "cancel"


TRANSITIONS: dict[tuple[Order, Event], Order] = {
    (Order.DRAFT, Event.SUBMIT): Order.SUBMITTED,
    (Order.SUBMITTED, Event.PAY): Order.PAID,
    (Order.DRAFT, Event.CANCEL): Order.CANCELLED,
    (Order.SUBMITTED, Event.CANCEL): Order.CANCELLED,
}


class InvalidTransition(ValueError):
    pass


def apply_event(state: Order, event: Event) -> Order:
    try:
        return TRANSITIONS[state, event]
    except KeyError as exc:
        raise InvalidTransition(f"{state} cannot handle {event}") from exc
```

## Review Model

Review a state machine in three passes, in order:

1. **Completeness**: are all states enumerated? all events? Is every `(state, event)` pair either an intended transition or an intended rejection? Are terminal states identified (`closed`, `cancelled` accept nothing further)?
2. **Correctness**: are guards correct and total? Are actions idempotent so a replayed or retried event does not double-charge or double-send? Is concurrent application safe (two events racing on the same entity)?
3. **Representation**: only now ask whether a table, a `match`, or state objects best expresses it. Get the model right before arguing about the form.

## Quick Signals

Reach for this model when you see:

- Status strings assigned in scattered places with no single definition of the legal set.
- Combinations of boolean flags standing in for state, with no enforced legal combinations.
- `if/elif` ladders that check both current state _and_ incoming event inline, repeated across several functions.
- Repeated events causing duplicate effects; a sign actions are not idempotent and transitions are not gated.

## False-Positive Boundary

A status enum on its own is **not** a state machine; it is just a named value until there are transition rules governing how it changes. Adding a transition table to genuinely trivial branching is over-engineering; if there is one obvious linear path and no illegal-state concern, the table is ceremony. The model earns its weight when illegal transitions are real and correctness matters. Apply it there, not everywhere a status field appears. See [object-oriented.md](./object-oriented.md) for when state plus behavior belongs in an object, and [declarative.md](./declarative.md) for why the table form is so reviewable.
