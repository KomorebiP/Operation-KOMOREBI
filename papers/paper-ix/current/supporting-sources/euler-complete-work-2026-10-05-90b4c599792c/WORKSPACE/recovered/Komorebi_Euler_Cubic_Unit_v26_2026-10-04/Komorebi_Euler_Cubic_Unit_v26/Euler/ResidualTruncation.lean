module
public import Euler.ResidualRows
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- Finite packet truncation. Each retained source is still its actual infinite analytic series. -/
def residualNumeratorTrunc (r Q : ℕ) : Series :=
  ∑ q ∈ Finset.range Q, residualPacketSeries r q

lemma residualNumeratorTrunc_restricted (r Q : ℕ) :
    Restricted (residualNumeratorTrunc r Q) := by
  induction Q with
  | zero => simpa [residualNumeratorTrunc] using PowerSeries.isRestricted_zero (R:=D) 1
  | succ Q ih =>
    simpa only [residualNumeratorTrunc,Finset.sum_range_succ] using
      PowerSeries.isRestricted.add 1 ih (residualPacketSeries_restricted r Q)

lemma residualNumeratorTrunc_coeff (r Q n : ℕ) :
    coeff n (residualNumeratorTrunc r Q)=
      ∑ q ∈ Finset.range Q, coeff n (residualPacketSeries r q) := by
  simp only [residualNumeratorTrunc,map_sum]

lemma residualNumeratorTrunc_error_coeff (r Q n : ℕ) :
    coeff n (eulerResidualNumerator r-residualNumeratorTrunc r Q)=
      ∑' q, coeff n (residualPacketSeries r (q+Q)) := by
  rw [map_sub,coeff_eulerResidualNumerator,residualNumeratorTrunc_coeff]
  have h := (residualPacketSeries_summable_coeff r n).sum_add_tsum_nat_add Q
  exact sub_eq_iff_eq_add.mpr (by simpa only [add_comm] using h.symm)

/-- Uniform omitted-packet bound, on every Taylor coefficient at once. -/
theorem residualNumeratorTrunc_error_coeff_norm (r Q n : ℕ) :
    ‖coeff n (eulerResidualNumerator r-residualNumeratorTrunc r Q)‖≤(1/8:ℝ)^Q := by
  rw [residualNumeratorTrunc_error_coeff]
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro q
  exact (residualPacketSeries_coeff_uniform r (q+Q) n).trans
    (pow_le_pow_of_le_one (by norm_num) (by norm_num) (by omega))

/-- Uniform functional error on the entire dyadic unit disc. -/
theorem residualNumeratorTrunc_error_norm (r Q : ℕ) (x : D) :
    ‖reval (eulerResidualNumerator r) x-reval (residualNumeratorTrunc r Q) x‖≤(1/8:ℝ)^Q := by
  rw [← reval_sub (eulerResidualNumerator_restricted r) (residualNumeratorTrunc_restricted r Q)]
  unfold reval
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro n
  rw [norm_mul]
  exact (mul_le_of_le_one_right (norm_nonneg _) (PadicInt.norm_le_one _)).trans
    (residualNumeratorTrunc_error_coeff_norm r Q n)

lemma one_eighth_pow_le_two_zpow (P Q : ℕ) (hPQ : P≤3*Q) :
    (1/8:ℝ)^Q≤(2:ℝ)^(-(P:ℤ)) := by
  have he : (1/8:ℝ)^Q=(2:ℝ)^(-((3*Q:ℕ):ℤ)) := by
    rw [zpow_neg,zpow_natCast,pow_mul]
    norm_num [div_pow]
  rw [he]
  apply zpow_le_zpow_right₀ (by norm_num : (1:ℝ)≤2)
  omega

/-- A complete coefficient certificate, including every uncomputed packet. -/
theorem residualNumeratorTrunc_coeff_modulus (r P Q : ℕ) (hPQ : P≤3*Q) (n : ℕ) :
    redPow P (coeff n (eulerResidualNumerator r))=
      redPow P (coeff n (residualNumeratorTrunc r Q)) := by
  apply redPow_eq_of_norm_sub_le P
  rw [← map_sub]
  exact (residualNumeratorTrunc_error_coeff_norm r Q n).trans
    (one_eighth_pow_le_two_zpow P Q hPQ)

/-- The full analytic residual numerator and its finite packet truncation agree modulo 2^P. -/
theorem residualNumeratorTrunc_value_modulus (r P Q : ℕ) (hPQ : P≤3*Q) (x : D) :
    redPow P (reval (eulerResidualNumerator r) x)=
      redPow P (reval (residualNumeratorTrunc r Q) x) := by
  exact redPow_eq_of_norm_sub_le P
    ((residualNumeratorTrunc_error_norm r Q x).trans (one_eighth_pow_le_two_zpow P Q hPQ))

/-- Division by beta_r has an explicit norm cost; H_r is not silently treated as integral. -/
theorem eulerResidualTrunc_error_norm (r Q : ℕ) (x : D) :
    ‖eulerResidual r (x:ℚ_[2])-
      (reval (residualNumeratorTrunc r Q) x:ℚ_[2])/(eulerBeta r:ℚ_[2])‖≤
      (1/8:ℝ)^Q/‖(eulerBeta r:ℚ_[2])‖ := by
  rw [eulerResidual_coe,← sub_div,norm_div]
  apply div_le_div_of_nonneg_right _ (norm_nonneg _)
  change ‖((reval (eulerResidualNumerator r) x-reval (residualNumeratorTrunc r Q) x:D):ℚ_[2])‖≤_
  rw [← PadicInt.norm_def]
  exact residualNumeratorTrunc_error_norm r Q x

end Komorebi.Euler
