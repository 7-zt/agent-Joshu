# Specifications for AI

Writing architectural constraints into persistent forms that load automatically when the runtime supports it and that machines can enforce. Use for holding architectural boundaries in AI-assisted development (vibe coding, agent coding): decision records, AGENTS.md-style rule files, and the layered placement of fitness functions.

## Judgment not written down equals none

The code may come from AI, but the specifications, constraints, and acceptance criteria are human—so how do you hand them to the AI? Saying "remember to add idempotency" in chat does not work: remembered this turn, forgotten next turn after context compression; a new session starts from zero; a new colleague knows nothing at all.

Worse, AI defaults to the happy path: unless you explicitly write that refunds must be idempotent and double-charges prevented, it will not, producing code whose demo runs and whose production explodes. Constraints that are verbal, one-off, and memory-dependent amount to nonexistence in AI collaboration. Architectural constraints must land in persistent forms, auto-loaded when the runtime supports and is configured for it (otherwise injected explicitly by the caller), and ideally machine-enforceable.

## The specification pyramid

Constraints layer by enforceability, harder and more unavoidable further down:

| Layer | Vehicle | What it constrains | Who reads it |
| --- | --- | --- | --- |
| Decision records | Documents in the project's existing format | Why it was decided, the tradeoffs | Humans + AI (understanding intent) |
| AGENTS.md-style rule files | Standing rules at the project root | Do / do not | AI (auto-loaded when the runtime supports and is configured) |
| Fitness functions / lint / CI | Automated tests | Red lines (violations block) | Machines |

Each layer governs its own span; none can be dropped: some constraints can only be understood by humans (why dual-write was chosen back then)—decision record; some can be stated in natural language for the AI to keep respecting (refunds must be idempotent)—AGENTS.md; some can be verified precisely by machines (the domain layer must not import the web layer)—CI check. **Whatever can sink one layer lower must not stop on the upper layer**—documents rely on self-discipline; CI enforces.

## Writing a good rule file

`AGENTS.md` / `CLAUDE.md` at the project root, auto-loaded every conversation when the runtime supports and is configured for the mechanism, is the AI's long-term memory. Most people write correct-sounding emptiness:

```
- Write high-quality, maintainable, scalable code
- Follow best practices
- Mind performance and security
```

The AI can do nothing with these—how high is high quality? Whose best practices? The useful form is specific, executable, carries the why, and includes counter-examples:

```
## Data and consistency
- Any interface touching money (charges, refunds) carries an idempotency key;
  a repeated request returns the previous result, never executes twice.
  Background in ADR-003.
- ❌ Never hand the payment API directly to the model; the model's output stops
  at refund proposals—the deterministic refund service does the acting.

## Resilience
- All external calls (model APIs / third parties) must set timeouts; retry with
  backoff only for recoverable errors, within idempotency, time-budget, and
  retry-budget limits. Rationale: dependencies will misbehave; but permanent
  errors, auth failures, exhausted quotas, and calls with non-idempotent side
  effects must not be auto-retried.

## Boundaries
- The domain layer must not import the web layer / framework. CI fails on it.
```

Five disciplines:

1. **Specific enough to execute.** Not "mind security", but "all external input is validated before storage; user content is untrusted input (prompt injection included)".
2. **Carry the why.** Give reasons like an ADR—only when AI and humans know the reason will they refrain from deleting a rule that looks redundant.
3. **Give counter-examples (❌).** Stating what is forbidden works better than stating what should be done; this is exactly where you plug the AI's happy-path default.
4. **Short and sharp.** A rule file is standing context cost, billed by the token. Write the few highest-frequency, most-violated rules; do not write a novel.
5. **Evolve with the code.** An outdated rule is worse than none (it actively misleads the AI); when the rule changes, change it.

Every "chose A, gave up B" tradeoff made in design, every decision record written, whatever you want the AI to keep respecting, should be distilled into a rule-file entry. AGENTS.md is the architecture boundary written for the AI.

## If a machine can enforce it, do not settle for a document

The pyramid's bottom layer is the hardest. Constraints sort by machine-verifiability into their destination:

| Constraint | What it becomes |
| --- | --- |
| Domain layer decoupled from the framework | CI dependency check blocks on violation |
| Refund interface requires idempotency | Rule in the rule file; contract test fails on a missing idempotency key |
| Model calls must go through the abstraction layer | Dependency check blocks on direct provider connections |
| p99 ceiling of 200ms | Performance test fails on breach |
| Why RAG instead of fine-tuning | Decision record (human-readable only, not machine-verifiable) |

The AI faithfully executes the constraints you write down, and faithfully ignores the ones you do not. Turn reminder-dependent constraints into red-light-guaranteed ones—the CI gate does not care whether the code was committed by a human or an AI; it blocks equally.

## Specification is architecture

In the AI era, writing constraints clearly, where the AI can read them, is not documentation chore-work; it is core architecture work itself. **The constraints you write = the boundaries of AI output. Write them vaguely, and the AI decides for you in the vague places, always picking the easiest happy path.** The architect's judgment, through the interface of specification, becomes the behavioral constraint on AI.

## Relationship to other documents

- How to write decision records (ADRs) is in [Architecture decisions](../07-architecture-decisions.md).
- The full practice of fitness functions against architecture rot is in [Evolution and migration](../12-evolution-and-migration.md).
- Specifications govern before the fact; reviewing AI output after the fact is in [Reviewing AI output](./04-reviewing-ai-output.md).
