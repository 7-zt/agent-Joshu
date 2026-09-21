# AI-era Judgment

Two fundamental changes AI brings to the architect's work: implementation getting cheap (vibe coding) and LLM systems as a new species. This document is the overview, giving the judgment baseline of "what changed, what did not"; the concrete design constraints of LLM systems are in [AI system design](./02-ai-system-design.md).

## Two shifts happening at once

Shift A: AI changed "how we build". Natural language to code—implementation collapsed from a scarce craft into seconds of generation. Shift B: AI brought a new species of "what we build". The LLM itself became a core component of a class of systems: chat products, RAG knowledge bases, agent platforms, inference services.

The combined core claim: **implementation gets ever cheaper, judgment gets ever more valuable.** When AI produces running code in seconds, the moat is no longer "can write" but "can judge"—judging, before acting, what this system should look like, where it will die, and what is being traded for what.

## Vibe coding amplifies everything, including architectural errors

Simon Willison's distinction: not all AI-assisted coding is vibe coding—the term specifically means **accepting AI-produced code without review**. For toys and prototypes it is brilliant; pushed straight to production, it hands users an unread house to live in.

The dangerous mechanism: AI accelerated output without accelerating judgment proportionally. In the traditional era the bottleneck was "writing"; now the bottleneck has moved entirely to "thinking it through". "AI writes fast" equally means "architecture goes wrong fast, wrong bigger, and debt piles faster". AI defaults to happy-path code: it runs a demo, but there are no timeouts, no retries or idempotency, no degradation or isolation, no thought of sharding or hotspots, no consideration of prompt injection. The prototype-to-production gap has never been so easily masked by "it looks like it runs".

The correct posture is not refusing vibe coding but using it with judgment: vibe freely on toys and prototypes—validating ideas as fast as possible without over-engineering; on production systems, vibe the draft and close with judgment, interrogating the AI output: is the data consistent across the system, what happens on failure, where does it die at scale, can it evolve, where are the security boundaries. Feed judgment to the AI: write architectural constraints and quality targets into memory files like `AGENTS.md`, turning judgment into guardrails the AI keeps respecting.

## Three new constraints of LLM systems

**Non-determinism.** Traditional systems stand on deterministic ground: same input, same output—precise assertions, reproducible bugs, and regression tests all depend on it. The LLM pulls that ground away: ask the same question twice, and sampling randomness, model-version changes, or context changes may yield different answers. The playstyle shifts from "asserting one right answer" to "measuring a distribution with an eval set and scores": prepare representative inputs, score with rules or LLM-as-judge, run evals in CI, watch for score drops. See [Evaluation-driven architecture](./05-evaluation-driven-architecture.md).

**Context engineering.** The LLM's context window is its working memory—finite and billed by the token. Fitting exactly enough information into a finite, expensive window is the core craft of LLM systems. In essence a new memory hierarchy: context window (most expensive, fastest) → retrieval RAG (fetch on demand) → long-term memory (persisted across sessions). Stuff too much and it gets expensive and "lost in the middle"; stuff too little and it answers without grounds.

**Cost/latency/quality triangle.** Strong models are high-quality but expensive and slow; weak models are fast and cheap but quality-discounted—always a position choice inside the triangle. Cost is a first-class citizen: every call burns tokens, and resident agents burn 24×7. The countermeasures: model routing (small models for simple tasks), caching, batching, budget caps.

## Agentic systems stack every traditional hard problem

Autonomous agent systems are not a new domain; they are a superposition of traditional distributed-system problems: the action loop needs step/cost/timeout caps against runaway burning (load shedding and circuit breaking); tool calls need idempotency, and multi-step tasks resemble a distributed Saga (consistency); long tasks run long, nodes fail, dead-or-alive is indistinguishable, and state must be recoverable (partial failure); multi-agent collaboration is distribution plus fan-out amplification; prompt injection is the top threat, tool permissions need minimizing and sandboxing (security); agents as virtual colleagues reshape team division (organization).

That is why Anthropic repeats that line: **if a deterministic workflow can solve it, do not reach for an autonomous agent.** The stronger the autonomy, the harder the hard problems stack. The soul of mature agent products lies entirely in fitting brakes onto unleashed autonomy—and the brakes' design principles are exactly traditional resilience, consistency, and security engineering.

## What has not changed

The thinking framework of requirements → constraints → quality attributes → tradeoffs still holds for LLM systems; the quality-attribute table merely gains rows for cost/latency/quality/evaluability. There is no best architecture, only the most fitting: long context or RAG, strong model or weak model, workflow or agent—all tradeoffs, no silver bullets. Ask why before how: AI can answer "how" in seconds, but "why this one, and at what cost" still has to be asked by a human.

AI commoditized implementation and pushed the scarcity of judgment to a historical high. A person who can naturally ask, of every technical choice, "why this one, what does it cost, where does it die" is not replaced in the vibe-coding era—they become more irreplaceable than ever.

## Relationship to other documents

- The full design constraints of LLM systems are in [AI system design](./02-ai-system-design.md).
- The engineering practice of evaluation-driven development is in [Evaluation-driven architecture](./05-evaluation-driven-architecture.md).
- Agent permissions and prompt-injection defense are in [Security and tenancy](../14-security-and-tenancy.md).
- The general framework of judgment (the AI-independent part) is in [Thinking and tradeoffs](../01-thinking-and-tradeoffs.md).
