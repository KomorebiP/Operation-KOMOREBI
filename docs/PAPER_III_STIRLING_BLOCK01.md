# Paper III: the Stirling/Touchard term count

This continuation supplies a Lean proof of **Proposition 17.6, Number of
labeled composition terms**, in Paper III. It also records focused
proofreading of the surrounding composition passage, lines 339–420 of the
published nonlinear-coordinate chapter. No source correction was needed in
that passage.

The count is

\[
N_{n,M}=\sum_{k=1}^{n}S(n,k)M^k \qquad(n\geq1).
\]

The new proof counts the actual canonical partitions and intermediate label
functions used to index the existing packet composition formula. It proves
their length distribution through the Stirling recurrence, then counts all
label assignments. Thus two intermediate packets give six second-order terms
and twenty-two third-order terms. Zero jets and cancellation can reduce the
number of nonzero contributions.

- [Separate companion, scope and reproduction](../formal/paper-iii-stirling-v0.1.0/README.md)
- [Lean source](../formal/paper-iii-stirling-v0.1.0/KomorebiPaperIIIStirling/CompositionTermCount.lean)
- [Statement correspondence and original register row](../formal/paper-iii-stirling-v0.1.0/CLAIM_MAP.json)
- [Proofreading and mathematical self-review](../formal/paper-iii-stirling-v0.1.0/REVIEW.md)
- [Proofreading receipt](../formal/paper-iii-stirling-v0.1.0/PROOFREAD_RECEIPT.json)
- [Compiler, axiom, kernel-replay and control receipt](../formal/paper-iii-stirling-v0.1.0/evidence/run.json)

The eight new theorem declarations support one newly matched manuscript
proposition. They are not eight additional manuscript results. The original
sixteen-module core and frozen edition are preserved, and no whole-paper
formalization percentage is inferred. The packet Taylor remainder and
estimate, separate norm corollaries and later expanded material remain outside
this companion. This review is self-review, not independent peer review.

[Paper III](works/paper-iii.md) · [Lean source finder](browse/LEAN.md)
