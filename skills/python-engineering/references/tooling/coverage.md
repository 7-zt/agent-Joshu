# coverage.py

coverage.py measures which lines and branches of code execute while tests run. It is not a test framework and not a quality metric on its own; it is an observability layer over test execution that answers "what did the tests actually reach", not "did the tests check the right things".

## Statement vs Branch Coverage

Statement coverage records which lines ran. Branch coverage also records which edges of each conditional were taken, so an `if` whose `else` path is never exercised shows as a partial branch even when every line ran. Branch coverage catches untested decision paths that statement coverage hides and is worth enabling for core logic and libraries.

```toml
[tool.coverage.run]
branch = true
source = ["mypackage"]
```

## Running Coverage

The native commands are straightforward and avoid an extra plugin dependency:

```bash
coverage run -m pytest
coverage report -m
coverage html
```

`coverage run` records execution, `report` prints a terminal summary (with `-m` showing missing line numbers), and `html` produces a browsable annotated report. `pytest-cov` integrates coverage into the pytest invocation and is convenient, but it is optional rather than required.

## Configuration

Configure under `[tool.coverage.*]` in `pyproject.toml`. `source` scopes measurement to your package so third-party code does not dilute the numbers. `omit` excludes files like generated code or migrations. `[tool.coverage.report]` controls `exclude_lines` (for example `pragma: no cover`, `if TYPE_CHECKING:`, and `raise NotImplementedError`) and the `fail_under` threshold.

```toml
[tool.coverage.report]
exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:"]
fail_under = 80
```

## Threshold Policy

`fail_under` fails the run when total coverage drops below a percentage. Start from a realistic, currently-reachable number and raise it gradually; a threshold set far above current reality just trains people to bypass it. A high number is also not proof of quality, since coverage counts execution, not assertion strength.

## What Coverage Measures and What It Does Not

Coverage tells you a line or branch was executed during the suite. It says nothing about whether an assertion checked the result, whether boundary values were tested, or whether error paths were verified meaningfully. Code can reach 100% coverage with tests that assert nothing. Treat coverage as a floor that flags clearly untested code, not as evidence of behavioral correctness.

## CI Gates

Coverage typically runs in CI, where the threshold gate is enforced consistently across contributors. Locally it is run on demand rather than on every commit, since a full coverage run is slower than the fast checks suited to a commit hook. Use [coverage.py](./coverage.md) combined with the [pytest](./pytest.md) run in CI, and keep the threshold the single source of truth referenced by both local and CI invocations.
