import PaperXI.OnePlusIntersection110
import Mathlib.RingTheory.Jacobson.Ideal

/-! Exact one-plus groups from actual radical ideals in the original order.
The order may be noncommutative. No arbitrary additive lattice is declared
to be a group or an ideal of the full field endomorphism algebra. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.RadicalOnePlus111
open PaperXI.OnePlusIntersection110

variable {R : Type*} [Ring R]

/-- A two-sided inverse follows from the left-Jacobson property alone.
No commutativity or desired invertibility premise is used. -/
theorem isUnit_of_sub_one_mem_jacobson (r : R)
    (hr : r - 1 ∈ Ideal.jacobson (⊥ : Ideal R)) : IsUnit r := by
  obtain ⟨s, hs⟩ := Ideal.exists_mul_sub_mem_of_sub_one_mem_jacobson r hr
  have hsr : s * r = 1 := by simpa only [Ideal.mem_bot, sub_eq_zero] using hs
  have hsrad : s - 1 ∈ Ideal.jacobson (⊥ : Ideal R) := by
    have h := (Ideal.jacobson (⊥ : Ideal R)).neg_mem
      ((Ideal.jacobson (⊥ : Ideal R)).mul_mem_left s hr)
    have he : -(s * (r - 1)) = s - 1 := by rw [mul_sub, mul_one, hsr]; abel
    rwa [he] at h
  obtain ⟨t, ht⟩ := Ideal.exists_mul_sub_mem_of_sub_one_mem_jacobson s hsrad
  have hts : t * s = 1 := by simpa only [Ideal.mem_bot, sub_eq_zero] using ht
  have htr : t = r := by
    calc t = t * (s * r) := by rw [hsr, mul_one]
         _ = (t * s) * r := (mul_assoc _ _ _).symm
         _ = r := by rw [hts, one_mul]
  exact ⟨⟨r, s, by simpa only [htr] using hts, hsr⟩, rfl⟩

/-- The actual subgroup of units whose offset belongs to I. -/
def onePlus (I : Ideal R) : Subgroup Rˣ := idealUnits I

theorem onePlus_offsets (I : Ideal R) :
    ∀ g : onePlus I, ((g : Rˣ) : R) - 1 ∈ I.toAddSubgroup := fun g => g.property

/-- Every actual ideal element has its literal unit 1+x in the subgroup. -/
theorem onePlus_surjective (I : Ideal R)
    (hI : I ≤ Ideal.jacobson (⊥ : Ideal R)) :
    ∀ x : I.toAddSubgroup, ∃ g : onePlus I, ((g : Rˣ) : R) = 1 + (x : R) := by
  intro x
  have hu : IsUnit (1 + (x : R)) :=
    isUnit_of_sub_one_mem_jacobson _ (by simpa using hI x.property)
  obtain ⟨g, hg⟩ := hu
  refine ⟨⟨g, ?_⟩, hg⟩
  change (g : R) - 1 ∈ I
  rw [hg]
  simp

/-- The ideal itself is the offset carrier, via the actual unit-valued map. -/
def offsetEquiv (I : Ideal R) (hI : I ≤ Ideal.jacobson (⊥ : Ideal R)) :
    onePlus I ≃ I.toAddSubgroup :=
  PaperXI.OnePlusIndex110.offsetEquiv I.toAddSubgroup (onePlus I)
    (onePlus_offsets I) (onePlus_surjective I hI)

end PaperXI.RadicalOnePlus111
