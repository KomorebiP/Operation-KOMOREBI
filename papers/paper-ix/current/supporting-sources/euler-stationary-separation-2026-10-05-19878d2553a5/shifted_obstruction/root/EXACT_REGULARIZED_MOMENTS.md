# Exact arithmetic of the regularized Euler moments

Base checkpoint: Euler-arithmetic-nonvanishing-20261005.
Base archive SHA256: 15e1f9114380e180adcf4f7306d894100d6fd499929ee7a841d8629bd27e7464.

Let Ecal be the already constructed restricted analytic interpolation of the
signed Euler numbers, Ecal(N)=E_(2N), and put

    b(s)=(1+3*9^s) Ecal(s),       s in Z_2.

Write Delta b(s)=b(s+1)-b(s). The following exact statements hold:

    v_2(Delta^k b(s))=3k+2,       k>=0, s in Z_2;             (1)
    v_2(b^(j)(s))=3j+2,           j>=0, s in Z_2.             (2)

These are statements about the full regularized interpolation, not the
prescribed residual. The latter distinction is necessary: the actual finite
prefix does not satisfy the same bounded-measure estimate.

## 1. Elementary construction of a bounded measure

The exponential generating function of the even moments b(N), with odd
moments zero, is

    sech t+3 sech(3t)=R(exp t),
    R(y)=2y(y^2+1)/(y^4-y^2+1).                              (3)

For n>=1 reduce R in the finite group ring
Z_2[y]/(y^(2^n)-1). Its denominator is invertible: modulo2 this ring is
F_2[y]/((y-1)^(2^n)), and the denominator takes the value1 at y=1.
The inverse therefore lifts by the convergent geometric/Newton procedure.
The resulting coefficients are all in2 Z_2, uniformly in n, and they are
compatible under reduction from n+1 to n. Interpret the coefficient of y^a
as the mass mu(a+2^n Z_2). Compatibility gives a bounded Z_2-valued measure
mu divisible by2. Equivalently its Amice power series is R(1+T).

The denominator is even in y and the numerator odd, so only odd residue
classes have nonzero mass. Also R(y^-1)=R(y), hence mu is invariant under
u -> -u. On odd units let

    w=(u^2-1)/8 in Z_2.

Push mu forward by this map to a measure nu on Z_2. Partition odd units
into u=1 and3 modulo4. Negation interchanges these two sets and preserves w.
Every mass of nu is twice a mass obtained by restricting mu to u=1 mod4.
Since mu is divisible by2, nu is divisible by4. Write nu=4 rho, where rho
is an integral bounded measure.

The moment identity from (3) now gives, for ordinary N>=0,

    b(N)=4 integral (1+8w)^N d rho(w).

Both sides extend to restricted analytic functions of s in Z_2. For the
right side use its binomial expansion: coefficient valuations are bounded
below by 3k-v_2(k!), which tends to infinity. Density of the ordinary
nonnegative integers and continuity give

    b(s)=4 integral (1+8w)^s d rho(w).                       (4)

This construction uses no unregularized bounded Euler measure.

## 2. The needed parity is an exact finite identity

Modulo y^16-1, direct polynomial multiplication verifies

    R(y)=2(y+y^3-y^7-y^9+y^13+y^15).                         (5)

The total mass of mu is R(1)=4, so rho(Z_2)=1.
For odd u modulo16, w is odd exactly in the classes3,5,11,13.
Equation (5) gives total mu mass4 to those classes, so

    rho(2 Z_2)=0,      rho(1+2 Z_2)=1.                      (6)

These are exact masses, not merely congruences. Consequently the integral
of w^k against rho is odd for every k>=1; for k=0 its value is1.

## 3. Exact differences and derivatives

Applying Delta^k under the bounded integral in (4) gives

    Delta^k b(s)=4*8^k integral w^k (1+8w)^s d rho(w).

The integrand reduces modulo2 to w^k, or to1 when k=0. Equations (6)
therefore make the remaining integral odd, proving (1) uniformly in s.

The uniformly convergent exponential expansion permits arbitrary ordinary
s derivatives under the integral:

    b^(j)(s)=4*8^j integral L(w)^j (1+8w)^s d rho(w),
    L(w)=log(1+8w)/8 in Z_2,       L(w)=w (mod2).

The same parity calculation proves (2). No finite computation or numerical
limit supplies the universal quantifiers in either assertion.

## 4. Exact transfer boundary

For the Euler prefix S_r and residual F_r=Ecal-S_r, let

    C_r(s)=(1+3*9^s) S_r(s),
    B_r(s)=(1+3*9^s) F_r(s)=b(s)-C_r(s).

The factor1+3*9^s has exact valuation2 and never vanishes on Z_2, so it
preserves root multiplicities. A repeated residual zero away from the known
factor P_r(s) is exactly a simultaneous contact

    C_r(s)=b(s),         C_r'(s)=b'(s).                     (7)

In particular (7) requires v_2(C_r(s))=2 and v_2(C_r'(s))=5.
It does not contradict (1)-(2). The finite cutoff cannot be discarded.
The exact countertests and torsion pole in
../moment/SCALE_REFLECTION_AND_PREFIX.md show that C_r and B_r do not
inherit the bounded-measure estimate. Therefore (1)-(2) are a new full
Euler theorem, not a proof of residual simplicity or arithmetic nonvanishing.

A remaining route would need a strict estimate for the order-two prefix
functional in (7), using its actual cutoff and the stationary condition.
The present theorem alone does not provide that estimate.

## 5. Computation scope

check_regularized_moments.py independently checks (3) by rational polynomial
multiplication, (5) in the exact finite group ring, the mass partition in
(6), and ordinary finite differences for s=0,...,4 and k=0,...,20 using an
integer Euler recurrence. These checks support indexing and normalization;
the proof above establishes the all-s and all-order assertions.

A preliminary attempt to use SymPy for finite group-ring inversion could not
execute because SymPy is absent. No dependency was installed. The final
checker uses Python's standard library and exact integers only.
