# Move Function

## What it is

Move Function relocates a function (or method) from one module or class to another that is a better owner. The structure of a program reflects where its behavior lives; as understanding improves, behavior often turns out to sit in the wrong place. Move Function is how you correct that: putting code next to the data it works with and the other code it changes alongside.

```python
# before: account.py reaches into a rate table it doesn't own
class Account:
    def overdraft_charge(self):
        if self.type.is_premium:
            base = 10
            return base + max(0, self.days_overdrawn - 7) * 0.85
        return self.days_overdrawn * 1.75

# after: the charge rule lives with the account type that defines it
class AccountType:
    def overdraft_charge(self, days_overdrawn):
        if self.is_premium:
            return 10 + max(0, days_overdrawn - 7) * 0.85
        return days_overdrawn * 1.75
```

## Signals it's time to move

- **Feature Envy.** The clearest signal: a function uses another object's data more than its own. The fix for the smell in [feature-envy.md](./feature-envy.md) is usually Move Function; relocate the behavior to the object whose data it craves. This follows the GRASP Information Expert idea: put behavior where the information lives ([`skills/code-quality/references/design-principles/grasp.md`](../design-principles/grasp.md)).
- **Coupling direction.** When a function in module A depends heavily on module B but barely on its own module, the dependency arrow is fighting the code's location. Moving the function to B can straighten the dependency graph and reduce coupling.
- **Co-change.** When a function consistently changes together with code in another module, you always edit them in the same commit, they probably belong together. This is the [shotgun-surgery.md](./shotgun-surgery.md) signal pointing toward consolidation.

## Doing the move safely

Decide what the function needs from its current context. If it uses only the target's data, the move is clean. If it straddles both, you may need to split it first (extract the part that belongs elsewhere, then move only that), or pass the remaining context as a parameter. Check what the function calls and what calls it: moving it may invert a dependency or create a cycle, which is itself information about whether the move is right.

Preserve behavior at every step and run the tests; see [safe-refactoring.md](./safe-refactoring.md). In Python, also update imports and watch for circular-import risk introduced by the new location.

## Maintaining the old API during migration

When the function is part of a public or widely-used interface, do not break callers in one shot. Move the body to the new home, then leave a delegating function at the old location that forwards to the new one. This is temporarily a [thin-wrapper-function.md](./thin-wrapper-function.md), and that is fine; it exists to keep the old API stable while callers migrate. Once every caller points at the new location (find them with `rg`), delete the delegate. For a deprecation window, mark the old path with a warning so callers know to update.

## When NOT to move

If a function genuinely uses data from several objects in balance, there may be no single better owner: forcing a move just relocates the coupling. And if the "better owner" is a data-only object (a DTO, an ORM row, a config object) that should stay behavior-free, moving behavior in would violate that boundary; see `tell-dont-ask.md` for where that line sits.
