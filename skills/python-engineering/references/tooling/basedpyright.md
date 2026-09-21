# basedpyright

basedpyright is a community fork of Pyright. It tracks Pyright closely for performance, import resolution, and LSP behavior, but ships stricter defaults, additional diagnostics, baseline support, and PyPI installation. It is most useful as a strict type-checking cross-reference and as a way to keep editor and CLI results consistent.

## Relationship to Pyright

Pyright supplies the foundation: a fast type checker with strong language-server support, CLI execution, import resolution, and the core typing rules. basedpyright is a fork that keeps following upstream while adding what its maintainers consider missing. Pyright's capabilities can be cited as upstream evidence for basedpyright, but the two are not identical, so Pyright documentation only establishes the baseline, not basedpyright's specific behavior.

## Default Strictness Differences

The headline difference is that basedpyright is strict by default where Pyright is not. It promotes to errors many diagnostics Pyright leaves as warnings or disables, so a codebase clean under Pyright can surface a wave of new findings under basedpyright. This is the point of the fork: it expresses a more demanding stance out of the box.

## reportUnusedX and Extra Diagnostics

basedpyright adds and enables diagnostics beyond Pyright's set, including stricter `reportUnused*` rules (unused imports, variables, expressions, and similar) and reporting around `Any` usage that escapes detection elsewhere. These rules catch dead code and silent `Any` leakage, but on a large existing codebase they need a baseline to avoid an unmanageable initial report.

## Baseline Adoption

For an existing project, basedpyright supports a baseline file that records current findings so only new issues fail the gate. This is the practical path to adopting it midstream: capture the baseline, hold the line on new code, and burn down recorded findings over time rather than fixing everything before the first green run.

## IDE Integration

basedpyright provides a language server and integrates with editors, including a path to Pylance-equivalent features outside the proprietary VS Code build. Because the same engine runs in the editor and on the CLI, in-editor feedback and the gate stay aligned, which is a large part of its appeal for strict workflows.

## When It Provides Value

When [ty](./ty.md) is the default gate, basedpyright can preserve a historical strict profile, cross-check a migration, verify hard inference cases, or supplement external collaboration. It does not displace ty as the default. Avoid a permanent triple gate of ty plus [mypy](./mypy.md) plus basedpyright unless project scale, risk, and payoff justify the configuration cost. When basedpyright is enabled, define the baseline, suppression style, strict rules, target Python version, and import resolution explicitly so results are reproducible across machines and CI.
