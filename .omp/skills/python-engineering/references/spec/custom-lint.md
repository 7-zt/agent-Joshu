# Custom Lint Rules

A custom lint rule is a project-specific check that fails the build when code violates a convention no general-purpose tool knows about. It is a powerful way to make a rule _enforced_ rather than _remembered_, but it is also a standing maintenance cost and a potential source of false positives that erode trust in the whole lint suite. Most conventions should not become custom rules. The skill here is recognizing the narrow set that should, designing them so they almost never cry wolf, and placing them where they run cheaply.

## When A Custom Rule Is Warranted

The general linter (Ruff) already covers the large catalog of community-wide patterns: unused imports, outdated syntax, common bug shapes. A custom rule is for the project-specific convention that no off-the-shelf rule expresses and that matters enough to enforce mechanically. The conditions that justify one:

- **The rule is project-specific.** A forbidden import path, a dependency-direction boundary ("the domain layer must not import the web layer"), a framework convention ("every handler module exposes a `router`"), an organizational naming or placement rule. These encode local knowledge a general tool cannot have.
- **Violations are frequent or costly enough to automate.** If the convention is broken rarely and caught easily in review, a rule is over-engineering. Automate the one that recurs, or whose violation causes real damage.
- **The check is mechanical.** It can be decided from the code's structure alone, with no understanding of intent. "Does this module import from `app.web`?" is mechanical; "is this abstraction appropriate?" is not and can never be a lint rule.
- **The false-positive rate can be kept near zero.** A rule that fires on legitimate code trains everyone to ignore or suppress it, which poisons the entire lint gate. If you cannot make a rule precise, it is not ready to be a rule.

When a convention fails these tests, it needs judgment, it is rare, it cannot be made precise, it belongs in a review checklist or documentation, not in a linter.

## How To Design A Rule

A good custom rule is **mechanical, static, and low-false-positive**, and it is documented and tested like any other code.

- **Static and structural.** Decide the rule from the source or its AST, not by running the code. Static checks are fast, safe, and deterministic; a rule that needs runtime behavior is the wrong tool.
- **Precise over broad.** Target the specific violation tightly. A rule that flags "imports that look risky" will misfire; a rule that flags "any import of `app.internal` from outside `app/`" is exact. Prefer a narrow rule that catches the real case to a broad one that also catches innocents.
- **A clear, prefixed error code.** Give the rule a stable code with a project prefix (for example `PRJ001`), so it can be referenced, selectively disabled with a justification, and recognized in output. The accompanying message should state what is wrong and what to do instead.
- **Documented and tested.** A custom rule is code: it needs a test that proves it fires on the violation and stays silent on valid code, and a line of documentation explaining its purpose. An undocumented rule that only its author understands becomes an invisible trap for everyone else.

## Ruff Versus Flake8 Plugins

Two practical mechanisms exist for project-specific rules.

A **Flake8 plugin** is the established way to ship custom checks: it is a small Python package that registers an AST visitor and emits error codes under your prefix. It is mature, well-documented, and purpose-built for exactly this: bespoke, project-local rules with full control over the logic. The cost is running Flake8 alongside Ruff solely to host these custom checks.

**Ruff** owns the general linting and is fast, but writing genuinely custom project-specific rules in it is more constrained than authoring a Flake8 plugin. The pragmatic split most projects land on: let Ruff handle all the standard rule families, and use a small Flake8 plugin to carry the handful of project-specific rules Ruff cannot express. Do not run Flake8 to re-check rules Ruff already covers; that is duplicated work and conflicting configuration. If a custom rule's logic later becomes expressible in Ruff (or Ruff grows native support), migrating it back is reasonable; the choice serves rule maintainability, not tool purity. Tooling specifics for each live in the tooling references ([`skills/python-engineering/references/tooling/ruff.md`](../tooling/ruff.md), [`skills/python-engineering/references/tooling/flake8-plugin.md`](../tooling/flake8-plugin.md)).

## Where Rules Run

Custom rules belong in the same two gates as the rest of linting: pre-commit and CI.

- **pre-commit** runs the rule before each commit, catching violations at the earliest cheap moment. This is where a fast, deterministic custom check pays off: the author sees the failure immediately, before review.
- **CI** runs the same rule again as the authoritative gate, because pre-commit can be skipped, uninstalled, or differ across machines. The rule that matters must run in CI regardless of local setup.

Keep the rule fast enough for pre-commit; a custom check that is slow or needs network access belongs in CI only. The relationship between the two gates is covered in [the pre-commit reference](../tooling/pre-commit.md): pre-commit is the early, fast, skippable layer, and CI is the final, complete, authoritative one.
