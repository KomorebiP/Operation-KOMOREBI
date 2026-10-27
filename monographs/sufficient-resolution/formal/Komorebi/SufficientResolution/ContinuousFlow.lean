import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Analysis.Calculus.Deriv.Mul
import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus

/-!
# Real bounded-operator flows and variation of constants

The flow is the actual Banach-algebra exponential. Completeness is explicit.
The forced integral formula below is derived by differentiating a backward
propagator and applying the fundamental theorem of calculus, not assumed.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousFlow

variable {X : Type*} [NormedAddCommGroup X] [NormedSpace ℝ X] [CompleteSpace X]

/-- Actual exponential evolution of a bounded real linear generator. -/
def flow (L : X →L[ℝ] X) (t : ℝ) : X →L[ℝ] X := NormedSpace.exp (t • L)

omit [CompleteSpace X] in
@[simp] theorem flow_zero (L : X →L[ℝ] X) : flow L 0 = 1 := by
  simp [flow]

 theorem flow_add (L : X →L[ℝ] X) (s t : ℝ) :
    flow L (s+t) = flow L s * flow L t := by
  unfold flow
  rw [add_smul]
  let : NormedAlgebra ℚ (X →L[ℝ] X) := .restrictScalars ℚ ℝ _
  apply NormedSpace.exp_add_of_commute
  show (s • L) * (t • L) = (t • L) * (s • L)
  simp only [smul_mul_smul_comm]
  rw [mul_comm s t]

 theorem hasDerivAt_flow (L : X →L[ℝ] X) (t : ℝ) :
    HasDerivAt (flow L) (L * flow L t) t :=
  hasDerivAt_exp_smul_const' L t

 theorem hasDerivAt_flow_right (L : X →L[ℝ] X) (t : ℝ) :
    HasDerivAt (flow L) (flow L t * L) t :=
  hasDerivAt_exp_smul_const L t

 theorem generator_commutes_flow (L : X →L[ℝ] X) (t : ℝ) :
    L * flow L t = flow L t * L :=
  (hasDerivAt_flow L t).unique (hasDerivAt_flow_right L t)

 theorem continuous_flow (L : X →L[ℝ] X) : Continuous (flow L) :=
  continuous_iff_continuousAt.mpr (fun t => (hasDerivAt_flow L t).continuousAt)

 theorem hasDerivAt_flow_apply (L : X →L[ℝ] X) (x : X) (t : ℝ) :
    HasDerivAt (fun s => flow L s x) (L (flow L t x)) t := by
  simpa using (hasDerivAt_flow L t).clm_apply (hasDerivAt_const t x)

 theorem continuous_flow_apply (L : X →L[ℝ] X) (x : X) :
    Continuous (fun t => flow L t x) :=
  continuous_iff_continuousAt.mpr (fun t => (hasDerivAt_flow_apply L x t).continuousAt)

 theorem flow_add_apply (L : X →L[ℝ] X) (s t : ℝ) (x : X) :
    flow L (s+t) x = flow L s (flow L t x) := by
  rw [flow_add]; rfl

 theorem flow_neg_inverse (L : X →L[ℝ] X) (t : ℝ) :
    flow L (-t) * flow L t = 1 := by
  rw [← flow_add, neg_add_cancel, flow_zero]

 theorem flow_inverse_neg (L : X →L[ℝ] X) (t : ℝ) :
    flow L t * flow L (-t) = 1 := by
  rw [← flow_add, add_neg_cancel, flow_zero]

/-- Algebraic jets of the exponential, with actual derivatives. -/
def jet (L : X →L[ℝ] X) (n : ℕ) (t : ℝ) : X →L[ℝ] X := flow L t * L^n

omit [CompleteSpace X] in
@[simp] theorem jet_zero_order (L : X →L[ℝ] X) (t : ℝ) : jet L 0 t = flow L t := by
  simp [jet]

omit [CompleteSpace X] in
@[simp] theorem jet_at_zero (L : X →L[ℝ] X) (n : ℕ) : jet L n 0 = L^n := by
  simp [jet]

 theorem hasDerivAt_jet (L : X →L[ℝ] X) (n : ℕ) (t : ℝ) :
    HasDerivAt (jet L n) (jet L (n+1) t) t := by
  simpa [jet, pow_succ', mul_assoc] using! (hasDerivAt_flow_right L t).mul_const (L^n)

end Komorebi.SufficientResolution.ContinuousFlow
