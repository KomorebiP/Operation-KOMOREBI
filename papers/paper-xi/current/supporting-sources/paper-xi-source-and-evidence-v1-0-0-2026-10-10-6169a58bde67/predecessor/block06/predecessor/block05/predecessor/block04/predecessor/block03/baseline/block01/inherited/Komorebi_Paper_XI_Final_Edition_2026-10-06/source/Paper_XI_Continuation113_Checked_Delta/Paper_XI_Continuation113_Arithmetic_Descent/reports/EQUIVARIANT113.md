# Continuation113: the coprime cyclic cochain correction

## Result and boundary

`CyclicDefect113.lean` removes the label-dependent character defect left open by
Continuation112. It proves that complex scalar cocycles with equal commutators
admit an equivariant normalized comparison when the common quotient has finite
exponent coprime to the order of the two supplied honest lifted cyclic actions.
The correction is constructed explicitly, and its character and norm identities
are derived from those full actions.

The endpoint is an isomorphism of complex scalar pushout extensions. It fixes
every complex scalar and every quotient label, and it intertwines the two
original lifted automorphisms. It does not identify the original finite central
groups, reconstruct dyadic power data, construct an arithmetic simple character,
or establish that the prescribed kappa has a particular determinant normalization.
Original Claim16.2 therefore remains at 65/66.

## Exact statement

Let A be an abelian group and let c,d be normalized complex-unit-valued scalar
2-cocycles on A with equal commutators. Their scalar extensions have multiplication

    (z,a)(w,b) = (zw c(a,b),ab).

Let beta be an automorphism of A. Suppose L and M are actual automorphisms of the
c and d extensions, respectively, fixing each scalar, covering beta, and satisfying

    beta^n = 1,    L^n = M^n = 1.

Assume a^m = 1 for all a in A and gcd(n,m) = 1. There exists a normalized function
s': A -> C^x such that

    c(a,b) = s'(a)s'(b)/s'(ab) * d(a,b),
    L_phase(a) s'(beta(a)) = s'(a) M_phase(a).

Consequently F(z,a) = (z s'(a),a) is an extension isomorphism with F L = M F.
The final two exported theorems are `exists_equivariant_cochain` and
`exists_equivariant_scalarBridge`. An initial cochain, covariance equation,
character correction, or norm-one defect is not a premise of either theorem.

The proof also works for arbitrary commutative coefficient groups once a
cochain has been supplied. Only initial cochain existence uses complex units
and the divisible-coefficient result from Continuation112.

## Construction

Continuation112 first constructs a normalized cochain s with c = delta(s) d.
The phase of an actual lift is derived by applying it to the fixed section:

    L(1,a) = (f(a), beta(a)),
    M(1,a) = (g(a), beta(a)).

Scalar fixation implies the full formulas L(z,a)=(zf(a),beta(a)) and similarly
for M. Multiplicativity then proves the phase law

    f(ab) = f(a)f(b)c(beta(a),beta(b))/c(a,b).

Iteration of the actual automorphisms proves

    product_{i=0}^{n-1} f(beta^i(a)) = 1,
    product_{i=0}^{n-1} g(beta^i(a)) = 1.

Define

    r(a) = f(a)s(beta(a))/(s(a)g(a)).

Substitution of the two phase laws and c=delta(s)d proves r(ab)=r(a)r(b).
The cyclic product of r is one: the f and g products are one, and the s factors
telescope using beta^n=1. Thus r is a character with norm one. Its m-th power is
one because A has exponent dividing m.

Define the weighted norm

    T(a) = product_{i=0}^{n-1} r(beta^i(a))^i.

A finite induction gives the more general identity

    T_n(beta(a)) N_n(r)(beta(a)) = T_n(a) r(beta^n(a))^n.

Using norm one and beta^n=1 yields T(beta(a))/T(a)=r(a)^n. Choose the explicit
integer e=Nat.gcdA(n,m). Bezout supplies an integer f0 with ne+mf0=1. Therefore

    chi(a)=T(a)^e,
    chi(beta(a))/chi(a)=r(a).

Since T and chi are constructed in the character group, they are multiplicative.
Put s'=s/chi. A character has trivial scalar coboundary, so the cocycle comparison
is unchanged. The displayed coboundary equation for chi gives the required
covariance of s'. This correction changes the section comparison, not either
original action or original scalar character.

## Relation to the new papers

The mathematical mechanism is finite cyclic cohomology with coprime torsion,
implemented here by a weighted norm and Bezout. This report makes no novelty
claim. The new paper assessment suggested combining scalar central enlargement
with honest coprime action control. The present proof is internal to the checked
Lean development and does not add an axiom for any result in those papers.

The proof permits m a power of 2 when n is odd, at the level of complex scalar
pushouts. This does not remove the separate requirement to retain and identify
any prescribed raw dyadic finite central extension.

## Verification and failures

The final source SHA256 is

    b6fe373c44ebd8725be1683e7f851da03bcc708c896db2103e02a5a31fbb3a19

All 37 explicitly named declarations were checked and their axiom dependencies
were audited. They use only Classical.choice, Quot.sound and propext, or a subset.
The module passed leanchecker. The exact declaration list and object hashes are
in `evidence/equivariant/CYCLIC_AUDIT113.json`. The source was freshly compiled;
inherited112 objects and Mathlib were reused, not rebuilt.

Seven development attempts are preserved with source snapshots, command lines,
exit codes, hashes and logs. Attempt01 failed because Lean's first PaperXI
namespace directory hid the separate inherited object tree. The runner was
corrected to use a private object tree of symlinks to unchanged112 inputs.
Attempts02,04,05 exposed local proof-script issues: overly broad rewriting of
powers, scalar multiplication orientation, and a remaining commutative cancellation.
The corrected proofs compile. Attempts03 and06 checked intermediate scopes;
attempt07 checks the final complete module. These failures were proof elaboration
failures, not failed tests silently reclassified as mathematical successes.

A final mathematical self-review checked the defect orientation, weighted-product
identity, Bezout exponent, correction sign, scalar fixation and endpoint scope.
No unresolved issue was found in these generic implications. Arithmetic attachment
and normalization of the original supplied kappa remain separate obligations.

## Completed actual-group adapter and representation composition

Two further checked modules now instantiate the abstract scalar-pushout result
on actual groups. `ActualScalarLift113` derives the pushout lift, scalar
covariance and honest period from an original theta-preserving group
automorphism. `EquivariantRepresentation113` then constructs the112 actual
representation using the corrected cochain and proves its covariance with the
unchanged original packet operator U. The latter endpoint has no cochain,
covariance-correction, or pushout-action premise.

The exact statements and boundaries are recorded in
`ACTUAL_SCALAR_LIFT113.md` and `EQUIVARIANT_REPRESENTATION113.md`. These close the
finite-action correction interface on supplied actual data. They do not supply
the missing arithmetic realization or normalize an original kappa without proof.
