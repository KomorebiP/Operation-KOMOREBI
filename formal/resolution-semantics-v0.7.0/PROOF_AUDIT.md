# Automatic traversal: self-review

**Verdict: proved as written**, for the finite binary graph contract below.
This is author-side self-review and Lean kernel checking, not independent
scientific review or a whole-manuscript assessment.

## Claim card

This algorithm refines Theorem 6.1, label `thm:integrability`, in the unchanged
`research/resolution-semantics/Komorebi_Resolution_Semantics.tex`. The base is
`be189a9d7d01ff01380bc48cafaf3518eef4473b`. Raw new proofs are
`GraphPathSearch.lean` and `GraphAutomaticTraversal.lean`; provenance and replay
input hashes bind the reviewed sources.

For every simple undirected graph on `Fin n` with decidable adjacency,
`buildTraversal` computes a certified actual component index and actual finite
walks from its representatives to all vertices. For every binary edge field
and finite list of vertex/value pins, `automaticSolve` returns a jointly
satisfying labeling exactly when one exists. It agrees with the exhaustive
reference on existence; equality of returned labelings is proved when the
pins cover all components. No traversal, partition, component count, field
integrability assumption or consistency witness is supplied by the caller.

The zero-vertex graph and arbitrary repeated or conflicting pins are included.
The ordering of `Fin n` is supplied. No symmetry-invariant representative,
acyclicity, sparse forest, runtime bound or wider semantic realization is
asserted.

## Dependency graph

```text
Array size/index certificates -> dependent cache lookup equals tabulation
Actual empty walks + actual adjacent-edge extension
  -> every walk of length <= k is covered in k rounds

Auxiliary zero field -> simple representative of any graph walk
Duplicate-free vertex list -> at most n distinct vertices
  -> every reachable pair is covered after n rounds
Stored Walk values -> no false reachability

Complete finite path table -> first reachable representative
Reachability equivalence -> representative constant on components
Representative idempotence + duplicate removal
  -> actual component index with coverage and no unused labels
Checked option extraction -> actual representative-to-vertex walks

Constructed traversal + inherited traversal solver correctness
  -> automatic solver soundness and completeness
  -> reference agreement on existence
  -> equal outputs with component-covering pins
```

Every leaf is an internal Lean/Std proof or a preserved 0.6.0 declaration.
There is no external theorem or load-bearing empirical computation. The
runtime examples corroborate the general proof; their tested graph sizes are
not a bound on its quantified claim.

## Obligations

| Obligation | Result and decisive evidence |
|---|---|
| Correct stored objects | Passed: each table entry is `Option (Walk G v w)`, with actual edges and endpoints. Array size and entry-index proofs justify every lookup and transport. |
| Search-round completeness | Passed: walk induction removes one edge per round; preservation retains earlier paths. |
| Universal finite bound | Passed: a simple walk has a duplicate-free vertex list, whose length is at most `n`; the proof covers `Fin 0` without a fabricated vertex. |
| Auxiliary field assumption | Passed: simple-walk reduction uses the identically zero auxiliary field and its proved zero integrals, independent of the caller's proposed edge field. |
| No false components or omitted vertices | Passed: stored paths characterize actual reachability. Root selection is constant on components; representative idempotence, duplicate removal and position recovery establish all `ComponentIndex` laws. |
| Computable data versus proof choice | Passed: roots use finite `find?`, positions use decidable finite recursion, and walks are extracted from stored options. Classical proof dependencies are inventoried; no classical choice constructs operational paths. |
| Arbitrary proposed fields and pins | Passed: soundness is the full edge-and-pin predicate. Completeness requires only existence of a joint solution. Nonintegrable, asymmetric and contradictory examples exercise rejection. |
| Empty and isolated cases | Passed: empty arrays and a zero-length root list yield zero components and one empty labeling. Isolated vertices remain distinct singleton components. |
| Reference comparison | Passed: agreement on existence is general; equality uses the inherited component-covering pin hypothesis. |
| Array implementation | Passed: the array cache replaces a slow linked prototype while preserving the lookup theorem. Final sources use the array implementation. No timing claim is promoted to a theorem. |
| Concrete outputs | Checked by replay: 21 new executable cases include 8/32-vertex paths and four component counts. The generic correctness theorems establish the universal conclusion. |
| Assumption controls | Passed by source-bound fresh replay: reject zero/insufficient rounds, merged disconnected components, contradictory pins and a phantom empty component. |
| Sparse spanning forest, rank and runtime formulas | Out of scope. |
| General Boolean algebras, ZFC models and forcing realizations | Out of scope. |

The strongest checked statement is automatic sound and complete finite binary
reconstruction, with an internally constructed actual traversal, together with
the preserved results. Rank formulas and a verified sparse forest implementation
remain separate obligations.
