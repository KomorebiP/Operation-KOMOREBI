# Independent source-level review of the noisy schedule

Reviewer: sibling agent `/root/proofread_appendices` (read-only review).
Reviewed file SHA-256: `71f276f7cea427384917c4aaa548980f043490eb086d360736923c1fd026e8bd`.
Review scope: the scalar schedule and explicitly conditional Hilbert transfer before concrete integration and before kernel compilation.

No semantic defect was found. The review checked the literal `Nat.ceil`, the real exponents `-(2 : ℝ)/3` and `(1 : ℝ)/3`, the range `0 < δ ≤ 1`, positivity of denominators, the correct noise order `s-r`, inverse-square square-root reduction, and retained real Hilbert/completeness assumptions. The endpoint `δ=1` gives `m=1`; `δ=0` is intentionally excluded.

The dependency chain is:
- positive real power and ceiling bounds;
- separate scalar bias/noise estimates;
- `noiseSchedule_rate`;
- existing universal `data_noise_bound`, an explicit `hbias`, and the triangle inequality;
- `noisy_error_of_bias_bound` and `noisy_rounded_rate_of_bias_bound`.

The generic `aMin` is arbitrary and its bias hypothesis is explicit. No minimum-preimage or concrete-diagonal identity is silently asserted. The mathematical dependency still needed at this reviewed revision is the actual diagonal correction identity together with squared bias `B m ≤ 2/(m:ℝ)`. This review is source-level evidence, not a substitute for kernel compilation or an axiom audit.

## Concrete integration review

The same reviewer subsequently checked SHA-256 `55ad01c40e768c2ab7d70895ff5576c2576751137ebb7994198f1ebe27e2d21e`, including `diagonal_bias_bound`, `diagonal_noisy_error`, and `corollary_30_3`. No semantic mismatch was found. The actual `H` is real `lp` at exponent two; coordinate `j` represents `n=j+1`; `T` multiplies by `1/n`; `b=T w` has coordinates `1/n²`; and `w` has coordinates `1/n` with its unique/minimum-preimage theorem.

`diagonal_bias_bound` uses the actual correction identity, `norm_bias_sq`, and `B_upper` to discharge the bias premise. `diagonal_noisy_error` applies the existing universal noise theorem. `corollary_30_3` exposes the literal ceiling and real exponents, retains `0 < δ ≤ 1`, uses `alpha m=m⁻²`, quantifies arbitrary Hilbert noise, and states both printed inequalities without a bias assumption. This was again a read-only source review; concrete kernel compilation was pending at review time.
