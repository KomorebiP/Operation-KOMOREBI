import Mathlib.Analysis.Complex.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum

/-! Four-sample shape for a terminal inductor shunting any RC network.
Author: Komorebi P. Physical RC characterization is a separate classical leaf.
-/
namespace SmithShuntMargin
open scoped BigOperators

noncomputable def stencil (f : ℝ → ℝ) : ℝ :=
  -(1/2)*f (1/2) + (9/4)*f (3/4) - 3*f 1 + (5/4)*f (5/4)

theorem kernel {p : ℝ} (hp : 0 ≤ p) :
    stencil (fun s => 1/(s+p)) =
      (3*p/32)/((p+1/2)*(p+3/4)*(p+1)*(p+5/4)) := by
  have h₀ : p+1/2 ≠ 0 := by linarith
  have h₁ : p+3/4 ≠ 0 := by linarith
  have h₂ : p+1 ≠ 0 := by linarith
  have h₃ : p+5/4 ≠ 0 := by linarith
  unfold stencil
  field_simp
  ring

theorem kernel_nonnegative {p : ℝ} (hp : 0 ≤ p) :
    0 ≤ stencil (fun s => 1/(s+p)) := by
  rw [kernel hp]
  positivity

theorem stencil_sum {J : Type*} [Fintype J] (f : J → ℝ → ℝ) :
    stencil (fun s => ∑ j, f j s) = ∑ j, stencil (f j) := by
  simp [stencil, Finset.sum_sub_distrib, Finset.sum_add_distrib,
    Finset.sum_neg_distrib, Finset.mul_sum]

theorem shape {J : Type*} [Fintype J] (h a b : ℝ) (c p : J → ℝ)
    (hc : ∀ j, 0 ≤ c j) (hp : ∀ j, 0 ≤ p j) :
    stencil (fun s => h/s+a+b*s-∑ j, c j/(s+p j)) ≤ 0 := by
  have hid : stencil (fun s => h/s+a+b*s-∑ j, c j/(s+p j)) =
      -stencil (fun s => ∑ j, c j/(s+p j)) := by
    unfold stencil
    ring
  rw [hid, stencil_sum]
  apply neg_nonpos.mpr
  apply Finset.sum_nonneg
  intro j hj
  have hjid : stencil (fun s => c j/(s+p j)) =
      c j * stencil (fun s => 1/(s+p j)) := by unfold stencil; ring
  rw [hjid]
  exact mul_nonneg (hc j) (kernel_nonnegative (hp j))

end SmithShuntMargin
#print axioms SmithShuntMargin.kernel
#print axioms SmithShuntMargin.kernel_nonnegative
#print axioms SmithShuntMargin.stencil_sum
#print axioms SmithShuntMargin.shape
