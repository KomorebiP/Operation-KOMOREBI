# Block 06 semantic and public-type review

This is a reviewed correspondence between the printed claim and the actual Lean statements. It is not an independent verifier or a kernel interpretation of prose. Full elaborated declarations are recorded in the accepted audit's `new_public_full_types.log`; all mapped names and axioms are recorded in `declaration_types_and_axioms.log`.

## The final theorem's inputs

`cyclic_six_way_algebraicClosure` takes a field k, an additive k-module V, finite-dimensionality of V, nontriviality of V, and an actual endomorphism T. It supplies the literal `AlgebraicClosure k` field internally. There is no decomposition parameter, Jordan basis, primary-count function, spectrum certificate, rank equality, or preservation hypothesis in its type.

The generic `cyclic_six_way K T` additionally takes a field K, a specified k-algebra structure, and `IsAlgClosed K`. Its sixth clause uses `T.baseChange K` on the actual tensor-product space. It is not a restriction-of-scalars theorem or a result about an unrelated operator over K.

## Review of the six clauses

| Printed clause | Actual object or predicate | Scope check |
|---|---|---|
| Cyclic vector | `Komorebi.SingleOperatorGraph.HasCyclicVector T` | Existing orbit-generation definition, not a new synonym for polynomial equality. |
| Seed rank one | `seedRank (operatorAlgebra T) V = 1` | Existing canonical cardinal-valued generator invariant for the actual operator algebra. |
| Nonzero primary components cyclic | `Cyclic k[X] (primarySubmodule (Module.AEval' T) p)` for irreducible p and nontrivial actual component | Literal intrinsic submodule and literal polynomial action. Zero components are explicitly handled in the reverse proof. |
| One invariant factor | `HasOneInvariantFactor T` | Actual monic positive-degree quotient presentation; not a stored count or equality certificate. Companion-basis and any-chain count theorems provide the normal-form interpretation. |
| Minimal equals characteristic polynomial | `minpoly k T = T.charpoly` | Actual library invariants of T. |
| Geometric multiplicity one after extension | The finrank of `Module.End.eigenspace (T.baseChange K) a` for actual `a ∈ spectrum K (T.baseChange K)` | Algebraic closure applied to the actual tensor extension, with nonzero tensor-space hypothesis supplied internally. |

## One-invariant-factor boundary

The fourth clause is formulated as mathematical existence of an actual one-factor invariant-factor presentation. A basis is constructed in which the original operator has the usual companion matrix, whose signs and orientation are separately tested. The presentation's monic polynomial is forced to be the minimal polynomial. For any supplied ordered invariant-factor chain of the actual module, the number of factors is one iff T is cyclic.

This matches the mathematical one-factor rational-canonical criterion. It is not an executable canonical-form procedure. No blanket existence/uniqueness theorem for sorted invariant factors of every noncyclic operator is silently claimed by this block.

## Scalar-extension argument is not circular

The minimal polynomial is proved to commute with base change by annihilation plus preservation of independence of the lower operator powers. Cyclicity is then transported using the already proved minimal/characteristic polynomial characterization. The minimal-polynomial lemma has no cyclicity assumption. The algebraically closed geometric criterion is applied only after this bridge is established.

## Boundaries retained

The minimal-polynomial and cyclicity extension identities include zero spaces. The six-way/rank-one statement explicitly excludes them. Field extensions need not be separable or algebraic for the preservation result. The geometry clause does need an algebraically closed target field. All constructions are noncomputable mathematical objects and proofs.

The original conditional APIs remain unchanged in the predecessor. The new final criterion, rather than a mutation of a legacy certificate-based statement, closes the publication-facing gap. No other publication record is automatically marked complete.
