import Mathlib.Basic.Complex.Basic
import Mathlib.Tactic

/-!
Author: Komorebi P.
Normalized homogeneous Smith action. Pair coordinates represent [u:v], so the
half-turn swaps zero and infinity. Chart formulas carry explicit denominators.
-/

namespace KomorebiPaperV.SmithAction

noncomputable def action (a : ℂ) (p : ℂ × ℂ) : ℂ × ℂ :=
  (((1 + a) * p.1 + (1 - a) * p.2) / 2,
   ((1 - a) * p.1 + (1 + a) * p.2) / 2)

theorem action_mul (a b : ℂ) (p : ℂ × ℂ) :
    action a (action b p) = action (a * b) p := by
  apply Prod.ext <;> dsimp [action] <;> ring

theorem action_one (p : ℂ × ℂ) : action 1 p = p := by
  apply Prod.ext <;> dsimp [action] <;> ring

theorem action_scale (a c : ℂ) (p : ℂ × ℂ) :
    action a (c * p.1, c * p.2) =
      (c * (action a p).1, c * (action a p).2) := by
  apply Prod.ext <;> dsimp [action] <;> ring

theorem action_nonzero (a : ℂ) (ha : a ≠ 0) (p : ℂ × ℂ) (hp : p ≠ 0) :
    action a p ≠ 0 := by
  intro h
  have hi := action_mul a⁻¹ a p
  rw [inv_mul_cancel₀ ha, action_one, h] at hi
  have hz : action a⁻¹ (0 : ℂ × ℂ) = 0 := by simp [action]
  exact hp (hi.symm.trans hz)

theorem half_turn (p : ℂ × ℂ) : action (-1) p = (p.2, p.1) := by
  apply Prod.ext <;> dsimp [action] <;> ring

theorem half_turn_zero : action (-1) ((0 : ℂ), 1) = (1, 0) := by
  exact half_turn _

theorem half_turn_infinity : action (-1) ((1 : ℂ), 0) = (0, 1) := by
  exact half_turn _

def denominator (a z : ℂ) : ℂ := (1 - a) * z + (1 + a)

noncomputable def mobius (a z : ℂ) : ℂ := ((1 + a) * z + (1 - a)) / denominator a z

theorem homogeneous_chart (a z : ℂ) :
    (action a (z, 1)).1 / (action a (z, 1)).2 = mobius a z := by
  dsimp [action, mobius, denominator]
  simp only [mul_one]
  exact div_div_div_cancel_right₀ (by norm_num : (2 : ℂ) ≠ 0) _ _

theorem chart_composition (a b z : ℂ)
    (hb : denominator b z ≠ 0)
    (hab : denominator (a * b) z ≠ 0)
    (ha : denominator a (mobius b z) ≠ 0) :
    mobius a (mobius b z) = mobius (a * b) z := by
  have hrel : mobius b z * denominator b z = (1 + b) * z + (1 - b) :=
    div_mul_cancel₀ _ hb
  apply (div_eq_div_iff ha hab).mpr
  dsimp only [denominator] at hrel ⊢
  linear_combination 2 * a * hrel

theorem finite_half_turn (z : ℂ) (hz : z ≠ 0) :
    denominator (-1) z ≠ 0 ∧ mobius (-1) z = z⁻¹ := by
  constructor
  · simpa [denominator] using hz
  · dsimp [mobius, denominator]
    field_simp [hz]
    ring

end KomorebiPaperV.SmithAction
