# Depth-one localization and the uniform good-reduction bound

Written consequences of DIAGONAL_RIGIDITY.md under the explicit inherited
arithmetic inputs. These are restrictions on the remaining reducible
(3,5,7) branch, not a proof of its nonexistence.

## 1. The good 13 subcase has depth exactly one (B53.5)

Block52's complete finite certificate and semisimple abelian Frobenius
argument give, when 13 does not divide C,

    rho(Frob_(13))=-13 I,     chi_7(Frob_(13))=169.

The scalar identity holds on every stable integral lattice. Hence the
actual diagonal correction satisfies

    eta_n(Frob_(13))=-1/13 mod 7^n.

But w_7(-1/13-1)=w_7(-14/13)=1. If n>=2, B53.3 forces eta_n=1 mod 49,
whereas -1/13 mod 49=15. This is a contradiction. Therefore

    13 does not divide C  ==>  n=1.                      (8)

No ordinary multiplicity or norm-congruence hypothesis is used. The
arithmetic claim remains conditional on the source-dependent construction
of the actual representation and on the explicit local input audit.
The converse is not claimed: n=1 can still have13 dividing C.

### Why a trace-only check would have missed depth two

Modulo49 the scalar matrix -13I and diag(169,1) have the same trace and
determinant:

    traces: -26 = 170 mod 49,
    determinants:169 =169 mod 49.

Their diagonal values differ:36,36 versus22,1. Thus a characteristic
polynomial congruence at 13 does not itself force the needed contradiction
at n=2. The proof uses the ACTUAL scalar matrix and the globally identified
diagonal characters. This ambiguity is retained as a negative control.

## 2. Every good place gives an order bound (B53.6)

Let v be a good place of the twisted Jacobian outside 7, with Q=Nv, and
put m=floor(n/2)+1. B53.3 gives d(Frob_v)=1 mod 7^m. Also n>=m. Thus

    det_E(I-rho(Frob_v))
      =(1-a)(1-d)-7^n bc  is in 7^m O.                   (9)

Taking the norm from the unramified quadratic coefficient field gives

    7^(2m) divides #J^nu(F_Q).                            (10)

There is NO hypothesis Q=1 mod 7 in (9)--(10). This is the improvement over
the earlier determinant test. The usual four-dimensional Tate determinant
is the norm of the rank-two determinant; we do not confuse a rank-two
coefficient representation with an elliptic curve.

The Weil bound and positivity of the order now imply

    7^(2m) <= #J^nu(F_Q) <= (1+sqrt(Q))^4,
    7^m <= (1+sqrt(Q))^2.                                (11)

Therefore any place outside the fixed bad primes whose norm satisfies
(1+sqrt(Q))^2<7^m must lie above a divisor of C. Equation (11) is a bound
on depth in terms of an actual good-reduction norm, not an absolute bound
on n independent of C.

### Two additional forced primes without new point counts

For n>=2, m>=2. The rational primes 11 and 31 split in Q(sqrt5), have norms
11 and 31, and are outside the fixed bad set. Since both are less than36,

    (1+sqrt(q))^4 < 7^4.

If either were good, this would contradict (10). Thus

    n>=2 ==> 11*31 divides C.                            (12)

Combining (8), (12), the inherited29*43 depth restriction and the existing
3990*71 divisibility yields

    n>=2 ==> 1566013238790 divides C,
    1566013238790 = 2*3*5*7*11*13*19*29*31*43*71.         (13)

Only squarefree divisibility is asserted. This condition leaves infinitely
many integers C. It neither bounds C from above nor shows that every one
of these primes ramifies in beta.

## 3. All good 13 support conclusions now apply without an extra depth assumption

Block52 gave a_phi=0 when 13 is good. Combining it with (8) gives

    13 not dividing C ==> alpha=a_3[3]+a_5[sqrt5], n=1.

At every ACTUALLY ramified supporting place, Block51 now gives t=1,s=0,
so the supporting prime multiplicity is prime to7 and the natural local
class is zero. The same compatible coefficients consequently imply:

* beta is unramified at all places over 71;
* ramification above 29 forces a_3/a_5=2;
* ramification above 43 forces a_3/a_5=5;
* these two types of ramification cannot both occur;
* beta must use another eligible divisor of C besides71 (29 or 43 are
  still allowed, as are other eligible primes).

These are now consequences of good 13 alone, rather than of good 13 PLUS
an unproved depth-one assumption. No ramification at an arbitrary divisor
of C is inferred from bad reduction alone. Neither the ratio nor the
remaining support is completely determined.

## 4. A paired-support restriction independent of good 13 (B53.7)

At depth one, allow a_phi to be arbitrary and normalize a_5=1. Write
u=a_phi/a_5 and r=a_3/a_5 in F_49, with r!=0. The compatible local forms
at the two places over 71 are

    2u+r,       5u+r.

If beta ramified at both, both forms would have to vanish. Subtraction
forces3u=0, hence u=0, and then r=0, impossible. Therefore

    n=1 ==> beta cannot ramify at BOTH places above 71.   (14)

This holds even when 13 divides C. It is not an exclusion at either place
individually. No conjugation invariance of beta has been proved in this
block. Such an invariance theorem would be needed to turn (14) into the
stronger conclusion that beta is unramified over 71 on the bad 13 subcase.

For comparison, vanishing at both places over 29 forces u=0,r=2, while
vanishing at the inert place over 43 forces r=5. The exact coefficient
check tests all 2352 normalized pairs(u,r) with r!=0, but it does not turn
these pairs into realized representations.
