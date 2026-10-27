# Canonical Block 47 irreducibility conclusion

Status: **written proof with source-checked arithmetic inputs and fresh
independent review**. This is not a Lean Galois theorem and not a proof of
nonexistence for the generalized Fermat equation.

## Theorem and exact scope

Let A,B,C be positive pairwise-coprime integers satisfying A^3+B^5=C^7.
Let J be the Jacobian of

\[
y^2+(x^3+B)y=2Bx^3+3Ax+B^2
\]

and let the rank-two representation over K=Q(sqrt(5)) be the RM
representation specified in the source contract of
`mod7_irreducibility_extension.md`. Its residual representation at the inert
prime (7) is absolutely irreducible if

\[
\boxed{14\nmid C.}
\]

Equivalently, the proof covers C odd or 7 not dividing C. Its only uncovered
parity/divisibility branch is C even and 7 dividing C. The theorem is a
property of an attached representation for a hypothetical primitive
solution. It does not assert that such a solution exists or cannot exist.

## Proof with the retained global label

The case C odd is the previously reviewed theorem in
`predecessor/mod7_oddC_written_proof.md`. Suppose C is even and 7 does not
divide C, and suppose for contradiction that the residual representation
is reducible over Fbar7.

The conductor, local-weight, determinant and global-unit argument in
`mod7_irreducibility_extension.md`, using the new semistable model at two,
gives one associated constituent nu which is unramified at seven. Its
eighth power is unramified at every finite and real place. The Euclidean
norm proof in the predecessor gives class number one for K, so global
class field theory implies nu^8=1. The character nu is unramified outside
(3) and (sqrt(5)), and tame at those two primes.

The stable special fiber at two has two F4-rational nodes, with the two
branches at each node exchanged by Frobenius over F4. Its normalization is
rational. The saturated integral torus/graph filtration therefore gives
full Frobenius eigenvalues

\[
-1,-1,-4,-4
\]

on the seven-adic semisimplification at the norm-four prime of K, and the
same reductions modulo seven. Since (-4)^8=2 modulo seven, the order
condition on nu forces

\[
\nu(\operatorname{Frob}_{(2)})=-1.
\]

The precise curve, branch calculation, integral filtration and source
hypotheses are proved in `evenC_torus_frobenius.md`.

Apply reciprocity to the totally positive unit phi^4=3phi+2, where
phi=(1+sqrt(5))/2. Its residues at (3) and (sqrt(5)) are -1 and 1,
respectively. This forces nu_(3)(-1)=1. Applying reciprocity to the totally
positive number 2/7 then gives

\[
\nu(\operatorname{Frob}_{(7)})
=\nu(\operatorname{Frob}_{(2)})=-1.
\]

This uses one fixed global character at both primes; the complete local
factor calculation is `reciprocity_two_seven.md`.

Because 7 does not divide C, J has good reduction at seven. Raynaud's
uniqueness theorem transports the unramified generic subquotient nu to its
finite étale special-fiber model without losing the Frobenius action.
The Cartier calculation gives the full special-fiber Frobenius polynomial
at the norm-49 prime

\[
P_{49}(T)\equiv T^2(T-A^3B)^2\pmod7.
\]

This polynomial annihilates Frobenius on the Jacobian and its special
seven-torsion subquotients. Since nu has nonzero Frobenius eigenvalue, it
follows that

\[
\nu(\operatorname{Frob}_{(7)})=A^3B\pmod7.
\]

The complete transport argument, including arbitrary finite coefficient
extension via powers of J and residual lattice independence, is in
`ordinary7_candidate.md`. That filename records the route's origin; its
local lemma is proved, and its global dependencies are supplied here.

Therefore A^3B=-1 modulo seven. Both bases are nonzero modulo seven, so
A^6=1 and B=-A^3. Then

\[
A^3+B^5=A^3-A^{15}=0\pmod7,
\]

contrary to 7 not dividing C. This proves the theorem.

## Dependencies and verification boundary

The source-dependent arithmetic contract is stated in
`mod7_irreducibility_extension.md` and the copied predecessor proof.
It includes the source realization and conductor bounds, degree-one local
weight theorem, Weil pairing and reciprocity. New sources are Raynaud's
finite-flat uniqueness, Deligne–Mumford's curve/Jacobian semistability
implication, Achter–Howe's corrected Frobenius congruence, and the saturated
integral torus/graph filtration of Dokchitser–Dokchitser–Morgan. Exact
locators and checked hypotheses are retained in the component proofs and
`final_irreducibility_audit.md`.

The original finite-flat obstruction for 7|AB and the prior C-odd proof
remain valid narrower results. This theorem is the canonical final scope
of their continuation. No claim of novelty is made from a limited source
check.

No modular form has been eliminated by this theorem. At 14|C the Jacobian
does not have good reduction at seven, so the finite-flat transport argument
used above is unavailable. The next stage still requires this remaining
irreducibility branch, exact level-lowering applicability, and elimination
of every attached modular candidate. No completed (3,5,7) or general Beal
proof follows from the present result.
