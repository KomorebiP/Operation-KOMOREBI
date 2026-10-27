# Concrete Hilbert integration for Corollary 30.3

The scalar theorem `noiseSchedule_rate` proves the second printed inequality at the literal schedule `noiseSchedule δ = Nat.ceil (δ ^ (-(2 : ℝ) / 3))`. The generic lemmas `noisy_error_of_bias_bound` and `noisy_rounded_rate_of_bias_bound` keep an explicit exact-data bias hypothesis and therefore do not, by themselves, certify the diagonal application.

For the concrete model `InfiniteDiagonalModel.lean`, discharge that hypothesis as follows:

1. Rewrite the exact correction with `c_eq_correction hm`.
2. Use `norm_bias_sq m : ‖c m - w‖^2 = B m`.
3. Apply `B_upper m hm : B m ≤ 2 / (m : ℝ)` and square-root order to prove `‖c m - w‖ ≤ Real.sqrt (2 / (m : ℝ))`.
4. Apply `noisy_error_of_bias_bound T b s w m hm hdata (alpha_pos hm)`; `alpha m` is definitionally `((m : ℝ)^2)⁻¹`.
5. Set `m = noiseSchedule δ` and combine the first bound with `noiseSchedule_rate hδ hδ₁`. The final theorem must quantify an arbitrary `s : H` and `‖s-b‖ ≤ δ`; it must have no bias hypothesis.

The model already records `T_w_eq_b`, `b_apply`, `w_apply`, `c_apply`, and `w_minimum_norm_preimage`, identifying the datum and minimum-norm preimage in the printed result. Full target completion still requires the concrete theorem to compile and pass its declaration/axiom audit.
