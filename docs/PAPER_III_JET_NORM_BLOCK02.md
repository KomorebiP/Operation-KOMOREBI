# Paper III: packet jet norm corollaries

This separate companion completes the previously missing norm clauses of
**Proposition 17.3, Jet norm bound**. It proves the projector-product estimate
for the actual packet ranges, specializes the bound to actual Hilbert
orthogonal output projections, and handles redundant zero packets. It uses
the existing Paper III jet definitions.

For a continuous multilinear map `B`, the range-jet bound is

\[
\|J_{\gamma\mid\alpha_1,\ldots,\alpha_n}B\|
\leq \|Q_\gamma\|\,\|B\|\prod_{k=1}^{n}\|P_{\alpha_k}\|.
\]

The sharper inherited-range bound needs only the output projector's norm.
An actual orthogonal output projector therefore gives a bound by `norm B`.
The proof retains the nonzero-subspace hypothesis when asserting projector
norm equal to one. Algebraic annihilation of distinct projectors does not
imply contractivity; a checked oblique complete-system fixture contains a
projector with norm at least three.

- [Companion, scope and reproduction](../formal/paper-iii-jet-norm-v0.1.0/README.md)
- [New Lean proofs](../formal/paper-iii-jet-norm-v0.1.0/KomorebiPaperIIIJetNorm/Bounds.lean)
- [Clause map and unchanged prerequisite identities](../formal/paper-iii-jet-norm-v0.1.0/CLAIM_MAP.json)
- [Mathematical and editorial self-review](../formal/paper-iii-jet-norm-v0.1.0/REVIEW.md)
- [Proofreading receipt: lines 205–284](../formal/paper-iii-jet-norm-v0.1.0/PROOFREAD_RECEIPT.json)
- [Compiler, axiom, kernel and control receipt](../formal/paper-iii-jet-norm-v0.1.0/evidence/run.json)

The companion adds nine theorem declarations and rebuilds four unchanged
prerequisite modules. Those counts do not describe whole-paper formalization.
The selected passage was proofread without source corrections. The original
manuscript, statement register, sixteen-module core and earlier evidence
remain preserved. Review is same-assistant self-review; the packet Taylor
formula and integral error estimate remain separate targets.

[Paper III](works/paper-iii.md) · [Stirling/Touchard companion](PAPER_III_STIRLING_BLOCK01.md)
