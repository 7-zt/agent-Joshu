# Observability and Reliability

Deriving the observability stack backward from SLOs: metrics, logs, traces as three kinds of evidence, plus the response chain of alerting, on-call, and runbooks. Use for monitoring-system design, alert governance, and reliability process building.

## Monitoring and observability are not the same thing

Monitoring answers: I knew in advance what to watch—has it crossed the line now? (CPU over 90%, error rate over 5%, queue backlog over 10,000.) Observability answers: I do not know where problems will pop up, but does the system leave enough evidence to follow? (One user's checkout is slow; the request crosses gateway, orders, inventory, payments—where exactly is it stuck? Is it one tenant, one version, one availability zone, or one index?)

Small systems survive on monitoring; distributed systems go blind on monitoring alone. The more services, the longer the call chains, the more frequent the releases, the more you need observability—not more dashboards.

## Derive from SLO, not from tools

Step one defines three things: SLIs (what to measure: success rate, P99 latency, error rate, availability); SLOs (the internal promise: 99.9% of requests < 300ms); the error budget (the allowed failure quota: while unspent, keep shipping; once burned, fix stability first).

This vocabulary turns "is the system stable" from a feeling into discussable numbers. Alerting also derives from SLOs: **only what actually hurts users deserves to wake a human.** High CPU, high memory, many threads are candidate causes; without user-journey impact they should not become a 3 a.m. phone call.

## Three kinds of evidence

| Signal | Answers | Cost |
| --- | --- | --- |
| Metrics | System-wide trends: QPS, error rate, P95/P99 latency, queue depth | Cheap, alert-friendly, but thin on detail |
| Logs | Single-event detail: why an order failed, why auth refused | Rich detail, but costly and noisy |
| Traces | One request's full cross-service path and per-hop timing | Strong distributed localization, but sampling and context propagation need design |

OpenTelemetry's value is decoupling instrumentation from the backend: generate telemetry in a relatively standard way first, and later switching the backend from open source to commercial, vendor A to vendor B, costs little. **Tools can be swapped; instrumentation habits barely can.** Getting the evidence formats right first—trace ids, structured logs, key business metrics—matters more than dashboard color schemes.

## Reliability is not just seeing; it is also closing out

Teams that buy observability tooling without improving reliability miss this: seeing a problem is not handling it. Reliability also needs a response chain: alerting (wake only people who can act) → on-call (who owns the response) → runbooks (what to do first when the alert fires) → incident management (severity levels, communication, escalation, retrospectives) → release governance (gradual rollout, rollback, feature flags, circuit breaking and degradation).

Selection is not just the monitoring backend; it is the incident process. Serious systems at minimum: actionable alerts, an owner per service, runbooks for critical alerts, a retrospective after incidents, and retrospective findings written back into alerts, code, or the platform.

## Alerting: few and precise

Low-quality alerts: CPU high, memory high, disk at 80%, thread count up. These are clues, not necessarily incidents. Better alerts center on user symptoms: login failures → login success rate below SLO; slow checkout → checkout P99 over target for 10 straight minutes; messages not delivering → backlog pushing notification delay past the promise.

Do not alert "the machine feels unwell"; alert "the user is being hurt". Otherwise you grow a noise system, and eventually everyone goes numb to real incidents too.

## Choosing the stack by maturity

Invest by maturity step, no skipping:

- **MVP/small team**: managed logging plus error tracking, uptime probes, a few core metrics. The goal is merely that someone knows when things break and the rough cause can be found.
- **Standard production system**: complete metrics, structured logs, key-path tracing, with SLO alerts and runbooks. The goal becomes locating, responding, and rolling back when users are affected.
- **Multi-service/multi-team**: adopt OTel to correlate metrics/logs/traces, build a service catalog and ownership. The goal is cross-team debugging without shouting for detectives.
- **High-reliability critical path**: SLO platform, canary analysis, synthetic monitoring, incident drills—all in. The goal is catching degradation early, limiting blast radius, shortening MTTR.

Watch the cost: full-retention logs, full-sampling traces, and high-cardinality labels all burn money fast. Observability is not "collect everything" but **leave sufficient evidence for the questions that matter**.

## Relationship to other documents

- The resilience engineering of SLOs, degradation, and circuit breaking is in [Resilience](../10-resilience.md).
- The mechanics of tail latency and fan-out are in [Scaling](../11-scaling.md).
- Observing AI-system quality drift is in [Evaluation-driven architecture](../ai/05-evaluation-driven-architecture.md).
- The unified selection decision tree is in [Selection principles](./01-principles.md).
