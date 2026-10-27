module
public import Euler.PacketDerivatives
public import Euler.ResidualNormalization
public import Euler.CriticalCharts
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- Finite packet truncation with each retained source still an exact infinite series. -/
def eulerPacketTruncFunction (r Q : ℕ) (x : ℚ_[2]) : ℚ_[2] :=
  (eulerBeta r:ℚ_[2])⁻¹*qeval (residualNumeratorTrunc r Q) x

lemma eulerPacketTruncFunction_iteratedDeriv (r Q k : ℕ) (x : D) :
    iteratedDeriv k (eulerPacketTruncFunction r Q) (x:ℚ_[2])=
      (eulerBeta r:ℚ_[2])⁻¹*(k.factorial:ℚ_[2])*
        (rjet k (residualNumeratorTrunc r Q) x:ℚ_[2]) :=
  iteratedDeriv_scaled_qeval (residualNumeratorTrunc_restricted r Q) _ k x

/-- Ordinary differentiation does not spend extra packet precision. The factorial gives a gain. -/
theorem eulerResidual_iteratedDeriv_trunc_error (r Q k : ℕ) (x : D) :
    ‖iteratedDeriv k (eulerResidual r) (x:ℚ_[2])-
      iteratedDeriv k (eulerPacketTruncFunction r Q) (x:ℚ_[2])‖≤
      ‖(k.factorial:ℚ_[2])‖/‖(eulerBeta r:ℚ_[2])‖*(1/8:ℝ)^Q := by
  rw [eulerResidual_iteratedDeriv,eulerPacketTruncFunction_iteratedDeriv,← mul_sub,
    ← PadicInt.coe_sub,norm_mul,← PadicInt.norm_def]
  have h := mul_le_mul_of_nonneg_left (residualNumeratorTrunc_rjet_error_norm r Q k x)
    (norm_nonneg ((eulerBeta r:ℚ_[2])⁻¹*(k.factorial:ℚ_[2])))
  convert h using 1 <;> first | rfl | (rw [norm_mul,norm_inv]; ring)

lemma eulerResidual_deriv_trunc_error (r Q : ℕ) (x : D) :
    ‖deriv (eulerResidual r) (x:ℚ_[2])-
      deriv (eulerPacketTruncFunction r Q) (x:ℚ_[2])‖≤
      (1/8:ℝ)^Q/‖(eulerBeta r:ℚ_[2])‖ := by
  simpa only [iteratedDeriv_one,Nat.factorial_one,Nat.cast_one,norm_one,one_div,
    div_eq_mul_inv,mul_comm,one_mul] using eulerResidual_iteratedDeriv_trunc_error r Q 1 x

/-- Exact scaling of every Hasse jet to the actual integral normalized residual. -/
theorem eulerNormalizedResidual_rjet_coe (r : ℕ) (hr : 0<r) (k : ℕ) (x : D) :
    (rjet k (eulerNormalizedResidual r hr) x:ℚ_[2])=
      residualNormalizationFactor r*(rjet k (eulerResidualNumerator r) x:ℚ_[2]) := by
  rw [rjet,coe_reval (restricted_hasseSeries (eulerNormalizedResidual_restricted r hr) k) x]
  unfold qeval
  simp_rw [coeff_hasseSeries,PadicInt.coe_mul,PadicInt.coe_natCast,eulerNormalizedResidual_coeff_coe]
  have hterm (n:ℕ) :
      (Nat.choose (n+k) k:ℚ_[2])*
          (residualNormalizationFactor r*((coeff (n+k) (eulerResidualNumerator r):D):ℚ_[2]))*
          (x:ℚ_[2])^n =
        residualNormalizationFactor r*
          ((Nat.choose (n+k) k:ℚ_[2])*
            ((coeff (n+k) (eulerResidualNumerator r):D):ℚ_[2])*(x:ℚ_[2])^n) := by ring
  simp_rw [hterm]
  have hs := summable_coe_dyadic
    (summable_reval (restricted_hasseSeries (eulerResidualNumerator_restricted r) k) x)
  simp only [coeff_hasseSeries,PadicInt.coe_mul,PadicInt.coe_pow,PadicInt.coe_natCast] at hs
  rw [hs.tsum_mul_left]
  congr 1
  simpa only [qeval,coeff_hasseSeries,PadicInt.coe_mul,PadicInt.coe_natCast,rjet] using
    (coe_reval (restricted_hasseSeries (eulerResidualNumerator_restricted r) k) x).symm

/-- An arbitrary-order packet precision certificate is retained after carry normalization,
with its normalization factor explicit rather than silently discarded. -/
theorem eulerNormalizedResidual_rjet_trunc_error (r : ℕ) (hr : 0<r)
    (Q k : ℕ) (x : D) :
    ‖(rjet k (eulerNormalizedResidual r hr) x:ℚ_[2])-
      residualNormalizationFactor r*(rjet k (residualNumeratorTrunc r Q) x:ℚ_[2])‖≤
      ‖residualNormalizationFactor r‖*(1/8:ℝ)^Q := by
  rw [eulerNormalizedResidual_rjet_coe,← mul_sub,← PadicInt.coe_sub,norm_mul,
    ← PadicInt.norm_def]
  exact mul_le_mul_of_nonneg_left (residualNumeratorTrunc_rjet_error_norm r Q k x)
    (norm_nonneg _)

/-- A finite packet slope witness excludes an actual analytic critical point. -/
theorem eulerResidual_deriv_ne_zero_of_packet_witness (r P Q : ℕ) (hPQ : P≤3*Q)
    (x : D) (hw : redPow P (rjet 1 (residualNumeratorTrunc r Q) x)≠0) :
    deriv (eulerResidual r) (x:ℚ_[2])≠0 := by
  rw [eulerResidual_deriv]
  apply div_ne_zero
  · apply PadicInt.coe_ne_zero.mpr
    intro hz
    have h := residualNumeratorTrunc_rjet_modulus r P Q 1 hPQ x
    rw [hz,map_zero] at h
    exact hw h.symm
  · exact PadicInt.coe_ne_zero.mpr (eulerBeta_ne_zero r)

/-- Complete finite polynomial value/slope certificates exclude critical zeros of the
original infinite Euler residual. The supplied coefficient certificate includes ALL degrees. -/
theorem eulerResidual_no_critical_of_packet_certificate (r P Q : ℕ) (hPQ : P≤3*Q)
    (p : Polynomial (ZMod (2^P)))
    (hc : ∀ n, redPow P (coeff n (residualNumeratorTrunc r Q))=p.coeff n)
    (hp : ∀ y, p.eval y=0 → p.derivative.eval y≠0) (x : D) :
    ¬ CriticalZero (eulerResidual r) (x:ℚ_[2]) := by
  rintro ⟨hv,hd⟩
  have hbeta : (eulerBeta r:ℚ_[2])≠0 := PadicInt.coe_ne_zero.mpr (eulerBeta_ne_zero r)
  have hval : reval (eulerResidualNumerator r) x=0 := by
    apply PadicInt.coe_eq_zero.mp
    rw [eulerResidual_coe] at hv
    exact (div_eq_zero_iff.mp hv).resolve_right hbeta
  have hjet : rjet 1 (eulerResidualNumerator r) x=0 := by
    apply PadicInt.coe_eq_zero.mp
    rw [eulerResidual_deriv] at hd
    exact (div_eq_zero_iff.mp hd).resolve_right hbeta
  have hcoeff (n:ℕ) : redPow P (coeff n (eulerResidualNumerator r))=p.coeff n :=
    (residualNumeratorTrunc_coeff_modulus r P Q hPQ n).trans (hc n)
  have hpval : p.eval (redPow P x)=0 := by
    rw [← reval_residue_polynomial (eulerResidualNumerator_restricted r) P p hcoeff x,
      hval,map_zero]
  apply hp (redPow P x) hpval
  rw [← Polynomial.hasseDeriv_one,
    ← rjet_residue_polynomial (eulerResidualNumerator_restricted r) P p hcoeff 1 x,
    hjet,map_zero]

end Komorebi.Euler
