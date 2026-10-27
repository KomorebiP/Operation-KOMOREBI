# Signal Reconstruction — edition 2026-10-06

This edition assembles the Signal work into a traditional manuscript, a mathematical visual guide and a Lean correspondence guide. It preserves the earlier source papers and programs while making the current publication's hypotheses and evidence boundaries explicit.

## Mathematical repairs

- The mean-zero periodic edge error receives its missing location factor. The paper includes the exact sawtooth translation norm and a counterexample to the inherited coefficient-one bound.
- Sparse uniqueness uses the kernel-secant criterion, with the full-column-rank and zero-sparsity cases handled explicitly rather than hidden by a spark convention.
- The failure of a uniform separation-free location Lipschitz bound is demonstrated within a fixed-order two-edge class.
- Exact Fourier recovery specifies the almost-everywhere class and the chosen right-continuous edge representative.
- Multi-offset recovery specifies the number of channels, alias collisions, branch margins and rank conditions. Root disks relying on true centers and coefficient-error bounds are conditional stability statements, not automatic available-data certificates.
- The VEXPA reference is corrected to *Signal Processing* 177 (2020), article 107722, DOI 10.1016/j.sigpro.2020.107722. The classical shifted-coefficient phase relation is attributed accordingly.

## Computational interpretation

The preserved benchmark's `bursts_6_jump` stress case estimates nine edges where the reference has six. Reconstruction error can improve while edge identification fails. The failed first bounded acceptance criterion is preserved alongside the later accurately scoped execution; the result is not silently converted into successful identification.

The infinite-packet experiments use finite implementations, regularized refitting and full reference-pixel residuals. They provide bounded adaptive approximation evidence. Exact orthogonal projection theorems require their own assumptions. Clipping is a nonlinear operation, and a finite stored mask atlas does not establish exhaustive infinite-grammar recovery. The inherited per-method runtime table's zero cells come from a method-key mismatch and do not support timing comparisons.

The original unknown-edge diagnostic can report a positive smallest compact-SVD value when a support has more columns than observations, despite the coefficient map having a kernel. The documented bounded example obeys the dimensional and rank assumptions. Any corrected working implementation is distributed separately, with its patch and tests; the preserved upstream files remain unchanged.

An exact three-jump witness also separates the largest adjacent singular-value ratio heuristic from guaranteed threshold selection. Its perturbed singular values are 400, 396, 4 and 0.4: the heuristic chooses order two, while an independently supplied admissible threshold selects the true order three. The threshold theorem retains its error-bound hypothesis; no automatic threshold certificate or heuristic repair is inferred.

## Formal and archive evidence

The related Paper V sources come from the validated `Paper_V_Complete_v1.1.0_With_Visual_Appendix.zip` checkpoint. Historical build and axiom records accompany them. The current Signal reconstruction statements have no fresh Lean certificate in this edition. The guide identifies exact related declarations and the obligations needed to formalize the wider statements.

The latest `Komorebi_Paper_V_Final_Traditional_Visual_Lean_2026-10-05.zip` could not be validated as a ZIP. Two separately downloaded copies have the same SHA-256 and advertised length of 63,593,585 bytes, but lack an end-of-central-directory record. The cause of the malformed bytes is not established. The failure and retry records identify their hash and the earlier fallback precisely.

## Sources and availability

All three companion `.md` files are included, along with editable TeX, deterministic mathematical figure code, claim maps, bounded execution records and preserved source payloads. The source ZIP indexes every distributable payload by SHA-256 and is CRC-checked. No external repository publication, additional license or machine-native edition is part of this release.
