# Exact classical dependencies and source boundary

The finite cyclic decomposition is not a new proof of the finite abelian group
structure theorem. The development invokes mathlib's existing theorem
`AddCommGroup.equiv_directSum_zmod_of_finite'`, then proves that each cyclic order
divides p^r and is consequently a positive power p^e with e<=r.

Authoritative checked library revision:
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
Exact local source: `Mathlib/GroupTheory/FiniteAbelian/Basic.lean`.
Online locator:
https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/GroupTheory/FiniteAbelian/Basic.lean

Scalar compatibility uses the fact that additive homomorphisms of ZMod(n)-modules
respect their scalars; exact source `Mathlib/Algebra/Module/ZMod.lean` at the same
revision. The invariant-factor multiplicity proof in this block uses torsion
cardinality differences, not an unverified imported uniqueness assertion.

The Python reference uses the installed SymPy 1.14.0 routine
`sympy.polys.matrices.normalforms.smith_normal_decomp`, returning (D,U,V) with
D=U*K*V, and `hermite_normal_form`. It independently checks each returned Smith
certificate before transporting any state. The algorithm itself is not proved
correct as Lean executable code. Official documentation:
https://docs.sympy.org/latest/modules/matrices/normalforms.html

No novelty, priority, or independent reviewer claim is attached to this block.
