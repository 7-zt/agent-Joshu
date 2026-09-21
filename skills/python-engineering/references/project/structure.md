# Project Structure

A long-lived Python project should never be just "a directory that the current working directory happens to be able to import." Structure exists so that the importable package, the tests, the tool configuration, the run entry points, the dependency declarations, and the deployment boundary each have an unambiguous home. The right shape depends on how the project is used and how long it is expected to live; this document covers every common form and the signals that move a project from one to the next.

## Single-File Script

A single `.py` file is the right shape for one-off automation, small tools, and experiments. With PEP 723 inline script metadata, even a standalone file can declare its dependencies and required Python version in a comment block, so a runner like `uv run script.py` can build an isolated environment without a surrounding project:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx"]
# ///
import httpx
```

This is appropriate when the script is genuinely small, has no test needs, and is not a long-term maintained component. The growth signals that mean it has outgrown a single file: it accumulates several helper functions, it needs its own tests, it grows a config file, or another piece of code wants to import part of it. At that point, promote it to a real package rather than letting it become a permanently-appended mega-script.

## Flat Layout

A flat (or "no-src") layout puts the import package directly at the project root:

```text
project/
├── pyproject.toml
├── mypkg/
│   ├── __init__.py
│   └── app.py
└── tests/
    └── test_app.py
```

It is intuitive, has low startup cost, and is common in small libraries, historical projects, and simple internal tools. Its structural weakness is that the project root naturally enters `sys.path`, so local tests and scripts tend to import the _source directory_ rather than the _installed artifact_: masking packaging mistakes such as a missing file in the built wheel.

The real degradation risk is not flat layout itself but its collapse into a "big script directory": `run.py`, `utils.py`, `db.py`, `api.py` all scattered at the root, importing each other through the current directory, with entry points and library logic tangled together and import-time side effects no one can trace. If you choose flat layout, still keep a clear package directory, separate entry scripts from importable logic, and forbid heavy import-time side effects (reading the environment, opening connections, starting threads).

## Src Layout

A src layout moves the intended import packages into a `src/` subdirectory:

```text
project/
├── pyproject.toml
├── README.md
├── src/
│   └── mypkg/
│       ├── __init__.py
│       └── app.py
└── tests/
    └── test_app.py
```

The point of the separation is _import safety_: because `src/` is not on `sys.path` by default, you cannot accidentally import the package from the source tree. Tests run against the _installed_ package (via an editable install), so they exercise the same import paths and packaging boundaries that real users will. This catches a class of bugs, a module missing from the build, a data file not packaged, that flat layout hides until release.

Choose src layout for any project that will be published, deployed, or maintained over time: libraries, SDKs, frameworks, CLIs, web services, and workspace members. The cost is a slightly higher initial mental model (you must install the package, even if editable, to run it) in exchange for tests that mean what they claim. Local development uses an editable install or an equivalent uv-managed environment; never depend on hand-edited `PYTHONPATH`.

## Packaged Application

A packaged application is installable, runnable, and deployable, a CLI, web/API service, background worker, or internal platform tool, described by `[project]` metadata rather than left as loose scripts:

```text
project/
├── pyproject.toml
├── uv.lock
├── README.md
├── src/
│   └── app_name/
│       ├── __init__.py
│       ├── __main__.py
│       └── cli.py
└── tests/
    └── test_cli.py
```

The `[project]` table declares `name`, `version` (or `dynamic`), `requires-python`, and `dependencies`. Entry points belong in `[project.scripts]` so the tool is invoked by its name, not by `python src/app_name/main.py`. Non-runtime dependencies such as dev, test, lint, and docs go in dependency groups and stay out of the runtime set; see [dependency-management](./dependency-management.md). A lockfile pins the deployment environment.

The common misreading is that "installable" means "must be published publicly." It does not. A private application is built into a wheel for internal deployment; the safeguard is to keep it from being published by accident: no public PyPI token in CI, no publish step by default, and a name that does not impersonate a public package.

## Workspace

A workspace is a multi-package repository where several packages or applications share one lockfile and one set of tooling entry points. A uv workspace fits an application plus shared libraries, a group of services, or a monorepo of co-evolving internal packages:

```text
repo/
├── pyproject.toml
├── uv.lock
├── packages/
│   ├── app-api/
│   │   ├── pyproject.toml
│   │   └── src/app_api/
│   └── shared-domain/
│       ├── pyproject.toml
│       └── src/shared_domain/
└── tests/
```

Introduce a workspace only when there are genuinely at least two packages with distinct, describable responsibilities, a clear dependency _direction_ between them, and shared packages that expose a stable API rather than internal directories temporarily carved out of an application. The workspace root owns shared tool configuration and whole-repo commands; each member owns its own metadata and runtime dependencies. Application members must not reach into a shared package's internals; they depend on its public API and on the declared direction only.

Do not reach for a workspace just because there are many directories, or to split one large application by folder, or when packages import each other's internals with no stable boundary. Without whole-repo tests, type checking, and a dependency-upgrade strategy, a workspace amplifies coupling instead of containing it.

## Decision Table

| Project type | Recommended layout | Signals to migrate up |
| --- | --- | --- |
| One-off automation, experiment | Single-file script (PEP 723) | Multiple helpers, test needs, a config file, or another module wants to import it |
| Small library, simple internal tool | Flat layout | Multiple entry points, dependency groups, or packaging mistakes start slipping through |
| Published library, SDK, framework | Src layout | (Default for anything maintained or released) |
| CLI, web/API, service, internal app | Packaged application (src + `[project]`) | Deployment artifacts, entry points, and lockfile needed |
| App + shared libs, service group, monorepo | Workspace | Two+ packages with stable APIs and a clear dependency direction |

When in doubt between flat and src for anything that will outlive the week, prefer src: the import-safety guarantee is cheap insurance against packaging surprises.

## Test Directory, Config, And Entry Points

Across all packaged forms, keep tests in a top-level `tests/` directory, not inside the production package, unless the ecosystem has a strong contrary convention. Name tests after behaviors and boundaries rather than mechanically mirroring every implementation file; for large frameworks and SDKs a loose mirror of the package tree aids navigation. Point the test runner at the test directory explicitly (`testpaths = ["tests"]`) so it never wanders into temporary directories or built docs. Coverage source should point at the actual package path so tooling and scripts do not pollute production coverage numbers. Detailed test conventions live in [testing](../spec/testing.md).

Tool configuration centralizes in `pyproject.toml` under `[tool.*]`, with the exceptions that tools genuinely require their own files (pre-commit keeps `.pre-commit-config.yaml`). Entry points for installed commands belong in `[project.scripts]`; a `__main__.py` enables `python -m app_name`. The guiding rule is that project shape, dependency groups, test scope, and type-check scope should all be _explicit in configuration_ rather than implied by whatever the current directory happens to make importable.
