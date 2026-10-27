import PaperXI.ActualELatticeTypeGroup59
import PaperXI.ProductNormalizerQuotient59

/-!
# Finite residue quotient of the literal extension-field lattice product

For the actual subgroup `GL_n(O_E) U^1` in `Aut_K(E^n)`, the quotient by
literal adjacent-lattice congruence is `GL_n(k_E)`. Conjugation by the
extension-field uniformizer is the identity on this quotient.
-/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ActualELatticeQuotient59
open Matrix ValuativeRel
open ActualELatticeNormalizer59 ActualELatticeResidue59 ActualELatticeTypeGroup59

variable (K E : Type*) [Field K] [Field E] [Algebra K E]
variable (n : Type*) [Fintype n] [DecidableEq n]
variable [ValuativeRel E] [TopologicalSpace E] [IsNonarchimedeanLocalField E]

/-- The literal congruence subgroup inside the actual product group. -/
def typeCongruence : Subgroup (typeGroup K E n) :=
  (congruence K E n).subgroupOf (typeGroup K E n)

instance typeCongruence_normal : (typeCongruence K E n).Normal :=
  Subgroup.normal_subgroupOf_sup_of_le_normalizer (integralImage_normalizes K E n)

/-- The entire actual quotient is the full residue general linear group. -/
def residueEquiv : typeGroup K E n ⧸ typeCongruence K E n ≃*
    GeneralLinearGroup n 𝓀[E] :=
  ProductNormalizerQuotient59.quotientEquivOfKernel
    (integralImage K E n) (congruence K E n) (integralImage_normalizes K E n)
    (residueAction K E n) (residueAction_surjective K E n)
    (congruence_subgroupOf_integralImage K E n)

/-- The actual surjective reduction map on the product group. -/
def reduction : typeGroup K E n →* GeneralLinearGroup n 𝓀[E] :=
  (residueEquiv K E n).toMonoidHom.comp (QuotientGroup.mk' (typeCongruence K E n))

theorem reduction_surjective : Function.Surjective (reduction K E n) :=
  (residueEquiv K E n).surjective.comp (QuotientGroup.mk'_surjective _)

@[simp] theorem reduction_kernel : (reduction K E n).ker = typeCongruence K E n := by
  ext j
  change residueEquiv K E n (QuotientGroup.mk' (typeCongruence K E n) j) = 1 ↔ _
  rw [← (residueEquiv K E n).map_one, (residueEquiv K E n).injective.eq_iff]
  exact QuotientGroup.eq_one_iff j

/-- Finiteness is inherited from the actual finite residue field. -/
theorem finite_quotient : Finite (typeGroup K E n ⧸ typeCongruence K E n) :=
  Finite.of_equiv (GeneralLinearGroup n 𝓀[E]) (residueEquiv K E n).symm.toEquiv

/-- Scalar multiplication by the extension uniformizer centralizes the first factor. -/
theorem uniformizer_centralizes (g : ((n → E) ≃ₗ[K] (n → E)))
    (hg : g ∈ integralImage K E n) :
    uniformizerAction K E n * g = g * uniformizerAction K E n := by
  obtain ⟨h, rfl⟩ := hg
  exact (integralMatrix_commute K E n h).eq.symm

omit [Fintype n] [DecidableEq n] in
/-- The actual uniformizer normalizes the full adjacent-lattice congruence group. -/
theorem uniformizer_normalizes_congruence : uniformizerAction K E n ∈
    Subgroup.normalizer (congruence K E n : Set ((n → E) ≃ₗ[K] (n → E))) := by
  simpa [congruence, latticeChain] using power_normalizes_firstCongruence (uniformizerAction K E n)
    (integralLattice E n) 1

/-- It therefore normalizes the literal lattice-product group. -/
theorem uniformizer_normalizes : uniformizerAction K E n ∈
    Subgroup.normalizer (typeGroup K E n : Set ((n → E) ≃ₗ[K] (n → E))) :=
  ProductNormalizerQuotient59.normalizes_sup
    (integralImage K E n) (congruence K E n) (uniformizerAction K E n)
    (uniformizer_centralizes K E n) (uniformizer_normalizes_congruence K E n)

/-- Literal conjugation on the actual type group. -/
def uniformizerConjugation : MulAut (typeGroup K E n) :=
  ProductNormalizerQuotient59.conjugation
    (integralImage K E n) (congruence K E n) (uniformizerAction K E n)
    (uniformizer_centralizes K E n) (uniformizer_normalizes_congruence K E n)

/-- The actual residue matrix is unchanged by uniformizer conjugation. -/
theorem reduction_conjugation (j : typeGroup K E n) :
    reduction K E n (uniformizerConjugation K E n j) = reduction K E n j := by
  apply ProductNormalizerQuotient59.map_conjugation
    (integralImage K E n) (congruence K E n) (uniformizerAction K E n)
    (uniformizer_centralizes K E n) (uniformizer_normalizes_congruence K E n)
    (integralImage_normalizes K E n) (reduction K E n)
  exact (reduction_kernel K E n).ge

end PaperXI.ActualELatticeQuotient59
