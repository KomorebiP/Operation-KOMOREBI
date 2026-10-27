# Euler interpolation, moment kernels, and the residual obstruction

Base checkpoint: `Euler-coupled-stationarity-20261005`.
Scope: actual ordinary positive indices r. This route addresses nonvanishing
of stationary critical values. It does not assert the universal simplicity
theorem and does not change any inherited finite certificate.

## 1. Exact source-free Euler interpolation

Keep the signed convention sech z = sum E_n z^n/n!, and set beta_0=1. Put

    Ecal(s) = sum_(m>=0) 8^m beta_m P_m(s) A(s-m).

The m-th term for m>=1 has coefficient valuation at least
3m+s2(m)-1, because P_m and A(s-m) are integral restricted series.
Consequently Ecal belongs to Z_2<s> and Ecal(N)=E_(2N) for every ordinary
N>=0 by the original Euler reconstruction identity.

Define the Volkenborn functional on the analytic functions used here by
I(a^k)=B_k and termwise convergence. Equivalently it is the limit of
2^-h sum_(a=0)^(2^h-1) f(a). The functions below have coefficient decay
fast enough that this limit and all displayed termwise operations exist.
The bound v2(B_k)>=-1 suffices for the power-series constructions.

There is the exact identity, for all s in Z_2,

    Ecal(s) = -I((1+4a)^(2s+1))/(2s+1).                    (1)

Proof at ordinary N: the integral is
4^(2N+1) B_(2N+1)(1/4). Its negative divided by 2N+1 has exponential
generating function sech z. This can be checked without a special-value
theorem: for all k>=0 define M_k=-I((1+4a)^(k+1))/(k+1). Then

    sum M_k z^k/k! = [1 - 4z e^z/(e^(4z)-1)]/z.

Its even part is

    -2(e^z-e^(3z))/(e^(4z)-1) = sech z.

Thus M_(2N)=E_(2N). Both sides of (1) are restricted analytic in s,
and the nonnegative ordinary integers are dense in Z_2.

Expanding (1), using B_1=-1/2 and B_(2m+1)=0 for m>=1, gives a
source-free Newton expansion involving the actual rational beta_m:

    Ecal(s) = 2 - 1/(2s+1)
              + sum_(m>=1) [4^m beta_m/(2m-1)]
                  (2s)^underlined(2m-1).                  (2)

The m-th summand has coefficient valuation at least 2m+s2(m)-1,
which tends to infinity. In particular this is an exact convergent identity,
not an asymptotic expansion and not an interpolation in the index r.

## 2. Uniform arithmetic control of the full interpolation

All terms m>=2 in (2) are divisible by16 coefficientwise. The m=1 term
is -8s/3. Expanding the rational term therefore gives

    Ecal(s) = 1 + 10s + 12s^2 + 8s^3 (mod16),              (3)
    Ecal'(s) = 2 (mod8),
    Ecal''(s) = 8 (mod16).

Thus, uniformly in s,

    v2(Ecal)=0,   v2(Ecal')=1,   v2(Ecal'')=3,
    v2(Ecal Ecal'' - (Ecal')^2)=2.                        (4)

Moreover (Ecal-1)/2 is a restricted series with coefficientwise reduction s.
The ordinary divided-difference and Hensel argument shows that Ecal is a
bijection Z_2 -> 1+2Z_2 satisfying

    v2(Ecal(s)-Ecal(t)) = 1+v2(s-t), s!=t.                 (5)

These identities control the full Euler interpolation. They do not yet
control the subtraction defining the residual: its finite prefix has the
same leading derivatives, so the unit in (4) can disappear after subtraction.

## 3. A finite rational-polynomial reduction of the actual residual

Set D(s)=(s+1)(2s+1), and let

    S_r(s)=sum_(0<=m<r) 8^m beta_m P_m(s) A(s-m),
    Q_r(s)=1+D(s) sum_(1<=m<r) 8^m beta_m 9^-m P_(m-1)(s),
    R_r(s)=1+D(s) sum_(1<=m<r) 8^m beta_m P_(m-1)(s).

Q_r and R_r are finite polynomials in Q[s], of degree at most 2r-2.
The exact elementary cancellation

    P_m(s) A(s-m) = P_(m-1)(s)(9^(s-m+1)-1)/8, m>=1

gives

    8D(s) S_r(s) = 9^(s+1) Q_r(s)-R_r(s).                 (6)

Splitting the convergent Euler series at r gives, with the actual mu_r,

    Ecal(s)-S_r(s)
       = 8^r beta_r 2^mu_r P_r(s) G_r(s-r).                (7)

Equivalently,

    8D Ecal - 9^(s+1) Q_r + R_r
       = 8^(r+1) beta_r 2^mu_r D P_r G_r(s-r).             (8)

This replaces two infinite source-elimination sums by one universal Euler
interpolation and two finite rational polynomials. It does not make Ecal,
its derivative, or its values at unknown dyadic arguments algebraic.

For s with D(s)P_r(s)!=0, a double root is equivalent to vanishing of
the left side of (8) and its first derivative. Eliminating 9^(s+1) yields

    Q_r(8D Ecal' + 8D' Ecal + R_r')
      -(Q_r'+log(9) Q_r)(8D Ecal+R_r) = 0.                (9)

This is a necessary equation. Reversing the elimination requires the
original value equation and Q_r!=0. No unproved denominator-unit claim
is made. This finite Wronskian still contains Ecal and Ecal'; (4) does not
show that (9) is nonzero.

## 4. The exact two-moment condition

Write n=2s+1 and

    J_j(s)=I((1+4a)^n log(1+4a)^j), j=0,1,2.

Coefficientwise convergence permits differentiation, giving

    J_j'=2J_(j+1), j=0,1,
    Ecal=-J_0/n,
    Ecal'=-2(Ecal+J_1)/n,
    Ecal''=-4(Ecal'+J_2)/n.                               (10)

At s with P_r(s)!=0, a repeated Euler residual root is therefore equivalent
to the exact simultaneous moment equations

    J_0(s) = -n S_r(s),
    J_1(s) = -S_r(s) - n S_r'(s)/2.                       (11)

This is the concrete remaining moment nonintersection assertion.

At a forced skeleton point s in {0,...,r-1}, P_r has a simple zero.
One must instead require (Ecal-S_r)'=(Ecal-S_r)''=0 for G_r=G_r'=0;
the value equation is automatic. Thus (11) alone must not be used there.

## 5. Why a bounded-measure or positivity shortcut does not apply

The Volkenborn functional is bounded on the restricted analytic coefficient
norm used above, but it is not a bounded measure on all continuous functions.
Indeed there cannot be a bounded Q_2-valued measure on Z_2 whose even power
moments are E_(2N). If there were one, symmetrize it under t -> -t to make
its odd moments zero. Its Amice transform would have bounded coefficients
and equal, as a formal power series,

    M(T)=sech(log(1+T))=2(1+T)/((1+T)^2+1).               (12)

Bounded coefficients make M convergent at every algebraic T with |T|_2<1.
But alpha=-1+i, with i^2=-1, has v2(alpha)=1/2. Evaluating
((1+T)^2+1)M(T)=2(1+T) at alpha would give 0=2i, a contradiction.

This is a precise obstruction to interpreting the Euler functional as a
bounded positive-type moment measure and then applying a real covariance
inequality to (11). It does not exclude more delicate analytic-distribution
arguments.

## 6. Exact Euler Hankel determinants, and failure of their transfer

Define the rational moment functional L(t^k)=E_k, where odd Euler numbers
are zero. Define monic polynomials p_n by

    sum p_n(t) z^n/n! = (1-z^2)^(-1/2) exp(t atanh z).

Equivalently p_0=1, p_1=t, and

    p_(n+1)=t p_n+n^2 p_(n-1).

The two-variable generating kernel is exactly

    L[(1-z^2)^(-1/2)e^(t atanh z)
      (1-w^2)^(-1/2)e^(t atanh w)] = 1/(1+zw).

This follows from L(e^(tu))=sech u and the hyperbolic addition formula.
Coefficient comparison proves

    L(p_n p_m)=delta_(n,m) (-1)^n (n!)^2.

Since p_(2j) is monic in t^2 of degree j, triangular change of basis gives
the exact nonzero determinant identity

    det(E_(2(i+j)))_(0<=i,j<=d) = product_(j=0)^d ((2j)!)^2. (13)

This is real arithmetic structure in the Euler moment functional. It is
not a proof about the residual G_r. That transfer was tested and fails for
the most direct proposed remainder identification. For r=1,

    Ecal(1)-A(1)=-8/3,   Ecal(2)-A(2)=-16/15,
    L(p_2(t)t^2)=4,      L(p_2(t)t^4)=-56.

The respective ratios are -2/3 and 2/105, so the residual is not a constant
multiple of this orthogonal-polynomial moment remainder.

More generally (6) writes S_r(s)=A(s)+9^s C_r(s)+D_r(s), with finite
rational polynomials C_r,D_r. The ordinary generating function of A(N)
is not rational: A(N) is asymptotic to (9/16)9^N/N^2, incompatible with
the polynomial-times-exponential coefficient form of a rational generating
function. Finite exponential polynomials have rational generating functions.
Therefore S_r(N) is not the moment sequence of a finite atomic or finite
derivative-atomic Gaussian approximation. The ordinary finite Padé/Hankel
remainder theorem has no exact dictionary to our prefix.

## 7. Route outcome

Proved here: the source-free interpolation (2), global arithmetic controls
(3)-(5), finite resummation (7)-(9), exact two-moment criterion (11), bounded
measure obstruction (12), and nonzero Euler Hankel determinant formula (13).

Not proved: exclusion of the simultaneous equations (11) for every ordinary
r, including the surviving terminal-161 chart. The full interpolation has
nonzero logarithmic curvature, but subtracting S_r removes the leading unit.
The finite moment determinant controls orthogonal/Padé remainders, while our
remainder is a different Taylor/deconvolution construction.

A new continuation must either prove nonintersection in (11) for this exact
S_r, or supply an exact remainder identity relating S_r to an appropriate
nondegenerate distribution kernel. Merely invoking positivity, Hankel
nonvanishing, or finite exponential-polynomial zero theorems is insufficient.

No Lean compilation was performed. Finite checks in `check_structure.py`
verify the algebra against independent Euler/Bernoulli recurrences and the
declared finite ranges. The general statements above have separate proofs.
