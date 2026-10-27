import KomorebiLSM.RationalFeasibility
import Mathlib.Logic.Encodable.Pi
import Mathlib.Data.Rat.Encodable
#synth DecidableEq ℚ
#synth DecidableEq (Fin 2 → ℚ)
#synth DecidableEq (Matrix (Fin 2) (Fin 2) ℚ)
#synth Decidable (∀ i : Fin 2, (0 : ℚ) ≤ i.val)
set_option pp.all true in
#check (fun (s m : ℕ) (A : Fin s → Matrix (Fin m) (Fin m) ℚ) => ∀ t i j, 0 ≤ A t i j)
example (s m : ℕ) (A : Fin s → Matrix (Fin m) (Fin m) ℚ) : Decidable (∀ t i j, 0 ≤ A t i j) := by infer_instance
example (s m : ℕ) (A : Fin s → Matrix (Fin m) (Fin m) ℚ) : Decidable (∀ t i j, (0 : ℚ) ≤ A t i j) := by infer_instance
