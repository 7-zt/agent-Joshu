# Python Version Policy

A project does not run on "Python" in the abstract; it runs on a range of versions, and that range is a design decision with consequences for syntax, dependencies, and deployment. Two numbers matter, and they are not the same: the _minimum_ version the code must support, and the _target_ version development and CI assume.

## Minimum Versus Target

The minimum version is the floor; the oldest interpreter on which the code is guaranteed to import and run. It is declared with `requires-python` and it constrains which syntax and standard-library APIs are available everywhere. If the floor is 3.10, you cannot use `type X = ...` aliases or PEP 695 generic parameters anywhere in the shipped code, because a 3.10 interpreter will raise a `SyntaxError` before any logic runs.

The target version is the one you develop against, pin locally (often via `.python-version`), and run first in CI. It is usually the newest version the dependency chain supports. Code must still stay within the minimum's syntax, but the target is where you get the fastest interpreter, the best error messages, and early warning of upcoming deprecations.

A healthy project keeps these aligned deliberately: a CI matrix runs both the floor and the target (and sometimes points in between), so a feature that accidentally requires a newer version fails fast rather than at a user's install.

## How To Determine The Minimum

The floor is not a preference; it is the maximum of several hard constraints. Determine it by asking what actually has to run the code:

- **Runtime environment.** If the code is deployed to a managed platform, a base image, or an OS package with a fixed interpreter, that version is a hard lower bound. You cannot require 3.12 if the only available runtime ships 3.11.
- **Dependency compatibility.** Every dependency declares its own `requires-python`. The project's floor cannot be lower than the highest floor among its dependencies. A single library that requires 3.11 pulls the whole project up to 3.11.
- **Deployment platform.** Serverless runtimes, Linux distributions, and corporate base images lag behind the latest release. The floor must be a version those targets actually offer.
- **CI matrix reach.** The versions you are willing and able to test form the practical support set. Claiming support for a version you never run in CI is an unverified promise.

The floor is the highest of these lower bounds. Lower than that and something breaks; higher than necessary and you exclude users or environments for no benefit.

## Version-Gated Features

Each recent release adds capabilities that become usable only once the floor reaches that version. Choosing a floor is therefore also choosing which of these are on the table:

- **3.10** brings structural pattern matching (`match`/`case`), the `X | Y` union operator in annotations, and parenthesized context managers. See [match-case](../grammar/match-case.md) for when pattern matching earns its place.
- **3.11** brings `ExceptionGroup` and `except*` for concurrent and batched failures, exception notes via `add_note()`, and `Self` in typing. See [exception-groups](../grammar/exception-groups.md).
- **3.12** brings PEP 695: the `type X = ...` alias statement and inline generic parameters (`def f[T](x: T) -> T`), plus `typing.override`. These remove most `TypeVar`/`Generic` boilerplate but are a hard syntax gate; covered in [type-hint](../spec/type-hint.md).
- **3.13** brings `warnings.deprecated()` as a runtime-and-static deprecation marker, type parameter defaults, and an experimental free-threaded build.
- **3.14** brings deferred annotation evaluation by default (PEP 649/749), `annotationlib` for reading annotations, and template strings. Code that _reads_ annotations at runtime, including frameworks, ORMs, serializers, and DI containers, needs verification against this behavior; see [type-hint](../spec/type-hint.md).

A feature being available is not a reason to use it. Pattern matching, exception groups, and generics each have a narrow zone where they help; the gate only decides whether the option exists.

## `requires-python` Semantics

`requires-python` in `[project]` is a constraint on the _installing_ interpreter, not a version the build pins. A specifier like `">=3.12"` tells installers and resolvers that the package refuses to install on anything older, and it lets dependency resolvers pick compatible versions of _your_ package for _their_ environment. It does not download or switch interpreters; it only declares the contract.

Keep `requires-python`, the local `.python-version`, and the CI matrix consistent. When they drift, `requires-python = ">=3.10"` but every developer runs 3.12 and CI never tests 3.10, the floor becomes fiction, and 3.10-incompatible syntax can slip in undetected.

## Docker And Base Images

When the deployment artifact is a container, the base image tag _is_ part of the version policy. Pin a specific minor version (`python:3.12-slim`), not a floating `python:3` or `python:latest`, so the runtime cannot shift under you between builds. The image's interpreter should match the target version, and it must satisfy the declared floor. Slim and distroless variants reduce surface area but change which system libraries are present, which can matter for packages with compiled extensions.

## When To Bump The Minimum

Raising the floor is a breaking change for anyone on an older interpreter, so it needs a reason beyond novelty. Good reasons:

- A dependency you need has itself dropped support for the old version, forcing your hand.
- The old version has reached end-of-life and no longer receives security fixes.
- A version-gated feature would materially simplify the code and the old version's user base is gone or negligible.
- The deployment and CI targets have all moved, leaving the old floor untested in practice.

When you do bump, do it as a deliberate, announced change: update `requires-python`, the CI matrix, the base image, and any compatibility shims in one coherent step, and only then start using the newly available syntax. Bumping the floor and adding 3.12-only syntax should be the same decision, not two accidents.
