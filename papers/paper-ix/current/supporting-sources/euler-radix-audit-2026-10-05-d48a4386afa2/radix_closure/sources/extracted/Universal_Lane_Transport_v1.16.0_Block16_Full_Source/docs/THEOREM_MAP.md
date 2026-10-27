# Theorem map

The release has two controlling theorem sections:

- [`theorem/Universal_Lane_Transport_Theorem_section.tex`](../theorem/Universal_Lane_Transport_Theorem_section.tex), integrated as Section 20;
- [`theorem/Holonomy_Twisted_Lane_Transport_section.tex`](../theorem/Holonomy_Twisted_Lane_Transport_section.tex), integrated as Section 21.

## Layer I: finite profiled lane transport

| Clause | Content |
|---|---|
| L1 | Exact analysis and synthesis at every declared finite resolution |
| L2 | Unique rectangular lane matrix for every morphism |
| L3 | Matrix composition and address-path expansion |
| L4 | Projector-sum refinement and coarse/fine compatibility |
| L5 | Boolean support selectors and exact named residuals |
| L6 | Support propagation and exact residual-composition identity |
| L7 | Transport through additive profile-preserving realizations |
| L8 | Exact kernel of a folded lane record and split-lossless criterion |

Subsequent finite-profile results include the visible-support loss ledger,
exact coordinate coarsening, abelian fold-loss sequences, matrix-category
equivalence, multilinear expansion, factorial/residue realization, typed
native specializations, and ordinary atlas descent under a global address
trivialization.

## Layer II: holonomy-twisted transport

| Result | Content |
|---|---|
| Matrix local system | Local source-target lane matrices and transition maps form a finite local system |
| H1-H5 | Exact section-valued analysis, synthesis, composition, refinement, selectors, and residuals |
| Base-fiber normal form | Global sections are the loop-invariant matrices in one base fiber |
| O1-O5 | Monodromy-orbit projectors, finest untwisted coarsening, fixed-label criterion, pair-orbit selectors, and equivariant refinement |
| Orbital calculus | Pair-orbit indicators form an intertwiner basis with exact path-count multiplication |
| Cyclotomic realization | Split cyclic Fourier idempotents descend rationally through Ramanujan-sum orbit projectors |

## Logical dependency

```text
finite split idempotents
        |
        v
exact local lane matrices -----> local matrix composition
        |                                  |
        v                                  v
coherent address/splitting cocycles -> matrix local system
        |                                  |
        +-------------------------> compatible sections
                                           |
                              connected groupoid evaluation
                                           |
                                           v
                                base-fiber loop invariants
                                           |
                          +----------------+----------------+
                          v                                 v
                  object-address orbits             pair-address orbits
                          |                                 |
                          v                                 v
              finest global lane coarsening      selectors and orbital algebra
```

## Critical distinction

Object-address orbits classify projector-sum global lane coarsenings. Pair
orbits classify invariant matrix positions and support selectors. A transitive
object action can still produce several pair orbits and a nontrivial global
endomorphism algebra.
