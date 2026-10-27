module
public import ErrorSpanRecovery
import all ErrorSpanRecovery
import all QuantumStateBridge
import all KnillLaflammeNecessity
import all KnillLaflammeSufficiency
public import Mathlib.Tactic
/-! Author: Komorebi P. Paper VII fifth block.
Exact regression examples for singular Gram matrices, failure of correction, and the zero code.
-/
public section
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
namespace KomorebiPaperVII.KnillLaflamme.Examples
open scoped BigOperators ComplexOrder
open Matrix
abbrev Qubit := Matrix (Fin 2) (Fin 2) ℂ

noncomputable def redundantRow : Matrix (Fin 1) (Fin 2) ℂ := fun _ a => if a=0 then 3/5 else 4/5
noncomputable def redundantGram : Matrix (Fin 2) (Fin 2) ℂ := redundantRow.conjTranspose*redundantRow
noncomputable def redundantError (a : Fin 2) : Qubit := redundantRow 0 a • 1

/-- Two nonorthogonal proportional errors form a normalized channel. -/
theorem redundant_complete : (∑ a, star (redundantError a)*redundantError a)=1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [redundantError, redundantRow, Matrix.mul_apply, Matrix.star_apply,
      Fin.sum_univ_two, Matrix.one_apply]

/-- The redundant error Gram is positive semidefinite, not assumed positive definite. -/
theorem redundant_gram_positive : redundantGram.PosSemidef :=
  Matrix.posSemidef_conjTranspose_mul_self redundantRow

/-- Its actual determinant vanishes. -/
theorem redundant_gram_singular : Matrix.det redundantGram=0 := by
  norm_num [redundantGram, redundantRow, Matrix.det_fin_two, Matrix.mul_apply,
    Matrix.conjTranspose_apply]

/-- The off-diagonal Gram entry is nonzero, so diagonal-only reasoning is insufficient. -/
theorem redundant_gram_off_diagonal : redundantGram 0 1=12/25 := by
  norm_num [redundantGram, redundantRow, Matrix.mul_apply, Matrix.conjTranspose_apply]

/-- The complete criterion actually accepts this singular, nonorthogonal example. -/
theorem redundant_correctable : StateCorrectable (1 : Qubit) redundantError := by
  apply (state_correctable_iff_gram 1 (IsStarProjection.one _) redundantError redundant_complete).mpr
  refine ⟨redundantGram, redundant_gram_positive, ?_⟩
  intro a b
  ext i j
  fin_cases a <;> fin_cases b <;> fin_cases i <;> fin_cases j <;>
    norm_num [redundantError, redundantGram, redundantRow, Matrix.mul_apply,
      Matrix.star_apply, Matrix.conjTranspose_apply, Fin.sum_univ_two, Matrix.one_apply]

def dephasingError (a : Fin 2) : Qubit := Matrix.single a a 1

/-- Full dephasing is a genuine normalized channel. -/
theorem dephasing_complete : (∑ a, star (dephasingError a)*dephasingError a)=1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [dephasingError, Matrix.mul_apply, Matrix.star_apply, Matrix.single_apply,
      Fin.sum_univ_two, Matrix.one_apply]

/-- No finite recovery channel can undo full qubit dephasing on the whole code space. -/
theorem dephasing_not_correctable : ¬ Correctable (1 : Qubit) dephasingError := by
  apply not_correctable_of_nonscalar 1 (IsStarProjection.one _) dephasingError dephasing_complete 0 0
  intro c heq
  have h00 := congrArg (fun M : Qubit => M 0 0) heq
  have h11 := congrArg (fun M : Qubit => M 1 1) heq
  norm_num [dephasingError, Matrix.mul_apply, Matrix.star_apply, Matrix.single_apply,
    Fin.sum_univ_two, Matrix.one_apply] at h00 h11
  exact one_ne_zero (h00.trans h11.symm)

/-- The zero-code edge case requires no density matrix to exist on that code. -/
theorem zero_code_correctable {n I : Type*} [Fintype n] [DecidableEq n]
    [Fintype I] [DecidableEq I] (E : I → Matrix n n ℂ) : Correctable 0 E := by
  refine ⟨1, fun _ => 1, ?_, ?_⟩
  · simp
  · intro rho hrho
    have hz : rho=0 := by simpa using hrho.symm
    simp [hz, noise]

end KomorebiPaperVII.KnillLaflamme.Examples
