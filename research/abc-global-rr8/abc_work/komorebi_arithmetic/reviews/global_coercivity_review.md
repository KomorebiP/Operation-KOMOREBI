# Independent audit: global coercivity and arithmetic stopping

## Normalized claim and verdict

**Primary verdict: proved as written** for the local theorem package in the pinned proof: the joint-coercivity equivalence and explicit estimate, the functional factorization criterion and transfer bound, failure of the specified real-exponent surrogate, the one-sided approximation lemma and fixed-radical integer near-exact family, failure of the stated bounded relative-residual proposal, and the strict integer stopping threshold.

The linear claims concern a real Hilbert space \(E\), real Banach defect and observable targets \(\mathcal R,Y\), bounded linear maps \(D:E\to\mathcal R\), \(P:E\to Y\), and \(L=\ker D\). They assume the stated finite transverse estimate

\[
\|x-P_Lx\|\le a\|Dx\|\qquad(x\in E).
\]

They do not identify \(P\) with a radical or a linear functional \(\ell\) with actual arithmetic height. For every specified finite \(B\ge0\), the functional claim uses the ordinary real-valued bounded linear functional convention: \(\ell:E\to\mathbb R\). This distinguishes the field from the earlier Banach space also denoted `R` in the ASCII note.

The integer negative result concerns **all positive primitive raw candidates**, with \(c\ge\max(a,b)\), rather than exact additive triples. It disproves the displayed universal relative-residual inequality on that domain. The real-exponent negative result concerns the declared continuous fixed-support relaxation. The stopping result concerns integer defect at an independently supplied bound on \(c\). None of these claims is an ABC theorem or an impossibility theorem for all arithmetic comparison mechanisms.

## Dependency graph

1. Boundedness of \(D\) makes \(L\) closed, so Hilbert orthogonal projection and decomposition are available. Closed range of \(D\), together with the bounded inverse theorem on \(L^\perp\to\operatorname{ran}D\), justifies the existence of the supplied transverse constant.
2. The decomposition \(x=u+v\), \(u\in L^\perp\), \(v\in L\), combines the transverse estimate with control of \(P|_L\). A Cauchy-sequence argument and the bounded inverse theorem identify that exact-locus control with injective closed range.
3. A functional estimate on \(L\) defines \(f(Pv)=\ell(v)\), with well-definedness furnished by the same estimate on differences. No completeness of \(P(L)\) is needed for this factorization. Closed range enters only in the later sufficiency of kernel annihilation.
4. Elementary differentiation and evaluation of the displayed exact real family establish the surrogate's failure, without using any arithmetic identification.
5. Pigeonhole approximation plus a one-sided conversion gives positive \(m_j,n_j\) with \(m_j\log2-n_j\log3\downarrow0\) in the sense of positive convergence, not necessarily monotone convergence. Unique prime factorization proves the required irrationality.
6. The resulting integer powers have fixed radical, unbounded height, and relative defect tending to zero. A modulo-eight argument excludes exact additivity eventually. This disproves the stated raw-candidate proposal.
7. The separate stopping implication uses only the fact that a nonzero integer defect has absolute value at least one.

There is no circular dependency. The arithmetic obstruction does not use the sibling integer-space route; that route provides context and an application domain for the stopping law. The named Realization Calculus source/interface attribution was not independently certified in this focused review. The local claims stand on the stated objects and estimates.

## Obligation matrix

| Obligation | Status | Evidence |
|---|---|---|
| Hilbert/Banach typing and existence of projections | Passed | Kernels of bounded linear maps are closed; \(L\) and its closed subspaces inherit Hilbert completeness. |
| Existence of a finite transverse constant from closed range | Passed | \(D:L^\perp\to\operatorname{ran}D\) is a bounded Banach-space bijection; the checked bounded inverse theorem applies. |
| Theorem 1: joint control implies exact-locus control | Passed | Set \(Dx=0\) in the proposed joint inequality. |
| Theorem 1: exact-locus control gives the stated estimate | Passed | Triangle inequality after orthogonal decomposition gives exactly \(a(1+b\|P\|)\|Dx\|+b\|Px\|\). |
| Theorem 1: equivalence with injective closed range | Passed | Bounded-below control makes preimages of a convergent image sequence Cauchy; the converse uses the bounded inverse theorem on the actual closed image. |
| Zero spaces and zero constants | Passed | If \(L=0\), its inverse norm is zero; if \(b=0\) works then \(L=0\); if \(E=0\), all conditions and zero constants are consistent. |
| Optimal coefficient on the exact locus | Passed | The proof explicitly identifies the **least** admissible \(b\) with \(\|(P|_L)^{-1}\|\); arbitrary larger admissible constants need not equal it. |
| Theorem 2 with nonclosed image | Passed | The norm on \(P(L)\) is inherited from \(Y\); direct well-definedness and boundedness suffice, without invoking an inverse theorem there. |
| Kernel annihilation sufficient under closed range | Passed | \(N=L\cap\ker P\) is closed; restrict \(P\) to \(N_L^\perp\) and use a Banach-space inverse onto the assumed closed image. |
| Transfer estimate (4) | Passed | Bound \(\ell(u)\) by \(\|\ell\|\|u\|\) and the exact component by \(B(\|Px\|+\|P\|\|u\|)\). |
| Real-exponent exact family and tangent obstruction | Passed | It stays in the positive real sector, has \(F=0\), fixed declared cost, and unbounded \(H\); the displayed tangent annihilates \(dF\) but not \(dH\). |
| Bounded lattice-distance penalty | Passed | Distance to \(\mathbb Z^3\) is at most \(\sqrt3/2\), so a fixed multiple cannot control the unbounded relaxed height. |
| One-sided approximation lemma | Passed | The low-fractional-part conversion produces a strictly positive error smaller than the original fractional part; denominators can be taken to infinity. |
| Integer family domain, radical, and limits | Passed | \((1,3^{n_j},2^{m_j})\) is positive and pairwise coprime, \(c_j>b_j\), radical \(6\), and height divergent. The displayed triangle estimate forces \(\eta_j\to0\). |
| Eventual nonzero integer defect | Passed | For \(m\ge3\), \(1+3^n\equiv2\) or \(4\pmod8\), whereas \(2^m\equiv0\pmod8\). |
| Scope of residual counterexample | Passed | Only the selected relative archimedean residual is small; the note explicitly disclaims exactness or smallness of every modular/joint defect. |
| Strict stopping law | Passed | \(c\eta=|d|\); \(c\eta<1\) forces the integer \(d\) to vanish. A supplied \(c\le B\) makes \(\eta<1/B\) sufficient. |
| External framework attribution and book build | Out of scope | The exact book passages and Lean build were not audited here; neither is used to fill a local mathematical gap. |
| Actual conductor-to-height comparison / ABC exponent | Out of scope | The proof labels this an independent missing arithmetic construction. |

## Decisive reconstructions

For Theorem 1, take \(u=x-P_Lx\) and \(v=P_Lx\). If \(\|v\|\le b\|Pv\|\) on \(L\), then

\[
\begin{aligned}
\|x\|&\le\|u\|+\|v\|\\
&\le(1+b\|P\|)\|u\|+b\|Px\|\\
&\le a(1+b\|P\|)\|Dx\|+b\|Px\|.
\end{aligned}
\]

The sum of the two nonnegative coefficients is an admissible joint constant for the maximum norm. To verify closed range, if \(Pv_n\to y\), apply the exact-locus estimate to \(v_n-v_m\). The sequence converges in the closed subspace \(L\), and continuity yields an actual preimage of \(y\). Conversely, injectivity and closed range make the actual map \(L\to P(L)\) a bounded bijection between Banach spaces. The example \(P(e_n)=e_n/n\), \(D=0\) confirms that mere injectivity is insufficient; its unit basis images tend to zero.

For Theorem 2, the estimate with \(v-w\) shows that \(Pv=Pw\) forces \(\ell(v)=\ell(w)\). Thus the proposed factorization is genuinely a map on the image rather than a choice-dependent assignment. Its norm is at most the **specified** \(B\). The converse is immediate from the factorization. A nonclosed image is allowed here because a bounded functional need not have a Banach domain. The subsequent sufficient condition is correctly restricted to a closed image: then \(P:N_L^\perp\to P(L)\) has a bounded inverse. No injectivity of \(P|_L\) is needed for that subsequent argument, since its kernel has been removed.

The one-sided approximation conversion is valid in the delicate low-fractional-part case. Write \(q\alpha=l+\delta\) with \(0<\delta<1/Q\), take \(k=\lfloor1/\delta\rfloor\), and note that irrationality of \(\delta\) excludes \(k\delta=1\). Hence

\[
0<1-k\delta<\delta<1/Q,
\qquad \lceil kq\alpha\rceil-kq\alpha=1-k\delta.
\]

For every fixed upper bound on the positive integer \(n\), there are only finitely many errors \(m-n\alpha\) in \((0,1)\), and their minimum is positive. Errors tending to zero therefore permit a subsequence with \(n_j\to\infty\); positivity of \(\alpha\) gives \(m_j\to\infty\). Scaling by \(\log2\) gives the displayed positive logarithmic errors for the integer powers.

The raw family satisfies

\[
\frac{b_j}{c_j}=e^{-\delta_j},\qquad
\eta_j=\left|2^{-m_j}+e^{-\delta_j}-1\right|
\le2^{-m_j}+\left|e^{-\delta_j}-1\right|\longrightarrow0.
\]

Its radical is exactly \(6\), so for any fixed finite real constants \(A,B,C\), the right side of (8) tends to \(A\log6+C\) while \(\log c_j\to\infty\). Any replacement penalty bounded above near zero has the same failure on this raw-candidate domain. The note's numerical illustration checks directly: \(1+243-256=-12\), \(|d|/256=3/64\), and \(\operatorname{rad}(243\cdot256)=6\). It is only an illustration, not the proof of the sequence.

The stopping law uses the absolute integer gap rather than a fixed tolerance for the relative residual. It is sharp for the inference stated: for example, the positive pairwise-coprime raw triple \((1,1,3)\) has \(|d|=1\), so \(c\eta=1\) and \(\eta=1/B\) at the supplied budget \(B=3\), yet it is not additive. Thus replacing either strict threshold by a non-strict one is invalid in general. Along the near-exact family, eventual nonzero defects force \(\eta_j\ge1/c_j\), consistently with \(\eta_j\to0\).

## External leaf verification and computation checks

The bounded inverse theorem was checked in an official primary teaching source: Casey Rodriguez, lecture notes by Andrew Lin, *18.102: Introduction to Functional Analysis*, Spring 2021, Corollary 38, printed page 19 (PDF page 19, one-based), following the proof of the open mapping theorem. The exact source says a bounded bijection between Banach spaces has bounded inverse. This applies to the actual closed images used above, which are Banach spaces with inherited norms. The same source, Theorem 180 and Proposition 183, supplies closed-subspace orthogonal decomposition and its bounded projection. The source hypotheses match these uses; no surjectivity onto all of \(Y\) or Hilbert structure on \(Y\) is inserted.

Source authentication, statement/proof extraction, and these applications were checked on 2026-10-25 at the official [MIT full-notes PDF](https://ocw.mit.edu/courses/18-102-introduction-to-functional-analysis-spring-2021/8fb8d5c170f1613151aca71de21027bc_MIT18_102s21_full_lec.pdf) and its [Lecture 4 extract](https://ocw.mit.edu/courses/18-102-introduction-to-functional-analysis-spring-2021/038fc32ab9c1bb63a4f29bd9d7c97961_MIT18_102s21_lec4.pdf). These web sources were not retained as local input files; no source-file hash or new formal verification is asserted. No novelty search was attempted or required.

The approximation, powers, congruence, and stopping calculations were checked analytically from the note. No load-bearing finite computation, numerical search, exhaustive enumeration, or Lean run was performed. The existing proof-audit instructions and relevant checklists were applied, with the bounded-inverse leaf separately checked under the literature-check workflow.

## Remaining gap and strongest safe conclusion

There is no missing implication in the scoped local theorem package. The exact-locus coercivity criterion is stronger than a transverse repair estimate; for a single size functional it can be weakened precisely to bounded factorization through the observable on that locus. The particular fixed-support real surrogate and the universal bounded relative-residual proposal fail for the displayed reasons.

These failures do not settle any height comparison restricted to exact positive primitive integer triples, do not test every possible joint local defect, and do not identify actual radical support with a bounded linear map. The remaining arithmetic obligation is a separate uniform comparison on the intended exact integer realization space, with justified transformation costs and the every-epsilon coefficient required for ABC. The cheapest next useful check is to type and test a concrete proposed arithmetic comparison against these exact domains; repeating the closed-range argument cannot supply that missing bridge.

## Provenance and exact revision

Independent delegated audit completed 2026-10-25. The final audited input is `abc_work/komorebi_arithmetic/routes/global_coercivity/PROOF_NOTE.md`, SHA-256:

`b0da1f4107cf74d65ab7ce43ead9feb13a5f9116c96c5407a1ecba3aee35728a`.

An earlier raw revision was read before notice of the author's pre-freeze scope clarification; the final revision was then re-read in full, and this report assesses only the final hash above. The finished integer-space report was not edited during this separate audit. No separate route outcome or other review was read, and no proof was edited. The raw note's own concluding section is part of the audited input, not independent evidence. The supplied RR6 archive hash is recorded provenance rather than an authenticated proof input. No applicable additional route instructions or local ledger were found.
