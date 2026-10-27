import MixedCharacteristicMatrixKernel
import FrobeniusSingleRestriction
import NilpotentPolynomialImage

/-! Exact uniqueness, not merely existence, in a nonresonant coefficient layer. -/
noncomputable section
namespace Komorebi.StrongArtin.FrobeniusTower
open SquareZeroH2 NonsemisimpleNorm
variable {G A B : Type} [Group G] [Ring A] [Ring B]

/-- An injective actual kernel norm makes the power map injective on one residue fibre. -/
theorem power_fibre_injective (D : Datum G A B) (F F' : Aˣ) (d : ℕ)
    (hn : Function.Injective (D.frobeniusNorm F d))
    (hq : D.q F' = D.q F) (hp : F'^d = F^d) : F' = F := by
  let x := D.unitMismatch F' F hq
  have hx : D.kernelUnit x * F = F' := D.unitMismatch_spec F' F hq
  have hn0 : D.frobeniusNorm F d x = 0 := by
    apply D.kernelUnit_injective
    apply mul_right_cancel (b := F^d)
    rw [← D.kernel_perturbed_power, hx, hp, D.kernelUnit_zero, one_mul]
  have hx0 : x = 0 := hn (hn0.trans (map_zero _).symm)
  simpa [hx0] using hx.symm

/-- A bijective norm gives a unique original Frobenius root in its residue fibre. -/
theorem exists_unique_power_lift (D : Datum G A B) (F U : Aˣ) (d : ℕ)
    (hn : Function.Bijective (D.frobeniusNorm F d))
    (hU : D.q U = D.q (F^d)) :
    ∃! F' : Aˣ, D.q F' = D.q F ∧ F'^d = U := by
  obtain ⟨x, hx⟩ := hn.2 (D.unitMismatch U (F^d) hU)
  obtain ⟨F', hq, hp⟩ := (D.power_lifting_iff_norm_image F U d hU).2 ⟨x, hx⟩
  refine ⟨F', ⟨hq, hp⟩, ?_⟩
  intro F'' hF''
  have hnorm : D.frobeniusNorm F' d = D.frobeniusNorm F d := by
    clear * - D F F' hq
    induction d with
    | zero => rfl
    | succ n ih =>
      change D.frobeniusNorm F' n + D.conjugate (F'^n) = _
      rw [ih]
      congr 1
      apply D.conjugate_same_residue
      simpa only [Units.val_pow_eq_pow_val, map_pow] using congrArg (fun a : B => a^n) hq
  exact power_fibre_injective D F' F'' d (hnorm ▸ hn.1)
    (hF''.1.trans hq.symm) (hF''.2.trans hp.symm)

variable {k : Type} [Field k] (n : Type) [Fintype n] [DecidableEq n]

def adjoint (F : (Matrix n n k)ˣ) : Module.End k (Matrix n n k) where
  toFun X := (F : Matrix n n k) * X * (↑F⁻¹ : Matrix n n k)
  map_add' X Y := by simp [Matrix.mul_add, Matrix.add_mul]
  map_smul' a X := by simp

/-- One condition on the residual adjoint operator; no higher-level targets occur here. -/
def Nonresonant (F : (Matrix n n k)ˣ) (d : ℕ) : Prop :=
  Function.Bijective (operatorNorm (adjoint n F) d)

/-- Prime-to-characteristic degree is enough for a unipotent adjoint action. -/
theorem nonresonant_of_unipotent_adjoint (F : (Matrix n n k)ˣ) (d : ℕ)
    (hN : IsNilpotent (adjoint n F - 1)) (hd : (d : k) ≠ 0) : Nonresonant n F d := by
  apply end_unit_bijective
  have h := aeval_isUnit_of_primary (adjoint n F) 1 (by simpa using hN)
    (normPolynomial k d) (by simpa [normPolynomial] using hd)
  simpa using h

@[simp] theorem adjoint_one : adjoint n (1 : (Matrix n n k)ˣ) = 1 := by
  ext X i j
  simp [adjoint]

theorem nonresonant_identity (d : ℕ) (hd : (d : k) ≠ 0) :
    Nonresonant n (1 : (Matrix n n k)ˣ) d := by
  apply nonresonant_of_unipotent_adjoint n _ d _ hd
  simp

end Komorebi.StrongArtin.FrobeniusTower
