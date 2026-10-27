import PaperXI.HenselianLiftTower
import PaperXI.ValuationFixingField
import PaperXI.UnramifiedValuation

/-! Replace the previous residue stabilizer by the decomposition group over an
actual, constructed finite intermediate field. This does not assert its full
local-field unramified classification or an absolute Weil identification. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HenselianWeilAttachment
open IsLocalRing PaperXI.ResidueWeil PaperXI.FiniteResidueBaseChange
open PaperXI.ResidueDegreeBaseChange
variable (k k' K : Type*) {L : Type*} [Field k] [Fintype k] [Field k'] [Fintype k']
  [Algebra k k'] [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [HenselianLocalRing A]
  [Algebra k (ResidueField A)] [Algebra k' (ResidueField A)]
  [Algebra.IsAlgebraic k (ResidueField A)] [Algebra.IsAlgebraic k' (ResidueField A)]

abbrev liftedField := HenselianFieldLift.field k' K A (algebraMap k' (ResidueField A))

omit [Algebra.IsAlgebraic k' (ResidueField A)] in
/-- The actual field fixer equals the residue-field fixer from v0.29. -/
theorem field_fixing_eq :
    HenselianFieldLift.fixing k' K A (algebraMap k' (ResidueField A)) =
      UnramifiedValuation.fixingGroup k' K A := by
  ext g
  exact HenselianFieldLift.fixing_iff_residue k' K A (algebraMap k' (ResidueField A)) g

/-- Actual decomposition group over the constructed field, not a renamed residue subgroup. -/
def decompositionEquiv : A.decompositionSubgroup (liftedField k' K A) ≃*
    UnramifiedValuation.fixingGroup k' K A :=
  (ValuationFixingField.decompositionEquiv K A (liftedField k' K A)).trans
    (MulEquiv.subgroupCongr (field_fixing_eq k' K A))

omit [Algebra.IsAlgebraic k' (ResidueField A)] in
/-- The underlying valuation-ring automorphisms agree. -/
theorem ring_action (g : A.decompositionSubgroup (liftedField k' K A)) (x : A) :
    (decompositionEquiv k' K A g).val • x = g • x := rfl

omit [Algebra.IsAlgebraic k' (ResidueField A)] in
/-- So do the actual residue actions. -/
theorem residue_action (g : A.decompositionSubgroup (liftedField k' K A)) (x : ResidueField A) :
    (decompositionEquiv k' K A g).val • x = g • x := by
  obtain ⟨a,rfl⟩ := residue_surjective x
  rw [← ResidueField.residue_smul, ← ResidueField.residue_smul]
  rfl

omit [Algebra.IsAlgebraic k' (ResidueField A)] in
/-- Residue action homomorphisms commute with the actual decomposition equivalence. -/
theorem residue_hom (g : A.decompositionSubgroup (liftedField k' K A)) :
    ValuationConductor.residue A (UnramifiedValuation.fixingGroup k' K A)
      (decompositionEquiv k' K A g) =
    ValuationConductor.residue A (A.decompositionSubgroup (liftedField k' K A)) g := by
  apply RingEquiv.ext
  exact residue_action k' K A g

/-- Isomorphism of the two pullbacks with the same geometric residue Frobenius. -/
def pullbackEquiv :
    Pullback (ValuationConductor.residue A (A.decompositionSubgroup (liftedField k' K A)))
      (geometric k' (ResidueField A)) ≃*
    Pullback (ValuationConductor.residue A (UnramifiedValuation.fixingGroup k' K A))
      (geometric k' (ResidueField A)) where
  toFun w := ⟨(decompositionEquiv k' K A w.val.1, w.val.2), by
    change ValuationConductor.residue A (UnramifiedValuation.fixingGroup k' K A)
      (decompositionEquiv k' K A w.val.1) = _
    rw [residue_hom]; exact w.property⟩
  invFun w := ⟨((decompositionEquiv k' K A).symm w.val.1, w.val.2), by
    change ValuationConductor.residue A (A.decompositionSubgroup (liftedField k' K A))
      ((decompositionEquiv k' K A).symm w.val.1) = _
    rw [← residue_hom k' K A, (decompositionEquiv k' K A).apply_symm_apply]
    exact w.property⟩
  left_inv w := by
    apply Subtype.ext
    exact Prod.ext ((decompositionEquiv k' K A).symm_apply_apply _) rfl
  right_inv w := by
    apply Subtype.ext
    exact Prod.ext ((decompositionEquiv k' K A).apply_symm_apply _) rfl
  map_mul' a b := by
    apply Subtype.ext
    exact Prod.ext ((decompositionEquiv k' K A).map_mul _ _) rfl

/-- Final source-facing bridge: an actual field-base decomposition pullback is
isomorphic to the original integer-degree subgroup. -/
def sourceEquiv :
    Pullback (ValuationConductor.residue A (A.decompositionSubgroup (liftedField k' K A)))
      (geometric k' (ResidueField A)) ≃*
    periodSubgroup (ValuationConductor.residue A (A.decompositionSubgroup K))
      (geometric k (ResidueField A)) (Module.finrank k k') :=
  (pullbackEquiv k' K A).trans (UnramifiedValuation.degreeSubgroupEquiv k k' K A)

/-- The literal inclusion for the newly constructed field base. -/
def embedding :
    Pullback (ValuationConductor.residue A (A.decompositionSubgroup (liftedField k' K A)))
      (geometric k' (ResidueField A)) →*
    Pullback (ValuationConductor.residue A (A.decompositionSubgroup K))
      (geometric k (ResidueField A)) :=
  (UnramifiedValuation.embedding k k' K A).comp (pullbackEquiv k' K A).toMonoidHom

/-- This is an actual injection, not a comparison of group cardinalities. -/
theorem embedding_injective : Function.Injective (embedding k k' K A) :=
  (UnramifiedValuation.embedding_injective k k' K A).comp (pullbackEquiv k' K A).injective

/-- Integer Frobenius degree scales by the residue-field degree. -/
theorem degree_formula
    (w : Pullback (ValuationConductor.residue A (A.decompositionSubgroup (liftedField k' K A)))
      (geometric k' (ResidueField A))) :
    Multiplicative.toAdd (embedding k k' K A w).val.2 =
      (Module.finrank k k' : ℤ) * Multiplicative.toAdd w.val.2 := rfl

/-- The embedded group has exactly the required degree-divisible range. -/
theorem embedding_range : (embedding k k' K A).range =
    periodSubgroup (ValuationConductor.residue A (A.decompositionSubgroup K))
      (geometric k (ResidueField A)) (Module.finrank k k') := by
  ext w
  constructor
  · rintro ⟨v,rfl⟩
    change UnramifiedValuation.embedding k k' K A (pullbackEquiv k' K A v) ∈ _
    rw [← UnramifiedValuation.embedding_range k k' K A]
    exact ⟨_,rfl⟩
  · intro h
    rw [← UnramifiedValuation.embedding_range k k' K A] at h
    obtain ⟨v,rfl⟩ := h
    refine ⟨(pullbackEquiv k' K A).symm v, ?_⟩
    change UnramifiedValuation.embedding k k' K A (pullbackEquiv k' K A
      ((pullbackEquiv k' K A).symm v)) = _
    rw [(pullbackEquiv k' K A).apply_symm_apply]

omit [Algebra.IsAlgebraic k' (ResidueField A)] in
/-- Field fixing by a base pullback element is exactly degree divisibility. -/
theorem fixes_liftedField_iff
    (w : Pullback (ValuationConductor.residue A (A.decompositionSubgroup K))
      (geometric k (ResidueField A))) :
    (∀ x ∈ liftedField k' K A, w.val.1.val x = x) ↔
      (Module.finrank k k' : ℤ) ∣ Multiplicative.toAdd w.val.2 := by
  rw [← IntermediateField.mem_fixingSubgroup_iff]
  change w.val.1 ∈ HenselianFieldLift.fixing k' K A (algebraMap k' (ResidueField A)) ↔ _
  rw [field_fixing_eq]
  exact FiniteResidueSubgroup.projection_mem_iff k k' (ResidueField A) _ w

end PaperXI.HenselianWeilAttachment
