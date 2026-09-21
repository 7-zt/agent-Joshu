---
name: architect
description: Use when architecture work or system design is needed, covering system-level analysis, design, review, technology selection, and evolution.
---

# Architecture

Use this Skill for system-level architecture analysis, design, review, technology selection, and evolution. The model does the primary reasoning; the reference documents supply architecture knowledge, judgment rationale, common tradeoffs, and examples. They do not freeze architecture work into fixed steps.

## Scope

This Skill handles system-level judgment: system boundaries, data and state, quality attributes, failure, scale, and long-term change. It covers five kinds of work: analysis, design, review, selection, and evolution. Boundaries: single-module internal design, coding implementation, and code-level quality review are out of scope; defining product behavior and ranking priorities are out of scope. Both follow their own ordinary processes.

This Skill does not do concrete implementation. Project facts come from the current code and configuration; product behavior comes from product documentation; priority calls belong to the user. The Skill replaces none of these. When recording architecture decisions, follow the current project's recording convention.

## Reference Navigation

Choose documents by the signals of the current question and read only what is needed. Numbering is for directory navigation only; documents are not meant to be read in order.

| Signal | Read First | Often Pair With |
| --- | --- | --- |
| Forming architecture judgment from requirements, constraints, and quality attributes; tradeoff framing | [Thinking and tradeoffs](./references/01-thinking-and-tradeoffs.md) | system-design, technology-selection/principles |
| Taking apart an unfamiliar system: starting from code, configuration, and runtime evidence | [System analysis](./references/02-system-analysis.md) | views, distributed-systems |
| Choosing views and abstraction levels to express boundaries, relationships, and data flow | [Views](./references/03-views.md) | system-analysis |
| Comparing when monoliths, microservices, event-driven, and other styles fit | [Architecture styles](./references/04-architecture-styles.md) | organization-and-ownership |
| State ownership, data lifecycles, storage boundaries | [Data and state](./references/05-data-and-state.md) | consistency, technology-selection/data-stores |
| Deriving a complete, verifiable system design from requirements | [System design](./references/06-system-design.md) | thinking-and-tradeoffs, scaling |
| Recording candidates, tradeoffs, consequences, and re-review conditions | [Architecture decisions](./references/07-architecture-decisions.md) | thinking-and-tradeoffs |
| Constraints from networks, time, concurrency, and partial failure | [Distributed systems](./references/08-distributed-systems.md) | consistency, resilience |
| Consistency models, transaction boundaries, conflict handling | [Consistency](./references/09-consistency.md) | distributed-systems, data-and-state |
| Timeout, retry, idempotency, isolation, and degradation design | [Resilience](./references/10-resilience.md) | distributed-systems, scaling |
| Finding bottlenecks from load evidence and choosing how to scale | [Scaling](./references/11-scaling.md) | data-and-state |
| Splitting, migrating, rolling back, retiring; evolution trigger signals | [Evolution and migration](./references/12-evolution-and-migration.md) | architecture-decisions, organization-and-ownership |
| Team ownership, communication structure, and their relation to system boundaries | [Organization and ownership](./references/13-organization-and-ownership.md) | architecture-styles, evolution-and-migration |
| Trust boundaries, identity and permissions, data isolation, multi-tenant risks | [Security and tenancy](./references/14-security-and-tenancy.md) | data-and-state |
| Uncertainty, cost, and capability boundaries introduced by AI components | [AI-era judgment](./references/ai/01-ai-era-judgment.md) | ai/ai-system-design |
| System boundaries of models, context, tools, memory, and orchestration | [AI system design](./references/ai/02-ai-system-design.md) | ai/01-ai-era-judgment, ai/05-evaluation-driven |
| Turning architecture constraints into AI-executable, verifiable specifications | [Specifications for AI](./references/ai/03-specifications-for-ai.md) | ai/04-reviewing-ai-output |
| Reviewing the omissions specific to AI architecture output | [Reviewing AI output](./references/ai/04-reviewing-ai-output.md) | consistency, resilience, scaling, security-and-tenancy |
| Defining AI system quality with evaluation targets, datasets, and feedback | [Evaluation-driven architecture](./references/ai/05-evaluation-driven-architecture.md) | ai/02-ai-system-design |
| General questions, comparison dimensions, and exit conditions of technology selection | [Selection principles](./references/technology-selection/01-principles.md) | architecture-decisions |
| Constraints, team fit, and maintenance cost of languages and backend frameworks | [Languages and frameworks](./references/technology-selection/02-languages-and-frameworks.md) | technology-selection/01-principles |
| Data model, consistency, and operational cost of data stores | [Data stores](./references/technology-selection/03-data-stores.md) | data-and-state, consistency |
| What caches, message queues, and event systems each solve | [Caching, messaging, and events](./references/technology-selection/04-cache-messaging-and-events.md) | consistency, resilience |
| Coupling, performance, and evolution cost of API and service communication styles | [API and communication](./references/technology-selection/05-api-and-communication.md) | architecture-styles |
| Delivery, elasticity, and operational constraints of deployment shapes and cloud platforms | [Cloud and deployment](./references/technology-selection/06-cloud-and-deployment.md) | scaling, security-and-tenancy |
| How observability and reliability tooling supports failure detection and response | [Observability and reliability](./references/technology-selection/07-observability-and-reliability.md) | resilience |
| AI infrastructure tradeoffs across training, inference, data, and cost | [AI infrastructure](./references/technology-selection/08-ai-infrastructure.md) | ai/01-ai-era-judgment, ai/05-evaluation-driven |

When terminology is unclear, read the [glossary](./glossary.md).

## Evidence Requirements

- Distinguish project facts, assumptions, suggestions, and user decisions, and label each category explicitly in output.
- Base judgments on the current project's code, configuration, and runtime evidence; the reference documents supply general judgment rationale, not project facts. Give project facts as `path:line`, config keys, command output, or observation windows.
- State uncertainty when evidence is missing; never pass generic assumptions off as project evidence.
- Company cases containing numerical claims, product-capability claims that affect decisions and may change across versions, and external research conclusions must cite a primary source with a publication date, product version, or access date. Stable category-level judgments and unverifiable rules of thumb do not need per-item citations; label the latter explicitly as heuristics and do not use them as upgrade triggers. Purely derived conclusions need no external citation.
- For derived conclusions (estimates, capacity reasoning, cost projections), show inputs, formulas, and uncertainty.
- Output distinguishes at least: observed (project evidence), derived from facts, unverified assumption, suggestion, and user decision.
- Citing upstream material marks the provenance of judgment rationale, not the decision itself.

## Output Contract

- Give candidate options with tradeoffs and applicability conditions for each, not a single answer; state the assumptions each judgment depends on.
- Translate technical tradeoffs into business consequences—cost, risk, and time; the user sets priorities.
- Analysis and design output centers on views and boundary descriptions; whether to proceed to implementation is the user's call.

## Sources

The topic map of the reference documents comes from [awesome-architecture](https://github.com/study8677/awesome-architecture/tree/7f43e49b95ad9c255418733738fddab4eb0f6a68) (by JingWen Fan, [MIT license](https://github.com/study8677/awesome-architecture/blob/7f43e49b95ad9c255418733738fddab4eb0f6a68/LICENSE)).
