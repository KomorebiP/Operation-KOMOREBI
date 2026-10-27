# Beal research, Block 52
## Scalar Frobenius, global Kummer coordinates, and depth-sensitive prime restrictions

**Release v5.2.0 — 19 September 2026**

This block completes a bounded part of the next mathematical objective: it
calculates an actual global Kummer coefficient on the good-13 subcase, obtains
compatible local coefficient relations at three further primes, and adds
fixed-prime restrictions on the actual stable-lattice depth.

It does not eliminate the remaining reducible branch of A^3+B^5=C^7. The
full signature and full Beal remain unproved in this project. Arithmetic
claims below use the explicit inherited input contract in TARGET_CONTRACT.md.
No new Lean certificate or independent mathematical review is claimed.

## 1. A global coefficient is now determined on a stated subcase

Write the natural class, in the single global coordinate system retained
from Block50, as

    alpha = a_phi[phi] + a_3[3] + a_5[sqrt5],
    phi=(1+sqrt5)/2,     a_3*a_5 != 0 in F_49.

The new result is

    13 does not divide C  ==>  a_phi=0.                    (A)

The mechanism uses the actual Frey Jacobian, not a generic extension. Exact
counts at good13 leave four parameter pairs, all with characteristic
polynomial (T^2-13)^2. Finite-field Frobenius is semisimple, so its square is
actually13I. Because13 is inert in K and the twist has value-1 there,

    rho(Frob_(13))=-13I.

The natural residual class is consequently zero locally. At that same
place, the images of3 and sqrt5 are seventh powers but the image of phi
is not. In F13[r]/(r^2-5), the explicit symbols are

    phi^24=10+5r !=1,   3^24=r^24=1.

Restricting the global class therefore isolates and kills a_phi. There is
no independent normalization of coefficients at different places.

The same scalar identity calculates one actual local higher diagonal value:
for eta_n=a_n/chi_7,

    eta_n(Frob_(13))=-1/13 mod7^n.

It lifts locally through all n. It does not show that the global diagonal
character lifts at its ramified places.

Before(A), the recorded three-generator support with nonzero a_3,a_5 had
2352 projective coefficient candidates over F49. On this subcase there are
48 possible ratios a_3/a_5. This counts candidate Kummer directions only,
not realized representations or a fraction of the conjecture solved.

## 2. The same coefficients now control several local restrictions

At the primes29,43,71, seventh-power symbols give explicit local functionals
on the same global vector(a_phi,a_3,a_5). On the subcase(A), they reduce to

| prime | local coefficient, relative to the image of global[3] |
|---:|---|
| 29, either split place | a_3+5a_5 |
| 43, inert place | a_3+2a_5 |
| 71, either split place | a_3 |

The third expression is always nonzero. At depth n=1, Block51's coupling
criterion requires the natural class to vanish at every place where the
actual opposite class beta ramifies. Thus, when13 does not divide C:

- beta cannot ramify above71;
- ramification above29 requires a_3/a_5=2;
- ramification above43 requires a_3/a_5=5.

In particular beta cannot ramify over both29 and43 at depth one. Since it
must ramify somewhere, at least one eligible rational divisor other than71
must occur in C. This does not assert ramification at every divisor of C.

At good29 and good43, point counts instead force alpha to be nonzero.
They yield ratio exclusions2 and5 respectively. When13,29,43 are all good,
46 of the48 projective Kummer candidates remain. None is asserted realized.

## 3. Deeper lattices force two fixed primes into C

In the common global basis, a Frobenius matrix at norm Q=1mod7 has the form

    M=[[a,b],[7^n c,d]],   a=d=1mod7.

If n>=2, then det_E(1-M) lies in49O. Its norm to Q7 is divisible by7^4.
For an actual good reduction this gives

    2401 divides #J^nu(F_Q).                               (B)

At29 the Weil bound gives #J^nu(F29)<2401, independently of any finite
search. Hence n>=2 forces29|C. At43, complete exact counts give
v_7(#J^nu(F1849))<=2 for all admissible good residues, so n>=2 also forces
43|C. Together,

    n>=2  ==>  29*43 | C.                                 (C)

No ordinary-multiplicity or norm-congruence hypotheses are needed for(C).
Conversely, good29 or good43 forces the actual depth to be one.

The same finite check at71 excludes even the required residual Frobenius
polynomial on every good equation residue. Therefore71|C throughout the
inherited reducible branch. Including the earlier3990|C restriction gives

    283290|C,
    n>=2 ==> 353262630|C.

These divisibilities leave infinitely many integers and do not constitute a
contradiction. The higher-depth condition concerns the actual global lattice,
not an arbitrarily selected congruence modulus.

## 4. What changes at depth three and for the old ray example

When13 does not divide C, the two surviving Kummer generators are locally
trivial at inert primes q=-1mod7. Such primes cannot carry a ramified upper
endpoint, because the endpoint criterion requires a nonzero local alpha.

Under the additionally assumed ordinary regime, n=3 is an upper endpoint
at every ramified supporting place. Its eligible support is therefore
reduced from six residue classes to

    {1,8,22,29} modulo35.

This does not prove that the ordinary regime holds or eliminate depth three.

The old nonliftable ray-character family at q=1504231 required a nonzero
local lifting obstruction, while3 and sqrt5 are seventh powers there.
Condition(A) makes alpha locally zero, contradicting that family's required
coupling. Thus the proposed ray realization is excluded when13 is good.
It is not excluded merely from13|C, and other actual diagonal characters
have not been exhausted.

## 5. Verification and the corrected failure

Block51 and all six selected predecessor checks were reproduced first in
isolated copies. The original ZIP is preserved byte for byte.

The new finite certificate covers exactly four auxiliary primes:

| q | admissible good pairs | pairs matching the residual polynomial | maximum v7 of the twisted Jacobian order |
|---:|---:|---:|---:|
| 13 | 156 | 4 | 4 |
| 29 | 116 | 8 | 2 |
| 43 | 258 | 36 | 2 |
| 71 | 710 | 0 | 0 |

One implementation counts164 weighted curve orbits. A separate implementation
counts all1240 admissible pairs directly, using explicit quadratic-field
square-root tables rather than norm characters. It also independently checks
smoothness, the twist signs, and the squared-Frobenius calculation. Every
point count and derived order agrees. Another exact script checks2500
integral matrices, the Kummer symbols and local functionals, and negative
controls for the theorem boundaries.

An initial exploratory orbit filter was wrong: it transferred the seventh-
power equation condition from an orbit representative to every member.
Weighted curve isomorphisms do not preserve that condition. The source is
retained as failed evidence, the filter was corrected to test each member,
and direct enumeration independently confirms complete coverage. No result
in this release depends on the faulty output.

All universal steps are separated from their finite checks. Classical
Frobenius facts and inherited local/global representation inputs remain
explicit source dependencies. The independent code is not an independent
proof reviewer. No new Lean compilation was attempted.

## 6. Remaining mathematical obstruction

The ratio a_3/a_5 is still unknown, and a_phi remains undetermined on the
general13|C subcase. The actual global diagonal character is not known.
Depth-one support can avoid the newly forbidden combinations, and depth
three can still use permitted places. Exceptional norm congruences and
prime multiplicities can permit deeper n.

The next useful step is to exploit the compatible coefficient functionals
in an actual global ray-class or arithmetic-descent calculation, while
keeping the good13 and bad13 branches separate. Replacing the old excluded
ray example by an arbitrary new abstract extension would not close this gap.

The CM cover and higher Hilbert levels are separate and unchanged. See
CONTINUE_HERE.md for the executable next-block contract and exact remaining
claims.
