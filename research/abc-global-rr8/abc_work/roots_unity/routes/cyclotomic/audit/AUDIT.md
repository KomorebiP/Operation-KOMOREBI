# Independent audit: cyclotomic filtering and primitive depth

**Primary verdict: proved as written.** The exact resolvent, primitive-pole preservation, arbitrary exact-depth construction, and fixed-filter resultant dichotomy hold in the stated domains. They refute the specific proposed algebraic cancellation gain. They do not refute ABC, prove an impossibility theorem for roots-of-unity methods, or exclude arithmetic filters with additional height estimates.

Audited source: `../PROOF_NOTE.md`, SHA-256 `45b432db3661862d8e535bedf4bc9e4220f34b3fccd132d721fcb8096bd67564`.

## Claim card and scope

The resolvent assumes n>=1, A>B>=1 coprime, primitive zeta of order n and eta^n=-1, with 0<=k<n. The valuation statement assumes an odd p∤nAB and a chosen split realization of the roots, or the stated unramified root-separation extension. The exact-depth theorem fixes n and p congruent to 1 modulo 2n but varies A with the prescribed depth. The resultant theorem fixes both n and the integral coefficient polynomial P, assumes gcd(P(T,1),Phi_(2n)(T))=1, and evaluates at a primitive order-2n output prime. Its finite exceptional-prime set belongs to that fixed pair (n,P).

The illustrative moving-conductor filter P(T)=T−2 now correctly restricts n=2^s to s>=1, ensuring degree P<=n−1.

## Dependency graph and reconstructed argument

1. Character orthogonality gives sum_j zeta^((l-k)j)=n if l=k modulo n and zero otherwise. Summing the geometric series in B/A produces exactly n A^(n−1−k)(eta B)^k/(A^n+B^n). All exponents agree, including k=0, k=n−1 and n=1. Clearing denominators gives a polynomial identity, so the conclusion does not depend on p-adic convergence.
2. When p∤nAB, its numerator is a p-adic unit. Hence the resolvent has valuation exactly −v_p(A^n+B^n). In the split setting the n roots of T^n+1 are distinct modulo p because their derivative is nT^(n−1), a unit at each root. Exactly one root equals A/B modulo p. Therefore exactly one denominator is nonunit, all others are units, and the product identity puts the full output valuation in that branch. The same argument works at the stated unramified local prime with normalized v(p)=1.
3. For F(T)=T^n+B^n, gcd(A,F(A))=1. Thus gcd(F(A),F'(A))=gcd(F(A),n), as claimed. Derivative invertibility controls the uniqueness of a lifting branch; it does not prohibit high valuations of F(A).
4. For p=1 modulo 2n, choose r of order 2n in F_p^*. Then r^n=−1 and F'(r) is a unit. Among the p candidate next digits, the displayed first-order expansion yields exactly one that extends a root by one depth. Choosing any other digit after reaching depth e makes v_p(A^n+1)=e exactly. Adding a multiple of p^(e+1) ensures A>=2 without changing the valuation or the order modulo p. Since order 2n prohibits divisibility of every A^d−1 for d properly dividing 2n, all p-adic depth lies in Phi_(2n)(A). This proves the final cyclotomic claim, including n=1.
5. After multiplication by eta^(−k), the kth numerator is n A^(n−1−k)B^k. A fixed integral linear combination is therefore nP(A,B), with P homogeneous of degree n−1. For monic integral H=Phi_(2n), a nonzero resultant admits an integral Bezout identity R_P=UH+VP(T,1). At T=A/B, all denominators are p-adic units. Since H(A,B)=B^deg(H)H(A/B), and P(A,B)=B^(n−1)P(A/B,1), homogeneous scaling preserves both valuations. Thus min(v_p(H(A,B)),v_p(P(A,B)))<=v_p(R_P).
6. At a primitive order-2n output prime, the valuation in H(A,B) equals that in A^n+B^n, and p∤n. Consequently the canceled primitive packet divides |R_P|. In particular p∤R_P means no cancellation at that prime. When P is divisible by H, deleting the component from the observable is algebraic cancellation, but the original output and its unknown primitive factor retain their full value.
7. Because H is monic and all its complex roots have modulus one, |R_P| is the product of |P(z,1)| over those roots and is at most L^deg(H), where L is the sum of absolute coefficients. This argument remains valid when the actual univariate degree of P(T,1) is below n−1, since its homogenizing B factors are local units.
8. For n=2^s, s>=1, P(T)=T−2 has coefficient norm 3 and absolute resultant H(2)=2^n+1. Its homogeneous degree-(n−1) version is XY^(n−2)−2Y^(n−1). At (A,B)=(2,1), it vanishes, while its moving resultant contains the entire output. This confirms that a fixed coefficient norm does not make the resultant or its prime support fixed as n varies.

## Obligation matrix

| Obligation | Verdict | Decisive point |
|---|---|---|
| Fourier weights and exponents | Passed | Character orthogonality |
| n=1 endpoint | Passed | Resolvent 1/(A+B), H=T+1 |
| Unique nonunit branch | Passed | Simple roots modulo odd p∤n |
| Exact pole depth for every mode | Passed | Unit numerator in the rational identity |
| Exact prescribed-depth Hensel construction | Passed | Exactly one extending digit, p−1 terminating digits |
| Primitive cyclotomic component | Passed | Residue order 2n excludes every proper divisor |
| Homogeneous resultant evaluation | Passed | B is a local unit; integral Bezout identity |
| Canceled packet divides fixed resultant | Passed | Primewise minimum-valuation inequality |
| Coefficient-height budget | Passed | Product over unit-circle roots |
| Fixed n versus varying n | Passed | Source explicitly separates these quantifiers |
| Universal bound on primitive depth | Refuted in the asserted local scope | Arbitrary depths exist while n,p remain fixed and A varies |
| Roots-of-unity methods with new height input | Not addressed | Explicitly left open |
| ABC or ABC counterexamples | Out of scope | Varying A with depth supplies neither |

## Exact independent checks

`independent_check.py` uses exact Python integer arithmetic. Its order finder directly tries all d=1,...,p−1; its root lifter tests all digits rather than using the author's derivative-digit implementation. The run passed:

- 30 exact-depth constructions at depths 1,...,5 across (n,p)=(1,3),(2,5),(3,7),(5,11),(6,13),(8,17), including direct integer cyclotomic-value valuations.
- 17 coprime homogeneous input cases with exactly one depth-two branch, and all 74 Fourier modes after denominator clearing.
- 13,296 homogeneous linear-filter cases for n=2, all coprime 1<=B<A<=30 and nonzero coefficient pairs in [-3,3]^2. In each, gcd(A^2+B^2,uA+vB) divides u^2+v^2, independently checking the cancellation packet and the B-unit issue.

The initial independent fixture generator stopped at (n,p,B)=(1,3,2), because its one-block search found only a coprime candidate of depth three. This was a finite fixture-selection error, not a theorem counterexample. Extending the search across all B congruence classes preserved the required depth and coprimality; the completed run above then passed. The final code and `independent_results.json` retain the stated finite domain. Run from this directory with `python3 independent_check.py`.

These computations support only their finite assertions. The universal verdict rests on the reconstructed elementary argument. No Lean compilation or novelty investigation was performed.

## Remaining implication and safe interpretation

The failed implication is specifically: character cancellation, a unit discriminant, or coprime fixed-filter resultants automatically diminish a primitive denominator's p-adic depth without a corresponding arithmetic budget. The resolvent preserves that depth; coprime filters can pay for cancellation only through their resultants; and exact-depth lifting shows no conductor-only local cap.

This does not exclude a family of conductor-dependent filters with a new bound on the resultants actually used, nor a global comparison of simultaneous contacts and least representatives. Those are open continuation obligations. Calling the computation an ABC no-go theorem would overstate it.

Review provenance: fresh delegated audit of the raw argument, with an independent reconstruction and finite implementation. No source changes were made by this audit.
