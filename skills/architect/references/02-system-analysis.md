# System Analysis

Taking apart an unfamiliar system from code, configuration, and runtime evidence. Use when inheriting a legacy system, reviewing an existing architecture, understanding a dependency, or scoping ahead of a migration or split.

## Reading a system is design in reverse

Forward design runs constraints → solution → diagram; analysis runs the diagram and code → inferred constraints and tradeoffs. The judgment framework is the same, only the direction flips.

Recognizing the words is not the same as reading the system. Recognizing is seeing a gateway, an orchestration layer, a vector store, GPUs. Reading is answering three questions for every part:

1. Which quality attribute or constraint does it serve?
2. What did it give up?
3. When load grows 100×, does this crack first?

If you cannot answer these three, you have learned the names of the boxes, not the system.

## The four-step method

**① Grasp the essence.** State the business in one sentence; name the two heaviest quality attributes and the single hardest constraint. Everyone sees the features; quality attributes and constraints are the forces that shaped the system into its current shape.

**② See the whole.** Find the soul data flow: the request path the system exists for, followed from entry to storage and back. Tracing one real request (say, a refund query) builds more of the whole picture than reading the directory structure ten times.

**③ Dig out the tradeoffs.** Find two or three judgments of the form "chose X, gave up Y, because constraint Z". Tradeoffs hide in the choice of key components: why a message queue instead of synchronous calls, why reads and writes live in separate stores, why self-hosted instead of a managed service.

**④ Find the fatal spots.** Where is the first scaling bottleneck (which part dies first when load grows a hundredfold), and what is the common anti-pattern (the easiest mistake to make in this system)?

The four steps produce one page of notes, not a full document. The notes' value is forcing you to answer the questions, not filing.

## Gathering evidence from code and configuration

Diagrams go stale; code does not. When analyzing a system, calibrate your picture against repository facts:

- **Entry points and boundaries.** Find system boundaries from deployment configs, route definitions, public interfaces. What is the first stop for external calls, and which deployable units sit inside the boundary.
- **Data flow.** Find real data ownership from schemas, migrations, and data-access layers. Which services write which tables; cross-service table reads usually mean boundary leakage.
- **Dependency direction.** Find dependency arrows from imports, dependency manifests, and service-to-service calls. Bidirectional and circular dependencies are direct evidence of unclear boundaries.
- **Where state lives.** Which components are stateless and scale freely, and which hold state (databases, caches, queues, local disks)—that decides how hard evolution will be.
- **Configuration and infrastructure code.** Deployment units, environment variables, and network policies often reflect the architecture more truthfully than documents.

Runtime evidence matters just as much: logs, traces, and metrics answer "does the drawn path actually run, and how often". Dead paths in code and heavy traffic in monitoring are both invisible to paper analysis.

## What analysis output must separate

- **Facts from inferences.** "This service takes about 200 calls per second, per monitoring" is a fact; "this service is on the critical path, because call volume is high" is an inference with possible alternative explanations (volume inflated by health checks, say). State them separately in the report.
- **What it is from how good it is.** Describe what the system is before judging what is wrong with it. Skipping description and jumping to judgment leaves readers unable to check the conclusion.
- **Design intent from historical baggage.** A strange design may be deliberate (constraints existed at the time) or simply untouched because nobody dared. The way to tell them apart is records (ADRs, commit history, comments); when no record exists, say "reason unknown" explicitly rather than inventing a plausible story.

## Legacy-system specifics

- **Do not read legacy code with disgust as your lens.** The goal is understanding why it survived, not tallying best-practice violations. A live system got something right; find that first.
- **Interfaces are promises.** A legacy system's most precious asset is its stabilized interfaces. List the interfaces external parties depend on; that list is the guardrail for later evolution (see [Evolution and migration](./12-evolution-and-migration.md)).
- **Data is the hardest constraint.** Schema is the hardest part of a legacy system to change; data ownership and lifecycle bound what splits and migrations are feasible (see [Data and state](./05-data-and-state.md)).

## Calibrating later work with analysis results

The end of analysis is not the notes; it is input to what follows:

- To take over development, confirm the fatal spots and anti-patterns first, so you do not fall where others already fell.
- To review (see the topic documents), use the four-step notes as the factual basis, so a diagram-only review does not miss real data flows.
- To evolve (see [Evolution and migration](./12-evolution-and-migration.md)), use the interface list and data ownership to draw the safe boundary of the first step.
- When analyzing AI systems, watch three extra constraints in the quality-attribute and tradeoff columns: cost (every call burns tokens), non-determinism (same input, not necessarily same output), and context (the model's working memory is finite and expensive). Judge whether each part saves money, prevents errors, or manages context (see [AI-era judgment](./ai/01-ai-era-judgment.md)).
