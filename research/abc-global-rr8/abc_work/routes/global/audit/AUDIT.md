# Independent audit of the common-power lifting statements

**Primary verdict: proved as written.** This verdict covers Theorems 1–2, Corollary 2.1 and escape inequality (9) in the exact note revision below. It does not assert unrestricted ABC, novelty, or Lean compilation.

Audited source: `../PROOF_NOTE.md`, SHA-256 `3535e4f37e82310cdd59f1c1280fd7615173ea310ec448adccc7fdc028d8229e`.

## Claim card

For coprime integers A>B>=1, n>=1, c=A^n+B^n, every odd p|c has d=ord_p(A/B) and e=v_p(A^d-B^d). The claimed valuation formula is v_p(c)=e+v_p(n). Its multiplicative consequence is U(c)=B_2 W_n G_n with G_n|n and B_2<=A. For epsilon>0, Y>=1, gamma=epsilon/(1+epsilon), if all exceptional output primes satisfy p<=Y and 1+J(Y)+log_2 n<=gamma n, the asserted conclusion is c<=rad(A^n B^n c)^(1+epsilon). The corollary quantifies N solely in terms of epsilon,delta, allowing A,B to vary.

## Dependency graph and independent reconstruction

1. Primitivity gives p∤AB for p|c. The finite-field element A/B has order d dividing p−1.
2. Its n-th power equals −1. Since p is odd, −1 has exact order two. Therefore d is even and n=(d/2)k with k odd. In particular p∤d and v_p(k)=v_p(n).
3. Put X=A^(d/2), Z=B^(d/2). Then p|X+Z, p∤X−Z and p∤XZ. Hence v_p(A^d−B^d)=v_p(X+Z).
4. For odd p, odd k and p|X+Z, the binomial/factorization proof of the elementary lifting identity gives v_p(X^k+Z^k)=v_p(X+Z)+v_p(k). Combining the preceding steps proves the critical formula. No averaging or distribution claim is used.
5. Multiplying p^(v_p(c)−1) over odd output primes yields W_n G_n. Its residual 2-adic contribution is exactly B_2. For odd A,B, odd n preserves v_2(A+B), while even n gives c=2 modulo 8. This verifies both branches, including n=1 and n=2. Coprimality rules out both bases even. The displayed B_2<=A bound follows from B_2<=(A+B)/2<A in the only nontrivial branch.
6. For each output prime p, p^e<=A^d−B^d<A^d and d<=p−1, proving log W_(<=Y)<=J(Y)log A. The rough J bound is valid because the integers p−1 occurring are a subset of 0,...,floor(Y)−1. There is no dependence on the bases in its coefficient.
7. Thus log U(c)<=(1+J(Y))log A+log n. Since A>=2, log n<=log_2(n)log A. Condition (6) therefore implies log U(c)<=gamma n log A<=gamma log c. The radical identity R=D c/U(c), D>=1, proves the asserted inequality.
8. With Y=n^(1/2−delta), the ratio of the error to log c is bounded above by 1/n+(1/2)n^(−2delta)+log_2(n)/n. This tends to zero independently of A,B. It proves both the uniform corollary and the factor gamma/2 in the escape bound.

## Obligation matrix

| Obligation | Status | Reason |
|---|---|---|
| Domain and invertibility | Passed | Coprimality implies p∤AB |
| Half-order class and parity | Passed | Unique order-two element in a cyclic odd-prime unit group |
| Exact valuation formula | Passed | Reconstruction in steps 2–4 |
| n=1 and 2-adic branches | Passed | Direct factorization and reduction modulo 8 |
| G_n divides n | Passed | Each exponent is v_p(n) on a subset of odd primes |
| Exceptional small-prime bound | Passed | Divisibility plus A^d−B^d<A^d |
| Uniformity in A,B | Passed | All error ratios bounded using log A>=log 2 |
| Escape inequality | Passed | Subtract an upper bound on the small-prime part |
| ABC for arbitrary triples | Out of scope | Note correctly leaves n=1 and unrestricted multipliers open |
| Novelty and external literature | Out of scope | No historical priority claim; proof has no load-bearing external source |
| Lean verification | Out of scope | No such claim |

## Independent finite checks

Using exact integer powers rather than the author's modular valuation routine, tested every coprime pair 1<=B<A<=20, every n in 1,...,12, and every odd prime p<=97 dividing A^n+B^n. The order was found by directly trying d=1,...,p−1. All 2,015 odd-prime contacts satisfied the valuation formula, and all 492 odd-base cases satisfied the 2-adic branch formula. Details are in `independent_checks.json`. These are limited finite checks, separate from the universal elementary proof.

## Remaining gap

The theorem does not control log W_n from exceptional primes above the cutoff. It also does not generalize the half-order argument to arbitrary h in 1+hq^n or to arbitrary primitive input exponent vectors. No small-case success fills either gap. The strongest safe statement is exactly the uniform restricted theorem in Corollary 2.1. The next meaningful check would test a proposed large-exceptional-prime estimate against exact exceptional birth-depth examples, beginning with base 2, p=1093, n=182.

Review provenance: fresh delegated audit of the raw proof; the critic reconstructed its critical implication. Agreement between agents is not a formal proof certificate. No source edit was made.
