# Exact finite normalization and retained-lift boundary

This check supports two precise finite statements. It does not construct an
arithmetic type or establish original H5. The root computation uses exact
finite fields and integer coordinates in the cyclotomic ring, with no floating
arithmetic or sampling.

## Quadratic Frobenius and its sign

Let k=F9=F3[u]/(u²+1), with Frobenius tau(a+bu)=a-bu and trace Tr(a+bu)=2a.
On a nine-dimensional complex space with basis e_t indexed by k, use

    eta(x,y,z)e_t = omega^(z + Tr(yt) + Tr(xy)/2) e_(t+x),

where z lies in F3 and omega³=1, omega≠1. The group law has central term
(Tr(yx')-Tr(xy'))/2. It is a finite Heisenberg group of order243.
The sign convention gives commutator -Tr(xy'-yx'), consistent with the
PLUS-normalized arithmetic form after the stated coordinate identification.

The permutation S(e_t)=e_(tau(t)) implements Frobenius, has S²=1, and has
three fixed basis vectors and three transpositions. Hence det S=-1. The
determinant-one extension has generator A=-S, for which A²=1, det A=1 and
trace A=-3. The fixed Heisenberg group has order27 and its irreducible
representation with the same central character has degree3. For all27 fixed
group elements h the exact calculation gives

    trace(A eta(h)) = - trace(eta_fixed(h)).

Under an arithmetic diagonal embedding the field trace multiplies a base
central value by2. Thus this is the fixed representation carrying theta_F²,
not theta_F under the unaltered additive-character convention.

The script verifies all59,049 group multiplication pairs on all nine basis
vectors, full Frobenius covariance, determinant parity, character support,
the degree/character norm and all27 fixed-group trace identities. This supplies
a finite benchmark. The separate LATTICE113 argument derives the same trace
for its actual arithmetic representation by Glauberman and determinant
normalization, so that arithmetic conclusion is not inferred merely from a
dimension match with this model.

## Why a quotient action still does not give a retained dyadic lift

Both D8 and Q8 have center of order2 and quotient F2² with the same nondegenerate
commutator pairing. Consider the quotient automorphism cycling its three
nonzero vectors. It has order3, coprime to the characteristic.

For D8 the square map on the three nonzero cosets has values (1,0,0), where1
means the nonidentity central element. Any center-preserving automorphism must
preserve this map, so the three-cycle cannot lift. For Q8 all three values
are1, and cyclic permutation of quaternion generators gives a lift. Exhausting
the7! identity-fixing bijections finds zero D8 lifts and four Q8 lifts, each
of order3.

This is a counterexample to the assertion that matching symplectic quotients
plus coprime quotient action alone supplies the same original finite-group
lift. It is not a counterexample to the new cochain theorem: that theorem
requires the actual full lifts and compares complex scalar pushouts. Nor is
it a counterexample to original Claim16.2 with its retained dyadic input.

The coprimality requirement also has a simple structural negative control.
Take A=C3, beta=identity, n=3, and a nontrivial character r of order3. Its
cyclic norm is1, but every coboundary chi(beta(a))/chi(a) is1. Thus the norm-one
condition alone cannot replace the coprimality hypothesis.

## Provenance and failures

Code: scripts/finite_models113.py. Contract: FINITE_CONTRACT.json.
Run: evidence/finite/run01/manifest.json and RESULT.json. The completed v2
manifest passes the bundled validator. An independent reader reconstructed
the finite model using different coordinates and checked the quaternion table.

Two launcher configuration failures occurred before the mathematical run:
an initial help invocation used the parent working directory, and the first
bounded-run request declared its result outside the fresh output directory.
The latter was rejected by the runner. The script now accepts an explicit
output path inside the run directory. The actual run01 completed and passed.
These were launch errors, not failed mathematical cases.

No assertion here identifies the original prescribed kappa with the canonical
finite extension. That arithmetic normalization remains a separate obligation.
