import PaperX.CyclotomicCrossingPair
import Mathlib.NumberTheory.Cyclotomic.Basic

/-!
# Embedding the crossed extension in a cyclotomic extension

The auxiliary field need only be contained in a cyclotomic extension. The root
of unity may lie in a larger ambient field than the original compositum.
-/

set_option autoImplicit false

noncomputable section

namespace PaperX.CyclotomicCrossing

open IntermediateField

variable {K T Ω : Type*} [Field K] [Field T] [Field Ω]
variable [Algebra K T] [Algebra K Ω]

/-- Mapping the ambient top field is exactly the image of the embedding. -/
theorem map_top_eq_fieldRange (i : T →ₐ[K] Ω) :
    (⊤ : IntermediateField K T).map i = i.fieldRange := by
  ext x
  simp only [mem_map, mem_top, true_and, AlgHom.mem_fieldRange]

/-- An equality of composita gives an actual inclusion into an adjunction
over the image of the first field. -/
theorem fieldRange_le_adjoin_of_sup_eq_top
    (E A : IntermediateField K T) (hsup : E ⊔ A = ⊤)
    (i : T →ₐ[K] Ω) (ζ : Ω) (hA : A.map i ≤ adjoin K ({ζ} : Set Ω)) :
    i.fieldRange ≤ (adjoin (E.map i) ({ζ} : Set Ω)).restrictScalars K := by
  rw [restrictScalars_adjoin_eq_sup, ← map_top_eq_fieldRange i, ← hsup,
    IntermediateField.map_sup]
  exact sup_le_sup_left hA _

variable [FiniteDimensional K T] [IsGalois K T]

/-- The crossed extension embeds into `E(ζ)` whenever the auxiliary field
embeds into `K(ζ)`. This statement does not require `ζ` to belong to `T`. -/
theorem crossing_fieldRange_le_adjoin
    (L A : IntermediateField K T) [IsGalois K L] [IsGalois K A]
    (hdisj : L.LinearDisjoint A) (hsup : L ⊔ A = ⊤)
    (sigma : L ≃ₐ[K] L) (eta : A ≃ₐ[K] A)
    (horder : orderOf sigma ∣ orderOf eta)
    (i : T →ₐ[K] Ω) (ζ : Ω) (hA : A.map i ≤ adjoin K ({ζ} : Set Ω)) :
    i.fieldRange ≤
      (adjoin ((fixedField (Subgroup.zpowers
        (crossingAutomorphism L A hdisj hsup sigma eta))).map i)
          ({ζ} : Set Ω)).restrictScalars K := by
  exact fieldRange_le_adjoin_of_sup_eq_top _ A
    (crossing_fixedField_sup_eq_top L A hdisj hsup sigma eta horder) i ζ hA

omit [FiniteDimensional K T] [IsGalois K T] in
/-- Adjoining the supplied primitive root is genuinely a cyclotomic extension
over the changed base field. -/
theorem adjoin_isCyclotomic_over_mapped_base
    (E : IntermediateField K T) (i : T →ₐ[K] Ω)
    {n : ℕ} [NeZero n] (ζ : Ω) (hζ : IsPrimitiveRoot ζ n) :
    IsCyclotomicExtension {n} (E.map i) (adjoin (E.map i) ({ζ} : Set Ω)) := by
  exact (IntermediateField.isCyclotomicExtension_singleton_iff_eq_adjoin
    n (E.map i) Ω (adjoin (E.map i) ({ζ} : Set Ω)) hζ).mpr rfl

end PaperX.CyclotomicCrossing
