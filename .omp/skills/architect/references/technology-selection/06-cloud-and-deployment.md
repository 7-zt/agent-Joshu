# Cloud and Deployment

A deployment platform is chosen for its operations model: peace of mind versus control, and whether the team can sustain it. Use for choosing among PaaS/containers/Serverless/K8s, designing deployment strategy, and planning the evolution path.

## You are not choosing machines; you are choosing an operations model

Novices ask "VMs or containers, Serverless or K8s, self-hosted or cloud". Architects ask first: who runs releases? who runs scaling? who handles alerts? when a new version breaks, who rolls back? who manages certificates, secrets, config, logs, metrics, permissions? when something breaks, can the team read the platform?

A deployment platform is not a machine or a console; it is **the entire path from code to live service**: build, config, secrets, release, health checks, traffic switching, autoscaling, logs and metrics, failure rollback.

The more worry-free the platform, usually the less control and the stronger the vendor lock-in; the more controllable, the more it eats team operations capacity. There is no high or low—only whether this complexity is worth paying for now.

## Four steps are a complexity price list, not a maturity ranking

PaaS/managed app platforms are the most worry-free, fitting MVPs, small teams, and standard web apps. Managed container platforms stay worry-free but add container and service boundaries. Serverless fits event-driven, bursty traffic, background jobs. K8s has the strongest control and the steepest platform-capability demand.

Do not read these four tiers as increasingly advanced. A three-person team shipping steadily on PaaS is healthier than self-hosting K8s and repairing the cluster daily; conversely, dozens of services, multiple teams, and complex traffic governance crammed into a simple platform also becomes a bottleneck. Choosing a deployment platform is like choosing transport: a bicycle is best for buying groceries downstairs, a truck is best for moving across the city—the question is not whether the truck is more advanced, but whether you are moving.

## When K8s is worth it

K8s solves not how to run one container but how to manage a flock of ever-changing containers: scheduling, scaling, service discovery, rolling releases, self-healing, resource isolation, declarative configuration.

Signals it is worth it: many services (unified scheduling, releasing, resource governance needed); multiple teams deploying independently (no queuing on each other's releases); complex traffic governance as the norm (gradual rollout, canary, blue-green, regional routing); hybrid cloud / on-prem needs (keeping the deployment model consistent across environments); a platform team exists (someone wraps K8s into an internal developer platform instead of every business team chewing raw config).

If it is just one standard web app + one database + one queue, K8s is mostly burden, not benefit: pre-paying a whole set of complexity—certificates, Ingress, network policies, image registries, cluster upgrades, access control, node resources, observability.

## Serverless limits

Value: on-demand scaling with low cost at low traffic; fits event triggers (transcode after upload, scheduled jobs, Webhook handling); the team manages fewer machines.

Costs: cold starts (the first request after idle is slow); runtime limits (execution time, memory, network, package size); observability and local debugging get harder; vendor lock-in tightens.

It fits short, scattered, event-driven tasks. Forcing a complex long flow into dozens of functions without workflow orchestration, tracing, and retry discipline produces a different kind of unmaintainable.

## Deployment strategy is itself architecture

Evaluating a platform means looking not at whether it runs but at how a bad version ends: health checks (how does the platform know an instance truly serves traffic?), rollback (can a broken version return to the old one fast?), progressive delivery (can traffic shift gradually—canary/blue-green?), config and secrets (separated from code? auditable?), infrastructure as code (live resources versioned, reviewable, rebuildable).

GitOps turns the live target state from clicking a console into versioned, reviewable, rollback-able declarations. A platform that cannot roll back quickly, identify versions, or explain config provenance turns every release into a gamble.

## The steadiest evolution path

| Stage | Shape |
| --- | --- |
| MVP/monolith | Managed app platform + managed database + simple CI/CD |
| Multi-service | Containers + managed container platform + standard logs/metrics/secrets |
| Multi-team | Managed K8s + platform team + GitOps + service catalog + permission governance |
| Heavily regulated / on-prem / hybrid | K8s or private-cloud platform, accepting higher ops cost |

Get the business running first; then converge recurring operational complexity into platform capability; let real pain decide the complexity investment.

## Relationship to other documents

- The organizational basis of platform engineering and cognitive load is in [Organization and ownership](../13-organization-and-ownership.md).
- The signal discipline for upgrade timing is in [Evolution and migration](../12-evolution-and-migration.md).
- The observability stack is in [Observability and reliability](./07-observability-and-reliability.md).
- The unified selection decision tree is in [Selection principles](./01-principles.md).
