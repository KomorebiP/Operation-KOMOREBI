# Block 05 semantic review

This review checks the meaning and dependency boundaries of the new public types. It is a reviewed correspondence artifact, not a Lean interpretation of the manuscript's prose. Final `#check`, full `#print`, axiom, and ownership receipts are retained under the accepted audit output.

| Public construction | Actual object and hypotheses | Not assumed or silently substituted |
|---|---|---|
| `polynomialCokernelMap` and exact kernel | Actual `Module.AEval' T`, scalar-image submodule, `range(aeval T p)`, quotient representative | No assumed kernel certificate, no quotient selected from a dimension |
| `polynomialQuotientEquivCokernel_mk` | Class of a vector maps to class of the same vector | Not only an abstract existence equivalence |
| `intrinsicMultiplicity_X_sub_C_eq_eigenspace` | Finite-dimensional endomorphism over any field; existing intrinsic residue-field dimension; actual `Module.End.eigenspace` | No diagonalizability, Jordan basis, or multiplicity input |
| `operator_seedFinrank_eq_spectralSeedMaximum` | Finite-dimensional endomorphism over an algebraically closed field; actual algebra spectrum; canonical seedFinrank | No supplied primary decomposition, eigenbasis, rank equality, or eigensolver output |
| Cardinal `seedRank` corollary | Same objects, cardinal cast of the natural maximum | Not a separately invented rank function |
| `spectralSeedMaximum_attained` | Nonzero finite-dimensional space over an algebraically closed field | No false nonempty-spectrum claim for the zero space |
| Geometric cyclic criteria | Nonzero finite-dimensional space whose original field is algebraically closed | Not scalar extension from an arbitrary base field |
| `cyclicMinpolyQuotientEquiv` | An actual k[t]-linear equivalence constructed from a cyclic vector | Not a count certificate or executed canonical-form algorithm |
| `hasCyclicVector_iff_minpoly_quotient_presentation` | Actual polynomial-module equivalence, in both directions | Does not assert that an ordered invariant-factor algorithm was implemented |

## Why the proof is not circular

The maximum functions are defined from the dimensions of actual eigenspaces. Seed rank is not part of those definitions. Boundedness is obtained from the already-proved intrinsic seed theorem. Equality follows because monic irreducibles over an algebraically closed field are exactly the linear factors, and the new residue/cokernel argument identifies each corresponding dimension. The prior seed theorem is reused as a proved theorem, not passed as a new input to the public statement.

## Why the general result is not only a diagonalizable special case

The residue/cokernel argument applies to every finite-dimensional endomorphism. Rank-nullity does not require a basis of eigenvectors. The regression suite includes the literal nonzero square-zero action on C[t]/(t^2) and a proof excluding an eigenbasis indexed by Fin 2. The older self-adjoint result remains unchanged, but it is not the premise of this new arbitrary-operator result.

## Publication coverage decision

Exactly `PSC-I-C-ALGEBRAICALLY-CLOSED-SINGLE-OPERATOR` moves from partial to covered. The exact maximum over the actual spectrum is proved, with the empty natural maximum interpreted as zero. The printed corollary inherits the finite-dimensional scope of the surrounding single-operator result. All 108 stored statement, source-proof, and source-location/hash fields remain identical to Block 04.

`PSC-I-C-CYCLIC-MATRIX` remains partial. Native algebraically closed cyclicity and an actual one-factor polynomial-module presentation are added to its correspondence, but the printed scalar-extension clause is not yet assembled.

## Remaining six-way criterion obligations

A future proof must use an actual scalar extension, such as `T.baseChange K` on `K ⊗[k] V`. It must justify preservation and reflection of cyclicity or of the minimal/characteristic polynomial equality. Merely assuming an arbitrary new operator over an algebraically closed field is not that construction. Likewise, the intrinsic-primary and rational-canonical clauses must be matched to the paper's exact statements rather than recognized only informally as classical equivalents.
