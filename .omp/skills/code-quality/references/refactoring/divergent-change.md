# Divergent Change

## What it is

Divergent Change is the smell where a single module is repeatedly changed for many unrelated reasons. Every time the database schema changes, you edit this module; every time the report format changes, you edit it again; every time a business rule moves, you are back in the same file touching a different part. The module has become a junction where several independent concerns happen to coexist. One file, many unrelated reasons to open it.

It is a _change preventer_ because the mixed concerns make every change riskier than it should be: editing the report-formatting code means navigating past the persistence code and the validation code, and a change to one concern can accidentally disturb another. The module also resists understanding, because to know "what this module is about" you have to hold several disjoint topics in your head at once.

## The signal

The detection question is: _for how many different reasons does this module get edited?_ If you can look at the commit history (or just imagine the kinds of future requests) and see that this one file changes for "new tax rule," "new export format," "new storage backend," and "new validation policy," those are four reasons, four concerns, one module. A within-file signal is a class or module whose sections have no data or logic in common: the methods cluster into groups that never call each other and never touch the same fields.

A clean contrast with [shotgun-surgery.md](./shotgun-surgery.md) sharpens it: there, one change hits many modules; here, many changes hit one module. They are mirror images.

## What it is telling you

Divergent Change is the signal to **split responsibilities**. The module is doing several jobs, and each job should live in its own module so it can change independently and in isolation. The refactoring is usually:

- [extract-function.md](./extract-function.md) to first isolate the cohesive groups, then Extract Class / Extract Module to give each concern its own home.
- [move-function.md](./move-function.md) to relocate behavior to the module that owns its concern.
- Separate the layers that were tangled: for example, split a module that mixed business rules, persistence, and formatting into three, so a formatting change touches only the formatting module.

After the split, each resulting module has a single axis of change: you edit the persistence module only when persistence changes, the rules module only when rules change. That is the practical meaning of cohesion.

## Relationship to SRP and Shotgun Surgery

Divergent Change is the **Single Responsibility Principle** stated as a smell. Uncle Martin framed SRP as "a module should have one reason to change." Divergent Change violates that property because the module has many reasons to change. The cure is to find the distinct actors or forces that drive change and give each its own module. See [solid](../design-principles/solid.md).

It is also the **inverse of Shotgun Surgery**, and the two must be balanced against each other:

- **Divergent Change** → one module, many reasons to change → **split** it apart.
- **Shotgun Surgery** → one reason to change, many modules → **gather** them together.

Over-correcting either way creates the other. Split too aggressively and a single change starts requiring edits across all the new fragments (Shotgun Surgery). Gather too aggressively and the combined module starts changing for many reasons (Divergent Change). The target both smells point at is the same: module boundaries should follow the real axes of change, so that one kind of change maps to one place to edit. When in doubt, identify the actual reasons this code has changed historically, and let those reasons define the boundaries.
