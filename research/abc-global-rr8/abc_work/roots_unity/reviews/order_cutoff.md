# Independent audit: exceptional-prime cutoff and weighted order escape

**Normalized claim.** Let A>B≥1 be coprime integers, n≥1, c=A^n+B^n, R=rad(A^nB^nc), ε>0, and γ=ε/(1+ε). Use the previously audited exceptional birth primes and occupied orders E_n, with D_n=Σ_{d∈E_n}φ(d). Let P_n be the largest exceptional odd prime, with P_n=1 if none exists. Define K_n=#{d|2n:d∤n}.

The new claims are the exact count K_n=τ(oddpart(n)); D_n≤K_n(Y−1) if all exceptional primes are at most Y≥1; the uniform eventual ABC conclusion under p≤n^{1−δ}, with fixed 0<δ<1; the stated necessary prime escape when T_n=γn−1−log_2(n)≥0; and the large-order birth-mass escape inequality.

**Primary verdict: proved as written**, for the frozen final revision. The cutoff and weighted statements are uniform restricted consequences of the degree-budget theorem. They do not establish the prime cutoff or exclude the resulting large-order obstruction unconditionally.

## Dependency graph and obligation matrix

| Obligation | Status | Dependency or evidence |
|---|---|---|
| Exact allowed-conductor count | Passed | n=2^s m, m odd, and d=2^{s+1}t with t|m. |
| Degree bound from a prime cutoff | Passed | Each occupied order has a witness prime and φ(d)≤d≤p−1. |
| Y≥1 and empty-exception cases | Passed | Explicit final restriction and P_n=1 convention. |
| Elementary divisor estimate | Passed | Finite small-prime constants and a+1≤2^a; no analytic input. |
| Uniform eventual near-linear cutoff | Passed | η=δ/2 gives D_n/n=O_δ(n^{−δ/2}), uniformly in the bases. |
| Strict escape and existence | Passed | Final source includes T_n≥0 before asserting an exceptional prime exists. |
| Low-order packet allocation | Passed | Same prime-by-prime divisibility as audited ORDER_BUDGET.md, restricted to d≤Z. |
| Uniform o(log c) errors | Passed | Explicit ratios below, valid for unbounded A,B. |
| Weighted high-order escape | Passed | Strict quality identity, followed by subtraction of controlled low-order and ordinary factors. |
| Universal exclusion of high-order contacts | Not addressed | This remains unproved. |
| Unrestricted ABC | Not addressed | The theorem assumes a restricted exceptional-prime regime. |

The degree-budget input was independently audited in `order_budget.md`; its final mathematical source hash is pinned below. This report reconstructs every new deduction.

## Exact count and prime cutoff

Writing n=2^s m with m odd, a divisor of 2n that does not divide n must have 2-adic exponent exactly s+1. Thus all allowed conductors are precisely 2^{s+1}t for t|m, giving

K_n=τ(m)=τ(2n)−τ(n)≥1.

For each occupied order d, choose any exceptional witness prime p. Multiplicative order gives d|p−1, hence φ(d)≤d≤p−1. If all such primes satisfy p≤Y, then each occupied channel costs at most Y−1, and there are at most K_n of them. Therefore

D_n≤K_n(Y−1)≤τ(2n)(Y−1).

The restriction Y≥1 is necessary for this displayed form: if Y<1 and the exception set is empty, its right side would be negative. The final source includes Y≥1. If E_n is empty, D_n=0 and the inequality holds; choosing Y=P_n=1 makes the right side zero as well. No count of primes inside a single channel is needed.

Substituting this bound into the already audited sufficient threshold proves the displayed exact criterion (4).

## Divisor estimate and uniform near-linear theorem

For each η>0 and prime p≥2^{1/η}, the inequality a+1≤2^a implies a+1≤p^{ηa} for all a≥1, with the a=0 case immediate. For each of the finitely many smaller primes, the supremum C_{p,η}=sup_{a≥0}(a+1)/p^{ηa} is finite and at least 1. Multiplying gives τ(r)≤C_ηr^η for every r≥1, including r=1. This proves the source's elementary estimate in its stated uniform form.

With 0<δ<1, Y=n^{1−δ}≥1. Choosing η=δ/2 gives

D_n≤C_δ n^{1−δ/2},

where the harmless factor 2^{δ/2} is absorbed into C_δ. Consequently

[1+log_2(n)+2D_n]/n
 ≤[1+log_2(n)]/n+2C_δn^{−δ/2}→0.

All bounds depend on n and δ alone, not on A or B. Thus for each ε,δ there is a uniform N_{ε,δ} after which the degree criterion applies to every base pair satisfying the prime cutoff. No exchange of an A,B-dependent threshold for a uniform one occurs.

The user's broader formulation with any fixed δ>0 also has a trivial additional case: if δ≥1 and n>1, then n^{1−δ}≤1, so the assumed cutoff permits no exceptional odd primes. Then D_n=0 and the degree criterion holds for all sufficiently large n. The formal source states the nontrivial range 0<δ<1.

## Strict prime escape and the small-n boundary

Put T_n=γn−1−log_2(n). The audited degree escape gives D_n>T_n/2 under c>R^{1+ε}. If T_n≥0, this forces D_n>0 and hence an exceptional odd prime exists. Since D_n≤K_n(P_n−1),

P_n>1+T_n/(2K_n).

The strict sign and added 1 are correct. Since K_n is subpolynomial and T_n/n→γ, this is a necessary near-linear prime scale for sufficiently large n.

The final source correctly separates existence from a numerical inequality using the sentinel P_n=1. At T_n<0, a quality violation need not have any odd exceptional prime. Its explicit control A=63,B=1,n=1 gives c=64, R=42, and

64^{10}=1152921504606846976
 >717368321110468608=42^{11}.

Thus c>R^{1.1}, while c has no odd prime divisor at all. This checks the need for the existence restriction. The original exact escape statement interpreted purely with P_n=1 would be a weak numerical necessary condition when T_n<0; it would not assert an actual prime. The final source's T_n≥0 formulation makes the stronger existence reading unambiguous.

## Uniform weighted escape

For Z≥1, restrict the exceptional packet to actual orders d≤Z. The same exact allocation into Φ_d(A,B) gives

log W_{order≤Z}
 ≤Σ_{occupied d≤Z}φ(d)log(A+B)
 ≤K_nZ log(A+B).

Taking Z=n^{1−δ}, with fixed 0<δ<1, and applying the divisor estimate with η=δ/2 gives

log W_{order≤Z}≤C_δ n^{1−δ/2}log(A+B).

Since log(A+B)≤2log A and log c≥n log A, its ratio to log c is at most 2C_δn^{−δ/2}. Independently,

log(B_2G_n)/log c
 ≤1/n+log n/(n log 2).

Both bounds tend to zero uniformly for every admissible pair A,B. In particular, their sum is at most γ/2 for all sufficiently large n depending only on ε,δ.

Coprimality gives the exact identity R=rad(AB)c/U(c), and U(c)=B_2G_nW_n. A strict quality violation therefore implies

log W_n>γlog c+log rad(AB)−log(B_2G_n).

Subtracting the low-order packet and using the uniform combined error bound proves

log W_{order>n^{1−δ}}
 >(γ/2)log c+log rad(AB).

This is exactly (9), including its strict sign and the retained radical term. Every prime in that packet has d_p>n^{1−δ} and p≥d_p+1, so it lies above n^{1−δ}+1. The statement concerns logarithmic birth-depth mass, not merely a count or existence of primes.

## Remaining gap and scope

The new result improves the admissible restricted prime cutoff to every positive fixed power below n, uniformly as n→∞. It does not extend that conclusion to all base pairs without the cutoff, nor to arbitrary primitive triples represented only with n=1. Ordinary primes need no size restriction because their valuation contribution was already absorbed into G_n|n.

Neither the divisor estimate nor the occupied-channel count bounds birth depths in large-order channels. The weighted escape accurately locates a necessary obstruction; it supplies no contradiction to its existence. Thus no unconditional ABC conclusion follows.

No new finite enumeration was necessary. The only additional arithmetic check above was the discriminating exact small-n boundary, evaluated with integer powers. No original files were changed by this auditor.

## Provenance and final input revision

Independent subagent proof audit from the degree-budget definitions and raw cutoff statements. A second isolated subagent checked the channel count, parameter range and uniform asymptotic reasoning; its weighted check assumed the previously audited birth allocation. Shared-model review is not formal verification. No external theorem, analytic prime-counting input or Lean compilation was needed.

Final source hashes:

- ORDER_CUTOFF_COROLLARY.md: `00956ab9aa67b7e97482bbe7fa27e847848ebd5175bf3302ea70631cfbbb53c6`
- ORDER_BUDGET.md: `46679caa7dedefda2557b48f16e3de0f375b8e4e2b03651694a6001d8837f0ea`

The author applied the forced empty-exception prose correction and made the escape-existence boundary explicit before this final source was pinned. No mathematical theorem or verifier in the preceding frozen notes was altered.

Audit date: 2026-10-25. Self-proofreading covered the full report; no unresolved mathematical notation or syntax issue remained.
