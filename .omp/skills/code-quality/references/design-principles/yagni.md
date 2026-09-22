# YAGNI: You Aren't Gonna Need It

## What it is

YAGNI says: do not build capability for a future you only imagine. The principle, sharpened by Martin Fowler, targets _presumptive features_ and _speculative abstractions_: functionality or flexibility added now because you guess it will be useful later. It is a statement about timing: build it when a real need arrives, not before.

YAGNI is frequently misquoted as an argument against tests, error handling, or careful design. It is not. Fowler is explicit that YAGNI does not oppose the refactoring, testing, and technical health that keep code easy to change. In fact YAGNI _depends_ on those things.

## Why speculative building costs more than it seems

Fowler breaks the cost of a presumptive feature into four parts:

- **Cost of build**: the time spent building something not yet needed, taken away from something that is.
- **Cost of delay**: the features you actually need ship later because you were busy with the speculative one.
- **Cost of carry**: the unused capability makes the system harder to understand and modify _for everyone, every day_, until it is finally used or removed.
- **Cost of repair**: when the speculative feature guessed wrong (the common case), you pay again to fix or remove it.

The carry cost is the one people forget. An unused extension point is not free real estate; it is a permanent tax on comprehension. Every reader has to wonder what it is for, every refactor has to preserve it, every test has to account for it.

## What YAGNI prohibits

- Building a plugin system, base class, registry, or generic framework before there is more than one real implementation.
- Adding an interface or abstraction for a hypothetical second implementation.
- Adding fields, parameters, config switches, or extension hooks that no current caller uses.
- Generalizing a function to handle inputs that never occur.

## What YAGNI does NOT prohibit

This is the part most often gotten wrong. YAGNI is about _speculative features_, not about engineering discipline. It does not excuse skipping:

- **Tests**: they protect the behavior that lets you defer decisions safely.
- **Error handling**: for failures that genuinely occur, especially at boundaries.
- **Type safety**: type hints on public APIs and module boundaries reduce, not increase, the cost of future change.
- **Resource cleanup**: context managers for files, connections, locks, and transactions are correctness, not speculation.
- **Refactoring**: keeping code malleable is precisely what makes YAGNI viable.
- **API stability for published interfaces**: for a public API, persisted schema, or external protocol, designing a stable boundary up front is not speculation; the cost of changing it later is real and known.

The discriminator: is the work serving a _known, present_ need (correctness, safety, a real consumer), or hedging against an _imagined, future_ one? The former is good engineering; only the latter is what YAGNI forbids.

## YAGNI requires malleable code

YAGNI is only safe when changing your mind later is cheap. If the code has no tests and resists refactoring, deferring a decision turns into a permanent gap; you'll be too afraid to add the capability when it's actually needed. So YAGNI, [tdd.md](./tdd.md) (or test-after), and refactoring form a package: tests and refactoring keep code malleable, and malleable code makes "decide later" a rational strategy rather than an excuse for debt.

## Interaction with other principles

- [kiss.md](./kiss.md): YAGNI removes speculative features; KISS removes unnecessary complexity in the ones you keep.
- [rule-of-three.md](./rule-of-three.md): the deduplication-specific form of "wait until it's actually needed."
- SOLID's Open/Closed Principle (see [solid.md](./solid.md)) pulls toward extension points; YAGNI says build them only when a real variation appears.
