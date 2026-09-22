# Common Standard Library Modules

This file aggregates short references for high-frequency standard-library modules. Each module solves a narrow, recurring problem; reaching for the right one removes hand-rolled code that is easy to get subtly wrong. The modules below are unrelated to each other, so each stands alone; there is no single decision table spanning them.

## pathlib

`pathlib` models filesystem paths as objects instead of strings. A `Path` carries platform-aware semantics: joining with `/`, splitting into `parts`, reading `.name`/`.stem`/`.suffix`, and resolving against the current OS separator.

```python
from pathlib import Path

config = Path("config") / "settings.toml"
text = config.read_text(encoding="utf-8")
for log in Path("logs").glob("*.log"):
    archive(log)
```

Prefer `Path` over `os.path` string manipulation: `config / "settings.toml"` is harder to corrupt than `os.path.join` calls nested inside f-strings, and the object documents intent. Methods like `read_text`, `write_text`, `mkdir(parents=True, exist_ok=True)`, and `iterdir` cover most file chores without the `open` boilerplate.

Accept `os.PathLike[str]` (or `str | Path`) at API boundaries so callers can pass either a string or a `Path`; convert to `Path` once on entry. Do not assume POSIX separators in path literals; let `pathlib` handle the difference between `/` and `\`. Reserve raw strings for paths that cross a boundary requiring text, such as serialization or subprocess arguments.

## enum / StrEnum

`enum` defines a finite, named set of values. Use it when a field has a closed domain, states, modes, categories, instead of bare strings or magic integers that the type checker cannot constrain.

```python
from enum import Enum, StrEnum, auto

class Color(Enum):
    RED = auto()
    GREEN = auto()

class Role(StrEnum):
    ADMIN = "admin"
    VIEWER = "viewer"
```

`StrEnum` (3.11+) members _are_ strings, so they serialize and compare against plain strings directly: convenient for JSON, config, and database columns. A plain `Enum` keeps members distinct from their values, which is safer when you want to forbid accidental string comparison. `IntFlag`/`Flag` model bit-set options that combine with `|`.

Enums make exhaustiveness visible: a `match` over enum members can be checked for missing cases. Avoid enums for open-ended or frequently changing value sets, where they add ceremony without payoff. When serializing, pin the wire format to `.value` (or use `StrEnum`) rather than `.name`, so renaming a member does not silently break stored data.

## dataclasses

`dataclasses` generates `__init__`, `__repr__`, and `__eq__` for classes that are primarily structured data. They suit value objects, configuration bundles, and DTOs where the fields _are_ the type.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, kw_only=True, slots=True)
class Endpoint:
    host: str
    port: int = 443
    headers: dict[str, str] = field(default_factory=dict)
```

Use `default_factory` for mutable defaults; a bare `[]` or `{}` is shared across instances and is a classic bug. `frozen=True` makes instances hashable and immutable; `kw_only=True` avoids positional-argument fragility as fields grow; `slots=True` reduces memory and blocks accidental attribute typos.

Choose dataclasses for plain data with little behavior. Reach for `attrs` when you need richer validation hooks or converters without a full framework, and for `pydantic` when you need runtime parsing and validation of external/untrusted input (request bodies, config files). A dataclass validates nothing at runtime; its annotations are hints, not guards. See [`match-case`](../grammar/match-case.md) for matching against dataclass fields.

## logging

`logging` separates _emitting_ diagnostic events from _deciding_ where they go. The core split: a **library** configures named loggers and emits records but never configures handlers or levels; an **application** owns handler, level, and format configuration once at startup.

```python
import logging

logger = logging.getLogger(__name__)

def fetch(url: str) -> bytes:
    logger.debug("fetching %s", url)
    try:
        return _download(url)
    except DownloadError:
        logger.exception("download failed for %s", url)
        raise
```

Use `logger.exception(...)` inside an `except` block to capture the traceback automatically; never `logger.error(str(exc))`, which discards the stack. Pass message arguments as `%s` parameters, not pre-formatted f-strings, so formatting is skipped when the level is disabled. For structured logging, attach context via the `extra=` dict or a structured-logging library rather than concatenating fields into the message text. Libraries should add a `NullHandler` to their top-level logger to stay silent until the application configures output.

## collections

`collections` provides specialized containers that replace error-prone manual patterns.

```python
from collections import Counter, defaultdict, deque

counts = Counter(words)                 # frequency tallies
groups: dict[str, list[int]] = defaultdict(list)
recent: deque[int] = deque(maxlen=100)  # bounded ring buffer
```

`defaultdict` removes the "check then initialize" dance when grouping; `Counter` gives `most_common` and arithmetic on tallies; `deque` offers O(1) appends/pops at both ends and a `maxlen` ring buffer that a `list` cannot do efficiently. `namedtuple` predates dataclasses and still fits lightweight immutable records, especially tuple-compatible return values, but for anything with behavior, defaults, or evolving fields, prefer a `@dataclass`, which is more readable and extensible.

## typing runtime utilities

Most of `typing` is erased at runtime, but a few utilities are meant to run. `typing.get_type_hints(obj)` resolves annotations to real objects, evaluating string/forward references; the correct entry point for frameworks that read annotations, instead of touching `__annotations__` directly. `TypeGuard` (and 3.13's `TypeIs`) annotate a function's return so the type checker narrows the argument on a `True` result:

```python
from typing import TypeGuard

def all_str(items: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in items)
```

`@runtime_checkable` lets a `Protocol` be used with `isinstance`, but it checks only attribute _presence_, not signatures, so treat it as a coarse guard. For runtime introspection on Python 3.14+, prefer `annotationlib.get_annotations()`, which is designed around deferred-annotation semantics. Keep runtime type logic at boundaries; do not scatter `isinstance` ladders through code the type checker could verify statically.
