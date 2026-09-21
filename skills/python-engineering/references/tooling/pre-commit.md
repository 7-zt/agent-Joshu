# pre-commit

pre-commit is a Git hook framework and multi-language hook environment manager. It installs hooks into the local repository so that fast, deterministic checks run before a commit lands, catching formatting, basic file hygiene, and obvious lint failures before they reach review. Hooks live locally first; CI integration is optional and project-dependent.

## Hook Framework

Configuration lives in `.pre-commit-config.yaml`, not in `pyproject.toml`. This is a tool fact: pre-commit reads its own file, and forcing the hook definitions into `pyproject.toml` for the sake of config centralization is not possible. Each hook declares a repo, a revision, and the hook IDs to run. pre-commit creates and caches an isolated environment per hook repo, so hooks do not depend on whatever happens to be installed in the project virtualenv.

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff-format
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

## Local Commit Gate

After `pre-commit install`, the hooks run automatically on `git commit` against staged files. The point is to fail trivial issues, formatting drift, leftover whitespace, broken YAML, at commit time rather than in review. Keep the hook set small and fast so the gate stays low-friction; a slow gate trains people to pass `--no-verify` and skip it entirely.

## Common Hooks

A typical Python set: file-hygiene hooks (`trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`), [`ruff-format`](./ruff.md) and `ruff` for formatting and linting, and a custom [Flake8 plugin](./flake8-plugin.md) for project-specific rules. A type-checking hook can be included, but a whole-repo type check is often too slow for every commit and fits CI better, with the editor LSP providing fast local feedback.

## Autofixing Hooks and File Modification

Some hooks modify files: `ruff-format`, `ruff --fix`, `end-of-file-fixer`, and `trailing-whitespace` rewrite content in place. When a hook changes a file, pre-commit reports failure and leaves the fix unstaged, so you review the change and re-stage before committing again. This is intentional; you see what was rewritten rather than committing machine edits blindly.

## Speed Considerations

The first run installs hook environments and is slow; that is expected and not a reason to treat pre-commit as a substitute for CI. Subsequent runs reuse the cached environments. Reserve the commit hook for fast, deterministic checks and push full test runs, coverage, and network-dependent scans to CI or manual tasks.

## Optional CI Integration

pre-commit only catches issues for contributors who installed the hooks and did not skip them, so CI must repeat the critical checks. Two common approaches: the hosted pre-commit.ci service, which runs the same config on pull requests and can auto-fix, or a manual CI step running `pre-commit run --all-files`. Not every project has CI, so treat this layer as optional rather than assumed, but where it exists it should mirror the local hook config so local and CI results agree.
