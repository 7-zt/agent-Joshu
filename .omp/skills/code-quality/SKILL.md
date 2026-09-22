---
name: code-quality
description: Use when evaluating or improving code quality, including maintainability, abstractions, design principles and patterns, refactoring, code smells, test design, and architecture.
---

# Code Quality

Use this Skill to judge whether code, tests, architecture, refactoring plans, and abstractions have reasonable structure, change boundaries, and maintenance cost.

## Entry Conditions

Activate this Skill for maintainability, design quality, test quality or test smells, abstraction boundaries, refactoring, code smells, programming-paradigm choice, design-pattern use, or design principles. Load reference leaves by signal, not all at once.

If the task does not explicitly require code-quality analysis, do not load any document under `references/`, even if this `SKILL.md` was loaded.

## Mode Selection

Three modes are available. Default to fast review.

| Mode | Trigger | Read |
| --- | --- | --- |
| Fast review | Default for daily self-check, small diff, PR review | `./workflow/fast-review.md` |
| Full review | User explicitly says "full review", "architecture review", "systematic review", "refactoring assessment" | `./workflow/full-review.md` |
| Analysis | User asks for discussion, brainstorm, design exploration, paradigm comparison, mechanism analysis | `./workflow/analysis.md` |

## Judgment Order

1. Identify the primary concern: correctness, readability, change cost, testability, performance, or delivery cost.
2. Decide whether the issue belongs to principles, patterns, refactoring, or paradigms.
3. Route to the relevant leaf document below.
4. Report only issues with sufficient evidence.

| Signal | Read First | Often Pair With |
| --- | --- | --- |
| DRY, duplicate knowledge, wrong abstraction | [DRY](./references/design-principles/dry.md) | Rule of Three, duplicated code |
| Two similar cases, premature abstraction | [Rule of Three](./references/design-principles/rule-of-three.md) | DRY, KISS |
| Unnecessary complexity | [KISS](./references/design-principles/kiss.md) | YAGNI, deep modules |
| Premature extension point, unneeded flexibility | [YAGNI](./references/design-principles/yagni.md) | KISS, deep modules |
| SOLID, responsibility, substitutability, interface size, dependency direction | [SOLID](./references/design-principles/solid.md) | composition over inheritance, dependency inversion |
| Responsibility assignment, where behavior belongs | [GRASP](./references/design-principles/grasp.md) | Tell Don't Ask, feature envy |
| Message chains, distant object structure knowledge | [Law of Demeter](./references/design-principles/law-of-demeter.md) | deep modules, facade |
| Callers query fields then make domain decisions | [Tell Don't Ask](./references/design-principles/tell-dont-ask.md) | GRASP, feature envy |
| Inheritance vs composition, mixins, subclassing | [Composition over Inheritance](./references/design-principles/composition-over-inheritance.md) | SOLID, dependency inversion |
| Dependency inversion, DI, composition root | [Dependency Inversion](./references/design-principles/dependency-inversion.md) | adapter, repository, unit of work |
| TDD, Red-Green-Refactor, behavior-first tests | [TDD](./references/design-principles/tdd.md) | safe refactoring |
| Test design, test smells, fragile/flaky tests, over-mocking, coverage strategy, fewer stronger tests | [Testing Principles](./references/testing/principles.md) | test smells, TDD |
| Test breaks on refactor, change-detector, obscure/duplicated tests, testing config/utils | [Test Smells](./references/testing/test-smells.md) | testing principles, code smells |
| Domain-driven design, bounded contexts, domain modeling | [DDD](./references/design-principles/ddd.md) | deep modules, repository |
| Abstraction depth, information hiding, shallow modules | [Deep Modules](./references/design-principles/deep-modules.md) | KISS, facade |
| Object creation varies by type/config/env | [Factory](./references/design-patterns/factory.md) | abstract factory, builder |
| Matched family of products varies together | [Abstract Factory](./references/design-patterns/abstract-factory.md) | factory, builder |
| Complex staged construction | [Builder](./references/design-patterns/builder.md) | factory, abstract factory |
| Algorithm/behavior varies behind stable call site | [Strategy](./references/design-patterns/strategy.md) | factory, functional core |
| One event notifies multiple subscribers | [Observer](./references/design-patterns/observer.md) | event-driven, command |
| Foreign interface needs translation | [Adapter](./references/design-patterns/adapter.md) | facade, dependency inversion |
| Cross-cutting behavior wraps calls/objects | [Decorator](./references/design-patterns/decorator.md) | facade, thin wrapper function |
| Simple surface over complex subsystem | [Facade](./references/design-patterns/facade.md) | deep modules, adapter |
| Request queued, retried, audited, undone, scheduled | [Command](./references/design-patterns/command.md) | state, observer |
| State-specific behavior, GoF State Pattern | [State](./references/design-patterns/state.md) | state machine, command |
| Operations vary over stable node types (AST/tree/schema) | [Visitor](./references/design-patterns/visitor.md) | strategy |
| Persistence boundary, ORM isolation | [Repository](./references/design-patterns/repository.md) | unit of work, dependency inversion |
| Transaction/consistency across repositories | [Unit of Work](./references/design-patterns/unit-of-work.md) | repository, dependency inversion |
| Refactoring as behavior-preserving Fowler-style work | [Fowler Refactoring](./references/refactoring/fowler-refactoring.md) | safe refactoring, code smells |
| General smell triage and smell map | [Code Smells](./references/refactoring/code-smells.md) | specific refactoring leaves |
| Safe behavior-preserving refactoring flow | [Safe Refactoring](./references/refactoring/safe-refactoring.md) | fowler refactoring, TDD |
| Function mixes phases, policy, I/O, branching | [Long Function](./references/refactoring/long-function.md) | extract function, duplicated code |
| Repeated rule, mapping, schema, copied knowledge | [Duplicated Code](./references/refactoring/duplicated-code.md) | DRY, extract function |
| Strings/dicts/primitives carry stable domain meaning | [Primitive Obsession](./references/refactoring/primitive-obsession.md) | DDD, data-oriented |
| Function envies another object/module data | [Feature Envy](./references/refactoring/feature-envy.md) | move function, GRASP |
| One change requires many scattered edits | [Shotgun Surgery](./references/refactoring/shotgun-surgery.md) | divergent change, move function |
| One module changes for many unrelated reasons | [Divergent Change](./references/refactoring/divergent-change.md) | shotgun surgery |
| Helper/wrapper adds no semantic boundary | [Thin Wrapper Function](./references/refactoring/thin-wrapper-function.md) | KISS, facade |
| Extract a coherent phase into a function | [Extract Function](./references/refactoring/extract-function.md) | long function, inline function |
| Inline a misleading or shallow function | [Inline Function](./references/refactoring/inline-function.md) | extract function |
| Move behavior to a better owner | [Move Function](./references/refactoring/move-function.md) | feature envy, GRASP |
| Direct steps, scripts, handlers, orchestration | [Imperative](./references/programming-paradigms/imperative.md) | declarative |
| Config, schema, table-driven, declarations | [Declarative](./references/programming-paradigms/declarative.md) | imperative |
| Object identity, state, invariants, polymorphism | [Object-Oriented](./references/programming-paradigms/object-oriented.md) | composition over inheritance, SOLID |
| Separate pure logic from side-effect shell | [Functional Core](./references/programming-paradigms/functional-core.md) | strategy, declarative |
| Explicit data shapes, mappings, schemas, tables | [Data-Oriented](./references/programming-paradigms/data-oriented.md) | primitive obsession, declarative |
| Events, hooks, event bus, pub/sub, domain events | [Event-Driven](./references/programming-paradigms/event-driven.md) | observer, command |
| State/status/event/transition workflow | [State Machine](./references/programming-paradigms/state-machine.md) | state, resource lifecycle |
| Resource acquisition, ownership, cleanup | [Resource Lifecycle](./references/programming-paradigms/resource-lifecycle.md) | state machine, unit of work |
| Async tasks, cancellation, timeouts, backpressure | [Async/Concurrency](./references/programming-paradigms/async-concurrency.md) | event-driven, resource lifecycle |

When terminology is unclear or inconsistent, read the [glossary](./glossary.md).

## Output Contract

Lead with findings. Principles are not mechanical rules; explain tradeoffs. Patterns are not default templates; prove the variation point exists first. Separate facts, inferences, judgments, and recommendations. Do not repeat issues a formatter or linter catches mechanically.

Output format is mode-specific. Follow the matching workflow document (`./workflow/fast-review.md`, `./workflow/full-review.md`, or `./workflow/analysis.md`). Analysis mode gives tradeoffs and options, not a findings list.

Write output in the language required by global, project, or user instructions; when none is specified, use the current conversation's language.

## Stop Rules

- Do not force findings to satisfy a principle.
- Do not abstract merely because code looks similar.
- Do not treat similar code as duplicate knowledge without proving shared intent.
- Do not automatically apply refactors, patches, unsafe fixes, or bulk suppressions.
- Read-only and analysis tasks leave reviewed files unchanged. Existing authorization to maintain reports or Task materials still applies.
- Do not report issues that a formatter or linter can catch mechanically. Note them once if relevant, then move on.
