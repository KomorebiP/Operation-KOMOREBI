module
public import PolynomialDeformationControls
@[expose] public section
open Komorebi.PolynomialDeformationControls MvPolynomial

-- Invalid: the checked bijective Jacobian at one does not make X²−1 globally injective.
-- The positive control proves two actual p-adic roots in different residue balls.
example : ∀ a b : Fin 1 → ℤ_[3],
    (∀ i, eval₂ (Int.castRingHom ℤ_[3]) a (squareMinusOne i) = 0) →
    (∀ i, eval₂ (Int.castRingHom ℤ_[3]) b (squareMinusOne i) = 0) → a = b := by
  exact square_minus_one_not_global_unique
