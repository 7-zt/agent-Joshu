# Deep Modules and Information Hiding

This document draws on John Ousterhout's _A Philosophy of Software Design_. Its central idea is
a way to judge the quality of an abstraction by comparing the cost of its interface against the
value of what it hides.

## Depth: interface cost vs implementation value

Every module has two faces: an **interface** (what callers must understand to use it) and an
**implementation** (everything behind that interface). Ousterhout frames module quality as the
ratio between them:

- A **deep module** has a simple interface that hides a large amount of useful complexity. A
  caller learns a little and gets a lot. A garbage collector, a well-designed file system API,
  or `requests.get(url)` are deep: trivial to call, substantial behind the curtain.
- A **shallow module** has an interface nearly as complicated as its implementation. The caller
  pays almost the full cost of understanding the internals just to use it, so the module
  provides little net benefit. A one-line wrapper whose signature restates its body is the
  extreme case.

The value of a module is not its size. A deep module can be large inside; what matters is that
the interface is small relative to what it absorbs. This reframes the goal of abstraction: not
"hide code" but "let callers ignore complexity they do not need to reason about".

## Information hiding

The mechanism behind depth is information hiding: each module encapsulates a design decision,
especially one likely to change or one that is hard to get right, so that other modules do not
depend on it. When the hidden decision changes, the change stays local.

The complement is **information leakage**: when a design decision shows up in multiple modules,
so a change forces edits in all of them. A storage format known to both the reader and the
writer, a wire protocol detail visible to every caller, an error-mapping convention duplicated
across layers; these are leaks. Leakage is the deeper cause behind smells like
[shotgun surgery](../refactoring/shotgun-surgery.md), and information hiding is how
[DRY](./dry.md) applies to design decisions, not just code: the knowledge lives in one module.

## What makes a good abstraction

- It hides something genuinely worth hiding: a hard algorithm, a volatile dependency, a
  protocol detail, a set of error and version differences.
- Its interface is expressed in terms the caller already thinks in, not in terms of the
  implementation.
- It does not force the caller to know the right _sequence_ of calls or the internal state to
  use it correctly. Needing such knowledge is itself a form of leaked complexity.
- The common case is simple to invoke; the rare case is possible but does not complicate the
  common path.

A frequent anti-pattern is the **pass-through method**; a method that does nothing but call
another method with the same signature. It adds interface surface and indirection while hiding
nothing, making the module shallower. The same applies to thin wrapper functions that rename a
single expression: see [DRY](./dry.md) on shallow helpers.

## Relationship to KISS and interface design

Deep modules sharpen [KISS](./kiss.md). "Keep it simple" does not mean every function must be
short; it means minimizing the complexity a reader must hold in mind. A few deep modules with
clean interfaces leave the reader with less total complexity than many shallow helpers that
force constant jumping between files. Chasing short functions and small files for their own sake
produces shallow modules and _more_ interface to learn: the opposite of simple.

Depth also tempers the small-interface instinct of [Interface Segregation](./solid.md): the goal
is interfaces that are small _for what they deliver_, not interfaces sliced so thin that callers
must assemble many of them to get anything done.

## When the principle is misapplied

- Treating information hiding as "make every field private and add getters/setters". Accessors
  that mechanically expose every field hide nothing and just add surface. A transparent
  dataclass for a simple data carrier is fine; encapsulate when there are invariants or likely
  change.
- Hiding things that callers legitimately need: necessary configuration, meaningful errors, or
  real performance costs. Hiding a cost does not remove it; it surprises the caller later.
- Splitting a coherent deep module into shallow fragments to satisfy a file-size or
  function-length preference.
