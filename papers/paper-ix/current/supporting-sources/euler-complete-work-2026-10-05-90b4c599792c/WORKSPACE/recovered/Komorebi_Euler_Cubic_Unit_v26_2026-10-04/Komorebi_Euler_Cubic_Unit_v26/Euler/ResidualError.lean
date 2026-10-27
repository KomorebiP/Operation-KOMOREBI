module
public import Euler.ResidualReduction
@[expose] public section
noncomputable section
namespace Komorebi.Euler

/-- Doubling both binomial indices preserves the exact dyadic valuation. -/
lemma choose_double_padicVal (N r : ℕ) (h : r≤N) :
    padicValNat 2 ((2*N).choose (2*r))=padicValNat 2 (N.choose r) := by
  have h1 := sub_one_mul_padicValNat_choose_eq_sub_sum_digits (p:=2)
    (n:=2*N) (k:=2*r) (by omega)
  have h2 := sub_one_mul_padicValNat_choose_eq_sub_sum_digits (p:=2) h
  norm_num only [Nat.reduceSub,one_mul] at h1 h2
  change padicValNat 2 ((2*N).choose (2*r))=
    binaryDigitSum (2*r)+binaryDigitSum (2*N-2*r)-binaryDigitSum (2*N) at h1
  rw [show 2*N-2*r=2*(N-r) by omega,
    binaryDigitSum_two_mul,binaryDigitSum_two_mul,binaryDigitSum_two_mul] at h1
  exact h1.trans h2.symm

lemma choose_double_norm (N r : ℕ) (h : r≤N) :
    ‖((2*N).choose (2*r):ℚ_[2])‖=‖(N.choose r:ℚ_[2])‖ := by
  rw [Padic.norm_eq_zpow_neg_valuation (by exact_mod_cast
      (Nat.choose_pos (show 2*r≤2*N by omega)).ne'),
    Padic.norm_eq_zpow_neg_valuation (by exact_mod_cast (Nat.choose_pos h).ne'),
    Padic.valuation_natCast,Padic.valuation_natCast,choose_double_padicVal N r h]

/-- Exact norm form of the entire Euler row: valid even when the tail is zero. -/
theorem signedEuler_error_normalized_norm (r N : ℕ) (hr : 0<r) (hN : r≤N) :
    ‖signedEulerEven N-reconstructionTrunc (r-1) N‖=
      (2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r))*
      ‖(N.choose r:ℚ_[2])‖*
      ‖reval (eulerNormalizedResidual r hr) ((N-r:ℕ):D)‖ := by
  have hp : ‖(2:ℚ_[2])‖=(2:ℝ)⁻¹ := by
    have h := Padic.norm_p (p:=2)
    norm_num at h ⊢
    exact h
  rw [PadicInt.norm_def,signedEuler_error_normalized r N hr hN,
    norm_mul,norm_mul,norm_mul,← PadicInt.norm_def,eulerKappa_norm r hr,
    choose_double_norm N r hN,norm_zpow,hp,inv_zpow,← zpow_neg,
    ← PadicInt.norm_def]
  have he : (2:ℝ)^(-(4*(r:ℤ)-1))*(2:ℝ)^(-residualCarryMinimum r)=
      (2:ℝ)^(-(4*(r:ℤ)-1+residualCarryMinimum r)) := by
    rw [← zpow_add₀ (by norm_num : (2:ℝ)≠0)]
    congr 1
    ring
  calc
    _ = ((2:ℝ)^(-(4*(r:ℤ)-1))*(2:ℝ)^(-residualCarryMinimum r))*
      ‖(N.choose r:ℚ_[2])‖*‖reval (eulerNormalizedResidual r hr) ((N-r:ℕ):D)‖ := by ring
    _ = _ := by rw [he]

/-- Exact valuation version, with a nonzero condition because Lean's valuation of zero is zero. -/
theorem signedEuler_error_normalized_valuation (r N : ℕ) (hr : 0<r) (hN : r≤N)
    (hg : reval (eulerNormalizedResidual r hr) ((N-r:ℕ):D)≠0) :
    Padic.valuation ((signedEulerEven N-reconstructionTrunc (r-1) N:D):ℚ_[2])=
      4*(r:ℤ)-1+(padicValNat 2 (N.choose r):ℤ)+residualCarryMinimum r+
        Padic.valuation (reval (eulerNormalizedResidual r hr) ((N-r:ℕ):D):ℚ_[2]) := by
  have hk : (eulerKappa r:ℚ_[2])≠0 := PadicInt.coe_ne_zero.mpr (eulerKappa_ne_zero r)
  have hc : ((2*N).choose (2*r):ℚ_[2])≠0 := by
    exact_mod_cast (Nat.choose_pos (show 2*r≤2*N by omega)).ne'
  have hz : (2:ℚ_[2])^residualCarryMinimum r≠0 := zpow_ne_zero _ (by norm_num)
  have hg' := PadicInt.coe_ne_zero.mpr hg
  have hp : Padic.valuation (2:ℚ_[2])=1 := Padic.valuation_p
  rw [signedEuler_error_normalized r N hr hN,
    Padic.valuation_mul (mul_ne_zero (mul_ne_zero hk hc) hz) hg',
    Padic.valuation_mul (mul_ne_zero hk hc) hz,Padic.valuation_mul hk hc,
    eulerKappa_valuation r hr,Padic.valuation_natCast,choose_double_padicVal N r hN,
    Padic.valuation_zpow,hp,mul_one]

/-- Root equivalence uses the constructed G_r, not an unrelated local polynomial. -/
theorem signedEuler_error_zero_iff_normalized (r N : ℕ) (hr : 0<r) (hN : r≤N) :
    signedEulerEven N=reconstructionTrunc (r-1) N ↔
      reval (eulerNormalizedResidual r hr) ((N-r:ℕ):D)=0 := by
  rw [signedEuler_error_zero_iff_residual r N hr hN]
  have h := eulerResidual_from_normalized r hr ((N-r:ℕ):D)
  simp only [PadicInt.coe_natCast] at h
  rw [h,mul_eq_zero]
  have hp : (2:ℚ_[2])^residualCarryMinimum r≠0 := zpow_ne_zero _ (by norm_num)
  simp only [hp,false_or,PadicInt.coe_eq_zero]

end Komorebi.Euler
