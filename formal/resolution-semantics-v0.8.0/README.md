# Resolution Semantics: image and quotient ranks, companion 0.8.0

For every finite decidable simple undirected graph on `Fin n`, this companion
proves that the actual derivative image has `2^(n-c)` elements and the actual
additive quotient of edge fields by that image has `2^(m+c-n)` elements.
Here `m` counts each undirected edge once and `c` counts actual connected
components. Both spaces have complete, duplicate-free lists. Taking `log2`
gives their binary cardinality ranks `n-c` and `m+c-n`.

These are the cardinality forms of manuscript Theorem 6.1(4). The ranks are
defined from the enumerated spaces, not from the target formulas. This
development uses Lean 4.24.0 and bundled `Std`; it does not introduce an
external module/basis library or claim a separately formalized comparison to
such a library's dimension definition.

The [0.7.0 companion](../resolution-semantics-v0.7.0/README.md) and all earlier
companions retain their sources and dated evidence. Nineteen inherited proof
and demo files are preserved byte for byte. The original manuscript and
scaffold remain unchanged. The automatic reconstruction solver still computes
paths without enumerating vertex assignments. The new rank enumerations are
exhaustive reference computations for small examples, with no efficiency claim.

## Reproduce

Run from this directory with the pinned compiler and Python 3.10 or later:

```text
lake build
lake env lean --run GraphRankDemo.lean
python replay.py --lean lean --output ../../verification/current/resolution-semantics-ranks-new-run
```

Use a fresh output directory for each replay. The runner compiles fresh proof
objects, inventories all 266 theorem declarations, checks 73 executable cases
across six demonstrations, and requires mathematical diagnostics for 26
rejection controls. Fifty declarations, eleven cases and six controls are new;
the declaration count includes supporting lemmas and examples.

The [source-bound Windows replay](../../verification/resolution-semantics/ranks-windows-2026-11-01-run2/receipt.json)
passed at source commit `816184a74049e90b3077eace13cd88b1e05b4c42` with no local
companion changes. It records every compiled input hash and exact diagnostics.

## Exact contracts

| Claim | Lean declaration |
|---|---|
| Increasing endpoint pairs index precisely the actual undirected edges | `edge_list_mem`, `edge_list_nodup` |
| The derivative preserves zero and XOR | `derivative_zero`, `derivative_xor` |
| Indexed derivative equality is exactly the inherited edge equation | `derivative_eq_iff` |
| The image list contains each derivative once | `cut_fields_complete`, `cut_fields_nodup` |
| Each derivative fiber has `2^c` elements | `derivative_fiber_count` |
| The quotient identifies exactly fields differing by a derivative | `edge_class_eq_iff` |
| Every quotient class occurs once in its list | `quotient_classes_complete`, `quotient_classes_nodup` |
| Every quotient fiber has image size | `quotient_fiber_count` |
| XOR descends to the quotient and obeys the binary additive laws | `quotient_xor_respects`, `quotient_xor_self`, `quotient_xor_zero`, `quotient_xor_comm`, `quotient_xor_assoc` |
| The actual image has `2^(n-c)` elements | `cut_fields_count`, `cut_count_by_components` |
| The actual quotient has `2^(m+c-n)` elements | `quotient_classes_count`, `quotient_count_by_components` |
| Cardinality ranks are `n-c` and `m+c-n` | `cut_rank_by_components`, `quotient_rank_by_components` |
| The computed component count gives the same formulas | `cut_rank_by_automatic_components`, `quotient_rank_by_automatic_components` |
| Rank plus nullity is `n`; image plus quotient rank is `m` | `graph_rank_nullity`, `graph_quotient_rank_balance` |

The proof first partitions all `2^n` vertex assignments into derivative fibers
of size `2^c`. It then partitions all `2^m` edge assignments into quotient
fibers of size `2^(n-c)`. List completeness and absence of duplicates justify
both finite counts. Positivity proves `c ≤ n` and `n-c ≤ m` before cancellation.
No integrability assumption on a proposed field is needed for these counts.

The natural-number expression is `m+c-n`, or equivalently `m-(n-c)` under the
proved bounds. Writing `(m-n)+c` with truncated natural subtraction would be
wrong, for example on four isolated vertices. The manuscript's integer-valued
notation `m-n+c` has the intended value.

## Executable checks and review

Eleven new cases enumerate the actual image and quotient for the empty graph,
isolated vertices, a single edge, a path, a triangle, a diamond, disconnected
edges with an isolated vertex, the complete four-vertex graph, a triangle plus
an isolated vertex, and two disjoint triangles. Each reports `n,m,c`, both
cardinalities and both ranks. The sixty-two earlier cases remain.

Six new controls reject double-counted edge orientations, full triangle cut
rank, a collapsed triangle quotient, omitted components, premature natural
subtraction, and identifying a non-cut triangle field with zero. Every false
conclusion must fail with the expected `decide` diagnostic. Twenty earlier
controls remain.

[PROOF_AUDIT.md](PROOF_AUDIT.md) records a focused self-review of the exact
finite binary contracts. [PROVENANCE.json](PROVENANCE.json) binds preserved
inputs. This is author-side review and Lean kernel checking, not independent
scientific review. Both inherited two-world obstruction theorems remain
axiom-free; only explicitly inventoried standard axioms are allowed elsewhere.
No accepted theorem may depend on `sorryAx` or a custom axiom.

A verified sparse spanning forest, complexity bounds, general Boolean-valued
transport, projectors, weighted multiresolution and the wider manuscript
remain separate obligations. No model-theoretic or forcing realization claim
is added. The paper remains active development.
