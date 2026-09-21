# uv

uv is a Python project and environment manager: it resolves dependencies, builds lockfiles, runs scripts, manages tool installs, and provisions Python interpreters. It answers "which Python does this project use, which dependencies are installed, how is the environment reproduced, and how are tools run" rather than dictating code style.

uv consolidates jobs that previously needed pip, pip-tools, pipx, virtualenv, and a version manager. It is fast and writes a lockfile by default, which makes reproducible environments the path of least resistance.

## Project Creation

`uv init` scaffolds a project with `pyproject.toml`, a `.python-version` file pinning the local interpreter, and a starting source layout. The `[project]` table holds `requires-python`, the dependency list, and packaging metadata. Pin `requires-python` deliberately because it drives version-conditional syntax decisions and constrains the resolver.

```bash
uv init my-project
cd my-project
uv add httpx
```

## Dependency Management

`uv add <pkg>` and `uv remove <pkg>` edit `pyproject.toml` and update the lockfile in one step. `uv lock` re-resolves without installing, and `uv sync` makes the environment match the lockfile exactly, removing anything not declared. The environment is treated as derived state: declare intent in `pyproject.toml`, let the lockfile and `.venv` follow.

```bash
uv add "fastapi>=0.115"
uv add --dev pytest ruff
uv remove requests
```

## Lockfile

`uv.lock` records the fully resolved dependency graph with hashes across platforms. Commit it for applications so every machine and CI run installs identical versions. A library that must resolve freshly against a range of dependency versions is the main case for not committing a lock, but most repositories benefit from a checked-in lockfile.

## Dependency Groups

Development, test, lint, and typing dependencies belong in groups rather than the runtime dependency list, so they are installable selectively and excluded from published artifacts. Use `uv add --dev` for the default dev group or `--group <name>` for named groups. The exact table layout follows whatever the current uv version supports under `[dependency-groups]` and `[tool.uv]`.

## Script Execution

`uv run <command>` executes inside the managed environment, syncing first if needed, so contributors never activate a virtualenv manually or get a stale environment. Route every tool invocation through it to keep local and CI behavior identical.

```bash
uv run pytest
uv run ruff check
uv run python -m myapp
```

Single-file scripts use PEP 723 inline metadata: a commented dependency block at the top of the file lets `uv run script.py` provision an ephemeral environment with no project required.

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///
import httpx
```

## Tool Management

`uv tool install` and `uv tool run` (aliased as `uvx`) manage standalone CLI tools in isolated environments, covering the role pipx fills. This suits globally useful tools that are not project dependencies. Project-scoped quality tools are better declared as dependency-group members and run with `uv run`, so their versions are locked alongside the code they check.

```bash
uvx ruff check
uv tool install pre-commit
```

## Workspace

A workspace groups multiple related packages under one lockfile and shared resolution, similar to Cargo or npm workspaces. Members are declared under `[tool.uv.workspace]`. Use it for a monorepo of co-developed packages that should share a single resolution; avoid it for unrelated projects that only happen to live in the same directory, since shared resolution couples their dependency constraints.

## Python Version Management

uv downloads and manages standalone CPython builds, so `requires-python` and `.python-version` are enough to get a matching interpreter without a separate tool like pyenv. `uv python install 3.12` provisions a version, and the resolver respects the project's declared bounds when selecting one.

## Relationship to pip, pipx, and Poetry

uv covers what pip (install), pip-tools (lock), pipx (tool isolation), virtualenv (environments), and a version manager each did separately. Compared to Poetry it overlaps on project and dependency management but emphasizes speed and a broader environment role. The tool being fast and unified is the reason to adopt it; it does not replace type checking, tests, coverage, or CI, which still gate correctness. Existing Poetry or Hatch projects, published libraries with their own constraints, and organization-standard setups are migrated on their own merits, not automatically.
