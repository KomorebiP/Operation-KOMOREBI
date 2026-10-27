# Collatz visual guide proofreading and figure review

Reader edition 1.1, 8 October 2026. The guide has a cover and 24 distinct educational spreads. The companion monograph contains the full proofs and primary-source register.

## Mathematical scope

The guide preserves the exact odd map convention, ordered offsets, realization cylinders, extra endpoint oddness bit, source floor, composition law, and first descent clock. It distinguishes homogeneous coefficient contraction from actual source descent. The 165 example is explicitly a finite word comparison after an earlier descent, not a least failure trajectory.

Independent review checked every spread against the current monograph. Two omitted hypotheses were supplied before finalization: the density bound uses integers ℓ≥1 and D≥0, and the smaller-source merger comparison assumes positive sources n>m. The permanent noncrossing branch retains its exact quantified hypothesis. Its unbounded-tail deficit conclusion is not changed into convergence of the deficit to infinity.

The historical 1804/2048 residue count is labeled historical and unreplayed. The waffle arrangement groups counts rather than reproducing residue addresses. The common-height capacity diagram is explicitly schematic and does not assert an observed counterexample trajectory. All finite illustrations are distinguished from the written uniform proofs.

## Visual inspection

All 24 native figures were regenerated and inspected on four contact sheets. Plot axes have fitted margins. Figure labels use at least 14-point source text, giving legible labels in the shared landscape layout. The exact peak arrow is computed from the orbit maximum. The 151 packet now uses an actual state plot so its final value appears below its original source floor.

An automatic text-bound check returned no drawn text outside any figure canvas. That check excludes out-of-range tick artists retained internally by Matplotlib but not drawn. It does not replace the visual review. Root-level inspection of the rendered guide verifies the complete page layout separately.

## Resolved failures

The first complete figure run stopped at the symmetric-log plot because the threshold parameter was passed through an unsupported API. Moving it to `set_yscale` fixed the failure, and a complete deterministic regeneration passed.

The first peak annotation pointed at manually entered step 17. Independent review identified the correct maximum at step 32. The location now derives from the exact data instead of a handwritten index.

Initial footer prose collided with several axis labels. The footer prose was removed from the graphics, retained in `data.json`, and placed in the adjacent reading columns. Automatic plot margins also corrected clipped vertical labels. Historical coverage count labels were separated from the bottom row of the waffle.

No mathematical counterexample or failed exact arithmetic assertion was found in the stated finite ranges. This edition does not rerun historical Lean builds or claim a universal Collatz proof.

## Language and formatting

Each spread gives one concrete reading task and a concise carry-forward statement. Prose avoids semicolons and unnecessary hyphenation. Every source comparison names its map, word, or original floor. The guide contains no unresolved draft markers.
