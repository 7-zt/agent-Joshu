# Command

## Intent

Encapsulate a request as an object, so that requests can be passed around, stored, queued, logged, replayed, and undone. The caller that issues a request is decoupled from the code that knows how to perform it.

## Problem it solves

A direct call, `service.send_email(to, template, context)`, executes immediately and leaves no trace. You cannot put it on a queue, persist it for later, record it in an audit log, replay it after a crash, or reverse it. When a request needs a life beyond the instant of its invocation, it has to become data. Command turns "do this" into a value you can hold and inspect.

## Structure and participants

- **Command**: an object carrying everything needed to perform a request: the operation and its parameters.
- **Receiver**: the object that knows how to carry out the work.
- **Invoker**: holds and triggers commands (a queue, a scheduler, a menu, a key binding).
- **Client**: creates commands and configures them with a receiver.

In the classic form a command exposes `execute()` and sometimes `undo()`. The point is that the invoker treats all commands uniformly without knowing what each one does.

## When to use

- **Queuing and scheduling**: tasks placed on a job queue, retried, or run later.
- **Undo/redo**: each action is a command with a paired inverse; a history stack drives undo.
- **Audit trails**: every state change is recorded as a command for compliance or debugging.
- **Macro recording / replay**: a sequence of commands captured and re-run.
- **Decoupling UI from action**: menu items, buttons, and shortcuts hold commands rather than calling services directly.

## When NOT to use (overkill)

- A simple, immediate function call suffices and the request needs no storage, replay, or reversal. Wrapping it in a command class is pure ceremony.
- The command has no stable schema, so it cannot actually be persisted or replayed; then it gives none of the benefits it costs you to build.
- You reach for command objects to "decouple" code that has only one caller and one receiver.

## Failure modes

- **Anemic commands plus fat handlers**: logic migrates into handlers until commands are bags of fields and the dispatch becomes a god function.
- **Unstable serialization**: persisted commands can't be deserialized after a refactor because the schema wasn't versioned. If you persist commands, treat their shape as a contract.
- **Undo that drifts**: an `undo()` that doesn't perfectly reverse `execute()` corrupts state silently. Undo correctness needs explicit tests.
- **Hidden side effects in construction**: building a command shouldn't perform the work; only the invoker should trigger it.

## Python example

A frozen dataclass is the natural carrier when the command is data to be queued, serialized, or audited:

```python
@dataclass(frozen=True)
class SendEmail:
    to: EmailAddress
    template: str
    context: dict[str, object]
```

A separate handler (or a `dispatch` map keyed by command type) performs the work, keeping the command itself a plain, serializable record. When a command needs no persistence and only carries behavior, a plain function or `functools.partial` already _is_ a command: Python's first-class functions absorb the simplest cases.

For undo, the command must capture enough prior state to reverse itself, or pair with a [unit-of-work.md](./unit-of-work.md) or memento that snapshots state.

## Relationship to other patterns

Command and [strategy.md](./strategy.md) both wrap behavior in an object, but Strategy parameterizes _how_ something is done (interchangeable algorithms) while Command parameterizes _what_ to do and _when_. A queue of commands is a common partner to [observer.md](./observer.md) event handling, where events become commands to process. Undo often combines Command with a memento or [unit-of-work.md](./unit-of-work.md). In Python, weigh every command class against a plain callable; only the need for state, serialization, queuing, audit, or undo justifies the object.
