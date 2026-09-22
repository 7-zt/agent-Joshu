# Builder

## Intent

Separate the construction of a complex object from its final representation, so the same construction process can be driven step by step, validated along the way, or reused to produce different outputs.

## Problem it solves

Some objects are awkward to create in a single constructor call: many optional parameters, construction that happens in stages, inputs that arrive from several sources, or validation that depends on combinations of fields. Stuffing all of this into one constructor produces long parameter lists, telescoping constructors, and validation logic tangled with assignment. Builder gives the assembly process its own named home where it can be tested and reused.

## Structure and participants

The classic form has a **director** that drives a sequence of steps against a **builder** interface; **concrete builders** accumulate state and produce a **product**. In practice the director often collapses into a plain function, and the builder is whatever accumulates the partial state.

## When to use

- The object has many optional parameters or several valid construction shapes.
- Construction proceeds in stages, with intermediate validation between them.
- The same construction process must yield different representations (HTML, PDF, JSON): the canonical Builder justification.
- The assembly logic itself is worth naming, testing, and reusing independently of the product.

## When NOT to use

- A record with named fields and defaults already says it clearly. A fluent builder over a simple value object is pure ceremony.
- A schema or model type already gives you validated construction from raw data.
- The builder hides a pile of mutable state where call order matters but isn't enforced: that's harder to reason about than a single constructor.

## Failure modes

- A fluent builder that can produce a half-initialized product if `build()` is called before required steps run. Validate in `build()` or make required fields constructor arguments.
- Mutable builder state shared or reused across products, leaking one build into the next.
- The builder duplicates the product's invariants instead of delegating to the product's own validation, so the two drift apart.

## Rust example

In Rust, a builder can accumulate construction options through consuming chainable methods, then produce the final value with `build()`:

```rust
struct RequestBuilder {
    endpoint: String,
    timeout_ms: u64,
    retries: u8,
}

impl RequestBuilder {
    fn new(endpoint: impl Into<String>) -> Self {
        Self {
            endpoint: endpoint.into(),
            timeout_ms: 1_000,
            retries: 0,
        }
    }

    fn timeout_ms(mut self, value: u64) -> Self {
        self.timeout_ms = value;
        self
    }

    fn retries(mut self, value: u8) -> Self {
        self.retries = value;
        self
    }

    fn build(self) -> Request {
        Request {
            endpoint: self.endpoint,
            timeout_ms: self.timeout_ms,
            retries: self.retries,
        }
    }
}

let request = RequestBuilder::new("https://example.com")
    .timeout_ms(2_000)
    .retries(3)
    .build();
```

## Relationship to other patterns

A [factory.md](./factory.md) decides _which_ class to make in one step; Builder handles complex _how-to-assemble_ over several steps. [abstract-factory.md](./abstract-factory.md) often uses builders to construct its individual products. The Prototype approach, cloning a template and changing a few fields, is an alternative when you mostly need small deltas from an existing object rather than fresh staged construction.
