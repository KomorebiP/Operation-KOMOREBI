module

public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
public import Mathlib.Tactic.Linarith
public import Mathlib.Tactic.Positivity
public import Mathlib.Tactic.FieldSimp
public import Mathlib.Tactic.Ring

public section
set_option autoImplicit false

/-! Author: Komorebi P. The printed second-order estimate, with its exact constant. -/
namespace KomorebiPaperVII.LowModeConvergence

theorem sine_square_error (x : ℝ) :
    0 ≤ x^2-Real.sin x^2 ∧ x^2-Real.sin x^2 ≤ x^4/3 := by
  have hlo : 0 ≤ x^2-Real.sin x^2 := sub_nonneg.mpr Real.sin_sq_le_sq
  have hp : |x+Real.sin x| ≤ 2*|x| :=
    (abs_add_le _ _).trans (by linarith [Real.abs_sin_le_abs (x := x)])
  have h := mul_le_mul (Real.abs_sub_sin_le x) hp (abs_nonneg _) (by positivity)
  rw [← abs_mul] at h
  have he : (x-Real.sin x)*(x+Real.sin x)=x^2-Real.sin x^2 := by ring
  rw [he,abs_of_nonneg hlo] at h
  constructor
  · exact hlo
  · calc
      _ ≤ |x|^3/6*(2*|x|) := h
      _ = x^4/3 := by rw [show |x|^3/6*(2*|x|)=|x|^4/3 by ring, (show Even (4:ℕ) by decide).pow_abs]

noncomputable def eigenvalue (w h : ℝ) : ℝ := 4/h^2*Real.sin (w*h/2)^2

theorem low_mode_error (w h : ℝ) (hh : h≠0) :
    0 ≤ w^2-eigenvalue w h ∧ w^2-eigenvalue w h ≤ w^4/12*h^2 := by
  have hs := sine_square_error (w*h/2)
  have hpos : 0 ≤ 4/h^2 := by positivity
  have he : w^2-eigenvalue w h=4/h^2*((w*h/2)^2-Real.sin (w*h/2)^2) := by
    unfold eigenvalue
    field_simp
    ring
  rw [he]
  constructor
  · exact mul_nonneg hpos hs.1
  · calc
      _ ≤ 4/h^2*((w*h/2)^4/3) := mul_le_mul_of_nonneg_left hs.2 hpos
      _ = w^4/12*h^2 := by field_simp; ring

end KomorebiPaperVII.LowModeConvergence

/-! Exported theorem axiom audit. -/
#print axioms KomorebiPaperVII.LowModeConvergence.sine_square_error
#print axioms KomorebiPaperVII.LowModeConvergence.low_mode_error
