# Traversal solver: self-review

**Verdict: proved as written**, for the supplied-traversal contract below.
This is author-side self-review and Lean kernel checking, not an independent
scientific review or a whole-manuscript assessment.

## Claim card

This is an algorithmic refinement of Theorem 6.1, label `thm:integrability`, in
the unchanged `research/resolution-semantics/Komorebi_Resolution_Semantics.tex`.
The base is `7266ebaf73c6b03383d761672fd85e733b612bbd`. The raw new proof is
`GraphTraversalSolver.lean`; provenance and replay input hashes identify the
reviewed artifacts.

For every simple undirected graph on `Fin n` with decidable adjacency, every
certified finite component index with actual representative-to-vertex walks,
every binary edge field and every finite list of vertex/value pins,
`traversalSolve` returns a labeling satisfying every edge and pin exactly when
one exists. It agrees with the exhaustive reference on existence. If the pins
cover every component, any returned labelings of the two solvers are equal.
Repeated and conflicting pins, isolated vertices and zero vertices are allowed.

The component index and walks are part of the input contract. This does not
claim to construct them from an arbitrary graph. Actual finite walks are
required; an unchecked partition, guessed path sum or collection of unrelated
edge samples is not a substitute. Acyclicity, a linear runtime and exact
reference output under incomplete pinning are not asserted.

## Dependency graph

```text
Actual checked walks + inherited walk-integral identity
  -> potential equals XOR of a witness's endpoint values
  -> common component root makes the candidate integrate every edge

Jointly satisfying witness + actual pin selected in its component
  -> selected root value equals the witness's root value
  -> candidate retains every original pin

Complete edge-and-pin check -> soundness of any returned labeling
Candidate passes whenever a witness exists -> completeness
Soundness + completeness -> none iff no solution
Inherited reference correctness -> agreement on existence
Inherited uniqueness with component-covering pins -> equality of results
```

Every leaf is an internal Lean/Std proof or a preserved 0.5.0 declaration.
No external mathematical theorem or load-bearing empirical computation is
used. Examples corroborate the general argument; they do not establish the
universal claim.

## Obligations

| Obligation | Result and decisive evidence |
|---|---|
| Admissible traversal data | Passed: a checked actual component index and `Walk` values fix all endpoints and certify every used edge. |
| No hidden forest assumption | Passed: soundness/completeness use actual walks and common component representatives; no acyclicity, uniqueness or shortest-path premise occurs. |
| Pins away from roots | Passed: `component_root_value_at_pin` translates any component pin back along its supplied walk. |
| Repeated and conflicting pins | Passed: a first matching pin chooses a root, while the final predicate retains every pin. Completeness uses joint consistency; soundness needs no consistency assumption. |
| Every edge is checked | Passed: the final predicate quantifies over all adjacent vertex pairs, including edges outside the supplied walks. The triangle case exercises that distinction. |
| All solutions versus one candidate | Passed: the endpoint identity proves that any jointly satisfying witness makes this candidate satisfy all constraints; no finite sample or search heuristic supplies completeness. |
| Comparison with the reference | Passed: general agreement concerns existence. Equality uses the explicit component-covering pin hypothesis. A changed unpinned root gives a concrete counterexample to unconditional equality. |
| Changed path and root choices | Passed: executable diamond certificates use another path and another root; the general proof is quantified over every supplied checked traversal. |
| Empty and isolated cases | Passed: no vertex access is needed on `Fin 0`; an isolated pin fixes its singleton component. |
| Enumeration and runtime claims | Passed within scope: `traversalSolve` constructs one candidate and calls `checkSolution`, without calling the assignment enumerator. It may recompute path integrals; no runtime bound is claimed. |
| Rejection controls | Passed by source-bound fresh replay: reject omitted non-tree edges, ignored non-root pins, contradictory pins and unconditional exact reference equality. |
| Automatic forest/traversal construction and rank formulas | Out of scope. |
| General Boolean algebras, ZFC models and forcing realizations | Out of scope. |

The strongest checked statement is sound and complete reconstruction from the
supplied checked traversal, together with the inherited results. Constructing
the traversal automatically and proving numerical rank formulas remain
separate obligations.
