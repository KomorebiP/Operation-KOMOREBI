import Mathlib.LinearAlgebra.Quotient.Defs
import Mathlib.Tactic.Abel
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
The ordinary additive cochain identities and affine linear algebra underlying
the reader's first-stage obstruction. No Galois cohomology, global arithmetic
primitive, finite-S duality, Frey representation or Beal theorem is encoded.
-/

namespace KomorebiBeal.ReaderAffine

section Cochains

variable {G K : Type*} [Monoid G] [AddCommGroup K]

/-- The inhomogeneous differential for a trivial additive coefficient action. -/
def differential (p : G → K) (g h : G) : K := p g + p h - p (g * h)

theorem differential_add (p q : G → K) (g h : G) :
    differential (fun x => p x + q x) g h =
      differential p g h + differential q g h := by
  simp only [differential]
  abel

theorem differential_sub (p q : G → K) (g h : G) :
    differential (fun x => p x - q x) g h =
      differential p g h - differential q g h := by
  simp only [differential]
  abel

theorem same_primitive_difference_additive (p q : G → K)
    (same : ∀ g h, differential p g h = differential q g h) :
    ∀ g h, (p (g * h) - q (g * h)) = (p g - q g) + (p h - q h) := by
  intro g h
  have hz : differential (fun x => p x - q x) g h = 0 := by
    rw [differential_sub, same, sub_self]
  exact (sub_eq_zero.mp hz).symm

theorem add_character_preserves_differential (p z : G → K)
    (additive : ∀ g h, z (g * h) = z g + z h) :
    ∀ g h, differential (fun x => p x + z x) g h = differential p g h := by
  intro g h
  rw [differential_add]
  simp [differential, additive]

end Cochains

section FixedPrimitive

variable {G F : Type*} [Monoid G] [Field F]

def fixedPrimitive (chi : G →* Fˣ) (alpha : G → F) (lambda : F) (g : G) : F :=
  lambda * (chi g : F)⁻¹ * alpha g

def fixedBeta (chi : G →* Fˣ) (lambda : F) (g : G) : F :=
  ((chi g : F)⁻¹ - 1) * lambda

theorem fixed_primitive_differential (chi : G →* Fˣ) (alpha : G → F)
    (lambda : F)
    (cocycle : ∀ g h, alpha (g * h) = alpha g + (chi g : F) * alpha h)
    (g h : G) :
    differential (fixedPrimitive chi alpha lambda) g h =
      -alpha g * (chi g : F)⁻¹ * fixedBeta chi lambda h := by
  simp only [differential, fixedPrimitive, fixedBeta, cocycle, map_mul, Units.val_mul]
  field_simp
  ring

theorem fixed_primitive_trace (chi : G →* Fˣ) (alpha : G → F)
    (lambda : F) (g : G) :
    ((chi g : F) - 1) * fixedPrimitive chi alpha lambda g +
      alpha g * fixedBeta chi lambda g = 0 := by
  simp only [fixedPrimitive, fixedBeta]
  field_simp
  ring

end FixedPrimitive

section Affine

variable {R V W U : Type*} [CommRing R]
variable [AddCommGroup V] [Module R V] [AddCommGroup W] [Module R W]
variable [AddCommGroup U] [Module R U]

theorem solvability_translation (A : V →ₗ[R] W) (t : W) (z0 : V) :
    (∃ z, A z = t) ↔ ∃ z, A z = t - A z0 := by
  constructor
  · rintro ⟨z, hz⟩
    exact ⟨z - z0, by simp [hz]⟩
  · rintro ⟨z, hz⟩
    exact ⟨z + z0, by simp [hz]⟩

theorem cokernel_origin_invariance (A : V →ₗ[R] W) (t : W) (z0 : V) :
    (Submodule.Quotient.mk (t - A z0) : W ⧸ LinearMap.range A) =
      Submodule.Quotient.mk t := by
  rw [Submodule.Quotient.mk_sub]
  have zero : (Submodule.Quotient.mk (A z0) : W ⧸ LinearMap.range A) = 0 := by
    exact (Submodule.Quotient.mk_eq_zero (LinearMap.range A)).mpr ⟨z0, rfl⟩
  rw [zero, sub_zero]

theorem null_test_necessary (A : V →ₗ[R] W) (N : W →ₗ[R] U)
    (annihilate : ∀ z, N (A z) = 0) (t : W)
    (solvable : ∃ z, A z = t) : N t = 0 := by
  obtain ⟨z, hz⟩ := solvable
  rw [← hz]
  exact annihilate z

/-- Completeness is an explicit hypothesis. Merely having N A = 0 is weaker. -/
theorem complete_null_test (A : V →ₗ[R] W) (N : W →ₗ[R] U)
    (complete : LinearMap.ker N = LinearMap.range A) (t : W) :
    (∃ z, A z = t) ↔ N t = 0 := by
  change t ∈ LinearMap.range A ↔ t ∈ LinearMap.ker N
  rw [complete]

theorem fiber_is_kernel_translate (A : V →ₗ[R] W) (t : W) (zref z : V)
    (reference : A zref = t) :
    A z = t ↔ z - zref ∈ LinearMap.ker A := by
  change A z = t ↔ A (z - zref) = 0
  rw [map_sub, reference, sub_eq_zero]

end Affine

end KomorebiBeal.ReaderAffine

#print axioms KomorebiBeal.ReaderAffine.differential_add
#print axioms KomorebiBeal.ReaderAffine.differential_sub
#print axioms KomorebiBeal.ReaderAffine.same_primitive_difference_additive
#print axioms KomorebiBeal.ReaderAffine.add_character_preserves_differential
#print axioms KomorebiBeal.ReaderAffine.fixed_primitive_differential
#print axioms KomorebiBeal.ReaderAffine.fixed_primitive_trace
#print axioms KomorebiBeal.ReaderAffine.solvability_translation
#print axioms KomorebiBeal.ReaderAffine.cokernel_origin_invariance
#print axioms KomorebiBeal.ReaderAffine.null_test_necessary
#print axioms KomorebiBeal.ReaderAffine.complete_null_test
#print axioms KomorebiBeal.ReaderAffine.fiber_is_kernel_translate
