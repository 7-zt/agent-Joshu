# Tell, Don't Ask

Tell, Don't Ask says: instead of pulling data out of an object and making decisions about it
from the outside, push the decision into the object that owns the data. Tell the object what
you want done; do not ask it for its internals and then act on its behalf.

The principle is about _where behavior lives relative to the data it depends on_. When the
data and the rules that govern it sit together, the rules can rely on invariants the object
maintains, and changes to those rules have one home. When callers repeatedly read fields and
assemble rules externally, the logic scatters, and the object cannot protect its own
consistency.

## The shape of the problem

"Ask" code reads state and branches on it from outside:

```python
# Ask: caller pulls data out and decides
if account.balance >= amount and not account.is_frozen:
    account.balance -= amount
    account.last_debit = now()
```

Every caller that debits an account must remember the same checks and the same bookkeeping. If
a new rule appears (overdraft limits, holds, audit logging), every site needs updating, and
any site that forgets leaves the account in an invalid state.

"Tell" code moves the decision inside:

```python
# Tell: object owns the rule and its invariants
account.debit(amount)   # raises if frozen or insufficient
```

The account now enforces its own invariants. Callers express intent. The rule has one home,
and the object can never be driven into an inconsistent state through this path.

## Relationship to encapsulation

Tell, Don't Ask is encapsulation viewed from the caller's side. Encapsulation says an object
should hide its internal state; Tell, Don't Ask says callers should not need that state in the
first place; they should hand the object a command and trust it to maintain its own
invariants. The two reinforce each other: an object that exposes behavior instead of raw state
keeps its data private and meaningful.

It also overlaps with the GRASP [Information Expert](./grasp.md) heuristic (assign a
responsibility to the class that has the information to fulfill it) and with the
[Law of Demeter](./law-of-demeter.md) (don't reach through structure to make external
decisions). All three push behavior toward the data.

## When asking IS appropriate

Tell, Don't Ask is a guideline for protecting invariants in objects that own behavior. It is
not a ban on reading data. Asking is correct when there is no invariant to protect:

- **Queries and reporting.** Computing totals, aggregates, and summaries inherently reads many
  fields across many objects. Forcing this into command methods on each object distorts the
  model.
- **Serialization and DTOs.** Turning an object into JSON, a row, or a wire format is pure
  data access. A data transfer object or an API schema should expose its fields plainly.
- **UI rendering.** Display code reads model state to draw it. That is its job; it is not
  making domain decisions the model should own.
- **Read models.** In systems that separate reads from writes, the read side is deliberately
  data-oriented and transparent.

The discriminator: is the caller _deciding something the object should own_ (a business rule,
a state transition, an invariant), or is it _reporting / transforming / displaying_ state that
genuinely belongs to the caller's concern? The first is a Tell, Don't Ask violation; the
second is normal and healthy.

## Common mistakes

- **Eliminating all getters.** Some readers take the principle to mean objects should never
  expose data. That breaks reporting, serialization, and UI, and produces awkward command-only
  models. Queries are fine.
- **Stuffing behavior into DTOs and dataclasses.** A pure data carrier should stay a data
  carrier. Adding domain commands to a transport object blurs its boundary and couples it to
  rules it has no business knowing. Add behavior to data only when the data has invariants to
  protect.
- **Hiding expensive work behind innocent-looking properties.** A `property` that triggers I/O
  or heavy computation surprises callers who expect cheap attribute access. Tell, Don't Ask
  argues for behavior near data, not for disguising side effects as attribute reads.
