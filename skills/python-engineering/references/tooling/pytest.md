# pytest

pytest is the default test runner for non-throwaway projects. It handles test discovery, fixtures, parametrization, markers, assertion introspection, and the run entry point. It does not dictate production style directly, but the way it injects dependencies and isolates behavior pushes code toward being testable.

## Test Discovery

By default pytest collects files matching `test_*.py` or `*_test.py`, functions prefixed `test_`, and classes prefixed `Test` (with no `__init__`). Configure `testpaths` so collection starts from the right place:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

Keeping tests under a top-level `tests/` directory separates them from the importable production package and makes discovery predictable. Whether tests are included in an sdist or wheel is controlled by the build backend's package discovery and include/exclude configuration.

## conftest.py

`conftest.py` holds fixtures, hooks, and plugin configuration shared across a directory subtree without being imported explicitly. pytest loads it automatically. A root `conftest.py` shares fixtures project-wide; nested ones scope helpers to a subtree. Use it for shared fixtures and hook implementations, not as a dumping ground for test helpers that would read more clearly as plain imported modules.

## Fixture Scoping

Fixtures have a `scope`: `function` (default), `class`, `module`, `package`, or `session`. Wider scopes share expensive setup (a database, a server) across more tests, trading isolation for speed. Match scope to the cost and mutability of the resource: a fresh temp directory per function, a read-only fixture once per session. `yield` fixtures run teardown after the `yield`, which is the idiomatic way to release resources.

```python
import pytest

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine()
    yield engine
    engine.dispose()
```

## Parametrize

`@pytest.mark.parametrize` runs one test function across multiple inputs, each as a separately reported case. It replaces hand-written loops and makes failures point at the specific input. Use `ids` for readable case names, and stack parametrize decorators to take the cross product of input sets.

```python
@pytest.mark.parametrize("value,expected", [(2, 4), (3, 9)])
def test_square(value, expected):
    assert square(value) == expected
```

## Markers

Markers tag tests for selection: built-ins like `skip`, `skipif`, `xfail`, and custom markers such as `slow` or `integration` selected with `-m`. Register custom markers in config so a typo does not silently create a new marker. `--strict-markers` turns unregistered markers into errors, which is worth enabling.

```toml
[tool.pytest.ini_options]
markers = ["slow: long-running tests", "integration: needs external services"]
```

## Import Modes

The import mode controls how test modules reach `sys.path`. The legacy `prepend` mode inserts the rootdir and relies on `__init__.py` placement, which can mask packaging mistakes. New projects should prefer `--import-mode=importlib`, which imports test modules without manipulating `sys.path`, avoiding name collisions and surprising import side effects.

```toml
[tool.pytest.ini_options]
addopts = "--import-mode=importlib"
```

## Strict Mode

`--strict-markers` and `--strict-config` turn unknown markers and config issues into hard failures, surfacing mistakes early. They are worth enabling, but they couple the suite to pytest's current behavior, so pin the pytest version. If you do not want to absorb future strictness changes automatically, enable the specific strict options rather than relying on a broad mode.

## Plugin Ecosystem

pytest has a large plugin ecosystem: `pytest-cov` for coverage, `pytest-xdist` for parallel runs, `pytest-asyncio` for coroutine tests, and many framework integrations. Add plugins for real needs rather than by default; each one is a dependency and a potential source of collection or fixture surprises. Coverage in particular can run through [coverage.py](./coverage.md) directly without the plugin.

pytest verifies that code runs and asserts on behavior, but a passing suite does not prove the assertions are meaningful or the edge cases covered. Coverage tooling answers what executed; only the assertions answer whether it was correct.
