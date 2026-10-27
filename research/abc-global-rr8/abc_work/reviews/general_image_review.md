# Independent audit of the general Wronskian image

**Normalized claim.** Let a,b be positive coprime integers, c=a+b, and (a,b)≠(1,1). For integer coordinates z_p supported on the prime divisors of abc, define

D_z(n)=Σ_{p|n}v_p(n)(n/p)z_p,
G(1)=0,
G(n)=gcd_{p|n}(v_p(n)n/p) for n>1.

Set A=G(a), B=G(b), C=G(c), g=gcd(A,B,C), and restrict to D_z(a)+D_z(b)=D_z(c). The claim is that W=aD_z(b)−bD_z(a) has exact image LZ, where

L=gcd(cAB,bAC,aBC)/g.

With rad(1)=1, R=rad(abc), P=abc/R, and H=max_{p|abc}|z_p|, the further claims are that J=L/P is a positive integer and that every W≠0 satisfies

cJ ≤ RH log(c)/log(2).

The extension proposes an explicitly conditional sufficient bound H/J ≪_δ c^δ, for every δ>0, for full ABC.

**Primary verdict: proved as written**, for the exact image, positivity on the stated domain, divisibility, pointwise inequality, and conditional sufficiency claim. The phrase “explicitly handled family” must mean a family already satisfying the desired ABC conclusion with a uniform constant; a mere list or classification of infinite exceptions does not suffice. No unconditional H/J upper bound or full ABC theorem is proved.

## Dependency graph and obligation matrix

| Obligation | Status | Dependency or evidence |
|---|---|---|
| Pairwise disjoint prime supports | Passed | Coprimality of a,b and c=a+b. |
| Independent derivative-value images | Passed | Bézout on each nonempty support; for n=1 the image is 0Z. |
| Formula L=gcd(minors)/g | Passed | Primitive row reduction over Z; proof reconstructed below. |
| Zero coordinates and boundary cases | Passed | Dummy coordinate when A=0 or B=0 is harmless; excluded boundary has image {0}. |
| Positive integral L | Passed | g>0, divisibility by g, and one displayed minor nonzero. |
| P divides every W | Passed | Three equivalent W expressions and pairwise coprimality of U(a),U(b),U(c). |
| J positive integral | Passed | The image contains W=L, so P divides L. |
| Coordinate-norm inequality | Passed | Triangle inequality and p log(p)≥2 log(2). |
| H/J sufficiency quantifiers | Passed | Explicit δ(ε), uniform constant and exception handling below. |
| Uniform existence of small lifts | Not addressed | This remains a substantive unproved arithmetic hypothesis. |
| Full ABC unconditionally | Not addressed | No bound on H/J is established. |

All exact theorem dependencies are elementary integer arithmetic. No external literature or finite experiment is load-bearing.

## Independent derivation of the image

The three prime supports are pairwise disjoint. The possible derivative values are independently x∈AZ, y∈BZ, and t∈CZ. Thus the problem reduces exactly to the integer triples (u,v,w) with

Au+Bv−Cw=0,
W=−bAu+aBv.

If a=1, then A=0: allowing a dummy integer u does not add derivative values or W values. The same applies to B=0. On the admitted domain C>0 and g>0.

Let r=(A,B,−C), s=(−bA,aB,0). Integer Euclidean column operations yield U∈GL_3(Z) with rU=(g,0,0). Write sU=(t,h,k). Under this bijective integer coordinate change, the kernel is precisely the vectors whose first coordinate is zero, so the W image is gcd(h,k)Z.

The content (gcd of all entries) of the exterior product r∧s is unchanged by U, since the induced map on second exterior powers is an invertible integer matrix. Its content after reduction is g·gcd(h,k). Computing before reduction gives the three minors

cAB, −bAC, aBC.

Consequently the image generator is exactly their nonnegative gcd divided by g. This also proves integrality, rather than merely suggesting a rational formula.

If a>1, then A,C>0 and bAC>0. If b>1, then B,C>0 and aBC>0. At least one case holds, so the numerator gcd and L are positive. In particular a nondegenerate integer derivation exists for each admitted primitive triple, with no bound on its prime-coordinate size supplied by this argument.

## Boundary and discriminating checks

- If a=1 and b>1, then A=0, g=gcd(B,C), and L=BC/g=lcm(B,C). This recovers the previously audited slice exactly.
- If b=1 and a>1, then B=0 and L=AC/gcd(A,C).
- For (a,b,c)=(1,1,2), one has (A,B,C)=(0,0,1), g=1, and the formula gives L=0. Additivity forces D_z(2)=z_2=0, hence W=0. The image formula still reads 0Z, but the positive-generator and nondegenerate-existence conclusions fail. The stated exclusion handles this precisely.
- For the interior triple 9+16=25, (A,B,C,g)=(6,32,10,2). The minor gcd is gcd(4800,960,2880)=960, so L=480. Directly, additivity is 3u+16v=5w, implying u≡3v modulo 5. Write u=3v+5k; then W=−96u+288v=−480k. Every k is possible since w=5v+3k. Thus the image is exactly 480Z. This test detects omission of the denominator g. Here P=120 and J=4.

These are exact calculations, not empirical evidence for the universal formula.

## Divisibility and the strengthened inequality

Put U(n)=n/rad(n), with U(1)=1. Each derivative coefficient is a multiple of U(n), so U(n)|D_z(n). Additivity gives

W=aD_z(b)−bD_z(a)
 =aD_z(c)−cD_z(a)
 =cD_z(b)−bD_z(c).

The first form shows divisibility by U(a) and U(b), and either appropriate remaining form gives U(c)|W. These three integers are pairwise coprime; therefore P=U(a)U(b)U(c)=abc/R divides W. Since the exact image contains W=L, P|L. Hence J is a positive integer.

For every prime-coordinate vector,

|W| ≤ abH Σ_{p|ab}v_p(ab)/p.

For each prime p, 1/p ≤ log(p)/(2log(2)), because p log(p)≥2log(2). Thus

Σ_{p|ab}v_p(ab)/p ≤ log(ab)/(2log(2)) ≤ log(c)/log(2),

where the last step uses ab≤c². A nonzero W belongs to LZ, so |W|≥L=PJ. Dividing by ab yields exactly

cJ ≤ RH log(c)/log(2).

The inequality is valid for every admitted nondegenerate additive derivation. If W=kL, the same proof yields the stronger c|k|J ≤ RH log(c)/log(2). No choice W=L is needed for the stated inequality.

## Precise sufficiency quantifiers

A fully explicit sufficient hypothesis is the following. Let E be a family of primitive triples for which, for every ε>0, a uniform constant C_{ε,E} already satisfies c≤C_{ε,E}R^{1+ε}. Suppose that for every δ>0 there exist a constant K_δ and a finite set F_δ such that every admitted primitive triple outside E∪F_δ has some integer additive derivation with W≠0 and

H/J ≤ K_δ c^δ.

The constants must be independent of the triple. The existence quantifier allows choosing a different derivation for every triple and δ. No compatibility between those choices is needed.

For a target ε>0, take δ=ε/[2(1+ε)]. Since log(c)≤c^δ/(eδ), the pointwise inequality gives

c^{1−2δ} ≤ [K_δ/(eδ log(2))] R.

Because 1/(1−2δ)=1+ε, this implies

c ≤ [K_δ/(eδ log(2))]^{1+ε} R^{1+ε}.

Take the maximum with the separately established constant on E and the finitely many ratios c/R^{1+ε} for F_δ and the excluded boundary triple. This is full ABC with a constant depending on ε. An exception family depending on δ is also permissible if its required ε-bound is separately uniform. An arbitrary infinite “handled” family cannot simply be discarded.

Requiring a lift of the image generator W=L is sufficient but stronger than necessary. Any nonzero W with the stated H/J bound suffices. The terminology “integral section norm” should therefore not be used to imply that a generator lift is necessary or that its minimum norm equals the minimum among all nondegenerate lifts; neither equality is asserted or proved by the image theorem.

## Exact remaining gap

No uniform upper bound for H/J is established. The image computation proves only that W=L is attainable by some integer prime-coordinate vector. Bézout lifts can have large coordinates, and the image generator does not control their size. Conversely, a small coordinate vector can have W=0.

The strongest unconditional safe result is the exact image formula and the pointwise inequality for any given nondegenerate derivation. The proposed every-δ upper bound is a new arithmetic hypothesis, sufficient for every-ε ABC under the uniform exception conditions above. A bound at one fixed δ alone does not establish the requested every-ε conclusion.

## Review provenance and exact revision

Independent subagent review from the raw D_z definitions, including exact boundary and interior checks. A second isolated subagent independently checked the H/J sufficiency calculation and quantifier conditions, assuming the pointwise inequality. Shared-model review is not formal verification. No finite enumeration or external source was needed, and no Lean compilation was performed. No original file was changed.

Audited input: `abc_work/routes/derivative/GENERAL_IMAGE.md`.

SHA-256: `019b8d2ac3a6cf78b04909706f57154ee0db9a1cbab5a8fae844126059bd1437`.

Audit date: 2026-10-25. This report supplements, and does not replace, the earlier derivative-route audit.

Self-proofreading: full report checked for notation and display consistency; no mathematical-token corrections or unresolved notation issues.
