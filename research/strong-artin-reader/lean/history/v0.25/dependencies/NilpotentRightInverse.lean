import Mathlib.RingTheory.Nilpotent.Basic
import Mathlib.LinearAlgebra.Projection

/-!
# Lifting a right inverse across a nilpotent error

An approximate right inverse whose error is nilpotent can be corrected exactly.
The proof uses the unit `1 + error` in the endomorphism ring.  A second theorem
specializes this to an error divisible by a nilpotent scalar.
-/

namespace Komorebi.StrongArtin.NilpotentRightInverse

noncomputable section

variable {R U W : Type*} [CommRing R]
  [AddCommGroup U] [Module R U]
  [AddCommGroup W] [Module R W]

/-- A nilpotent scalar times an endomorphism is nilpotent. -/
theorem isNilpotent_smul_end
    (pi : R) (E : Module.End R W) (hpi : IsNilpotent pi) :
    IsNilpotent (pi • E) := by
  obtain ⟨n, hn⟩ := hpi
  refine ⟨n, ?_⟩
  rw [smul_pow, hn, zero_smul]

/-- If the error of an approximate right inverse is nilpotent, the right inverse
can be corrected exactly in the endomorphism ring. -/
theorem exists_exact_rightInverse_of_nilpotent_error
    (J : U →ₗ[R] W) (R₀ : W →ₗ[R] U)
    (hnil : IsNilpotent (J.comp R₀ - LinearMap.id)) :
    ∃ R₁ : W →ₗ[R] U, J.comp R₁ = LinearMap.id := by
  have hunit : IsUnit (J.comp R₀ : Module.End R W) := by
    have h := hnil.isUnit_add_one
    change IsUnit ((J.comp R₀ - LinearMap.id) + LinearMap.id) at h
    simpa only [sub_add_cancel] using h
  let inv : Module.End R W := ↑hunit.unit⁻¹
  refine ⟨R₀.comp inv, ?_⟩
  calc
    J.comp (R₀.comp inv) = (J.comp R₀) * inv := by rfl
    _ = 1 := hunit.mul_val_inv
    _ = LinearMap.id := by rfl

/-- An approximate right inverse with error `pi • E` is exact whenever `pi` is
nilpotent. -/
theorem exists_exact_rightInverse_of_scalar_nilpotent_error
    (J : U →ₗ[R] W) (R₀ : W →ₗ[R] U)
    (pi : R) (E : Module.End R W)
    (happrox : J.comp R₀ = LinearMap.id + pi • E)
    (hpi : IsNilpotent pi) :
    ∃ R₁ : W →ₗ[R] U, J.comp R₁ = LinearMap.id := by
  apply exists_exact_rightInverse_of_nilpotent_error J R₀
  have herror : J.comp R₀ - LinearMap.id = pi • E := by
    rw [happrox]
    exact add_sub_cancel_left LinearMap.id (pi • E)
  rw [herror]
  exact isNilpotent_smul_end pi E hpi

/-- The corrected right inverse proves surjectivity. -/
theorem surjective_of_scalar_nilpotent_approx_rightInverse
    (J : U →ₗ[R] W) (R₀ : W →ₗ[R] U)
    (pi : R) (E : Module.End R W)
    (happrox : J.comp R₀ = LinearMap.id + pi • E)
    (hpi : IsNilpotent pi) :
    Function.Surjective J := by
  obtain ⟨R₁, hR₁⟩ :=
    exists_exact_rightInverse_of_scalar_nilpotent_error J R₀ pi E happrox hpi
  exact (show Function.RightInverse R₁ J from fun w => by
    have := LinearMap.congr_fun hR₁ w
    simpa using this).surjective

end

end Komorebi.StrongArtin.NilpotentRightInverse

#print axioms Komorebi.StrongArtin.NilpotentRightInverse.exists_exact_rightInverse_of_nilpotent_error
#print axioms Komorebi.StrongArtin.NilpotentRightInverse.exists_exact_rightInverse_of_scalar_nilpotent_error
#print axioms Komorebi.StrongArtin.NilpotentRightInverse.surjective_of_scalar_nilpotent_approx_rightInverse
