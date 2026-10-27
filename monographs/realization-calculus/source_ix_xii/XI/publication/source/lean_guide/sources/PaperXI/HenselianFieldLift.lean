import PaperXI.HenselianResidueLift
import Mathlib.RingTheory.Valuation.RamificationGroup
import Mathlib.FieldTheory.Galois.Basic
import Mathlib.FieldTheory.IntermediateField.Adjoin.Basic

/-! Construct an actual finite intermediate field from finite residue-field
Hensel lifts. The fixed-field statement concerns literal automorphisms of L. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HenselianFieldLift
open IsLocalRing
variable (k K : Type*) {L : Type*} [Field k] [Fintype k] [Field K] [Field L] [Algebra K L]
variable (A : ValuationSubring L) [HenselianLocalRing A]
variable (e : k →+* ResidueField A)

def element (x : k) : L := (HenselianResidueLift.lift k A e x : A)

/-- The lifted residue generators form an actual subfield of L over K. -/
def field : IntermediateField K L := IntermediateField.adjoin K (Set.range (element k A e))

theorem element_mem (x : k) : element k A e x ∈ field k K A e :=
  IntermediateField.subset_adjoin K _ ⟨x,rfl⟩

theorem element_integral (x : k) : IsIntegral K (element k A e x) := by
  refine ⟨Polynomial.X ^ Fintype.card k - Polynomial.X, HenselianResidueLift.poly_monic k K, ?_⟩
  simp only [Polynomial.eval₂_sub, Polynomial.eval₂_pow, Polynomial.eval₂_X]
  apply sub_eq_zero.mpr
  exact congrArg (fun z : A => (z : L)) (HenselianResidueLift.lift_pow k A e x)

/-- Finiteness is derived from a finite set of integral generators. -/
instance finiteDimensional : FiniteDimensional K (field k K A e) := by
  have : Finite (Set.range (element k A e)) := Set.finite_range _
  apply IntermediateField.finiteDimensional_adjoin
  rintro x ⟨a, rfl⟩
  exact element_integral k K A e a

/-- Actual residue class of every generator. -/
theorem residue_element (x : k) :
    residue A (HenselianResidueLift.lift k A e x) = e x :=
  HenselianResidueLift.residue_lift k A e x

/-- The true pointwise field-fixing subgroup inside the valuation decomposition group. -/
def fixing : Subgroup (A.decompositionSubgroup K) :=
  (field k K A e).fixingSubgroup.comap (A.decompositionSubgroup K).subtype

/-- Pointwise field fixing is tested on the actual lifted generators. -/
theorem mem_fixing_iff (g : A.decompositionSubgroup K) :
    g ∈ fixing k K A e ↔ ∀ x : k, g.val (element k A e x) = element k A e x := by
  change g.val ∈ (field k K A e).fixingSubgroup ↔ _
  rw [IntermediateField.mem_fixingSubgroup_iff]
  constructor
  · intro h x; exact h _ (element_mem k K A e x)
  · intro h x hx
    apply IntermediateField.adjoin_induction (F := K) (p := fun x _ => g.val x = x)
      (fun x hx => ?_) (fun x => g.val.commutes x)
      (fun x y _ _ hx hy => by rw [map_add, hx, hy])
      (fun x _ hx => by rw [map_inv₀, hx])
      (fun x y _ _ hx hy => by rw [map_mul, hx, hy]) hx
    obtain ⟨y, rfl⟩ := hx
    exact h y

/-- Hensel uniqueness identifies the field fixer with the literal residue-field fixer. -/
theorem fixing_iff_residue (g : A.decompositionSubgroup K) :
    g ∈ fixing k K A e ↔ ∀ x : k, g • e x = e x := by
  rw [mem_fixing_iff]
  constructor
  · intro h x
    have hh : g • HenselianResidueLift.lift k A e x = HenselianResidueLift.lift k A e x := by
      apply Subtype.ext
      exact h x
    have := congrArg (residue A) hh
    simpa only [ResidueField.residue_smul, HenselianResidueLift.residue_lift] using this
  · intro h x
    have hh := (HenselianResidueLift.automorphism_fix_iff k A e
      (MulSemiringAction.toRingAut (A.decompositionSubgroup K) A g) x).mpr (by
        change residue A (g • HenselianResidueLift.lift k A e x) = e x
        rw [ResidueField.residue_smul, HenselianResidueLift.residue_lift, h])
    exact congrArg (fun z : A => (z : L)) hh

/-- All actual inertia automorphisms fix the generated field, not just its residues. -/
theorem inertia_le_fixing : A.inertiaSubgroup K ≤ fixing k K A e := by
  intro g hg
  apply (fixing_iff_residue k K A e g).mpr
  intro x
  change MulSemiringAction.toRingAut (A.decompositionSubgroup K) (ResidueField A) g = 1 at hg
  exact RingEquiv.congr_fun hg (e x)

/-- No finite-dimensionality of L/K is required for this containment. -/
theorem contained_in_inertia_fixed : field k K A e ≤
    IntermediateField.fixedField ((A.inertiaSubgroup K).map (A.decompositionSubgroup K).subtype) := by
  apply (IntermediateField.le_iff_le _ _).mpr
  rintro g ⟨h, hh, rfl⟩
  exact inertia_le_fixing k K A e hh

end PaperXI.HenselianFieldLift
