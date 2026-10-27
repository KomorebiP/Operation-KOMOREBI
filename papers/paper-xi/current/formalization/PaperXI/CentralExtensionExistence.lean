import PaperXI.CentralExtensionUniqueness
import PaperXI.CentralCharacterRepresentation

/-! Existence is obtained from an actual simple ideal of the constructed
twisted algebra, then the reverse action construction. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralExtensionExistence
open CentralExtension CentralCharacter CocycleCommutator

variable {Z H A : Type*} [CommGroup Z] [Group H] [CommGroup A] [Fintype A]

set_option backward.isDefEq.respectTransparency false in
/-- There exists an actual irreducible representation with the prescribed
central action and square-root dimension. -/
theorem exists_irreducible (D : Datum Z H A) (ζ : Z →* ℂˣ)
    (hnd : radical (scalarCocycle D ζ) = ⊥) :
    let B : Type _ := CentralCharacter.Algebra D ζ
    letI : Ring B := inferInstance
    letI : Algebra ℂ B := inferInstance
    ∃ I : Ideal B, ∃ σ : Representation ℂ H I,
      Representation.IsIrreducible σ ∧
      (∀ z, σ (D.i z) = (ζ z : ℂ) • (LinearMap.id : Module.End ℂ I)) ∧
      Module.finrank ℂ I = Nat.sqrt (Fintype.card A) := by
  let B : Type _ := CentralCharacter.Algebra D ζ
  let : Ring B := inferInstance
  let : Algebra ℂ B := inferInstance
  let : IsSimpleRing B :=
    TwistedSimple.isSimpleRing (scalarCocycle D ζ) (normalized_scalarCocycle D ζ) hnd
  obtain ⟨I, hI⟩ := SimpleModuleClassification.exists_simple_ideal B
  let : IsSimpleModule B I := hI
  let φ : B →ₐ[ℂ] Module.End ℂ I := Algebra.lsmul ℂ ℂ I (A := B)
  let σ := ofAlgebraAction (W := I) D ζ φ
  have hc : ∀ z, σ (D.i z) = (ζ z : ℂ) • LinearMap.id := ofAlgebraAction_central (W := I) D ζ φ
  have hs : IsSimpleModule B (AlgebraActionModule.Space (B := B) φ) :=
    (AlgebraActionModule.ofModule_simple_iff (B := B) (W := I)).mpr hI
  have hirr : Representation.IsIrreducible σ :=
    (ofAlgebraAction_irreducible_iff (W := I) D ζ φ).mpr hs
  have hd : Module.finrank ℂ I = Nat.sqrt (Fintype.card A) :=
    TwistedModules.finrank_sqrt (scalarCocycle D ζ) (normalized_scalarCocycle D ζ) hnd I
  exact ⟨I, σ, hirr, hc, hd⟩

end PaperXI.CentralExtensionExistence
