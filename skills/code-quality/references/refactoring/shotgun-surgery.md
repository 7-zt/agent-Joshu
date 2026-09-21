# Shotgun Surgery

## What it is

Shotgun Surgery is the smell where one conceptual change forces you to make many small edits across many different files or classes. You decide to add a new payment method, change how dates are formatted, or rename a field in the wire protocol, and suddenly you are touching a dozen modules, each with a tiny piece of the change. Miss one, and the system is subtly broken. The change is logically single but physically scattered.

The pain is felt at change time, which is what makes it a _change preventer_: the code might read fine in any one place, but the cost of evolving it is high and the risk of an incomplete change is constant. The more places a single decision is smeared across, the more likely some future edit updates most of them and forgets the rest.

## The signal

You notice it when a routine change generates a long, repetitive diff across unrelated-seeming files, or when your mental checklist for a change is "remember to also update X, Y, and Z." Code review comments like "did you also change the validator / the serializer / the docs?" are the social symptom. A practical detection move is to make the change and watch how the edit fans out: if a single responsibility required edits in seven places, those seven places are holding fragments of one concept.

This is frequently a downstream effect of Primitive Obsession and Duplicated Knowledge: when a domain concept (a status, a rate, a format) has no single home, every place that uses it must encode the same knowledge, so every change to that knowledge hits every place. See [duplicated-code.md](./duplicated-code.md) and [primitive-obsession.md](./primitive-obsession.md).

## What it is telling you

Shotgun Surgery is the symptom of a **missing abstraction** or **poor cohesion**: the thing that should be in one place is spread out. The remedy is to gather the scattered pieces into a single module, class, or function that owns that decision: the inverse operation of the smell. Common moves:

- [move-function.md](./move-function.md) and Move Field to pull the scattered behavior and data together into one owner.
- Introduce the missing type (a value object, an enum, a config object) so the concept has a home, after which the scattered usages collapse to references to that one type.
- Replace the repeated knowledge with a single source of truth, a table, a dispatch map, a schema, so a change is one edit.

The goal is that a future change of this kind touches one place. You will not always get to exactly one, but going from twelve places to two is a large reduction in risk.

## Relationship to Divergent Change

Shotgun Surgery and [divergent-change.md](./divergent-change.md) are inverse smells, and it is worth holding both in mind because the fixes pull in opposite directions.

- **Shotgun Surgery:** _one change → many modules._ One kind of change is spread across too many places. The fix is to **gather**: pull the pieces together so the change is localized.
- **Divergent Change:** _one module → many kinds of change._ One module is changed for many unrelated reasons. The fix is to **split**: separate the responsibilities so each changes for one reason.

Both are about aligning module boundaries with the axes along which the code actually changes. Shotgun Surgery says a boundary is missing (a concept has no home); Divergent Change says a boundary is in the wrong place (a module holds too many concepts). The unifying target is the Single Responsibility Principle read as "one reason to change"; see [solid](../design-principles/solid.md). Fixing one can reveal the other, so re-evaluate after each move rather than over-gathering or over-splitting in a single pass.
