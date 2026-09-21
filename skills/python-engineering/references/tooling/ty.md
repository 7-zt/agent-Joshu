# ty

ty is a fast, Rust-based type checker and language server from Astral, the team behind Ruff and uv. Its design goals are speed and tight editor integration: a type checker fast enough to run on every keystroke through the LSP, plus a CLI suitable for a CI gate.

## Speed Advantage

The defining trait is incremental speed. A Rust core lets ty re-check large projects in a fraction of the time mypy or pyright take, which keeps the editor feedback loop tight and makes a CI type gate cheap. Fast feedback is the whole reason to adopt it early: the cost of running it is low enough that it does not slow daily work.

## What It Checks

ty does the work expected of a static type checker: full type coverage across a project, interface boundaries, `Any` leakage, type narrowing, reachability analysis, and unreachable-code detection. It serves both the editor (via LSP) and the command line, so the same checks a developer sees inline also run in CI.

```bash
ty check
```

## Maturity and Limitations

ty is newer than mypy and pyright, so it sits on an early-adoption path. It does not yet provably cover every typing scenario the older checkers handle, and coverage of every third-party stub, edge-case inference, and the newest Python semantics needs project-level verification rather than assumption. Treat it as high-potential and capable, but verify behavior on the specific project rather than trusting it blindly.

## Relationship to mypy and pyright

ty competes with [mypy](./mypy.md) and [basedpyright](./basedpyright.md) as the primary checker. The tradeoff is concrete: ty offers speed and editor responsiveness today, while mypy and pyright/basedpyright offer more mature ecosystems and, in basedpyright's case, stricter defaults. Choosing ty as the default gate is a judgment that fast feedback outweighs the maturity gap for the project at hand; the older checkers remain available as a comparison layer when publishing a library, collaborating externally, or migrating.

## Configuration and Adoption

Configure ty in `pyproject.toml` under its `[tool.ty]` table, and define rule strictness explicitly rather than enabling every experimental diagnostic at once. The risk-control approach for early adoption is to pin the tool version, keep a project-level config, validate in CI, and keep mypy or basedpyright reachable as a cross-check when a specific type question needs a second opinion. Lock the version so a tool update does not silently change which diagnostics fire.

## What It Catches vs Misses

ty catches the broad class of static type errors: mismatched arguments, bad returns, `None` handling, narrowing failures, and unreachable branches. What it can miss are scenarios involving immature third-party stubs, the most recent language semantics, or inference corners the older checkers have spent years hardening. When ty and a mature checker disagree on a hard case, investigate rather than assuming ty is wrong or right.
