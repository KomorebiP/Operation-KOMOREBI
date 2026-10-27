import PaperXI.HenselianFieldLift

/-! Restricting the base field in the literal decomposition subgroup. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ValuationFixingField
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) (E : IntermediateField K L)

/-- Valuation-preserving automorphisms over E are exactly valuation-preserving
K-automorphisms fixing every element of E. -/
def decompositionEquiv : A.decompositionSubgroup E ≃*
    E.fixingSubgroup.comap (A.decompositionSubgroup K).subtype where
  toFun g := ⟨⟨g.val.restrictScalars K, g.property⟩, by
    change g.val.restrictScalars K ∈ E.fixingSubgroup
    rw [IntermediateField.mem_fixingSubgroup_iff]
    intro x hx
    exact g.val.commutes ⟨x,hx⟩⟩
  invFun g := ⟨{ g.val.val.toRingEquiv with
    commutes' := fun x => (IntermediateField.mem_fixingSubgroup_iff E g.val.val).mp g.property x x.property },
    g.val.property⟩
  left_inv g := by rfl
  right_inv g := by rfl
  map_mul' g h := by rfl

/-- The equivalence preserves the ambient field automorphism literally. -/
@[simp] theorem decompositionEquiv_apply (g : A.decompositionSubgroup E) (x : L) :
    (decompositionEquiv K A E g).val.val x = g.val x := rfl

/-- In particular the induced actions on the valuation ring agree. -/
theorem ring_action (g : A.decompositionSubgroup E) (x : A) :
    ((decompositionEquiv K A E g).val • x : A) = g • x := rfl

/-- And their actual residue actions agree, not merely their degree indices. -/
theorem residue_action (g : A.decompositionSubgroup E) (x : IsLocalRing.ResidueField A) :
    (decompositionEquiv K A E g).val • x = g • x := by
  obtain ⟨a,rfl⟩ := IsLocalRing.residue_surjective x
  rw [← IsLocalRing.ResidueField.residue_smul, ← IsLocalRing.ResidueField.residue_smul]
  rfl

end PaperXI.ValuationFixingField
