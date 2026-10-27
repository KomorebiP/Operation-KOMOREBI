# Visual review: physical pages 97–120

## Scope and method

Reviewed all 24 actual page PNGs, individually at their original 857 × 1109 pixel size, in six batches of four through `view_image`. The files are `tmp/pdfs/monograph_v1.9_draft1/page_097.png` through `page_120.png`. No contact sheet or text extraction substituted for this inspection. An earlier attempted image batch was truncated before context renewal; it was repeated, and all pages listed below were subsequently visible in full.

The assigned 166-page PDF is `monograph_v1.9.0/publication/Komorebi_Space_Monograph.pdf`, SHA-256 `bf3ede62b24958ddc4cc5e52516c2aa7bdff73d4ff84ca5e7c23797095110a85`. Physical page numbers below refer to the PDF position; the printed folios are six lower.

This was a read-only visual inspection. No source, figure, PDF, or Lean file was modified. A visual review does not replace a full mathematical proof audit or a compiler run.

## Outcome

Layout passes throughout the assigned range: no clipped text or equations, text/figure/table overlaps, broken mathematical glyphs, misplaced equation numbers, literal LaTeX leakage, unresolved rendered reference markers, or orphan headings were observed. Figures, arrows, legends, and captions are readable. One mathematical figure-label discrepancy requires a local correction before a clean publication pass can be assigned.

### Required figure-label correction: physical page 109, Figure 28

The blue legend says **“Reachable residuals at the fixed budget.”** The plotted ellipse is centered at zero and includes the point labeled \(Ta=(1/2,1/5)\). It therefore depicts \(T(B_M)\), the image of the correction ball. The reachable residual set \(r-T(B_M)\) would instead be centered at \(r=(1,1)\). The caption already correctly calls this the image of a correction ball, and the arrow from \(Ta\) to \(r\), labeled \(v=(1/2,4/5)\), is correct.

Suggested uniquely local correction: **“Reachable images at the fixed budget.”** The plotted geometry and arrow need no change. The axis wording “Residual coordinate” identifies the target-space coordinates but may optionally be made “Target coordinate” for consistency; the erroneous set identification is specifically the legend.

## Page-by-page record

| Physical page | Printed folio | Material inspected | Finding |
|---:|---:|---|---|
| 97 | 91 | Chapter 26 opening; §§26.1–26.2; sequence spaces, sums, operator formulas and quotient notation | Pass. Equations and indices are legible; headings have following content; no clipping. |
| 98 | 92 | §26.3 finite-repair calculations, four-row table, §26.4 and equations (26.1)–(26.2) | Pass. Table columns and interval fractions remain separate; both tags clear; final prose continues normally. |
| 99 | 93 | Figure 26, its three legend entries and caption; escape continuation; §26.5 | Pass. Logarithmic ticks, bounds and legend styles are readable; caption is clear of plot and prose. |
| 100 | 94 | §26.6 inverse-limit discussion, product-space displays and boxed conclusion | Pass. Box text fits within its borders; lower white space is a chapter-ending layout, not missing or clipped content. |
| 101 | 95 | Chapter 27 opening; formal-status box; §§27.1–27.2; Lemma 27.1 opening | Pass. Box fits, restriction/adjoint notation is legible, and lemma/proof transition is well formed. |
| 102 | 96 | Lemma 27.1 continuation; Bessel and weak-limit displays; Theorem 27.2 and proof | Pass. Subscripts and pairing symbols are clear; lower equations fit above the footer. |
| 103 | 97 | WR01 proof conclusion and evidence line; range/escape paragraph; §27.3 | Pass. No glyph or reference defects; section heading remains with its content. |
| 104 | 98 | §27.4; Figure 27 and caption; Theorem 27.3 and opening proof | Pass. Figure legend and energy curves are readable, caption separated, theorem displays and tag (27.1) clear. |
| 105 | 99 | WR02 proof continuation; exact energy identities; diagonal example and boxed conclusion | Pass. Norms, squared indices and sums render cleanly; box fits. |
| 106 | 100 | Chapter 28 and §28.1; Theorem 28.1; budget profile and convexity/Lipschitz proof | Pass. Infimum indexing, closures, arrows and inequalities are legible; no display/tag overlap. |
| 107 | 101 | WR03 proof end; equation (28.1); closed ball-image prose; §28.2 dual theorem and proof | Pass. Dual maximization bounds and tag (28.2) are distinct; proof continues with adequate bottom clearance. |
| 108 | 102 | WR04 proof conclusion; §28.3 two-dimensional example and matrix | Pass. Matrix entries, square roots and rational calculations are readable and properly spaced. |
| 109 | 103 | Figure 28, ellipse, supporting line, arrow, annotations and caption; §28.4 theorem opening | Layout pass; **legend correction required**, as detailed above. Figure labels do not collide, arrow endpoints are clear, and robustness formulas fit. |
| 110 | 104 | WR05 proof conclusion; Figure 29 uncertainty band and caption | Pass. Legend and shaded band are distinguishable; parameter caption fits without collision. |
| 111 | 105 | Chapter 29; §29.1 normal equation; Theorem 29.1 and inverse proof | Pass. Adjoint/superscript notation and equation (29.1) are legible; bottom display stays clear of footer. |
| 112 | 106 | Energy-identity proof; WR06 evidence line; §§29.2–29.3; coordinate metric and Proposition 29.2 | Pass. Multiline display aligns, coordinate formula/tag (29.2) clear, final proposition text unclipped. |
| 113 | 107 | WR07 proof; witness formulas; §29.4 and Theorem 29.3 | Pass. Greek subscripts, inequality chains and limit arrows are clear; heading has sufficient following content. |
| 114 | 108 | WR08 proof Steps 1–5; strong-convergence and divergence formulas; evidence line | Pass. Dense proof remains legible, long norm expressions fit, and no content touches the footer. |
| 115 | 109 | Four-case table; §29.5; Figure 30 noise multiplier and caption; Theorem 29.4 opening | Pass. Table rows/columns stay separate; plot maxima, legend and bound annotation are clear; theorem separated from caption. |
| 116 | 110 | Theorem 29.4 continuation; estimates and limiting argument; WR09 evidence line and box | Pass. Fractions and parameter-dependent subscripts legible; long evidence line and box fit. |
| 117 | 111 | Chapter 30; §30.1; Proposition 30.1; equations (30.1)–(30.2), sums and integral comparison | Pass. Long displays and right-hand equation tags remain separated; bottom sum fits. |
| 118 | 112 | WR10 proof end; Figure 31 soft-correction curves and caption; §30.2 opening | Pass. Curves, midpoint dots and legend are clear. §30.2 has two lines of prose after it, so it is not orphaned. |
| 119 | 113 | Theorem 30.2; equation (30.3); Riemann-sum bounds, integrals and budget ratios | Pass. Large delimiters, floor notation, fractions and integral limits are legible; tags do not intrude. |
| 120 | 114 | WR11 proof conclusion; Figure 32 certified intervals and asymptotic lines; caption | Pass. Error bars, legend and labels \(1\), \(\pi/4\) are visible; caption fits below the axes without clipping. |

## Handoff

The page 109 legend finding was sent to the parent reviewer during inspection. Reinspect the corrected Figure 28 in the next render and record its PDF/image identity. All other observations above apply to the stated draft hash and page images.
