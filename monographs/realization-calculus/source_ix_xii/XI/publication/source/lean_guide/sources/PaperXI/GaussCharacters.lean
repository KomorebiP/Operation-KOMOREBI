import PaperXI.GaussSums

/-! Translation to the manuscript's multiplicative characters kˣ → ℂˣ.
No additional unitarity assumption is needed over a finite field. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.GaussCharacters
open scoped Classical
variable {k : Type*} [Field k] [Fintype k]

/-- The manuscript's Gauss sum for a character on the unit group. -/
def sum (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) : ℂ :=
  ∑ x : kˣ, (χ x : ℂ) * ψ x

/-- Zero extension preserves the literal unit-group sum. -/
theorem sum_eq_unitSum (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) :
    sum χ ψ = GaussSums.unitSum (MulChar.ofUnitHom χ) ψ := by
  simp only [sum, GaussSums.unitSum, MulChar.ofUnitHom_coe]

omit [Fintype k] in
/-- A nontrivial unit-group character remains nontrivial after zero extension. -/
theorem extension_ne_one {χ : kˣ →* ℂˣ} (hχ : χ ≠ 1) :
    MulChar.ofUnitHom χ ≠ 1 := by
  intro h
  apply hχ
  ext x
  have hx := congrArg (fun f : MulChar k ℂ => f (x : k)) h
  simpa only [MulChar.ofUnitHom_coe, MulChar.one_apply_coe,
    MonoidHom.one_apply, Units.val_one] using hx

omit [Fintype k] in
/-- Inverting the unit-group character agrees with inverting its extension. -/
theorem extension_inverse (χ : kˣ →* ℂˣ) :
    MulChar.ofUnitHom χ⁻¹ = (MulChar.ofUnitHom χ)⁻¹ := by
  exact (MulChar.mulEquivToUnitHom (R := k) (R' := ℂ)).symm.map_inv χ

/-- Proposition 6.1 in the exact unit-group character convention. -/
theorem magnitude {χ : kˣ →* ℂˣ} {ψ : AddChar k ℂ}
    (hχ : χ ≠ 1) (hψ : ψ ≠ 1) :
    ‖sum χ ψ‖ = Real.sqrt (Fintype.card k) := by
  rw [sum_eq_unitSum]
  exact GaussSums.magnitude (extension_ne_one hχ) hψ

/-- Definition 6.2 uses the positive square root of the field cardinality. -/
def phase (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) : ℂ :=
  sum χ ψ / (Real.sqrt (Fintype.card k) : ℂ)

/-- Normalization commutes with extending the multiplicative character. -/
theorem phase_eq (χ : kˣ →* ℂˣ) (ψ : AddChar k ℂ) :
    phase χ ψ = GaussSums.phase (MulChar.ofUnitHom χ) ψ := by
  rw [phase, GaussSums.phase, sum_eq_unitSum]

/-- Definition 6.2's unit-circle assertion, for the manuscript's character type. -/
theorem phase_norm {χ : kˣ →* ℂˣ} {ψ : AddChar k ℂ}
    (hχ : χ ≠ 1) (hψ : ψ ≠ 1) : ‖phase χ ψ‖ = 1 := by
  rw [phase_eq]
  exact GaussSums.phase_norm (extension_ne_one hχ) hψ

/-- Proposition 6.3 with χ(-1) evaluated in the actual unit group. -/
theorem phase_duality {χ : kˣ →* ℂˣ} {ψ : AddChar k ℂ}
    (hχ : χ ≠ 1) (hψ : ψ ≠ 1) :
    phase χ ψ * phase χ⁻¹ ψ = (χ (-1) : ℂ) := by
  rw [phase_eq, phase_eq, extension_inverse,
    GaussSums.phase_duality (extension_ne_one hχ) hψ]
  exact MulChar.ofUnitHom_coe χ (-1)

end PaperXI.GaussCharacters
