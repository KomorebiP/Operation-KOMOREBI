/-
Compatibility export of the pinned AINTLIB density-lift contract, implemented
through the independently compiled degree-one and zero-density-error modules.
The statement retains the actual cyclic-density premise without adding assumptions.
-/
module
public import CebotarevDensity.FixedFieldDensityTransfer

@[expose] public section
noncomputable section
open NumberField
namespace Chebotarev
variable {K L : Type*} [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L]

/-- The pinned external interface, with the same fixed-field, restriction and cyclic-density inputs. -/
theorem density_lift_through_fixedField
    (σ : Gal(L/K)) (E : IntermediateField K L) (σE : Gal(L/E))
    (hσE : letI : IsScalarTower K ↥E L := E.isScalarTower_mid'; σE.restrictScalars K = σ)
    (_hEfix : E = IntermediateField.fixedField (Subgroup.zpowers σ))
    (_hab : HasDirichletDensity
        {P : Ideal (𝓞 ↥E) | P.IsPrime ∧ UnramifiedIn ↥E L P ∧
          frobeniusClass ↥E L P = ConjClasses.mk σE}
        ((Nat.card Gal(L/E) : ℝ)⁻¹)) :
    HasDirichletDensity
      {𝔭 : Ideal (𝓞 K) | 𝔭.IsPrime ∧ UnramifiedIn K L 𝔭 ∧
        frobeniusClass K L 𝔭 = ConjClasses.mk σ}
      ((Nat.card (ConjClasses.mk σ).carrier : ℝ) / Nat.card Gal(L/K)) := by
  revert σE
  subst E
  intro σE hσE hab
  have hσ : σE = FixedFieldFibres.generator K L σ :=
    AlgEquiv.restrictScalars_injective K
      (hσE.trans (FixedFieldFibres.generator_restrict K L σ).symm)
  have hcard : Nat.card Gal(L/(↥(IntermediateField.fixedField (Subgroup.zpowers σ)))) =
      orderOf σ := by
    rw [← Nat.card_congr (IntermediateField.subgroupEquivAlgEquiv (Subgroup.zpowers σ)).toEquiv,
      Nat.card_zpowers]
  rw [hσ, hcard] at hab
  exact FixedFieldDensityTransfer.conjugacy_density_of_cyclic_density K L σ hab

end Chebotarev
