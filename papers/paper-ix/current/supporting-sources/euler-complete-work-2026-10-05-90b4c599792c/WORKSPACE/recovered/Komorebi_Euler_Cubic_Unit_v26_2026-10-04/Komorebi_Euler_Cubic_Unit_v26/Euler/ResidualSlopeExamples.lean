module
public import Euler.ResidualSlopeTransport
public import Euler.PacketIntegerSlopes
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries

lemma residualPacketSlope_zero (r : ℕ) (x : D) :
    residualPacketSlope r 0 x=eulerBeta r*rjet 1 eulerSource x := by
  simp [residualPacketSlope,residualNumeratorTap,eulerPacket_zero]

lemma eulerPacketTruncFunction_one_deriv (r : ℕ) (x : D) :
    deriv (eulerPacketTruncFunction r 1) (x:ℚ_[2])=deriv (qeval eulerSource) (x:ℚ_[2]) := by
  have h := eulerPacketTruncFunction_iteratedDeriv r 1 1 x
  simp only [iteratedDeriv_one,Nat.factorial_one,Nat.cast_one,mul_one,
    residualNumeratorTrunc_rjet,Finset.sum_range_one,residualPacket_rjet_one,
    residualPacketSlope_zero,PadicInt.coe_mul] at h
  rw [h,deriv_qeval eulerSource_restricted]
  have hb : (eulerBeta r:ℚ_[2])≠0 := PadicInt.coe_ne_zero.mpr (eulerBeta_ne_zero r)
  rw [← mul_assoc,inv_mul_cancel₀ hb,one_mul]

/-- Exact first-derivative norm of the constructed dyadic Euler source. -/
theorem eulerSource_deriv_norm (x : D) :
    ‖deriv (qeval eulerSource) (x:ℚ_[2])‖=(1/2:ℝ) := by
  have hr : redPow 3 (rjet 1 eulerSource x-2)=0 := by
    change red8 (rjet 1 eulerSource x-2)=0
    rw [map_sub,eulerSource_first_jet_mod8]
    change (2:ZMod 8)-red8 ((2:ℕ):D)=0
    rw [map_natCast]
    norm_num
  have he := (redPow_zero_iff_norm 3 (rjet 1 eulerSource x-2)).mp hr
  have hn2 : ‖(2:ℚ_[2])‖=(1/2:ℝ) := by
    have h := norm_two
    rwa [PadicInt.norm_def] at h
  have hs : ‖(rjet 1 eulerSource x:ℚ_[2])-(2:ℚ_[2])‖<‖(2:ℚ_[2])‖ := by
    rw [hn2]
    have hh : ‖(rjet 1 eulerSource x:ℚ_[2])-(2:ℚ_[2])‖≤(1/8:ℝ) := by
      have hn : ‖rjet 1 eulerSource x-2‖≤(1/8:ℝ) := by
        convert he using 1; norm_num
      rw [PadicInt.norm_def,PadicInt.coe_sub] at hn
      norm_cast at hn ⊢
    exact hh.trans_lt (by norm_num)
  rw [deriv_qeval eulerSource_restricted,Padic.norm_eq_of_norm_sub_lt_right hs,hn2]

/-- A concrete infinite family of actual Euler residuals has a nonvanishing slope everywhere.
This is a derivative statement, not an increase in the previously classified root range. -/
theorem eulerResidual_deriv_norm_two_bits (r : ℕ) (hr : 0<r)
    (hbits : binaryDigitSum r≤2) (x : D) :
    ‖deriv (eulerResidual r) (x:ℚ_[2])‖=(1/2:ℝ) := by
  have hb : (1/2:ℝ)≤‖(eulerBeta r:ℚ_[2])‖ := by
    change (1/2:ℝ)≤‖eulerBeta r‖
    rw [eulerBeta_norm r hr]
    calc
      (1/2:ℝ)=(2:ℝ)^(-1:ℤ) := by norm_num
      _ ≤ _ := zpow_le_zpow_right₀ (by norm_num : (1:ℝ)≤2) (by omega)
  have he := eulerResidual_deriv_trunc_error r 1 x
  rw [eulerPacketTruncFunction_one_deriv] at he
  simp only [pow_one] at he
  have hs : ‖deriv (eulerResidual r) (x:ℚ_[2])-
      deriv (qeval eulerSource) (x:ℚ_[2])‖<
      ‖deriv (qeval eulerSource) (x:ℚ_[2])‖ := by
    rw [eulerSource_deriv_norm]
    calc
      _ ≤ (1/8:ℝ)/‖(eulerBeta r:ℚ_[2])‖ := he
      _ ≤ (1/8:ℝ)/(1/2) :=
        div_le_div_of_nonneg_left (by norm_num) (by norm_num) hb
      _ < 1/2 := by norm_num
  rw [Padic.norm_eq_of_norm_sub_lt_right hs,eulerSource_deriv_norm]

theorem eulerResidual_deriv_ne_zero_two_bits (r : ℕ) (hr : 0<r)
    (hbits : binaryDigitSum r≤2) (x : D) :
    deriv (eulerResidual r) (x:ℚ_[2])≠0 := by
  intro h
  have hn := eulerResidual_deriv_norm_two_bits r hr hbits x
  rw [h,norm_zero] at hn
  norm_num at hn

/-- The same slope witness applies to the actual normalized residual. -/
theorem eulerNormalizedResidual_no_critical_of_packet_certificate (r P Q : ℕ)
    (hr : 0<r) (hPQ : P≤3*Q) (p : Polynomial (ZMod (2^P)))
    (hc : ∀ n, redPow P (coeff n (residualNumeratorTrunc r Q))=p.coeff n)
    (hp : ∀ y, p.eval y=0 → p.derivative.eval y≠0) (x : D) :
    ¬ CriticalZero (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2]) := by
  rw [eulerNormalizedResidual_critical_iff]
  exact eulerResidual_no_critical_of_packet_certificate r P Q hPQ p hc hp x

end Komorebi.Euler
