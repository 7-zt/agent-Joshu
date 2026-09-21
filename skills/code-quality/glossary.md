# Glossary

These terms carry specific meanings in this Skill. Use the routing table in [SKILL.md](./SKILL.md) when a judgment needs examples or fuller criteria.

## Review language

**Fact**

Something directly observable in code, configuration, tests, or runtime behavior.

**Inference**

A conclusion drawn from facts that may still have another explanation.

**Judgment**

An evaluation of evidence against a stated engineering concern or tradeoff.

**Recommendation**

The smallest sufficient action proposed for a supported finding or a clearly framed decision.

**Finding**

A supported concern that states the evidence, impact, and recommendation. A stylistic preference alone is not a finding.

**False positive**

A plausible concern that does not apply after the surrounding constraints or intent are considered.

## Design boundaries

**Change boundary**

The module or component that should absorb a particular kind of expected change without forcing unrelated edits elsewhere.

**Semantic boundary**

A function, type, or module boundary that names and enforces a real concept rather than merely forwarding work.

**Variation point**

A dimension of behavior that is known or reasonably expected to change and may justify indirection.

**Deep module**

A module whose small interface hides substantial implementation detail or policy.

**Shallow module**

A module whose interface exposes nearly as much complexity as its implementation.

## Refactoring and testing

**Knowledge duplication**

The same rule or decision encoded in more than one place. Similar text alone is not duplication.

**Wrong abstraction**

A shared abstraction that combines code whose reasons or directions of change differ.

**Thin wrapper**

A forwarding function or type that adds no policy, semantic name, isolation, or stable interface.

**Change-detector test**

A test that fails on behavior-preserving refactoring because it asserts internal calls or structure.

**Test seam**

A boundary where a dependency can be controlled or replaced so behavior can be tested deterministically.
