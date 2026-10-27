import KomorebiLSM.OrientedEllipsoid

/-! The actual negative identity passes the quadratic test but reverses mass. -/
open Komorebi.LSM.OrientedEllipsoid
open scoped Matrix
abbrev I := Unit ⊕ Fin 1

example : (-(1 : Matrix I I ℝ)).transpose * Q (0 : Fin 1 → ℝ) 1 * (-(1 : Matrix I I ℝ)) -
    (1 : ℝ) • Q (0 : Fin 1 → ℝ) 1 = 0 := by
  simp

example : (-(1 : Matrix I I ℝ)) *ᵥ point 1 (0 : Fin 1 → ℝ) ∈
    cone (0 : Fin 1 → ℝ) 1 := by
  rw [Matrix.neg_mulVec,Matrix.one_mulVec]
  change (0≤mass (-point 1 (0 : Fin 1 → ℝ))) ∧ _
  rw [map_neg,mass_point]
  norm_num
