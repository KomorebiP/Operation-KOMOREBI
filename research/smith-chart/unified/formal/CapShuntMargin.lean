import Mathlib.Analysis.Complex.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-! Sixth-difference shape for a terminal capacitor shunting any RL network.
Author: Komorebi P. Classical physical characterization is a separate leaf.
-/
namespace SmithCapShuntMargin
open scoped BigOperators
noncomputable def stencil (f : ℝ → ℝ) : ℝ :=
  f (1/2)-6*f (3/4)+15*f 1-20*f (5/4)+15*f (3/2)-6*f (7/4)+f 2

theorem kernel {p : ℝ} (hp : 0 ≤ p) :
    stencil (fun s => 1/(s+p)) =
      (45/256)/((p+1/2)*(p+3/4)*(p+1)*(p+5/4)*(p+3/2)*(p+7/4)*(p+2)) := by
  have h₀ : p+1/2 ≠ 0 := by linarith
  have h₁ : p+3/4 ≠ 0 := by linarith
  have h₂ : p+1 ≠ 0 := by linarith
  have h₃ : p+5/4 ≠ 0 := by linarith
  have h₄ : p+3/2 ≠ 0 := by linarith
  have h₅ : p+7/4 ≠ 0 := by linarith
  have h₆ : p+2 ≠ 0 := by linarith
  unfold stencil
  field_simp
  ring

theorem kernel_nonnegative {p : ℝ} (hp : 0 ≤ p) :
    0 ≤ stencil (fun s => 1/(s+p)) := by
  rw [kernel hp]
  positivity

theorem stencil_sum {J : Type*} [Fintype J] (f : J → ℝ → ℝ) :
    stencil (fun s => ∑ j, f j s) = ∑ j, stencil (f j) := by
  simp [stencil, Finset.sum_sub_distrib, Finset.sum_add_distrib, Finset.mul_sum]

theorem shape {J : Type*} [Fintype J] (a b : ℝ) (c p : J → ℝ)
    (hc : ∀ j, 0 ≤ c j) (hp : ∀ j, 0 ≤ p j) :
    0 ≤ stencil (fun s => a+b*s+∑ j, c j/(s+p j)) := by
  have hid : stencil (fun s => a+b*s+∑ j, c j/(s+p j)) =
      stencil (fun s => ∑ j, c j/(s+p j)) := by unfold stencil; ring
  rw [hid, stencil_sum]
  apply Finset.sum_nonneg
  intro j hj
  have hjid : stencil (fun s => c j/(s+p j)) =
      c j * stencil (fun s => 1/(s+p j)) := by unfold stencil; ring
  rw [hjid]
  exact mul_nonneg (hc j) (kernel_nonnegative (hp j))
end SmithCapShuntMargin
#print axioms SmithCapShuntMargin.kernel
#print axioms SmithCapShuntMargin.kernel_nonnegative
#print axioms SmithCapShuntMargin.stencil_sum
#print axioms SmithCapShuntMargin.shape
