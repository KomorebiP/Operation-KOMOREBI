import Mathlib.Analysis.Complex.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-! Exact sample-separation consequences of the RC/RL shape inequalities.
Author: Komorebi P. The network-to-shape implication is a separate source/proof leaf.
-/
namespace SmithPureTypeMargins
open scoped BigOperators

noncomputable def stencil (f : ℝ → ℝ) : ℝ :=
  f (1/2) - 4*f (3/4) + 6*f 1 - 4*f (5/4) + f (3/2)

/-- Exact fourth-difference identity for a Stieltjes kernel. -/
theorem kernel_stencil {p : ℝ} (hp : 0 ≤ p) :
    stencil (fun s => 1/(s+p)) =
      (3/32) / ((p+1/2)*(p+3/4)*(p+1)*(p+5/4)*(p+3/2)) := by
  have h₀ : p+1/2 ≠ 0 := by linarith
  have h₁ : p+3/4 ≠ 0 := by linarith
  have h₂ : p+1 ≠ 0 := by linarith
  have h₃ : p+5/4 ≠ 0 := by linarith
  have h₄ : p+3/2 ≠ 0 := by linarith
  unfold stencil
  field_simp
  ring

theorem kernel_stencil_nonnegative {p : ℝ} (hp : 0 ≤ p) :
    0 ≤ stencil (fun s => 1/(s+p)) := by
  rw [kernel_stencil hp]
  positivity

theorem stencil_sum {J : Type*} [Fintype J] (f : J → ℝ → ℝ) :
    stencil (fun s => ∑ j, f j s) = ∑ j, stencil (f j) := by
  simp [stencil, Finset.sum_sub_distrib, Finset.sum_add_distrib, Finset.mul_sum]

/-- Every finite positive Stieltjes representation gives the required RL shape. -/
theorem rl_shape {J : Type*} [Fintype J] (a p : J → ℝ) (c : ℝ)
    (ha : ∀ j, 0 ≤ a j) (hp : ∀ j, 0 ≤ p j) :
    stencil (fun s => c - ∑ j, a j/(s+p j)) ≤ 0 := by
  have hid : stencil (fun s => c - ∑ j, a j/(s+p j)) =
      -stencil (fun s => ∑ j, a j/(s+p j)) := by unfold stencil; ring
  rw [hid, stencil_sum]
  apply neg_nonpos.mpr
  apply Finset.sum_nonneg
  intro j hj
  have hjid : stencil (fun s => a j/(s+p j)) =
      a j * stencil (fun s => 1/(s+p j)) := by unfold stencil; ring
  rw [hjid]
  exact mul_nonneg (ha j) (kernel_stencil_nonnegative (hp j))

/-- Any decreasing response has this error against the two endpoint samples. -/
theorem rc_margin {g₀ g₁ δ : ℝ} (hshape : g₁ ≤ g₀)
    (h₀ : |g₀ - (-9 / 37)| ≤ δ) (h₁ : |g₁ - (-3 / 71)| ≤ δ) :
    (264 / 2627 : ℝ) ≤ δ := by
  obtain ⟨ha,hb⟩ := abs_le.mp h₀
  obtain ⟨hc,hd⟩ := abs_le.mp h₁
  linarith

/-- Nonpositive fourth divided difference gives a usable positive RL margin. -/
theorem rl_margin {g₀ g₁ g₂ g₃ g₄ δ : ℝ}
    (hshape : g₀ - 4*g₁ + 6*g₂ - 4*g₃ + g₄ ≤ 0)
    (h₀ : |g₀ - (-9/37)| ≤ δ) (h₁ : |g₁ - (-17/94)| ≤ δ)
    (h₂ : |g₂ - (-2/15)| ≤ δ) (h₃ : |g₃ - (-15/152)| ≤ δ)
    (h₄ : |g₄ - (-7/95)| ≤ δ) : (401/5286560 : ℝ) ≤ δ := by
  obtain ⟨ha,hb⟩ := abs_le.mp h₀
  obtain ⟨hc,hd⟩ := abs_le.mp h₁
  obtain ⟨he,hf⟩ := abs_le.mp h₂
  obtain ⟨hg,hh⟩ := abs_le.mp h₃
  obtain ⟨hi,hj⟩ := abs_le.mp h₄
  linarith

/-- The numerical witness is positive, independently of circuit enumeration. -/
theorem rl_margin_positive : (0 : ℝ) < 401/5286560 := by norm_num

end SmithPureTypeMargins
