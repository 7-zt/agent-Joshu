# mypy

mypy is the mature, reference static type checker of the Python typing ecosystem. It is the natural choice when a project needs a strict, well-understood gate, broad third-party stub support, or alignment with the wider open-source community's expectations.

## Strict Mode

`--strict` turns on a bundle of flags that together demand full annotation coverage and reject the silent gaps gradual typing otherwise permits: `disallow_untyped_defs`, `disallow_any_generics`, `warn_return_any`, `no_implicit_optional`, `warn_unused_ignores`, and more. Enabling strict mode up front on a new project is cheap; retrofitting it onto an untyped codebase is where the work lives.

```toml
[tool.mypy]
strict = true
```

## Gradual Adoption

mypy was built for gradual typing, which makes it well suited to incremental adoption on an existing codebase. Start loose, then tighten module by module using per-module override sections, raising strictness where annotations already exist before pushing into untyped areas.

```toml
[[tool.mypy.overrides]]
module = "legacy.*"
disallow_untyped_defs = false
```

## Plugin System

mypy supports plugins that teach it framework-specific semantics the core type system cannot express on its own. Plugins exist for ORMs, data-modeling libraries, and other frameworks that generate attributes or transform classes at runtime. A plugin is what lets mypy understand a dataclass-like construct it would otherwise see as opaque.

## Common Pain Points

The recurring friction is third-party stubs: a dependency may ship no type information, an incomplete stub, or a separately installed `types-*` package, and missing stubs force a choice between installing them, writing local stubs, or ignoring the module. Conditional imports (`TYPE_CHECKING` blocks, version-gated imports, optional dependencies) are another common source of confusion. When suppressing an error, write the specific error code and a reason rather than a bare `# type: ignore`, so the suppression stays auditable.

## When mypy Adds Value over ty

mypy earns its place when the project needs to align with the open-source ecosystem, match an existing codebase's history, accommodate external contributors' habits, or pin down a subtle type-behavior difference. Where [ty](./ty.md) is the default gate for its speed and editor integration, mypy's value is maturity and ecosystem reach. A library being published, or a migration that must match upstream expectations, is a typical reason to enable a mypy strict profile alongside or instead of the default.

## Relationship to Other Checkers

mypy, [ty](./ty.md), and [basedpyright](./basedpyright.md) all check the same type system but differ in maturity, strictness, and speed. They will occasionally disagree on hard inference cases. Running all three permanently as a triple gate is rarely worth the configuration cost on a personal project; reserve the extra checkers for library releases, external collaboration, or migration windows where the cross-check pays for itself.
