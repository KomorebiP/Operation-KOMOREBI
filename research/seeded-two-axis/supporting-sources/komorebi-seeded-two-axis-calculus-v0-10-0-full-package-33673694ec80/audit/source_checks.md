# Source verification — v0.10.0

Checked on 27 September 2026. This is a targeted dependency and overlap check, not a global novelty audit. The source texts themselves are not bundled.

## 1. Finite-group ultrametric stability

**Primary source:** Francesco Fournier-Facio, *Ultrametric analogues of Ulam stability of groups*, arXiv:2105.00516v5. Version posted 22 July 2026; manuscript dated 23 July 2026. Version-pinned PDF: https://arxiv.org/pdf/2105.00516v5 .

**Authentication and extraction:** the exact v5 PDF was opened. Its first-page version/date and Section 7.1, printed pp. 53–55, were checked. PDF page index 53 (printed p. 54) was inspected as a screenshot, including Lemma 7.3 and its lifting diagram. The parsed proof and adjacent Proposition 7.4 and Example 7.5 were also read. No unverified result elsewhere in the paper is used.

**Exact statement needed:** Lemma 7.3 assumes an approximate representation into GL_n(o) with defect at most p^{-k}. If its finite reduction image C has v_p(|C|) <= l < k/2, it supplies an exact homomorphism at distance at most p^{l-k}. The proof improves k to 2(k-l) and iterates. We use the strict inequality from the lemma. No endpoint improvement is inferred from the wording of later examples.

**Dictionary:** source o = Z_p, ramification index a = 1, source k = our m, source l = our e = v_p(|G|), source Gamma = our fixed finite G, and source matrix dimension n = our d. The finite reduction image is a quotient of our G, so its order valuation is at most e. Multiplicative defect (A_g A_h A_gh^{-1} - I) and additive matrix distance (A_g A_h - A_gh) have the same entrywise divisibility, since A_gh and its inverse are integral. Thus the hypothesis m > 2e and closeness m-e are exactly applicable.

**Project implication:** K66 is known after this notation/hypothesis translation; the manuscript supplies its own direct matrix-averaging proof rather than taking the source proof as a black box. K67 follows by choosing h=max(n+e,2e+1), lifting finite matrices arbitrarily, and retaining only level h-e. That finite-horizon form is a direct corollary of the established bound. No claim of historical novelty for this criterion or its bound is made.

**Search limitations:** initial general web searches produced irrelevant results and were discarded. A title/author search located the primary source, which was then read directly. We did not conduct a citation-graph survey of every Maranda, rigidity, or deformation-theory formulation. Consequently no “apparently new” verdict is issued.

## 2. Group extension cocycles

**Primary source:** J. S. Milne, *Class Field Theory*, version 4.03, 6 August 2020, https://www.jmilne.org/math/CourseNotes/CFT.pdf .

**Extraction:** Chapter II, 1.17–1.19 gives the inhomogeneous H^2 cocycle law and extension interpretation, including normalized cocycles. Printed p. 66 (PDF page index 74) was inspected as a screenshot for normalization and boundary conventions. Earlier v0.9 source checks of the coefficient boundary and cyclic resolution remain inherited, not freshly re-audited here.

**Dictionary:** coefficient module is End_k(k^d) with the residual conjugation action. The square-zero kernel of GL_d(R_{n+1}) -> GL_d(R_n) is additive through I+p^nX. Taking a section of the pullback extension over rho_n gives c(g,h). Our corrections are on the left, yielding c' = c + delta b with delta b(g,h)=b(g)+g.b(h)-b(gh). Strict conjugation changes b by the negative of a 0-coboundary, with the same subgroup of coboundaries.

**Project implication:** K62 and the H^1/H^0 portion of K63 recover standard extension/deformation obstruction theory. Full matrix derivations and finite certificates are provided, so the arithmetic use is not inferred merely from matching terminology. Milne is not cited as having stated the manuscript's exact finite-horizon result.

## 3. Remaining status

The central-sign counterexample, cyclic Jacobian specialization, worked positive-witness example, and fixed-quotient/profinite distinction have self-contained proofs. They have not undergone independent review or a comprehensive prior-art survey. The underlying mechanisms are elementary or classical. There is no external citation asserted to supply automorphic existence, all-profinite lifting, or a universal new foundation.
