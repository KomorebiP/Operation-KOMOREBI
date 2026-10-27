module
public import Euler.TerminalLowerSeries
@[expose] public section
noncomputable section
set_option maxHeartbeats 1000000
namespace Komorebi.Euler
open PowerSeries

lemma eulerNormalizedResidual_coe_numerator (r : ℕ) (hr : 0<r) (x : D) :
    (reval (eulerNormalizedResidual r hr) x:ℚ_[2])=
      residualNormalizationFactor r*(reval (eulerResidualNumerator r) x:ℚ_[2]) := by
  rw [eulerNormalizedResidual_reval,eulerResidual_coe,residualNormalizationFactor]
  ring

lemma terminalLowerSeries_coe_numerator (r : ℕ) (hr : 0<r) (x : D) :
    (reval (terminalLowerSeries r hr) x:ℚ_[2])=
      ((2:ℚ_[2])^(-terminalLowerMinimum (residualTerminalIndex r))/(eulerBeta r:ℚ_[2]))*
        ∑ q∈Finset.range (residualTerminalIndex r),(residualPacketValue r q x:ℚ_[2]) := by
  rw [terminalLowerSeries_reval,PadicInt.coe_sum,← Fin.sum_univ_eq_sum_range]
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro q _
  simp only [PadicInt.coe_mul,terminalLowerScalarInt,terminalLowerScalar,
    residualScalarRat_coe,residualPacketValue,residualNumeratorTap,
    PadicInt.coe_pow]
  change (2:ℚ_[2])^(-terminalLowerMinimum (residualTerminalIndex r))*
      ((8:ℚ_[2])^q.val*(eulerBeta (r+q.val):ℚ_[2])/(eulerBeta r:ℚ_[2]))*
      (((eulerPacket q.val).eval x:D):ℚ_[2])*(reval eulerSource (x-(q.val:D)):ℚ_[2])=_
  have h8 : ((8:D):ℚ_[2])=8 := rfl
  rw [h8]
  ring

lemma terminalNormalization_scale (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) :
    residualNormalizationFactor r=
      (2:ℚ_[2])^(terminalWallDistance r)*
      ((2:ℚ_[2])^(-terminalLowerMinimum (residualTerminalIndex r))/(eulerBeta r:ℚ_[2])) := by
  rw [residualNormalizationFactor,residualCarryMinimum_eq_lower_sub_distance r hr hj,
    show -(terminalLowerMinimum (residualTerminalIndex r)-(terminalWallDistance r:ℤ))=
      (terminalWallDistance r:ℤ)+(-terminalLowerMinimum (residualTerminalIndex r)) by ring,
    zpow_add₀ (by norm_num : (2:ℚ_[2])≠0),zpow_natCast]
  ring

lemma terminalUpperSeries_reval (r : ℕ) (hr : 0<r) (x : D) :
    (reval (terminalUpperSeries r hr) x:ℚ_[2])=
      normalizedResidualScalar r (residualTerminalIndex r)*
        eulerResidual (r+residualTerminalIndex r) (x:ℚ_[2]) := by
  rw [terminalUpperSeries,reval_C_mul (eulerNormalizedResidual_restricted _ (by omega)),
    PadicInt.coe_mul,← terminal_shift_H_eq_G r hr x]
  rfl

lemma terminalScalar_numerator_factor (r : ℕ) (_hr : 0<r) (x : D) :
    normalizedResidualScalar r (residualTerminalIndex r)*
      eulerResidual (r+residualTerminalIndex r) (x:ℚ_[2])=
    residualNormalizationFactor r*(8:ℚ_[2])^(residualTerminalIndex r)*
      (reval (eulerResidualNumerator (r+residualTerminalIndex r)) x:ℚ_[2]) := by
  rw [normalizedResidualScalar,residualScalarRat_coe,eulerResidual_coe,
    residualNormalizationFactor]
  have hb : (eulerBeta (r+residualTerminalIndex r):ℚ_[2])≠0 :=
    (PadicInt.coe_eq_zero).not.mpr (eulerBeta_ne_zero _)
  field_simp

/-- Exact normal form of the ACTUAL Euler residual, on the entire dyadic unit disc. -/
theorem eulerNormalizedResidual_terminal_form (r : ℕ) (hr : 0<r)
    (hj : 0<residualTerminalIndex r) (x : D) :
    reval (eulerNormalizedResidual r hr) x=
      (eulerPacket (residualTerminalIndex r)).eval x*
        reval (terminalUpperSeries r hr) (x-(residualTerminalIndex r:D))+
      (2:D)^(terminalWallDistance r)*reval (terminalLowerSeries r hr) x := by
  apply Subtype.ext
  rw [PadicInt.coe_add,PadicInt.coe_mul,PadicInt.coe_mul,PadicInt.coe_pow]
  rw [eulerNormalizedResidual_coe_numerator,terminalUpperSeries_reval,
    terminalScalar_numerator_factor r hr,terminalLowerSeries_coe_numerator]
  have h := congrArg (fun z:D => (z:ℚ_[2]))
    (eulerResidualNumerator_block r (residualTerminalIndex r) x)
  simp only [PadicInt.coe_add,PadicInt.coe_mul,PadicInt.coe_pow,PadicInt.coe_sum] at h
  rw [h,terminalNormalization_scale r hr hj]
  change _= (((eulerPacket (residualTerminalIndex r)).eval x:D):ℚ_[2])*
    (((2:ℚ_[2])^(terminalWallDistance r)*
      ((2:ℚ_[2])^(-terminalLowerMinimum (residualTerminalIndex r))/(eulerBeta r:ℚ_[2])))*
      (8:ℚ_[2])^(residualTerminalIndex r)*
      (reval (eulerResidualNumerator (r+residualTerminalIndex r))
        (x-(residualTerminalIndex r:D)):ℚ_[2]))+
    (2:ℚ_[2])^(terminalWallDistance r)*
      (((2:ℚ_[2])^(-terminalLowerMinimum (residualTerminalIndex r))/(eulerBeta r:ℚ_[2]))*
        ∑q∈Finset.range (residualTerminalIndex r),(residualPacketValue r q x:ℚ_[2]))
  have h8 : ((8:D):ℚ_[2])=8 := rfl
  rw [h8]
  ring

/-- At every skeleton integer the terminal packet vanishes EXACTLY. -/
theorem eulerNormalizedResidual_at_skeleton (r i : ℕ) (hr : 0<r)
    (hi : i<residualTerminalIndex r) :
    reval (eulerNormalizedResidual r hr) (i:D)=
      (2:D)^(terminalWallDistance r)*reval (terminalLowerSeries r hr) (i:D) := by
  rw [eulerNormalizedResidual_terminal_form r hr (by omega)]
  rw [eulerPacket_eval_nat_zero _ _ hi,zero_mul,zero_add]

end Komorebi.Euler
