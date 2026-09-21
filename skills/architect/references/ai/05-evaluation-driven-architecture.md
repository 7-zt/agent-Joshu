# Evaluation-Driven Architecture

Non-deterministic output cannot be asserted verbatim; its quality distribution can only be measured: eval-set scoring plus statistical gates against regression. Use for quantifying and gatekeeping "good enough" in LLM-bearing systems.

## Verbatim assertion cannot cover non-deterministic output

Traditional assertion stands on determinism: `assert summarize(x) == "the expected sentence"`—binary right-or-wrong, precisely assertable. The LLM pulls that ground away: change the temperature, the model version, or the context, and two outputs differ verbatim while both count as correct—an `assert ==` inevitably false-alarms. Note this does not retire traditional testing: the deterministic parts of the system (refund idempotency, state machines, authentication) have unique right answers and stay with asserts; eval governs only the quality distribution of non-deterministic output.

Worse is **silent regression**: upgrade the model or change one line of system prompt, and answers to some question class quietly worsen—no test turns red; you learn from user complaints. The shift: from "asserting one item correct" to "measuring a quality distribution"—no longer asking whether this one answer is right, but whether the overall quality score over a batch of representative inputs is good enough and has not regressed versus the last version.

## The eval trio

**Eval set**: a batch of representative inputs plus expected points per item. Points/criteria, not verbatim standard answers. Example: the user asks "the shoes I bought last week came unglued—can I return them?" The expected points: cites the warranty policy, gives a clear yes/no, invents no nonexistent policy, appropriate tone—score how many points were hit, never compare verbatim.

**Scoring**: who judges good enough.

| Method | Fits | Cost |
| --- | --- | --- |
| Rule/programmatic checks | Objective criteria (keyword presence, format, citations present) | Cheap and stable; only judges hard criteria |
| LLM-as-judge | Subjective quality (is the answer good, is it relevant) | Flexible, but the judge is itself non-deterministic, fallible, and token-burning |
| Human sampling | Calibrating the other two; backstopping high-value scenarios | Good for defining standards and calibration, but limited by inter-annotator agreement, domain expertise, and cost |

Practice: rules first where rules can judge; LLM-as-judge for the subjective; regular human sampling to calibrate the judge—never blindly trust the model judge; it is also a model that errs (with a preference for long answers, for instance).

**Gates**: running evals is not enough; wire them into CI. Before swapping models, changing prompts, or changing retrieval strategy, CI runs the evals automatically and judges by the statistical conditions below—guarding precisely against silent regression. "Block on any total score below baseline" is too crude: one total can mask regression in a high-risk category, and one randomly low run may be noise. At minimum define:

- Fix model/prompt/data versions and decoding parameters, so the change under test is the only variable;
- Hard thresholds on high-risk categories (money, safety, core business), regardless of the total;
- Tolerance bands, not single lines, on overall metrics;
- Repeat runs with averaged scores or paired comparison for components with randomness (sampling temperature, LLM judge);
- Report effect size and confidence intervals, separating real regression from run variance;
- Calibrate the LLM judge against a human-labeled set and monitor its bias (e.g., the long-answer preference).

## Start small, from real failures

A newcomer hears "eval set" and dreams of thousands of items—then never starts. The correct posture:

1. **Seed from real production bad cases.** Every user complaint and every wrong-answer screenshot is the most valuable sample—they are real failures, not imagined ones. A dozen or two dozen items are enough to start running.
2. **Offline and online, two legs.** Offline eval: a fixed dataset wired into CI, gatekeeping before release. Online eval: sample and score real traffic or shadow-run scoring, gatekeeping after release—the real distribution is always more devious than the dataset.
3. **Keep adding cases.** Every newly discovered failure mode becomes one more eval item, exactly like writing regression tests. The eval set is alive and grows with the system.

Do not wait for the perfect eval set; get the loop running with a rough one first.

## Eval does not replace traditional testing; it adds a layer

The deterministic parts of an AI system still use traditional tests: refund idempotency, state machines, authentication, API contracts—unique right answers, `assert ==` still valid. Eval governs only the quality distribution of non-deterministic output. The two coexist, each covering its span.

The design of caging uncertainty away from side effects pays off again here: the deterministic parts can still be tested with deterministic means.

## Eval's costs and traps

Treating eval as an architectural component means weighing its costs like any component:

- **Money and time.** Every sample makes a real model call, and LLM-as-judge adds another call per scored item. Larger sets and more frequent runs cost more; balance coverage against cost.
- **Judges err.** LLM-as-judge is non-deterministic and biased; calibrate with human sampling and never treat its score as gospel.
- **Overfitting and aging.** Tuning against a fixed eval set for long optimizes for the test; out-of-set samples may not benefit; when the business changes, the old eval set goes stale. Keep it updated—an outdated eval is worse than none.

Eval is the AI system's quality fitness function: what it is to answer quality, fitness functions are to architecture boundaries—turning what you care about into an automated check that fails and blocks CI. The only difference: architecture boundaries can be asserted exactly; answer quality can only be seen as a distribution. Write "good enough" into the eval and wire it into the gate, and only then dare you upgrade models and iterate prompts freely—otherwise every upgrade is a blind bet that nothing got worse.

## Relationship to other documents

- The full account of non-determinism, the root constraint, is in [AI-era judgment](./01-ai-era-judgment.md).
- Shadow runs (the vehicle of online eval) are in [Evolution and migration](../12-evolution-and-migration.md).
- Fitness functions (the automated check of architecture boundaries) are in [Evolution and migration](../12-evolution-and-migration.md).
- The tradeoff framework of coverage versus cost is in [Thinking and tradeoffs](../01-thinking-and-tradeoffs.md).
