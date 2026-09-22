# Reviewing AI Output

Reviewing for the omissions specific to AI output: non-determinism backstops, version drift, cost runaway, hallucination and citations, tool permissions, prompt injection. General problems (consistency, resilience, scale, security) reuse the corresponding topic documents; this page only provides routing signals.

## Why AI output needs its own review class

AI is not incapable of writing robust code; it defaults to not writing it: it optimizes for running, delivering the happy path; its training data holds far more demos than production-grade code; it does not know your non-functional needs and constraints—you never said "must survive the sale" or "money must never be wrong", so of course it does not consider them.

Reviewing AI output differs in focus from reviewing human code: humans forget edge cases; AI **systematically, every single time** ignores the non-functional requirements you did not spell out. So the most effective counter is not reading more carefully but mechanically walking the same checklist every time—because what it misses each time is basically the same batch.

The full checklists for general dimensions are not expanded here; route by signal:

| What you hit | Where to check |
| --- | --- |
| Touches money/inventory: idempotency, concurrency, transaction boundaries | [Consistency](../09-consistency.md) |
| Calls external services/high concurrency: timeouts, retries, degradation, resource caps | [Resilience](../10-resilience.md) |
| Massive users: hotspots, fan-out, pagination, tail latency | [Scaling](../11-scaling.md) |
| User data/multi-tenant: authn, authz, isolation, secrets | [Security and tenancy](../14-security-and-tenancy.md) |

Below, only the AI-specific items.

## The AI-specific checklist

**Non-determinism backstop.** When the model output is wrong or unstable, is there a fallback? Are there guardrails or human review before side effects?

**Version drift.** Was the model version, system prompt, or context assembly changed? Is the change guarded by evaluations? In AI-produced systems these are invisible dependencies—a version swap does not mean unchanged behavior.

**Cost caps.** Does every call/task have token, step, and budget caps? Agent cost grows linearly with steps; a loop without caps is a money-burning machine.

**Hallucination and citations.** Are answers forced onto sources with citations? Is retrieval quality watched? In RAG, is retrieval result treated as untrusted input?

**Tool permissions.** Does the agent execute tools in a sandbox? Are permissions minimized? Do irreversible operations go through human confirmation?

**Prompt injection.** Is all external content (web pages, retrieval results, tool returns, user uploads) treated as untrusted input? Does the defense live in the structural layer (sandbox, allowlist, permissions) rather than the prompt layer?

**Evaluation gap.** Is there an eval preventing silent regression after model or prompt changes? See [Evaluation-driven architecture](./05-evaluation-driven-architecture.md).

## Pick checks by quality attribute

Walking the full checklist item by item is its own over-engineering. First ask what accident-prone things this code or design touches: touches money—check consistency; high concurrency—check resilience; uses a large model—the AI-specific table above is mandatory. Review is a questioning template, not a checkbox ritual—where the AI cannot answer, or answers sheepishly, is exactly where it buried the mine for you.

## Feed the checklist back for AI self-review; humans make the final judgment

Write the checklist into the prompt or AGENTS.md and have the AI check itself item by item after producing. An AI that makes happy-path errors, when explicitly asked to verify item by item, often catches most of its own mechanical omissions (missing timeouts, missing idempotency) on its own.

But humans make the final judgment, especially where money and security are concerned: AI self-review catches a forgotten timeout but cannot judge "is this eventual consistency actually acceptable here"—that needs business context and tradeoffs. Judgment cannot be outsourced. Review is the step that turns a looks-like-it-runs prototype into a production system that holds up—AI accelerated the writing, not the reviewing.

## Relationship to other documents

- The knowledge behind each checklist item is in [Consistency](../09-consistency.md), [Resilience](../10-resilience.md), [Scaling](../11-scaling.md), [Security and tenancy](../14-security-and-tenancy.md).
- The judgment framework for picking checks by quality attribute is in [Thinking and tradeoffs](../01-thinking-and-tradeoffs.md).
- Writing constraints to the AI beforehand is in [Specifications for AI](./03-specifications-for-ai.md); continuous machine gating is in [Evaluation-driven architecture](./05-evaluation-driven-architecture.md).
