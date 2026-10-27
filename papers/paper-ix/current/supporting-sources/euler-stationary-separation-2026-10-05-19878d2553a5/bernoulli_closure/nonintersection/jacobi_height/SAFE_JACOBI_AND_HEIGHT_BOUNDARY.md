# A safe shifted Jacobi model and the remaining arithmetic separation

Date: 2026-10-05. This extends the reviewed `BERNOULLI_HANKEL_SEPARATION.md`; it does not change that frozen proof. The target is still the actual stationary value `Phi_r(2^(2r−25))`, not merely a moment determinant.

## 1. What the new determinant theorem gives beyond coefficient fitting

Fix an ordinary r>=0 and put

    L_r(U^q)=D(r+q),   D(z)=sum_(h>=0)2^h B_h binom(2z,h).

The reviewed theorem constructs monic orthogonal polynomials P_n for the unshifted functional, normalized by

    c_n=4^n(n!)²,  e_n=P_n/c_n.

The e_n have dyadic unit norms, multiplication by U is an integral bounded tridiagonal operator J, and J=I mod4. For the shifted functional L_r the Gram matrix of this same basis is a diagonal unit matrix modulo4. Finite Gram–Schmidt therefore produces a unique orthogonal basis

    e_n^(r)=e_n+sum_(i<n)t_(n,i)e_i,
    t_(n,i) in4Z₂.                                      (1.1)

Every norm of e_n^(r) is a dyadic unit. The triangular change of basis and its inverse have integral coefficients and finite columns, so they extend to bounded mutually inverse maps of the c₀ coefficient lattice. Thus multiplication by U in this basis, denoted J_r, is integral and J_r=I mod4. Since multiplication is symmetric and preserves polynomial degree up to one, J_r is tridiagonal.

Write P_n^(r)=c_n e_n^(r). These are monic rational polynomials when r is ordinary. Their recurrence is

    U P_n^(r)=P_(n+1)^(r)+b_n^(r) P_n^(r)+a_n^(r)P_(n−1)^(r).

The shifted determinant theorem gives

    b_n^(r)=1 (mod4),
    v₂(a_n^(r))=4+4v₂(n), n>=1.                        (1.2)

In the unit-norm basis the upward coefficient is exactly 4(n+1)²; the downward coefficient at n is a_n^(r)/(4n²). Both are integral and divisible by4.

All quantities here come from the actual rational moments D(r),...,D(r+2n+1), through finite rational Gram–Schmidt. This is not a freely chosen recurrence.

## 2. A uniform error theorem at every subsequent packet index

Let J_(r,m) be the leading m-by-m truncation of J_r, m>=1, and define

    d_(r,q)=D(r+q)/D(r),
    d_(r,q)^[m]=(J_(r,m)^q)_(0,0), q>=0.

Both are integral units. For the model this follows from J_(r,m)=I mod4. We have

    d_(r,q)^[m]=d_(r,q)                   for q<2m,

    v₂(d_(r,q)−d_(r,q)^[m])>=h_m
      :=4m+4v₂(m!)                       for every q>=0. (2.1)

At q=2m the error has valuation exactly h_m.

Proof: compute a matrix-power entry as a finite sum over tridiagonal walks starting and ending at index0. A walk distinguished by truncation must visit index m. It therefore crosses every edge 0↔1,...,m−1↔m in both directions. The product of those paired edge weights is

    a_1^(r)...a_m^(r),

whose valuation is h_m by (1.2). All extra weights are integral. Such a walk has length at least2m. At length exactly2m there is only the direct ascending and descending walk, so the bound is exact. This proves (2.1), uniformly in q, with all moments retained.

This is stronger than matching a finite prefix and hoping the subsequent recurrence remains stable. The entire future moment sequence is approximated to h_m bits, and the model moments stay units.

## 3. Reinserting the exact factorial and source factors

Now let r be an admitted ordinary terminal-161 index, so mu_r=−154. Put

    R_(r,q)=2^154 * 2^(5q) * (2r+2q−1)/(2r−1)
                  / product_(h=1)^(2q)(2r+h).

This is the precise depleted packet scalar with its moment ratio removed. Its valuation is

    v₂(R_(r,q))=154+lambda_r(q)>=0,
    lambda_r(q)=3q+s₂(r+q)−s₂(r).                       (3.1)

The depleted normalized deep-chart function is

    Khat_r(Z)=2^−178 sum_(q>=0) R_(r,q)d_(r,q)
                             P_q(x)A(x−q),
    x=10202+2^15 Z.                                    (3.2)

Define Khat_r^[m] by replacing only d_(r,q) with the Jacobi model d_(r,q)^[m]. The rising factorial factors, falling source packets, source A, and ordinary index r are unchanged.

The model packet series converges restricted analytically: (3.1) tends to infinity with q, while every d^[m] is integral. Each model packet has exactly the original scalar valuation because d^[m] is a unit. In particular no unsafe denominator slope has been introduced by replacing the shifted Bernoulli sequence with a rational recurrence.

Equations (2.1) and (3.1) give the full coefficientwise bound

    Khat_r^[m]−Khat_r in2^(h_m−178) Z₂<Z>.              (3.3)

Every packet, including the infinite tail, is included in this bound. Matching the first2m packets is not the sole justification for it.

Write L=h_m−178 and assume L>=9. Differentiation in the restricted algebra is bounded and division by2 loses at most one bit, so

    (Khat_r^[m])'/2−Khat_r'/2 in2^(L−1) Z₂<Z>.         (3.4)

Both half derivatives remain dyadic isometries in the inherited quadratic chart. Let c_m,c be their unique critical points. Then

    v₂(c_m−c)>=L−1,
    v₂(Khat_r^[m](c_m)−Khat_r(c))>=L.                  (3.5)

The first inequality follows by evaluating the model half derivative at c and using its inverse isometry. For the second, the direct function error has valuation at least L, while the displacement of a stationary value has valuation at least2L−2. No critical point is assumed rational or algebraic over Q.

Thus a finite Jacobi model of dimension m provides a certified critical-value approximation through

    L=8m−4s₂(m)−178

bits, with exact prescribed Bernoulli input. This improves convergence control. It does not yet give a nonzero critical value.

## 4. What this would need to prove actual nonintersection

Let E=2r−25. The inherited independent-undepletion theorem implies that the actual stationary value and Khat_r(c)=Phi_r(0) differ by an element of exact valuation E.

If for some model size m one proves

    v₂(Khat_r^[m](c_m))<min(L,E),                      (4.1)

then (3.5) proves the same valuation for Phi_r(0), and the actual undepletion cannot cancel it. This is a sound sufficient test with all derivative and tail losses recorded.

No uniform inequality (4.1) is established here. In particular, a zero model residue through L bits proves only agreement with zero to that precision. The uniform model error does not force the model stationary value outside the error ball.

## 5. Why the orthogonal conditioning does not remove the height deficit

There are two different variables. The moment Hankel theorem and J_r act in U. The critical equation is differentiated in Z. Passing to the orthogonal U basis does not lower the degree in Z of an existing rational polynomial approximation p_P(Z), and it does not change the reduced rational value p_P(d_P) at a fixed integer lift d_P.

The inherited complete construction for either actual or depleted packets uses

    Q=ceil((P+s₂(r)+24)/3),
    M=ceil((P+179)/2),  N=P+178,

and gives a rational polynomial p_P of degree at most2Q+M+N satisfying

    p_P−Khat_r in2^(P+1)Z₂<Z>.

If d_P is the least critical lift through ceil(P/2) bits, stationarity gives

    p_P(d_P)=Phi_r(0) (mod2^P).

Writing p_P=C^−1 sum_(j=0)^d a_j Z^j, A=max|a_j|, the available direct bound is

    log₂ H(p_P(d_P))
      <=max(log₂|C|, log₂ A+log₂(d+1)+d ceil(P/2)).    (5.1)

The last term remains quadratic in P. The new U-basis conditioning supplies a dyadic denominator bound for moment systems; it supplies no cancellation of the archimedean height in (5.1). Applying it to the same p_P is only a different expression for the same rational number.

Using a rational resultant instead of an integer critical lift does not itself fix this. A Sylvester determinant of two degree-O(P) polynomials has a direct height estimate proportional to degree times coefficient height. The coefficient height includes the actual Bernoulli ratios and source approximation denominators. The Hankel theorem does not identify that Sylvester matrix with its controlled moment Gram matrix. It also does not prove that the resultant is nonzero, or isolate the unique integral critical factor over Q.

The new Jacobi model is finite dimensional in U, but its source transform remains an infinite analytic function of Z. Its critical value is not thereby rational or algebraic of a proved bounded height. Rationality of J_(r,m) is insufficient for that inference.

## 6. An actual-coefficient control: unit moment norm can have excessive height

The failure of the proposed inference from dyadic unit conditioning to small rational height already appears in the one-by-one actual depleted moment matrix [D(r)]. Its determinant is a dyadic unit, but

    H(D(r))>2^(2r) for every ordinary r>=40.             (6.1)

Indeed DLMF25.6.2 gives

    |D(r)|=2(1−2/4^r)(2r)! zeta(2r)/pi^(2r)
           >(2r)!/pi^(2r)>(r/pi²)^r.

Since pi²<10 and r>=40, the last expression exceeds4^r. Reduced rational height is at least the absolute value, proving (6.1). The authoritative formula was checked at https://dlmf.nist.gov/25.6.E2 on2026-10-05; the proof here uses only this Bernoulli evaluation and elementary inequalities.

For instance exact rational arithmetic gives the following floor(log₂ H(D(r))) values:

| r | floor(log₂ H(D(r))) | 2r−25 |
|---|---:|---:|
|16|73|7|
|32|199|39|
|64|513|103|
|128|1278|231|

This is an actual Bernoulli control, not a fabricated family. It disproves the inference that an integral unit inverse or unit Gram norm gives a rational height below the undepletion scale. It does not prove that specially normalized critical expressions cannot have large exact height cancellations.

## 7. Exact remaining arithmetic input

The Jacobi construction has now supplied the missing uniform convergence and all-tail error control for a natural shifted moment model. To turn it into stationary nonintersection, one still needs either:

1. A nonzero arithmetic expression for the model critical value, with a proved valuation bound strictly smaller than L and E; or
2. A rational/algebraic approximation to that critical scalar whose *reduced* height is strictly below its certified approximation precision, together with a proof that the approximant is nonzero; or
3. A proved identity transporting actual double contact to a singular principal Gram or Schur block covered by the Hankel theorem.

None follows from moment-system conditioning alone. The current theorem resolves a concrete convergence obstacle and quantifies the resulting critical approximation; the strict value-versus-error inequality, and therefore the actual Euler nonintersection target, remains open.
