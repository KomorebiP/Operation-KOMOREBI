import PaperX.AbsoluteGaloisRestriction
import Mathlib.FieldTheory.Galois.Infinite

/-! Comparison between restriction along the chosen embedding of a normal
extension and canonical restriction to a normal subfield of Qbar. The two
restriction maps differ by one fixed inner automorphism of the subfield's
Galois group, so their conjugacy coverage conditions agree. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.RestrictionEmbeddingConjugacy

abbrev Qbar := AlgebraicClosure ℚ
abbrev GQ := Gal(Qbar/ℚ)

variable (L : IntermediateField ℚ Qbar) [Normal ℚ L]

/-- A chosen embedding of a normal subfield differs from its inclusion by an
actual automorphism of that subfield. -/
def embeddingAutomorphism : Gal(L/ℚ) :=
  (AbsoluteGaloisRestriction.embedding L).restrictNormal' L

theorem embeddingAutomorphism_commutes (x : L) :
    algebraMap L Qbar (embeddingAutomorphism L x) =
      AbsoluteGaloisRestriction.embedding L x := by
  exact (AbsoluteGaloisRestriction.embedding L).restrictNormal_commutes L x

/-- Chosen and canonical restriction are intertwined by the fixed comparison
automorphism of the normal subfield. -/
theorem restriction_intertwines (σ : GQ) :
    embeddingAutomorphism L * AbsoluteGaloisRestriction.restriction L σ =
      AlgEquiv.restrictNormalHom L σ * embeddingAutomorphism L := by
  ext x
  change algebraMap L Qbar
      (embeddingAutomorphism L (AbsoluteGaloisRestriction.restriction L σ x)) =
    algebraMap L Qbar (AlgEquiv.restrictNormalHom L σ (embeddingAutomorphism L x))
  rw [embeddingAutomorphism_commutes]
  erw [AbsoluteGaloisRestriction.restriction_commutes]
  change σ (AbsoluteGaloisRestriction.embedding L x) =
    algebraMap L Qbar (σ.restrictNormal L (embeddingAutomorphism L x))
  rw [AlgEquiv.restrictNormal_commutes, embeddingAutomorphism_commutes]

/-- One fixed inner automorphism converts chosen restriction into canonical
restriction for every absolute Galois element. -/
theorem restriction_conjugate (σ : GQ) :
    embeddingAutomorphism L * AbsoluteGaloisRestriction.restriction L σ *
        (embeddingAutomorphism L)⁻¹ = AlgEquiv.restrictNormalHom L σ := by
  rw [restriction_intertwines, mul_assoc, mul_inv_cancel, mul_one]

/-- The two restrictions define the same conjugacy class. -/
theorem restriction_isConj (σ : GQ) :
    IsConj (AbsoluteGaloisRestriction.restriction L σ)
      (AlgEquiv.restrictNormalHom L σ) :=
  isConj_iff.mpr ⟨embeddingAutomorphism L, restriction_conjugate L σ⟩

end PaperX.RestrictionEmbeddingConjugacy
