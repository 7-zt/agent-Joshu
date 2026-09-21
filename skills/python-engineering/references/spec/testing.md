# Testing

This is the Python testing spec for organizing and writing pytest suites. It covers test placement, naming, fixtures, parametrization, mocking, async tests, and maintainable pytest idioms. Runner configuration such as discovery, import mode, markers, strict mode, config, and plugins lives in [pytest](../tooling/pytest.md).

A test should couple to the code's _behavior_ and stay independent of its _structure_. Test what a unit does from outside: return values, raised exceptions, and recorded side effects. Do not test how it does the work internally.

## Test Organization

Keep tests in a top-level `tests/` directory, separate from the production package, so they import and exercise the package the way a real consumer would and so discovery stays predictable (see [structure](../project/structure.md) for why the src layout reinforces this). The layout keeps tests out of the _importable_ package, but it does not by itself decide what ships in an sdist or wheel; that is governed by the build backend's package discovery and include/exclude config, so verify the built artifact if excluding tests from distribution matters. Name test files and functions after the _behavior_ under test, not the implementation file they happen to touch; `test_expired_token_is_rejected` tells a reader what the system guarantees; `test_validate` tells them only which function ran. For a large library or framework, loosely mirroring the package tree helps locate tests, but the mirror is a navigation aid, not a rule that every module gets a parallel test file. Tests deserve the same care as production code: clear names, no copy-paste sprawl, and obvious intent.

## Fixtures That Kill Duplication Instead of Creating It

A fixture is requested by name: a test declares the fixture as a parameter, pytest finds it and injects it. The mechanic that matters for maintainability is that **fixtures can request other fixtures**, so shared setup composes into a dependency graph rather than being copied. The two recurring failures in agent-written suites are opposite ends of the same misunderstanding: either fixtures are ignored and setup is pasted into every test, or one giant fixture builds an entire world that every test drags in.

Both are fixed by the same discipline:

- **Put shared fixtures at the right level.** [pytest](../tooling/pytest.md) covers how `conftest.py` loading and visibility work; the judgment is _where_ to put a fixture. A fixture used across the suite goes in the root `conftest.py`; one used only by a subtree goes in that subtree's `conftest.py`. This is the direct cure for "the same fixture defined in several places, subtly different"; define it once at the right level rather than scattering near-copies. Deliberately overriding a fixture in a nested `conftest.py` to customize it for that subtree is a supported pattern, not a duplicate; the smell is _accidental_ near-copies, not intentional per-subtree specialization.
- **Discover before you define.** `pytest --fixtures` lists every available fixture and where it comes from. Run it before writing a new fixture so you reuse the existing one instead of adding a sixth near-duplicate.
- **Keep fixtures small and named for what they provide** (`temp_db`, `authenticated_client`), and compose them. A test's parameter list should read as its dependency list. Resist the "God fixture" that constructs everything; it is Meszaros' General Fixture smell and makes every test obscure.
- **Scope for isolation, widen only for cost.** [pytest](../tooling/pytest.md) documents the scope levels and `yield` teardown; the judgment is to stay at the default (fresh state per test, the isolation baseline) and widen only for setup that is genuinely expensive _and_ safe to share, since a wider scope buys speed by spending isolation. When a fixture needs cleanup, pair one setup with its own teardown rather than stacking several fragile setups in one fixture.

```python
# conftest.py: one definition, composed, function-scoped by default
import pytest


@pytest.fixture
def config() -> Config:
    return Config(timeout=30, retries=3)


@pytest.fixture
def client(config: Config) -> Iterator[Client]:
    c = Client(config)          # setup
    yield c
    c.close()                   # teardown, runs even on failure
```

### Factory-as-Fixture for Varying Instances

When a test needs _several_ objects of the same kind, or an object whose fields vary per test, return a _function_ from the fixture instead of an object. This replaces a swarm of near-identical fixtures with one, and keeps the varying values visible in the test body (DAMP):

```python
@pytest.fixture
def make_user() -> Callable[..., User]:
    def _make(name: str = "alice", *, admin: bool = False) -> User:
        return User(name=name, admin=admin)
    return _make


def test_admins_can_publish(make_user: Callable[..., User]) -> None:
    author = make_user(admin=True)
    assert author.can_publish()
```

### autouse Sparingly

An `autouse=True` fixture applies to every test in its scope without being requested. It fits a genuine cross-cutting side effect (patching a clock for a whole module), but it creates an _implicit_ dependency the test body does not show, which works against readability. Prefer an explicitly requested fixture unless the setup truly must apply everywhere.

## Parametrization: Cases as Data

[pytest](../tooling/pytest.md) covers the `@pytest.mark.parametrize` mechanics. For test quality, use parametrization to express the same check over different data as a visible table instead of copying test bodies. This produces fewer, stronger tests.

```python
@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param("  Alice ", "alice", id="trims-and-lowercases"),
        pytest.param("BOB", "bob", id="lowercases"),
        pytest.param("", "", id="empty-passes-through"),
    ],
)
def test_normalize_username(raw: str, expected: str) -> None:
    assert normalize_username(raw) == expected
```

Two idioms bridge parametrization and fixtures, beyond the basics:

- **`indirect=True`** routes a parameter through a same-named fixture first, for cases that need setup before they reach the test body.
- **Parametrizing a fixture** (`@pytest.fixture(params=[...])`) runs _every_ test that uses it against each variant; use it when the variation belongs to the dependency, not to one test.

The limit: parametrize only when the cases are the _same check over different data_. When cases need genuinely different setup or different assertions, forcing them through one body produces branching logic that is harder to read than separate tests. Different behaviors want different tests.

## Asserting Exceptions and Warnings

```python
def test_zero_timeout_is_rejected() -> None:
    with pytest.raises(ValueError, match="must be positive") as excinfo:
        Config(timeout=0)
    assert excinfo.value.field == "timeout"
```

- **`pytest.raises` matches subclasses.** `pytest.raises(RuntimeError)` also passes for subclasses of `RuntimeError`. When the _exact_ type is the contract, add `assert excinfo.type is RuntimeError`: otherwise the test silently accepts a broader failure.
- **`match=` is `re.search` against the message**: it is a substring or regex check, not a full match. Use it to pin the _meaningful_ part of the message, not the whole string, which would be a fragile over-specification.
- **`pytest.warns(SomeWarning, match=...)`** for warnings; `pytest.deprecated_call()` specifically for deprecation warnings; the `recwarn` fixture records warnings for inspection.
- Assert on the raised exception's _observable_ attributes, not on internal state built while raising it.

## Capturing Logs and Output: caplog, capsys

When the observable behavior _is_ a log line or console output, assert on it through pytest's capture fixtures rather than by hand-wiring handlers or redirecting streams.

- **`caplog`** captures log records. Assert on structured fields (`caplog.records`, `caplog.record_tuples`) rather than substrings of `caplog.text` when you can, so the assertion survives message-wording changes. Set the captured level with `caplog.set_level(logging.INFO)` or the scoped `with caplog.at_level(logging.INFO):`; `caplog.records` holds only the current phase's records (use `caplog.get_records("setup")` for other phases). Prefer asserting the _event_ was logged at the right level over pinning the exact string.
- **`capsys`** captures `stdout`/`stderr`; `captured = capsys.readouterr()` returns a namedtuple with `.out` and `.err`, snapshotting output so far. Use `capfd` when you must capture at the file-descriptor level (a subprocess or C library writing directly to FD 1/2), and the `*binary` variants for bytes. The streams are restored after the test automatically.

```python
def test_warns_on_retry(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.WARNING):
        connect(retries=1)
    assert any(r.levelno == logging.WARNING for r in caplog.records)
```

A caveat worth knowing: logging is easy to over-test. A log line is often incidental, not a contract; assert on it only when emitting it is the behavior someone depends on (an audit trail, an operator alert), not merely because the code happens to log.

## monkeypatch and tmp_path: State You Don't Clean Up by Hand

Prefer pytest's built-in state manipulators over hand-rolled setup/cleanup. `monkeypatch` **reverts automatically** after the test; `tmp_path` is **managed by pytest** rather than left for you to delete. Either way, there is no manual restore step that gets skipped when the test fails.

- **`monkeypatch`** patches and auto-undoes: `setattr` / `delattr`, `setenv` / `delenv`, `setitem` / `delitem`, `syspath_prepend`, `chdir`. The `raising` argument controls whether patching a missing target errors. Timing matters: the patch must be applied _before_ the code under test reads the target.
- **Patch where the name is looked up, not where it is defined.** If the module under test does `from services import Client`, patch `module_under_test.Client`; if it does `import services` and calls `services.Client`, patch `services.Client`. This "where to patch" rule (from the `unittest.mock` docs) is the single most common cause of a mock that silently does nothing.
- **`tmp_path`** gives each test a unique `pathlib.Path` temp directory (function scope); **`tmp_path_factory`** is the session-scoped version for temp resources shared across tests. pytest manages their creation and retention: by default it keeps the directories from the last few runs (configurable via `tmp_path_retention_count` / `tmp_path_retention_policy`), so a test never needs hand-rolled deletion. Use these instead of `tempfile` plus manual cleanup.

```python
def test_reads_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_TOKEN", "secret")   # reverted after the test
    assert load_token() == "secret"
```

## Mocking at the Boundary

pytest does not replace `unittest.mock`; it hosts it. Mock at _system boundaries_ such as the network, clock, filesystem, or external services, where the real dependency is slow or nondeterministic. Use real objects for cheap, deterministic collaborators. A test that mocks the code under test and its close collaborators becomes a Change-Detector Test. It asserts that the code called mocks exactly as prescribed, which is circular and breaks on behavior-preserving refactors.

Two mechanics keep mocks honest:

- **`monkeypatch.setattr` or `patch` at the looked-up namespace** (see above); a mock at the wrong path patches nothing and the test passes against real code by accident.
- **Prefer a real in-memory fake to a mock with scripted call expectations.** A fake (an in-memory repository, a fixed clock) verifies _state_ and survives refactoring; a mock that verifies _call order and arguments_ pins structure. Reach for interaction verification only when the interaction itself is the observable behavior (a charge happened exactly once).

When a unit is hard to test without mocking everything around it, that is a design signal: its dependencies want to be injected as arguments rather than reached for internally.

## Async Tests

With `pytest-asyncio` in its default **strict** mode, mark coroutine tests with `@pytest.mark.asyncio` and async fixtures with `@pytest_asyncio.fixture`, so the plugin coexists cleanly with others. Each test gets a function-scoped event loop by default, which maximizes isolation; widen with `loop_scope` only when tests must share a loop. Async tests run sequentially, not concurrently, precisely to preserve isolation; do not rely on them racing.

```python
@pytest.mark.asyncio
async def test_fetch_returns_payload() -> None:
    result = await fetch("/health")
    assert result.status == 200
```

Pin behavior, not the plugin's dev-version API surface: the concepts (marker, async fixture, loop scope) are stable, but specific fixtures have churned across versions.

## Anti-Patterns, in pytest Terms

These are common test-smell shapes in pytest:

- **Duplicated `conftest`/fixture definitions** across files → consolidate into the nearest common `conftest.py`; find them with `pytest --fixtures`.
- **A God fixture** every test depends on → split into small composable fixtures; General Fixture is an Obscure Test smell.
- **`assert_called_with` as the only assertion** → Change-Detector Test; assert on the result or a real side effect instead.
- **`time.sleep` to wait for async work, real `datetime.now()`, unseeded `random`** → Erratic Test; inject a clock, seed the RNG, control the boundary.
- **A test that asserts `SETTINGS.timeout == 30`** → Testing the Wrong Thing; test the behavior the value drives, not the literal.
- **`pytest.raises(Exception)` with no `match`** → over-broad; a bug that raises the wrong error passes. Narrow the type and pin the message.
