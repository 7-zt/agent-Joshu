# AI Infrastructure

The five-layer decomposition of the AI stack and its upgrade signals: managed APIs as the default start, gateways, RAG/vector stores, self-hosted inference, training and fine-tuning, and the gatekeeping layer. Use for infrastructure selection in LLM-bearing systems.

## What are you actually self-hosting?

Hearing "AI infrastructure" one thinks of GPUs, vector stores, agent frameworks, model gateways, inference engines, training and fine-tuning, evaluation platforms. But step one is not listing components; it is asking: **are you actually building infrastructure, or just making an AI application?**

For an early product at MVP, the most sensible default is to call managed model APIs, add minimal logging and cost monitoring, and get the business loop running first. Only on clear trigger signals—runaway cost, data that must not leave the domain, missed latency targets, unacceptable vendor single-point risk, deep model customization needs—does sinking down to gateways, self-hosted inference, or GPU pools become worthwhile.

AI infrastructure is not "deeper is more advanced". The deeper you go, the more control you take back and the bigger the bill you accept: cost, capacity planning, failure recovery, security isolation, team operations capability.

## The five layers

| Layer | Components |
| --- | --- |
| Ingress governance | Model gateway, auth, rate limiting, cost accounting, model routing |
| Context | RAG, vector store, document permissions, rerank, citations |
| Inference | Inference serving, GPUs, KV cache, batching |
| Training and fine-tuning | Data versioning, job orchestration, checkpoints, experiment tracking, validation and promotion |
| Gatekeeping | Observability, eval, trace, human approval |

Not all five layers exist from day one. The correct order: **see the risk that cannot be skipped first, then add the layer that answers it**: cannot see cost—add the gateway or usage logging first; retrieval quality caps the answers—add RAG eval first; multiple teams calling models—add the unified gateway; GPU cost exceeding API cost—consider self-hosted inference; a genuine need to change model behavior—only then fine-tuning or training; agents executing side effects—permissions, human review, and audit are mandatory.

## API or self-hosted inference: a cost decision, not a vanity decision

| Approach | Strength | Cost |
| --- | --- | --- |
| Managed model APIs | Fast start, stable operation, little ops, new models on tap | Vendor lock-in, data traverses their path, unit cost may overtake at volume |
| Self-hosted inference | Full control of model, data, cost structure, deployment | GPUs, VRAM, batching, scaling, failures, capacity—all on you |
| Hybrid routing | Cheap models for simple tasks, strong models only for hard ones | Routing policy, evaluation, fallback, cost accounting all get more complex |

The fork is a cost decision, not a vanity decision: it asks four questions: can the data leave the domain? can the managed API meet the latency target? is the call volume big enough that self-hosting is cheaper? can the team operate GPU serving? One yes usually does not justify self-hosting; hitting two or three together is when sinking the infrastructure makes sense.

## RAG, long context, fine-tuning: adding knowledge or changing behavior?

| Route | Solves | Choose when |
| --- | --- | --- |
| RAG | Answers grounded in material retrieved on the spot | Large knowledge base, frequently updated content, citations required, permission filtering needed |
| Long context | Reading a body of material whole in the window in one pass | Limited material volume, one-shot tasks, window capacity sufficient |
| Fine-tuning | Adjusting the model's default behavior, output style, fixed formats | Rigid format requirements, stable domain vocabulary, high-quality samples in hand |

The most common misjudgment: blaming the model for dumbness when retrieval was done poorly, or fine-tuning a "knowledge freshness" problem that RAG should have solved. The test sentence: **knowledge goes through retrieval; only behavior talks fine-tuning.** Need citations, updates, or permissions—get RAG right first.

## Training and fine-tuning: when managed, when self-built

Training infrastructure is not inference's extension; it is another ledger: data pipelines (cleaning, dedup, licensing compliance, versioning—or experiments cannot be reproduced), job orchestration (long-running jobs must be interruptible and resumable), GPUs and interconnect (multi-card training is sensitive to inter-card bandwidth and storage throughput, a different hardware profile from inference), checkpoints and model artifacts (resumable, version-traceable), experiment tracking (hyperparameters, datasets, metrics tied to each run), validation and promotion (offline metrics gate the eval set; the eval set gates the candidate release).

The fork: **when managed fine-tuning (API-provided services) meets the need, default to managed; only when training jobs are frequent enough that a self-built cluster pays off, or data/models cannot leave the domain, or deep customization of the training pipeline is required, build training infrastructure.** Most teams making AI applications never need the latter. Before self-building, also ask: does anyone on the team debug distributed training? How much does one training run cost, and how often do you iterate? These are the same account as self-hosted inference, at a higher threshold.

## Agent frameworks: workflow first, autonomy second

The first question stays the same: can a deterministic workflow solve it? Yes → workflow first (more predictable, testable, auditable); no → agent, but with permissions, budgets, human review, tracing, and eval mandatory.

Agent framework selection focuses on: can tool permissions be tiered? Is human approval supported? Is every step traced? Can budgets and maximum steps be capped? Are context compression and task resume supported?

## The gatekeeping layer is the production threshold

The biggest difference between AI systems and traditional ones is unstable output and drifting quality. Watching only API success rates after launch is not enough: what were the prompt and context? Which chunks were retrieved? What did the model call cost? Did any tool call exceed its permission? Does the final answer cite sources, or fabricate? Did quality regress after a model swap or prompt change?

When the system touches money, user data, or autonomous actions, eval is not "add later"—it is part of the architecture. Without eval, every model swap, prompt change, or retrieval-strategy change is essentially launching blind.

## Selection quick reference

| Question | Start with | Upgrade trigger |
| --- | --- | --- |
| Just validating an AI product | Managed model API plus basic logging | Multiple apps sharing, cost opaque, vendor failures with wide impact—then add the gateway |
| Multiple models/teams calling | Model gateway as the unified entry | When unified auth, rate limiting, billing, failover are needed |
| Answering from private knowledge | RAG plus simple vector retrieval | Retrieval quality unstable, permissions complex, or the knowledge base has grown |
| Vector scale still small | pgvector or single-node vector search | Millions of vectors and up, complex filtering, tight latency—then a dedicated vector store |
| Model call cost high | Model routing, caching, quotas | API cost above total self-hosted cost, or data cannot leave the domain |
| Autonomous actions needed | Deterministic workflow | Steps open-ended, dynamic planning required—then an agent |
| Steady iteration needed | Trace plus a small eval set | Production-grade, money-touching, frequent model swaps—expand to full gates |
| Changing model behavior | Managed fine-tuning service | Training frequent enough that self-building pays, data/models confined, deep customization needed |

## Relationship to other documents

- The full workflow-versus-agent judgment is in [AI system design](../ai/02-ai-system-design.md).
- The eval trio and gates are in [Evaluation-driven architecture](../ai/05-evaluation-driven-architecture.md).
- Vector storage and read-model selection are in [Data stores](./03-data-stores.md).
- Training-data versioning and the eval-set lifecycle are in [Data and state](../05-data-and-state.md).
- The unified selection decision tree is in [Selection principles](./01-principles.md).
