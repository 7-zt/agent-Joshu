# Object-Oriented Programming

## What it is

Object-oriented programming organizes state, behavior, and invariants into objects, and expresses system behavior through their collaboration. An object bundles data with the operations that are allowed on that data, and ideally guarantees that the data stays valid, its invariants hold, across every public operation. Python fully supports OO but does not force it: functions, modules, and plain data are first-class alternatives.

OO provides the most value when a concept has a long-lived identity, internal state that must stay consistent, and a set of operations that belong together. It provides the least value for one-shot calculations or data reshaping, where a function or plain record is clearer.

## The assumption underneath

- When a concept has lasting identity, internal state, invariants, and related behavior, modeling it as an object keeps the logic that protects those invariants in one place.
- An object's interface should express _meaning_, not expose its internal storage layout.
- Inheritance models a genuine subtype relationship or a framework extension point; reuse of implementation is better served by composition.

## When it fits

- Domain entities, value objects, resource objects, external clients, strategy objects, plugin objects.
- Objects that must maintain an invariant: a state machine, a money amount, a time range, a permission rule, a bounded buffer.
- Objects with an obvious lifecycle: a connection pool, a transaction, a cache, a task runner.
- Polymorphism: several implementations behind one interface, selected at runtime: though in Python a `Protocol` plus plain functions often expresses this with less ceremony.

The test for "should this be an object" is whether bundling the data with its operations _protects an invariant that would otherwise be everyone's responsibility_. A `Money` type that refuses to add two different currencies, or a `DateRange` that refuses to construct with `end < start`, earns its class because the guarantee lives in one place and no caller can bypass it:

```python
@dataclass(frozen=True)
class DateRange:
    start: date
    end: date

    def __post_init__(self) -> None:
        if self.end < self.start:
            raise ValueError("end must not precede start")

    def overlaps(self, other: "DateRange") -> bool:
        return self.start <= other.end and other.start <= self.end
```

Every `DateRange` in the system is valid by construction, and the overlap rule lives with the data it operates on. Contrast this with a plain dict `{"start": ..., "end": ...}` whose validity every caller must re-check.

## Common mistakes

- **Everything is a class.** Simple pure calculations and data transforms forced into classes that hold no state. A module of functions is clearer.
- **Anemic models.** `Manager`, `Service`, and `Helper` classes absorb all the behavior while the "domain object" is reduced to a bag of public fields. The data and the rules that govern it have been split apart; the opposite of what OO is for. See [tell-dont-ask](../design-principles/tell-dont-ask.md).
- **Deep inheritance.** Subclassing used to share implementation rather than to substitute behavior. Each level adds MRO complexity and hidden coupling. Prefer composition; see [composition-over-inheritance](../design-principles/composition-over-inheritance.md).
- **Java/C++ ceremony transplanted.** Interfaces, abstract base classes, and factory layers introduced for every collaboration, where Python would use a function, a small `Protocol`, or a `dataclass`.

The anemic-model trap is worth seeing concretely. The anemic version scatters a rule across every caller:

```python
# Anemic: the rule "cannot withdraw more than balance" lives in callers
@dataclass
class Account:
    balance: int

def withdraw(account: Account, amount: int) -> None:
    if amount > account.balance:      # every caller must remember this
        raise ValueError("insufficient funds")
    account.balance -= amount
```

The encapsulated version owns the rule, so no caller can violate it:

```python
@dataclass
class Account:
    _balance: int

    def withdraw(self, amount: int) -> None:
        if amount > self._balance:
            raise ValueError("insufficient funds")
        self._balance -= amount
```

The difference is not style. In the first form, a new caller that forgets the check corrupts the balance; in the second, the invariant cannot be bypassed. This is the [tell-dont-ask](../design-principles/tell-dont-ask.md) principle in practice.

## Relationship to other paradigms

A long-lived object with invariants is often best paired with a [state-machine.md](./state-machine.md) for its lifecycle. The decision _logic_ inside its methods can still be pure and pushed toward a [functional-core.md](./functional-core.md). "More OO" is never the goal; the goal is to put state, invariants, and behavior at the boundary where they belong.
