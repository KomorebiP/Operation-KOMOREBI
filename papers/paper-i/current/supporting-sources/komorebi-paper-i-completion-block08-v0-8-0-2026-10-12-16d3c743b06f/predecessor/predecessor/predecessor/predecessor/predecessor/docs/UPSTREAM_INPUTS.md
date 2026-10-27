# Block 03 proved upstream inputs and trust boundary

All references below are to the pinned local Mathlib source revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, compiled with Lean `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. These are theorem dependencies, not added axioms. Their acceptance is subject to the complete transitive axiom inventory in the final audit.

| Input | Use |
|---|---|
| `Module.AEval.isTorsion_of_finiteDimensional` | The actual polynomial module of a finite-dimensional operator is torsion. |
| `Module.equiv_directSum_of_isTorsion` | A proved PID torsion-module decomposition into irreducible-power quotients. |
| `DFinsupp.linearEquivFunOnFintype` | Convert a finite direct sum to a finite product without changing its module structure. |
| `Ideal.pi_quotient_surjective` | Construct one coefficient realizing the selected coordinates in a color class via CRT. |
| `Ideal.Quotient.factorₐ` and `Ideal.Quotient.factor_surjective` | Build the literal residue quotient maps and prove surjectivity. |
| `PrincipalIdealRing.isMaximal_of_irreducible` and `Ideal.Quotient.field` | Supply the residue-field structure for an irreducible principal ideal. |
| `Polynomial.exists_irreducible_of_natDegree_pos` | Choose an irreducible factor of the first nonconstant invariant factor. |
| `Komorebi.SingleOperatorGraph.operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast` | Transport the proved finite minimum to the existing canonical natural-valued seed rank. |
| `Komorebi.SingleOperatorGraph.operatorAlgebra_seedRank_eq_of_seedNumber_isLeast` | Transport the same minimum to the canonical cardinal rank. |
| `Komorebi.PaperICompletion.CyclicClassification.hasCyclicVector_iff_minpoly_eq_charpoly` | The already proved Block 02 cyclic polynomial criterion. |

The baseline and Block 02 proof sources are preserved and freshly rebuilt by the Block 03 launcher. The full Mathlib dependency source is not rebuilt. Its cached objects are reused under the authenticated archived runtime and exact checked Git revisions.

The new theorem constructs an actual primary presentation. It does not prove a stronger classification theorem from the foundational axioms without using the proved PID library result. The relevant distinction is between an imported proved theorem and a supplied unproved conclusion or custom axiom.

The serial module replay calls the pinned official `replayFromImports` operation. It uses Lean's own kernel and cached imports. It is not a separately implemented verifier and does not fully replay all Mathlib imports.
