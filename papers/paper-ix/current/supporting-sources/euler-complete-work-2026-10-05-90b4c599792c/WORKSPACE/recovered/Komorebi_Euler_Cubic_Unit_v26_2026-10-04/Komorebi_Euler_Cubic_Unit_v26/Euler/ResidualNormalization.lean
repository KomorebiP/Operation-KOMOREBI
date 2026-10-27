module
public import Euler.ResidualMinimum
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The common scalar converting J_r to the carry-normalized G_r. -/
def residualNormalizationFactor (r : ℕ) : ℚ_[2] :=
  (2:ℚ_[2])^(-residualCarryMinimum r)/(eulerBeta r:ℚ_[2])

def normalizedResidualScalar (r q : ℕ) : ℚ_[2] :=
  (2:ℚ_[2])^(-residualCarryMinimum r)*(residualScalarRat r q:ℚ_[2])

lemma normalizedResidualScalar_ne_zero (r q : ℕ) : normalizedResidualScalar r q≠0 := by
  apply mul_ne_zero (zpow_ne_zero _ (by norm_num))
  exact_mod_cast residualScalarRat_ne_zero r q

lemma normalizedResidualScalar_val (r q : ℕ) (hr : 0<r) :
    Padic.valuation (normalizedResidualScalar r q)=
      residualCarryCost r q-residualCarryMinimum r := by
  have hp : Padic.valuation (2:ℚ_[2])=1 := Padic.valuation_p
  rw [normalizedResidualScalar,Padic.valuation_mul (zpow_ne_zero _ (by norm_num))
    (by exact_mod_cast residualScalarRat_ne_zero r q),Padic.valuation_zpow,
    hp,Padic.valuation_ratCast,residualScalarRat_val r q hr]
  ring

/-- Every normalized packet scalar is integral, by the actual global-minimum theorem. -/
lemma normalizedResidualScalar_norm_le_one (r q : ℕ) (hr : 0<r) :
    ‖normalizedResidualScalar r q‖≤1 := by
  apply (Padic.norm_le_one_iff_val_nonneg _).mpr
  rw [normalizedResidualScalar_val r q hr]
  exact sub_nonneg.mpr (residualCarryMinimum_le r q hr)

lemma residualNormalizationFactor_packet (r q n : ℕ) :
    residualNormalizationFactor r*((coeff n (residualPacketSeries r q):D):ℚ_[2])=
      normalizedResidualScalar r q*
        ((coeff n ((eulerPacket q:Series)*sourceShift (-(q:D))):D):ℚ_[2]) := by
  rw [residualPacketSeries,coeff_C_mul]
  simp only [PadicInt.coe_mul,residualNumeratorTap,PadicInt.coe_pow,
    normalizedResidualScalar,residualScalarRat_coe,residualNormalizationFactor]
  change (2:ℚ_[2])^(-residualCarryMinimum r)/(eulerBeta r:ℚ_[2])*
      ((8:ℚ_[2])^q*(eulerBeta (r+q):ℚ_[2])*
        ((coeff n ((eulerPacket q:Series)*sourceShift (-(q:D))):D):ℚ_[2]))=_
  ring

lemma residualNormalizationFactor_coeff_norm (r n : ℕ) (hr : 0<r) :
    ‖residualNormalizationFactor r*((coeff n (eulerResidualNumerator r):D):ℚ_[2])‖≤1 := by
  have hh := ((residualPacketSeries_summable_coeff r n).hasSum.map
    (PadicInt.Coe.ringHom : D →+* ℚ_[2]) PadicInt.isOpenEmbedding_coe.continuous).mul_left
      (residualNormalizationFactor r)
  change HasSum (fun q => residualNormalizationFactor r*
    ((coeff n (residualPacketSeries r q):D):ℚ_[2]))
    (residualNormalizationFactor r*((∑'q, coeff n (residualPacketSeries r q):D):ℚ_[2])) at hh
  have he : HasSum (fun q => residualNormalizationFactor r*
      ((coeff n (residualPacketSeries r q):D):ℚ_[2]))
      (residualNormalizationFactor r*((coeff n (eulerResidualNumerator r):D):ℚ_[2])) := by
    simpa only [coeff_eulerResidualNumerator] using hh
  rw [← he.tsum_eq]
  apply IsUltrametricDist.norm_tsum_le_of_forall_le
  intro q
  rw [residualNormalizationFactor_packet,norm_mul]
  have hc : ‖((coeff n ((eulerPacket q:Series)*sourceShift (-(q:D))):D):ℚ_[2])‖≤1 := by
    rw [← PadicInt.norm_def]
    exact PadicInt.norm_le_one _
  exact (mul_le_of_le_one_right (norm_nonneg _) hc).trans
    (normalizedResidualScalar_norm_le_one r q hr)

/-- Actual integral Taylor coefficients after normalization; the bound is proved, not a field. -/
def normalizedResidualCoefficient (r : ℕ) (hr : 0<r) (n : ℕ) : D :=
  ⟨residualNormalizationFactor r*((coeff n (eulerResidualNumerator r):D):ℚ_[2]),
    residualNormalizationFactor_coeff_norm r n hr⟩

/-- The genuine carry-normalized residual G_r in Z_2[[X]]. -/
def eulerNormalizedResidual (r : ℕ) (hr : 0<r) : Series :=
  mk (normalizedResidualCoefficient r hr)

lemma eulerNormalizedResidual_coeff_coe (r : ℕ) (hr : 0<r) (n : ℕ) :
    ((coeff n (eulerNormalizedResidual r hr):D):ℚ_[2])=
      residualNormalizationFactor r*((coeff n (eulerResidualNumerator r):D):ℚ_[2]) := by
  simp only [eulerNormalizedResidual,coeff_mk,normalizedResidualCoefficient]

/-- Carry normalization preserves restricted convergence; G_r is integral on the whole disc. -/
theorem eulerNormalizedResidual_restricted (r : ℕ) (hr : 0<r) :
    Restricted (eulerNormalizedResidual r hr) := by
  rw [restricted_iff]
  have h := (restricted_iff _).mp (eulerResidualNumerator_restricted r)
  have hn : ∀ n, ‖coeff n (eulerNormalizedResidual r hr)‖=
      ‖residualNormalizationFactor r‖*‖coeff n (eulerResidualNumerator r)‖ := by
    intro n
    rw [PadicInt.norm_def,eulerNormalizedResidual_coeff_coe,norm_mul,← PadicInt.norm_def]
  simp_rw [hn]
  simpa only [mul_zero] using h.const_mul ‖residualNormalizationFactor r‖

/-- Exact analytic normalization identity, with no omitted packets or hypothetical series. -/
theorem eulerNormalizedResidual_reval (r : ℕ) (hr : 0<r) (x : D) :
    (reval (eulerNormalizedResidual r hr) x:ℚ_[2])=
      (2:ℚ_[2])^(-residualCarryMinimum r)*eulerResidual r (x:ℚ_[2]) := by
  rw [coe_reval (eulerNormalizedResidual_restricted r hr) x]
  unfold qeval
  simp_rw [eulerNormalizedResidual_coeff_coe,mul_assoc]
  have hs := (summable_reval (eulerResidualNumerator_restricted r) x).hasSum.map
    (PadicInt.Coe.ringHom : D →+* ℚ_[2]) PadicInt.isOpenEmbedding_coe.continuous
  change HasSum (fun n => ((coeff n (eulerResidualNumerator r)*x^n:D):ℚ_[2]))
    ((reval (eulerResidualNumerator r) x:D):ℚ_[2]) at hs
  have hsum : Summable (fun n => ((coeff n (eulerResidualNumerator r):D):ℚ_[2])*(x:ℚ_[2])^n) := by
    simpa only [PadicInt.coe_mul,PadicInt.coe_pow] using hs.summable
  rw [hsum.tsum_mul_left,residualNormalizationFactor]
  change _=(2:ℚ_[2])^(-residualCarryMinimum r)*
    ((∑'n, ((coeff n (eulerResidualNumerator r):D):ℚ_[2])*(x:ℚ_[2])^n)/(eulerBeta r:ℚ_[2]))
  ring

/-- The original H_r is recovered by the inverse integer power of two. -/
theorem eulerResidual_from_normalized (r : ℕ) (hr : 0<r) (x : D) :
    eulerResidual r (x:ℚ_[2])=
      (2:ℚ_[2])^(residualCarryMinimum r)*(reval (eulerNormalizedResidual r hr) x:ℚ_[2]) := by
  rw [eulerNormalizedResidual_reval,← mul_assoc,← zpow_add₀ (by norm_num : (2:ℚ_[2])≠0)]
  simp

/-- Exact whole Euler error in the carry-normalized coordinate. -/
theorem signedEuler_error_normalized (r N : ℕ) (hr : 0<r) (hN : r≤N) :
    ((signedEulerEven N-reconstructionTrunc (r-1) N:D):ℚ_[2])=
      (eulerKappa r:ℚ_[2])*((2*N).choose (2*r):ℚ_[2])*
      (2:ℚ_[2])^(residualCarryMinimum r)*
        (reval (eulerNormalizedResidual r hr) ((N-r:ℕ):D):ℚ_[2]) := by
  rw [signedEuler_error_residual_of_le r N hr hN]
  have h := eulerResidual_from_normalized r hr ((N-r:ℕ):D)
  simp only [PadicInt.coe_natCast] at h
  rw [h]
  ring

end Komorebi.Euler
