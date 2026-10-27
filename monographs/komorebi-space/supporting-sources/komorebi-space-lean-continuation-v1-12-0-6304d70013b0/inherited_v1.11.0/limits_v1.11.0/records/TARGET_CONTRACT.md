# Exact formalization target

Base: KS-v1.10.0-WR03-WR05-complete. Literal manuscript chapters are frozen in `targets/`; their hashes and every inherited formal source hash are in `BASE_CHECKPOINT.json`.

Work in arbitrary real Hilbert spaces H and Y with bounded linear T : H → Y and datum r. Put C = closure(range T), b = P_C r and q = ‖r − b‖. For every α > 0, aα is the existing WR06 minimizer of ‖T a − r‖² + α‖a‖², with the original Hilbert norm.

## WR08 — all five conclusions

As the real parameter α tends to zero through strictly positive values:

1. T aα tends in norm to b.
2. ‖r − T aα‖ tends to q.
3. α‖aα‖² tends to zero.
4. If b is in the actual range, construct its unique minimum-norm preimage a† and prove aα tends in norm to a†.
5. If b is outside the actual range, prove ‖aα‖ tends to +∞.

The endpoint α = 0 need not have a defined optimizer. An all-real convenience path may equal zero for α ≤ 0 only if its equality with the existing optimizer for α > 0 is proved and every limit uses the right-hand punctured neighborhood. Sequence-only results, weak convergence alone, unboundedness alone, or vanishing penalty alone do not satisfy the target. Do not add finite-dimensionality, separability, closed range, injectivity or a positive residual floor.

## WR09 — finish all named theorem clauses

Retain the accepted pointwise correction and image-noise estimates. Prove sharpness of 1/(2√α) over bounded linear real Hilbert operators, including an actual scalar witness. For attained b, positive α(δ) tending to zero and δ/√α(δ) tending to zero, prove convergence of the measured-data corrections to a† as δ tends to zero. The same fixed T and Hilbert metrics are required.

## WR16 — finish all named theorem clauses

For positive αn and measured data/proposals in the same correction space, retain the full three-term pointwise estimate and prove strong convergence assuming αn → 0, δn/√αn → 0, εn/αn → 0 and the printed data and measured normal-residual bounds. A general filter theorem may imply this sequence statement, but expose a direct instance. Protection at each index follows from working in the protected kernel; retain its accepted interface. The adjacent diagonal-rate example belongs to the WR12 dependency and is outside this target.

## Definition of done

No coverage promotion until strict compilation, complete declaration/axiom audit, intended controls, a fresh independent review of exact exported types and definitions, and integrated evidence validation all pass. Keep every failed numbered attempt and its actual diagnosis. Preserve the accepted baseline; version new results separately. The existing PDF is historical context and will not be relabeled as updated by this Lean-only continuation.
