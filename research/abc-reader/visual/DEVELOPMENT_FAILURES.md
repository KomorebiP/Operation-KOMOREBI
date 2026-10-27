# Development failures and corrections

The first checkpoint export terminated on an exact benchmark assertion for the proposed example `2 + 3^10 = 23^5`. That equality is false. The independently factored corrected example is `2 + 109*3^10 = 23^5`. Its radical is 15042 and its displayed quality is approximately 1.629912. The assertion terminated the run before exporting the incorrect figure. The already exported radical figure was correct.

This was an example specification error caught by the implementation, not a counterexample to ABC. The corrected generator retains exact equality, radical, coprimality, and balanced normalization assertions.

The next checkpoint export caught a card containment failure in the balanced defect figure. The text extended about 1.4 pixels beyond the card's inner horizontal margin. The font size was reduced from 17 to 16 and the strict check was rerun. No failing figure was exported.

Later batches caught card text margin failures in figures 6, 8, 12, 18, and 23. Figure 8 needed three separate refinements as its wording was clarified, and figure 23 needed both a status-card and footer refinement. The corrections shortened or wrapped labels, or reduced a font size by one point. The final complete export checks every text element against its native canvas and every card text against its interior. All 24 figures pass both checks.

An intermediate figure 10 used a Unicode character intended as an output-sector subscript. Matplotlib reported that this character was absent from the font, and an intermediate asset was exported with that missing glyph. The label was replaced by the explicit mathtext subscripts `R_c` and `M_c`. The final complete export has no missing-glyph warning and overwrote the intermediate asset.

The first small-prime budget integration assumed that the replay JSON supplied a `B` field. Its authoritative schema supplies the prime exponent map `C_p` instead. The run stopped with `KeyError: 'B'`. The generator now derives the exact integer product from that exponent map and checks that it equals 3456.

The first rank-two truncation assertion accidentally compared coefficients of the full determinant with the displayed index-three truncated determinant. The assertion failed before exporting that figure. The coefficient helper now has an explicit truncation parameter, and the check uses `K=3`. It verifies exactly the coefficients `1/8`, `4/27`, and `1/216` at powers 3, 4, and 5. This was a computational surrogate mismatch, rather than a failure of the displayed truncation identity.

Independent review requested three final scope clarifications: the Fermat height normalization term is for each fixed exponent, the jet combination includes the factorial divisor, and the small-prime chart states the hypothesis `v_p(t)=e>=1`. These are included in the final figure and prose sources. The final provenance-recorded export completed successfully, and its version 2 manifest validated against all declared inputs and outputs.

Full-resolution visual inspection then caught an annotation overlap in Figure 21 that canvas and card containment cannot detect: the lower copper note began over the prime-3 bar, making its first letters hard to see. Independent computation review reported the same issue. The note was moved right into open space. The superseded completed run and all seven original inputs are preserved together in `computations/superseded_atlas-v1.0.zip`. Extracting it in an isolated root preserves the original manifest paths and input hashes. A new final run records the corrected figure. This was a visual verification limitation, with no arithmetic change.
