# Carry-adapted actual Bernoulli models and exact stationary-error laws

Status: new convergent actual-coefficient models, an actual finite-carry Hankel
theorem, and exact finite-rank critical-error laws. The universal actual Euler
critical nonvanishing theorem remains open.

Throughout, r=(17659+2^18 T)2^640-161 is an admitted ordinary positive index
with true terminal161. Put m=r+161=B2^640, with B odd, and

    a_n=4^n B_(2n)/(2n)!,
    t_q=a_(m+q)/a_m,  t_0=1.

The Bernoulli numbers and all rational coefficients in this note are the actual
ordinary-index ones. No all-precision interpolation of T is assumed.

## 1. Actual Hankel control throughout the first carry range

For 1<=q<2^640, no binary carry crosses the zero block in m, so exactly

    v2(t_q)=s2(m+q)-s2(m)=s2(q).                          (1)

Let f_n in F_2 be1 exactly when n is a positive power of2. Then
t_q/2=f_q mod2 in this range. Define

    A_d=det[f_(i+j+1)]_(0<=i,j<d),
    B_d=det[f_(i+j+2)]_(0<=i,j<d), A_0=B_0=1.

Both determinants are1 for every d. Here is a proof. Since f_(2j)=f_j for
j>=1 and the only odd positive index with f_n=1 is n=1, even/odd ordering
of rows and columns gives

    A_(2k)=A_k^2,
    A_(2k+1)=B_k^2,
    B_d=A_ceil(d/2) B_floor(d/2).                          (2)

For the first identity the matrix is [[E_00,A_k],[A_k^T,0]], where E_00 has
only its top-left entry1. For odd size that sole same-parity entry is forced
in every nonzero determinant term; removing its row and column leaves the
B_k cross-blocks. The B matrix is block diagonal after parity ordering.
Together with A_1=B_1=1 these recurrences prove the assertion by induction.

For H_d=[t_(i+j)]_(0<=i,j<d), divide rows1,...,d-1 by2. The resulting matrix
U_d is integral; modulo2 its first row is(1,0,...), and its complementary
minor is B_(d-1). Thus

    v2(det H_d)=d-1,
    U_d is unimodular,
    H_d^(-1) has all entries in(1/2) Z_2.                 (3)

For the Padé construction below this is valid for every actual

    1<=d<=2^639.                                         (4)

It uses actual moments only through2d-1<2^640. This is a proof at every rank
in the displayed carry range, not an extrapolation from the ten computations.

The corresponding reset limit has moments h_0=1 and
h_q=(2-4^q)a_q for q>=1, with generating series

    sum h_q w^q=2z coth z-2z coth(2z)=2z/sinh(2z), w=z^2.

The same parity proof applies to its Hankel matrices at every rank without
the finite-carry restriction. This limit is not 2z coth z-1: replacing it
by that expression would omit the Euler depletion factor at positive q.

## 2. Integral rational denominators and the first exact error

Let Q_d(w)=1+q_1 w+...+q_d w^d solve

    t_k+sum_(j=1)^d q_j t_(k-j)=0,  k=d,...,2d-1.

These are rational equations with the actual rational moments t_k. Reversing
columns identifies their matrix with H_d. The right side moments are even;
(3) proves

    every q_j belongs to Z_2.                            (5)

The last coefficient has exact valuation1. Its Cramer numerator is, up to
sign, det[t_(i+j+1)]_(0<=i,j<d). Factor2 from each row; the remaining parity
determinant is A_d=1. That numerator has valuation d, while the denominator
has valuation d-1. Therefore

    v2(q_d)=1.                                           (6)

Define the [d-1/d] rational model R_d=P_d/Q_d, whose coefficients t_q^(d)
agree with t_q for0<=q<2d. They obey the recurrence supplied by Q_d thereafter.
All t_q^(d) are integral, and all positive-index coefficients are even.
The latter follows from the even initial moments and (6): when q=d the only
constant-moment contribution is q_d t_0, which is even; later every previous
coefficient has positive index.

For d<2^639, the first error is the Schur complement

    e_(2d)=t_(2d)-t_(2d)^(d)=det H_(d+1)/det H_d,
    v2(e_(2d))=1.                                       (7)

The strict inequality on d is sharp. At d=2^639 the next moment is at the
carry boundary q=2^640. Since B=17659+2^18 T is3 modulo8, it has exactly two
trailing binary ones, and the actual moment has valuation
s2(B+1)-s2(B)=-1. The model moment is even, so the first error has valuation
-1 there, rather than1. For2d<=q<2^640 all coefficient errors remain even.
This provides both rational existence and a dyadic denominator/error budget.

## 3. Keep the actual lower161 packets

Let gamma_q be the actual normalized packet scalars, so gamma_161 is an odd
unit and every gamma_q is integral by the true-terminal hypothesis. Keep
gamma_q unchanged for q<161. Replace only the terminal tail by

    gamma_(161+t)^(d)=gamma_161 8^t t_t^(d)
                                (2m+2t-1)/(2m-1), t>=0.  (8)

The odd quotient in (8) is a unit. Integrality of t_t^(d) proves that the
resulting packet series converges as a restricted analytic function:

    K_d(Z)=2^-178 sum_q gamma_q^(d) P_q(x) A(x-q),
    x=10202+2^15 Z.                                      (9)

This convergence holds for every actual rank in (4). It is not a claim that
the source transform is a rational function of Z. The kernel tail R_d is
rational in its own variable; (9) remains an analytic source transform.

## 4. Exact uniform errors for ranks1 through10

The following source-chart conclusions are restricted to d=1,...,10. Set

    q0=161+2d,
    p_d=v2(P_q0(10202)),
    E_d=6d+1+p_d-178.

The resulting table is

| d | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| E_d | -8 | -1 | 7 | 14 | 24 | 31 | 39 | 46 | 55 | 62 |

For every admitted T and every Z in Z_2, exactly

    v2(K_d(Z)-K_r(Z))=E_d,
    v2((K_d-K_r)'(Z))=E_d+8.                             (10)

The derivative estimate also holds coefficientwise:

    (K_d-K_r)' in2^(E_d+8) Z_2<Z>.                       (10a)

Here is the full tail argument. By (7), the first changed packet has scalar
valuation6d+1. All later errors before the next carry are even. Factor the
first packet P_q0(x)A(x-q0) and its scalar from this near part of the error.
The remaining multiplier is1+8 R(x), with R integral restricted. This follows
from P_(q0+h)=P_q0 P_h(x-q0), the unit inverse of A, and the factor8^h.
The near sum is finite at the next carry but may contain an enormous number
of terms; its integrality and convergence bounds are uniform.

The remote actual tail q>=161+2^640 does not satisfy the same unscaled moment
parity statement. It is controlled separately. Every actual gamma_q is integral,
as is every model gamma_q^(d). On the local chart, at least floor(q/2) factors
x-i have both even constant and even linear coefficients. Hence

    P_q(10202+2^15 Z) in2^floor(q/2) Z_2<Z>.

The remote error, after normalization and division by the first packet, has
an enormous local Gauss valuation, well above18. Its Z derivative preserves
that bound. No global-in-x divisibility is inferred from this local statement.

For q0<=181 the largest valuation among x-i, 0<=i<q0, on the chart is7,
attained uniquely at i=90. Every other x-i has valuation at most6, and all
2x-2i-1 factors are odd. Thus P_q0 has fixed value valuation p_d, and

    v2(d/dx log P_q0(x))=-7.

The logarithmic derivative of A(x-q0) has valuation at least1, and that of
the near multiplier1+8R(x) has valuation at least3. Converting to Z adds15.
The remote local correction has derivative valuation at least18, so it cannot
cancel the unique contribution of valuation8. This proves both assertions
in (10), with all local/global derivative bounds distinguished. More precisely,
after its constant valuation is removed, each local linear factor of the
first packet has Z coefficient divisible by2^8; its logarithmic derivative
is therefore coefficientwise in2^8 Z_2<Z>. The A factor and the near and
remote corrections have the stronger coefficientwise derivative bounds
just proved. Multiplication by the normalized unit factors proves (10a).

The integer valuations in the table can also be calculated as
p_d=93+v2((70+2d)!), hence E_d=6d+v2((70+2d)!)-84.
These formulas are not extended beyond the displayed small-rank range.

## 5. Stationary points and critical values move with the approximation

The actual half derivative K_r'/2 is an isometry and its critical point c is
unique. Its exact stationary expansion has a unit quadratic coefficient.
For rank1, (10) gives an odd derivative error, while the actual derivative is
even. Therefore K_1' is odd everywhere and K_1 has no stationary point on Z_2.

For d=2,...,10, the half-derivative perturbation has exact valuation E_d+7>=6
and, by (10a), all its coefficients are divisible by2^(E_d+7).
Thus the model half derivative remains an isometry. It has a unique critical
point c_d, and comparison of its zero equation with the actual one gives

    v2(c_d-c)=E_d+7.                                     (11)

Write Phi_d=K_d(c_d), Phi=K_r(c). Then

    Phi_d-Phi=(K_d-K_r)(c_d)+K_r(c_d)-K_r(c).

The two terms have valuations E_d and2E_d+14 respectively. The second is
strictly higher for every d>=2 in the table. Consequently

    v2(Phi_d-Phi)=E_d.                                   (12)

This is an exact error law for the moving stationary point. It does not
freeze the critical center.

Equation (12) yields an actual nonvanishing certificate whenever

    v2(Phi_d) != E_d.                                    (13)

If the model valuation is below E_d, the actual valuation equals the model's.
If it is above E_d, the actual valuation equals E_d. Equality is the unresolved
cancellation case. An exact actual zero would necessarily give
v2(Phi_d)=E_d at every rank in this table, consistently with nonzero Hankel
determinants and nonzero model critical values.

## 6. Bounded execution on the two previously fixed indices

The checker reconstructs complete actual local coefficients at256 global bits
and compares them with the inherited94-bit local records after reduction.
It then constructs actual moment matrices with384 bits and exact integer
Bareiss/Cramer arithmetic. For ranks1..10 the determinant valuations are d-1,
all denominator coefficients are integral, and the last has valuation1.
Matching of all2d coefficients, the next Hankel determinant, and the exact
first moment error are checked. The source and infinite packet tails
are capped using proved coefficient bounds, rather than sampling values.

| d | Source error E_d; critical error for d>=2 | Model valuation, T=0 | Model valuation, T=718787533 |
|---|---:|---:|---:|
| 1 | -8 | no stationary point | no stationary point |
| 2 | -1 | -1 | -1 |
| 3 | 7 | 0 | 7 |
| 4 | 14 | 0 | 14 |
| 5 | 24 | 0 | 24 |
| 6 | 31 | 0 | 30 |
| 7 | 39 | 0 | 30 |
| 8 | 46 | 0 | 30 |
| 9 | 55 | 0 | 30 |
| 10 | 62 | 0 | 30 |

Rank3 certifies the previously known T=0 nonvanishing with a seven-bit margin.
Rank6 certifies the previously known T=718787533 value of valuation30 with an
error of valuation31. These are strict arithmetic margins obtained from the
new approximants, not new Euler indices or newly discovered valuations.

For the second index, ranks3,4,5 have model valuation exactly equal to error.
They are nonzero, but do not certify the actual value. This supplies a concrete
demonstration of the remaining logical issue: until the approximation resolves
the actual cancellation, the model value can consist entirely of approximation
error. The all-rank Hankel theorem guarantees a well-defined convergent model
through the first carry range; it does not bound the actual critical value.

No new multiplier digits or Lean compilation were used. The requested universal
arithmetic separation is still unproved. The remaining required statement is
that every actual admitted index eventually admits a model with a strict
critical-value/error inequality, or another arithmetic argument excluding
the equality case. Nonzero moment determinants alone do not imply that.
