# Ruff

Ruff is a fast Rust-based formatter and linter that covers the work of Black, Flake8, isort, pyupgrade, and many Flake8 plugins in one tool. Two responsibilities live under one binary: `ruff format` handles mechanical layout, and `ruff check` handles lint rules. Keeping them in one toolchain means shared configuration and consistent, fast feedback.

## Formatter

`ruff format` reformats layout: line wrapping, indentation, quotes, parentheses, blank lines, and trailing commas. It targets Black compatibility, so output is close to Black's and adopting it on a Black codebase produces minimal churn. Trust it for everything mechanical and stop reviewing formatting by hand. It is deterministic and safe to run on every save and in pre-commit.

```bash
ruff format
ruff format --check    # CI: fail if not formatted
```

The default style stays Black-compatible. Preview style enables in-progress formatting changes; leave it off unless the project accepts periodic reformatting diffs as the style evolves. Configure under `[tool.ruff.format]`, for example `docstring-code-format` to format code blocks inside docstrings, which is optional and not on by default.

## Linter

`ruff check` runs lint rules organized into families identified by prefix: `E`/`W` (pycodestyle), `F` (Pyflakes), `I` (isort import sorting), `UP` (pyupgrade modernization), `B` (bugbear), `SIM` (simplify), `C4` (comprehensions), `RET` (return), `RUF` (Ruff-native), and many more. A small starting set such as `E`, `F`, `I`, `UP`, `B` catches real defects without drowning the project in stylistic noise.

```bash
ruff check
ruff check --fix
```

Import sorting comes from the `I` family, so a separate isort is unnecessary. Avoid `select = ["ALL"]`: it turns linting into a collection of micro-preferences, and every added family carries false-positive cost, reviewer cognition cost, autofix-safety risk, and migration cost on existing code. Add families like `SIM`, `RUF`, `C4`, `PIE`, `RET` as the need appears.

## Rule Maturity

Rules are stable or preview. Stable rules are enabled through `select`; preview rules need preview mode and may change. Treat preview rules as opt-in experiments, not defaults, so the rule set does not shift underneath the project on a Ruff upgrade.

## `ruff check --fix` Behavior

`--fix` applies fixes Ruff classifies as safe, such as removing unused imports and sorting them. Unsafe fixes can change behavior or intent and require `--unsafe-fixes` to opt in. Review autofix diffs rather than committing them blindly, especially in bulk across a legacy codebase, because a "safe" fix on unusual code can still surprise.

## Configuration

Configuration lives in `pyproject.toml` under `[tool.ruff]`, with `[tool.ruff.lint]` for rule selection and `[tool.ruff.format]` for formatting. Set `target-version` and `line-length` once and let both halves share them. Per-file ignores handle legitimate exceptions, for example relaxing import rules in `__init__.py`.

```toml
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

## What Ruff Handles vs What Needs Human Review

Ruff settles formatting and a wide band of mechanical lint, which is exactly the noise that should never reach a human reviewer. It does not judge naming quality, module responsibility, exception context, type-boundary design, docstring information value, or architecture; those need a type checker, tests, and human review. Ruff's security rules (`S`, from Bandit) are low-cost static reminders, not a full SAST or dependency-vulnerability scan, and do not replace dedicated tools or human security review.
