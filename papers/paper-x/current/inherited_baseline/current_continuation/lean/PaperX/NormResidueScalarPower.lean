import PaperX.NormResidueScalarWitness

/-!
# Scalar power witnesses for residue-norm characters

Scalar units in the residue algebra have determinant norm equal to the
`[K : ℚ]`-th power of the corresponding scalar residue.  If that power map is
bijective on `(ZMod m)ˣ`, every nontrivial character on scalar units therefore
produces the unit witness required by the norm-residue cancellation theorem.
-/

set_option autoImplicit false
noncomputable section

open scoped NumberField

namespace PaperX.NormResidue

variable (K : Type*) [Field K] [NumberField K]

/-- A nontrivial multiplicative character on scalar units has a concrete
scalar witness. -/
theorem exists_scalar_character_witness (m : ℕ) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1) :
    ∃ b : (ZMod m)ˣ, χ (b : ZMod m) ≠ 1 := by
  by_contra h
  push Not at h
  apply hχ
  ext b
  simpa using h b

/-- If the degree is coprime to the order of the scalar unit group, the degree
power map on scalar units is surjective.  Hence every nontrivial scalar-unit
character supplies an actual unit of `𝓞 K / m 𝓞 K` on which the determinant
norm character is nontrivial. -/
theorem exists_scalarResidueUnit_witness_of_card_coprime
    (m : ℕ) (hm : m ≠ 0) (χ : ZMod m →*₀ ℂ)
    (hχ : χ.toMonoidHom.comp (Units.coeHom (ZMod m)) ≠ 1)
    (hdeg : (Nat.card ((ZMod m)ˣ)).Coprime (Module.finrank ℚ K)) :
    ∃ u : (𝓞 K ⧸ modulusIdeal (𝓞 K) m)ˣ,
      χ (integerQuotientNorm K m (u : 𝓞 K ⧸ modulusIdeal (𝓞 K) m)) ≠ 1 := by
  let _ : NeZero m := ⟨hm⟩
  obtain ⟨b, hb⟩ := exists_scalar_character_witness m χ hχ
  let d : ℕ := Module.finrank ℚ K
  let a : (ZMod m)ˣ := b ^ ((d⁻¹ : ZMod (Nat.card ((ZMod m)ˣ))).val)
  have ha : a ^ d = b := by
    dsimp [a, d]
    exact pow_zmod_val_inv_pow hdeg.gcd_eq_one b
  refine ⟨scalarResidueUnit K m hm a, ?_⟩
  rw [integerQuotientNorm_scalarResidueUnit]
  have ha' : (a : ZMod m) ^ Module.finrank ℚ K = (b : ZMod m) := by
    simpa [d] using congrArg (fun u : (ZMod m)ˣ => (u : ZMod m)) ha
  rw [ha']
  exact hb

end PaperX.NormResidue
