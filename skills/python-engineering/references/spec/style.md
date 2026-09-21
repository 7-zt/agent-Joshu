# Code Style

Style in a Python project splits cleanly into two layers: the part a tool can decide and enforce mechanically, and the part that requires human judgment about meaning. Conflating them wastes review attention on things a formatter already settled and, worse, lets the things that actually matter, names, boundaries, abstraction level, slip through because everyone was arguing about line length. This document is about drawing that line and spending judgment only where it pays.

## The PEP 8 Baseline

PEP 8 is the default style substrate for Python: layout, indentation, imports, naming, comments, and a handful of programming recommendations. It is the shared baseline that makes unfamiliar Python code readable. But it is not a complete engineering specification: it says nothing about type boundaries, exception semantics, tooling, or architecture, and many of its concrete formatting rules predate modern auto-formatters. The right way to adopt PEP 8 is "follow it by default, allow local consistency and readability to win," not "transcribe every historical formatting clause into a hard rule."

## The Automation Boundary

The single most useful move in style management is to delegate everything mechanical to tools and stop discussing it.

A formatter (Ruff's formatter, or Black) owns layout: line wrapping, quote style, whitespace, trailing commas, bracket placement. These have no semantic content, so the only thing that matters is consistency, and a formatter delivers that for free. Once a formatter runs in pre-commit and CI, formatting is no longer a review topic; there is nothing to debate.

A linter (Ruff) owns the mechanically detectable: unused imports, import ordering, obviously dead code, outdated syntax that a modern target version supersedes, and a large catalog of bug-prone patterns. A linter is configured by selecting rule families deliberately rather than enabling everything; every rule added should earn its place against false-positive cost. Tooling specifics, which rule families, how they are configured, live in the tooling references; what matters here is the principle: if a rule can decide it, a human should not be deciding it in review.

What this leaves for human review is everything a tool _cannot_ judge: whether a name communicates intent, whether a module has one responsibility, whether an abstraction is pulling its weight, whether the code says what it means. That is where style review attention belongs.

## Naming

Names are the most consequential style decision because readers see them far more often than writers change them, and no tool can evaluate them. Beyond PEP 8's mechanical conventions (`snake_case` for functions and variables, `PascalCase` for classes, `UPPER_CASE` for constants), judge whether a name communicates intent at the point of use.

A name should describe what a thing _is_ or _does_ in the domain, not its type or its implementation. `users` beats `user_list`; `deadline` beats `dt2`; `is_expired` beats `flag`. Scope should guide length: a loop index can be `i`, a module-level function cannot. Avoid encoding type information a reader can already see from the annotation, and avoid abbreviations that save a few characters at the cost of a moment's decoding on every read. Booleans read best as predicates (`is_`, `has_`, `should_`); functions with side effects read best as verbs.

## Module Boundaries

A module should have a reason to exist that can be stated in one sentence. When a module accumulates unrelated responsibilities, request handling next to database access next to formatting helpers, every change touches it and every import drags in the whole pile. The judgment a tool cannot make is whether the things in a module belong together: do they change for the same reasons, are they at the same level of abstraction, would a reader looking for one expect to find the others. Cohesion is the test, not file size. A focused 400-line module is healthier than a 50-line grab-bag named `utils` that everything imports and nothing owns.

## Abstraction Level

Good code reads at a consistent level within any one function: a high-level orchestration function should call well-named steps, not interleave orchestration with byte-twiddling. Mixing levels, a function that both decides business policy and manipulates string indices, forces the reader to constantly shift mental gears. The corrective is not "more abstraction" but _consistent_ abstraction: extract the low-level detail behind a name so the high-level function reads as a sequence of intentions. This is a judgment call with a real failure mode in the other direction (premature abstraction, indirection with no payoff), which is exactly why it cannot be automated.

## Explicitness

PEP 20's "explicit is better than implicit" is a style value, not a lint rule, and it shows up in dozens of small decisions: passing dependencies as arguments rather than reaching for globals, returning a named type rather than a bare tuple the caller must remember how to unpack, raising a specific exception rather than a bare `Exception`, naming a magic number as a constant. Explicitness trades a little brevity for a lot of readability and is almost always worth it at interface boundaries. The counterweight is that explicitness taken to an extreme becomes noise: spelling out what is already obvious from a good name or a clear type adds nothing. The judgment is whether making something explicit _reduces_ the reader's work; when it does, prefer it.
