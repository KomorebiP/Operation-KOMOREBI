import KomorebiVerification.PaperII.ReleaseAnalyticContour
import Mathlib.Analysis.ConstantSpeed
import Mathlib.MeasureTheory.Integral.IntervalIntegral.AbsolutelyContinuousFun

/-! # Concrete integral representations of rectifiable curves
The first bridge constructs velocities from derivatives of the real and
imaginary coordinates of an absolutely continuous complex path. No supplied
integral representation is assumed. -/

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperII.ReleaseRectifiable

open MeasureTheory Set
open scoped Topology
open Komorebi.PaperII.ReleaseAnalyticContour

/-- Canonical complex velocity obtained from the two real coordinate derivatives. -/
def coordinateVelocity (f : ℝ → ℂ) (x : ℝ) : ℂ :=
  (deriv (fun t ↦ (f t).re) x : ℂ) + (deriv (fun t ↦ (f t).im) x : ℂ) * Complex.I

theorem ac_re {f : ℝ → ℂ} {a b : ℝ}
    (hf : AbsolutelyContinuousOnInterval f a b) :
    AbsolutelyContinuousOnInterval (fun t ↦ (f t).re) a b :=
  Complex.reCLM.lipschitz.comp_absolutelyContinuousOnInterval hf

theorem ac_im {f : ℝ → ℂ} {a b : ℝ}
    (hf : AbsolutelyContinuousOnInterval f a b) :
    AbsolutelyContinuousOnInterval (fun t ↦ (f t).im) a b :=
  Complex.imCLM.lipschitz.comp_absolutelyContinuousOnInterval hf

theorem integrable_coordinateVelocity {f : ℝ → ℂ} {a b : ℝ}
    (hf : AbsolutelyContinuousOnInterval f a b) :
    IntervalIntegrable (coordinateVelocity f) volume a b := by
  have hr := (ac_re hf).intervalIntegrable_deriv
  have hi := (ac_im hf).intervalIntegrable_deriv
  have hr' : IntervalIntegrable (fun x ↦ (deriv (fun t ↦ (f t).re) x : ℂ)) volume a b :=
    ⟨Complex.ofRealCLM.integrable_comp hr.1, Complex.ofRealCLM.integrable_comp hr.2⟩
  have hi' : IntervalIntegrable (fun x ↦ (deriv (fun t ↦ (f t).im) x : ℂ)) volume a b :=
    ⟨Complex.ofRealCLM.integrable_comp hi.1, Complex.ofRealCLM.integrable_comp hi.2⟩
  exact hr'.add (hi'.mul_const Complex.I)

/-- The real-valued absolutely-continuous FTC yields the full complex FTC. -/
theorem integral_coordinateVelocity {f : ℝ → ℂ} {a b : ℝ}
    (hf : AbsolutelyContinuousOnInterval f a b) :
    (∫ x : ℝ in a..b, coordinateVelocity f x) = f b - f a := by
  have hr := (ac_re hf).intervalIntegrable_deriv
  have hi := (ac_im hf).intervalIntegrable_deriv
  have hr' : IntervalIntegrable (fun x ↦ (deriv (fun t ↦ (f t).re) x : ℂ)) volume a b :=
    ⟨Complex.ofRealCLM.integrable_comp hr.1, Complex.ofRealCLM.integrable_comp hr.2⟩
  have hi' : IntervalIntegrable (fun x ↦ (deriv (fun t ↦ (f t).im) x : ℂ)) volume a b :=
    ⟨Complex.ofRealCLM.integrable_comp hi.1, Complex.ofRealCLM.integrable_comp hi.2⟩
  unfold coordinateVelocity
  rw [intervalIntegral.integral_add hr' (hi'.mul_const Complex.I),
    intervalIntegral.integral_mul_const, intervalIntegral.integral_ofReal,
    intervalIntegral.integral_ofReal, (ac_re hf).integral_deriv_eq_sub,
    (ac_im hf).integral_deriv_eq_sub]
  apply Complex.ext <;> simp

/-- Construct the actual IntegralCycle from an arbitrary finite family of
closed absolutely continuous paths. -/
def cycleOfAbsolutelyContinuous (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hf : ∀ i, AbsolutelyContinuousOnInterval (f i) 0 1)
    (hclosed : ∀ i, f i 1 = f i 0) : IntegralCycle where
  count := n
  base := fun i ↦ f i 0
  velocity := fun i ↦ coordinateVelocity (f i)
  velocity_integrable i := integrable_coordinateVelocity (hf i)
  closed i := by rw [integral_coordinateVelocity (hf i), hclosed, sub_self]

/-- The constructed curve agrees pointwise with the original path throughout
the whole closed parameter interval. -/
theorem curve_cycleOfAbsolutelyContinuous (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hf : ∀ i, AbsolutelyContinuousOnInterval (f i) 0 1)
    (hclosed : ∀ i, f i 1 = f i 0) (i : Fin n) (s : ℝ) (hs : s ∈ uIcc (0:ℝ) 1) :
    (cycleOfAbsolutelyContinuous n f hf hclosed).curve i s = f i s := by
  change f i 0 + (∫ r : ℝ in 0..s, coordinateVelocity (f i) r) = f i s
  rw [integral_coordinateVelocity ((hf i).mono (uIcc_subset_uIcc_left hs))]
  abel

/-- In particular every finite family of closed Lipschitz paths has a
constructed integrable-velocity representation, not an assumed certificate. -/
def cycleOfLipschitz (n : ℕ) (f : Fin n → ℝ → ℂ) (K : Fin n → ℝ≥0)
    (hf : ∀ i, LipschitzOnWith (K i) (f i) (uIcc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) : IntegralCycle :=
  cycleOfAbsolutelyContinuous n f (fun i ↦ (hf i).absolutelyContinuousOnInterval) hclosed

theorem curve_cycleOfLipschitz (n : ℕ) (f : Fin n → ℝ → ℂ) (K : Fin n → ℝ≥0)
    (hf : ∀ i, LipschitzOnWith (K i) (f i) (uIcc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) (i : Fin n) (s : ℝ) (hs : s ∈ uIcc (0:ℝ) 1) :
    (cycleOfLipschitz n f K hf hclosed).curve i s = f i s :=
  curve_cycleOfAbsolutelyContinuous n f _ hclosed i s hs

end Komorebi.PaperII.ReleaseRectifiable
