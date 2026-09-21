# Flake8 Plugin

A Flake8 plugin is a Python package that registers AST or token visitors to produce custom lint warnings. It lets projects enforce domain-specific or architecture-specific rules that general-purpose linters cannot cover: forbidden imports, required decorator patterns, module boundary violations, naming conventions tied to framework semantics, or structural constraints on specific base classes.

## How It Works

Flake8 plugins operate at AST level. They receive the parsed tree (or raw tokens/lines) and yield `(line, col, message, type)` tuples. The plugin registers itself via `entry_points` in `pyproject.toml` under the `flake8.extension` group.

A minimal AST-checker plugin needs:

1. A class with `name` and `version` class attributes.
2. An `__init__(self, tree)` that receives the AST (for AST checkers) or `__init__(self, tree, filename)`.
3. A `run(self)` generator that yields `(line, col, message, type)`.
4. Registration via `[project.entry-points."flake8.extension"]` in `pyproject.toml`.

For token-based or physical-line checkers, alternative registration hooks exist, but AST checkers are the most common for structural rules because they have access to the full parse tree.

## When A Plugin Is Appropriate

- The rule is mechanical: it can be evaluated from the AST without runtime information.
- The rule has low false-positive rate once properly scoped.
- The rule applies consistently across the codebase, not just in one module.
- The rule would otherwise require repeated human review effort.
- The rule cannot be expressed as a [Ruff](./ruff.md) rule configuration or `select`/`ignore` combination.

## When A Plugin Is Not Appropriate

- The check requires runtime type resolution, cross-module data flow, or import resolution beyond what the AST provides. These need a type checker, not a lint plugin.
- The rule is subjective or context-dependent, better suited to review judgment.
- [Ruff](./ruff.md) or another existing tool already covers the check. Before writing a custom plugin, check whether Ruff implements the rule family natively (e.g., `flake8-bugbear`, `flake8-comprehensions`).
- The rule only applies to one or two files; a code comment or review note suffices.
- Maintaining the plugin costs more than the bugs it prevents.

## Testing

Test plugins by invoking them against synthetic AST snippets:

- Parse a code string with `ast.parse`.
- Instantiate the checker class with the tree.
- Collect results from `run()`.
- Assert expected line/col/message tuples for positive cases and empty results for negative cases.

For integration testing, run `flake8 --select=YOUR_CODE` against fixture files that exercise both triggering and non-triggering patterns.

## Relationship To Ruff

Ruff implements many Flake8 plugin rule sets natively. Before writing a custom plugin, check whether Ruff already covers the rule family. If it does, prefer [Ruff configuration](./ruff.md).

Custom project-specific plugins remain valuable because Ruff does not support arbitrary user-defined AST visitors. Projects that need truly custom structural checks still need Flake8 plugins (or alternative approaches: custom Ruff rules via the unstable plugin API, or standalone AST scripts run in [pre-commit](./pre-commit.md)).

The relationship to [custom lint specification](../spec/custom-lint.md) is: the spec document defines _what_ project-specific rules to create and _how to think about_ rule design; this document covers the Flake8 plugin _mechanism_ for implementing and running those rules.

## Error Message Design

An actionable error message tells the developer:

- What was detected (the violation).
- Why it matters (briefly).
- What to do about it.

Prefix messages with a short code (e.g., `PRJ001`) for selective suppression. Keep messages under one line. If a rule needs extensive explanation, link to internal documentation in the message.
