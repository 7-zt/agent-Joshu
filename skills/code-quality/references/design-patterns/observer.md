# Observer / Pub-Sub

## Intent

Let one object (the subject) notify many dependents (observers) when its state changes or an event occurs, without the subject knowing who they are. It establishes a one-to-many dependency that can change at runtime.

## Problem it solves

When several parts of a system must react to something happening, a cache must invalidate, a UI must refresh, an audit log must record, wiring direct calls from the source to each reactor couples the source to all of them. Adding a new reactor means editing the source. Observer inverts this: reactors subscribe, and the source only publishes.

## Structure and participants

- **Subject / publisher**: holds the subscription list and emits notifications.
- **Observer / subscriber**: registers interest and handles notifications.
- **Event**: the payload describing what happened.

## Python example

In Python the subject is often an event bus keyed by event type:

```python
class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[type[Event], list[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: type[Event], handler: Callable[[Event], None]) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: Event) -> None:
        for handler in list(self._subscribers.get(type(event), [])):
            handler(event)
```

## Design concerns to decide explicitly

These are where Observer implementations go wrong. None has a single right answer, but each must be a deliberate choice, not an accident.

- **Subscriber lifecycle**: who unsubscribes, and when? Subscriptions that outlive their subscriber leak memory and keep dead objects alive. Consider `weakref` for handlers, or hand back an explicit unsubscribe handle / use a context manager.
- **Error propagation**: if one handler raises, do later handlers still run? Swallowing errors hides bugs; letting them propagate lets one bad subscriber break the publish. Decide and document the policy. One common choice is to isolate per-handler errors, log them, and continue.
- **Ordering**: do subscribers run in registration order, or is order undefined? Don't let callers depend on order unless you guarantee it.
- **Reentrancy**: can a handler publish, subscribe, or unsubscribe during dispatch? Iterating over a copy of the subscriber list (as above) avoids mutation-during-iteration bugs.
- **Sync vs async**: synchronous in-process notification is simplest. For `async` handlers you must choose sequential `await` vs `asyncio.gather`, and how to handle a handler that blocks or never completes.

## When to use

- Multiple independent reactors must respond to an event, and the set of reactors changes or is unknown to the source.
- You want to decouple a domain action from its side effects (email, metrics, cache).
- The relationship is genuinely one-to-many and dynamic.

## When NOT to use

- There is exactly one, fixed reactor; call it directly. An event bus adds indirection and hides control flow for no decoupling benefit.
- Strict ordering and a clear sequential workflow matter more than decoupling; an explicit pipeline reads better.
- Cross-process delivery is needed: in-process Observer gives no delivery, retry, or durability guarantees. Use a real message system (queue, broker) with defined semantics.

## Failure modes

- **Hidden control flow**: a `publish` triggers a cascade of effects that no one can trace by reading the call site.
- **Memory leaks**: forgotten subscriptions hold references forever.
- **Surprise reentrancy**: a handler mutates the subject mid-dispatch, corrupting iteration.
- **Silent failure**: a swallowed exception means an event "happened" but its effect never did.

## Relationship to other patterns

Observer overlaps with [command.md](./command.md) when events are reified objects that can be queued or replayed. [mediator] coordination is the inverse stance: a mediator centralizes interaction logic, whereas Observer distributes it. For cross-process fan-out, this pattern gives way to message-broker infrastructure rather than an in-memory bus.
