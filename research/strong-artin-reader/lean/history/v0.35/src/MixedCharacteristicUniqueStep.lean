import FrobeniusNormRigidity

/-! Uniform root existence and uniqueness on the actual Z/(mp) -> Z/m layer. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
open SquareZeroH2 MixedCharacteristic NonsemisimpleNorm
variable (p m : ℕ) [Fact (Nat.Prime p)] (hpm : p ∣ m) (hm : m ≠ 0)
variable (n : Type) [Fintype n] [DecidableEq n]

omit [Fact (Nat.Prime p)] in
theorem conjugate_power_coord (F : (Matrix n n (Upper p m))ˣ)
    (j : ℕ) (x : (matrixDatum p m hpm n).Kernel) :
    kernelCoordinates p m hpm n hm ((matrixDatum p m hpm n).conjugate (F^j) x) =
      (residualAdjoint p m n F ^ j) (kernelCoordinates p m hpm n hm x) := by
  induction j with
  | zero => simp
  | succ j ih =>
    rw [pow_succ', Datum.conjugate_mul, Module.End.mul_apply, conjugation_coordinates, ih, pow_succ']
    rfl

theorem layer_norm_coordinates (F : (Matrix n n (Upper p m))ˣ)
    (d : ℕ) (x : (matrixDatum p m hpm n).Kernel) :
    kernelCoordinates p m hpm n hm ((matrixDatum p m hpm n).frobeniusNorm F d x) =
      operatorNorm (adjoint n (residualFrobenius p m n F)) d
        (kernelCoordinates p m hpm n hm x) := by
  induction d with
  | zero => simp
  | succ j ih =>
    rw [Datum.frobeniusNorm_succ, map_add, ih,
      conjugate_power_coord p m hpm hm n F, operatorNorm_succ]
    rfl

include hm in
theorem layer_norm_bijective (F : (Matrix n n (Upper p m))ˣ) (d : ℕ)
    (h : Nonresonant n (residualFrobenius p m n F) d) :
    Function.Bijective ((matrixDatum p m hpm n).frobeniusNorm F d) := by
  let E := kernelCoordinates p m hpm n hm
  constructor
  · intro x y hxy
    apply E.injective
    apply h.1
    rw [← layer_norm_coordinates p m hpm hm n F,
      ← layer_norm_coordinates p m hpm hm n F, hxy]
  · intro y
    obtain ⟨z, hz⟩ := h.2 (E y)
    refine ⟨E.symm z, E.injective ?_⟩
    rw [layer_norm_coordinates p m hpm hm n F]
    simpa only [E, AddEquiv.apply_symm_apply] using hz

include hm in
theorem mixed_unique_power_lift (F U : (Matrix n n (Upper p m))ˣ) (d : ℕ)
    (h : Nonresonant n (residualFrobenius p m n F) d)
    (hU : (matrixDatum p m hpm n).q U = (matrixDatum p m hpm n).q (F^d)) :
    ∃! F' : (Matrix n n (Upper p m))ˣ,
      (matrixDatum p m hpm n).q F' = (matrixDatum p m hpm n).q F ∧ F'^d = U :=
  exists_unique_power_lift (matrixDatum p m hpm n) F U d
    (layer_norm_bijective p m hpm hm n F d h) hU

end Komorebi.StrongArtin.FrobeniusTower
