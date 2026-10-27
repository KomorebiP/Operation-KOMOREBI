import PaperXI.HenselianGaloisResidue
import Mathlib.FieldTheory.Finite.GaloisField

/-! Exact degree of the Hensel-generated field in a finite Galois ambient extension.
The base is the full residue field of the restricted valuation. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LiftedResidueDegree
open IsLocalRing
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L)

abbrev BaseResidue := ResidueField (A.comap (algebraMap K L))

instance baseResidueAlgebra : Algebra (BaseResidue K A) (ResidueField A) :=
  (ValuationResidueEmbedding.residueMap A (algebraMap K L)).toAlgebra

variable (stable : ∀ g : L ≃ₐ[K] L, g ∈ A.decompositionSubgroup K)

def residueAut : (L ≃ₐ[K] L) →* (ResidueField A ≃ₐ[BaseResidue K A] ResidueField A) where
  toFun g := { (HenselianGaloisResidue.residueAction K A stable g) with
    commutes' := HenselianGaloisResidue.fixes_base K A stable g }
  map_one' := by ext x; exact RingEquiv.congr_fun (map_one (HenselianGaloisResidue.residueAction K A stable)) x
  map_mul' g h := by ext x; exact RingEquiv.congr_fun (map_mul (HenselianGaloisResidue.residueAction K A stable) g h) x

@[simp] theorem residueAut_apply (g : L ≃ₐ[K] L) (x : ResidueField A) :
    residueAut K A stable g x = HenselianGaloisResidue.residueAction K A stable g x := rfl

variable [FiniteDimensional K L] [IsGalois K L]
variable [HenselianLocalRing A] [Fintype (ResidueField A)]

theorem residueAut_surjective : Function.Surjective (residueAut K A stable) := by
  intro σ
  obtain ⟨g, hg⟩ := HenselianGaloisResidue.lift_automorphism K A stable σ.toRingEquiv σ.commutes
  exact ⟨g, AlgEquiv.ext (fun x => RingEquiv.congr_fun hg x)⟩

variable (s : IntermediateField (BaseResidue K A) (ResidueField A))
local instance subfieldFintype : Fintype s := Fintype.ofFinite s

/-- All lifts of the literal residue subfield s, adjoined to K. -/
def field : IntermediateField K L :=
  HenselianFieldLift.field s K A s.val.toRingHom

omit [FiniteDimensional K L] [IsGalois K L] in
/-- The actual fixing group is the preimage of the residue fixing group. -/
theorem fixingSubgroup_eq :
    (field K A s).fixingSubgroup = s.fixingSubgroup.comap (residueAut K A stable) := by
  ext g
  have h := HenselianFieldLift.fixing_iff_residue s K A s.val.toRingHom
    (HenselianGaloisResidue.decompositionMap K A stable g)
  change g ∈ (field K A s).fixingSubgroup ↔
    residueAut K A stable g ∈ s.fixingSubgroup
  change (g ∈ (field K A s).fixingSubgroup) ↔
    (∀ x : s, residueAut K A stable g x = x) at h
  constructor
  · intro hg
    rw [IntermediateField.mem_fixingSubgroup_iff]
    intro x hx
    exact h.mp hg ⟨x, hx⟩
  · intro hg
    apply h.mpr
    intro x
    exact (IntermediateField.mem_fixingSubgroup_iff s _).mp hg x x.property

include stable in
/-- The field degree is derived, rather than supplied as a certificate. -/
theorem degree : Module.finrank K (field K A s) = Module.finrank (BaseResidue K A) s := by
  rw [IntermediateField.finrank_eq_fixingSubgroup_index,
    fixingSubgroup_eq K A stable s,
    Subgroup.index_comap_of_surjective _ (residueAut_surjective K A stable),
    ← IntermediateField.finrank_eq_fixingSubgroup_index]

include stable in
/-- The generated field is Galois, since a subextension of finite fields is normal. -/
theorem galois : IsGalois K (field K A s) := by
  have hn : (field K A s).fixingSubgroup.Normal := by
    rw [fixingSubgroup_eq K A stable s]
    infer_instance
  have := IsGalois.of_fixedField_normal_subgroup (field K A s).fixingSubgroup
  rwa [IsGalois.fixedField_fixingSubgroup] at this

end PaperXI.LiftedResidueDegree
