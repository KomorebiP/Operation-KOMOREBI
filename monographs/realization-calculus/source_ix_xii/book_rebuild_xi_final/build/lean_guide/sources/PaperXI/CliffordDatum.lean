import PaperXI.QuotientRepresentation
import Mathlib.Analysis.Complex.Basic

/-! Actual restriction, conjugation and normalized quotient representatives
for the Clifford multiplicity construction. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordDatum

variable {G W X : Type*} [Group G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]

/-- Restriction to the actual subgroup. -/
abbrev restriction (N : Subgroup G) (π : Representation ℂ G X) : Representation ℂ N X :=
  π.comp N.subtype

/-- Ambient conjugation, with membership supplied by normality. -/
def conjugation (N : Subgroup G) [N.Normal] (g : G) : N →* N where
  toFun n := ⟨g * n * g⁻¹, Subgroup.Normal.conj_mem (inferInstance : N.Normal) (n : G) n.property g⟩
  map_one' := by apply Subtype.ext; simp
  map_mul' n m := by apply Subtype.ext; simp [mul_assoc]

@[simp] theorem conjugation_coe (N : Subgroup G) [N.Normal] (g : G) (n : N) :
    (conjugation N g n : G) = g * n * g⁻¹ := rfl

@[simp] theorem conjugation_one (N : Subgroup G) [N.Normal] (n : N) :
    conjugation N 1 n = n := by apply Subtype.ext; simp

@[simp] theorem conjugation_mul (N : Subgroup G) [N.Normal] (g h : G) (n : N) :
    conjugation N (g * h) n = conjugation N g (conjugation N h n) := by
  apply Subtype.ext
  simp [mul_assoc]

@[simp] theorem conjugation_inv_cancel (N : Subgroup G) [N.Normal] (g : G) (n : N) :
    conjugation N g (conjugation N g⁻¹ n) = n := by
  rw [← conjugation_mul]
  simp

/-- The representation obtained by the actual ambient conjugation. -/
abbrev conjugate (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W) (g : G) :=
  ρ.comp (conjugation N g)

/-- The source invariance hypothesis is equivalence of actual representations. -/
def Invariant (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W) : Prop :=
  ∀ g : G, Nonempty (Representation.Equiv ρ (conjugate N ρ g))

/-- A normalized sectionMap of the actual quotient map. -/
def sectionMap (N : Subgroup G) [N.Normal] (a : G ⧸ N) : G :=
  by
  classical
  exact if a = 1 then 1 else Classical.choose (QuotientGroup.mk_surjective a)

@[simp] theorem section_one (N : Subgroup G) [N.Normal] : sectionMap N 1 = 1 := by
  simp [sectionMap]

@[simp] theorem quotient_section (N : Subgroup G) [N.Normal] (a : G ⧸ N) :
    QuotientGroup.mk' N (sectionMap N a) = a := by
  classical
  by_cases ha : a = 1
  · subst a; simp
  · simpa [sectionMap, ha] using (Classical.choose_spec (QuotientGroup.mk_surjective a))

/-- The actual subgroup-valued multiplication defect of the chosen sectionMap. -/
def defect (N : Subgroup G) [N.Normal] (a b : G ⧸ N) : N :=
  ⟨sectionMap N a * sectionMap N b * (sectionMap N (a * b))⁻¹, by
    apply (QuotientGroup.eq_one_iff _).mp
    change QuotientGroup.mk' N (_ * _ * _⁻¹) = 1
    rw [map_mul, map_mul, map_inv, quotient_section, quotient_section, quotient_section]
    exact mul_inv_cancel _⟩

@[simp] theorem defect_coe (N : Subgroup G) [N.Normal] (a b : G ⧸ N) :
    (defect N a b : G) = sectionMap N a * sectionMap N b * (sectionMap N (a * b))⁻¹ := rfl

theorem section_mul (N : Subgroup G) [N.Normal] (a b : G ⧸ N) :
    sectionMap N a * sectionMap N b = (defect N a b : G) * sectionMap N (a * b) := by
  simp [mul_assoc]

@[simp] theorem defect_one_left (N : Subgroup G) [N.Normal] (a : G ⧸ N) :
    defect N 1 a = 1 := by apply Subtype.ext; simp

@[simp] theorem defect_one_right (N : Subgroup G) [N.Normal] (a : G ⧸ N) :
    defect N a 1 = 1 := by apply Subtype.ext; simp

/-- The subgroup part of an arbitrary representative's normal form. -/
def coordinate (N : Subgroup G) [N.Normal] (g : G) : N :=
  ⟨g * (sectionMap N (QuotientGroup.mk' N g))⁻¹, by
    apply (QuotientGroup.eq_one_iff _).mp
    change QuotientGroup.mk' N (g * (sectionMap N (QuotientGroup.mk' N g))⁻¹) = 1
    rw [map_mul, map_inv, quotient_section]
    exact mul_inv_cancel _⟩

theorem normal_form (N : Subgroup G) [N.Normal] (g : G) :
    g = (coordinate N g : G) * sectionMap N (QuotientGroup.mk' N g) := by
  simp [coordinate, mul_assoc]

/-- An invertible intertwiner chosen from invariance, normalized at the identity. -/
def sectionIntertwiner (N : Subgroup G) [N.Normal] (ρ : Representation ℂ N W)
    (hρ : Invariant N ρ) (a : G ⧸ N) :
    Representation.Equiv ρ (conjugate N ρ (sectionMap N a)) := by
  classical
  by_cases ha : a = 1
  · subst a
    exact Representation.Equiv.mk (LinearEquiv.refl ℂ W) (by intro n; simp [conjugate])
  · exact Classical.choice (hρ (sectionMap N a))

@[simp] theorem sectionIntertwiner_one (N : Subgroup G) [N.Normal]
    (ρ : Representation ℂ N W) (hρ : Invariant N ρ) (w : W) :
    sectionIntertwiner N ρ hρ 1 w = w := by
  simp only [sectionIntertwiner, dite_true]
  rfl

end PaperXI.CliffordDatum
