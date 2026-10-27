# Exact radix compiler with the actual Euler cutoff retained

Base: Euler-shifted-obstruction-20261005, archive SHA256
7125e5ed1ce7b0a3fb25473284ac92fa1a4c6db42862980f1b07cbfb50233dea.

The full regularized Euler measure has a precision-independent six-state
spatial radix compiler. The prescribed finite prefix also has a finite
meromorphic compiler for each fixed cutoff. Retaining its two polar
coefficients produces an explicit correction in the moment equations.
These statements do not prove that the stationary critical value is nonzero.

## 1. Two different section operations must not be confused

Write y=exp(t) and R(y)=2y(y^2+1)/(y^4-y^2+1). The previous checkpoint
constructs the bounded measure mu with Amice transform R(1+T) and moments
b(s)=(1+3*9^s)Ecal(s).

Spatial section restricts mu to a residue b modulo2 and pushes it forward
by u -> (u-b)/2. On its transform it is

    C_b F(y)=y^(-b/2)[F(sqrt(y))+(-1)^b F(-sqrt(y))]/2.

The formula is first interpreted on a small disc through the measure,
and the rational expressions below give its continuation. This is not
the operation retaining the even or odd Taylor coefficients in T=y-1.

Put S=2(y+1)/(y^2-y+1), U=1/(1+y+y^2), V=y/(1+y+y^2). Exact identities are

    C_0 R=0,        C_1 R=S,
    C_0 S=2U+4V,    C_1 S=4U+2V,
    C_0 U=U+V,      C_1 U=-U,
    C_0 V=-V,       C_1 V=U+V.

Thus on a coefficient column (a,b) representing aU+bV, the matrices are

    M_0=[[1,0],[1,-1]],   M_1=[[-1,1],[0,1]].

They satisfy M_0^2=M_1^2=(M_0 M_1)^3=I. The two initial vectors have orbits

    (2,4), (2,-2), (-4,-2),
    (4,2), (-2,2), (-2,-4).

These are precisely the six recurrent states. Each state has total mass
(a+b)/3, since U(1)=V(1)=1/3. Consequently every depth>=2 dyadic residue
mass is 0, 2, or -2. The states and matrices are exact over Q_2 and do not
depend on a chosen modulus. Bits are read from least significant upward.
There are also the initial transient states R,S and the zero state.

This is a genuine finite-state arithmetic input. It determines the whole
bounded regularized Euler measure, including all moment derivatives.

## 2. The Amice Taylor-coefficient kernel instead has infinite linear rank

This does not contradict section1. Let a_n=[T^n]R(1+T) and let Lambda_0
select the even Taylor coefficients. The functions Lambda_0^e R(1+T),
e>=0, are linearly independent over Q_2.

Indeed the original four poles are T=zeta-1 where zeta runs over primitive
twelfth roots. All are simple, with nonzero residues. Write alpha=1/(zeta-1).
The two alpha corresponding to zeta=exp(+-i*pi/6) have complex absolute
value L=(2-sqrt(3))^(-1/2)>1. The other two have absolute value L^(-1).
After e even sections the coefficient exponential bases are alpha^(2^e),
so the dominant poles have radius L^(-2^e). The two dominant bases never
coalesce: their quotient has order12, which does not divide any2^e.
For every new e these pole radii differ from all earlier ones, precluding
linear dependence. Equality or inequality of the algebraic poles is
field-independent, so the same argument applies after extension to Q_2.

Therefore rationality in T does not supply a finite constant-matrix
Cartier state valid over all precisions. For each fixed modulus2^P a finite
state can still be built from the integral order-four recurrence. This
paragraph excludes a precision-independent *linear coefficient kernel*,
not a nonlinear radix algorithm or the spatial compiler above.

## 3. The actual prefix has an exact finite meromorphic compiler

Let C_r(s)=(1+3*9^s)S_r(s), with the actual Bernoulli prefix from the base.
Its even-moment exponential transform is

    F_r(t)=Aegf(t) f_<r(2t)+3 Aegf(3t) f_<r(6t),
    Aegf(t)=(cosh(3t)-cosh(t))/(4t^2),
    f_<r(t)=sum_(0<=n<r) beta_n t^(2n).

As a meromorphic function of y and t=log y, it is the finite sum

    sum_(0<=n<r) beta_n t^(2n-2)
      [4^(n-1)(cosh(3t)-cosh(t))
        +36^n/12 (cosh(9t)-cosh(3t))].                 (3.1)

All Laurent y exponents lie in {+-1,+-3,+-9}. Algebraic spatial sections
on this class retain the log branch log(zeta y)=log y for 2-power torsion:

    C_b[y^j t^k] = 2^(-k) y^((j-b)/2)t^k  if j=b mod2,
                 0                        otherwise. (3.2)

The identity is a root-of-unity filter, valid as meromorphic continuation.
It does not assert that every resulting state is the Amice transform of
a measure. The exponent k belongs to {-2,0,2,...,2r-4} and is preserved.
Laurent exponents contract into the invariant interval [-9,9]; after four
sections all surviving exponents are0 or-1. Hence for each fixed r the
prefix admits a finite linear meromorphic state, of dimension O(r), with
the actual beta_n in its initial vector. The denominators in 2^(-k) are
retained. No uniform-in-r bounded integral state is claimed.

## 4. Three bits expose the exact source correction

For N=8, write H_a(t)=(C_(8,a) F_r)(exp t). Only odd residues survive.
Its principal parts are independent of r because every n>=1 term of
(3.1) is regular at t=0 after sectioning. The n=0 term is

    [y^9+y^-9+2y^3+2y^-3-3y-3y^-1]/(24t^2).

At the four odd residues its section is respectively

    (8/3)(y-3)/t^2,  (16/3)/t^2,
    (16/3)y^-1/t^2,  (8/3)(y^-2-3y^-1)/t^2.

Thus in H_a(t)=c_(a,-2)/t^2+c_(a,-1)/t+H_a^reg(t),

| a | c_(a,-2) | c_(a,-1) |
|---|---:|---:|
| 1 | -16/3 | 8/3 |
| 3 | 16/3 | 0 |
| 5 | 16/3 | -16/3 |
| 7 | -16/3 | 8/3 |

These states are meromorphic, but they remain algebraically usable. The
exact reconstruction identity is

    F_r(t)=sum_(a=0)^7 exp(a t) H_a(8t).

For h_(a,j)=j![t^j]H_a^reg(t), coefficient extraction gives

    (2s)! [t^(2s)]F_r(t)
      = sum_a sum_(j=0)^(2s) binom(2s,j) a^(2s-j)8^j h_(a,j)
        + B_8(s)                                      (4.1)

for ordinary nonnegative s, where the retained polar correction is

    B_8(s)= [1-10*25^s+7*49^s]/[3(2s+1)]
      +[-1+9*9^s+25*25^s-49*49^s]/[12(2s+1)(2s+2)]. (4.2)

The right side of (4.2) extends through its removable point s=-1.
All powers use the actual odd-unit branch d^(2s)=(d^2)^s.
The correction is nonzero, for example B_8(0)=B_8(1)=-4/3.
Discarding it would change the source even before stationarity is imposed.

For a general N and principal coefficients c, the omitted terms would be

    sum_a c_(a,-1) a^(n+1)/(N(n+1))
      +c_(a,-2) a^(n+2)/(N^2(n+1)(n+2)).                (4.3)

This formula explains why merely taking finite parts does not commute
with the residue reconstruction. The double-pole terms contribute to
every nonnegative moment after multiplication by exp(a t).

## 5. Value and derivative remain coupled with the source retained

Set p=2s+1, q=2s+2,

    U_s=1-10*25^s+7*49^s,
    V_s=-1+9*9^s+25*25^s-49*49^s.

The derivative of the exact correction is

    B_8'(s)=U_s'/(3p)-2U_s/(3p^2)
              +V_s'/(12pq)-(p+q)V_s/(6p^2q^2),

where U_s' and V_s' retain log25, log49, and log9 in the usual way.
This expression is regular on the focused odd chart, where s+1 has fixed
valuation1. An analytically interpolated finite-part contribution may be
defined without an unjustified infinite binomial sum by J_r=C_r-B_8.
Then repeated contact is exactly

    b(s)=J_r(s)+B_8(s),
    b'(s)=J_r'(s)+B_8'(s).                              (5.1)

The six-state Euler measure computes the left side and the meromorphic
prefix compiler computes the right side, preserving its actual cutoff.
No strict inequality or incompatible unit has been derived from (5.1).
The exact compiler has not removed the prescribed Bernoulli coefficients.
Their new arithmetic restriction is still the missing implication.

The directly tempting finite-state proof fails in a precise way: its
state class must be enlarged by the two polar modes, and those modes
restore the complete source term rather than an independent constraint.
This does not exclude a further argument using the enlarged compiler.

## 6. A contracting two-function recursion for the full value and derivative

Let mu_U,mu_V be the bounded measures with transforms U,V. Their masses
are1/3, and their coefficients are integral. For z in2 Z_2 define

    F_v(s,z)=integral ((1+zu)^2)^s d mu_v(u),  v=U,V.

The integrands use a unit square, so they are analytic in s on Z_2. Their
z expansions converge uniformly on2 Z_2; arbitrary s derivatives may be
taken under the bounded integral. Put a(s,z)=((1+z)^2)^s and
z*=2z/(1+z). The exact spatial identities in section1 give

    F_U(s,z)=F_U(s,2z)+F_V(s,2z)-a(s,z)F_U(s,z*),
    F_V(s,z)=-F_V(s,2z)+a(s,z)[F_U(s,z*)+F_V(s,z*)].     (6.1)

Both new z arguments gain one dyadic valuation. The joint value/slope
system follows by differentiation, retaining

    partial_s a=log((1+z)^2) a.

The initial odd section of R and the next section of S give the exact
dictionary at the two scales in the active obstruction:

    b(s)=2F_U(s,4)+4F_V(s,4)
        +9^s[4F_U(s,4/3)+2F_V(s,4/3)].                 (6.2)

Its derivative retains the additional log9 times the second bracket.
Thus the full Euler value and slope genuinely admit a two-function
contracting-argument recursion, with exact fixed initial masses. This
does not require summing an unproved interpolated binomial series.

## 7. Actual cutoff modes cancel the proposed strict contraction

The enlarged compiler has a specific obstruction to a strict contraction
for the simultaneous-zero equations. For a positive integer k, the
meromorphic state t^k has

    C_0(t^k)=2^(-k)t^k,     C_1(t^k)=0.

Its moment functional is kth differentiation at u=0. Therefore its
Mellin moment and its exponent derivative are

    H_k(s,z)=(2s)_(k) z^k,
    partial_s H_k(s,z)=partial_s[(2s)_(k)] z^k.

Both satisfy exactly

    2^(-k)H_k(s,2z)=H_k(s,z),
    2^(-k)partial_s H_k(s,2z)=partial_s H_k(s,z).       (7.1)

The factor gained from contracting z is canceled by the section weight.
On any normed function space containing this nonzero mode, a strict
contraction factor less than1 for this operator is impossible: (7.1)
would say ||H_k||<=c||H_k|| with c<1.

These modes occur in the actual prefix. For r=3, the depth4 residue9
section is exactly

    C_(16,9) F_3 =32/(3t^2)-1/2+(9/640)t^2.           (7.2)

For every r>=3 the three displayed coefficients persist, with additional
higher even powers of t. The coefficients are the prescribed Bernoulli
ones: beta_0=1,beta_1=-1/3,beta_2=1/15. Thus the missing strictness is
already present in a concrete occupied Euler cutoff state. A more
restrictive arithmetic invariant may still succeed, but generic strict
contractivity of the enlarged value/slope recursion does not.

## 8. The exact two-packet contact model survives all these radix identities

The base proved that A(y) and J(y)=P_1(y)A(y-1)=(9^y-1)/8 have a unit
value/derivative determinant at every a in Z_2. It also proved

    Ecal(s)-S_r(s)=P_r(s) Hbar_r(s-r),
    Hbar_r,Hbar_r' in2^(3r) Z_2<s>.

Consequently unique d0,d1 in2^(3r) Z_2 can be chosen so that

    Q(y)=Hbar_r(y)-d0 A(y)-d1 J(y),
    Q(a)=Q'(a)=0.

Append the two corresponding free packets to the unchanged actual prefix:

    S_tilde=S_r+d0 P_r A(s-r)+d1 P_(r+1)A(s-r-1).

It has an exact repeated residual zero at s=r+a whenever P_r(r+a)!=0,
and retains all forced lower zeros. Its regularized prefix retains exactly
the inherited range v_2(C_tilde^(j)(s))=3j+2 for every s in Z_2 and
0<=j<r. No assertion is made for j>=r. In the meromorphic compiler this changes only the two
initial coefficients at k=2r-2 and k=2r. These are nonnegative for r>=1.
Thus it preserves every pole coefficient in section4, B_8 and B_8', the
six-state full Euler measure, and both recursions (6.1)-(6.2).

For a named check, r=2,a=3 gives, modulo2^32,

    d0=1952704,   d1=2996829184.

Reconstruction from complete source-polynomial data at32 bits gives both
quotient residual value and derivative equal to0 modulo2^32. The eight
spatial principal parts are independently unchanged under this deformation.
The exact existence statement follows from the unit determinant, not from
the finite zero congruences.

This model uses free dyadic coefficients in those two positions. It is not
an actual Euler counterexample. It pinpoints the input that the radix
recursions have not supplied: an additional property of the prescribed
next Bernoulli coefficients. The compiler and its source correction alone
cannot imply simultaneous-zero exclusion, because this model satisfies
them all. No universal impossibility claim about radix arguments is made.

## 9. Evidence scope

check_cartier_mask.py uses standard-library exact rational arithmetic.
It checks eight rational section identities; the six recurrent states;
254 residue masses through depth7 against independent polynomial
inversion in Q[y]/(y^(2^k)-1); increasing Taylor-kernel ranks1 through6;
and 95 exact moment reconstructions for r in{1,2,3,5,9}, degrees0 through18.
It additionally checks81 Mellin identities for integer s=0,...,8 at four
rational z arguments, and independently rebuilds the named32-bit two-jet
contact before checking invariance of all eight principal parts.
These are finite checks supporting the formulas. Sections1-8 contain the
uniform proofs and their restrictions. No Euler stationary nonvanishing
or universal simplicity result follows from the finite checks.

The current run is certified_run_final. The earlier certified_run checked
only sections1-5; its input script hash is now superseded. It remains a
development record and is not current-source evidence.
