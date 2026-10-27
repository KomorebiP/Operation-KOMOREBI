# Arithmetic support consequences

All statements retain TARGET_CONTRACT.md. Let q be a variable divisor of C,
f_q its residue degree in K, h_q=v7(q^f_q-1), and t_q=1+v7(v_q(C)).
Power conditions are at prime ideals v, not chosen independently between
conjugate residue fields. At split q both conjugate phi values have the
same 7-power status because their product is -1.

## Universal necessary condition

Because beta must ramify somewhere, at least one actual beta place satisfies

    h_q>=1, phi in (k_v^*)^7.

More precisely phi is a 7^min(t_q,floor(t_q/2)+1) power there. At depth2
there must be a place satisfying all of

    h_q>=2, v7(v_q(C))=1, phi in (k_v^*)^49,
    rho_natural|G_v=I mod49, alpha|G_v=0.

This is a strengthened necessary condition, not a sufficient condition for
an actual representation or solution. It holds with unrestricted additional
prime support. A maximal-order inertia place for nontrivial eta also requires
phi in (k_v^*)^(7^t_q); not every nonmaximal eta-ramified place has been shown
to satisfy it.

## B59.7. Exact test in the retained ten-prime universe

U={97,197,293,491,587,883,1373,1471,1567,1667}.

| q | residue degree | h_q | phi a seventh power? | phi a forty-ninth power? |
|---|---:|---:|---|---|
|97|2|2|no|no|
|197|2|2|yes|yes|
|293|2|2|no|no|
|491 (both places)|1|2|no|no|
|587|2|2|no|no|
|883|2|2|yes|yes|
|1373|2|3|yes|yes|
|1471 (both places)|1|2|no|no|
|1567|2|2|no|no|
|1667|2|2|yes|yes|

Thus NONE of the six rational primes {97,293,491,587,1471,1567} can support
beta at ANY depth under the retained geometry. They may still divide C.
They also cannot be maximal-order eta inertia places. Do not infer that
eta itself is locally trivial at every one of them at every depth.

For the four remaining inert primes, q=1 modulo7, and phi^(q+1)=-1 in
F_(q^2). The order of phi divides2(q+1), prime to7. Thus phi is a 7^d power
for every d in their finite multiplicative groups. The positive entries
are structurally expected, not numerical near-zero tests.

Under COMPLETE H(C) subset U, Block58 gives n<=2 and eta=1. If n2 occurs,
beta ramification is now restricted to

    S={197,883,1373,1667}.

Arbitrary additional low-h divisors cannot support beta at n2. No prime
multiplicity is assumed prime to7. Every actual beta-supporting q has
multiplicity divisible by7 but not49, as previously required.

In particular

    H(C) subset {97,293,491,587,1471,1567} => n=1.

This permits arbitrary low-h prime divisors of any size or multiplicity.
More generally, within COMPLETE H(C) subset U, n=1 whenever none of the
four remaining primes divides C with v7(v_q(C))=1. This is not an assertion
that those multiplicities are automatically absent.

## Compatible natural coefficients

Normalize a_5=1 and write alpha=(u,r,1), u in F49, r in F49^*.
The residual Kummer rows (phi,3,sqrt5) at the four remaining primes are

    197: (0,6,6), 883: (0,0,0),
    1373: (0,3,4), 1667: (0,3,4).

At n2 actual beta ramification requires the corresponding row to vanish.
Hence ramification at197 forces r=6; ramification at1373 or1667 forces
r=1. It is impossible to ramify at197 and either1373 or1667 in the same
actual representation. The four displayed residue rows alone leave all2352 normalized
natural coefficient directions compatible with ramification solely at883.
B59.9 below also forces u!=0 at depth2, reducing this particular necessary
coefficient set to2304 directions. These counts are not representation counts.
The coefficient u is not determined by this calculation.

This is not a universal coefficient-field descent theorem. It uses the
same global coefficients and the specified actual support, with all
directions over F49 checked independently.

## Strictness of the forty-ninth-power test

At the inert prime14503, h=2, phi is a seventh power but NOT a forty-ninth
power in F_(14503^2). Both places above split18229 have the same property.
Consequently these primes are not excluded by this period test at depth1,
but cannot support beta at depth2. This gives explicit evidence that the
new 49-level condition is genuinely stronger than its residual version.
No assertion is made that an actual solution uses any of these primes.

The declared search inspected every prime11<=q<=20000 with h>=2, including
both split places:108 prime ideals. It found these three prime-ideal
controls. The bounded search is not a classification of all high primes.

## Remaining boundary

No theorem removes the S-prime cases at depth2. The unbounded support problem
remains. A successful single off-diagonal period test does not make the full
period lattice divisible, prove beta zero, or construct a global Frey model.
CM nonboundary points, higher Hilbert levels, the full signature and Beal
remain separate obligations.


## B59.9. The unit coefficient detects bad13

At any variable bad place with Q=1 modulo7, a vanishing local natural class
alpha would make the entire natural residual representation identity:
its two characters are trivial locally, so a zero extension class is a
trivial unipotent representation. B59.6 then requires phi to be a seventh
power. Equivalently,

    phi not a seventh power at a variable bad place => alpha|G_v != 0.

At the inert prime13, the exact residue symbols in the phi basis are

    phi^24=5+10phi !=1, 3^24=1, (sqrt5)^24=1 in F169.

Thus if13|C, the local natural class equals a_phi times a nonzero Kummer
class. The period obstruction forces a_phi!=0. Block52 supplies the
opposite good-reduction implication13 not dividing C =>a_phi=0. Together,

    a_phi=0 if and only if13 does not divide C.

This determines vanishing, not the numerical value of a_phi. In particular
n>=2 already forces13|C, hence a_phi!=0 throughout the depth-two target.
The coordinate u remains otherwise undetermined by this argument.

There is also a depth-one consequence. On the good13 subcase, a_phi=0.
At an inert variable q=-1 mod7, rational units are seventh powers because
7 does not divide q-1, and [sqrt5] vanishes since twice it is [5]. Therefore
alpha is locally zero. Such a prime may divide C only if phi is a seventh
power there. In particular97,293,587,1567 cannot even divide C on this
subcase. This is a divisor restriction, not a general exclusion of those
primes when13|C and not a proof of the depth-one branch.
