# Code Smells

## What a smell is

A code smell is a **surface symptom that suggests a deeper structural problem**, but it is not the problem itself, and it is not a verdict. Kent Beck coined the term deliberately as an analogy to smell: something that makes you stop and look closer, not something that proves anything is wrong. A long function might be a problem, or it might be a clear linear sequence that reads fine. Duplicated code might encode one rule in three places, or it might be three fragments that merely resemble each other today.

This distinction, symptom, not diagnosis, is the most important thing about smells. Treating a smell as an automatic defect leads to mechanical "fixes" that make code worse: extracting functions that did not need extracting, deduplicating code that was not really duplicated, introducing abstractions for variation that never arrives. A smell is an invitation to investigate, and the investigation can legitimately conclude "this is fine."

## The major categories

Fowler and Beck group smells into families. Knowing the family helps you reach for the right kind of fix.

- **Bloaters**: code that has grown too large to handle comfortably. Long Function, Large Class, Long Parameter List, Data Clumps, Primitive Obsession. These accumulate gradually; each addition seems reasonable until the whole is unwieldy. See [long-function.md](./long-function.md) and [primitive-obsession.md](./primitive-obsession.md).
- **Object-orientation abusers**: incomplete or incorrect use of OO mechanisms. Switch Statements that should be polymorphism, Refused Bequest, Temporary Field, Alternative Classes with Different Interfaces.
- **Change preventers**: structures where one change forces many others. Divergent Change (one module changed for many reasons) and Shotgun Surgery (one change scattered across many modules) are the two canonical, and opposite, forms. See [divergent-change.md](./divergent-change.md) and [shotgun-surgery.md](./shotgun-surgery.md).
- **Dispensables**: things whose absence would make the code cleaner. Duplicated Code, Dead Code, Speculative Generality, Lazy Element (a class or function that does not earn its keep: closely related to the thin wrapper, see [thin-wrapper-function.md](./thin-wrapper-function.md)), Comments used to explain bad code. See [duplicated-code.md](./duplicated-code.md).
- **Couplers**: smells of excessive coupling between modules. Feature Envy, Inappropriate Intimacy, Message Chains, Middle Man. See [feature-envy.md](./feature-envy.md).

These categories overlap and a single piece of code can exhibit several. The point of the taxonomy is recall: when something feels off, the families prompt you to name what you are seeing.

## How to triage: is it worth fixing now?

Finding a smell is the easy part. The judgment is whether to act, and the answer is frequently "not now." Run a quick triage:

1. **Is it confirmed, or just shape?** Look past the surface. Is the duplicated code really one rule, or two that look alike? Is the long function mixing abstraction levels, or is it one clear sequence? If you cannot articulate the underlying structural problem, stop here.
2. **Is it in your way?** Smells in code you are actively changing, or about to change, are worth fixing: preparatory and comprehension refactoring pay off immediately. Smells in stable code that nobody touches are usually best left alone; the risk of changing working code outweighs the tidiness gain.
3. **What is the cost of leaving it?** High-risk knowledge duplication (security, money, protocol contracts, schema) is worth fixing on sight regardless of frequency, because divergence is expensive. A slightly-too-long function in a quiet corner is not.
4. **Is there a safety net?** If you cannot verify behavior is preserved, do not restructure yet. See [safe-refactoring.md](./safe-refactoring.md).

The goal of triage is to spend your refactoring effort where it reduces real future cost, not to drive every smell count to zero.

## Smells in agent-assisted development

Agentic coding raises both the speed of code production and the speed at which smells appear. The characteristic problems are not "the code looks non-human" but structural: repeated adapters, thin wrapper helpers, over-wide Protocols, speculative registries, deep mocks, the same domain rule written separately in schema, service, and test fixture. Because the volume is higher, smell detection has to be more active and more deliberate than in traditional hand-written code, but the triage discipline above matters more too, since the temptation is to mechanically "clean up" everything an agent produced.

## Relationship to the dedicated documents

This document is the map. Each dedicated leaf in this directory goes deep on one smell or one transformation: what it really is, the signals that distinguish a genuine problem from a false alarm, when the smell is actually acceptable, and which named refactoring addresses it. When triage says a smell is worth investigating, route to the specific document. The transformations themselves, Extract Function, Inline Function, Move Function, live in [extract-function.md](./extract-function.md), [inline-function.md](./inline-function.md), and [move-function.md](./move-function.md), and the overall discipline of applying them safely lives in [fowler-refactoring.md](./fowler-refactoring.md).
