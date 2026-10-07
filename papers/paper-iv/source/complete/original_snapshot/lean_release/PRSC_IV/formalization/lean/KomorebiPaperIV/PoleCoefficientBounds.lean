/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import Mathlib.Analysis.Complex.Liouville
import Mathlib.Analysis.Asymptotics.Defs

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric Asymptotics
open scoped Topology

def analyticTaylorCoefficient (f : ℂ → ℂ) (n : ℕ) : ℂ :=
  iteratedDeriv n f 0 / (n.factorial : ℂ)

/-- The exact Cauchy bound after conversion to ordinary Taylor coefficients. -/
theorem analyticTaylorCoefficient_norm_le {f : ℂ → ℂ} {R C : ℝ}
    (hR : 0 < R) (hf : DiffContOnCl ℂ f (ball 0 R))
    (hC : ∀ z ∈ sphere 0 R, ‖f z‖ ≤ C) (n : ℕ) :
    ‖analyticTaylorCoefficient f n‖ ≤ C / R ^ n := by
  have h := Complex.norm_iteratedDeriv_le_of_forall_mem_sphere_norm_le n hR hf hC
  rw [analyticTaylorCoefficient, norm_div, Complex.norm_natCast]
  apply (div_le_iff₀ (by positivity : (0 : ℝ) < n.factorial)).mpr
  simpa only [div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm] using h

/-- Cauchy's estimate supplies the exponential remainder in the nearest-pole
expansion once the principal parts have been removed holomorphically. -/
theorem analyticTaylorCoefficient_isBigO {f : ℂ → ℂ} {R : ℝ}
    (hR : 0 < R) (hf : DiffContOnCl ℂ f (ball 0 R)) :
    (fun n : ℕ => analyticTaylorCoefficient f n) =O[atTop] (fun n => R⁻¹ ^ n) := by
  have hc : ContinuousOn f (sphere 0 R) :=
    hf.continuousOn.mono (by simpa only [closure_ball (0 : ℂ) hR.ne'] using! (sphere_subset_closedBall : sphere (0 : ℂ) R ⊆ closedBall 0 R))
  obtain ⟨C, hC⟩ := (isCompact_sphere (0 : ℂ) R).bddAbove_image hc.norm
  apply IsBigO.of_bound C
  apply Eventually.of_forall
  intro n
  have hb : ∀ z ∈ sphere (0 : ℂ) R, ‖f z‖ ≤ C := by
    intro z hz
    exact hC (mem_image_of_mem (fun z => ‖f z‖) hz)
  simpa only [norm_pow, Real.norm_eq_abs, abs_inv, abs_of_pos hR, ← inv_pow, div_eq_mul_inv] using
    analyticTaylorCoefficient_norm_le hR hf hb n

/-- Factorial rescaling and the block subsequence preserve the required error
bound, including the exact `(N*n)!` normalization of the manuscript. -/
theorem analyticTaylorCoefficient_block_error {f : ℂ → ℂ} {R C : ℝ}
    (hR : 0 < R) (hf : DiffContOnCl ℂ f (ball 0 R))
    (hC : ∀ z ∈ sphere 0 R, ‖f z‖ ≤ C) (N n : ℕ) :
    ‖((N * n).factorial : ℂ) * analyticTaylorCoefficient f (N * n)‖ ≤
      C * ((N * n).factorial : ℝ) * R⁻¹ ^ (N * n) := by
  rw [norm_mul, Complex.norm_natCast]
  have h := mul_le_mul_of_nonneg_left (analyticTaylorCoefficient_norm_le hR hf hC (N * n))
    (show (0 : ℝ) ≤ (N * n).factorial by positivity)
  simpa only [div_eq_mul_inv, inv_pow, mul_assoc, mul_comm, mul_left_comm] using h

end
end Komorebi.PaperIV
