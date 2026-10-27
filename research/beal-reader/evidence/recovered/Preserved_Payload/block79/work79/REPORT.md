# Beal research — Block 79
## First-stage ramification control and restricted character differences

Release 7.9.0, 21 September 2026.

The unrestricted auxiliary-ramification issue from Block78 now separates into two
substantially different cases. The first-stage diagonal cochain p cannot acquire
new inertia outside the fixed primes and beta's support. The upper cochain q can.
This supplies a justified finite ramification set for Stage P even if C has
arbitrarily many additional bad divisors where beta is unramified.

No one of the eight depth-one patterns is eliminated. The affine first-stage
particular solution and the full global q-matching problem remain uncomputed.
All actual arithmetic statements retain TARGET_CONTRACT.md's inherited hypotheses.
No new Lean compilation or independent mathematical review is claimed.

## 1. The first-stage ramification gap is closed in the stated scope

Use the same reference and natural frame:

    rho=(I+7X)rho0 mod49, X=[[p,q],[beta,-p]].

At every variable bad place, natural inertia is I+N with N in7M2(O), N^2=0,
and reference inertia is identity. In the residue FIELD k=F49,

    p(T)^2+q(T)beta(T)=0.

Therefore beta(T)=0 implies p(T)=0. Good places supply no inertia either. If
S is the complete beta-ramification support and S0 the places over2,3,5,7,

    p(I_v)=0 outside S0 union S.

The cochain p factors through G_(K,S0 union S). It is not itself generally a
character; its equation remains dp=-alpha cup beta. See INERTIA_RESTRICTION.md.

Thus the absence of a bound on every bad divisor of C no longer prevents a
ramification-restricted FIRST-STAGE computation. It still matters for Stage Q.

## 2. Differences of actual p's lie in a small explicit finite space

Fix the same residual alpha, normalized beta cocycle and reference for two
candidates. Then z=p'-p is an ordinary k-valued global character. The first
result excludes its auxiliary inertia. Exact trace equality chi+1 and a local
separating cyclotomic element at each fixed place force

    z|G_v=0 at v over2,3,5,7.

This conclusion concerns a difference, not an assertion that actual p vanishes
at those places. The ray-class exact sequence now gives the five rows

    phi, 2, 3, sqrt5, 7

on the nine beta-support primes. These are the correct ORDINARY rows for z,
not a replacement for beta's inverse-cyclotomic weights. The rank is3 for all
four frozen support patterns, so the fixed-local difference space has dimension6
 over k.

At a supporting inert q=-1 mod7, descent of beta gives beta(F_q^2)=0. The actual
toric equation then fixes p(F_q^2), and hence forces z(F_q^2)=0. The corresponding
principal-uniformizer rows further reduce the homogeneous difference space:

|Pattern|Augmented matrix rank|Dimension bound over F49|
|---|---:|---:|
|A|6|3|
|B|6|3|
|C|5|4|
|D|6|3|

The full matrices and kernel bases are in verification/primary79.json and are
reconstructed separately in independent79.json. In a COMMON pointwise semilinear
frame, the additional coefficient condition gives dimensions3,3,4,3 over F7,
with bounds343,343,2401,343 on the number of first-stage cochains once a particular
solution is fixed. Without that extra common-frame condition the bounds are over
F49, not F7.

These are bounds on differences/ambiguity. No affine origin p0 has been computed.
The homogeneous zero vector does not prove that the original inhomogeneous
problem has any solution. Nor do the dimensions eliminate a pattern.
See RESTRICTED_P_CHARACTERS.md.

## 3. Once p is fixed, q's values at beta support are no longer free

At beta support, put c=beta(T)!=0, b=beta(F), h=(Q-1)/7 mod7, and
B0(F)=b0(F)/7 mod7 for the SAME chosen reference. The local toric normal form gives

    c p(F)-b p(T)=-h c,
    c q(T)=-p(T)^2,
    c (q(F)+B0(F))=-p(T)p(F).

In particular, if two deformations have the same p and beta, their upper
k(chi)-correction must vanish on the FULL local group at every beta-supporting
place. This retains the reference term and is invariant under a compatible
change of the Frobenius lift. See SUPPORT_Q_VALUES.md.

## 4. Auxiliary upper ramification is restricted, but it survives

At a beta-unramified bad place with nonzero upper inertia, the actual toric line
reduces to the upper direction. Writing it as(1,7s) gives

    beta(F)=s*(Q-1)/Q mod7.

For Q=1 mod7 this is zero. For Q!=1, an unramified chi^-1 class is locally zero
as a cohomology class. Thus such upper inertia can occur only where beta splits
locally. It need not disappear.

The matrices N=7uE12 and F=[[Q,R],[0,1]] give exact all-precision local toric
positive controls. A genuine local Frey control also survives at5167:

    A=3238, C=5167, B=3658 mod5167,
    B^5=5167^7-3238^3 in Q_5167.

The fifth root exists uniquely by Hensel, and both implementations reproduce it
modulo5167^8. The inherited level-seven period criterion holds. Its natural node
thickness is7, giving nonzero purely upper first-order inertia in a local toric
frame. This is not a global frame, global beta, ordinary integer B or a Beal
counterexample. See AUXILIARY_UPPER.md.

The attempted strengthening that ALL adjoint ramification is confined to beta
support fails. The new restriction applies to p; q remains a separate problem.

## 5. Verification and evidence level

New exact checks, independently implemented in two quadratic bases:

|Finite assertion|Coverage per implementation|
|---|---:|
|Traceless coefficient matrices|117649|
|Nilpotent matrices found|2401|
|Nilpotents with zero lower entry|49, all purely upper|
|Full beta-support p/q packets|806736|
|Rejected opposite-sign q-equations|790272|
|Integral auxiliary toric packets|33614|
|Exact residue fields for the ray matrices|10|
|Restricted support matrices|4|
|Independent local Hensel control|one root modulo5167^8|

The second implementation constructs matrices by conjugation rather than the
primary rank-one formula. Its residue arithmetic uses a different field basis;
its rank audit also checks nonzero integer minors and full nullspace bases.
Neither program imports the other's arithmetic. Full scientific JSONs agree.

The release verifier regenerates both output files in a fresh scratch tree,
compares complete results, checks exact predecessor bytes and inherited source
leaves, and requires deliberate corruptions to be rejected. Observed timings,
process exit codes and final archive integrity are recorded externally.

The CFT source was inspected at the rendered ray-class exact-sequence pages.
The finite tests do not prove global class field theory or the inherited actual
Frey geometry. The source record and self-review keep those distinctions explicit.

## Remaining task

Construct the actual ramification-restricted first-stage affine translate, or
compute the obstruction to its existence, using the finite support now justified.
Then impose the remaining toric and fixed-seven conditions on that SAME p.
For the upper stage, include its required local zeros at beta support and the
beta-splitting restriction on any auxiliary inertia, without pretending that
those conditions bound every new prime.

Eight patterns, unrestricted beta support/depth, the minus component, integral
realization, independent upstream acceptance, CM/higher-Hilbert branches, the
complete signature and full Beal remain open.
