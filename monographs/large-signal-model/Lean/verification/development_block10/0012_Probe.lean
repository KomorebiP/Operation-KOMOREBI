import KomorebiLSM.RationalFeasibility
import Mathlib.Logic.Encodable.Pi
import Mathlib.Data.Rat.Encodable
#synth DecidableEq ℚ
#synth DecidableEq (Fin 2 → ℚ)
#synth DecidableEq (Matrix (Fin 2) (Fin 2) ℚ)
#synth Decidable (∀ i : Fin 2, (0 : ℚ) ≤ i.val)
