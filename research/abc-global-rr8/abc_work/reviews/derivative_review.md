# Independent audit: arithmetic-derivative route

**Normalized claim.** For each integer b>1, put c=b+1 and use integer coordinates z_p supported on the prime divisors of bc. Define

D_z(n)=Σ_{p|n} v_p(n)(n/p)z_p,
K={z:D_z(b)=D_z(c)}, and W(z)=D_z(b).

The elementary claims are that W(K)=L Z for L=lcm(G(b),G(c)), where G(n)=gcd_{p|n}(v_p(n)n/p); that U(b)U(c)|L for U(n)=n/rad(n); and that every nondegenerate z in K has

||z||∞ ≥ max{L/S(b),L/S(c)},  S(n)=Σ_{p|n}v_p(n)n/p.

The four table entries are also claimed as exact integer minima.

**Primary verdict: proved as written**, for these elementary claims and four finite comparisons. This verdict does not certify full ABC, an eventual small-derivative theorem, or a general impossibility result for lattice projection methods.

## Dependency graph

- Integer linear-map image = coefficient gcd times Z (Bézout; internal elementary argument).
- gcd(b,c)=1 ⇒ disjoint prime-coordinate sets ⇒ the attainable common derivatives are the intersection G(b)Z∩G(c)Z=LZ.
- Every derivative coefficient is divisible by U(n) (prime-factor calculation), and gcd(U(b),U(c))=1 ⇒ U(b)U(c)|L.
- The triangle inequality |D_z(n)|≤||z||∞S(n), together with 0≠W∈LZ, gives the norm obstruction.
- Exact linear equations for the four examples ⇒ the stated shortest and nondegenerate minima; exhaustive cube computation supplies an independent finite consistency check.
- Pasten's stated source results supply context, not a missing premise for the elementary proof.

No circular dependency or unchecked mathematical leaf is needed for the elementary claims.

## Obligation matrix

| Obligation | Status | Evidence |
|---|---|---|
| Domain and support | Passed | Finite integer coordinate set p|bc; outside coordinates are fixed to zero. This restriction is necessary for the shortest-vector claims. |
| Image of D_z(n) | Passed | Bézout applied to the positive integer coefficients. |
| Image of W on K | Passed | Both common-derivative inclusions proved below; disjoint coordinates allow independent choices. |
| Radical divisibility | Passed | v_p(n)n/p=U(n)v_p(n)rad(n)/p. |
| Norm obstruction | Passed | Integer nonzero image implies |W|≥L, followed by the triangle inequality on each side. |
| Four exact minima | Passed | Exact parameterizations and attaining witnesses below. |
| Original verifier coverage | Passed | It enumerates all integer x,y in a complete cube and solves uniquely for z, retaining |z|≤cap; every smaller cube is included. |
| Source exponent dependencies | Passed | Independent source subcheck of official v3 PDF; page locators below. |
| Uniform asymptotic upper bound | Not addressed | Neither the image theorem nor these finite examples supplies one. |
| Full every-epsilon ABC | Not addressed | Remains outside the proved claims. |

## Derivation from the raw definitions

Write A_p=v_p(b)b/p and C_q=v_q(c)c/q. The maps on the b and c coordinates have respective images G(b)Z and G(c)Z. If z∈K, its common derivative belongs to both groups, so W(z)∈LZ. Conversely, for every integer k, the integer Lk is divisible by both gcds. Bézout gives integer b-side coordinates realizing Lk and integer c-side coordinates realizing Lk. The two coordinate sets are disjoint, so combining them gives z∈K with W(z)=Lk. Thus W(K)=LZ, with no claim about the size of a Bézout lift.

For each p|n,

v_p(n)n/p = U(n)·v_p(n)·rad(n)/p.

Therefore U(n)|G(n). Since b and c are coprime, U(b) and U(c) are coprime, and their product divides lcm(G(b),G(c)). As rad(bc)=rad(b)rad(c), this product is bc/rad(bc). Finally, if W≠0 and B=||z||∞, then

L≤|W|=|D_z(b)|≤B S(b), and L≤|W|=|D_z(c)|≤B S(c).

This proves the asserted lower bound; taking ceilings can express its integer consequence. It does not yield an upper bound.

## Four examples, proved exactly

Coordinates below are ordered as the two prime divisors of b followed by the prime divisor of c. Heights are maximum absolute coordinates.

| b,c | Integer equation | Parameter restriction | Shortest nonzero witness and height | Nondegenerate witness and minimum height | Minimum absolute W |
|---|---|---|---|---|---:|
| 36,37 | 36x+24y=z | z=12(3x+2y) | (2,−3,0), height 3 | (1,−1,12), height 12 | 12 |
| 48,49 | 96x+16y=14z | z=8k; 6x+y=7k | (1,−6,0), height 6 | (1,1,8), height 8 | 112 |
| 80,81 | 160x+16y=108z | z=4k; 10x+y=27k | (3,−3,4), height 4 | (3,−3,4), height 4 | 432 |
| 108,109 | 108x+108y=z | z=108(x+y) | (1,−1,0), height 1 | (1,0,108), height 108 | 108 |

For 36/37, a nonzero z has |z|≥12. If z=0, then (x,y)=(2t,−3t), so every nonzero degenerate vector has height at least 3. The displayed witnesses attain both bounds.

For 48/49, dividing the equation by 2 and reducing modulo 8 gives 8|z. Thus nondegenerate height is at least 8. If z=0, then y=−6x, whose shortest nonzero vector has height 6. The witnesses attain both bounds.

For 80/81, reducing 40x+4y=27z modulo 4 gives 4|z, so nondegenerate height is at least 4. If z=0, then y=−10x and a nonzero degenerate vector has height at least 10. Consequently every nonzero vector has height at least 4; (3,−3,4) attains it.

For 108/109, nondegeneracy is x+y≠0 and forces |z|≥108. Degenerate vectors satisfy y=−x, with nonzero minimum height 1. Both bounds are attained.

The displayed nondegenerate witnesses also attain the predicted minimum |W|. In 48/49 both b and c are composite. Thus this example lies outside the {1,N,q} prime exception and disproves the exact finite assertions “a shortest nonzero additivity vector always has nonzero W” and “every such triple has a nondegenerate vector of height ≤√c.” Here √49=7<8. It does not disprove any eventual bound with an unspecified constant or exponent.

## Computation and source checks

I inspected the original verify.py without executing its output-writing entry point, so no original results file was altered. Its cube coverage is correct for its four cases: x,y are completely enumerated; the equation determines the sole candidate z; and the remaining coordinate bound is enforced. The table's minimal-|W| entries are computed by the gcd/lcm formula, whose independent proof is given above.

An independent Python integer enumeration used coefficient rows (36,24,1), (96,16,14), (160,16,108), (108,108,1), with caps 12,8,4,108. It found respectively:

- shortest heights: 3,6,4,1;
- nondegenerate heights: 12,8,4,108;
- minimum nonzero |W| inside those cubes: 12,112,432,108;
- nonzero solution counts inside those cubes: 24,8,2,648.

The analytic lower bounds make these global minima, so no extrapolation from a finite scan is needed.

An additional isolated agent checked the official [Pasten v3 PDF](https://arxiv.org/pdf/2106.16165v3) directly. Theorem 2.6 (PDF p. 5) provides the quoted product bound for r=ω(abc)−1 independent derivations when c>2. Theorem 3.3 (p. 6) has the quoted radical/norm inequality with coprimality, c>2, additivity, and nonzero Wronskian. Conjecture 3.9 (p. 7) is eventual, excludes the indicated prime family, and uses 0<η<1 and strict ||ψ||<c^η. Lemma 4.1 (p. 9) gives M>1/(1−η), while Theorem 4.5 (p. 11) assumes 1<M<2 and gives η>1−(2−M)/(4M). These agree with the route's exponent caution. The source's Conjecture 3.2 is printed without a multiplicative constant; absorbing finitely many exceptional triples directly gives a constant version, and eliminating that constant may require increasing the exponent. This normalization does not affect the route's elementary claims or its caution that a single η<1 does not establish every-epsilon ABC.

## Exact remaining gap and strongest safe statement

The image theorem gives the exact quotient of attainable W values and a lower bound for the coordinate cost of a nonzero W. It supplies no uniform upper bound for the smallest nondegenerate coordinate norm as b varies. The four examples show failure of two specific finite universal assertions, not a no-go theorem for all projection/lifting arguments. Accordingly, the route's phrase closing the “projection-only construction” is supported only to the extent it refers to those naive automatic-shortest-vector and exact √c assertions.

A general lift estimate, with its exact constants, exceptions, quantifiers and exponent implication, is the missing research input. Any subsequent claim of progress toward full ABC must derive the required every-epsilon radical estimate, not only a fixed exponent.

## Provenance and exact inputs

Independent subagent audit, deriving the image, obstruction and examples from the raw definitions. The source check was delegated to a separate isolated subagent, which read the official PDF. Shared-model review and finite enumeration are not formal verification. No Lean compilation was performed. This auditor read original artifacts without modifying them. An ancillary results.json rerun occurred concurrently; its values were inspected and agree with the claims. The mathematical statement and verifier hashes remained unchanged.

SHA-256 inputs audited:

- DERIVATIVE_ROUTE.md: `35e91745cb52bb9019dd4b9a5dd22ce043327737af83d856d37a7d5a54abe44d`
- verify.py: `b81405e56215ec3182936d7cd29bc6bda8c8ac90f660255346b5572f755338a5`
- results.json (initial observation): `5cd2bc12b25f41380f7304c255cfde20b4a3f0764d637185597a0e8356117bb3`
- results.json (later inspected rerun): `ebac35b5258005ae8232cd8d7276d72bc371387ec038062a588bb511389a7a1c`
- SHA256SUMS.json: `76ef2aab7c6dcfba76b31512a1dc643c3539f375b7e44790bf623b69ba99dd85`

Audited on 2026-10-25. Report scope is the derivative route above; other routes and the base archive were not audited here.

Self-proofreading of this report: corrected the table header formatting; no mathematical-token corrections or unresolved notation issues.
