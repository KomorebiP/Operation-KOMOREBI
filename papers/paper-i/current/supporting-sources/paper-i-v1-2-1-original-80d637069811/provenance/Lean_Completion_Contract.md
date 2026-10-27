# Paper I Lean Completion Contract

Author: Komorebi P.  
Target manuscript release: v1.2.1  
Target Lean component: v1.0.1

## Completion rule

Paper I may be described as theorem-complete in Lean only when every named
mathematical statement below has an imported declaration with hypotheses and
conclusions equal to or stronger than the manuscript statement. A related
special case, computational experiment, or infrastructure lemma does not count
as complete coverage.

Each accepted declaration must compile with the pinned toolchain and dependency
manifest. The imported project must contain no `sorry`, `admit`, `sorryAx`,
project-specific axiom, `unsafe` declaration, or opaque proof substitute. The
kernel audit records the standard Lean/Mathlib principles on which principal
declarations depend.

Methodological prose, figures, numerical samples, bibliographic priority, and
performance claims are outside the theorem-completion denominator. The three
algorithm rows require a proved mathematical specification; code extraction and
performance are separately identified implementation concerns.

## Named manuscript statements

| ID | Manuscript statement | v0.3.0 baseline | v1.0.1 acceptance target |
|---:|---|---|---|
| 1 | Universal one-seed presentation | Partial | Algebraic quotient plus dense-isometric completion into a Banach target and bounded-operator intertwining |
| 2 | Multi-seed presentation | Partial | Quotient presentation and minimal free-rank bridge |
| 3 | Cyclic characterization | Partial | Unrestricted nonzero cardinal-valued equivalence |
| 4 | Quotient monotonicity | Partial | Algebra-homomorphism and change-of-scalars scope |
| 5 | Image-algebra invariance | Partial | Literal image-algebra formulation |
| 6 | Shared direct-sum bound | Missing | Exact theorem |
| 7 | Independent direct-sum formula | Missing | Exact product-algebra theorem |
| 8 | Tensor-product bound | Missing | Exact theorem with the manuscript action |
| 9 | Scalar quotient obstruction | Missing | Exact theorem |
| 10 | Semisimple multiplicity formula | Partial | Finite-product assembly under chosen split algebra and compatible semilinear module equivalences |
| 11 | Full matrix algebra | Near-full | Bridge to general cyclicity and seed rank |
| 12 | Multiplicity obstruction | Near-full | Bridge to general seed rank |
| 13 | Certified single-operator seed number | Missing | Exact least-number theorem from explicit block-generation, polynomial-extraction, and scalar-quotient certificates, together with the canonical polynomial-orbit/`k[T]` module bridge |
| 14 | Certified cyclic matrix criterion | Missing | Cyclicity equivalence from the least-number certificate, with both the geometric-multiplicity/block-multiplicity identification and the minpoly/charpoly bridge supplied explicitly |
| 15 | Exact packet coordinates | Complete | Preserve exact equivalence |
| 16 | Packetwise equality | Near-full | Literal iff theorem |
| 17 | Topological packet isomorphism | Partial | Bounded maps, closed ranges, and continuous linear equivalence for the standard finite product norm |
| 18 | Completion preserves a finite packet split | Missing | Exact closure equality; invariance of the dense submodule is not required |
| 19 | Exact operator reconstruction | Complete | Preserve operator identity |
| 20 | Packet matrix multiplication | Complete | Preserve composition identity |
| 21 | Packet powers | Missing | Finite path expansion for every power |
| 22 | Adjoint reversal | Missing | Exact Hilbert-space identity |
| 23 | Algebraic full block representation | Partial | Arbitrary-block synthesis and algebra equivalence |
| 24 | Dimension count | Missing | Exact finite-dimensional corollary |
| 25 | Algebraic packet support pattern | Partial | Arbitrary nonzero packet-space converse |
| 26 | Reachability obstruction | Missing | Algebraic reachable-support theorem plus the bounded-projector closure obstruction once the algebraic hull lies in its kernel |
| 27 | Coordinate transport | Near-full | Explicit transfer-graph invariance |
| 28 | Naturality of generation and packets | Partial | Complete strict-morphism theorem |
| 29 | Dense realization theorem | Missing | Exact theorem for normed spaces, bounded operator families, and a surjective continuous intertwiner, plus packet-range descent |
| 30 | Typed reachability certificate | Missing | Exact finite quiver certificate |
| 31 | Bilateral-shift seed | Missing | Explicit integer-power family on `ℓ²(ℤ,K)` and least finite dense-generating seed cardinality one |
| 32 | Certified spectral seed number | Missing | Diagonalizable formula from an explicit finite eigenbasis with distinct labels, plus unconditional path and complex-cycle corollaries |

## Algorithm specifications

| ID | Construction | v0.3.0 baseline | v1.0.1 acceptance target |
|---:|---|---|---|
| 33 | Orbit-hull iteration | Python instances | Termination and equality of the stabilized subspace iteration with the finite operator hull; no extraction claim |
| 34 | Transfer-block table | Reconstruction invariant | Proved mathematical specification for block formation, reconstruction, and support output; no edge-list implementation claim |
| 35 | Certified exact graph seed-rank specification | Python instances | Correctness of the noncomputable spectrum maximum from supplied exact spectral certificates; no verified eigensolver claim |

## Release gate

The v1.2.1 gate is satisfied. All 35 rows are classified `Exact` or `Stronger`
in `formalization/lean/LEAN_THEOREM_MAP_v1.0.1.md`; the warning-fatal aggregate
build succeeds; the executable map checker resolves all 84 unique mapped
declarations; the complete direct audit and namespace-wide fail-closed audit
pass; and the manuscript and verification report use the same
certificate-explicit scopes. This gate applies only to the revised statements
above and does not absorb the exclusions in the completion rule.
