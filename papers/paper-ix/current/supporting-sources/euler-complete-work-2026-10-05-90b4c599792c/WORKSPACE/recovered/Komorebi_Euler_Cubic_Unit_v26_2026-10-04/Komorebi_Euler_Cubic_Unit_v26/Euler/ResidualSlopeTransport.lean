module
public import Euler.PacketDerivativeBounds
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open PowerSeries Filter
open scoped Topology

/-- The exact one-step transfer coefficient, independent of the row variable. -/
def residualStepScalar (r : ℕ) : ℚ_[2] :=
  8*(eulerBeta (r+1):ℚ_[2])/(eulerBeta r:ℚ_[2])

lemma residualStepScalar_ne_zero (r : ℕ) : residualStepScalar r≠0 := by
  apply div_ne_zero
  · exact mul_ne_zero (by norm_num) (PadicInt.coe_ne_zero.mpr (eulerBeta_ne_zero _))
  · exact PadicInt.coe_ne_zero.mpr (eulerBeta_ne_zero _)

/-- Derivative of the complete one-step Euler residual identity. -/
theorem eulerResidual_deriv_succ (r : ℕ) (x : D) :
    deriv (eulerResidual r) (x:ℚ_[2])=
      deriv (qeval eulerSource) (x:ℚ_[2])+
      residualStepScalar r*
        ((4*(x:ℚ_[2])-1)*eulerResidual (r+1) ((x:ℚ_[2])-1)+
          (x:ℚ_[2])*(2*(x:ℚ_[2])-1)*
            deriv (eulerResidual (r+1)) ((x:ℚ_[2])-1)) := by
  have he : eulerResidual r =ᶠ[𝓝 (x:ℚ_[2])]
      (fun y : ℚ_[2] => qeval eulerSource y+
        residualStepScalar r*(y*(2*y-1)*eulerResidual (r+1) (y-1))) := by
    apply eventuallyEq_of_eq_on_dyadic
    intro z
    rw [eulerResidual_succ,coe_reval eulerSource_restricted]
    unfold residualStepScalar
    ring
  have ha := (hasDerivAt_qeval eulerSource_restricted x).differentiableAt.hasDerivAt
  have hn := (eulerResidual_hasDerivAt (r+1) (x-1)).differentiableAt.hasDerivAt
  simp only [PadicInt.coe_sub,PadicInt.coe_one] at hn
  have hshift : HasDerivAt (fun y : ℚ_[2] => eulerResidual (r+1) (y-1))
      (deriv (eulerResidual (r+1)) ((x:ℚ_[2])-1)) (x:ℚ_[2]) := by
    convert hn.comp (x:ℚ_[2]) ((hasDerivAt_id (x:ℚ_[2])).sub_const 1) using 1 <;>
      first | rfl | simp only [mul_one]
  have hp : HasDerivAt (fun y : ℚ_[2] => y*(2*y-1)) (4*(x:ℚ_[2])-1) (x:ℚ_[2]) := by
    convert (hasDerivAt_id (x:ℚ_[2])).mul
      (((hasDerivAt_id (x:ℚ_[2])).const_mul 2).sub_const 1) using 1 <;>
      first | rfl | (simp only [id_eq]; ring)
  have hd := (ha.add ((hp.mul hshift).const_mul (residualStepScalar r))).congr_of_eventuallyEq he
  exact hd.deriv

/-- A denominator-free source/continuation Wronskian. -/
def residualStepWronskian (r : ℕ) (x : ℚ_[2]) : ℚ_[2] :=
  qeval eulerSource x*
    ((4*x-1)*eulerResidual (r+1) (x-1)+x*(2*x-1)*deriv (eulerResidual (r+1)) (x-1))-
  deriv (qeval eulerSource) x*x*(2*x-1)*eulerResidual (r+1) (x-1)

/-- Exact elimination of the transfer coefficient; valid even when the polynomial factor vanishes. -/
theorem residualStepWronskian_identity (r : ℕ) (x : D) :
    residualStepScalar r*residualStepWronskian r (x:ℚ_[2])=
      qeval eulerSource (x:ℚ_[2])*deriv (eulerResidual r) (x:ℚ_[2])-
        deriv (qeval eulerSource) (x:ℚ_[2])*eulerResidual r (x:ℚ_[2]) := by
  rw [eulerResidual_deriv_succ,eulerResidual_succ,coe_reval eulerSource_restricted]
  unfold residualStepScalar residualStepWronskian
  ring

/-- At an Euler residual zero, slope cancellation is EXACTLY the Wronskian obstruction.
No nonvanishing conclusion for that Wronskian is assumed or asserted. -/
theorem eulerResidual_critical_iff_wronskian (r : ℕ) (x : D) :
    CriticalZero (eulerResidual r) (x:ℚ_[2]) ↔
      eulerResidual r (x:ℚ_[2])=0 ∧ residualStepWronskian r (x:ℚ_[2])=0 := by
  have hc := residualStepScalar_ne_zero r
  have ha : qeval eulerSource (x:ℚ_[2])≠0 := by
    rw [← coe_reval eulerSource_restricted]
    exact PadicInt.coe_ne_zero.mpr (eulerSource_reval_ne_zero x)
  constructor
  · rintro ⟨hv,hd⟩
    refine ⟨hv,?_⟩
    have h := residualStepWronskian_identity r x
    rw [hv,hd,mul_zero,mul_zero,sub_zero] at h
    exact (mul_eq_zero.mp h).resolve_left hc
  · rintro ⟨hv,hw⟩
    refine ⟨hv,?_⟩
    have h := residualStepWronskian_identity r x
    rw [hv,hw,mul_zero,mul_zero,sub_zero] at h
    exact (mul_eq_zero.mp h.symm).resolve_left ha

/-- A genuine nonzero Wronskian witness excludes a critical Euler zero. -/
theorem eulerResidual_no_critical_of_wronskian (r : ℕ) (x : D)
    (hw : residualStepWronskian r (x:ℚ_[2])≠0) :
    ¬ CriticalZero (eulerResidual r) (x:ℚ_[2]) := by
  rw [eulerResidual_critical_iff_wronskian]
  exact fun h => hw h.2

/-- Carry normalization is a constant gauge on EVERY ordinary derivative order. -/
theorem eulerNormalizedResidual_iteratedDeriv (r : ℕ) (hr : 0<r) (k : ℕ) (x : D) :
    iteratedDeriv k (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=
      (2:ℚ_[2])^(-residualCarryMinimum r)*
        iteratedDeriv k (eulerResidual r) (x:ℚ_[2]) := by
  rw [iteratedDeriv_qeval (eulerNormalizedResidual_restricted r hr),
    eulerNormalizedResidual_rjet_coe,eulerResidual_iteratedDeriv]
  unfold residualNormalizationFactor
  ring

lemma eulerNormalizedResidual_deriv (r : ℕ) (hr : 0<r) (x : D) :
    deriv (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2])=
      (2:ℚ_[2])^(-residualCarryMinimum r)*deriv (eulerResidual r) (x:ℚ_[2]) := by
  simpa only [iteratedDeriv_one] using eulerNormalizedResidual_iteratedDeriv r hr 1 x

/-- The actual H_r and G_r have exactly the same analytic critical zeros. -/
theorem eulerNormalizedResidual_critical_iff (r : ℕ) (hr : 0<r) (x : D) :
    CriticalZero (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2]) ↔
      CriticalZero (eulerResidual r) (x:ℚ_[2]) := by
  have hval := eulerNormalizedResidual_iteratedDeriv r hr 0 x
  simp only [iteratedDeriv_zero] at hval
  have hc : (2:ℚ_[2])^(-residualCarryMinimum r)≠0 := zpow_ne_zero _ (by norm_num)
  unfold CriticalZero
  rw [hval,eulerNormalizedResidual_deriv]
  simp only [mul_eq_zero,hc,false_or]

/-- A root has no normalization-dependent value/slope ambiguity. -/
theorem eulerNormalizedResidual_critical_iff_wronskian (r : ℕ) (hr : 0<r) (x : D) :
    CriticalZero (qeval (eulerNormalizedResidual r hr)) (x:ℚ_[2]) ↔
      eulerResidual r (x:ℚ_[2])=0 ∧ residualStepWronskian r (x:ℚ_[2])=0 := by
  rw [eulerNormalizedResidual_critical_iff,eulerResidual_critical_iff_wronskian]

end Komorebi.Euler
