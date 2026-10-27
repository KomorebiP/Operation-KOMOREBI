# B61.4–B61.5. The common-coefficient contradiction and exact consequences

Retain TARGET_CONTRACT.md. Let S={197,883,1373,1667} and
U={97,197,293,491,587,883,1373,1471,1567,1667}.

## B61.4. No depth-two opposite extension with ramification contained in S

Suppose the actual n=2 and every beta-ramification place lies above S. The
actual beta is nonzero, unramified outside S and split at7. The determinant
and nodal-period argument makes it locally zero above29,71,491. It descends
cohomologically to Q. Correct chi^-1 reciprocity over Q(zeta7) gives

    (s_197,s_883,s_1373,s_1667)=c*(1,0,0,3), c in k.

If c=0 then all inertia is zero, so the inherited inertia localization
injectivity gives beta=0, impossible. Therefore c!=0, and beta must ramify
at BOTH197 and1667.

At actual ramification the SAME natural Kummer class alpha vanishes. The
natural residue rows in coordinates(phi,3,sqrt5), computed with common
rational residue generator2, are:

    197: (0,6,6)
    883: (0,0,0)
    1373:(0,3,4)
    1667:(0,3,4).

The phi symbols are1 at all four primes. For rational units, restricting to
the inert quadratic residue field multiplies every logarithm by the same
nonzero scalar q+1 modulo7, so zero conditions and the displayed relative
normalization are unchanged. The sqrt5 logarithm is half that of5, namely
4*ell_q(5) modulo7. The independent computation evaluates all three symbols
in F_(q^2) directly using the sqrt5 basis.

At197 the equation6*a_3+6*a_5=0 forces a_3/a_5=6. At1667 the equation
3*a_3+4*a_5=0 forces a_3/a_5=1. More invariantly,

    det([[6,6],[3,4]])=6 in F7,

so the two restrictions force a_3=a_5=0, contradicting a_3*a_5!=0. No choice
of a_phi repairs this because its two local symbols vanish. This proves

    n=2 => beta ramifies somewhere outside S.          (6)

Equation (6) is conditional on the actual inherited branch. Additional
primes may divide C, including all the previously forced primes, without
invalidating the proof. But additional beta ramification outside S is the
remaining case, not a case covered by the four-column matrix.

## B61.5. Complete high-congruence support in U has only depth one

Write

    H(C)={q|C, q outside{2,3,5,7}: v7(q^f_q-1)>=2}.

Assume COMPLETE H(C) subset U. Block58 gives n<=2. At depth2, inherited
same-lattice and period conditions force beta to ramify only at high primes
and exclude the other six rational primes in U. Thus its entire ramification
would lie above S, contradicting (6). Hence

    COMPLETE H(C) subset U => n=1, eta_n=1.            (7)

Arbitrarily many additional low-congruence divisors are allowed, with arbitrary
multiplicities. No assumption that high-prime multiplicities are prime to7
has been introduced. The previous exceptional condition v7(v_q(C))=1 was
permitted throughout the contradiction, not discarded.

In fact, without assuming COMPLETE H(C) subset U, every actual depth-two beta
must ramify outside U: the six primes of U\S are universally excluded from
beta ramification by Block59, and all-S support is now excluded. This does
not identify the outside prime or bound all possible support.

## Local positive controls remain valid

The four Block60 local primitive Frey families still satisfy the full
49-torsion criterion, including E=3*5^9*A/C0^35 being a49th-power residue.
Neither these local facts nor the local q-adic roots are retracted. What is
excluded is gluing such possible supporting places into a SINGLE actual
global beta with no ramification outside S while retaining the common alpha
and the forced local Frobenius values.

This does not prove that197,883,1373,1667 can never be individual beta-support
primes on a larger conductor. It proves that together they cannot supply the
entire ramification of a depth-two beta in the retained branch.

## Remaining obligations

Depth one remains open, including on the class in (7). General depth two with
outside-U beta ramification remains open. Unrestricted higher depth and high
support remain open. The CM nonboundary-point branch, higher Hilbert levels,
the full signature, and full Beal are separate unresolved tasks. Independent
upstream proof review is still required. No percentage of Beal completion is
assigned to the 112,896 finite coefficient tests or to the block number.
