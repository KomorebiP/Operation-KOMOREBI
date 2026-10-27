# Block 71: fixed-seven period comparison
## A Fermat-quotient constraint on the actual first coordinate

Version 7.1.0, 21 September 2026.

The new result is a condition at the fixed prime seven, connecting the actual
local period extension to the same normalized global natural class. It is not
another homogeneous Frobenius row. Under TARGET_CONTRACT.md, at every positive
depth and without a conductor bound, write

    alpha=(v*w,r,1), v,r in F7*, w^2=5,
    q7(A)=(A^6-1)/7 mod7.

Then

    (2r+1)^2 = v^2*(3q7(A)+5)^2 in F7.                 (1)

This is a written conditional arithmetic theorem with exact finite checks. The
actual-model, integral RM, uniformization, and all-depth coefficient inputs remain
explicit inherited dependencies. No new Lean proof or independent mathematical
review is claimed. The reducible branch and full Beal remain unresolved.

## What closes in this block

Block60 computed the period residues away from seven, but that calculation could
not simply be reused at seven by discarding all principal units. Here the actual
one-parameter integral deformation supplies errors in 1+7^(7c)O_F, c=v7(C)>=1.
Those errors really ARE seventh powers. In F=Q7(sqrt5), arbitrary principal units
are not: 8 is an explicit counterexample.

The resulting actual local period matrix in F*/F*7 is

    P=Z*I+2X*R, R=[[1,-2],[-2,-1]], R^2=5I,
    X=[phi], Z=-3[A]-3[3]-5[sqrt5].

The unit-class map L(z)=(z^48-1)/7 mod7 gives

    L(phi)=5*sqrt5_bar, L(3)=6, L(sqrt5)=3.

Thus X=[phi], H=[3] are independent and

    [sqrt5]=4H, Z=(3q7(A)+5)H.

The new comparison identifies the ACTUAL local coefficient action. Its matrices
on the toric submodule and quotient intertwine the completed period matrix. The
valuation matrix is 7c*I, so these two matrices agree after cancellation OVER Z7,
not after reducing modulo7. Their common reduction commutes with R and has
characteristic polynomial T^2-5. The centralizer calculation forces Sbar=+/-R.
This is substantially stronger than merely noticing R^2=5I.

Consequently the local rank-two coefficient extension is

    kappa7=(3q7(A)+5)H+2*epsilon*w*X, epsilon=+/-1.

The global natural class restricts to v*w*X+(r+4)H. Changes of the two graded
bases permit ONE nonzero scalar c0; it is not silently set to1. Comparing
coefficients forces c0=v/(2epsilon) and then

    2r+1=epsilon*v*(3q7(A)+5),

which proves (1). The source-to-family integral specialization and actual
period/Tate-module comparison are written out in the notes. They are not
certified merely by the finite arithmetic.

## Effect on the eight surviving patterns

All eight frozen Block70 patterns have r=6. The exact restrictions are:

| Unit coefficient | q7(A) | A^6 modulo49 |
|---|---|---|
| +/-3w, patterns A and B | 0 or6 | 1 or43 |
| +/-w, patterns C and D | 1 or5 | 8 or36 |

For +/-3w, allowed A modulo49 are

    1,3,5,8,18,19,30,31,41,44,46,48.

For +/-w, they are

    6,9,10,15,16,24,25,33,34,39,40,43.

Every predecessor pattern retains twelve residues. There are96 augmented
(pattern,A mod49) pairs, with24 distinct A residues. NO ONE of the eight
coefficient/character patterns is eliminated. Under the predecessor's COMPLETE
rational beta-ramification<=2000 hypothesis, q7(A) in{2,3,4} is now excluded.
That bounded conclusion is not asserted for arbitrary conductors.

Across all36 normalized natural directions and42 rational units A mod49,396
of1512 combinations satisfy (1). These are coefficient/residue combinations,
not representations, solutions, or a completion percentage.

## Positive local controls and failed stronger claim

For each of the24 retained A residues, choose its positive integer representative,
put C=7, and define B as the unique7-adic unit fifth root of7^7-A^3. The derivative
5B^4 is a unit, so Hensel gives an exact primitive local solution. The local
extension comparison remains possible for the appropriate sign and gauge.

These are actual local Frey families under the inherited model, not a simultaneous
global integer solution or a constructed global beta. In particular B is7-adic,
not asserted rational or an ordinary integer. Nor is full J[7] rational over F:
F does not contain mu7. The claim concerns the extension class.

Thus the attempt to finish the eight patterns by this one fixed-prime condition
fails. It leaves a concrete local input for a future global or higher-precision
endpoint argument. Block70's finite-sieve limitation remains intact: its abstract
characters did not claim compatibility with this actual period extension.

## Observed finite checks

| Check | Coverage |
|---|---:|
| Unit residues of O_F/49 |2304 in both implementations|
| Principal-unit inputs modulo343 |2401 in both|
| Matrix candidates over F7 |2401 in both|
| Roots S^2=5I / compatible actual centralizer roots |42 /2|
| Rational period-unit pairs(A,C0) |1764 in both|
| Natural-coefficient/A triples |1512|
| Primary sign-and-gauge checks |145152|
| Separate proportionality determinant tests |3024|
| Accepted coefficient/A triples |396|
| Retained pattern/A pairs |96|
| Separate7-adic fifth-root certificates modulo7^18 |24|

The primary uses the sqrt5 basis, binary powering, exhaustive sign/gauge tests,
and Newton lifting. The separate program uses a phi basis, repeated products,
a sixth Fermat quotient, determinant proportionality, and one-digit Hensel
lifting. It imports no primary arithmetic. Their full accepted classification
hash, pattern lists, and root residues agree. No new Frobenius point counts were
needed.

The observed default Block70 replay passed in142.296 seconds before this block.
It was not a fresh full historical-chain run. The final new-block verifier
regenerates the two scientific JSONs from scratch, compares their complete
contents, checks all payload and inherited source hashes, and requires rejection
of deliberate corruptions. Its actual runtime and archive audit are recorded
outside the immutable ZIP.

## Remaining work

The fixed-seven local comparison is now explicit modulo7, including the actual
A-dependent rational coordinate. What remains is to constrain the SAME comparison
at higher precision or couple it to the global opposite endpoint/fixed-prime data
so that its allowed residues cannot all be realized. No compatibility is supplied
for one global integer B, the full integral representation, or all primes at once.

Eight bounded patterns, unrestricted conductors and depths, the minus component,
upstream independent acceptance, CM/higher Hilbert branches, the full signature,
and full Beal remain separate obligations.
