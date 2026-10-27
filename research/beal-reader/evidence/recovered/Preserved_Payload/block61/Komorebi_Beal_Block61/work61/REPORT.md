# Beal research, Block 61
## Twisted opposite-extension reciprocity and depth-two closure on a stated support class

Version6.1.0. 19 September2026.

The remaining depth-two opposite extension is excluded when its entire
ramification is contained in {197,883,1373,1667}. Consequently, under the
explicit inherited actual Frey-geometry and representation hypotheses,

    COMPLETE H(C) subset U => n=1,
    U={97,197,293,491,587,883,1373,1471,1567,1667}.

This closes the depth-two branch left on the complete ten-prime high-divisor
class. It does not eliminate depth one or general depth two with ramification
outside that class, and it does not solve the complete signature or Beal.

The four local49-torsion Frey families of Block60 remain valid. The obstruction
is that their possible ramification cannot be combined into one actual global
opposite extension with the stipulated common natural Kummer class and the
new full local Frobenius conditions. The evidence is written conditional
proofs and exact computational certificates, not new Lean proofs or independent
mathematical review.

## 1. A full local condition on beta, not another eta row

At a variable bad place of norm Q=1 modulo7, suppose eta_n=1 modulo7^n. Write
actual natural Frobenius in the same basis as

    F=[[a,b],[7^n c,d]], tr(F)=Q+1, det(F)=Q,
    d=1+7^n D, a=Q-7^n D.

Then

    b c=(Q-1)D-7^n D^2.

If beta is unramified but locally nonzero, c is a unit. Thus b=0 modulo7,
and the entire natural residual representation is locally trivial. The
inherited actual nodal period then forces phi to be a seventh-power residue.
At beta ramification that same period requirement was already known. Hence,

    phi not a seventh-power residue => beta locally zero,

under the displayed scalar-diagonal and toric hypotheses. This rules out a
nonzero unramified Frobenius as well as ramification.

At n2, eta2=1 and the primes29,71,491 are already forced divisors of C. Both
places over each prime fail the phi seventh-power test. Therefore beta is
zero on all six full local groups. No good reduction at these primes is used.
See notes/OPPOSITE_FROBENIUS.md.

## 2. The opposite twist is treated over the correct field

For beta ramification contained in S={197,883,1373,1667}, all supporting
rational primes are inert in K=Q(sqrt5) and1 modulo7. Their inertia data are
fixed by Gal(K/Q), including the coefficient action. The inherited injective
inertia localization for the split-at-seven Selmer group makes beta invariant
as a cohomology class. Inflation–restriction then descends it uniquely to
H^1(Q,F49(chi^-1)).

This is not descent of the actual Tate lattice, not descent of alpha, and not
a restriction of the coefficients to F7. See notes/TWISTED_DESCENT.md.

Over M=Q(zeta7), this is an additive ray character with chi^-1 equivariance.
For residue primes zeta->r_q^b, that equivariance gives coefficients b*s_q.
Ordinary constant weights, as used for eta, would be wrong. Integral generators
of norm29,71,491 and principal-idele reciprocity give the exact matrix

    R=[[4,2,6,1],
       [6,2,0,5],
       [3,6,1,6]],

with columns197,883,1373,1667. Its rank is3, and its full F49-kernel is

    F49*(1,0,0,3).

So reciprocity alone still has a nonzero abstract survivor. The proof does
not replace rank3 by rank4 or discard this line. Both norm and residue-symbol
implementations reproduce it. See notes/TWISTED_RECIPROCITY.md.

## 3. The same natural coefficients contradict the surviving line

A nonzero kernel vector forces beta to ramify at BOTH197 and1667. The natural
class has one global vector

    alpha=a_phi[phi]+a_3[3]+a_5[sqrt5], a_3*a_5 nonzero.

At actual beta ramification its local value must vanish. The two residue rows
are

    197: (0,6,6),
    1667:(0,3,4).

Thus197 requires a_3/a_5=6, whereas1667 requires a_3/a_5=1. Their2x2 determinant
is6 modulo7, so they cannot annihilate a_3,a_5 without both being zero. No
choice of a_phi can repair the contradiction.

This proves that an actual depth-two beta must ramify outside S. Combined
with the existing geometric exclusions of the other six primes in U, it must
in fact ramify outside U. If COMPLETE H(C) subset U, the existing n<=2 bound
therefore improves to n=1. Arbitrarily many low-congruence divisors and arbitrary
prime multiplicities are permitted. See notes/DEPTH_TWO_CLOSURE.md.

## 4. What did not fail

All four actual local Frey families from Block60 still pass their complete
49-torsion test. The congruence on3*5^9*A/C0^35 is preserved, as is the actual
multiplicity v7(v_q(C))=1 at depth-two support. The new theorem is global:
no individual one of the four primes is excluded with unrestricted additional
beta ramification. New ramification elsewhere adds columns and changes the
reciprocity calculation. Merely adding more divisors unramified in beta does not.

A separate exact Q29 local toric model shows that the new local implication
would be false without full eta precision. The nonzero ray-kernel line and
this local matrix are retained as negative controls. No local positive family
or older proof is silently rewritten.

## 5. Exact checks and provenance

The original Block60 verifier was run from a clean extraction with its declared
selected nested predecessor chain before development and returned
PASS_DECLARED_CHECKS. Its complete report and execution log are retained.

The new exact computations cover the ranges below. The cyclotomic, residue,
and common-coefficient results were reproduced by the separate implementation.
The local matrix family has one executable checker and its displayed algebraic
proof; it is not presented as an independently implemented matrix audit.

| Verification | Coverage |
|---|---:|
|Same-lattice trace/determinant examples|13,608|
|Examples with nonrational coefficients|13,104|
|Depth-two examples|3,402|
|Integral cyclotomic generators and exact norms|7|
|Direct twisted residue evaluations|72|
|Independent prime/coefficient transport checks|144|
|Direct natural Kummer symbols|12|
|Split-place nonseventh phi tests|6|
|All F7^4 vectors in the independent kernel enumeration|2,401|
|Normalized F49 natural coefficient directions|2,352|
|Nonzero F49 twisted kernel vectors|48|
|Joint coefficient/vector pairs, each implementation|112,896|
|Compatible pairs|0|
|Primary independent base-prime reindexings|1,296|

The independent program uses theta=zeta^-1, cyclic group-ring norm products,
direct seventh-power symbols, a sqrt5 residue-field basis, determinant expansion
and Cramer's rule. It imports no primary arithmetic code. The primary uses
multiplication determinants, complete rational discrete logs, and modular row
reduction. No new point counts were needed.

The release verifier regenerates complete JSON outputs in a scratch copy,
checks pre/post hashes,17 named inherited leaves through10 nested archives,
and tests rejection of altered residue data, a false matrix entry, an invented
compatible-pair count, and a modified package payload. Final fresh-extracted
replay and ZIP integrity results are recorded externally rather than inserted
into a self-referential package hash.

The first streaming-session predecessor launch failed before execution; its
observed replacement passed. Broad source discovery returned irrelevant pages,
which were discarded; the required Milne CFT theorem pages were then opened
and rendered directly. The analytic period and old class-number inputs remain
inherited, not independently re-proved. All incidents and failed strengthenings
are recorded in DEVELOPMENT_FAILURES.md.

No new Lean compilation or independent mathematical review took place.

## 6. Next obligation

On COMPLETE H(C) subset U, the remaining target is depth one. On unrestricted
support, depth-two beta must now ramify outside U. Its new columns must be
included with the chi^-1 weights, not deleted or replaced by eta's ordinary
rows. At depth one,29 and491 are not automatically bad; their new local-zero
rows cannot be reused without a fresh justification. The CM branch, higher
Hilbert levels, full signature and Beal remain separate obligations.
