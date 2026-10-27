import PaperXI.LiftedResidueDegree

/-! The whole residue field of the lifted intermediate field, not merely an
embedded copy of the requested finite field. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LiftedFullResidue
open IsLocalRing PaperXI.LiftedResidueDegree
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [HenselianLocalRing A] [Fintype (ResidueField A)]
variable (s : IntermediateField (BaseResidue K A) (ResidueField A))
local instance subfieldFintype : Fintype s := Fintype.ofFinite s

/-- Restrict the valuation to the field actually constructed from Hensel roots. -/
def valuation : ValuationSubring (field K A s) := A.comap (field K A s).val.toRingHom

def residueMap : ResidueField (valuation K A s) →+* ResidueField A :=
  ValuationResidueEmbedding.residueMap A (field K A s).val.toRingHom

/-- Every requested residue has a representative in the lifted field. -/
theorem residueMap_contains (x : s) :
    (x : ResidueField A) ∈ Set.range (residueMap K A s) := by
  let a := HenselianResidueLift.lift s A s.val.toRingHom x
  let e : field K A s := ⟨(a : L), HenselianFieldLift.element_mem s K A s.val.toRingHom x⟩
  let u : valuation K A s := ⟨e, a.property⟩
  refine ⟨residue (valuation K A s) u, ?_⟩
  exact HenselianResidueLift.residue_lift s A s.val.toRingHom x

variable [FiniteDimensional K L] [IsGalois K L]
variable (stable : ∀ g : L ≃ₐ[K] L, g ∈ A.decompositionSubgroup K)

include stable in
/-- No extra residues occur: a field element fixed by the field fixer has residue
fixed by the entire residue-field fixer, because residue automorphisms lift. -/
theorem residueMap_mem (x : ResidueField (valuation K A s)) :
    residueMap K A s x ∈ s := by
  suffices h : residueMap K A s x ∈ IntermediateField.fixedField s.fixingSubgroup by
    simpa only [IsGalois.fixedField_fixingSubgroup] using h
  rw [IntermediateField.mem_fixedField_iff]
  intro σ hσ
  obtain ⟨g, hg⟩ := residueAut_surjective K A stable σ
  have hgE : g ∈ (field K A s).fixingSubgroup := by
    rw [fixingSubgroup_eq K A stable s]
    change residueAut K A stable g ∈ s.fixingSubgroup
    rw [hg]; exact hσ
  obtain ⟨u, rfl⟩ := residue_surjective x
  let a := ValuationResidueEmbedding.inclusion A (field K A s).val.toRingHom u
  have ha : (HenselianGaloisResidue.decompositionMap K A stable g) • a = a := by
    apply Subtype.ext
    exact (IntermediateField.mem_fixingSubgroup_iff (field K A s) g).mp hgE u.val u.val.property
  change σ (residue A a) = residue A a
  rw [← hg, residueAut_apply, HenselianGaloisResidue.residueAction_residue, ha]

include stable in
/-- Exact image of the canonical residue embedding. -/
theorem residueMap_range : Set.range (residueMap K A s) = (s : Set (ResidueField A)) := by
  ext x
  constructor
  · rintro ⟨y, rfl⟩; exact residueMap_mem K A s stable y
  · intro hx; exact residueMap_contains K A s ⟨x, hx⟩

/-- The canonical residue map, corestricted to the full target subfield. -/
def toSubfield : ResidueField (valuation K A s) →+* s where
  toFun x := ⟨residueMap K A s x, residueMap_mem K A s stable x⟩
  map_zero' := Subtype.ext (map_zero _)
  map_one' := Subtype.ext (map_one _)
  map_mul' x y := Subtype.ext (map_mul _ x y)
  map_add' x y := Subtype.ext (map_add _ x y)

/-- An actual residue-field isomorphism, preserving the ambient residue embedding. -/
def residueEquiv : ResidueField (valuation K A s) ≃+* s :=
  RingEquiv.ofBijective (toSubfield K A s stable) ⟨(toSubfield K A s stable).injective, by
    intro x
    obtain ⟨y, hy⟩ := residueMap_contains K A s x
    exact ⟨y, Subtype.ext hy⟩⟩

@[simp] theorem residueEquiv_val (x : ResidueField (valuation K A s)) :
    (residueEquiv K A s stable x : ResidueField A) = residueMap K A s x := rfl

include stable in
theorem residue_card : Nat.card (ResidueField (valuation K A s)) = Nat.card s :=
  Nat.card_congr (residueEquiv K A s stable).toEquiv

/-- The base residue map is also induced by literal restriction of valuations. -/
def baseResidueMap : BaseResidue K A →+* ResidueField (valuation K A s) :=
  ValuationResidueEmbedding.residueMap (valuation K A s) (algebraMap K (field K A s))

omit [FiniteDimensional K L] [IsGalois K L] in
@[simp] theorem base_composition (x : BaseResidue K A) :
    residueMap K A s (baseResidueMap K A s x) =
      ValuationResidueEmbedding.residueMap A (algebraMap K L) x := by
  obtain ⟨x, rfl⟩ := residue_surjective x
  rfl

instance actualBaseAlgebra : Algebra (BaseResidue K A) (ResidueField (valuation K A s)) :=
  (baseResidueMap K A s).toAlgebra

/-- Full residue identification with its actual base-field structure. -/
def residueAlgEquiv : ResidueField (valuation K A s) ≃ₐ[BaseResidue K A] s :=
  { residueEquiv K A s stable with
    commutes' := fun x => by
      apply Subtype.ext
      change residueMap K A s (baseResidueMap K A s x) =
        ValuationResidueEmbedding.residueMap A (algebraMap K L) x
      exact base_composition K A s x }

include stable in
/-- Both sides now use the actual base residue, not a smaller declared subfield. -/
theorem residue_degree :
    Module.finrank (BaseResidue K A) (ResidueField (valuation K A s)) =
      Module.finrank K (field K A s) := by
  rw [(residueAlgEquiv K A s stable).toLinearEquiv.finrank_eq]
  exact (degree K A stable s).symm

end PaperXI.LiftedFullResidue
