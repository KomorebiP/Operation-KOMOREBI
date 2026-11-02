# Focused self-review: image and quotient cardinality ranks

Verdict: **proved as written** for the finite binary cardinality contracts
below. This is self-review with Lean kernel checking, not independent review.
Reviewed source: `816184a74049e90b3077eace13cd88b1e05b4c42`, especially
`GraphFiniteCounting.lean`, `GraphEdgeSpace.lean`, `GraphQuotient.lean`,
`GraphRanks.lean` and `GraphRankExamples.lean`. No reviewed compiled input was
changed after that source revision.

## Claim card

For every decidable simple undirected graph `G` on `Fin n`, let `m` be the
length of the duplicate-free list of adjacent endpoint pairs `u<v`, and let
`c` be its actual number of connected components. The binary derivative sends
a vertex labeling to the XOR of its endpoints on each indexed edge. Its
actual image has `2^(n-c)` elements; the actual additive quotient of all edge
fields by that image has `2^(m+c-n)` elements. Their cardinality ranks, defined
as `log2` of complete duplicate-free enumerations, are `n-c` and `m+c-n`.
The quotient XOR operation is well-defined and obeys the binary additive laws.

The domain includes zero vertices, no edges, isolated vertices, disconnected
graphs and cycles. There is no supplied consistency assumption, spanning
forest or empirical size bound. Coefficients are Boolean XOR, i.e. the
additive structure over F2. No orientation-dependent sign is used.

## Dependency graph

1. Actual sorted edges → endpoint derivative → equivalence with inherited
   edge equations. Leaves: definitions, finite-list proofs and Boolean cases.
2. The inherited exact `2^c` reconstruction count → equal derivative fibers
   → partition of all `2^n` vertex assignments → exact image cardinality.
   Leaves: preserved `GraphCounting.lean` and its internal Lean dependencies.
3. Image closure under XOR → actual quotient setoid → complete unique class
   list → XOR translation bijects every class fiber with the image → partition
   of all `2^m` edge assignments → exact quotient cardinality.
4. Positive image and quotient counts → `c≤n`, `n-c≤m` → valid natural-number
   subtraction and power cancellation → exact log2 rank formulas.

All load-bearing leaves are internal kernel-checked proofs or stated
definitions. Executed examples and rejection controls check implementations
and assumptions; they do not establish universal claims. There are no new
unchecked external mathematical leaves or circular rank definitions.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Count each real undirected edge once | Passed | `edge_list_mem`, `edge_list_nodup`; orientations sorted by `Fin` order |
| Indexed field uses all original edges | Passed | `derivative_eq_iff` recovers either orientation, using symmetry and looplessness |
| F2 linear behavior | Passed | `derivative_zero`, `derivative_xor`; Boolean case proofs |
| Actual image, no sample surrogate | Passed | `cut_fields_complete`, `cut_fields_nodup` |
| Uniform derivative fibers | Passed | `derivative_fiber_count`; inherited theorem applies because the base is itself a derivative |
| Quotient equivalence and additive descent | Passed | `cutSetoid`, `edge_class_eq_iff`, `quotient_xor_respects` and additive laws |
| Actual quotient, complete without duplicates | Passed | `quotient_classes_complete`, `quotient_classes_nodup` |
| Uniform cosets, not merely equal sample outputs | Passed | `quotient_fiber_count`; injective involutive XOR translation |
| Exhaustive finite counting | Passed | `fiber_partition_length`, `constant_fiber_count` |
| Nonnegative exponents and empty cases | Passed | `component_index_le_vertices`, `cut_rank_le_edges`, positivity and eleven executable cases |
| No premature truncation | Passed | Quotient formula is `m+c-n`; dedicated edgeless rejection control |
| Ranks derived from spaces | Passed | Exact power-of-two counts precede `Nat.log2_two_pow` |
| Module/basis library dimension comparison | Out of scope | Explicit cardinality dimension convention; no external basis API |
| Sparse forest, runtime bound, graph symmetry invariance | Out of scope | No such claim is made |
| Wider Boolean-valued, semantic or forcing claims | Out of scope | Original manuscript unchanged |

## Decisive evidence and reproducibility

The source-bound replay in
`verification/resolution-semantics/ranks-windows-2026-11-01-run2/receipt.json`
compiles all 266 declarations with warnings as errors, inventories their
axioms, executes all 73 cases, and requires all 26 rejection controls to fail
mathematically. Only `propext`, `Quot.sound` and `Classical.choice` are allowed;
the two inherited obstruction theorems remain axiom-free. The receipt records
the exact source revision, every compiled input digest, raw logs and controls.

Run `lake build` and `python replay.py --lean lean --output <fresh-directory>`
with Lean 4.24.0. The eleven new finite cases enumerate actual image and class
lists, including the complete four-vertex graph and two disjoint triangles.
No runtime timing is claimed as a complexity theorem.

## Boundary and final prose review

The strongest supported statement is the exact finite binary cardinality
theorem and its log2 ranks. A module/basis interface, sparse forest algorithm,
complexity bound and the wider paper remain separate work. There is no missing
implication inside the stated cardinality contract. A useful next check is a
verified sparse spanning forest, while preserving this exhaustive reference.

Self-proofreading covered only this edition's new prose and the updated reader
guide. Routine edits checked terminology, references and subtraction notation;
no mathematical-token corrections to inherited sources were made. All nineteen
inherited proof/demo inputs are hash-bound unchanged. No independent reviewer
or whole-manuscript audit is claimed.
