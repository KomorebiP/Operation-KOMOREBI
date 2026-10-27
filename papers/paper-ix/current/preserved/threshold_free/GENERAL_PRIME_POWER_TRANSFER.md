# Prime-power section transfer without a starting threshold

This file derives a further consequence of the translated differential proof.
It uses the exact normalized Euler section, not a numerical surrogate.

Let p be prime, a>=1, N=p^a, and 0<=j<N. Define

    G(t)=j! sum_(n>=0) t^(Nn)/(Nn+j)!,
    G(t)^(-1)=sum_(n>=0) C_(N,j)(n) t^(Nn)/(Nn)!.

Then the original generalized Euler coefficient is
E_(Nn)^(N,j)=j! C_(N,j)(n).

## 1. Source integrality and higher differences

The packed source coefficient is

    g(n)=prod_(i=1)^j (1+(N/i)n)^(-1).

Every N/i belongs to p Z_p, because i<N implies v_p(i)<a.
For s in p Z_p,

    Delta_1^k [(1+s n)^(-1)]
      =(-s)^k k! / prod_(h=0)^k (1+s(n+h)).

The denominator factors are units, so the expression is divisible by p^k.
The exact discrete Leibniz identity proves closure of this property under
products. Hence Delta_1^k g(n) belongs to p^k Z_p for all n,k>=0.

## 2. Translated differential reciprocal lemma

Write D=d/dt and L_lambda=(D^N-lambda)/p on Q_p[[t]].
Every interior binomial coefficient binom(N,i) is divisible by p, since
(1+X)^(p^a)=1+X^(p^a) over F_p.

Consequently the proof in combinatorial/THRESHOLD_FREE_EIGENFLAT_PROOF.md
works with p replacing 2:

    L_(lambda+mu)(AB)=(L_lambda A)B+A(L_mu B)
       +sum_(i=1)^(N-1) [binom(N,i)/p](D^i A)(D^(N-i) B).

All operators on each factor commute. In the full multinomial expansion
of L_0^k(G G^(-1))=0, the unique term using inverse L-order k is
G L_(-1)^k G^(-1). Every other term has lower inverse L-order.
Induction in the Hurwitz-integral lattice proves that G^(-1) is
(-1)-flat. This argument has no coefficient-index restriction.

Thus, with S the packet shift,

    (S+1)^k C(n) belongs to p^k Z_p       for all n,k>=0.

For p=2, L_1=L_(-1)-1, so the usual differences also have this bound.
For odd p that conversion is invalid. Instead put A(n)=(-1)^n C(n).
Then

    Delta_1^k A(n)=(-1)^(n+k)(S+1)^k C(n),

and A has the ordinary p^k higher-difference property.

## 3. Mixed steps and the original normalization

If Delta_1^m F is divisible by p^m for every m, use

    Delta_H=sum_(i=1)^H binom(H,i) Delta_1^i.

Every coefficient p^i binom(H,i) has valuation at least 1+v_p(H):
v_p binom(H,i)>=v_p(H)-v_p(i), and i-v_p(i)>=1.
Multiplying these polynomial identities gives, for positive H_1,...,H_k,

    v_p(Delta_(H_1)...Delta_(H_k) F(n))
      >=sum_(nu=1)^k [1+v_p(H_nu)].

For p=2 this applies directly to C. For arbitrary p define
T_H=S^H-(-1)^H. The exact sign conversion from A to C therefore gives

    v_p(T_(H_1)...T_(H_k) E_(Nn)^(N,j))
      >=v_p(j!)+sum_(nu=1)^k [1+v_p(H_nu)].

For p=2 the stronger *ordinary* difference statement also holds:

    v_2(Delta_(H_1)...Delta_(H_k) E_(Nn)^(N,j))
      >=v_2(j!)+sum_(nu=1)^k [1+v_2(H_nu)].

Order zero is ordinary integrality. A zero step in ordinary mixed
differences makes the result zero and is handled separately. All statements
hold starting at n=0. Zero values have infinite valuation.

## Scope and boundary

This is a self-contained prime-power section theorem. For odd p it is a
sign-twisted higher-difference theorem, not an assertion that ordinary
step-one differences are divisible by p. Indeed for j=0, C(0)=1 and
C(1)=-1, so the ordinary first difference is -2.

The direct translated differential argument does not cover arbitrary
non-prime-power N: its interior binomial coefficients need not be divisible
by p. No such extension is claimed. This file makes no historical-priority
claim and has not been compiled in Lean.
