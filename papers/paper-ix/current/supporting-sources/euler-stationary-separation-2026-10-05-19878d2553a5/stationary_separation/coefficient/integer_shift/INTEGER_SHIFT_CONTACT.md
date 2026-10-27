# Integer-shift closure test with the actual source

This is a disjoint continuation of the audited full-recurrence note. It uses
only ordinary integer shifts, the existing actual terminal161 chart, and the
three already fixed control parameters. It does not use the rejected source
umbral dictionary or introduce a new jet hierarchy.

## 1. Correct denominator dictionary

Distinguish

    Q(x)=x(2x-1),       D(x)=Q(x+1)=(x+1)(2x+1).

The exact polynomial identity is

    Q(x)P_n(x-1)=Q(x-n)P_n(x),
    Q(x-n)=2n^2-(4x-1)n+Q(x).                            (1)

Thus, for theta=t d/dt and h_+(s)=h(s+1),

    Q(x)T_c h_+(x-1)
       =2T_(theta^2 c)h(x)-(4x-1)T_(theta c)h(x)
          +Q(x)T_c h(x).                                (2)

The source has denominator D, not Q at the same argument:

    D(x-n)A(x-n)=(9^(x-n+1)-1)/8.                        (3)

Confusing these two quadratics would shift the coefficient of the index jet
by4. We retain (1)-(3) without dividing by a vanishing polynomial.

For the actual normalized coefficients define

    G(x)=sum gamma_n P_n(x)A(x-n),
    V(x)=sum n gamma_n P_n(x)A(x-n),
    U(x)=sum n(n-1)gamma_n P_n(x)A(x-n),
    C_lambda(x)=sum gamma_n lambda^-n P_n(x), lambda=1,9.

All these series converge on Z_2. Multiplying each source term by D(x-n)
and using D(x-n)=D(x)-(4x+3)n+2n^2 gives

    2U-(4x+1)V+D G=(9^(x+1)C_9-C_1)/8.                  (4)

Separately (1) and (3), applied with the source shifted by -1, give

    8Q(x)G(x-1)=9^x C_9(x)-C_1(x).                      (5)

Equivalently, this follows directly by cancelling
Q(x)P_n(x-1)/D(x-1-n)=P_n(x). Combining (4) and (5) yields

    2U-(4x+1)V+D G=9Q G(x-1)+C_1.                       (6)

Every source value in (2)-(6) is at an integer translate of a point in Z_2.
No half-shift continuation is invoked.

## 2. Uniform leading arithmetic on the actual chart

Let x=10202+2^15 Z. The actual coefficient and source units used in the
parent note imply, uniformly,

    V/2^154=3 mod8,        U/2^159=7 mod8,
    C_1/2^155=7 mod8,      C_9/2^155=3 mod8,
    G(x-1)/2^153=1 mod8.                                 (7)

For the two new plain transforms only packets0 and1 matter modulo2^158.
We have gamma_1/2^153=43 mod64 and P_1(x)/2=7 mod16. Thus
C_1/2^154=1+11*7=14 mod16, while multiplying packet1 by9^-1=9 mod16
gives C_9/2^154=1+11*7*9=6 mod16. Packet2 has valuation158,
and every other omitted packet has larger value valuation.

At x-1, packet1 has valuation153 and normalized unit3 mod8. Packet0
contributes2A(x-1)=6 mod8 at this scale. Every other packet has value
valuation at least159. This proves the shifted-source unit in (7).

Since Q(x)/2=7 mod8 and D G is divisible by2^178, both sides of (6)
have valuation154 and normalized unit5 mod8. On the right the terms are
respectively valuation154/unit7 and valuation155/unit7. They balance
-(4x+1)V rather than force V to vanish.

## 3. Differentiate once, retaining both shift-product terms

Ordinary differentiation of (6) is exactly

    2U'-(4x+1)V'-4V+D'G+DG'
      =9Q G'(x-1)+9Q'G(x-1)+C_1'.                       (8)

The following uniform bounds suffice:

    v2(U')>=158,        v2(C_1')>=156,
    G'(x-1)/2^152=3 mod8.                                (9)

For U', packet2 has the extra weight2 and derivative valuation158;
packets161 and162 have derivative valuations at least158 after their
weights n(n-1). All other lower and upper packets have stronger bounds.
The remote tail is controlled by the factorial derivative bound already
used in the parent note.

For the remaining derivative calculations, two finite integer products give

    P_161'(10202)/2^153=5 mod8,
    P_161'(10201)/2^152=3 mod8.                            (10)

They can be verified by the recurrence
p_(j+1)=p_j Q(x-j), p'_(j+1)=p'_j Q(x-j)+p_j Q'(x-j),
starting at p_0=1,p'_0=0. The factorial second-derivative bound is at
least144; hence changing x by2^15 Z preserves both units in (10).
For C_1', the only contributions below valuation156 are packets1 and161:
after division by2^153 their units are3*7=5 and7*5=3 modulo8.
They sum to0 modulo8. All remaining packets have valuation at least157.
This proves v2(C_1')>=156 without assuming stationarity.

For G'(x-1), packet161 contributes7*3=5 modulo8 at scale2^152.
The two derivatives of packet1 contribute respectively2 and4 modulo8:
P_1'(x-1)=3 mod8, P_1(x-1)=1 mod8,
A(x-2)=1 mod8, and A'(x-2)/2=1 mod8.
Their total is6 modulo8. Packet0 begins at valuation155 and all other
packets are higher. The sum5+6=3 mod8 proves the last assertion of (9).

Consequently the first two terms on the right of (8) each have valuation153,
with normalized units5 and7 modulo8. Their sum has exact valuation155,
since5+7=4 modulo8. The term C_1' is more divisible and does not remove it.
There is a real two-bit cancellation between the shift derivative and the
factor derivative; dropping either derivative would give a false obstruction.

At every actual stationary point the known constrained-tangent theorem gives
V'/2^155=7 mod8. With G'=0 and G divisible by2^178, the left side of (8)
therefore has valuation155 and normalized unit

    -(4x+1)(V'/2^155)-2(V/2^154)=-7-6=3 mod8.             (11)

Thus the complete right side has this same unit, too. In particular its
nonzero derivative is fully compatible with actual stationarity.

## 4. Exact surviving contact equations and scope

At a hypothetical actual double contact G=G'=0, equations (6) and (8) reduce to

    2U-(4x+1)V=9Q G(x-1)+C_1,
    2U'-(4x+1)V'-4V=9Q G'(x-1)+9Q'G(x-1)+C_1'.          (12)

Their two sides have fixed nonzero valuations154 and155, respectively,
and the units just proved agree. The source at x-1 is actually nonzero,
but its value balances the surviving index jet. The additional plain
transform is also actually nonzero. The integer-shift identity does not
force either index jet to vanish or supply a strict estimate for the
stationary value of G. These two-jet equations therefore do not exclude
contact. No iteration to an unbounded shifted-jet hierarchy is claimed.

The checker verifies the exact value and derivative identities using
independently assembled G(x-1), C_1, C_9, U and V on the three fixed
controls. It additionally records sharper observed units for U', C_1',
and C_9'; only the bounds stated in (9) are used as uniform theorems.

The precision is384 global bits, with a205-bit stationary Z lift. The x
uncertainty is220 bits. First and second factorial derivative estimates
from the parent proof make all reported valuations and units insensitive
to that uncertainty. The coefficient cutoff and local degree25 truncation
use the same proved bounds as the audited parent checker. The exponential
9^x is evaluated on its ordinary dyadic branch at the lifted representative;
the exact finite identities are checked there, while the proved stability
bounds transfer the reported low units to the true center. No new T values, parameter digits,
approximation ranks, or universal nonvanishing conclusion occur.
