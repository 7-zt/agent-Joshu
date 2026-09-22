# Glossary

These terms carry specific meanings in this Skill. Use the routing table in [SKILL.md](./SKILL.md) when a term needs exact syntax, configuration, or examples.

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

## Language mechanisms

**Context manager**

An object used by `with` or `async with` to pair setup with guaranteed teardown when the block exits.

**Decorator**

A callable that replaces or wraps a function or class at definition time.

**Structural pattern matching**

`match` and `case` syntax that selects behavior by the shape and contents of a value and binds names from the matched parts.

**`ExceptionGroup`**

An exception that contains several independent failures and allows `except*` to handle matching members while the rest continue to propagate.

## Type system

**Type narrowing**

A control-flow proof that gives a value a more specific type within a branch.

**`Protocol`**

A typing construct that defines structural subtyping through required members rather than explicit inheritance.

**Generic**

A function or type parameterized over types while preserving relationships among its inputs, outputs, or contained values.

**Type alias**

A reusable name for a type expression. It does not create a distinct runtime type.

## Testing

**Fixture**

Setup data or a resource that pytest manages and supplies to tests by name.

**Parametrization**

Running one test body against several explicit sets of inputs and expected results.

**Marker**

Metadata attached to a test that pytest uses for selection or to declare properties such as async execution.

**Test discovery**

The rules pytest uses to locate test modules, classes, and functions.

**Import mode**

The strategy pytest uses to make test and application modules importable during a test run.

**Branch coverage**

Whether tests execute each control-flow branch, not merely each source line.
