# Docstrings And API Docs

Once type annotations carry the static contract, a docstring's job changes. It is no longer the place to record parameter types and return types, the signature already does that, machine-checkably, and repeating it only creates a second copy that drifts out of sync. The docstring's job is everything the signature _cannot_ express: what the function means in the domain, what it promises and assumes, what it touches in the outside world, and how to use it correctly. The core skill is placing each piece of information where it belongs and writing a docstring only when it adds something the reader could not already see.

## Where Information Belongs

A modern Python API spreads its documentation across several surfaces, and most documentation problems are really placement problems; the right fact in the wrong place, or the same fact in three places. The first question for any piece of information is not "how do I phrase it" but "which surface owns it."

| Information | Owning surface | Why |
| --- | --- | --- |
| Parameter and return _types_ | Signature / annotations | Machine-checked, IDE-read; a copy in the docstring drifts |
| Domain meaning, business rules | Docstring | The type system cannot express what a value _means_ |
| Value ranges, units, shape, dtype | Docstring or `Annotated`/`Field` | Depends on whether a machine needs to read it |
| Cross-parameter constraints | Docstring or a validator | A single annotation cannot relate two parameters |
| Side effects, resource lifecycle | Docstring | Callers must know about IO, network, DB, global state |
| Exception semantics | Docstring | Python types do not express "raises" |
| Machine-readable field constraints | Schema metadata (`Field(...)`) | Feeds validation and generated API docs |
| Worked examples | Docstring, README, or tests | Best when also executed, so they cannot rot |
| Version changes, deprecations | Release notes, `warnings.deprecated()` | Serves readers, checkers, and runtime together |

The single most common mistake is duplicating a fact that a more authoritative surface already owns: writing `min_length=3` in prose when a `Field(min_length=3)` already declares it, or restating a type the annotation already gives.

## When A Docstring Adds Value

A docstring earns its place when it tells the reader something the signature cannot. The clearest signals:

- **Semantics.** What does the returned value _mean_? `-> str` says it is a string; the docstring says it is "a normalized form suitable for case-insensitive lookup, not a display name."
- **Constraints the type cannot hold.** A window that must be odd, a list that must be non-empty, a timestamp that must be UTC; the annotation says `int`, `list`, `datetime`, and the docstring carries the rest.
- **Side effects.** Anything observable beyond the return value: a database write, a network call, a mutated argument, a cache populated, a file created. Callers need this to use the function safely, and no annotation reveals it.
- **Exception semantics.** Which exceptions a caller is expected to handle, and what they mean, not an exhaustive list of everything that could propagate, but the ones that are part of the contract.

```python
def normalize_username(raw: str) -> str:
    """Return a normalized username for account lookup.

    Leading and trailing whitespace is stripped and the result is
    case-folded, so it is suitable for case-insensitive comparison. The
    result is not guaranteed to be a valid display name.
    """
    return raw.strip().casefold()
```

Here `raw: str -> str` is already in the signature; the docstring adds the lookup semantics, the case-folding rule, and the explicit limit ("not a display name"). The bad version restates the function name ("Normalize username") or re-types the signature ("raw is a str, returns a str").

## When A Docstring Is Noise

A docstring that repeats the signature is worse than none; it adds maintenance cost and a second source of truth that will eventually contradict the first. Skip or trim the docstring when:

- It would only restate types already in the annotations (`user_id (str): the user id`).
- It would only echo the function name (`def save_user(...): """Save a user."""`).
- The function is a small, private helper whose name and signature already say everything.
- It would repeat a constraint already declared in schema metadata.

Coverage-driven docstring mandates ("every function must have a docstring") tend to manufacture exactly this noise. A linter can check that a docstring _exists_ and that its sections are well-formed; it cannot check that it says anything useful. Treat docstring linting as a low-level hygiene gate, never as evidence that the documentation is good.

## Docstring Styles

Three formats are in wide use, and the skill does not force one; the choice follows the project's documentation needs, not fashion.

- **Google style** uses `Args:`, `Returns:`, `Raises:` sections. It is light, readable, and well-suited to general engineering APIs and backend services. With full type annotations, omit the types from the sections (`host: the bind target`, not `host (str): the bind target`).
- **NumPy / numpydoc style** uses underlined sections (`Parameters`, `Returns`, `Notes`, `Examples`). It is more structured and the right fit for scientific and data APIs, where shape, dtype, units, mathematical definitions, and examples carry real weight. It is overkill for short business helpers.
- **reStructuredText / Sphinx** uses field lists (`:param x:`, `:returns:`) and integrates with a Sphinx documentation site, cross-references, and version directives. It suits published libraries and frameworks; for internal code its syntax noise outweighs the benefit.

Whatever the style, with annotations present the rule is constant: do not write the types into the prose. Let the signature own the types and let the docstring own the meaning.

## Schema-Driven Documentation

For web APIs and data models built on tools like Pydantic and FastAPI, the type annotations and field metadata become the single source of truth for validation, serialization, _and_ generated documentation. A field's type, its constraints (`Field(gt=0, le=100)`), and its description (`Field(description=...)`) flow into the generated OpenAPI/JSON schema. In this world the docstring's territory shrinks to the part schema cannot express: the higher-level business semantics, transaction behavior, and cross-field relationships:

```python
class CreateOrderRequest(BaseModel):
    sku: Annotated[str, Field(min_length=3, description="Public stock keeping unit.")]
    quantity: Annotated[int, Field(gt=0, le=100, description="Units requested.")]
```

The constraints and per-field descriptions live in `Field(...)`, which feeds the schema directly. A docstring on the endpoint then explains what the operation _does_, "reserves inventory before writing the order; on reservation failure no order is created", which no field metadata can capture. The failure mode to guard against is maintaining the same sentence in `Field(description=...)`, the model docstring, and a hand-written OpenAPI description at once. Pick the source of truth and let the others reference it.

## Documentation Sites Versus Docstrings

A docstring documents one object; it cannot replace a documentation site. Tutorials, how-to guides, design rationale, and migration notes are narrative documents that no amount of per-function docstring adds up to. A tool like Sphinx with `autodoc` can pull docstrings into an API reference, but an auto-generated reference is not the same as good documentation; the narrative still has to be written by hand. One practical caution: `autodoc` imports the module to read it, so any import-time side effect will run during the doc build; keep module import clean (the same discipline [structure](../project/structure.md) asks for) and the doc build stays predictable.
