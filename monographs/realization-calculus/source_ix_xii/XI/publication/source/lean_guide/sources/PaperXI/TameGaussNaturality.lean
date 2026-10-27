import PaperXI.GaussCharacters
import Mathlib.Algebra.Group.Units.Equiv

/-! Additive-character normalization is part of the finite comparison data.
These statements concern the literal finite Gauss sum, not a full local epsilon
factor. A nontrivial residue character is required for a unit-norm phase. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TameGaussNaturality
open scoped Classical
variable {k : Type*} [Field k] [Fintype k]

/-- Pull the multiplicative character back along a field automorphism. -/
def pullMul (e : k ≃+* k) (χ : kˣ →* ℂˣ) : kˣ →* ℂˣ :=
  χ.comp (Units.map e.toMonoidHom)

/-- The additive character must be transported at the same time. -/
def pullAdd (e : k ≃+* k) (ψ : AddChar k ℂ) : AddChar k ℂ :=
  ψ.compAddMonoidHom e.toAddMonoidHom

/-- Simultaneous transport of both characters is an exact change of summation variable. -/
theorem sum_transport (e : k ≃+* k) (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) :
    GaussCharacters.sum (pullMul e χ) (pullAdd e ψ) = GaussCharacters.sum χ ψ := by
  unfold GaussCharacters.sum
  exact Fintype.sum_equiv (Units.mapEquiv e.toMulEquiv).toEquiv _ _ (fun _ => rfl)

theorem phase_transport (e : k ≃+* k) (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) :
    GaussCharacters.phase (pullMul e χ) (pullAdd e ψ) = GaussCharacters.phase χ ψ := by
  unfold GaussCharacters.phase
  rw [sum_transport]

/-- Rotation of the residue character preserves the phase only with the stated
additive-character invariance. In particular this applies to Frobenius-stable ψ. -/
theorem phase_of_stable_additive (e : k ≃+* k) (χ : kˣ →* ℂˣ)
    (ψ : AddChar k ℂ) (hψ : pullAdd e ψ = ψ) :
    GaussCharacters.phase (pullMul e χ) ψ = GaussCharacters.phase χ ψ := by
  simpa only [hψ] using phase_transport e χ ψ

/-- Rescaling the additive character contributes the inverse multiplicative value. -/
theorem phase_mulShift (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) (a : kˣ) :
    GaussCharacters.phase χ (ψ.mulShift (a : k)) =
      (χ a : ℂ)⁻¹ * GaussCharacters.phase χ ψ := by
  simp only [GaussCharacters.phase, GaussCharacters.sum_eq_unitSum,
    GaussSums.unitSum_eq_gaussSum]
  rw [gaussSum_mulShift_eq, MulChar.inv_apply_eq_inv', MulChar.ofUnitHom_coe,
    mul_div_assoc]

/-- The trivial multiplicative character does not have a unit-norm normalized sum. -/
theorem phase_trivial {ψ : AddChar k ℂ} (hψ : ψ ≠ 1) :
    GaussCharacters.phase (1 : kˣ →* ℂˣ) ψ =
      -1 / (Real.sqrt (Fintype.card k) : ℂ) := by
  have he : MulChar.ofUnitHom (1 : kˣ →* ℂˣ) = (1 : MulChar k ℂ) :=
    (MulChar.mulEquivToUnitHom (R := k) (R' := ℂ)).symm.map_one
  simp only [GaussCharacters.phase, GaussCharacters.sum_eq_unitSum,
    GaussSums.unitSum_eq_gaussSum, he]
  rw [gaussSum_one_left hψ]

/-- Both trivial and nontrivial residue characters have an exact magnitude rule. -/
theorem phase_norm_cases (χ : kˣ →* ℂˣ) {ψ : AddChar k ℂ} (hψ : ψ ≠ 1) :
    ‖GaussCharacters.phase χ ψ‖ =
      if χ = 1 then (Real.sqrt (Fintype.card k))⁻¹ else 1 := by
  by_cases hχ : χ = 1
  · subst χ
    rw [ite_eq_left rfl, phase_trivial hψ, norm_div]
    simp [Complex.norm_real, Real.norm_eq_abs,
      abs_of_pos (GaussSums.sqrt_card_pos (k := k)), one_div]
  · rw [ite_eq_right hχ]
    exact GaussCharacters.phase_norm hχ hψ

/-- A declared residue phase is never zero under a nontrivial additive character. -/
theorem phase_ne_zero (χ : kˣ →* ℂˣ) {ψ : AddChar k ℂ} (hψ : ψ ≠ 1) :
    GaussCharacters.phase χ ψ ≠ 0 := by
  apply norm_ne_zero_iff.mp
  rw [phase_norm_cases χ hψ]
  split_ifs
  · exact inv_ne_zero (ne_of_gt (GaussSums.sqrt_card_pos (k := k)))
  · exact one_ne_zero

end PaperXI.TameGaussNaturality
