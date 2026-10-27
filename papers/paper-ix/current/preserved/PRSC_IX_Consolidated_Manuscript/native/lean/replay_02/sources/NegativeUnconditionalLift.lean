import FiniteAffineObstruction
open Komorebi.NativeAffine
example : obstruction 2 (0 : (Fin 1 → ℤ) →ₗ[ℤ] (Fin 1 → ℤ)) (fun _ => 1) = 0 := by
  rw [obstruction_zero_iff_correction]
  exact ⟨0, rfl⟩
