import FiniteAffineObstruction

noncomputable section
set_option autoImplicit false

namespace Komorebi.NativeAffine.Controls
open Komorebi.NativeAffine

/-- An invertible coefficient map has no obstruction. -/
theorem identity_unobstructed (p n : ℕ) (r : Fin n → ℤ) :
    obstruction p (LinearMap.id : (Fin n → ℤ) →ₗ[ℤ] (Fin n → ℤ)) r = 0 := by
  rw [obstruction_zero_iff_correction]
  refine ⟨-r, ?_⟩
  simp

/-- This obstruction can genuinely be nonzero. -/
theorem zero_map_residual_nonzero :
    obstruction 2 (0 : (Fin 1 → ℤ) →ₗ[ℤ] (Fin 1 → ℤ)) (fun _ => 1) ≠ 0 := by
  intro h
  obtain ⟨t, ht⟩ := (obstruction_zero_iff_correction 2
    (0 : (Fin 1 → ℤ) →ₗ[ℤ] (Fin 1 → ℤ)) (fun _ => 1)).mp h
  have h0 : (1 : ZMod 2) = 0 := by
    simpa [reduction] using congrFun ht (0 : Fin 1)
  exact one_ne_zero h0

/-- The singular constant system 0*x=-2 is satisfied modulo 2. -/
theorem singular_lower_solution :
    ∀ i : Fin 1, (2 : ℤ) ∣
      ((0 : (Fin 1 → ℤ) →ₗ[ℤ] (Fin 1 → ℤ)) 0 - (fun _ : Fin 1 => (-2 : ℤ))) i := by
  intro i
  exact dvd_refl 2

/-- That same actual lower solution has no solution modulo 4. -/
theorem singular_no_lift :
    ¬ ∃ y : Fin 1 → ℤ, ∀ i : Fin 1, (4 : ℤ) ∣
      ((0 : (Fin 1 → ℤ) →ₗ[ℤ] (Fin 1 → ℤ)) y - (fun _ : Fin 1 => (-2 : ℤ))) i := by
  rintro ⟨y, hy⟩
  have h := hy 0
  change (4 : ℤ) ∣ 2 at h
  exact (by decide : ¬ (4 : ℤ) ∣ 2) h

#print axioms identity_unobstructed
#print axioms zero_map_residual_nonzero
#print axioms singular_lower_solution
#print axioms singular_no_lift

end Komorebi.NativeAffine.Controls
