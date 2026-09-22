# Long Function

## What it is

Long Function is the most common bloater, and the most misjudged. The smell is not length measured in lines; a function is too long when it **mixes levels of abstraction, carries more than one responsibility, or has subsections you can only understand by reading them in full**. Length is a hint that one of those is happening, not the problem itself. A forty-line function that reads as one clear sequence at a single level of abstraction is fine; a twelve-line function that interleaves high-level policy with low-level byte manipulation is not.

The reliable test is whether you can name the function honestly. If the name is a truthful summary of everything inside, the function is cohesive. If the honest name would be "validate the order, _and_ compute the total, _and_ format the receipt, _and_ send the email," it is doing several things and the "and"s mark the seams where it wants to split.

## What makes a function too long

- **Mixed abstraction levels.** The body jumps between "what" (orchestrating a business workflow) and "how" (string formatting, index arithmetic, dictionary munging). The reader has to constantly shift altitude. Each low-level chunk wants to become a named function so the high-level flow reads cleanly.
- **Multiple responsibilities.** Distinct phases, parse, then validate, then transform, then persist, packed into one function. Each phase is a candidate for extraction, especially when they communicate through a handful of local variables that form a natural interface.
- **Hard-to-name subsections.** A telltale sign is a comment introducing a block: `# now compute the discount`. The comment is naming a concept the code refused to name. That block is usually an Extract Function waiting to happen, with the comment becoming the function name.
- **Deep nesting and long conditionals.** Arrow-shaped code where guard clauses or extracted predicates would flatten the logic and reveal the intent.

## Extraction signals

Reach for [extract-function.md](./extract-function.md) when:

- You wrote a comment to explain the next few lines; extract them and let the name carry the comment.
- A block of lines uses a tight cluster of local variables that the rest of the function does not touch; that cluster is a function boundary.
- You find yourself scrolling to hold the whole function in your head.
- A phase could be tested in isolation but currently cannot because it is buried.

## When length is acceptable

Not every long function is a smell, and forced splitting can make code worse by scattering a linear story across many tiny functions the reader must reassemble. Length is acceptable when:

- **It is one clear sequence at one abstraction level.** A function that does ten steps, in order, all at the same level, with no branching complexity, reads top-to-bottom like prose. Splitting it just adds jump cost. See the tension with [thin-wrapper-function.md](./thin-wrapper-function.md): extracting a step used once, with no abstraction boundary, often produces a shallow helper that hurts more than the length did.
- **Configuration or data.** A long literal table, a big mapping, a set of constants: length here is just data volume, not logical complexity.
- **Test setup and test bodies.** Tests often read better as explicit, linear setup-act-assert even when long; over-extracting test helpers hides what the test actually exercises.
- **A `match` or dispatch over many cases** where each case is short and the structure is flat.

## Relationship to other smells and refactorings

Long Function is the primary trigger for [extract-function.md](./extract-function.md). It frequently travels with Long Parameter List and Data Clumps: when extraction produces functions that need the same five arguments, those arguments are asking to become a parameter object. It can also be a symptom of a missing abstraction: in agent-assisted code, functions grow long because each new requirement gets appended as another branch, turning the function into a change dumping ground; that is closer to [divergent-change.md](./divergent-change.md), and the fix is to find the variation axis rather than to keep extracting.
