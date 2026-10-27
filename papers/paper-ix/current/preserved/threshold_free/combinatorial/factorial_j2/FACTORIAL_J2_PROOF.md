# Factorial higher-difference bound for the actual N=4,j=2 reciprocal

## Statement

For the normalized actual packet

C_2(n)=(4n)![t^(4n)] (2! sum_(q>=0) t^(4q)/(4q+2)!)^(-1),

one has, for every n,k>=0 and every positive natural u,

v_2(Delta_u^k C_2(n)) >= k(1+v_2(u))+v_2(k!).

This is stronger than the threshold-free k-flat theorem. The proof uses the actual j=2 factorization and Bernoulli values, not a generic divided-flat inverse closure.

## 1. A self-contained Bernoulli denominator bound

Let B denote the Bernoulli umbra with EGF t/(e^t-1); evaluation means B^m -> B_m with B_1=-1/2. Every 2B_m belongs to Z_(2).

Indeed, the exact Stirling identity is

B_m=sum_(r=0)^m (-1)^r r! S(m,r)/(r+1),

where S(m,r) is an integer Stirling number of the second kind. This follows by summing its EGFs:

sum_(r>=0) (-1)^r(e^t-1)^r/(r+1)=log(1+(e^t-1))/(e^t-1)=t/(e^t-1).

Each 2r!/(r+1) is dyadically integral. If v_2(r+1)=a>=1, then r>=2^a-1 and v_2(r!)>=a-1 (already the factors 2,4,...,2^(a-1) suffice; when a=1 the inequality is zero). If r+1 is odd the denominator is a unit. Thus every summand after multiplication by two is integral.

Consequently, evaluation of any integral-coefficient polynomial in B lies in (1/2)Z_2.

## 2. An integral divided-power Bernoulli source

Put S=2B+1 under this umbral evaluation. Its EGF is

E(exp(St))=exp(t) 2t/(exp(2t)-1)=t/sinh(t).

It has odd moments zero and

E(S^(2m))=(2-2^(2m))B_(2m)

for m>=0 (at m=0 this is 1). Thus all its ordinary moments are integral by the preceding denominator bound.

Set U=(S^2-1)/2. In the underlying polynomial variable B,

U=2B(B+1).

For every r,ell>=0,

E(S^ell U^r/r!) belongs to Z_2.

At r=0 this is ordinary S-moment integrality. At r>0, the expression is

(2^r/r!) E((2B+1)^ell B^r(B+1)^r).

The polynomial inside evaluation has integral coefficients, so its evaluation has valuation at least -1. Meanwhile

v_2(2^r/r!)=r-v_2(r!)=s_2(r)>=1.

Therefore the product is integral. No convergence or bounded-measure claim is needed; these are finite polynomial evaluations.

Take two independent copies S,T, and put V=(T^2-1)/2. Their joint umbral evaluation is the tensor product of the two evaluations, so every monomial

S^ell T^m gamma_r(U)gamma_s(V),  gamma_r(Z)=Z^r/r!,

has integral evaluation. Integral linear combinations over Z_2[i] do as well.

## 3. The actual j=2 factorization

Work temporarily over Q_2(i), with

a=(1+i)/2, b=(1-i)/2, a+b=1, a-b=i, ab=1/2.

The exact source identity is

2! sum_(q>=0) t^(4q)/(4q+2)! = (cosh(t)-cos(t))/t^2

= [sinh(at)/(at)] [sinh(bt)/(bt)].

(The product identity follows from 2sinh(at)sinh(bt)=cosh(t)-cosh(it), and ab=1/2.)

Therefore the reciprocal is

[at/sinh(at)] [bt/sinh(bt)].

Under the independent S,T evaluations this is the EGF of

Y=aS+bT.

It follows exactly, coefficient by coefficient, that C_2(n)=E(Y^(4n)).

## 4. The divided-power cancellation polynomial

Using S^2=1+2U and T^2=1+2V,

Y^2=ST+i(U-V),

Y^4=1+2U+2V+6UV-U^2-V^2+2iST(U-V).

Consequently

W=(Y^4-1)/2 = U+V+3UV-U^2/2-V^2/2+iSTU-iSTV.

Let M be the Z_2[i]-module spanned by the monomials

S^ell T^m gamma_r(U)gamma_s(V).

It is an algebra: gamma_r(U)gamma_s(U)=binom(r+s,r)gamma_(r+s)(U), and similarly for V. Its umbral evaluation is integral by Section 2.

Every divided power gamma_k(W) lies in M. This follows from the divided-power addition formula and these exact integral component formulas:

* gamma_k(U)=gamma_k(U), and similarly for V;
* gamma_k(3UV)=3^k k! gamma_k(U)gamma_k(V);
* gamma_k(-U^2/2)=(-1)^k (2k-1)!! gamma_(2k)(U), and similarly for V;
* gamma_k(iSTU)=i^k S^k T^k gamma_k(U);
* gamma_k(-iSTV)=(-i)^k S^k T^k gamma_k(V).

At k=0 the odd double-factorial coefficient is interpreted as 1. Every displayed scalar is an integer or a Gaussian integer. Thus expanding gamma_k of the seven-term sum gives an integral linear combination of elements of M.

Furthermore, for n>=0,

Y^(4n)=(1+2W)^n.

For each q>=0,

W^q gamma_k(W)=[(k+q)!/k!] gamma_(k+q)(W) belongs to M.

The finite binomial expansion therefore proves

E(Y^(4n) gamma_k(W)) belongs to Z_2[i].

## 5. Higher differences

The exact polynomial stencil yields

Delta_1^k C_2(n)=E(Y^(4n)(Y^4-1)^k)

=2^k k! E(Y^(4n) gamma_k(W)).

Hence Delta_1^k C_2(n)/(2^k k!) belongs to Z_2[i]. The quotient is rational (the original generating function and difference stencil are rational), and Q_2 intersect Z_2[i]=Z_2. Equivalently, elements of Z_2[i] are integral over Z_2 and any rational 2-adic integral element lies in Z_2. This proves the all-row, all-order factorial bound.

For a positive step u, put s=v_2(u) and write

((1+X)^u-1)^k=sum_m b_m X^m.

The same coefficient argument as in the proved global theorem gives v_2(2^m b_m)>=k(s+1). Every nonzero term has m>=k, so v_2(m!)>=v_2(k!). Applying the proved step-one factorial estimate to Delta_1^m C_2 proves

v_2(Delta_u^k C_2(n))>=k(s+1)+v_2(k!).

Zero differences use infinite valuation. At k=0 the statement is ordinary integrality. The unnormalized j=2 packet is 2C_2(n), so its bound gains one further bit.

## Scope and validation boundary

This is a finite exact umbral proof for the actual j=2 kernel. It does not assert a generic divided-flat reciprocal theorem, does not prove the j=1 factorial candidate, and does not address the separate Euler-residual root-simplicity program. No new Lean compilation is claimed.

## 6. Mixed-step differences

More generally, for any positive natural steps H_1,...,H_k,

v_2(Delta_(H_1)...Delta_(H_k) C_2(n))
  >= k+v_2(k!)+sum_(i=1)^k v_2(H_i).

For each i, every coefficient of (1+2W)^(H_i)-1 has valuation at least 1+v_2(H_i), as proved in the base theorem. Thus in

product_i [(1+X)^(H_i)-1]=sum_m b_m X^m,

every coefficient 2^m b_m has valuation at least k+sum_i v_2(H_i). The product has no terms of degree below k. The factorial first-step estimate supplies a further v_2(m!)>=v_2(k!) in every nonzero term after applying it to the sequence. This proves the claimed mixed-step bound. If any H_i=0, the mixed difference is zero; the empty mixed difference k=0 is ordinary integrality.

The original unnormalized j=2 sequence gains one bit in this bound.

## 7. Actual analytic interpolation

Let a_m=Delta_1^m C_2(0). The theorem proves a_m/m! in 2^m Z_2. The exact Newton interpolation on natural rows is

C_2(n)=sum_(m=0)^n (a_m/m!) (n)_m.

Use the signed Stirling integers s(m,ell) defined by

(x)_m=sum_(ell=0)^m s(m,ell)x^ell.

For every ell>=0 define

b_ell=sum_(m>=ell) (a_m/m!) s(m,ell).

This converges dyadically: its mth summand has valuation at least m. Moreover b_ell belongs to 2^ell Z_2. Uniform convergence on Z_2 permits exchanging the two sums, yielding

C_2(x)=sum_(ell>=0) b_ell x^ell,

with C_2 agreeing with the original rational packet at every nonnegative integer. Both the Newton series and this ordinary power series converge uniformly on Z_2, so this is also the unique continuous interpolation.

The ordinary power series converges on the larger open dyadic disc |x|_2<2, since |b_ell|_2<=2^(-ell). Thus the interpolation is analytic beyond the closed unit disc. No claim about convergence on the boundary |x|_2=2 is needed.

The factorial estimate therefore proves actual analyticity for this prescribed lane; the earlier weaker k-flat estimate alone did not prove that conclusion.
