---
name: grill-me
description: Turn an incomplete idea or existing plan into shared understanding and an action-ready specification through sustained, evidence-first questioning. Discover goals, scenarios, preferences, and assumptions; keep a durable record and global question numbering; work by dependency; report qualitative readiness.
disable-model-invocation: true
---

# Grill Me

Grill turns an incomplete idea or existing plan into a specification both sides read the same way. Continue discovering requirements, facts, preferences, and boundaries until the finish condition holds or the user ends the review.

Use **requirement discovery** to establish what to solve, for whom, in which situations, within what scope, and how completion is judged. Use **preference elicitation** to learn which workable direction the user wants and why. Run both as a collaborative interview: follow the user's vocabulary, ask about concrete cases, and seek shared understanding rather than flaws, questionnaire completion, or agreement with your recommendation.

## Set the starting point

Identify the starting point:

- For an idea, discover requirements before approaches.
- For a plan or design, confirm its requirement basis before examining evidence, trade-offs, and boundaries.

Never jump from a vague idea to a solution or from a detailed plan to implementation.

Throughout the review, distinguish the described **problem or opportunity**, the **intended outcome**, and the current **candidate requirement or intervention**. A request may contain several requirements; split only parts that could be independently retained, changed, deferred, or excluded, and refine the mapping as interaction adds evidence and context.

For each sufficiently understood part, check the problem's factual basis, whether the candidate serves the outcome, and whether existing behavior or a simpler option already suffices:

- If they align, retain the branch and discover its detail.
- If the problem is real but the candidate is misaligned, retain the problem and outcome, explain the mismatch, and find a better candidate for the user to confirm, modify, or replace; check each alternative the same way.
- If support is partial or missing, retain what matters and narrow, defer, exclude, or research the rest; do not let an unconfirmed branch drive an approach.

Pure preference discovery and exploratory goals need no checkable problem premise. Confirm their desired experience, scope, and finish condition instead. Challenge checkable premises, causal claims, and problem-to-requirement mappings, not the user's goals or preferences. Reassess affected branches whenever later interaction changes the judgment, stating what remains, what changed, and the impact.

Establish a baseline of the goal, users, main situations, scope and non-goals, constraints and authorization, named artifacts and prior decisions, experience and preferences, success and stop criteria, and what is sufficient to act. Carry each consequential gap until it is answered, safely defaulted, deferred with a trigger, or excluded; assumptions may guide research but never substitute for an unstated requirement.

Build a stable provisional review map for the dimensions that can affect the goal: requirements and situations, experience and preferences, alternatives and trade-offs, assumptions and dependencies, execution and support boundaries, failure and fallback, acceptance and risk. Mark irrelevant dimensions not applicable; attach ordinary detail below existing branches and revise the top level only for a genuine new major branch or agreed scope or finish change.

Classify information as fact, inference, user experience, preference, decision, pending evidence, or risk, and map dependencies. The **frontier** contains items whose prerequisites are settled and that can advance without guessing. Work in the order orient, discover intent and boundaries, verify facts, decide, audit, returning upstream when an answer changes the basis. This is a sequencing lens, not another structure or a fixed round count; continuously turn confirmed answers into requirements, boundaries, or acceptance criteria.

## Research facts, ask for what only the user knows

Resolve checkable project, code, upstream, and historical facts from evidence; ask the user directly for goals, lived experience, examples, terminology, preferences, authorization, and risk acceptance. Before each substantive question, research relevant checkable facts with effort proportional to their impact. Evidence-first applies to facts, not to the user's unexpressed mind.

Use this evidence order:

1. the user's current explicit statements;
2. user-named artifacts and existing project decisions or documentation;
3. code, tests, runtime results, and direct local evidence;
4. authoritative upstream documentation and source;
5. other external sources;
6. model inference.

Read every relevant user-named artifact before questioning what it establishes; inspect named directories for material relevant to the candidate question. To challenge an existing decision, present the conflicting evidence, affected conclusion, and recommended revision.

Queue a candidate question only when:

- plausible answers would materially change the need, scope, success criteria, preference, conclusion, approach, action, commitment, risk acceptance, or go/no-go decision;
- evidence cannot settle it because user experience, preference, meaning, authorization, or judgment is required;
- it cannot be safely defaulted or deferred in the current decision horizon;
- it is unanswered and its prerequisites are settled.

Route everything else: record what evidence settles; research discoverable facts; mark unavailable evidence and its effect; omit immaterial items or defer them with a real trigger. Keep required artifacts, validation, and an agreed next phase out of the queue unless their outcome or scope still contains a material choice. Stop research when more search is unlikely to change the judgment, current evidence supports the decision level, or the unavailable gap and impact are recorded.

Adopt and group **operational defaults** that are low-risk, reversible, and direction-neutral. Recommend and confirm **directional defaults** that choose a goal, experience, architecture, quality priority, or risk posture. Never hide a material decision in a default block.

Rank ready questions by their effect on need and direction, cost and reversibility of error, downstream work unblocked, and uncertainty or time sensitivity. Ask from the frontier; hold dependent questions.

## Keep a durable record

Maintain a concise, append-oriented record in the established task or material location. Use a supplied file path only when the user identifies it as the record output, not the subject or reference material. Confirm an existing record belongs to this review; read it before appending and preserve its history. If no location is established, recommend a concrete path, using `grill.md` unless the user chooses another name, and confirm it. A read-only review of the project does not cancel existing authorization to save review materials. If the user prohibits recording or no location permits writing, keep the state in the current review context and state the storage limitation.

The no-record exception changes storage only; keep global `Q` numbering and all other review behavior.

Record location and interaction mode are operational coordination, not numbered questions. When both are pending and structured `ask` exists, ask them together. Continue research and substantive discussion while the location is pending. Default to ordinary prose when no interaction preference is stated.

Keep:

- the baseline, finish condition, review map, and sources;
- the requirement contract: problem or opportunity, outcome, candidate requirements, situations, non-goals, constraints, acceptance criteria, and branch changes;
- the preference ledger: values, rejections, experience, reasons, and applicability;
- material facts, inferences, pending evidence, risks, questions, recommendations, decisions, corrections, defaults, deferrals, progress, and effects.

Keep the baseline, evidence, direct conclusions, and first question batch in the review state. After each response, add its summary and resulting decision or open status before the next batch. When a record location is authorized, persist this state promptly, including the actual text and global number of each question before presenting its round; question numbers or references to the conversation alone are not a recoverable record. Otherwise retain the state in context without claiming a requested record has been delivered.

Append new entries rather than revising history. Edit earlier text only to repair corruption or at the user's request. When a conclusion changes, append the old conclusion, correcting evidence, replacement, and impact. Exclude raw tool output, search noise, whole referenced artifacts, and hidden reasoning. Research and record maintenance belong to the review, not implementation of its subject.

## Ask in rounds

Ask at most three independent, highest-value ready questions per round: three when three qualify, fewer when fewer do or answers are dependent. There is no round limit; never lower the bar to fill one.
Before invoking `ask` or presenting any prose question round, write or append every question's exact user-facing text and global `Q` number to the authorized record. Treat an empty question section, number-only placeholder, or conversation reference as a failed persistence step and repair it before asking.

Give each new substantive topic a globally increasing `Q` number, continuing after the record's highest number across rounds, compaction, recovery, and reloads. Clarification or revision keeps its number; only a new independent topic gets a new one.

Display the number on every user-facing substantive question, including questions introduced by research summaries, progress updates, or audits. A number only in the record, a local list number, or a bare `Q` is insufficient. Operational coordination and finish confirmation remain unnumbered.

Use two question types:

1. **Discovery** elicits goals, situations, experience, preferences, terminology, and success criteria. Explain why the answer matters without presuming or recommending it.
2. **Decision** settles approaches and trade-offs. State relevant facts or judgment, recommend with reasons and material impact, then ask openly.

Prefer concrete probes: past satisfying or disappointing examples, the first real-use scenario, a failure counterfactual, a trade-off comparison, or the boundary where a default stops. Keep one independently answerable topic per number; tightly coupled context may share one, while separately decidable or dependent matters do not.

When several materially different directions are viable, lead with the preferred one and present real alternatives and trade-offs as non-exhaustive. The user may accept, modify, replace, defer, skip, or request explanation; invent no options and impose no coded response format.

Prefer ordinary prose for substantive rounds so answers, custom context, side thoughts, and corrections can share one response. Structured `ask` suits bounded questions whose options cover the main directions and can be answered independently; it often works well for record location, authorization, phase or action choices, and interaction mode. Before the first substantive question, offer only two modes: prose throughout, or `ask` where suitable. Until the user chooses the second mode, do not use `ask` for substantive questions; open questions always use prose. This unnumbered preference may change but never overrides the suitability criteria.

Wait for each answer before asking what it unlocks. If the user follows up, challenges, doubts, corrects, or goes deeper, pause the queue and settle that discussion. Exploration is not agreement; establish the basis of a new direction before revising a question or opening another.

## Process every response before continuing

After each response, in order:

1. separate what was accepted, modified, challenged, deferred, skipped, or left open;
2. append its summary, rationale, status, and effects, or retain the same state under the no-record exception;
3. update reusable requirements, preferences, the review map, dependencies, and frontier;
4. name superseded conclusions and downstream effects, then reopen affected branches;
5. research newly exposed checkable facts;
6. select the next ready round or begin the audit.

Reuse a confirmed preference with its basis instead of asking again. When answers conflict, ask where each applies rather than overwriting history.

Check alignment when the user:

- corrects or reinterprets the problem;
- changes, combines, or works around offered options;
- answers outside the current framing;
- introduces a new goal, constraint, or priority;
- gives several local answers that conflict with the current inference.

A single rejection of a recommendation is a normal trade-off, not a trigger. When several answers conflict with the inference without a shared reason, state the prior working assumption and which answers challenge it before continuing; merely summarizing decisions is insufficient.

Surface only assumptions the user has not stated, evidence has not settled, and whose failure would change the goal, scope, approach, evaluation, or later questions. If the response explains the difference, update state and continue; if a material cause remains unclear, pause the queue, state the current understanding and key assumptions, and invite correction. A signal prompts a check, not a judgment that the user is wrong.

## Report global progress

Report one rough global percentage as a qualitative judgment of overall finish and action readiness. Re-estimate it from the stage, top-level map, upstream questions, pending evidence, and readiness of requirements and approach; let unresolved high-leverage dependencies dominate.

Use these anchors as judgment guides, not a formula:

- at most about 20% until the first substantive answer;
- normally at most about 30% while goal, main situations, or success remain unclear;
- normally at most about 60% while direction exists but key preferences, boundaries, or acceptance criteria rely on assumptions;
- about 80% when consequential decisions and the action specification are largely complete, with a named blocker or audit left;
- about 90% when only final blockers or the shared-understanding audit remain;
- 100% only after the audit and finish condition pass.

Use coarse values, normally tens and occasionally fives, prefixed by "about" or equivalent. State what most advances and blocks the estimate. Never derive it from counts of questions, decisions, materials, tasks, checkboxes, or branches; replace any unclear or item-based percentage with a fresh global judgment. Prior qualitative estimates may show trend but never determine the current value.

A progress update gives the stage (orientation, discovery, verification, decision convergence, action specification, or final audit), percentage and rationale, completed top-level branches, remaining high-impact branches and dependencies, pending evidence, deferrals, and exclusions. If requirement clarity and approach readiness differ, report separate qualitative judgments without extra percentages or averaging.

Update after the initial map, about every five completed rounds, after a major branch or scope change, on request, and before finishing. Include confirmed decisions, evidence and inferences, corrections, open or deferred items, and the next frontier. Skip an update while one question remains under discussion; otherwise it may accompany the next batch.

## Audit shared understanding and finish

Before proposing to finish, ensure each relevant top-level branch is settled by evidence or a user statement or decision; safely defaulted with conditions, risk, and reversibility; deferred with a trigger and no current blocker; or excluded as not applicable.

Reverse-audit for unverified assumptions or pending facts treated as settled; missing failure, fallback, reversibility, support, or acceptance paths; conflicts among requirements, preferences, decisions, evidence, or branches; and hidden directional defaults. Research or ask about any material gap. Round counts and checkpoints are not finish conditions; omit or safely defer immaterial detail.

Present a correctable shared-understanding summary covering:

- problem, outcome, and main situations;
- scope, non-goals, constraints, and acceptance criteria;
- key experience, preferences, trade-offs, and reasons;
- chosen direction, evidence, inferences, and accepted risks;
- defaults, deferrals, open items, and triggers.

The review is complete only when it can state what will be done, why it matches expectations, and how success will be verified; an approach summary alone does not qualify. If no material question remains, show covered branches, active defaults, deferrals, and uncertainty, then ask whether to finish or dig deeper. If the user continues, re-examine the map and raise the next substantive gaps yourself.

Finish when consequential matters are settled or safely deferred, the summary is confirmed, and the finish condition holds. Close with global readiness, decisions, evidence and inferences, accepted risks, deferrals, open items, and the next step.

The user may skip, accept, defer, revisit, or end at any time. On early finish, report readiness and blockers. Do not implement the subject or take side effects before final confirmation unless the user asks to decide and act in parallel; then proceed without extra per-action gates. Research and record maintenance may continue.
