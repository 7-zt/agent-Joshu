# Visitor

The Visitor pattern separates operations from the object structure they operate on. It lets you define new operations over a fixed set of node types without modifying those types. Each node type implements an `accept(visitor)` method that calls the visitor's corresponding `visit_*` method, enabling double dispatch.

The pattern is most valuable when the set of types is stable but the set of operations changes frequently. It inverts the usual tradeoff: adding a new operation is easy (add a new Visitor class), but adding a new node type requires updating all existing Visitors.

## Structure

- Element (node type): declares `accept(visitor)`.
- ConcreteElement: implements `accept` by calling `visitor.visit_concrete_element(self)`.
- Visitor (interface): declares a `visit_*` method for each element type.
- ConcreteVisitor: implements each `visit_*` with operation-specific logic.

## When The Pattern Fits

- The node type hierarchy is stable. New types are rare.
- New operations over the structure are common.
- Operations need access to the concrete type without `isinstance` cascades.
- The operation logic should not pollute the data classes.
- Multiple independent traversal concerns exist (lint, transform, serialize, pretty-print).

## When The Pattern Does Not Fit

- Node types change frequently. Every new type forces updates to all Visitors.
- The structure is simple enough that a single recursive function or `match`/`case` suffices.
- Only one or two operations exist. The ceremony of accept/visit adds no clarity.
- The language supports pattern matching or `singledispatch`, making double dispatch unnecessary.
- Operations do not need the full concrete type; a common interface method is enough.

## Common Implementation Issues

**Traversal responsibility.** Who walks the tree; the visitor, the node's accept method, or an external iterator? Keep it consistent within a structure. Mixing strategies leads to nodes being visited twice or skipped.

**Return values.** Classic Visitor uses void visits with accumulated state. For functional traversals where each visit produces a value, consider returning values from visit methods rather than mutating the visitor.

**Default handling.** Provide a `visit_default` or `generic_visit` for unknown node types. Without it, adding a new node type silently skips its visit rather than raising. This is especially important in evolving trees.

**Composite children.** For tree structures, decide whether `accept` recurses into children automatically or requires explicit visitor logic. Auto-recursion is convenient but may hide traversal order; explicit traversal gives the visitor control over depth-first vs breadth-first and allows pruning.

## Python example

Python's `ast.NodeVisitor` is a practical Visitor variant rather than the classic `accept()`-based double-dispatch form. AST nodes do not implement `accept()`; `NodeVisitor.visit()` dispatches to `visit_<NodeType>`, while `generic_visit()` walks the child nodes:

```python
import ast


class DefinitionCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.names.append(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.names.append(node.name)
        self.generic_visit(node)


tree = ast.parse("""
class User:
    def display_name(self):
        return "Ada"
""")

collector = DefinitionCollector()
collector.visit(tree)

assert collector.names == ["User", "display_name"]
```

The AST nodes stay unchanged while the visitor adds a new operation over them. Calling `generic_visit()` from a specialized method continues traversal into that node's children; omitting it prunes that subtree.

## Relationship To Strategy

[Strategy](./strategy.md) varies the algorithm behind a stable call site. Visitor varies the operations over a stable type hierarchy. Strategy is per-call-site; Visitor is per-node-type-family. If you have one operation over many types, Visitor might be overkill; [Strategy](./strategy.md) or a plain function suffices.
