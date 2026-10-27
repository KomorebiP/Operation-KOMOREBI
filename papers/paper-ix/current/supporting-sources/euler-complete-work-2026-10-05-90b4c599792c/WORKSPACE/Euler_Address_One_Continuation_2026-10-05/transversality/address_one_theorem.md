# Address-one derivative exclusion theorem

This note proves a structural exclusion theorem for the actual Euler address-one recurrence. It does not prove nonvanishing on the remaining critical strata.

## Setup and source coordinate

Let j be the true terminal label of the wall under consideration, let its last lower minimizing address be exactly 1, and set k=j−1. Thus k is the regular complement. Put t=v₂(k)≥4, D=t−4, and δ≥1 for the outer wall distance. The identities below require this true-terminal and last-lower-address hypothesis; they are not asserted for an arbitrary representation r=B2^L−j. Assume the wall and complement have the normalized identities established in the source notes:

G(x)=u P₁(x)F(x−1)+2^(δ+D) A(x),   F=G_(r+1),   u∈Z₂×,

F(y)=P_k(y)U(y−k)+2^δ V(y),

where U,V∈Z₂⟨y⟩ both reduce coefficientwise to 1 modulo 2. Here

P₁(x)=x(2x−1),
A(x)=(9^(x+1)−1)/(8(x+1)(2x+1)).

These normalizations follow from H_r=A+a_(r,1)P₁H_(r+1), v₂(a_(r,1))=4−t=−D, μ_r=−D−δ, and μ_(r+1)=−δ.

Put ℓ=log9 and

C(y)=(9^y−1)/(8y)=(ℓ/8) Σ_(n≥0) ℓ^n y^n/(n+1)!,
Q(x)=P₁(x)/A(x)=x(4x²−1)/C(x+1).

C is a restricted analytic unit and C≡1 (mod4). Consequently Q≡−x (mod4) coefficientwise, and Q′(x) is a unit for every x∈Z₂. More precisely,

C′/C=ℓ/2+terms divisible by 16,
(Q/x)′/(Q/x)=8x/(4x²−1)−C′(x+1)/C(x+1)

has exact valuation 2 on Z₂. Only Q′ being a unit is needed below. Q is an analytic isometry of Z₂ because Q≡−x (mod4) coefficientwise.

The source-normalized equation is

G/A=u Q(x)F(x−1)+2^(δ+D).

At any root x, x≠0 and F(x−1)≠0. Write s=v₂(x). Then

v₂(F(x−1))=δ+D−s.                                     (1)

If the root were multiple, differentiation (the derivative of A drops out at a zero) would give

Q′F+QF′=0,

so, since v₂(Q)=s and v₂(Q′)=0,

v₂(F)=s+v₂(F′).                                       (2)

## Complement discs

For 0≤i<k, set

d_i=v₂(i!)+v₂((k−1−i)!),
h_i=1+floor(log₂(max(i,k−1−i))),
B_i=i+2^h_i Z₂.

These discs partition Z₂. Since k is divisible by 2^t, h_i≥t>D.

The exact regular-wall atlas gives:

* If δ<d_i+h_i, then v₂(F(y))=δ throughout B_i.
* If δ≥d_i+h_i, there is a unique simple α_i∈B_i, with
  v₂(F(y))=d_i+v₂(y−α_i),
  v₂(α_i−i)=δ−d_i,
  and v₂(F′(y))=d_i throughout B_i.

The last derivative statement follows directly from the coefficientwise affine reduction on B_i, including at the root.

## Theorem

Every multiple dyadic root of G must lie in a root-free complement disc, and must satisfy

v₂(x)=D,
v₂(i+1)=D,
δ=d_i+D.                                               (3)

In particular every other address-one root is simple.

### Proof: emerged complement discs

Suppose x−1∈B_i and δ≥d_i+h_i. Put β=α_i+1 and z=v₂(x−β)≥h_i. By (2), z=s. By (1),

δ−d_i=2s−D.                                            (4)

If s<h_i, z=s contradicts z≥h_i. Hence s≥h_i, and (4) implies δ−d_i>h_i because D<h_i.

The translated disc i+1+2^h_i Z₂ therefore contains zero. Its center i+1 has valuation exactly h_i: among these consecutive-skeleton discs the unique one containing zero has i+1=2^floor(log₂k) and h_i=floor(log₂k). Since v₂(β−(i+1))=δ−d_i>h_i, we get v₂(β)=h_i.

Now if s>h_i, then v₂(x−β)=h_i<s. If s=h_i, the two units x/2^h_i and β/2^h_i have even difference, so v₂(x−β)>h_i=s. Both contradict z=s. Thus no multiple root occurs in an emerged complement disc.

### Proof: root-free complement discs

Now δ<d_i+h_i. Then v₂(F)=δ, so (1) forces s=D. Since D<h_i, the disc center satisfies v₂(i+1)=D.

On B_i, the derivative of P_k times U has valuation exactly d_i: the derivative of the normalized skeleton is a unit, while the U′ contribution has larger valuation. Since V≡1 modulo2 coefficientwise, v₂(2^δ V′)≥δ+1.

If d_i>δ, this proves v₂(F′)>δ, contradicting (2), which requires v₂(F′)=δ−D≤δ. If d_i≤δ, the skeleton derivative dominates and v₂(F′)=d_i. Equation (2) now gives δ=D+d_i. This proves (3).

## Finite arithmetic form of the critical distances

Write k=2^t c with c odd, and i=2^t b+a with 0≤a<2^t and 0≤b<c. Binary complement in the lower t bits gives

d_i=k−1−t−s₂(b)−s₂(c−1−b).

Hence every multiple root must satisfy

δ=k−5−s₂(b)−s₂(c−1−b),
v₂(a+1)=t−4.                                          (5)

For each b, the second condition selects exactly eight lower-bit residues a modulo 2^t. Thus each address-one wall has at most 8c candidate skeleton discs and at most c candidate wall distances. This is an exact necessary condition; it does not assert a root or a multiple root exists.

The same condition has a compact binomial form. The factorial digit-sum formula gives

v₂ binom(c−1,b)=s₂(b)+s₂(c−1−b)−s₂(c−1),

hence

δ=k−5−s₂(c−1)−v₂ binom(c−1,b).                         (6)

Since k=2^t c, its regular wall scale is

Θ(k)=3k+1+s₂(k−1)=3k+1+t+s₂(c−1).

Consequently the critical outer exponent L=Θ(k)+δ must satisfy the exact formula

L=4k+t−4−v₂ binom(c−1,b).                              (7)

For a power-of-two complement (c=1), the binomial is binom(0,0)=1. Therefore the only critical outer exponent is L=4k+t−4. In particular terminal129 has only L=515. For terminal161, c=5 and the binomial row binom(4,b) has valuations 0,2,1,2,0, so the only critical outer exponents are L∈{639,640,641}. These exclusions are universal over every multiplier satisfying the stated true-terminal/address hypothesis, not bounded computation results.

For k=128 (j=129), t=7,c=1: only δ=123 is critical, and v₂(x)=3.

For k=160 (j=161), t=5,c=5: the binary sums for b=0,1,2,3,4 are 1,3,2,3,1. Therefore only δ∈{152,153,154} can be critical, and v₂(x)=1. At δ=153, b=2 and exactly eight integer skeleton centers remain: x≡66,70,74,78,82,86,90,94 modulo128. These eight discs all have h_i=7.

## Boundary δ=0

For k≥16 the regular-boundary reduction is F≡1+X-underlined-k modulo2. This polynomial takes value1 at both dyadic residues, and its derivative is identically zero in F₂[X] because k is divisible by4. Hence F(y) is always a unit and F′(y) is even. At a root of G/A=uQF+2^D, its derivative Q′F+QF′ is a unit. All boundary roots are therefore simple as well.

## Why the remaining unit condition is real

The regular atlas, the source A, and the exact address-one recurrence do not by themselves rule out tangency. There is an exact analytic counterexample using the same skeleton and all those structural properties.

Take k=16,t=4,D=0,δ=11, u=1. Let Q be the exact coordinate above and p=P₁₆′(0), with v₂(p)=11. Define constant units

v₀=−1/Q(1)=−5/3,
u₀=2^11 Q′(1)/(Q(1)^2 p),

and set

F(y)=u₀ P₁₆(y)+2^11 v₀,
G(x)=A(x)[Q(x)F(x−1)+2^11].

Both u₀ and v₀ are odd. F has precisely the regular-wall form, and its valuation is constantly11 throughout Z₂ because the k=16 emergence threshold is15. Yet G(1)=G′(1)=0 by the defining equations. Thus a proof of actual Euler simplicity must use more than the regular-complement atlas and the fact that its decoration is a unit. This example is not an actual Euler counterexample: u₀ and v₀ were chosen freely, whereas the actual Euler coefficients are fixed by Bernoulli ratios.
