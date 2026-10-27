# Threshold-free dyadic higher differences by translated differential flatness

## Exact statement

Let `R=Z_2` and let `H_R` be the Hurwitz-integral subring of `Q_2[[t]]`, consisting of series

`F(t)=sum_{d>=0} f_d t^d/d!` with every `f_d` in `R`.

Let `N=2^a`, where `a>=0`. Suppose `g:Naturals -> R` satisfies

`Delta_1^k g(n) in 2^k R` for every `k,n>=0`.

Pack its exponential generating series

`F(t)=sum_{n>=0} g(n) t^(Nn)/(Nn)!`.

Assume `g(0)` is a unit. Define its exact reciprocal

`H(t)=F(t)^(-1)=sum_{n>=0} C(n) t^(Nn)/(Nn)!`.

Then

`Delta_u^k C(n) in 2^k R` for every `u,k,n>=0`.

This is a genuine reciprocal theorem for the packed Hurwitz product; it does not use pointwise inversion of sequences.

## 1. Basic integrality

The ordinary series inverse exists since `F(0)=g(0)` is a unit. Its factorial-scaled coefficients satisfy the recurrence

`h_0=g(0)^(-1)`,

`h_d=-g(0)^(-1) sum_{i=1}^d binom(d,i) f_i h_(d-i)`.

Therefore every `h_d` is integral. Since all `f_i` vanish away from degrees divisible by `N`, the recurrence implies that all `h_d` vanish away from degrees divisible by `N` too. Thus `H` has the displayed packed form and belongs to `H_R`.

The derivative `D=d/dt` acts by coefficient shift in this lattice. Every `D^i` preserves `H_R`. Multiplication preserves `H_R` by the binomial product rule.

## 2. Translated flatness

For an integer `lambda`, define

`L_lambda=(D^N-lambda)/2`.

Call `A` lambda-flat if `L_lambda^k A` is in `H_R` for every `k>=0`.

Since `N` is a power of two, every interior binomial coefficient `binom(N,i)` is even. This follows from `(1+X)^N=1+X^N` over `F_2`.

For any integer `lambda,mu`, the exact Leibniz identity is

`L_(lambda+mu)(AB) = (L_lambda A)B + A(L_mu B) + sum_{i=1}^{N-1} c_i (D^i A)(D^(N-i) B)`,

where `c_i=binom(N,i)/2` is an integer.

All differential operators `D^i,L_lambda,L_mu` commute on each factor. Hence this identity can be iterated without untracked correction terms.

Precisely, define the commuting pair operator

`T=L_lambda on first factor + L_mu on second factor + sum c_i D^i on first factor D^(N-i) on second factor`.

Applying multiplication after `T^k` gives exactly `L_(lambda+mu)^k(AB)`.

The multinomial expansion has terms indexed by nonnegative

`a,b,e_1,...,e_(N-1)` with `a+b+sum e_i=k`,

and equals

`sum k!/(a! b! prod e_i!) prod c_i^e_i * (D^alpha L_lambda^a A)(D^beta L_mu^b B)`,

where

`alpha=sum i e_i`, `beta=sum (N-i)e_i`.

Every coefficient in this expansion is an integer. In particular, flatness types add under multiplication.

## 3. The inverse lemma

Suppose `F` is lambda-flat, `F(0)` is a unit, and `H=F^-1` belongs to `H_R` as established above. Then `H` is negative-lambda-flat.

Proof is induction on `k`. The `k=0` claim is ordinary reciprocal integrality. For `k>0`, apply the multinomial formula with `A=F`, `B=H`, and `mu=-lambda`.

Since `FH=1`,

`L_0^k(FH)=(D^N/2)^k 1=0`.

There is exactly one term having `b=k`: it has `a=0` and all `e_i=0`, so it is `F L_(-lambda)^k H`.

Every other term has `b<k`. Its second factor `D^beta L_(-lambda)^b H` is integral by induction and coefficient-shift integrality. Its first factor `D^alpha L_lambda^a F` is integral by the assumed flatness of `F`. The scalar is integral by the multinomial formula. Hence the sum of all other terms is in `H_R`.

Therefore `F L_(-lambda)^k H` is in `H_R`. Multiplying by the integral reciprocal `H` proves `L_(-lambda)^k H` is in `H_R` and completes the induction.

## 4. Apply the lemma to the exact source

For packed `F`, the factorial coefficient of `L_1^k F` at degree `Nn` is

`2^(-k) sum_{i=0}^k (-1)^(k-i) binom(k,i) g(n+i) = Delta_1^k g(n)/2^k`.

At other residue classes the coefficient is zero. The source hypothesis is thus exactly 1-flatness, with no lower bound on `n`.

By the inverse lemma, `H` is minus-1-flat. But

`L_1=L_(-1)-1`.

Consequently `L_1^k H=sum_{b=0}^k binom(k,b)(-1)^(k-b)L_(-1)^b H` is integral.

Its coefficient at degree `Nn` is `Delta_1^k C(n)/2^k`. This proves the all-row, all-order estimate.

For a natural step `u>0`, write the shift identity

`E^u-1=(E-1)(1+E+...+E^(u-1))`.

Both shift operators commute, so the `k`th power of the rightmost integral sum transforms the proved step-one divisibility into `Delta_u^k C(n) in 2^k R`. If `u=0`, positive-order differences vanish, and order zero is ordinary integrality.

## 5. The four actual N=4 kernels

The exact source coefficients are

`g_0(n)=1`,

`g_1(n)=1/(4n+1)`,

`g_2(n)=1/((4n+1)(2n+1))`,

`g_3(n)=3/((4n+1)(2n+1)(4n+3))`.

Every denominator is odd and every affine factor has even slope. The discrete product formula and induction for pointwise inverses establish the source hypothesis uniformly in `k,n`. These source lemmas are already present in the checked completion.

Thus, for every `j=0,1,2,3` and all naturals `n,k,u`,

`v_2(Delta_u^k C_(4,j)(n))>=k`,

with zero differences interpreted as having infinite valuation.

For the original unnormalized coefficients `E_(4n)^(4,j)=j! C_(4,j)(n)`, the bound is at least `k+v_2(j!)`.

## Claim boundary

This removes the sufficient starting row for the solved dyadic Nishibuchi family. It does not prove the unrelated universal simplicity claim for recent Euler residuals. The proof is mathematical; no Lean compilation is claimed by this file.

## 6. All dyadic section orders, beyond N=4

For `N=2^a` and every `0<=j<N`, the prescribed kernel is

`g_(N,j)(n)=j!(Nn)!/(Nn+j)!=prod_{i=1}^j (1+(N/i)n)^(-1)`.

The empty product covers `j=0`. For each positive `i<N`, `v_2(i)<a`, so `N/i` lies in `2Z_2`. Thus each affine factor is a unit-valued source satisfying P2, and the exact discrete pointwise inverse/product lemmas imply the same for the full actual kernel. Consequently the threshold-free theorem holds for every dyadic section order `N=1,2,4,8,...`, every address, every row, every difference order, and every natural step.

This is a larger parameter family than the original external conjecture's dyadic branch.

## 7. Step-sensitive higher-difference bound

The proved global P2 property strengthens to

`Delta_u^k C(n) in 2^(k(1+v_2(u))) Z_2`, for every positive natural `u` and every `k,n>=0`.

Indeed, write `s=v_2(u)` and `Delta=E-1`. For `1<=m<=u`,

`v_2(binomial(u,m)) >= s-v_2(m)`

by `m binomial(u,m)=u binomial(u-1,m-1)`. Since `m-v_2(m)>=1`, all coefficients of

`P_u(W)=(1+2W)^u-1`

are divisible by `2^(s+1)`. Therefore all coefficients of `P_u(W)^k` are divisible by `2^(k(s+1))`.

Write `((1+X)^u-1)^k=sum_m b_m X^m`. The preceding statement says that `2^m b_m` is divisible by `2^(k(s+1))`. The global difference estimate says `Delta^m C(n)=2^m z_m` with integral `z_m`. Thus

`Delta_u^k C(n)=sum_m b_m Delta^m C(n)=sum_m 2^m b_m z_m`

has the claimed divisibility.

For `u=0`, positive-order differences vanish. For `k=0`, this reduces to ordinary integrality.

For original unnormalized coefficients, multiply by `j!` to obtain

`v_2(Delta_u^k E_(Nn)^(N,j)) >= k(1+v_2(u))+v_2(j!)`.

## 8. Threshold-free period consequence

Let `r>v_2(j!)`, and choose the positive row displacement

`u=2^(max(0,r-v_2(j!)-1))`.

Then the first-difference bound proves, for every `n>=0`,

`E_(N(n+u))^(N,j) congruent E_(Nn)^(N,j) modulo 2^r`.

If `r<=v_2(j!)`, all coefficients themselves are zero modulo `2^r`. These are sufficient periods; no minimality is asserted for the general dyadic family.
