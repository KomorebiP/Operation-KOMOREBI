# From threshold-free Mahler divisibility to exact dyadic periods

Use the threshold-free base theorem proved in `../combinatorial/THRESHOLD_FREE_EIGENFLAT_PROOF.md`:

> For j=0,1,2,3 and every k≥0, a_j(k):=Δ^k C_j(0) belongs to 2^k Z_2.

The argument below proves that this base theorem, together with finitely many exact rational calculations, implies an exact first-difference law at every row and every positive step. The base theorem was reviewed here: its commuting tensor differential operators, integral multinomial expansion, and inverse induction preserve the entire Hurwitz lattice without a row cutoff.

## General lemma

Let C:Z_{≥0}→Z_2 have Newton coefficients a_k=Δ^k C(0). Suppose b≥0,

* v_2(a_1)=b;
* v_2(a_k)≥b+1+floor(log_2 k) for every k≥2.

Then, for every n≥0 and every H>0,

v_2(C(n+H)−C(n))=b+v_2(H).

Proof. Newton's exact finite expansion gives C(N)=Σ_{k=0}^N a_k binom(N,k). By Vandermonde,

binom(n+H,k)−binom(n,k)=Σ_{i=1}^k binom(H,i)binom(n,k−i).

For 1≤i≤H, the identity binom(H,i)=(H/i)binom(H−1,i−1) gives

v_2(binom(H,i))≥v_2(H)−v_2(i)≥v_2(H)−floor(log_2 k).

Terms i>H are zero. Consequently each k≥2 summand in the Newton difference has valuation ≥b+v_2(H)+1. The k=1 summand is Ha_1, of valuation exactly b+v_2(H). Thus the full finite sum has that exact valuation. ∎

The same hypotheses also give a uniformly convergent Newton interpolation on Z_2, and the same exact law for every distinct n,m in Z_2. For integer inputs, no infinite series argument is needed.

## Application to the four N=4 reciprocal lanes

Set

C_j(n)=(4n)![t^{4n}](j! Σ_{q≥0} t^{4q}/(4q+j)!)^{−1}, 0≤j≤3.

Then C_j(0)=1 and the rational recurrence is

C_j(n)=−Σ_{q=1}^n binom(4n,4q) A_j(q) C_j(n−q),

where

A_0(q)=1,
A_1(q)=1/(4q+1),
A_2(q)=1/((4q+1)(2q+1)),
A_3(q)=3/((4q+1)(2q+1)(4q+3)).

All denominators here are odd. Put b=(1,1,4,2).

The following exact low Newton coefficients cover every k for which the base bound v_2(a_j(k))≥k does not automatically imply the general lemma's stronger requirement.

| j | k | a_j(k) | v_2 |
|---|---|---|---|
| 0 | 1 | −2 | 1 |
| 0 | 2 | 72 | 3 |
| 1 | 1 | −6/5 | 1 |
| 1 | 2 | 184/45 | 3 |
| 2 | 1 | −16/15 | 4 |
| 2 | 2 | 64/45 | 6 |
| 2 | 3 | −14848/1365 | 9 |
| 2 | 4 | 71426048/69615 | 13 |
| 2 | 5 | −25509691392/85085 | 16 |
| 2 | 6 | 149113198870528/765765 | 22 |
| 3 | 1 | −36/35 | 2 |
| 3 | 2 | 256/231 | 8 |
| 3 | 3 | −65792/35035 | 8 |
| 3 | 4 | 161644544/4849845 | 15 |

For j=0,1 the generic bound works at k=3 and every k≥4. For j=2 it works at every k≥7. For j=3 it works at every k≥5. These elementary inequalities follow from k−floor(log_2 k)≥b+1 in those ranges; after a power of two the left side increases monotonically until the next power, and its values at the relevant powers also increase.

Therefore the base theorem implies

v_2(C_j(n+H)−C_j(n))=v_2(H)+b_j

for every n≥0 and H>0.

For the unnormalized generalized Euler numbers E_{4n}^{(4,j)}=j!C_j(n), put B_j=b_j+v_2(j!)=(1,1,5,3). Then

v_2(E_{4(n+H)}^{(4,j)}−E_{4n}^{(4,j)})=v_2(H)+B_j.

In particular, the least positive row period modulo 2^r is exactly

P_j(r)=2^{max(0,r−B_j)}.

This period is valid starting at row zero. It is optimal: if H is a period at even one row modulo 2^r, the exact law forces v_2(H)+B_j≥r. When r≤B_j the least period is 1. In the actual Euler subscript, the period is 4P_j(r).

## Scope

This is a proved deduction about the N=4 congruence conjecture using the threshold-free Mahler divisibility theorem. It does not close the distinct dyadic Euler-tail root simplicity/nonvanishing program.

## Complete dyadic residue distribution

The Newton series converges uniformly on Z_2 because v_2(a_j(k))≥k and binom(x,k) is integral on Z_2. It therefore defines a continuous extension of C_j. The first-difference identity extends from natural integer pairs to every distinct pair x,y∈Z_2 by continuity; approximate x,y by naturals with v_2(x−y) stable, and the resulting quotient remains a unit.

Consequently

T_j(x)=(C_j(x)−1)/2^{b_j}

is a distance-preserving map Z_2→Z_2 with T_j(0)=0. It is also onto: the exact distance identity induces an injection on every quotient Z_2/2^r Z_2, which is a bijection since both sides have 2^r elements. Inverting these compatible quotient bijections gives a preimage of every dyadic integer. Thus C_j is a bijection from Z_2 onto 1+2^{b_j}Z_2; the unnormalized Euler interpolation is a bijection onto j!+2^{B_j}Z_2.

Equivalently, for r>B_j, one least row period modulo 2^r visits every residue in j!+2^{B_j}Z/2^r Z exactly once. For r≤B_j it is constant with least row period 1.

## Infinite sharp subfamily at every power-of-two rank

The base theorem applies more generally to every N=2^a. For each 0≤j<N put

C_{N,j}(n)=(Nn)![t^{Nn}](j! Σ_{q≥0}t^{Nq}/(Nq+j)!)^{−1},

g_{N,j}(n)=1/binom(Nn+j,j)=∏_{s=1}^j(1+(N/s)n)^{−1}.

Because v_2(N/s)≥1 for s<N, each affine denominator is a unit on Z_2 and has 2-flat finite differences. Pointwise products and inverses preserve that property, so the general reciprocal theorem gives v_2(Δ^k C_{N,j}(0))≥k for every lane.

For every N=2^a≥4 and 0≤j<N/2, in fact v_2(N/s)≥2 for all s≤j. Therefore g(1)≡1 mod4 and g(2)≡1 mod8. The recurrence gives

a_1=−g(1)−1,

a_2=binom(2N,N)g(1)^2−g(2)+2g(1)+1.

The first expression has valuation exactly 1. The central binomial coefficient is 6 modulo 8 for every N=2^a≥2: write B_a=binom(2^{a+1},2^a)=2∏_{k=1}^{2^a−1}(1+2^a/k). Its even k factors give B_{a−1}; its odd k factors are all 1 modulo4 for a≥2. Hence B_a≡B_{a−1} mod8, and B_1=6. Consequently a_2≡6−1+2+1=0 mod8. The generic Mahler bound covers every k≥3, so the general lemma yields the exact law

v_2(C_{N,j}(n+H)−C_{N,j}(n))=v_2(H)+1

for every n≥0,H>0, all N=2^a≥4, and all 0≤j<N/2. This also holds for N=2,j=0 since g=1 and the same a_1,a_2 calculation applies.

Thus these lanes have exact least unnormalized row period

2^{max(0,r−1−v_2(j!))}

modulo 2^r, starting at row zero. Their normalized dyadic interpolations biject Z_2 onto 1+2Z_2.

The all-rank lower bound does not imply an exact first-difference law in every upper lane. For example, at N=16,j=9, the first difference at n=0 has valuation 5 while the H=2 difference has valuation 7, rather than 6. No universal upper-lane isometry is claimed.

## Full exact period laws at N=2 and N=8

The same finite-coefficient criterion applies to every lane at N=2 and N=8. The exact rational verifier `verify_all_rank_extensions.py` computes the reciprocal recurrence and checks every low Mahler coefficient not covered by v_2(a_k)≥k. It records all coefficients in `all_rank_extensions_verified.json`.

Thus, for N=2 and N=8, for every lane j, n≥0, and H>0,

v_2(C_{N,j}(n+H)−C_{N,j}(n))=v_2(H)+b_{N,j}.

| Rank N | Normalized shifts b_{N,j}, j increasing from zero | Original Euler shifts b_{N,j}+v_2(j!) |
|---|---|---|
| 2 | 1, 2 | 1, 2 |
| 4 | 1, 1, 4, 2 | 1, 1, 5, 3 |
| 8 | 1, 1, 1, 1, 4, 3, 2, 2 | 1, 1, 2, 2, 7, 6, 6, 6 |

Every lane in this table therefore has exact least row period 2^{max(0,r−B_{N,j})} modulo 2^r, and one such period enumerates the entire permissible coset exactly once. In the Euler subscript the period is N times the row period.

The same verifier preserves exact rational failures of the naive extension to every upper lane: N=16,j=9,n=0,H=2 has valuation 7 rather than 6; N=32,j=18,n=0,H=2 has valuation 6 rather than 7; N=32,j=19,n=0,H=2 has valuation 7 rather than 6. These failures concern the proposed stronger exact law, not the proved universal lower bound or the underlying conjecture.
