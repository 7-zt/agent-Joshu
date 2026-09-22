# Primitive Obsession

## What it is

Primitive Obsession is the habit of representing domain concepts with raw primitives, strings, ints, floats, bare tuples, and untyped dictionaries, where a dedicated type would add safety and clarity. A user ID is "just a string," a currency amount is "just a float," an order status is "just one of these string values," a coordinate is "just a tuple of two numbers," a parsed record is "just a `dict[str, Any]`." Each decision is individually convenient, and collectively they erase the domain from the code.

The cost is that primitives carry no meaning and enforce no rules. A function taking `(str, str, str)` gives the caller no help remembering which string is the email, which is the name, and which is the city, and nothing stops them passing the three in the wrong order. A `float` for money invites a `float` for a quantity to be multiplied with it in the wrong unit. A status represented as a string can hold `"shippped"` and no one notices until production. The type system, which could have caught these, has been told nothing.

## The signals

- **Validation scattered across call sites.** The same `if not re.match(EMAIL_RE, value)` appears wherever an email string arrives, because the string itself guarantees nothing. A value object validates once at construction.
- **Primitives that travel in fixed groups.** Latitude and longitude always passed together, `currency` and `amount_cents` always side by side: these Data Clumps want to be one type.
- **Stringly-typed states and kinds.** A field that is really an enumeration but is stored as a free string, compared with string literals throughout the code.
- **`dict[str, Any]` as a pseudo-record.** Data with a known, fixed shape passed around as a dictionary, where every access is a stringly-typed lookup that the type checker cannot verify and that fails at runtime on a typo.
- **Type-coupled behavior with nowhere to live.** Functions that operate on the primitive (format this phone number, normalize this code) pile up as free functions because there is no type to hang them on.

## When to introduce a domain type

Introduce a **value object** (in Python a `frozen` dataclass, `NamedTuple`, or a small class) when a concept has its own validation rules, invariants, or associated behavior: money, email, date range, coordinate. Introduce an **enum** (`Enum`, `StrEnum`) when a value is one of a fixed, known set; this turns typos into errors and gives you exhaustiveness in `match`. Introduce a **typed record** (`dataclass`, `TypedDict`, Pydantic model) when a `dict[str, Any]` has a known shape, so field access is checked and the structure is documented by the type.

The payoff is concentration: validation happens once at the boundary where the type is constructed, invariants hold everywhere the type is used, and behavior has an obvious home. Illegal states become unrepresentable rather than merely unlikely.

## When primitives are fine

Domain types are not free, they add a definition, a construction step, and a layer of indirection, and over-applying them is its own smell. Primitives are the right choice when:

- **Internal plumbing.** A loop index, a temporary count, a local accumulator; these are genuinely just numbers, and wrapping them adds noise without safety.
- **Truly generic code.** A serializer, a cache, a generic container, or a logging helper that should work for _any_ value has no business knowing about your domain types; primitives and generics are correct there.
- **Performance-critical paths.** Wrapping every element of a large numeric array in a value object can be a real cost. In hot numeric code, arrays of primitives (or NumPy dtypes) are appropriate, and the domain meaning is documented elsewhere.
- **The concept has no rules and no behavior.** If a string is just an opaque label that is never validated, compared against a fixed set, or operated on, a `NewType` alias may be all the clarity it needs, or nothing at all.

The judgment is whether the concept _earns_ a type: does wrapping it prevent a class of error, centralize a rule, or give behavior a home? If yes, introduce the type. If it only adds ceremony, leave the primitive.
