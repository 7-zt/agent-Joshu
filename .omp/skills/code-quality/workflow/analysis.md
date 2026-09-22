# Analysis Mode: Code Quality

Advisory mode. The user is asking _what to do_, not _what is wrong_. No diff to grade. Help reason through a design or refactoring decision and converge on one.

## Trigger

- Design discussion: "how should I structure this?", "where should this behavior live?"
- Pattern choice: "which pattern fits: Strategy or just a function?", "is a Factory worth it here?"
- Refactoring planning: how to break up a module, sequence a safe refactor, or decide whether to refactor at all.
- Paradigm choice: imperative vs functional core, OO vs data-oriented, when a state machine earns its keep.
- Principle application: how DRY, KISS, YAGNI, or SOLID bear on a specific situation.

## Steps

1. Understand the design question and its context: what change is anticipated, what hurts now, what constraints exist. Ask if a key fact is missing.
2. Read the relevant reference documents (`skills/code-quality/references/design-principles`, `design-patterns/`, `refactoring/`, `programming-paradigms/`) matching the topic, so the discussion uses the project's real vocabulary.
3. Present options with tradeoffs. Most design questions have several defensible answers; show the realistic ones and what each costs in change-cost, readability, and complexity.
4. Frame the discussion in terms of principles, patterns, and paradigms where they genuinely apply, but only invoke a pattern once the variation point it manages actually exists.
5. Converge. Recommend an option for _this_ context and explain why, or ask a focused clarifying question. Don't just enumerate.

## Output

Conversational, recommendation-oriented. No rigid finding format. Lay out the alternatives, name the tradeoff that decides it, then recommend. Keep it proportional to the question.

## Stop Rules

- Advisory only. No file modifications.
- Don't force a principle or pattern onto a situation where it doesn't fit; the absence of a pattern is often the right answer.
- Don't recommend abstraction on the basis of similarity alone.
- The user decides. If the discussion turns into real work, suggest fast or full review rather than silently switching.
