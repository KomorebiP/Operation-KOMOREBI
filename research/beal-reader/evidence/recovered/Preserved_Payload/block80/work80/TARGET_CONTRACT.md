# Block 80 target contract

Version 8.0.0. Authoritative predecessor: the exact Block79 ZIP in predecessor/.
Its SHA256 is 54fc40812f5590f3215c8c643ceedbd3c49ca13b58854fadb6bb3088fa8da40e.
No upstream mathematical claim is made unconditional by preserving its bytes.

## Target

For each of the four frozen nine-prime supports, distinguish:
1. existence of a continuous restricted primitive p0 with dp0=-alpha cup beta;
2. existence of one primitive meeting every first-stage fixed-local trace and toric
   hyperplane; and
3. lifting that primitive to the actual upper q-stage and integral Frey representation.

This release proves (1), computes the exact finite linear operator controlling (2),
and tightens its homogeneous kernel. It does NOT evaluate the actual affine target
in (2), construct numerical p0-values, solve (3), or eliminate a residual pattern.

## Domains and inherited arithmetic inputs

K=Q(sqrt5); phi=(1+sqrt5)/2 is a BASE-field unit. Coefficients are
k=F49=F7[w]/(w^2-5). The base and coefficient radicals have different roles.
All new finite matrices have entries in F7 and are extended to k without a
coefficient-descent assumption. Actual applications have lattice depth n=1.

Use normalized continuous cocycles alpha in Z1(K,k(chi)) and beta in
Z1(K,k(chi^-1)) and a single pinned natural frame and reference rho0. The
inhomogeneous differential convention is

    dp(g,h)=p(g)+p(h)-p(gh),
    (alpha cup beta)(g,h)=alpha(g) chi(g)^-1 beta(h).

S is the COMPLETE ramification support of beta, one of the four frozen nine-prime
sets. Sigma consists of S, the primes over2,3,5,7, and the two real places.
Alpha and beta factor through G_(K,Sigma). At each v in S, alpha is locally zero
and chi is trivial modulo7. Beta is locally a coboundary at the four fixed primes.
These are inherited properties of the stipulated residual patterns/geometry, not
conclusions inferred from new finite arithmetic.

Block79 proves that every actual p is unramified outside Sigma. The fixed-local
trace condition and the toric hyperplanes

    c_v p(F_v)-b_v p(T_v)=-h_v c_v,
    c_v=beta(T_v)!=0, b_v=beta(F_v), h_v=(Nv-1)/7 mod7

are inherited. Local inertia and Frobenius are normalized through local Artin maps,
with the rational prime itself as uniformizer at the inert support places. The
new computation evaluates b_v in precisely that normalization and converts c_v
from the frozen twisted residue convention. No Frobenius at a conductor prime is
silently treated as an unramified test prime.

The matrices describe the ordinary characters z=p-p0. They are not ordinary
character equations for beta. Counting a common pointwise semilinear subproblem
requires the SAME j, frame and reference; that extra hypothesis remains explicit.

## Evidence and nonclaims

Written proofs use finite-S Poitou--Tate and local duality in Milne, Arithmetic
Duality Theorems, 2nd edition (2006). The class-number/unit calculation and its
application are proved in the notes. The two finite arithmetic implementations
share input facts but import no arithmetic from each other or the predecessor.
The evaluator tests supplied linear targets and never authenticates an arithmetic p0.
There is no new Lean compilation or independent mathematical reviewer.

Other divisors of C may exist and may carry upper q-ramification. That does not
invalidate the Stage-P support theorem, but is NOT covered by an assertion of
bounded q-ramification. None of the eight patterns, unrestricted supports/depths,
minus-component cases, other modular/CM branches, full signature, or Beal is closed.
