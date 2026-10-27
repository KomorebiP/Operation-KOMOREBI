# Final Verification Report

## Projector-Resolved Prime-Contact Coherence Calculus

**Subtitle:** Sparse Additive Relations, Prime-Power Contact, and Adelic Coherence  
**Author:** Komorebi P.  
**Verified edition:** 31 July 2026  
**Final length:** 142 pages

## Overall conclusion

The final paper has passed a complete internal audit of its source, exact algebra, computational implementations, corpus calculations, references, layout, headers, rendering, and clean-source rebuild.

Two substantive mathematical issues found during the audit were corrected before this edition was built:

1. The Smith obstruction theorem is now stated for the exponent-free phase or shell-synthesis rows, which are the rows for which the Smith normal form is exactly
   \[
   \operatorname{diag}\left(1,\frac{abc}{\operatorname{rad}(abc)}\right).
   \]
   The proof now uses determinantal divisors and the cross-sector minors explicitly.

2. The final uniform arithmetic target is now the combined bound
   \[
   WC\le C_\varepsilon R_aR_bR^\varepsilon,
   \]
   not a bound for the coherence factor \(C\) alone. The pure coherence estimate is retained only for the subfamily \(W=1\).

Additional corrections include explicit unit-sector cases, a strengthened real-height derivation, a precise formal-completion statement, a qualified Fermat line-bundle height statement, explicit truncation of finite-ring valuations, and a stricter separation between dyadic Smith bookkeeping and the principal-unit logarithm shift at two.

No internal mathematical contradiction was found after these corrections. The audit does not convert the conditional endpoints into theorems. In particular, the paper does **not** prove the \(abc\) conjecture.

## Exact mathematical audit

The independent exact audit passed all of the following checks:

| Audit family | Exact cases passed |
|---|---:|
| Exponent-free phase Smith normal form | 152,095 primitive triples |
| Polyphase Smith form | 195 cases |
| Wronskian radical divisibility | 2,499 packets |
| Divisor-polyphase identities | 5,001 integers |
| Kummer kernel formula | 391 cases |
| Atkin–Lehner Walsh packet identities | 254 packets |
| Worked shortest transverse packet | \(\Theta(3,125,128)=6\) |

The complete exact result ledger is included as `verification/final_math_audit_results.json` in the source package.

## Implementation audit

Nine independent implementation groups passed:

- arbitrary-precision moving-coset recovery
- unit-sector handling
- the signed-64-bit overflow regression
- Witt and Kummer packet arithmetic
- polylogarithmic distribution and functional identities
- filtered contact transfer
- integral Hecke and ray-class packets
- Hecke cotangent and Wiles-defect toy models
- the final coherence factorization and worked row

The large overflow regression was recomputed with Python arbitrary-precision integers:

\[
24833+5020969537415167=5020969537440000.
\]

The exact moving-search result is

\[
\Phi=4072242,
\qquad
\frac{\Phi}{\overline H}
=
\frac{5578869055243}{5578855041600}.
\]

All seven reference Python implementations used in the audit compile successfully.

## Complete coherence-corpus rerun

The 361-row coherence corpus was regenerated from the exact implementation. Every common output column matched the stored corpus exactly.

The rerun reproduced:

| Quantity | Result |
|---|---:|
| Rows | 361 |
| Exact factorization checks | 361 |
| \(K=1\) | 352 triples |
| \(W=1\) | 349 triples |
| \(C=1\) | 9 triples |
| Largest \(W\) | 2,197 |
| Largest \(C\) | 21,457,672,119,140,625 |
| Median relation-compression ratio | 0.7142857142857143 |
| Minimum relation-compression ratio | 0.01074809404143488 |
| Correlation of quality with \(\log C\) | 0.5347749451312078 |

The worked example was recovered exactly:

\[
(\epsilon_2,K,W,C)=(2,1,1,32),
\qquad
(29,31)\pmod{32}.
\]

## Source-language and claim audit

The final source contains:

- no references to numbered development stages
- no version-history language
- no artificial-intelligence or model-generated language
- no project-management language
- no placeholders
- no unsupported breakthrough language
- no duplicate theorem labels
- no duplicated long prose paragraphs
- no control characters or replacement characters
- no prose semicolons

The paper contains no sentence claiming that the \(abc\) conjecture has been proved or solved. Exact theorems, finite evidence, structural limitations, conjectures, and conditional implications are separated explicitly.

## PDF and layout audit

The final PDF passed the following checks:

| Check | Result |
|---|---:|
| Pages | 142 |
| PDF preflight warnings | 0 |
| LaTeX overfull boxes | 0 |
| LaTeX underfull boxes | 0 |
| Undefined references | 0 |
| Duplicate labels | 0 |
| Words outside page boundaries | 0 |
| Header overlaps | 0 |
| Genuine text overlaps | 0 |
| Blank pages | 0 |
| Low-content divider pages | 0 |
| Unexpected page rotations | 0 |
| Visible semicolons | 0 |
| Fonts embedded | all |
| Pages rendered successfully | 142 |

The former standalone part-title pages were merged with their opening chapters. This removed six sparse divider pages and produced a continuous 142-page paper.

One automated overlap detector flagged a mathematical arrow and its label on page 68. Full-resolution visual inspection confirmed that this was normal mathematical typesetting rather than a genuine overlap.

## Rebuild verification

A source-only copy was rebuilt in an isolated directory with three clean `pdflatex` passes.

The clean rebuild:

- produced 142 pages
- produced no LaTeX layout warnings
- passed PDF preflight
- passed Ghostscript rendering validation
- embedded all fonts
- matched the canonical PDF text on all 142 pages

## Claim boundary

The following are exact internal results in the paper:

- prime-packet identities and Wronskian divisibility
- the exponent-free Smith obstruction theorem
- the polyphase Smith decomposition
- the exact obstruction-lattice sequence
- the moving-coset reduction and finite stopping law
- prime-shell and divisor-polyphase identities
- filtered contact and Witt carry structure
- Kummer kernel formulas
- finite character and polylogarithmic identities
- the exact factorization \(M=\epsilon_2KWC\)
- the construction and index of the adelic coherence lattice
- the stated structural no-go theorems

The following remain open or conditional:

- the combined logarithmic–coherence estimate for \(WC\)
- the required adelic minor or regulator lower bound
- the filtered local-global automorphic transfer
- a sparse motivic or Jacobi quotient with radical-scale synthesis cost
- the functorial gluing bound
- every deduction of the full \(abc\) conjecture or another major conjecture that depends on one of those estimates

## Independent review

This is a detailed internal consistency and reproducibility audit. It is not independent peer review. The advanced arithmetic constructions and the claimed novelty of the framework should still be examined by specialists in Diophantine geometry, arithmetic derivatives, local and global Galois theory, modular forms, K-theory, and polylogarithmic motives.
