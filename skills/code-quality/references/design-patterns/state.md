# State Pattern (GoF)

The GoF State Pattern eliminates conditional logic for state-dependent behavior by delegating to polymorphic state objects. A Context holds a reference to a current State object. Each concrete State class implements the same interface, providing behavior specific to that state. State transitions replace the Context's current state reference.

This is one specific OO implementation of state-machine behavior. It is not synonymous with state machines in general; many state machines are better served by simpler representations: enum + transition table, reducer functions, `match`/`case`, or dispatch maps. Always start with [state-machine modeling](../programming-paradigms/state-machine.md) to define states, events, transitions, guards, and invalid-transition policy before deciding whether the State Pattern adds value over simpler implementations.

## Structure

- Context: maintains a reference to a ConcreteState; delegates state-dependent requests.
- State (interface/Protocol): defines the interface for state-dependent behavior.
- ConcreteState: implements behavior for a specific state; may trigger transitions by replacing the Context's state reference.

## When The Pattern Fits

- Each state has substantial, distinct behavior, not just a different return value or flag.
- The number of states is moderate and relatively stable.
- State-specific behavior is complex enough that splitting into classes improves readability over flat conditionals.
- New states can be added without modifying existing state classes (OCP benefit).
- State objects need access to Context data to perform their behavior.

## When The Pattern Does Not Fit

- States are few, transitions are simple, and behavior differences are minor. A transition table or `match` is clearer.
- The workflow is primarily about transition permissions and side effects, not polymorphic behavior. Use a transition table instead.
- State classes become trivial one-method wrappers around a single expression; the indirection cost exceeds the clarity gain.
- The number of states grows rapidly or is data-driven. A table-based approach scales better.
- State transitions need to be auditable in one place. The State Pattern scatters transitions across concrete state classes.

## Common Implementation Issues

**Transition ownership.** Who decides the next state? If each ConcreteState decides, transitions are scattered across classes and harder to audit. If Context decides, the pattern may degenerate into conditionals in Context. Choose one approach consistently within a given context boundary.

**Shared context data.** State objects often need access to Context data. Pass Context explicitly to state methods or use a shared data object. Avoid hidden coupling through global state or module-level variables.

**State identity.** Are state objects singletons, or do they carry per-instance data? Stateless state objects can be shared safely; stateful ones need explicit lifecycle management: who creates them, when they are discarded.

**Testing.** Test each state class independently with focused unit tests, then test transitions at the Context level. Verify illegal transitions are rejected, not silently ignored.

## Distinguishing State From Strategy

[Strategy](./strategy.md) and State both delegate to polymorphic objects, but they vary different things. Strategy varies the _algorithm_. State varies the _lifecycle phase_. If objects do not transition between strategies during their lifetime, it is Strategy, not State. If the subject moves through a sequence of phases and behavior changes with each phase, it is State.

## Distinguishing State Pattern From State Machines

The State Pattern is an implementation technique. State-machine modeling is a design technique. A state machine can be implemented as an enum + transition table, a reducer, a `match` block, a dispatch map, a dedicated library, _or_ the GoF State Pattern. The State Pattern earns its keep only when each state carries substantial behavior that benefits from polymorphic dispatch.

If you only need to track legal transitions and run side effects during a transition, without giving each state a rich behavioral interface, a [transition table](../programming-paradigms/state-machine.md) is simpler and easier to audit.

[Command Pattern](./command.md) encapsulates requests rather than states; it complements State when transitions queue commands for later execution.
