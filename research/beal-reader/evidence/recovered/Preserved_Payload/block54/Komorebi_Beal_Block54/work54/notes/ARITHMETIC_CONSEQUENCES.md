# Consequences for the retained reducible branch

All statements here assume the exact actual-representation inputs inherited
through Block53. This block does not independently reprove the Frey geometry.

## B54.9. Every actual beta-support norm agrees with1 through m digits

The opposite extension beta must ramify somewhere at an eligible variable
prime, by the retained support theorem. At EVERY such place,

    n=t_v+2s_v,  t_v=1+v_7(v_q(C)),
    h_v=v_7(q^f-1)>=floor(n/2)+1,  s_v<h_v,
    alpha|G_v=0.                                           (1)

Here f is the actual residue degree of q in K, and v_q(C) is the multiplicity
of q in C, not the value q and not C itself. An equivalent depth bound is
n<=2h_v-1. No ordinary-multiplicity hypothesis is used.

If every eligible divisor of C has h_v=1, then n=1. The older conditional
alternative {1,3} is therefore sharpened to {1} on this norm hypothesis alone.
This does NOT prove that all divisors of a hypothetical C have h=1.

## B54.10. Higher depth requires an additional prime divisor

For n>=2, at least one beta-supporting q divides C with

    q^f=1 mod49.                                          (2)

For q outside5,7, splitting in K gives the exact alternatives

    q mod5 in {1,4}: q=1 mod49;
    q mod5 in {2,3}: q=1 or -1 mod49.

Their six classes modulo245 are

    {1,48,97,99,148,197}.                                  (3)

The previously forced divisor for n>=2 is

    D=1566013238790=2*3*5*7*11*13*19*29*31*43*71.

None of its variable primes can support beta at n>=2: the eligible ones have
h=1, and the others are ineligible. Thus n>=2 forces some additional prime
q outside this displayed list satisfying (3). No particular one of those
primes is forced; (3) has infinitely many candidate primes.

The new theorem restricts SUPPORT, not just divisibility. A prime can divide C
and nevertheless be unramified in beta, as71 already illustrates. It would be
wrong to infer a contradiction from the continued divisibility13|C, or to say
that every prime divisor must satisfy (3).

## B54.11. A conditional finite-support exclusion

Assume every variable divisor of C belongs to P0 union {491}, where
P0={11,13,19,29,31,43,71}. The exact reduced quotient is zero. Then every
beta-supporting place has n=t and h>=n. In particular n<=2. If n>=2,

    n=2,     beta is supported above491,
    t_491=2, v_7(v_491(C))=1.                              (4)

Thus its491-multiplicity must be divisible by7 but not49. If that multiplicity
is prime to7, n=1. No assumption bounds the remaining multiplicities.
This eliminates depth3 and higher on this explicit finite-support subcase.
It does not eliminate depth2, and no proof bounds general C to this support.

With both491 and1471 allowed, the reduced quotient is C7, not zero. The
universal character-exponent conclusion there is e=1, hence s<=1 and
n<=h+1<=3 at a supporting place. At n=3 the alternatives t=1,s=1 and
t=3,s=0 are both retained; an individual beta-supporting prime need not have
ordinary multiplicity. No actual configuration is constructed here.

## Changes to previously open character cases

The old q=1504231 nonliftable ray family has h=1 and nontrivial inertia. It
cannot be the actual eta_n at any n>=2, including the bad13 subcase. The
family remains a valid character construction in its stated abstract
class-field setting; the new representation-specific inequality excludes
its identification with the Frey diagonal.

The actual global obstruction delta(a_n) is now zero at all depths. Unknown
eta_n values, unknown Kummer coefficients, and a nonzero beta remain possible.
Good13 still forces n=1 by Block53, and a_phi=0 by Block52. On that branch,
ramification over29 requires a_3/a_5=2, over43 requires5, and beta is unramified
over71. Other eligible supporting primes remain possible. On bad13 no new
semilinear coefficient descent or paired support is assumed.

## The remaining target

The next arithmetic problem is to exclude simultaneously compatible actual
alpha, beta, eta, and toric-line positions under (1), (R), and cup-zero.
It is no longer correct to leave a possibly nonzero ACTUAL delta(a_n) in the
gap ledger. It is equally incorrect to replace that gap with an unsupported
claim beta=0, eta=1, or an increase in the stable-lattice depth.

The CM cover and three higher Hilbert-level branches are unchanged. Full
(3,5,7) and full Beal remain separate unsolved project obligations.

## B54.12. Simultaneous reciprocity and Kummer coordinates eliminate depth3

Assume every variable divisor of C belongs to P0 union{491,1471}. Then

    n<=2.                                                  (5)

This improves the exponent-only bound n<=3 without making the nonzero
abelian ray quotient disappear.

Proof. The exact reduced quotient is C7, so B54.8 gives n<=3. Suppose n=3.
If eta_3 were trivial, (4) in REDUCED_RECIPROCITY would force h>=3 at every
beta-support prime, whereas all eligible primes of this support have h<=2.
Since beta must ramify somewhere, eta_3 is nontrivial.

Write eta_3=1+49 theta with theta valued in F49. For the coordinate order

    491:phi=74, 491:phi=418, 1471:phi=478, 1471:phi=994,

the full reduced five-row reciprocity matrix is

    4 3 5 2       phi
    1 1 1 1       2
    5 5 5 5       3
    6 6 2 2       sqrt5
    4 4 2 2       7.

Its kernel overF7 is the line generated by (3,4,6,1). Base extension toF49
preserves this rank and kernel. Therefore every nonzero theta has nontrivial
inertia at all four displayed places. This forces paired ramification HERE
by an exact reciprocity calculation, not by an unproved conjugation principle.

At depth3, eta-ramification implies j=w(N_11)=2 by Block53's m=2 precision.
The proof of B54.2 gives x a unit, s>0, j=t+s and t+2s>=3. With t>=1 these
conditions force t=s=1 and w(N_21)=3. Thus beta ramifies at all four places.
B54.1 requires the SAME global alpha to vanish at all four.

The local Kummer equations in the global coordinates(a_phi,a_3,a_5) have matrix

    4 5 6
    3 5 6
    5 5 2
    2 5 2.                                                 (6)

The determinant of the first three rows is-20, which is1mod7. Thus (6) has
rank3 overF49, forcing alpha=0, contrary to a_3*a_5!=0. More explicitly,
the first two equations force a_phi=0 and a_3/a_5=3; the latter two force
a_3/a_5=1. These are incompatible. This proves (5). QED.

The exact local logarithms and Smith certificate establish the complete
finite arithmetic assertions in this proof. A separate field/logarithm
implementation verifies the forced support and rejects all2352 normalized
F49 coefficient vectors. No possible integer C has been enumerated.

This is an actual incompatibility theorem on an explicit support class. It
is not a proof that every C has that support, not a proof eta=0 in general,
and not an exclusion of depths1 or2. At depth2 any beta-supporting491 or1471
still requires v_7(v_q(C))=1. Other prime supports remain open.
