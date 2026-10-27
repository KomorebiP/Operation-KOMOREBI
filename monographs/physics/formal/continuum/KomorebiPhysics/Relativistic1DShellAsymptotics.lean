module

public import KomorebiPhysics.Dispersion1D
public import Mathlib.Analysis.Calculus.Taylor
public import Mathlib.Analysis.Calculus.IteratedDeriv.Lemmas
public import Mathlib.Analysis.SpecialFunctions.Trigonometric.Deriv
public import Mathlib.Analysis.Asymptotics.AsymptoticEquivalent

/-!
Small-spacing structure of the exact one-dimensional product-cosine shell.
This module first proves coefficient identities and a genuine Taylor remainder
for the exact shell, independently of the inverse-cosine frequency branch.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic1DShellAsymptotics

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.Dispersion1D

/-- Continuum energy scale. -/
def energy (m k : ℝ) : ℝ := Real.sqrt (m^2 + k^2)

/-- Quartic coefficient in the exact product-cosine shell. -/
def shellQuarticCoeff (m k : ℝ) : ℝ :=
  (m^4 + k^4) / 24 + (m^2 * k^2) / 4

/-- The source's equivalent quartic coefficient `E^4/24 + m^2 k^2/6`. -/
def shellQuarticCoeffSource (m k : ℝ) : ℝ :=
  energy m k ^ 4 / 24 + (m^2 * k^2) / 6

/-- The fourth-order shell approximant. -/
def shellPoly4 (m k ε : ℝ) : ℝ :=
  1 - (m^2 + k^2) * ε^2 / 2 + shellQuarticCoeff m k * ε^4

/-- Smoothness of the exact shell to arbitrary finite order. -/
theorem contDiff_scaled_cos (a : ℝ) (n : ℕ) : ContDiff ℝ n (fun ε : ℝ => Real.cos (a * ε)) := by
  exact Real.contDiff_cos.comp (contDiff_const.mul contDiff_id)

/-- Smoothness of the exact shell to arbitrary finite order. -/
theorem contDiff_shell (m k : ℝ) (n : ℕ) : ContDiff ℝ n (fun ε => shell m k ε) := by
  exact (contDiff_scaled_cos m n).mul (contDiff_scaled_cos k n)

/-- Iterated derivatives of a scaled cosine. -/
theorem iteratedDeriv_scaled_cos (a : ℝ) (n : ℕ) :
    iteratedDeriv n (fun ε : ℝ => Real.cos (a * ε)) =
      fun ε => a^n * iteratedDeriv n Real.cos (a * ε) := by
  simpa using iteratedDeriv_comp_const_mul (Real.contDiff_cos : ContDiff ℝ n Real.cos) a

/-- Even scaled-cosine derivative at zero. -/
theorem iteratedDeriv_scaled_cos_even_zero (a : ℝ) (r : ℕ) :
    iteratedDeriv (2*r) (fun ε : ℝ => Real.cos (a * ε)) 0 = (-1 : ℝ)^r * a^(2*r) := by
  rw [iteratedDeriv_scaled_cos]
  rw [Real.iteratedDeriv_even_cos]
  simp
  ring

/-- Odd scaled-cosine derivative at zero vanishes. -/
theorem iteratedDeriv_scaled_cos_odd_zero (a : ℝ) (r : ℕ) :
    iteratedDeriv (2*r+1) (fun ε : ℝ => Real.cos (a * ε)) 0 = 0 := by
  rw [iteratedDeriv_scaled_cos]
  rw [Real.iteratedDeriv_odd_cos]
  simp


@[simp] theorem scaled_cos_d0_zero (a : ℝ) :
    iteratedDeriv 0 (fun ε : ℝ => Real.cos (a * ε)) 0 = 1 := by
  rw [iteratedDeriv_zero]
  simp

@[simp] theorem scaled_cos_d1_zero (a : ℝ) :
    iteratedDeriv 1 (fun ε : ℝ => Real.cos (a * ε)) 0 = 0 := by
  have h := iteratedDeriv_scaled_cos_odd_zero a 0
  norm_num at h
  rw [iteratedDeriv_one]
  exact h

@[simp] theorem scaled_cos_d2_zero (a : ℝ) :
    iteratedDeriv 2 (fun ε : ℝ => Real.cos (a * ε)) 0 = -a^2 := by
  have h := iteratedDeriv_scaled_cos_even_zero a 1
  norm_num at h
  exact h

@[simp] theorem scaled_cos_d3_zero (a : ℝ) :
    iteratedDeriv 3 (fun ε : ℝ => Real.cos (a * ε)) 0 = 0 := by
  have h := iteratedDeriv_scaled_cos_odd_zero a 1
  norm_num at h
  exact h

@[simp] theorem scaled_cos_d4_zero (a : ℝ) :
    iteratedDeriv 4 (fun ε : ℝ => Real.cos (a * ε)) 0 = a^4 := by
  have h := iteratedDeriv_scaled_cos_even_zero a 2
  norm_num at h
  exact h

@[simp] theorem scaled_cos_d5_zero (a : ℝ) :
    iteratedDeriv 5 (fun ε : ℝ => Real.cos (a * ε)) 0 = 0 := by
  have h := iteratedDeriv_scaled_cos_odd_zero a 2
  norm_num at h
  exact h

@[simp] theorem scaled_cos_d6_zero (a : ℝ) :
    iteratedDeriv 6 (fun ε : ℝ => Real.cos (a * ε)) 0 = -a^6 := by
  have h := iteratedDeriv_scaled_cos_even_zero a 3
  norm_num at h
  exact h

/-- Exact shell value at zero. -/
theorem shell_zero (m k : ℝ) : shell m k 0 = 1 := by
  simp [shell]

/-- First shell derivative at zero vanishes. -/
theorem shell_deriv1_zero (m k : ℝ) :
    iteratedDeriv 1 (fun ε => shell m k ε) 0 = 0 := by
  rw [show (fun ε => shell m k ε) =
      (fun ε : ℝ => Real.cos (m*ε)) * (fun ε : ℝ => Real.cos (k*ε)) by rfl]
  rw [iteratedDeriv_mul (f := fun ε : ℝ => Real.cos (m*ε))
      (g := fun ε : ℝ => Real.cos (k*ε))
      (contDiff_scaled_cos m 1).contDiffAt (contDiff_scaled_cos k 1).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose]

/-- Second shell derivative at zero. -/
theorem shell_deriv2_zero (m k : ℝ) :
    iteratedDeriv 2 (fun ε => shell m k ε) 0 = -(m^2 + k^2) := by
  rw [show (fun ε => shell m k ε) =
      (fun ε : ℝ => Real.cos (m*ε)) * (fun ε : ℝ => Real.cos (k*ε)) by rfl]
  rw [iteratedDeriv_mul (f := fun ε : ℝ => Real.cos (m*ε))
      (g := fun ε : ℝ => Real.cos (k*ε))
      (contDiff_scaled_cos m 2).contDiffAt (contDiff_scaled_cos k 2).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose]

/-- Third shell derivative at zero vanishes. -/
theorem shell_deriv3_zero (m k : ℝ) :
    iteratedDeriv 3 (fun ε => shell m k ε) 0 = 0 := by
  rw [show (fun ε => shell m k ε) =
      (fun ε : ℝ => Real.cos (m*ε)) * (fun ε : ℝ => Real.cos (k*ε)) by rfl]
  rw [iteratedDeriv_mul (f := fun ε : ℝ => Real.cos (m*ε))
      (g := fun ε : ℝ => Real.cos (k*ε))
      (contDiff_scaled_cos m 3).contDiffAt (contDiff_scaled_cos k 3).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose]

/-- Fourth shell derivative at zero. -/
theorem shell_deriv4_zero (m k : ℝ) :
    iteratedDeriv 4 (fun ε => shell m k ε) 0 = m^4 + 6*m^2*k^2 + k^4 := by
  rw [show (fun ε => shell m k ε) =
      (fun ε : ℝ => Real.cos (m*ε)) * (fun ε : ℝ => Real.cos (k*ε)) by rfl]
  rw [iteratedDeriv_mul (f := fun ε : ℝ => Real.cos (m*ε))
      (g := fun ε : ℝ => Real.cos (k*ε))
      (contDiff_scaled_cos m 4).contDiffAt (contDiff_scaled_cos k 4).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose]
  ring

/-- Fifth shell derivative at zero vanishes. -/
theorem shell_deriv5_zero (m k : ℝ) :
    iteratedDeriv 5 (fun ε => shell m k ε) 0 = 0 := by
  rw [show (fun ε => shell m k ε) =
      (fun ε : ℝ => Real.cos (m*ε)) * (fun ε : ℝ => Real.cos (k*ε)) by rfl]
  rw [iteratedDeriv_mul (f := fun ε : ℝ => Real.cos (m*ε))
      (g := fun ε : ℝ => Real.cos (k*ε))
      (contDiff_scaled_cos m 5).contDiffAt (contDiff_scaled_cos k 5).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose]

/-- Sixth shell derivative at zero, retained only to control the remainder order. -/
theorem shell_deriv6_zero (m k : ℝ) :
    iteratedDeriv 6 (fun ε => shell m k ε) 0 =
      -(m^6 + 15*m^4*k^2 + 15*m^2*k^4 + k^6) := by
  rw [show (fun ε => shell m k ε) =
      (fun ε : ℝ => Real.cos (m*ε)) * (fun ε : ℝ => Real.cos (k*ε)) by rfl]
  rw [iteratedDeriv_mul (f := fun ε : ℝ => Real.cos (m*ε))
      (g := fun ε : ℝ => Real.cos (k*ε))
      (contDiff_scaled_cos m 6).contDiffAt (contDiff_scaled_cos k 6).contDiffAt]
  norm_num [Finset.sum_range_succ, Nat.choose]
  ring

/-- Algebraic equality between the expanded and source quartic coefficients. -/
theorem shellQuarticCoeff_eq_source (m k : ℝ) :
    shellQuarticCoeff m k = shellQuarticCoeffSource m k := by
  have hnonneg : 0 ≤ m^2 + k^2 := by positivity
  have hs : energy m k ^ 2 = m^2 + k^2 := by
    rw [energy, Real.sq_sqrt hnonneg]
  rw [shellQuarticCoeff, shellQuarticCoeffSource]
  rw [show energy m k ^ 4 = (energy m k ^ 2)^2 by ring, hs]
  ring

/-- Taylor polynomial of order six, evaluated at zero, in closed form. -/
theorem taylor6_shell_closed (m k ε : ℝ) :
    taylorWithinEval (fun x => shell m k x) 6 Set.univ 0 ε =
      shellPoly4 m k ε -
        (m^6 + 15*m^4*k^2 + 15*m^2*k^4 + k^6) * ε^6 / 720 := by
  simp only [taylorWithinEval_succ, taylor_within_zero_eval, iteratedDerivWithin_univ]
  norm_num [shell_zero, shell_deriv1_zero, shell_deriv2_zero,
    shell_deriv3_zero, shell_deriv4_zero, shell_deriv5_zero, shell_deriv6_zero,
    shellPoly4, shellQuarticCoeff]
  ring

/-- Genuine sixth-order Taylor control for the exact shell. -/
theorem shell_sub_taylor6_isLittleO (m k : ℝ) :
    (fun ε => shell m k ε -
      taylorWithinEval (fun x => shell m k x) 6 Set.univ 0 ε) =o[𝓝 0]
      (fun ε : ℝ => ε^6) := by
  simpa using (taylor_isLittleO_univ (x₀ := (0 : ℝ)) (contDiff_shell m k 6))

/-- Equation (8.15): the product-cosine shell has the stated quartic term and an `O(ε^6)` remainder. -/
theorem shell_expansion_isBigO (m k : ℝ) :
    (fun ε => shell m k ε - shellPoly4 m k ε) =O[𝓝 0]
      (fun ε : ℝ => ε^6) := by
  have hsmall := (shell_sub_taylor6_isLittleO m k).isBigO
  have hpoly :
      (fun ε : ℝ => taylorWithinEval (fun x => shell m k x) 6 Set.univ 0 ε - shellPoly4 m k ε) =O[𝓝 0]
        (fun ε : ℝ => ε^6) := by
    have hc : (fun ε : ℝ =>
        -(m^6 + 15*m^4*k^2 + 15*m^2*k^4 + k^6) / 720 * ε^6) =O[𝓝 0]
        (fun ε : ℝ => ε^6) :=
      (isBigO_refl (fun ε : ℝ => ε^6) (𝓝 0)).const_mul_left _
    convert hc using 1
    funext ε
    rw [taylor6_shell_closed]
    ring
  exact (hsmall.add hpoly).congr_left (by
    intro ε
    ring)

/-- Same shell expansion in the source's `E^4/24 + m^2k^2/6` notation. -/
theorem shell_expansion_source_form_isBigO (m k : ℝ) :
    (fun ε => shell m k ε -
      (1 - energy m k ^ 2 * ε^2 / 2 + shellQuarticCoeffSource m k * ε^4)) =O[𝓝 0]
      (fun ε : ℝ => ε^6) := by
  have hE : energy m k ^ 2 = m^2 + k^2 := by
    rw [energy, Real.sq_sqrt (by positivity : 0 ≤ m^2+k^2)]
  simpa [shellPoly4, shellQuarticCoeff_eq_source, hE] using shell_expansion_isBigO m k

end KomorebiPhysics.Relativistic1DShellAsymptotics
