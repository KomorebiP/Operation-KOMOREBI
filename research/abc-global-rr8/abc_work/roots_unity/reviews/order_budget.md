# Independent audit: cyclotomic order-degree budget

**Normalized claim.** Let A>B≥1 be coprime integers, n≥1, c=A^n+B^n, and R=rad(A^nB^nc). For each odd prime p|c, define d_p=ord_p(A/B) and e_p=v_p(A^{d_p}−B^{d_p}). Put

W_n=∏_{odd p|c}p^{e_p−1},
E_n={d_p: odd p|c and e_p≥2},
D_n=Σ_{d∈E_n}φ(d).

The claims are that W_n divides the product of the distinct occupied homogeneous cyclotomic factors Φ_d(A,B), that log U(c)≤log A+log n+D_n log(A+B), and that the stated degree threshold gives the claimed uniform restricted ABC inequality and escape condition.

**Primary verdict: proved as written.** Theorems 1–2, Corollaries 2.1–2.2, the stated boundary examples, and the exact allocation to birth factors are correct. The conclusion is conditional on a degree-budget hypothesis, not a proof that such a budget holds for all triples. In fact the threshold implies the stronger c≤rad(c)^{1+ε}.

## Dependency graph and obligation matrix

| Obligation | Status | Dependency or evidence |
|---|---|---|
| Orders are defined and lie among allowed conductors | Passed | p∤AB; (A/B)^n=−1 in F_p. |
| Birth valuation lies in the actual-order factor | Passed | Proper-divisor factors cannot contain p by minimality of the order. |
| Primes also dividing other conductors | Passed | Full valuation classification derived below: only d_p p^j, with valuation 1 for j≥1. |
| Exact lifting v_p(c)=e_p+v_p(n) | Passed | Elementary odd-prime binomial lifting and p∤d_p. |
| Simultaneous divisibility for many primes and shared orders | Passed | Within each order, distinct prime powers divide that single factor; multiplying distinct order factors preserves divisibility. |
| 2-adic contribution | Passed | Parity and an odd alternating quotient; explicit cases below. |
| Positive cyclotomic values and degree bound | Passed | Primitive-root product and positive conjugate pairs. |
| D_n≤n | Passed | E_n is a subset of d|2n, d∤n, whose total degree is n. |
| Uniform threshold and every-ε conclusion | Passed | Base-free inequalities log(A+B)≤2log A and log n≤log_2(n)log A. |
| Sublinear-budget corollary | Passed | Explicit threshold depending only on ε,δ given below. |
| Degree escape statement | Passed | Exact contrapositive of the sufficient threshold. |
| Uniform sublinear occupancy theorem | Not addressed | No such theorem is proved or used unconditionally. |
| Unrestricted ABC | Not addressed | High-degree exceptional channels remain uncontrolled. |

No external literature is load-bearing for this audit. The inherited lifting identity is independently reconstructed below rather than accepted as an unchecked input.

## 1. Exact odd-prime and conductor allocation

If p|c, then p∤A and p∤B, since gcd(A,B)=1. For odd p, x=A/B in F_p satisfies x^n=−1≠1. Hence d=ord_p(x) divides 2n, does not divide n, is even, and divides p−1. In particular p∤d.

Define a_m=v_p(A^m−B^m). If d∤m, then a_m=0. If d|m, elementary odd-prime lifting gives

a_m=e_p+v_p(m/d).

For completeness, writing X=Y+p^e t with p∤Yt shows that raising X,Y to a power prime to p preserves v_p(X−Y)=e (the geometric sum is a unit modulo p), while raising to the p-th power increases it by exactly one. The binomial leading term has valuation e+1 and all subsequent terms have larger valuation for odd p. Factoring an arbitrary positive exponent into a p-power and a coprime part proves the displayed formula.

Because p∤d and p is odd,

v_p(A^{2n}−B^{2n})=e_p+v_p(2n/d)=e_p+v_p(n).

Also p∤A^n−B^n, since A^n≡−B^n and 2B^n is a unit modulo p. Therefore all of this valuation belongs to c=A^n+B^n:

v_p(c)=e_p+v_p(n).

Now use A^m−B^m=∏_{t|m}Φ_t(A,B). At m=d, every proper-divisor factor is prime to p: otherwise p|A^t−B^t for a proper divisor t<d, contradicting the definition of d. Consequently

v_p(Φ_d(A,B))=e_p.

This argument does not assume that p is absent from other conductors. The complete allocation is

v_p(Φ_m(A,B)) = e_p if m=d;
                           1 if m=d p^j for j≥1;
                           0 otherwise.

To verify this classification without an unstated cyclotomic theorem, sum the proposed values over all t|m. The result is 0 if d∤m, and e_p+v_p(m/d) if d|m, exactly a_m. Values of the individual cyclotomic factors are uniquely recovered recursively from these divisor sums. Thus p can indeed appear at conductors divisible by p, but those appearances are ordinary lifting, not additional birth depth. Among the allowed factors of c, the conductors d p^j with 1≤j≤v_p(n) account exactly for v_p(n).

For each d∈E_n, every exceptional prime with actual order d contributes the distinct factor p^{e_p−1}, and their product divides Φ_d(A,B), since each such prime has valuation e_p there. Multiplication over distinct d gives exactly the claimed W_n divisibility. Extra appearances of any prime in other occupied factors can only increase the valuation of the right side; they cause neither cancellation nor a missing branch.

## 2. The 2-adic term and U(c)

Let B_2=2^{max(v_2(c)−1,0)}. There are three exhaustive cases:

| Parity and exponent | v_2(c) | Bound for B_2 |
|---|---:|---|
| A,B of opposite parity | 0 | B_2=1≤A |
| A,B both odd and n even | 1 | B_2=1≤A, since odd squares are 1 modulo 8 |
| A,B both odd and n odd | v_2(A+B) | B_2≤(A+B)/2<A |

In the last case, (A^n+B^n)/(A+B) is an odd alternating sum of n odd terms, so the valuation equality follows directly, including n=1.

For the odd primes, define G_n=∏_{odd p|c}p^{v_p(n)}. Then G_n|n, and the preceding exact valuation formula gives

U(c)=B_2 W_n G_n,
B_2≤A,
G_n≤n.

There is no residual prime contribution. Empty products are 1, so the formulas cover the absence of odd prime factors or exceptional primes.

A discriminating hand check is A=8,B=1,n=3: c=513=3^3·19. For p=3, d=2 and e=2; Φ_2(8,1)=9 has valuation 2, while Φ_6(8,1)=57 has valuation 1. Thus W_n=3, G_n=3, B_2=1, and U(c)=9. This separates birth depth from the ordinary p-divisible conductor and checks the overlap issue directly. The case A=3,B=1,n=1 gives c=4 and B_2=2<A, checking the odd-exponent 2-adic branch.

## 3. Positivity, size, and available degree

For each occupied d, the homogeneous cyclotomic value is the product of φ(d) factors A−ζB over the primitive d-th roots of unity. Every factor has modulus at most A+B. Since d is even and at least 2, d=2 contributes the positive value A+B, and for d>2 all primitive roots pair into nonreal conjugate pairs giving positive products. Therefore

0<Φ_d(A,B)≤(A+B)^{φ(d)}.

The divisibility proved above gives

log W_n≤Σ_{d∈E_n}log Φ_d(A,B)≤D_n log(A+B).

All primes sharing one order use the same factor, so the degree is correctly charged once per distinct occupied order. Combining this with B_2≤A and G_n≤n proves

log U(c)≤log A+log n+D_n log(A+B).

The allowed conductors are exactly d|2n with d∤n, because

X^n+Y^n=∏_{d|2n, d∤n}Φ_d(X,Y).

Their degrees sum to 2n−n=n. Hence 0≤D_n≤n. The definition at n=1 is valid; the later sufficient threshold is then impossible for finite ε>0, so it makes no false small-exponent assertion.

## 4. Uniform ABC criterion and parameters

Fix ε>0 and γ=ε/(1+ε). Since A≥2 and B<A,

A+B≤A²,
log n≤log_2(n)log A.

Thus

log U(c)≤[1+log_2(n)+2D_n]log A.

Under the proposed threshold, this is at most γn log A≤γ log c. Therefore U(c)≤c^γ and rad(c)=c/U(c)≥c^{1−γ}. Consequently

c≤rad(c)^{1+ε}≤R^{1+ε}.

This proves Theorem 2 uniformly in the bases. The source's identity R=rad(AB)rad(c), used in its equivalent logarithmic argument, is valid because gcd(AB,c)=1. The sharper base-dependent threshold follows by retaining the unrounded ratios log(A+B)/log A and log n/log A.

For Corollary 2.1, ε and δ are fixed before the bases are chosen. If D_n≤n^{1−δ}, then the threshold follows from

(1+log_2(n))/n+2n^{−δ}≤γ.

For example, it suffices to take

N_{ε,δ}=ceil(max{16,(4/γ)^2,(4/γ)^{1/δ}}).

For n≥16, log_2(n)≤sqrt(n) and 1+log_2(n)≤2sqrt(n). The two displayed contributions are then at most γ/2 each. This makes the uniformity explicit: the threshold depends on ε,δ alone, and the conclusion applies to every triple satisfying the budget at that n. It does not assert that the budget eventually holds for every choice of bases.

The degree-escape inequality is precisely the contrapositive: if c>R^{1+ε}, then 1+log_2(n)+2D_n>γn, yielding D_n>(γn−1−log_2(n))/2. For fixed ε and large n this forces a positive linear degree proportion.

The n=3^s example is correct: Σ_{j=0}^Jφ(2·3^j)=3^J, so occupancy confined through J≤(1−δ)s gives the proposed sublinear budget. The prime-exponent and binary-exponent boundary descriptions are also correct: an occupied primitive channel costs ℓ−1 at an odd prime exponent ℓ, while for n a power of 2 the sole possible conductor is 2n and its degree is n.

## 5. Computation scope and remaining limitation

I inspected verify_order_budget.py and its recorded output without running its output-writing entry point. The script enumerates all coprime 1≤B<A≤10 and 1≤n≤12, recursively constructs the integral homogeneous cyclotomic values, computes orders by exact modular powers, and checks the product allocation, valuation identity, degree range and integer size inequality. The reported 372 grid cases, 32 nonempty degree cases, 45 imprimitive overlap contacts and three controls are consistent with the implemented domain. These finite checks do not establish a distribution law or asymptotic occupancy bound.

The proof and this audit do not require a finite scan: all universal implications above are derived directly. No original file was modified.

The exact remaining gap is control of high-degree exceptional channels. The theorem permits large primes in low-degree channels but does not exclude an exceptional prime in a channel of degree comparable to n. No unconditional bound D_n=o(n), valuation compensation, or radical payment for such a channel is supplied. This is a valid restricted ABC criterion, not unrestricted ABC.

## 6. Provenance and final input hashes

Independent subagent proof audit from the raw definitions. A second isolated subagent checked the 2-adic cases and threshold parameters, assuming the odd-prime budget bound. Shared-model review is not formal verification. No external source or Lean compilation was used. Final mathematical source was read after its author declared it frozen.

SHA-256 inputs:

- ORDER_BUDGET.md: `46679caa7dedefda2557b48f16e3de0f375b8e4e2b03651694a6001d8837f0ea`
- verify_order_budget.py: `ba94417d645b34d671cf1f5363ae8dc49cc469b23eaf34559bf955e4b8420cd0`
- order_budget_verification.json: `6b395bb888127d17d0b6a2913e891509815eebded71f95e41d984ea262011ab5`

Audit date: 2026-10-25. Self-proofreading covered the complete report; no mathematical-token corrections or unresolved notation issues remained.
