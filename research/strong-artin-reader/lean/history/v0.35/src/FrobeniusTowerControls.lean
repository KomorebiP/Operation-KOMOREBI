import SimultaneousPadicFrobenius

/-! Positive nonsemisimple all-depth sector and a resonant partial branch that
cannot extend. The latter does not disprove existence of a different full branch. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower.Controls

abbrev k := ZMod 3
abbrev n := Fin 2

def unipotent : (Matrix n n k)ˣ where
  val := !![1, 1; 0, 1]
  inv := !![1, -1; 0, 1]
  val_inv := by decide
  inv_val := by decide

set_option maxRecDepth 10000 in
theorem unipotent_adjoint_cube : (adjoint n unipotent - 1)^3 = 0 := by
  have h : ∀ X : Matrix n n k, ((adjoint n unipotent - 1)^3 : Module.End k (Matrix n n k)) X = 0 := by decide
  ext X i j
  exact congrFun (congrFun (h X) i) j

/-- A genuine nonsemisimple residual Frobenius supports unique full p-adic square roots. -/
theorem unipotent_unique_padic_square_root
    (U : (Matrix n n ℤ_[3])ˣ)
    (hU : padicUnitReduction 3 n 0 U = unipotent^2) :
    ∃! F : (Matrix n n ℤ_[3])ˣ,
      padicUnitReduction 3 n 0 F = unipotent ∧ F^2 = U :=
  unipotent_adjoint_unique_padic_root 3 n 2 unipotent U hU
    ⟨3, unipotent_adjoint_cube⟩ (by decide)

def reduce27to9 : ZMod 27 →+* ZMod 9 := ZMod.castHom (by decide) _
def reduce9to3 : ZMod 9 →+* ZMod 3 := ZMod.castHom (by decide) _

theorem partial_cube_branch : reduce9to3 4 = 1 ∧ (4 : ZMod 9)^3 = 1 := by decide

theorem partial_branch_has_no_next_lift :
    ¬ ∃ x : ZMod 27, reduce27to9 x = 4 ∧ x^3 = 1 := by decide

/-- No genuine 3-adic root can extend that already-solvable mod-9 branch. -/
theorem no_padic_cube_root_above_four :
    ¬ ∃ x : ℤ_[3], x.toZModPow 2 = 4 ∧ x^3 = 1 := by
  rintro ⟨x, hx, hpow⟩
  apply partial_branch_has_no_next_lift
  refine ⟨x.toZModPow 3, ?_, ?_⟩
  · have hc := PadicInt.cast_toZModPow 2 3 (by decide) x
    exact hc.trans hx
  · change (PadicInt.toZModPow 3 x)^3 = (1 : ZMod (3^3))
    rw [← map_pow, hpow, map_one]

/-- The target itself has a full tower; only the bad intermediate branch is obstructed. -/
theorem target_has_a_different_full_root : ∃ x : ℤ_[3], x.toZModPow 1 = 1 ∧ x^3 = 1 := by
  exact ⟨1, by simp⟩

end Komorebi.StrongArtin.FrobeniusTower.Controls
