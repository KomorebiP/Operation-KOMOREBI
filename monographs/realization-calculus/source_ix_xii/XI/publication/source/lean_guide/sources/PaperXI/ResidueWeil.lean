import PaperXI.NormalInertia
import Mathlib.RingTheory.Valuation.RamificationGroup
import Mathlib.GroupTheory.QuotientGroup.Basic

/-! A pullback of an actual residue-field action along the integer powers of a
chosen residue automorphism. No equivalence with the absolute local Weil group
is postulated. The inertia identification below is with Mathlib's valuation
inertia subgroup, not with an independently named abstract kernel. -/
set_option autoImplicit false
noncomputable section
open scoped Classical

namespace PaperXI.ResidueWeil

variable {D C : Type*} [Group D] [Group C]

/-- The infinite degree direction is retained, even for finite residue data. -/
def subgroup (r : D →* C) (F : C) : Subgroup (D × Multiplicative ℤ) where
  carrier := {x | r x.1 = F ^ Multiplicative.toAdd x.2}
  one_mem' := by simp
  mul_mem' := by
    intro a b ha hb
    change r (a.1 * b.1) = F ^ (Multiplicative.toAdd a.2 + Multiplicative.toAdd b.2)
    rw [map_mul, ha, hb, zpow_add]
  inv_mem' := by
    intro a ha
    change r a.1⁻¹ = F ^ (-Multiplicative.toAdd a.2)
    rw [map_inv, ha, zpow_neg]

abbrev Pullback (r : D →* C) (F : C) := subgroup r F

def projection (r : D →* C) (F : C) : Pullback r F →* D :=
  (MonoidHom.fst D (Multiplicative ℤ)).comp (subgroup r F).subtype

def degree (r : D →* C) (F : C) : Pullback r F →* Multiplicative ℤ :=
  (MonoidHom.snd D (Multiplicative ℤ)).comp (subgroup r F).subtype

@[simp] theorem projection_apply (r : D →* C) (F : C) (w : Pullback r F) :
    projection r F w = w.val.1 := rfl

@[simp] theorem degree_apply (r : D →* C) (F : C) (w : Pullback r F) :
    degree r F w = w.val.2 := rfl

/-- The degree kernel is precisely residue inertia, with inverse g ↦ (g,0). -/
def inertiaEquiv (r : D →* C) (F : C) : (degree r F).ker ≃* r.ker where
  toFun w := ⟨w.val.val.1, by
    change r w.val.val.1 = 1
    have h : r w.val.val.1 = F ^ Multiplicative.toAdd w.val.val.2 := w.val.property
    have hz : w.val.val.2 = 1 := w.property
    rw [hz] at h
    simpa using h⟩
  invFun g := ⟨⟨(g.val, 1), by
    change r g.val = F ^ (0 : ℤ)
    simpa only [zpow_zero] using (show r g.val = 1 from g.property)⟩, rfl⟩
  left_inv w := by
    apply Subtype.ext
    apply Subtype.ext
    apply Prod.ext
    · rfl
    · exact w.property.symm
  right_inv g := rfl
  map_mul' _ _ := rfl

/-- The quotient needs only to embed into the abelian degree group. -/
instance degreeQuotientCommutative (r : D →* C) (F : C) :
    IsMulCommutative (Pullback r F ⧸ (degree r F).ker) := by
  apply IsMulCommutative.of_comm
  intro a b
  apply QuotientGroup.kerLift_injective (degree r F)
  simp only [map_mul, mul_comm]

/-- A degree-one lift exists exactly when the selected residue automorphism lifts. -/
theorem exists_degree_one_iff (r : D →* C) (F : C) :
    (∃ w : Pullback r F, degree r F w = Multiplicative.ofAdd (1 : ℤ)) ↔
    F ∈ r.range := by
  constructor
  · rintro ⟨w, hw⟩
    refine ⟨projection r F w, ?_⟩
    have hh : r w.val.1 = F ^ Multiplicative.toAdd w.val.2 := w.property
    change w.val.2 = Multiplicative.ofAdd (1 : ℤ) at hw
    simpa [hw] using hh
  · rintro ⟨g, hg⟩
    refine ⟨⟨(g, Multiplicative.ofAdd (1 : ℤ)), ?_⟩, rfl⟩
    change r g = F ^ (1 : ℤ)
    simpa using hg

section Valuation
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]

abbrev residueAction (A : ValuationSubring L) :
    A.decompositionSubgroup K →* RingAut (IsLocalRing.ResidueField A) :=
  MulSemiringAction.toRingAut (A.decompositionSubgroup K) (IsLocalRing.ResidueField A)

abbrev valuationGroup (A : ValuationSubring L) (F : RingAut (IsLocalRing.ResidueField A)) :=
  Pullback (residueAction K A) F

/-- Specialization to the actual valuation-ring inertia subgroup. -/
def valuationInertiaEquiv (A : ValuationSubring L)
    (F : RingAut (IsLocalRing.ResidueField A)) :
    (degree (residueAction K A) F).ker ≃* A.inertiaSubgroup K :=
  inertiaEquiv (residueAction K A) F

variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]

/-- No cyclic finite-inertia presentation is needed for this vanishing result. -/
theorem valuation_invariants_eq_bot (A : ValuationSubring L)
    (F : RingAut (IsLocalRing.ResidueField A))
    (ρ : Representation ℂ (valuationGroup K A F) V) [Representation.IsIrreducible ρ]
    (hdim : 1 < Module.finrank ℂ V) :
    Representation.invariants (ρ.comp (degree (residueAction K A) F).ker.subtype) = ⊥ :=
  NormalInertia.fixed_eq_bot_of_dimension_gt_one ρ (degree (residueAction K A) F).ker hdim

end Valuation
end PaperXI.ResidueWeil
