# Partial vertex pin counts: self-review

**Verdict: proved as written**, for the finite binary graph contract below.
This is author-side self-review and Lean kernel checking, not independent
scientific review or a whole-manuscript assessment.

## Claim card

The source contract is Theorem 6.1(3), label `thm:integrability`, in the unchanged
`research/resolution-semantics/Komorebi_Resolution_Semantics.tex`, at base
`1015c0eb1704cffc5e2ec294a15716f5f64c5df3`. Partial pinning refines its unpinned
count and root-fixed uniqueness statements; it is not a separately numbered
manuscript theorem. The raw new proof is `GraphPinning.lean`. Source identities
are recorded in `PROVENANCE.json` and the replay's compiled-input hashes.

For every finite simple undirected graph on `Fin n` with decidable adjacency,
every binary edge field, and every finite list of vertex/value pairs, the
complete duplicate-free list of jointly satisfying vertex labelings has length
`2 ^ unpinnedComponentCount G pins` when a joint solution exists, and zero
otherwise. The count is the length of a complete duplicate-free list of actual
component quotient classes containing no vertex in the pin list. Repeated and
conflicting pins are allowed, and the zero-vertex graph is included.

The total theorem uses the inherited sound and complete exhaustive solver to
express the consistency case distinction. It does not assume that every
integrable field admits every collection of pin values. No component partition,
numerical component count or satisfying witness is required by the total
theorem's caller.

## Dependency graph

```text
Inherited actual component quotient and canonical finite index
  -> pin membership by component
  -> complete duplicate-free list of components containing no pin
  -> number of free component choices

Recursive Boolean offsets, fixed to zero on pinned components
  -> completeness and no duplicates
  -> length 2^u

Two integrating labelings -> their XOR difference is constant along walks
  -> every reconstruction is a unique component offset of a base solution
  -> every pin is preserved exactly when its component offset is zero
  -> translated list has exactly the jointly satisfying labelings
  -> equal lengths of complete duplicate-free lists

Inherited exhaustive solver soundness and completeness
  -> total count formula, including inconsistent edge equations or pins
```

Every leaf is an internal Lean/Std proof or a preserved 0.4.0 declaration.
There is no external mathematical theorem or load-bearing empirical
computation. The examples corroborate the general proof; they do not establish
its quantified conclusion.

## Obligations

| Obligation | Result and decisive evidence |
|---|---|
| Correct admissible domain | Passed: arbitrary finite vertex/value lists, including repeated entries; no uniqueness-of-pins assumption. |
| Actual component count | Passed: `unpinned_components_complete` identifies exactly the quotient classes containing no pinned vertex; filtering preserves no duplicates. |
| Pin values are retained | Passed: `pinned_solutions_complete` requires every original pin; `shift_by_pins_iff` uses a jointly satisfying base, including every pin value. |
| Repeated pins do not consume extra choices | Passed: the mask records whether any vertex in a component is pinned; the count is not the number of list entries. The same-component and duplicate examples exercise this distinction. |
| Offsets are counted exactly once | Passed: `free_assignments_complete`, `free_assignments_nodup` and `free_assignments_length`, followed by injective translation. |
| Every solution is reached | Passed: actual walks from the certified component representatives make the XOR difference constant; the resulting component offsets reconstruct every solution. |
| Invalid pins and nonintegrable fields | Passed: empty output is equivalent to absence of a joint solution; the total count uses the verified solver case distinction. |
| Empty and isolated cases | Passed: one empty labeling for no vertices; pinning an isolated vertex removes its sole choice; an unpinned isolated component retains its independent choice. |
| General proof versus examples | Passed: five numerical examples instantiate the general indexed count; the universal theorem does not depend on finite sample agreement. |
| Assumption controls | Passed by fresh replay: reject counting pin entries, ignoring conflicting pins, and dropping a free isolated component with mathematical `decide` diagnostics. |
| Choice and symmetry | Passed within scope: classical dependencies are inventoried. The vertex ordering is supplied; no symmetry-invariant representative or Boolean projector is asserted. |
| Rank formulas and efficient solver | Out of scope. |
| Arbitrary Boolean algebras, ZFC models or forcing realizations | Out of scope. |

The strongest checked claim is the total finite binary count above, together
with inherited results. Numerical rank formulas and a verified spanning-forest
algorithm remain separate obligations.
