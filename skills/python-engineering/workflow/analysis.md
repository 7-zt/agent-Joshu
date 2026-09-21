# Analysis: Python Engineering

Collaborative exploration, not grading. Use this mode when the user wants to _decide what to do_ rather than learn _what is wrong_: brainstorming an approach, designing a mechanism, analyzing how existing code behaves, or planning a refactor. There is no diff to score and no findings list to produce. The goal is a shared, well-reasoned decision.

## Trigger

- "How should I structure this?", "what's the best way to…", "what are my options?"
- Mechanism design: how a cache, a retry policy, a plugin system, or a data model should work.
- Code analysis: explaining how a module behaves, why it is shaped the way it is, where its seams are.
- Refactoring discussion: planning a change before committing to it.

## Preconditions

- Read-only. Analysis never modifies code on its own.
- Gather enough context to reason concretely. Do not theorize about code you have not read.

## Gathering Context

Read before reasoning. The amount of context scales with the decision:

- Project facts: `pyproject.toml` for `requires-python`, dependencies, and project shape. The version floor decides which language features are even on the table.
- The actual code under discussion, plus its callers and tests, so options are grounded in the real structure rather than an imagined one.
- Relevant leaf documents for the mechanism in question (e.g. [match-case](../references/grammar/match-case.md), [type-hint](../references/spec/type-hint.md)) so the tradeoffs you present are the established ones, not improvised.

## Structuring The Analysis

Lead with a recommendation, then show the reasoning. A useful analysis is not an exhaustive survey of everything possible; it is a clear path plus the honest tradeoff.

1. **Frame the decision.** Restate the actual question and the constraints that bound it, version floor, existing architecture, dependency limits, how long the code must live. Surface a hidden constraint if you found one while reading.
2. **Present options that genuinely differ.** Two or three real alternatives, not five trivial variations. For each: what it is, what it costs, when it wins. Use a short comparison table when the options are parallel choices along the same axes.
3. **Recommend.** State which option you would choose and _why_, in terms of the constraints from step 1. A recommendation with a reason the user can push back on is more useful than a neutral menu.
4. **Name the tradeoff.** Every real choice gives something up. Say what the recommended path costs so the user is deciding with open eyes.

## Recommend Versus Ask

- **Recommend and proceed to detail** when the constraints point clearly to one option and the cost of being wrong is low or reversible.
- **Stop and ask** when the decision hinges on information only the user has (deployment targets, team conventions, future plans), when options trade off along an axis only the user can weigh (speed vs. simplicity, flexibility vs. clarity), or when the change is large or hard to reverse.
- Do not invent a requirement to force a clean answer. If the right response is "it depends on X," name X and ask.

## Output

Prose and tables, not a findings block. Match depth to the question, a small design question gets a few paragraphs, a structural decision gets options and a recommendation. End with the concrete next step, and only move to implementation when the user agrees.

## Stop Rules

- Do not modify code; analysis is read-only until the user accepts a plan.
- Do not run commands that write files, create `.venv`/cache, or alter the lockfile.
- Do not collapse a genuine "it depends" into false certainty.
- Do not pad with options you would never recommend; three real ones beat seven filler ones.
