# Independent audit: the first multiplicative dilation comparison

## Normalized claim and verdict

**Primary verdict: proved as written** for the elementary candidate in the pinned input. The power presentation is an exact semiring with transported addition; its ordinary-addition comparison has the displayed positive defect. Protecting the first two coordinates uniquely determines the ordinary additive repair, whose declared logarithmic cost is not uniformly sublinear in the original height for any fixed integer \(s\ge2\). The parity and odd-quotient gcd identities are correct.

The quantified domain is a fixed integer \(s\ge2\) and every positive primitive integer triple \(a+b=c\). Here primitivity gives \(\gcd(a,b)=\gcd(a,c)=\gcd(b,c)=1\). The transported semiring is the set \(I_s=\{n^s:n\in\mathbb Z_{\ge0}\}\), with ordinary multiplication and addition

\[
x+_s y=(x^{1/s}+y^{1/s})^s.
\]

The roots are the unique nonnegative integer roots, as stated. No power map on arbitrary integers, preservation of ordinary addition, or model of a full IUT link is claimed. The costs are explicit choices in the note; this review does not infer an independently meaningful conductor cost from them.

## Dependency graph

1. The power map is a bijection \(\mathbb Z_{\ge0}\to I_s\), and \((mn)^s=m^sn^s\). Transport of addition therefore produces the declared semiring, including its zero and unit.
2. Substituting \(c=a+b\) into the ordinary binomial expansion gives the positive defect \(D_s\). Distinct prime support is invariant under positive powers.
3. With \(a^s,b^s\) protected, ordinary additivity fixes the third coordinate \(c_s=a^s+b^s\); ordinary primitivity follows from \(\gcd(a,b)=1\).
4. The primitive family \((1,t,t+1)\), \(t\ge1\), bounds that exact defect between two fixed positive multiples of \(t^{s-1}\), proving the cost ratio limit at fixed \(s\).
5. Reduction modulo \(c\), followed by multiplication by the unit \(a^s\) or \(a^{s-1}\), gives the parity and gcd identities. The odd factorization is an ordinary polynomial identity.

All leaves are elementary algebra or integer arithmetic. No external theorem, computation, or separate route is load-bearing, and there is no circular dependency.

## Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Power presentation has the stated source and target | Passed | Each element of \(I_s\) has a unique nonnegative root; its multiplication is closed and agrees with transported multiplication. |
| Semiring identities, zero, and unit | Passed | The bijection transports the ordinary laws; zero and unit are \(0^s=0\) and \(1^s=1\). |
| Transported additive relation | Passed | Roots of \(a^s,b^s\) are exactly \(a,b\), so their transported sum is \((a+b)^s=c^s\). |
| Ordinary comparison defect and its sign | Passed | The mixed binomial terms are positive for \(a,b>0\), \(s\ge2\). |
| Special defects \(D_2,D_3\) | Passed | \(D_2=2ab\); \(D_3=3ab(a+b)=3abc\). |
| Radical and output height before repair | Passed | Raising positive integer coordinates to \(s\) preserves their prime support and multiplies the largest coordinate's logarithm by \(s\). |
| Unique protected ordinary repair | Passed | Only the third coordinate is free, and its ordinary additive value is forced to be \(a^s+b^s\). |
| Repair stays positive and primitive | Passed | \(a^s,b^s>0\) and \(\gcd(a^s,b^s)=1\); the sum makes all coordinate pairs coprime. |
| Fixed-\(s\) cost lower and upper bounds | Passed | The leading mixed term is \(st^{s-1}\); every remaining power is at most \(t^{s-1}\) for \(t\ge1\). |
| Cost asymptotic and its quantifiers | Passed | The constants may depend on fixed \(s\); \(\log(1+D_s)=(s-1)\log t+O_s(1)\) and \(\log(t+1)/\log t\to1\). No uniform-in-\(s\) estimate is inferred. |
| Even parity gcd identity | Passed | \(c_s\equiv2a^s\pmod c\) and \(a\) is a unit modulo \(c\). |
| Odd divisibility and quotient factorization | Passed | For odd \(s\), \(a+b\) divides \(a^s+b^s\); the displayed alternating polynomial is the quotient. |
| Odd quotient congruence and exact gcd | Passed | Every quotient summand becomes \(a^{s-1}\pmod c\), so \(Q_s\equiv s a^{s-1}\pmod c\); the unit factor gives \(\gcd(c,Q_s)=\gcd(c,s)\), including prime multiplicities. |
| Radical after repair | Passed | It is \(\operatorname{rad}(ab c_s)\), since the first two coordinate powers add no support. No preservation of the old radical after repair is asserted. |
| ABC, useful radical-controlled cost, or a full IUT comparison | Out of scope | These are expressly not established by the candidate. |

## Decisive derivations and boundary cases

The original map is multiplicative in the ordinary sense, but its additive codomain law has been changed explicitly. This is not an illicit transfer of ordinary additivity. Its residual in the ordinary target is exactly

\[
(a+b)^s-a^s-b^s
=\sum_{k=1}^{s-1}\binom sk a^k b^{s-k}>0.
\]

Thus the powered coordinates are not ordinary additive ABC triples. Protecting \(a^s,b^s\) forces the unique correction \((0,0,-D_s)\) to the third coordinate. Its absolute correction size is \(D_s\), in agreement with the note's declared norm, and the repaired triple is an actual positive primitive ordinary additive triple.

For \(a=1,b=t,c=t+1\), \(t\ge1\), the \(k=1\) term gives the lower bound \(st^{s-1}\). Since \(1\le s-k\le s-1\), every mixed power satisfies \(t^{s-k}\le t^{s-1}\). The mixed coefficients sum to \(2^s-2\), giving

\[
st^{s-1}\le D_s\le(2^s-2)t^{s-1}.
\]

For each fixed \(s\), taking logarithms after adding one proves the stated ratio limit \(s-1>0\). This single primitive family therefore excludes a uniform \(o(\log c)\) upper bound for this declared repair cost across all input triples. The claim concerns this chosen correction and norm; it supplies neither a lower bound for all possible comparison mechanisms nor a radical-to-height inequality.

For the gcd identities, \(b\equiv-a\pmod c\) implies

\[
c_s=a^s+b^s\equiv(1+(-1)^s)a^s\pmod c.
\]

The factor \(a^s\) is coprime to \(c\). This proves \(\gcd(c,c_s)=\gcd(c,2)\) for even \(s\) and \(c\mid c_s\) for odd \(s\). In the latter case the alternating quotient is positive because it equals the quotient of positive integers. Reducing its \(k\)-th summand modulo \(c\) gives

\[
(-1)^ka^{s-1-k}b^k
\equiv(-1)^ka^{s-1-k}(-a)^k=a^{s-1}.
\]

There are exactly \(s\) terms. Therefore the quotient congruence and exact gcd with \(s\) follow, without discarding valuations or confusing a gcd equality with a mere support assertion.

The smallest positive input \((a,b,c)=(1,1,2)\) checks the repeated-coordinate boundary. For \(s=2\), \(D_2=2\), \(c_2=2\), and \(\gcd(2,c_2)=2\). For \(s=3\), \(D_3=6\), \(c_3=2\), \(Q_3=1\), and \(\gcd(2,Q_3)=1=\gcd(2,3)\). At the family endpoint \(t=1\), the upper defect bound is an equality, while the lower bound remains valid, including the equality of both bounds for \(s=2\).

Two direct examples verify the need to recompute the radical. For \((1,2,3)\), \(s=2\) repairs to \((1,4,5)\): the old radical is \(6\), the repaired radical is \(10\), and the old odd prime \(3\) is lost. For \((1,3,4)\), \(s=3\) repairs to \((1,27,28)\), with \(Q_3=7\): the radical changes from \(6\) to \(42\), while \(\gcd(4,7)=\gcd(4,3)=1\). These calculations are illustrations checked directly, not an exhaustive computation or evidence replacing the universal derivations.

## Remaining gap and strongest safe conclusion

There is no missing implication in the stated elementary comparison package. It proves that this exact transported power presentation yields a nonzero ordinary-addition residual, and that the uniquely protected ordinary repair has a leading logarithmic cost of the same order as the formal height increment on an explicit primitive family. The parity identities correctly describe how the old third coordinate interacts with the repaired one.

The comparison does not establish an independently useful bound on the repaired radical or a radical-controlled correction cost. An arithmetic comparison with those properties remains a new obligation. No ABC counterexample or assertion about a full IUT link follows. The cheapest next meaningful check is to specify a different candidate's source, target, protected data, actual residual, and independently motivated cost before testing a uniform arithmetic bound; no further finite sampling is needed to settle this candidate's stated cost obstruction.

## Input, checks, and review provenance

Independent delegated proof audit completed 2026-10-25. The exact input was `abc_work/komorebi_arithmetic/FIRST_COMPARISON.md`, SHA-256:

`c75896f1cd724e47f03958b023f1ea89424ee96c57f17dbef5db6e7af3f78523`.

The source was read raw and with numbered lines; `sha256sum` pinned it before and after the review. No separate outcome report, other review, or unprovided IUT model was used. The previous two completed review files were not edited. The supplied RR6 archive SHA-256 `026d1f544ba86acc3fd9d63b75b4a8fc73595407f67e15f1b9b7f7e5144d993a` is recorded provenance rather than an independently authenticated source input.

The proof-audit skill and relevant logic, typing, coefficient-domain, and computation checklists were applied. There is no load-bearing external source requiring an additional literature check. No finite search, numerical approximation, formal verification, or Lean compilation was performed or is claimed. The proof was not edited. The reviewer received the raw scope without a preferred verdict and reconstructed the algebra, quantifiers, and domains directly.
