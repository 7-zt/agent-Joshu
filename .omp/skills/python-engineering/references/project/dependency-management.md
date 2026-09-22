# Dependency Management

Every dependency is a standing liability as much as a convenience: it must be resolved, locked, installed, audited, and eventually upgraded, and each one widens the surface on which the project can break. Dependency management is the discipline of declaring _where_ each dependency lives, _why_ it is there, _how tightly_ it is constrained, and _whether_ the full resolution is pinned. The goal is an install that is reproducible where it must be, minimal for each use case, and honest about what is truly required at runtime versus what only the developers need.

## Runtime, Dev, Optional, And Workspace-Internal

The first decision for any dependency is which bucket it belongs in, because the buckets ship to different audiences.

Runtime dependencies go in `[project.dependencies]`. They are the libraries the package cannot import or run without; they install for every end user and every deployment. The bar for entry is real necessity: the package genuinely cannot function without it, and reimplementing it would be unreasonable.

Development dependencies, linters, formatters, type checkers, pytest, coverage, docs builders, are needed only while working on the project, never at runtime. They belong in dependency groups under `[dependency-groups]` (PEP 735), typically split into coherent groups like `dev`, `test`, and `docs`. Keeping them out of the runtime set is what stops a deployed service from dragging in a test framework it will never call.

Optional dependencies in `[project.optional-dependencies]` enable features that not every user wants; a database driver, a YAML parser, a docs extra. Each extra should map to one coherent feature boundary that a user can opt into by name (`pip install mypkg[redis]`), not become a dumping ground for "things some people might want."

Workspace-internal dependencies are the edges between members of a [workspace](./structure.md): one member depending on another in the same repository. These follow the declared dependency _direction_ and must point at a member's stable public API, never reach across into its internals.

## Lockfile Policy

A lockfile records the exact resolved graph, every transitive package at an exact version, so an install is byte-for-byte reproducible. Whether to commit it is a function of what the project _is_, not a universal rule.

Applications and services commit their lockfile (`uv.lock` or equivalent), because the whole point is to deploy the same resolved environment that was tested. CI installs _from_ the lock so production matches development. Libraries usually do _not_ commit a lockfile: downstream consumers resolve their own graph against their own constraints, and a library that tested only against one frozen resolution would miss breakage in the version ranges it actually claims to support. A workspace uses a single root lockfile covering all members, with each member's own constraints expressed in its own `pyproject.toml`.

When a lockfile change shows up in a diff, it is worth reading rather than rubber-stamping: an unexpected major-version jump, a new transitive dependency, or a removed package can ride in on an unrelated change. Upgrades should come from an explicit command and review, not drift in silently alongside other edits.

## Version Constraints

The tension in every constraint is between flexibility and reproducibility. A compatible-release constraint (`>=2.1,<3` or `~=2.1`) lets the resolver pick patch and minor updates, which keeps the project current and avoids conflicts when it sits alongside other packages; this is the right default for libraries, whose constraints are inherited by everyone downstream. An exact pin (`==2.1.4`) guarantees one specific version, which is what you want for an application's reproducible deployment, but in a library it is antisocial: it forces the pin on every consumer and is a frequent source of unsatisfiable resolutions.

The general rule is to constrain as widely as is safe. Pin exactly where reproducibility is the goal (applications, via the lockfile rather than the spec where possible); use compatible ranges where the package will be composed with others (libraries). A pin tighter than necessary should carry a reason, because a future reader will otherwise have to guess whether it guards a real incompatibility or is just stale caution.

## Weight And Justification

Each new dependency should clear a justification bar: could the need be met by the standard library, a smaller library, or a few lines of local code? The standard library is the default dependency; reach past it only when a stdlib mechanism is genuinely insufficient. Pulling a heavy framework in for a single utility function trades a large install, a larger attack surface, and an ongoing upgrade burden for something a short helper would cover.

The cost is not only download size. Every dependency is a supply-chain entry, a license to check, and a maintenance commitment; an unmaintained or thinly-maintained package becomes the project's problem when it stops receiving fixes. Some weight is unavoidable and correct: numerical and data work legitimately depends on large, well-maintained packages, and that is not a smell. The judgment is proportionality, not minimalism for its own sake.

## Dependency Direction In A Monorepo

In a workspace or monorepo, the dependencies between internal packages form a graph, and that graph must stay a directed acyclic one. Shared and lower-level packages (domain models, utilities) are depended _upon_; applications and services depend _on_ them, not the other way around. When two members start importing each other, the boundary between them has failed and they are really one package wearing two names.

Each member should declare only its own direct dependencies. A member that relies on a package transitively because another member happens to pull it in has an undeclared dependency. It will break when the intermediary drops that package. Explicit per-member declarations and a shared lockfile keep a workspace coherent instead of amplifying coupling; [structure](./structure.md) covers the structural side.
