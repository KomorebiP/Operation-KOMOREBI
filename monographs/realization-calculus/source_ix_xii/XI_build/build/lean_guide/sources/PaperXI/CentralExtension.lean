import PaperXI.CocycleCommutator
import Mathlib.Tactic.Group

/-! An actual central extension and normalized coordinates on its middle group.
No characteristic, finiteness, or scalar-character assumption is used. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralExtension

/-- A short exact sequence whose distinguished kernel lies in the center. -/
structure Datum (Z H A : Type*) [CommGroup Z] [Group H] [CommGroup A] where
  i : Z →* H
  q : H →* A
  i_injective : Function.Injective i
  q_surjective : Function.Surjective q
  range_i_eq_ker_q : i.range = q.ker
  central : ∀ z h, i z * h = h * i z

variable {Z H A : Type*} [CommGroup Z] [Group H] [CommGroup A]
variable (D : Datum Z H A)

@[simp] theorem q_i (z : Z) : D.q (D.i z) = 1 := by
  have h : D.i z ∈ D.i.range := ⟨z, rfl⟩
  rw [D.range_i_eq_ker_q] at h
  exact h

/-- A chosen quotient section, normalized at the identity. -/
def sectionMap (a : A) : H := by
  classical
  exact if a = 1 then 1 else Classical.choose (D.q_surjective a)

@[simp] theorem section_one : sectionMap D 1 = 1 := by
  simp [sectionMap]

@[simp] theorem q_section (a : A) : D.q (sectionMap D a) = a := by
  classical
  by_cases ha : a = 1
  · simp [ha]
  · simpa [sectionMap, ha] using Classical.choose_spec (D.q_surjective a)

theorem exists_coordinate (h : H) :
    ∃ z : Z, D.i z = h * (sectionMap D (D.q h))⁻¹ := by
  have hk : h * (sectionMap D (D.q h))⁻¹ ∈ D.q.ker := by
    simp only [MonoidHom.mem_ker, map_mul, map_inv, q_section, mul_inv_cancel]
  rw [← D.range_i_eq_ker_q] at hk
  exact hk

/-- The unique central coordinate of a group element relative to the section. -/
def coordinate (h : H) : Z := Classical.choose (exists_coordinate D h)

theorem coordinate_spec (h : H) :
    D.i (coordinate D h) = h * (sectionMap D (D.q h))⁻¹ :=
  Classical.choose_spec (exists_coordinate D h)

/-- Every group element has its actual central-times-section normal form. -/
theorem normal_form (h : H) :
    h = D.i (coordinate D h) * sectionMap D (D.q h) := by
  rw [coordinate_spec, inv_mul_cancel_right]

theorem coordinate_eq_of_eq (h : H) (z : Z) (a : A)
    (heq : h = D.i z * sectionMap D a) : coordinate D h = z := by
  have hq : D.q h = a := by rw [heq, map_mul, q_i, q_section, one_mul]
  have hn := normal_form D h
  rw [hq] at hn
  exact D.i_injective (mul_right_cancel (hn.symm.trans heq))

@[simp] theorem coordinate_one : coordinate D 1 = 1 :=
  coordinate_eq_of_eq D 1 1 1 (by simp)

@[simp] theorem coordinate_section (a : A) : coordinate D (sectionMap D a) = 1 :=
  coordinate_eq_of_eq D (sectionMap D a) 1 a (by simp)

@[simp] theorem coordinate_i (z : Z) : coordinate D (D.i z) = z :=
  coordinate_eq_of_eq D (D.i z) z 1 (by simp)

/-- Both coordinates of the normal form are unique. -/
theorem normal_form_unique (h : H) (z : Z) (a : A) :
    h = D.i z * sectionMap D a ↔ coordinate D h = z ∧ D.q h = a := by
  constructor
  · intro heq
    exact ⟨coordinate_eq_of_eq D h z a heq, by rw [heq, map_mul, q_i, q_section, one_mul]⟩
  · rintro ⟨hz, ha⟩
    simpa only [hz, ha] using normal_form D h

end PaperXI.CentralExtension
