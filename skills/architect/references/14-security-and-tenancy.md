# Security and Tenancy

Treating security as structure, not patches: threat modeling, trust boundaries, defense in depth, blast radius, multi-tenant isolation, secret management, supply chain, and compliance. Use when designing systems involving sensitive data, multiple tenants, an external attack surface, or agent tool permissions.

## Threat modeling: systematically thinking about bad things

A newcomer does security by remembering to add things: add a login, add HTTPS, run a scan before launch. That is patch thinking—scattered and reactive. An architect does security by spreading the system out and systematically interrogating every data flow and trust boundary about how it would be attacked.

STRIDE's six questions (Microsoft, 1999): spoofing identity (S, breaking authentication), tampering with data (T, breaking integrity), repudiation (R, breaking non-repudiation), information disclosure (I, breaking confidentiality), denial of service (D, breaking availability), elevation of privilege (E, breaking authorization). Walk the data-flow diagram and interrogate every process, store, data flow, and trust boundary. You need not memorize the letters—remember the six bad things: impersonate you, alter your data, do it and deny it, peek at what is forbidden, knock you down, make yourself admin.

The soul is the **trust boundary**: every time data crosses a boundary (public internet → gateway, gateway → service, service → database), the trust level changes, and bad things almost always happen on boundaries. External input crossing inward (injection), low privilege reaching toward high (privilege escalation), sensitive data crossing out (leakage). Defense resources go precisely on boundaries, not spread uniformly. The gateway boundary mainly defends against spoofing and denial of service; the service boundary against overreach and tampering; the data boundary against wholesale extraction.

Security's structural nature differs from other attributes: performance and availability can launch first and optimize later; security's structural holes are often set at launch and cannot be patched in afterward.

## Defense in depth and zero trust

The castle-and-moat model's fatal assumption is that the internal network is trusted by default. Once an attacker breaches the perimeter (phishing, a vulnerability, an insider), they walk freely inside (lateral movement)—SolarWinds amplified a single breach into total compromise exactly this way. Remote work, the cloud, and the explosion of east-west microservice traffic have collapsed that wall itself.

Defense in depth: never count on one wall; layer the defenses (WAF → authentication → authorization → encryption → isolation → audit), so breaching one layer still leaves the next. Zero trust: cancel the internal-network trust assumption—never trust, always verify—regardless of whether a request comes from the public internet or the internal network, every access re-verifies identity, checks authorization, and encrypts in transit; trust binds to user + device + request context, not to network location. Google's BeyondCorp is the best-known implementation: no company-wide VPN; all applications deployed on the public internet; an access proxy admits dynamically by identity, device state, and resource sensitivity. Zero trust is not convenient—it has friction and overhead—but what it buys is that a single breach no longer equals total compromise.

Least privilege threads through both: every component and every account gets only the bit of permission the work requires, not a fraction more.

## Blast radius

Perfect security cannot guarantee never being breached; the mature security view shifts from "never an incident" to "how far an incident can reach". Isolation cages the cost of one mistake in a small cell: an attacker with one service's permissions cannot reach other services' data; a thief with one tenant's credentials cannot see other tenants.

Blast-radius-shrinking means: least privilege, network segmentation (only necessary ports between services), credential isolation (one key set per service), short-lived credentials (tokens expiring in minutes—theft buys little time). Fault isolation and security isolation use the same structural weapons—bulkheads, rate limiting, and circuit breakers, viewed from another angle, also stop attack propagation: a compromised component firing requests wildly and a faulty component retrying wildly have the same injury shape. The bulkheads built for availability moonlight for security.

## The multi-tenant isolation spectrum

Multi-tenancy is SaaS's foundation; the benefit is cost (shared infrastructure), and the number-one nightmare is tenant crossover: company A's data seen by company B—the most severe, most headline-prone, most customer-losing failure.

Isolation is a spectrum, not a switch; the core tradeoff is cost versus isolation strength: pooled (all tenants share one stack—lowest cost, isolation rests entirely on code discipline) → bridged (partly shared, partly separate—shared gateway, separate stores, say) → siloed (dedicated resources per tenant—hardest isolation and compliance, cost growing linearly with tenants). The data-isolation dimension from soft to hard: row-level (one table, relying on a `tenant_id` column) → schema-level → database-level → physical (dedicated machines/accounts).

**Row-level isolation is the number-one breeding ground for crossover incidents.** The entire isolation rests on every SQL correctly carrying `WHERE tenant_id = ?`. One omission is disaster: a new endpoint forgetting the condition, a cache key missing the tenant prefix (`user:123` instead of `tenant:7:user:123`), an object-storage path using guessable auto-increment IDs, a background job scanning the whole table, an endpoint checking login but not ownership (IDOR). These leaks throw no errors, run fine, and tests usually miss them (developer self-tests hold only one tenant's data). Salesforce is the industrial-grade pooled exemplar: one shared relational store serving 8000+ tenants on a single instance, with the key being that isolation does not rely on developer discipline but on platform-enforced tenant filtering plus metadata-driven design.

The ruler: how much does tenant crossover cost in this business. Low cost (public content platforms)—pool and save money; high cost (healthcare, finance, government)—move toward silos; several times the price is still worth it. **At whichever tier, isolation strength can be negotiated on cost, but one thing is non-negotiable: isolation must be guaranteed by structure, not by human discipline**: the platform layer auto-injects tenant conditions, the ORM applies global filters, and automated tests specifically verify cross-tenant invisibility.

## Secret management

The most valuable things in a system are secrets and credentials—the largest blast-radius category. Three iron laws: central custody, regular rotation, minimal exposure.

The deadliest error is secrets in the repository: once committed, they live forever in Git history, and deleting the file afterward is useless; a repo cloned, open-sourced, or leaked equals keys copied to the world. Scanning bots watch new commits and harvest a mistakenly pushed AWS key within seconds for cryptomining. The structural fix: secrets never enter code; a secret-management service (Vault/KMS/Secrets Manager) manages them, injects them at runtime, and secret scanning runs in CI. Rotation cuts losses on already-leaked keys, short-lived credentials make stolen keys rot quickly, and minimal exposure lets each key open exactly one door. Capital One's counterexample: one SSRF vulnerability plus an over-privileged IAM role (able to access 700+ S3 buckets) = the data of 106 million people leaked—with least privilege in place, that intrusion should have been locked in a small box.

**Any plaintext that can be grepped, committed, or printed into logs should be assumed already leaked.**

## Supply-chain security

In modern software, the code you write yourself may be 5%; the other 95% is dependencies: open-source libraries, base images, CI/CD tooling, build scripts. The vast majority of the attack surface is other people's code. Trust is transitive: trusting a library means trusting all its dependencies, its maintainers, and its build pipeline—any link breached, and poison flows downstream to the whole network.

Two counterintuitive amplification effects. Depth: dozens of direct dependencies can imply hundreds or thousands of transitive ones—Log4Shell spread so wide precisely because countless teams did not know they indirectly depended on Log4j. Automation: a poisoned dependency can be built into artifacts and pushed to production unattended—and SolarWinds went further, compromising the build system itself so the officially signed update was the poison.

Structural fixes: lock versions (no blind auto-upgrades to latest), generate an SBOM (know exactly what you use), scan for known vulnerabilities and suspicious changes, minimize dependencies (unused libraries are free attack surface), reproducible builds (same source must yield the same artifact—poison cannot hide). The xz backdoor's lesson: nearly three years of social engineering infiltrating an open-source project, a backdoor hidden in the release tarball evading code review, discovered by no security scanner—uncovered only because an engineer happened to notice SSH logins running 0.5 seconds slow. "It is a famous open-source library, it should be fine"—that blind trust is exactly the assumption the attackers engineered to exploit.

## Compliance as architecture

Data residency, audit trails, the right to erasure (GDPR's right to be forgotten), data minimization—these are not legal-department items or post-launch switches; they are structural constraints that cannot be added afterward: data residency forces the data tier to partition by region (globally mixed data in one database means that extracting EU users later equals redoing the data tier); the right to erasure is nearly impossible to satisfy after the fact—data scattered across a dozen services, dozens of tables, N backups, also flowing into warehouses and logs—so data ownership must be woven into the structure from day one; audit trails need instrumentation up front; data minimization decides from the start which fields are never collected. Structural constraints like compliance, security, and availability get cheaper the earlier they enter and costlier the later—and past some point, only a redo remains.

## Two new attack surfaces AI brings

**AI-generated code**: models confidently invent package names that do not exist (Lanyi et al., "We Have a Package for You!", USENIX Security 2025: across 16 models, 19.7% of recommended packages did not exist). Attackers pre-register the fake names AI loves to invent and wait for developers to install as suggested—slopsquatting, more insidious than typosquatting because it is industrialized and predictable (the same model hallucinates the same batch of names for similar prompts). AI code also tends to be insecure by default: concatenated SQL, disabled certificate checks, hardcoded secrets, missing auth, wide-open CORS. Governance through structure: verify AI-recommended packages actually exist and are trustworthy before use; security gates (code review/SAST/secret scanning) do not relax because "AI wrote it"; treat AI output as the PR of an untrusted junior contributor.

**Prompt injection**: OWASP GenAI LLM Top 10 (2025 edition LLM01; it also led the prior edition). The root cause is that LLMs take instructions and data through one channel and cannot reliably separate them—malicious text hidden in web pages, retrieval results, or tool returns may be executed as commands. Fundamentally different from SQL injection: parameterized queries cure SQL injection completely, while prompt injection is an inherent LLM property—it cannot be plugged, only layered against. EchoLeak (disclosed by Alekseev, 2025, CVSS 9.3) is the first proven production-grade zero-click prompt injection: one crafted email induced M365 Copilot to read internal files and exfiltrate them—Microsoft's injection classifiers were still bypassed. The iron law: treat all external content as untrusted input; the real hard constraints (sandboxing, least privilege, allowlists, human confirmation for irreversible operations) must live in the structural layer the model cannot reach and injection cannot bypass—not written into the prompt begging it to behave. The prompt is persuasion; structure is constraint. A chat-only model injected can at worst ramble; an agent that can run shells, alter databases, and transfer money does real damage when injected—tool permissions push security from a feature concern to a structural one.

## Relationship to other documents

- The same structural weapons for fault isolation are in [Resilience](./10-resilience.md).
- Storage selection for secrets and sensitive data is in [Selection principles](./technology-selection/01-principles.md).
- Further design of agent permission boundaries in AI systems is in [AI system design](./ai/02-ai-system-design.md).
