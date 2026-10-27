import PaperXI.ValuationResidueEmbedding
import Mathlib.FieldTheory.Galois.IsGaloisGroup

/-! Derive residue-automorphism lifting in a finite Galois extension with invariant
Henselian valuation and finite residue field. No surjectivity is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HenselianGaloisResidue
open IsLocalRing
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L)
variable (stable : ∀ g : L ≃ₐ[K] L, g ∈ A.decompositionSubgroup K)
def decompositionMap : (L ≃ₐ[K] L) →* A.decompositionSubgroup K where
  toFun g := ⟨g, stable g⟩
  map_one' := rfl
  map_mul' _ _ := rfl
def residueAction : (L ≃ₐ[K] L) →* RingAut (ResidueField A) :=
  (MulSemiringAction.toRingAut (A.decompositionSubgroup K) (ResidueField A)).comp
    (decompositionMap K A stable)
@[simp] theorem residueAction_residue (g : L ≃ₐ[K] L) (x : A) :
    residueAction K A stable g (residue A x) =
      residue A ((decompositionMap K A stable g) • x) := by rfl
theorem fixes_base (g : L ≃ₐ[K] L)
    (x : ResidueField (A.comap (algebraMap K L))) :
    residueAction K A stable g
      (ValuationResidueEmbedding.residueMap A (algebraMap K L) x) =
      ValuationResidueEmbedding.residueMap A (algebraMap K L) x := by
  obtain ⟨x, rfl⟩ := residue_surjective x
  rw [ValuationResidueEmbedding.residueMap_residue, residueAction_residue]
  congr 1
  apply Subtype.ext
  exact g.commutes x.val
variable [FiniteDimensional K L] [IsGalois K L]
variable [HenselianLocalRing A] [Fintype (ResidueField A)]
theorem fixed_iff_base (z : ResidueField A) :
    (∀ g, residueAction K A stable g z = z) ↔
      z ∈ Set.range (ValuationResidueEmbedding.residueMap A (algebraMap K L)) := by
  constructor
  · intro hz
    let a := HenselianResidueLift.lift (ResidueField A) A (RingHom.id _) z
    have ha : ∀ g : L ≃ₐ[K] L, g (a : L) = (a : L) := by
      intro g
      have hh : (decompositionMap K A stable g) • a = a := by
        apply (HenselianResidueLift.automorphism_fix_iff (ResidueField A) A (RingHom.id _)
          (MulSemiringAction.toRingAut (A.decompositionSubgroup K) A
            (decompositionMap K A stable g)) z).mpr
        change residue A ((decompositionMap K A stable g) • a) = z
        rw [← residueAction_residue]
        simpa only [a, HenselianResidueLift.residue_lift, RingHom.id_apply] using hz g
      exact congrArg (fun x : A => (x : L)) hh
    obtain ⟨b, hb⟩ := IntermediateField.mem_bot.mp ((IsGalois.mem_bot_iff_fixed (a : L)).mpr ha)
    apply (ValuationResidueEmbedding.mem_range_iff A (algebraMap K L) z).mpr
    refine ⟨b, hb ▸ a.property, ?_⟩
    have he : (⟨algebraMap K L b, hb ▸ a.property⟩ : A) = a := Subtype.ext hb
    rw [he]
    exact HenselianResidueLift.residue_lift (ResidueField A) A (RingHom.id _) z
  · rintro ⟨x, rfl⟩ g
    exact fixes_base K A stable g x
theorem lift_automorphism (σ : RingAut (ResidueField A))
    (hσ : ∀ x : ResidueField (A.comap (algebraMap K L)),
      σ (ValuationResidueEmbedding.residueMap A (algebraMap K L) x) =
        ValuationResidueEmbedding.residueMap A (algebraMap K L) x) :
    ∃ g : L ≃ₐ[K] L, residueAction K A stable g = σ := by
  let : MulSemiringAction (L ≃ₐ[K] L) (ResidueField A) :=
    MulSemiringAction.compHom _ (residueAction K A stable)
  let τ : ResidueField A ≃ₐ[FixedPoints.subfield (L ≃ₐ[K] L) (ResidueField A)]
      ResidueField A := AlgEquiv.ofRingEquiv (f := σ) (by
    intro x
    obtain ⟨b, hb⟩ := (fixed_iff_base K A stable x.val).mp x.property
    change σ x.val = x.val
    rw [← hb]
    exact hσ b)
  obtain ⟨g, hg⟩ := FixedPoints.toAlgAut_surjective (L ≃ₐ[K] L) (ResidueField A) τ
  exact ⟨g, RingEquiv.ext (fun x => AlgEquiv.congr_fun hg x)⟩
end PaperXI.HenselianGaloisResidue
