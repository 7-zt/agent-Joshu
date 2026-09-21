# AI System Design

Turning the three LLM constraints (non-determinism, context, the cost triangle) and the hard problems of autonomous agents into concrete design: the workflow-versus-agent judgment, brakes on the action loop, guardrails and human review. Use when designing chat products, RAG, agent platforms, and other LLM-bearing systems.

## The first judgment: workflow or autonomous agent

Make this decision before drawing any box—it outweighs all the design that follows. Anthropic's core advice in "Building Effective Agents": **if a deterministic workflow can solve it, do not use an autonomous agent.**

The method: are the task's steps essentially fixed and pre-orchestratable? If yes, use a deterministic workflow (intake → classify → retrieve policy → draft response → execute)—predictable, debuggable, cheap, easy to evaluate; most intelligence needs end right here. If no (the task is open, must improvise, steps vary by situation), use an autonomous agent—and immediately fit it with brakes.

For example, checking logistics, refunding shipping, and changing an address are fixed flows; only the few cases with ambiguous responsibility, multi-party verification, and genuine tradeoffs need an autonomous agent. Make every fixed step explicit and leave only the truly open part to autonomy. Predictability is an engineering virtue.

## Landing the three new constraints

**Non-determinism → evaluation-driven + guardrails + rollback.** Two runs of the same input may take different paths; assertion-style testing fails. Three things: build an eval set of representative inputs plus expected points; run evals in CI before changing prompts, models, or tools (rules + LLM-as-judge), and no release on score drops; catch uncertain outputs before side effects—irreversible actions like refunds go through human-in-the-loop, and low-confidence cases escalate to humans; trace every step end to end, replayable and rollback-able.

**Context → manage it as a memory hierarchy.** An agent running a dozen steps will burst its context. Window (most expensive, fastest—hold only what this step truly needs) → retrieval RAG (fetch policies/history on demand) → long-term memory (persisted across sessions). The core tradeoff—no silver bullet among the three: long context is simple but expensive and the model gets lost in the middle; RAG is precise but retrieval quality must be maintained; fine-tuning changes behavior but stiffens it. Compress or summarize historical steps periodically on long tasks; never let context grow unbounded.

**Cost/latency/quality triangle → routing + caching + hard caps.** Agents burn the most: cost grows linearly with steps, and a dozen-step task equals a dozen model calls. Model routing (small models for simple subtasks; big models only where weighing judgment is needed); caching (repeated policy retrievals, identical subquestions reused); **the hard cap matters most**: per task, at most N steps / at most $X / timeout T—stop beyond and hand to a human; it is both the money-saver and the lifeline against runaway.

## Brakes on the action loop

An autonomous agent is the superposition of traditional distributed hard problems; designing an agent is fitting the brakes one by one:

| Hard problem | What it really is | The brake |
| --- | --- | --- |
| The action loop can spin in place and burn money forever | Load shedding / circuit breaking | Step/cost/timeout caps + repetition detection; stop on breach |
| Tool calls have side effects; multi-step resembles a distributed transaction | Saga / idempotency | Idempotent tools; multi-step actions compensable and rollback-able |
| Long tasks run long, nodes die, state must be recoverable | Partial failure | Checkpoints persisted; resume after interruption |
| Multi-agent collaboration | Distribution + fan-out amplification | Start with a single agent, split only when it cannot hold; control fan-out |
| Prompt injection is the top threat | Security | Tool sandbox + least privilege; external content as untrusted input |
| Gradual evolution from prototype | Evolution | Shadow runs to verify; gradual rollout |

An agent loop without control valves is a runaway machine that burns money on its own and may cause harm. **The soul is not making it more autonomous but the ring of control valves fitted around the autonomy**: step/cost/timeout caps, sandboxing, least privilege, human-review gates, end-to-end tracing. Mature agent products without exception spend a large share of design on braking unleashed autonomy. Capability comes from the model; safety comes from the architecture.

## The ladder of autonomy

Single Q&A → conversation + controlled actions (model proposes, code executes) → deterministic workflow (fixed steps, node-level judgment) → autonomous agent (plans its own next step). Upward, capability grows and the hard problems stack harder: most expensive, slowest, least controllable, most dangerous.

The essence of AI-native system design: **solve the problem at the lowest autonomy possible, and fit brakes on whatever part must be unleashed.** The low-autonomy tiers (model proposes, deterministic code executes) are naturally safe and the default for sensitive actions (payments, refunds); every step up in autonomy must be bought back with corresponding brakes.

## Relationship to other documents

- The theoretical overview of the three new constraints is in [AI-era judgment](./01-ai-era-judgment.md).
- The engineering practice of eval sets and gates is in [Evaluation-driven architecture](./05-evaluation-driven-architecture.md).
- Writing constraints into specifications to feed the AI is in [Specifications for AI](./03-specifications-for-ai.md).
- The full defense line against prompt injection and permission boundaries is in [Security and tenancy](../14-security-and-tenancy.md).
