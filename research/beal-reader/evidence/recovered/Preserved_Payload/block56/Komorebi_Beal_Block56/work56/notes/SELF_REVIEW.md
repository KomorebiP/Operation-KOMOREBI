# Adversarial self-review

The author performed this review. It is not independent mathematical review.

1. SAME FROBENIUS. The actual global eta precision is applied to the actual
Frobenius in the fixed natural basis, not a separately constructed ray character.
The new rank-two trace comparison needs only G1-G3, not a new Kummer descent.

2. PRECISION. The identity is (Q-1)u+u^2/(1+u), and 2m>n. This gives exactly
r=min(n,m+h). The n=2 integral control disproves omitting the minimum with n.

3. RESTRICTION OF SCALARS. The rank-four polynomial is a norm of a rank-two
polynomial. Jacobian-order divisibility is 7^(2r), not 7^r. Integer polynomial
congruence alone would give only the weaker divisibility and is not substituted
for the norm proof.

4. INERT PRIME. At 197, rational Frobenius must be squared. With P_q=T^4+bT^2+q^2,
squaring and applying nu=-1 gives (T^2-bT+q^2)^2. Thus the test is b=Q+1,
not b=-(Q+1). The independent implementation uses Newton identities and
the defining twist radicand, not the primary closed formula.

5. SPLIT PRIME. At 491, both radicand symbols are -1. The surviving rational
traces {-25,10,24} become {25,-10,-24}. The required rank-four trace is
2*(491+1)=4 modulo49. None qualifies. This is not a rank-two/rank-four mixup.

6. EXHAUSTIVE GOOD LOCUS. Every pair with nonzero seventh-power equation sum
is generated independently. Weighted scaling is used only for curve counts.
Admissibility is never propagated from an orbit representative. A polynomial
gcd checks smoothness at each of the 39,886 pairs.

7. STAGING. At split491, failure of the degree-one trace modulo7 is a sufficient
rejection of the required residual polynomial. It is legitimate to omit N2
there, but those rows are explicitly null and are not reported as full counts.
At inert197, all N2 values are computed.

8. INDEPENDENT COVERAGE. The second field is theta^2+theta+1, irreducible
because both q are 2 modulo3. Cubing is bijective, so B=1 normalization is
valid; B=0 uses fifth-power cosets. This differs from the primary weighted
orbit traversal. Every original pair is compared under the independent mapping.

9. EXACT SUPPORT QUANTIFIERS. H(C) means all high-congruence divisors of C.
It is not the support of eta, its highest layer, or beta. The claimed 97/293
exclusion uses H(C) subset {97,293}. It is not generalized to a highest-layer
support of {97,293} with additional high divisors of C.

10. GOOD REDUCTION. Both auxiliary exclusions apply only when q does not
divide C. The primitive residue (-1,1,0) is retained as a bad-prime control.
Forcing 197 and491 into C is not itself a contradiction.

11. UNSUCCESSFUL SHORTCUTS. Explicit local toric models satisfy the 97/293
ramified constraints and reciprocal line. Generic Weil polynomials also meet
the target congruences. Actual Frey point counts provide the missing input.
These controls are not claimed global geometric realizations.

12. STATUS. The actual no-solution target remains open. The new bounded
branch exclusion is established under the inherited inputs. Exact checks,
source-page inspections, and this self-review do not certify the whole
unformalized upstream geometry or amount to a new Lean proof.
