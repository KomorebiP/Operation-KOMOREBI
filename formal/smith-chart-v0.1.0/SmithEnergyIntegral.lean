import SmithSamplingIntegral
import SmithPackets
import SmithEnergy

open Set Metric Real

namespace SmithEnergyIntegral

theorem integral_nat_mul_periodic {N : ℕ} (hN : 0 < N) {f : ℝ → ℝ}
    (hper : Function.Periodic f (2 * Real.pi)) (hf : Continuous f) :
    (∫ x in (0 : ℝ)..2 * Real.pi, f ((N : ℝ) * x)) =
      ∫ x in (0 : ℝ)..2 * Real.pi, f x := by
  have hn : (N : ℝ) ≠ 0 := by exact_mod_cast hN.ne'
  have hfi : ∀ a b, IntervalIntegrable f MeasureTheory.volume a b :=
    fun a b => hf.intervalIntegrable _ _
  have hi : (∫ x in (0 : ℝ)..(N : ℝ) * (2 * Real.pi), f x) =
      (N : ℝ) * ∫ x in (0 : ℝ)..2 * Real.pi, f x := by
    simpa using hper.intervalIntegral_add_zsmul_eq (N : ℤ) (0 : ℝ) hfi
  rw [intervalIntegral.integral_comp_mul_left f hn]
  simp [hi, hn]

noncomputable def profile (q x : ℝ) : ℝ := (1 - q ^ 2) / (1 - 2 * q * Real.cos x + q ^ 2)

theorem reciprocal_kernel_mean {q : ℝ} (hq0 : 0 ≤ q) (hq1 : q < 1)
    {N : ℕ} (hN : 0 < N) :
    (2 * Real.pi)⁻¹ * (∫ θ in (0 : ℝ)..2 * Real.pi,
      1 / (1 - 2 * q * Real.cos ((N : ℝ) * θ) + q ^ 2)) = (1 - q ^ 2)⁻¹ := by
  have hden (θ : ℝ) : 0 < 1 - 2 * q * Real.cos θ + q ^ 2 := by
    have hm := mul_nonneg hq0 (sub_nonneg.mpr (Real.cos_le_one θ))
    have hs := sq_pos_of_pos (sub_pos.mpr hq1)
    nlinarith
  have hc : Continuous (profile q) := by
    unfold profile
    apply Continuous.div (by fun_prop) (by fun_prop)
    intro θ
    exact (hden θ).ne'
  have hp : Function.Periodic (profile q) (2 * Real.pi) := by
    intro θ
    simp [profile, Real.cos_add_two_pi]
  have hnorm : (∫ θ in (0 : ℝ)..2 * Real.pi, profile q ((N : ℝ) * θ)) = 2 * Real.pi := by
    rw [integral_nat_mul_periodic hN hp hc]
    exact SmithPoisson.poisson_trig_integral (by simpa [profile, abs_of_nonneg hq0] using hq1)
  let R : ℝ := ∫ θ in (0 : ℝ)..2 * Real.pi,
    1 / (1 - 2 * q * Real.cos ((N : ℝ) * θ) + q ^ 2)
  have hfactor : (1 - q ^ 2) * R = 2 * Real.pi := by
    have heq : (∫ θ in (0 : ℝ)..2 * Real.pi, profile q ((N : ℝ) * θ)) = (1 - q ^ 2) * R := by
      dsimp [R, profile]
      rw [← intervalIntegral.integral_const_mul]
      apply intervalIntegral.integral_congr
      intro θ _
      simp [div_eq_mul_inv]
    rw [← heq]
    exact hnorm
  have hqpos : 0 < 1 - q ^ 2 := by
    nlinarith [mul_nonneg hq0 (sub_nonneg.mpr hq1.le)]
  change (2 * Real.pi)⁻¹ * R = (1 - q ^ 2)⁻¹
  field_simp [ne_of_gt hqpos, Real.pi_ne_zero]
  nlinarith [hfactor]

theorem nonzero_packet_norm_sq {ρ : ℝ} (hρ0 : 0 ≤ ρ) (N j : ℕ) (θ : ℝ) :
    ‖(2 : ℂ) * (circleMap 0 ρ θ) ^ j / (1 - (circleMap 0 ρ θ) ^ N)‖ ^ 2 =
      (4 * ρ ^ (2 * j)) /
        (1 - 2 * ρ ^ N * Real.cos ((N : ℝ) * θ) + (ρ ^ N) ^ 2) := by
  have hd : ‖(1 : ℂ) - (circleMap 0 ρ θ) ^ N‖ ^ 2 =
      1 - 2 * ρ ^ N * Real.cos ((N : ℝ) * θ) + (ρ ^ N) ^ 2 := by
    rw [circleMap_zero_pow, ← Complex.normSq_eq_norm_sq, Complex.normSq_apply]
    simp only [Complex.sub_re, Complex.sub_im, Complex.one_re, Complex.one_im,
      circleMap_zero_re, circleMap_zero_im]
    nlinarith [Real.cos_sq_add_sin_sq ((N : ℝ) * θ)]
  rw [norm_div, div_pow, hd]
  simp [norm_pow, norm_circleMap_zero, abs_of_nonneg hρ0, mul_pow, ← pow_mul, Nat.mul_comm]; norm_num

/-- Finite-radius angular mean of the nonzero-lane rational packet. -/
theorem nonzero_packet_mean {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N : ℕ} (hN : 0 < N) (j : ℕ) :
    (2 * Real.pi)⁻¹ * (∫ θ in (0 : ℝ)..2 * Real.pi,
      ‖(2 : ℂ) * (circleMap 0 ρ θ) ^ j / (1 - (circleMap 0 ρ θ) ^ N)‖ ^ 2) =
      (4 * ρ ^ (2 * j)) / (1 - (ρ ^ N) ^ 2) := by
  have hq0 : 0 ≤ ρ ^ N := pow_nonneg hρ0 _
  have hq1 : ρ ^ N < 1 := pow_lt_one₀ hρ0 hρ1 hN.ne'
  have hmean := reciprocal_kernel_mean hq0 hq1 hN
  have heq : (∫ θ in (0 : ℝ)..2 * Real.pi,
      ‖(2 : ℂ) * (circleMap 0 ρ θ) ^ j / (1 - (circleMap 0 ρ θ) ^ N)‖ ^ 2) =
      (4 * ρ ^ (2 * j)) * (∫ θ in (0 : ℝ)..2 * Real.pi,
        1 / (1 - 2 * ρ ^ N * Real.cos ((N : ℝ) * θ) + (ρ ^ N) ^ 2)) := by
    rw [← intervalIntegral.integral_const_mul]
    apply intervalIntegral.integral_congr
    intro θ _
    dsimp only
    rw [nonzero_packet_norm_sq hρ0]
    simp [div_eq_mul_inv]
  rw [heq]
  calc
    (2 * Real.pi)⁻¹ * ((4 * ρ ^ (2 * j)) *
        (∫ θ in (0 : ℝ)..2 * Real.pi,
          1 / (1 - 2 * ρ ^ N * Real.cos ((N : ℝ) * θ) + (ρ ^ N) ^ 2))) =
      (4 * ρ ^ (2 * j)) * ((2 * Real.pi)⁻¹ *
        (∫ θ in (0 : ℝ)..2 * Real.pi,
          1 / (1 - 2 * ρ ^ N * Real.cos ((N : ℝ) * θ) + (ρ ^ N) ^ 2))) := by ring
    _ = (4 * ρ ^ (2 * j)) * (1 - (ρ ^ N) ^ 2)⁻¹ := by rw [hmean]
    _ = (4 * ρ ^ (2 * j)) / (1 - (ρ ^ N) ^ 2) := by rw [div_eq_mul_inv]

theorem zero_packet_norm_sq {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N : ℕ} (hN : 0 < N) (θ : ℝ) :
    ‖((1 : ℂ) + (circleMap 0 ρ θ) ^ N) / (1 - (circleMap 0 ρ θ) ^ N)‖ ^ 2 =
      2 * (1 + (ρ ^ N) ^ 2) /
        (1 - 2 * ρ ^ N * Real.cos ((N : ℝ) * θ) + (ρ ^ N) ^ 2) - 1 := by
  have hq0 : 0 ≤ ρ ^ N := pow_nonneg hρ0 _
  have hq1 : ρ ^ N < 1 := pow_lt_one₀ hρ0 hρ1 hN.ne'
  have hpos : 0 < 1 - 2 * ρ ^ N * Real.cos ((N : ℝ) * θ) + (ρ ^ N) ^ 2 := by
    have hm := mul_nonneg hq0 (sub_nonneg.mpr (Real.cos_le_one ((N : ℝ) * θ)))
    have hs := sq_pos_of_pos (sub_pos.mpr hq1)
    nlinarith
  have hd : ‖(1 : ℂ) - (circleMap 0 ρ θ) ^ N‖ ^ 2 =
      1 - 2 * ρ ^ N * Real.cos ((N : ℝ) * θ) + (ρ ^ N) ^ 2 := by
    rw [circleMap_zero_pow, ← Complex.normSq_eq_norm_sq, Complex.normSq_apply]
    simp only [Complex.sub_re, Complex.sub_im, Complex.one_re, Complex.one_im,
      circleMap_zero_re, circleMap_zero_im]
    nlinarith [Real.cos_sq_add_sin_sq ((N : ℝ) * θ)]
  have hn : ‖(1 : ℂ) + (circleMap 0 ρ θ) ^ N‖ ^ 2 =
      1 + 2 * ρ ^ N * Real.cos ((N : ℝ) * θ) + (ρ ^ N) ^ 2 := by
    rw [circleMap_zero_pow, ← Complex.normSq_eq_norm_sq, Complex.normSq_apply]
    simp only [Complex.add_re, Complex.add_im, Complex.one_re, Complex.one_im,
      circleMap_zero_re, circleMap_zero_im]
    nlinarith [Real.cos_sq_add_sin_sq ((N : ℝ) * θ)]
  rw [norm_div, div_pow, hn, hd]
  field_simp; ring

/-- Finite-radius angular mean of the zero-lane rational packet. -/
theorem zero_packet_mean {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N : ℕ} (hN : 0 < N) :
    (2 * Real.pi)⁻¹ * (∫ θ in (0 : ℝ)..2 * Real.pi,
      ‖((1 : ℂ) + (circleMap 0 ρ θ) ^ N) / (1 - (circleMap 0 ρ θ) ^ N)‖ ^ 2) =
      1 + 4 * (ρ ^ N) ^ 2 / (1 - (ρ ^ N) ^ 2) := by
  let q : ℝ := ρ ^ N
  have hq0 : 0 ≤ q := pow_nonneg hρ0 _
  have hq1 : q < 1 := pow_lt_one₀ hρ0 hρ1 hN.ne'
  have hqpos : 0 < 1 - q ^ 2 := by
    nlinarith [mul_nonneg hq0 (sub_nonneg.mpr hq1.le)]
  have hd (θ : ℝ) : 0 < 1 - 2 * q * Real.cos ((N : ℝ) * θ) + q ^ 2 := by
    have hm := mul_nonneg hq0 (sub_nonneg.mpr (Real.cos_le_one ((N : ℝ) * θ)))
    have hs := sq_pos_of_pos (sub_pos.mpr hq1)
    nlinarith
  have hrec : Continuous (fun θ : ℝ =>
      1 / (1 - 2 * q * Real.cos ((N : ℝ) * θ) + q ^ 2)) := by
    apply Continuous.div (by fun_prop) (by fun_prop)
    intro θ
    exact (hd θ).ne'
  let R : ℝ := ∫ θ in (0 : ℝ)..2 * Real.pi,
    1 / (1 - 2 * q * Real.cos ((N : ℝ) * θ) + q ^ 2)
  have hmean : (2 * Real.pi)⁻¹ * R = (1 - q ^ 2)⁻¹ := by
    dsimp [R, q]
    exact reciprocal_kernel_mean hq0 hq1 hN
  have heq : (fun θ : ℝ =>
      ‖((1 : ℂ) + (circleMap 0 ρ θ) ^ N) / (1 - (circleMap 0 ρ θ) ^ N)‖ ^ 2) =
      (fun θ => 2 * (1 + q ^ 2) *
        (1 / (1 - 2 * q * Real.cos ((N : ℝ) * θ) + q ^ 2)) - 1) := by
    funext θ
    rw [zero_packet_norm_sq hρ0 hρ1 hN]
    dsimp [q]
    simp [div_eq_mul_inv]
  have hi1 : IntervalIntegrable (fun θ : ℝ => 2 * (1 + q ^ 2) *
      (1 / (1 - 2 * q * Real.cos ((N : ℝ) * θ) + q ^ 2)))
      MeasureTheory.volume 0 (2 * Real.pi) := (continuous_const.mul hrec).intervalIntegrable _ _
  have hi2 : IntervalIntegrable (fun _ : ℝ => (1 : ℝ))
      MeasureTheory.volume 0 (2 * Real.pi) := intervalIntegrable_const
  have hintegral : (∫ θ in (0 : ℝ)..2 * Real.pi,
      ‖((1 : ℂ) + (circleMap 0 ρ θ) ^ N) / (1 - (circleMap 0 ρ θ) ^ N)‖ ^ 2) =
      2 * (1 + q ^ 2) * R - 2 * Real.pi := by
    rw [heq, intervalIntegral.integral_sub hi1 hi2, intervalIntegral.integral_const_mul]
    simp [R]
  rw [hintegral]
  change (2 * Real.pi)⁻¹ * (2 * (1 + q ^ 2) * R - 2 * Real.pi) =
    1 + 4 * q ^ 2 / (1 - q ^ 2)
  field_simp [Real.pi_ne_zero, ne_of_gt hqpos] at hmean ⊢
  nlinarith [hmean]

/-- The actual nonzero impedance packet has the computed angular mean. -/
theorem impedance_nonzero_angular_energy {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N j : ℕ} (hN : 0 < N) (hj : j ≠ 0) :
    (2 * Real.pi)⁻¹ * (∫ θ in (0 : ℝ)..2 * Real.pi,
      ‖SmithChart.impedancePacket N j (circleMap 0 ρ θ)‖ ^ 2) =
      (4 * ρ ^ (2 * j)) / (1 - ρ ^ (2 * N)) := by
  have hnorm (θ : ℝ) : ‖circleMap 0 ρ θ‖ < 1 := by
    simpa [norm_circleMap_zero, abs_of_nonneg hρ0] using hρ1
  have heq : (fun θ : ℝ => ‖SmithChart.impedancePacket N j (circleMap 0 ρ θ)‖ ^ 2) =
      (fun θ => ‖(2 : ℂ) * (circleMap 0 ρ θ) ^ j / (1 - (circleMap 0 ρ θ) ^ N)‖ ^ 2) := by
    funext θ
    rw [SmithChart.packet_nonzero (hnorm θ) hN hj]
  rw [heq]
  simpa only [← pow_mul, Nat.mul_comm] using nonzero_packet_mean hρ0 hρ1 hN j

/-- The actual zero impedance packet has the computed angular mean. -/
theorem impedance_zero_angular_energy {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N : ℕ} (hN : 0 < N) :
    (2 * Real.pi)⁻¹ * (∫ θ in (0 : ℝ)..2 * Real.pi,
      ‖SmithChart.impedancePacket N 0 (circleMap 0 ρ θ)‖ ^ 2) =
      1 + 4 * ρ ^ (2 * N) / (1 - ρ ^ (2 * N)) := by
  have hnorm (θ : ℝ) : ‖circleMap 0 ρ θ‖ < 1 := by
    simpa [norm_circleMap_zero, abs_of_nonneg hρ0] using hρ1
  have heq : (fun θ : ℝ => ‖SmithChart.impedancePacket N 0 (circleMap 0 ρ θ)‖ ^ 2) =
      (fun θ => ‖((1 : ℂ) + (circleMap 0 ρ θ) ^ N) / (1 - (circleMap 0 ρ θ) ^ N)‖ ^ 2) := by
    funext θ
    rw [SmithChart.packet_zero (hnorm θ) hN]
  rw [heq]
  simpa only [← pow_mul, Nat.mul_comm] using zero_packet_mean hρ0 hρ1 hN

/-- Nonzero-lane angular mean equals the proved squared-coefficient sum. -/
theorem nonzero_angular_eq_coefficient_energy {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N j : ℕ} (hN : 0 < N) (hj : j ≠ 0) :
    (2 * Real.pi)⁻¹ * (∫ θ in (0 : ℝ)..2 * Real.pi,
      ‖SmithChart.impedancePacket N j (circleMap 0 ρ θ)‖ ^ 2) =
      SmithEnergy.impedanceCoefficientEnergy ρ N j := by
  rw [impedance_nonzero_angular_energy hρ0 hρ1 hN hj,
    SmithEnergy.coefficient_energy_nonzero hρ0 hρ1 hN hj]

/-- Zero-lane angular mean equals the proved squared-coefficient sum. -/
theorem zero_angular_eq_coefficient_energy {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N : ℕ} (hN : 0 < N) :
    (2 * Real.pi)⁻¹ * (∫ θ in (0 : ℝ)..2 * Real.pi,
      ‖SmithChart.impedancePacket N 0 (circleMap 0 ρ θ)‖ ^ 2) =
      SmithEnergy.impedanceCoefficientEnergy ρ N 0 := by
  rw [impedance_zero_angular_energy hρ0 hρ1 hN,
    SmithEnergy.coefficient_energy_zero hρ0 hρ1 hN]

end SmithEnergyIntegral
