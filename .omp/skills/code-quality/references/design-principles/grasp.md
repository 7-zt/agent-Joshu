# GRASP: General Responsibility Assignment Software Patterns

## What it is

GRASP is a vocabulary of nine heuristics for the single most common design question: _where should this responsibility go?_ Where does this behavior belong, which object should create that one, who coordinates a use case, where do we put a rule so that change stays contained. Unlike GoF patterns, GRASP patterns are not structures you build; they are reasoning tools for assigning responsibility well. They pair naturally with SOLID (see [solid.md](./solid.md)) and with [tell-dont-ask.md](./tell-dont-ask.md).

The main misuse is treating GRASP as a UML-driven process, or reading "Controller" as "web controller" and then piling business logic into request handlers. Used well, GRASP is just a precise way to talk about responsibility placement.

## The nine patterns

**Information Expert.** Assign a responsibility to the class or module that has the information needed to fulfill it. Behavior gravitates toward the data it operates on. This is the engine behind [tell-dont-ask.md](./tell-dont-ask.md) and the antidote to the "feature envy" smell where a function reaches deep into another object's fields to make a decision.

**Creator.** Assign the responsibility of creating an object B to a class A that aggregates, contains, closely uses, or has the initializing data for B. It puts construction where the knowledge to construct already lives, reducing coupling. When creation logic is complex enough to vary, this is where a Factory becomes justified.

**Controller.** Assign the responsibility of handling a system operation (a use case) to a coordinating object that is _not_ the UI and _not_ the domain logic itself. The controller's job is thin coordination: receive the request, delegate to the domain, return a result. In Python a CLI command handler or an API view should be this thin controller, with business rules living in a core module.

**Low Coupling.** Assign responsibilities so that dependencies between modules stay low. Lower coupling means a change in one place propagates to fewer others, and units are easier to test and reuse in isolation. It is a force to balance, not an absolute; some coupling is necessary.

**High Cohesion.** Assign responsibilities so that each module's contents are strongly related and focused. High cohesion is the positive form of [solid.md](./solid.md)'s SRP; it keeps a module understandable and gives it a single clear reason to change. Low coupling and high cohesion are evaluated together; optimizing one while ignoring the other produces bad designs.

**Polymorphism.** When behavior varies by type, assign the varying behavior using polymorphism (in Python: duck typing, `Protocol`-based dispatch, a dispatch map, or `functools.singledispatch`) rather than scattered `if/elif` type checks. This localizes each variant and makes adding a new one an addition rather than an edit: the mechanism behind OCP.

**Pure Fabrication.** When no domain concept is the right home for a responsibility, invent a non-domain object to hold it; a service, mapper, adapter, repository, or policy function. This keeps domain objects cohesive and prevents you from polluting them with infrastructure concerns purely to satisfy Information Expert. Pure Fabrications are legitimate and common; the caution is not to overuse them as a dumping ground.

**Indirection.** Assign a responsibility to an intermediate object or function to decouple two units that would otherwise be directly coupled (an adapter between your core and a third-party client, for example). Indirection is a tool for Low Coupling, but each layer adds a hop to trace; add it for a real coupling problem, not reflexively.

**Protected Variations.** Wrap a predicted point of instability behind a stable interface so that variation on one side does not ripple to the other. This is the unifying idea behind OCP, DIP, Indirection, and Polymorphism. The critical word is _predicted_; protect variations that are real and identified, not every point that _might_ someday change, or you drift into the speculative generality that [yagni.md](./yagni.md) warns against.
