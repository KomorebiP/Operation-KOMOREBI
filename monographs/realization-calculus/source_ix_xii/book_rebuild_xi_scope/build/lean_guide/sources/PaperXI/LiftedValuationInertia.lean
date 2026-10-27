import PaperXI.LiftedFullResidue

/-! The actual residue-action inertia of the generated field is trivial.
This is not an assumed ramification-index certificate. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LiftedValuationInertia
open IsLocalRing PaperXI.LiftedResidueDegree PaperXI.LiftedFullResidue
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [HenselianLocalRing A] [Fintype (ResidueField A)]
variable (s : IntermediateField (BaseResidue K A) (ResidueField A))
local instance subfieldFintype : Fintype s := Fintype.ofFinite s

/-- A valuation-preserving automorphism with trivial residue action fixes every
Hensel generator and therefore the whole generated field. -/
theorem inertia_trivial : (valuation K A s).inertiaSubgroup K = ⊥ := by
  apply le_antisymm ?_ bot_le
  intro g hg
  change g = 1
  have he : (field K A s).val.comp g.val.toAlgHom = (field K A s).val := by
    apply IntermediateField.adjoin_algHom_ext K
    rintro _ ⟨a, rfl⟩
    let z := HenselianResidueLift.lift s A s.val.toRingHom a
    let e : field K A s := ⟨(z : L), HenselianFieldLift.element_mem s K A s.val.toRingHom a⟩
    let v : valuation K A s := ⟨e, z.property⟩
    let σ := MulSemiringAction.toRingAut ((valuation K A s).decompositionSubgroup K)
      (valuation K A s) g
    let inc : valuation K A s →+* A := ValuationResidueEmbedding.inclusion A (field K A s).val.toRingHom
    have hv : v ^ Fintype.card s = v := by
      apply Subtype.ext
      apply Subtype.ext
      exact congrArg (fun x : A => (x : L)) (HenselianResidueLift.lift_pow s A s.val.toRingHom a)
    have hy : inc (σ v) ^ Fintype.card s = inc (σ v) := by
      rw [← map_pow, ← map_pow, hv]
    have hres : residue (valuation K A s) (σ v) = residue (valuation K A s) v := by
      change residue (valuation K A s) (g • v) = _
      rw [ResidueField.residue_smul]
      change MulSemiringAction.toRingAut ((valuation K A s).decompositionSubgroup K)
        (ResidueField (valuation K A s)) g = 1 at hg
      exact RingEquiv.congr_fun hg (residue (valuation K A s) v)
    have hresA : residue A (inc (σ v)) = residue A z :=
      congrArg (ValuationResidueEmbedding.residueMap A (field K A s).val.toRingHom) hres
    have hz := HenselianResidueLift.unique_lift s A s.val.toRingHom hy
      (HenselianResidueLift.lift_pow s A s.val.toRingHom a) hresA
    exact congrArg (fun x : A => (x : L)) hz
  apply Subtype.ext
  apply AlgEquiv.ext
  intro x
  exact (field K A s).val.injective (AlgHom.congr_fun he x)

end PaperXI.LiftedValuationInertia
