import KomorebiVerification.PaperII.ReleaseRectifiableCycle
import Mathlib.Analysis.Complex.RealDeriv

/-!
Candidate module, not yet compiled.  A geometric upper bound suffices for the
paper's contour norm estimate, without assuming the exact length/speed theorem.
-/

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseRectifiableLength

open MeasureTheory Set
open scoped Topology BigOperators
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseRectifiable
open Komorebi.PaperII.ReleaseRectifiableCycle
open Komorebi.PaperII.ReleaseArcLength

/-- At a point where both real coordinates are differentiable, the coordinate
velocity is the genuine derivative of the complex-valued real-variable path. -/
theorem hasDerivAt_coordinateVelocity {f : ℝ → ℂ} {x : ℝ}
    (hr : DifferentiableAt ℝ (fun t ↦ (f t).re) x)
    (hi : DifferentiableAt ℝ (fun t ↦ (f t).im) x) :
    HasDerivAt f (coordinateVelocity f x) x := by
  have h := hr.hasDerivAt.ofReal_comp.add
    (hi.hasDerivAt.ofReal_comp.mul_const Complex.I)
  have heq : ((fun y : ℝ ↦ Complex.ofReal (f y).re) +
      fun y : ℝ ↦ Complex.ofReal (f y).im * Complex.I) = f := by
    funext y
    exact Complex.re_add_im (f y)
  rw [heq] at h
  exact h

/-- The coordinate velocity is bounded by a Lipschitz constant at each interior
point.  At a non-differentiability point a missing coordinate derivative is zero
by the definition of `deriv`; the one-coordinate bound handles these cases. -/
theorem norm_coordinateVelocity_le {f : ℝ → ℂ} {a b x : ℝ} {K : NNReal}
    (hf : LipschitzOnWith K f (Icc a b)) (hx : x ∈ Ioo a b) :
    ‖coordinateVelocity f x‖ ≤ (K : ℝ) := by
  have hs : Icc a b ∈ nhds x := Icc_mem_nhds hx.1 hx.2
  have hrLip : LipschitzOnWith K (fun t ↦ (f t).re) (Icc a b) := by
    apply LipschitzOnWith.of_dist_le_mul
    intro x hx y hy
    calc
      dist (f x).re (f y).re = |(f x - f y).re| := by simp [Real.dist_eq]
      _ ≤ ‖f x - f y‖ := Complex.abs_re_le_norm _
      _ ≤ (K : ℝ) * dist x y := by simpa only [dist_eq_norm] using hf.dist_le_mul x hx y hy
  have hiLip : LipschitzOnWith K (fun t ↦ (f t).im) (Icc a b) := by
    apply LipschitzOnWith.of_dist_le_mul
    intro x hx y hy
    calc
      dist (f x).im (f y).im = |(f x - f y).im| := by simp [Real.dist_eq]
      _ ≤ ‖f x - f y‖ := Complex.abs_im_le_norm _
      _ ≤ (K : ℝ) * dist x y := by simpa only [dist_eq_norm] using hf.dist_le_mul x hx y hy
  by_cases hr : DifferentiableAt ℝ (fun t ↦ (f t).re) x
  · by_cases hi : DifferentiableAt ℝ (fun t ↦ (f t).im) x
    · exact (hasDerivAt_coordinateVelocity hr hi).le_of_lipschitzOn hs hf
    · simp only [coordinateVelocity, deriv_zero_of_not_differentiableAt hi,
        Complex.ofReal_zero, zero_mul, add_zero, Complex.norm_real]
      simpa only [Real.norm_eq_abs] using norm_deriv_le_of_lipschitzOn hs hrLip
  · simp only [coordinateVelocity, deriv_zero_of_not_differentiableAt hr,
      Complex.ofReal_zero, zero_add, norm_mul, Complex.norm_real, Complex.norm_I, mul_one]
    simpa only [Real.norm_eq_abs] using norm_deriv_le_of_lipschitzOn hs hiLip

/-- The actual velocity-integral length of a Lipschitz path is at most its
Lipschitz constant times the parameter interval's length. -/
theorem integral_norm_coordinateVelocity_le {f : ℝ → ℂ} {a b : ℝ} {K : NNReal}
    (hab : a ≤ b) (hf : LipschitzOnWith K f (Icc a b)) :
    (∫ x : ℝ in a..b, ‖coordinateVelocity f x‖) ≤ (b-a) * (K : ℝ) := by
  have hac : AbsolutelyContinuousOnInterval f a b := by
    apply LipschitzOnWith.absolutelyContinuousOnInterval
    simpa only [uIcc_of_le hab] using hf
  calc
    _ ≤ ∫ x : ℝ in a..b, (K : ℝ) := by
      exact intervalIntegral.integral_mono_on_of_le_Ioo hab
        (integrable_coordinateVelocity hac).norm intervalIntegrable_const
        (fun x hx ↦ norm_coordinateVelocity_le hf hx)
    _ = _ := by simp

/-- Arclength reconstruction gives exactly the upper bound needed in the
manuscript's length-times-suprema estimate.  No equality of the two notions of
length is assumed. -/
theorem length_cycleOfRectifiable_le (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) :
    (cycleOfRectifiable n f hv hc hclosed).length ≤ ∑ i : Fin n, geometricLength (f i) := by
  apply Finset.sum_le_sum
  intro i hi
  change (∫ s : ℝ in (0:ℝ)..1, ‖coordinateVelocity (unitIntervalPath (f i)) s‖) ≤ _
  have h := integral_norm_coordinateVelocity_le (by norm_num : (0:ℝ) ≤ 1)
    (unitIntervalPath_lipschitz (hv i) (hc i))
  change (∫ s : ℝ in (0:ℝ)..1, ‖coordinateVelocity (unitIntervalPath (f i)) s‖) ≤
    ((1:ℝ) - 0) * geometricLength (f i) at h
  simpa only [sub_zero, one_mul] using h

end Komorebi.PaperII.ReleaseRectifiableLength
