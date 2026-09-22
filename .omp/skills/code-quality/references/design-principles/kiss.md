# KISS: Keep It Simple

## What it is

KISS says: choose the simplest design that meets the actual goal. The trap is reading "simple" as "short." Simplicity is not measured in lines of code. It is measured in the number of concepts a reader must hold in their head to understand and safely change the code: the number of dependencies, the amount of hidden control flow, the breadth of state, and how far a change has to propagate.

A more operational phrasing: minimize _unnecessary_ complexity; the complexity you added, not the complexity the problem inherently has.

## Necessary vs accidental complexity

This distinction is the whole principle.

- **Necessary (essential) complexity** comes from the problem itself. A correct distributed consensus protocol is complex because consensus is hard. A tax engine is complex because tax law is complex. You cannot wish this away.
- **Accidental complexity** comes from the solution: speculative abstraction layers, configuration knobs nobody asked for, frameworks built for one call site, indirection that exists only to look flexible, clever one-liners that take ten minutes to read.

KISS targets accidental complexity. It does not ask you to pretend a hard problem is easy. When the domain is genuinely complex, the goal is to _contain_ that complexity inside a well-bounded module with a simple interface (see [deep-modules.md](./deep-modules.md)), not to spread it thin across the whole system.

## Simplicity is "fewer concepts," not "fewer lines"

Two clear, slightly repetitive copies are often simpler than one generic function with three boolean flags and a callback. A flat sequence of statements is often simpler than a chain of tiny helpers that force the reader to jump around the file. A plain `dict` lookup is often simpler than a registry with a plugin protocol. When you compress lines but multiply concepts, you have made the code shorter and harder: the opposite of KISS.

This is why KISS is in tension with naive [dry.md](./dry.md) and with a blanket "small functions" preference: both can trade a concrete, readable repetition for an abstract, harder-to-hold structure.

## Over-engineering symptoms

- Abstractions, interfaces, or base classes with exactly one implementation.
- Configuration options, flags, or extension points that no current caller uses (this is also a [yagni.md](./yagni.md) violation).
- Layers of indirection whose only justification is "flexibility" or "in case we need to swap it later."
- A framework or plugin system built to serve a single concrete use.
- Many one-line wrapper functions that rename expressions without hiding complexity.
- Clever metaprogramming, dynamic dispatch, or generic machinery where a direct call would do.

## When complexity IS justified

KISS is not an excuse to under-build. Added complexity earns its place when it serves:

- **Correctness**: handling the real edge cases, concurrency hazards, or invariants the problem actually has.
- **Performance**: a measured, necessary optimization on a hot path (with the complexity localized and documented as to why).
- **Safety**: input validation at system boundaries, resource cleanup, error handling for failures that genuinely occur.

Stripping these out in the name of "simplicity" is not KISS; it is producing fragile code. The skill is distinguishing complexity that buys correctness, performance, or safety from complexity that buys only the appearance of sophistication.

## Interaction with other principles

- [yagni.md](./yagni.md): YAGNI removes speculative features; KISS removes unnecessary complexity in the features you do build. Together they resist over-engineering.
- [deep-modules.md](./deep-modules.md): the long-term-simple way to handle real complexity is to hide it behind a simple interface, not to scatter shallow helpers.
- [dry.md](./dry.md): when deduplication would add more concepts than it removes, KISS wins; keep the clear duplication.
