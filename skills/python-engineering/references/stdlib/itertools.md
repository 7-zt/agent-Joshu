# itertools

`itertools` provides iterator building blocks that compose into lazy data pipelines. Each function consumes and produces iterators, computing values one at a time instead of materializing intermediate lists. This keeps memory flat over large or infinite sequences and lets a pipeline stop early without doing surplus work.

## Lazy Evaluation

An itertools pipeline does no work until something pulls from it. Chaining `map`, `filter`, and itertools functions describes a computation; iterating runs it element by element. The payoff is memory and short-circuiting: a stage feeding `next()`, `any()`, or a sliced consumer never processes elements past what the consumer asks for.

```python
from itertools import islice

# Reads only the lines needed, not the whole file.
first_errors = islice((ln for ln in log_file if "ERROR" in ln), 10)
```

The cost is that laziness is easy to lose. Wrapping a stage in `list()`, `sorted()`, or `len()` forces full evaluation; do it deliberately at the point you actually need a concrete collection.

## Common Recipes

- `chain(a, b, ...)` and `chain.from_iterable(iterables)` concatenate iterables without building a combined list: useful for flattening one level.
- `islice(it, start, stop, step)` slices an iterator. Unlike list slicing it cannot index backwards, but it works on infinite and streaming sources.
- `groupby(it, key)` groups _consecutive_ elements sharing a key. Input must already be sorted by that key, or groups fragment. This trips up newcomers expecting SQL-style grouping.
- `product`, `permutations`, `combinations` generate combinatorial sequences lazily: handy for test matrices and parameter sweeps, but growth is exponential, so guard the input size.
- `pairwise(it)` (3.10+) yields overlapping adjacent pairs `(s0,s1), (s1,s2), ...`, cleaner than manual index zipping for deltas and windows.
- `starmap(func, arg_tuples)` applies a function to pre-grouped argument tuples: `map` when arguments arrive already packed.
- `batched(it, n)` (3.12+) yields tuples of up to `n` items, the standard way to chunk a stream for paged requests or bulk writes. Before 3.12, an `islice`-based helper fills the same role.
- `accumulate`, `takewhile`, `dropwhile`, `count`, `cycle`, `repeat`, `tee`, `zip_longest`, `compress`, `filterfalse` cover running totals, conditional slicing, and stream alignment.

## When It Helps vs Obscures

itertools improves clarity when it names a recognized operation: `batched` says "chunk", `pairwise` says "adjacent windows", `chain` says "concatenate". Readers who know the vocabulary grasp intent faster than they would from hand-rolled index arithmetic. It also matters when the data does not fit in memory or the source is unbounded; there a lazy pipeline is the only sensible shape.

It obscures when a plain comprehension or loop would read more directly. A deep stack of `chain`/`filter`/`starmap`/`takewhile` can hide the actual transformation behind composition; a single `for` loop with a clear body is often better. Reach for itertools when it removes bookkeeping, not when it adds a layer of indirection over simple logic.

## Multiple-Consumption Pitfall

An iterator is exhausted after one pass. This is the most common itertools bug:

```python
results = map(transform, records)   # an iterator, not a list
total = sum(r.size for r in results)
for r in results:                   # empty: already consumed by sum()
    save(r)
```

If you must traverse the data twice, materialize it once (`results = list(map(...))`) or duplicate the iterator with `itertools.tee`. Note that `tee` buffers everything consumed from one branch but not yet from the other, so two branches advancing far apart can use as much memory as a list: `tee` helps only when the branches stay roughly in step. The same single-pass rule applies to `groupby`: its group iterators are valid only until you advance to the next group, so capture a group's contents before moving on if you need them later.
