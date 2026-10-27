# Riemann monograph v1.1 self review

Proofread: expanded `body.tex`, with `bibliography.tex` and the shared macro definitions read for consistency.

- Routine edits: no additional conservative copy edits were needed after the substantive expansion was reread. New text uses the established notation, plain prose, and no prose semicolons.
- Mathematical token changes during conservative self review: in the Chernoff optimization sentence, `R>lambda` was clarified to `R>lambda>0` because the immediately following ratio R/lambda requires a nonzero denominator. The lambda=0 tail is explicitly zero. This does not change the positive shell rate or any theorem conclusion.
- Unresolved local notation or cross reference issues: none found. The Hermite cutoff R and the barrier tail multiplier R occur in separate sections and are expressly distinguished in the glossary. Positive test width s is distinguished from the complex zeta variable.
- Validation: Python inspection found no duplicate labels, missing references, missing citation keys, or unmatched LaTeX environments. All previously declared labels are retained. Root performs compilation and rendered layout review separately.
- Coverage: complete expanded manuscript, bibliography keys, and nearby shared macro definitions. Historical recovered files were not edited.

The substantive expansion adds expository derivations and finite worked examples. It is separate from conservative proofreading and does not change the theorem conclusions or the open conjecture. Independent mathematical review has reconstructed the convergence, Fourier normalization, vector residue, Gaussian overlap, Hermite expansion, Poisson rate, finite binomial formula, cube tables, squarefree support count, and barrier exponent steps.

All nine displayed cube table rows were checked by exact rational arithmetic. The finite support counts are nine bases for Q=6 and seven for Q=30 in [30,60]. The Poisson tail and Gram condition values are rounded finite calculations. The exact expressions remain in the manuscript.

No new Lean replay, direct Möbius to heat transport theorem, or universal signed cancellation estimate is claimed. The historical verification limits and the two repaired v1.0 barrier errors remain explicitly documented in the manuscript and author notes.
