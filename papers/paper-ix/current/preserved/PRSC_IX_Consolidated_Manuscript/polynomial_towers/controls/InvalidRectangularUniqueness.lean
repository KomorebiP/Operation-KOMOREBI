module
public import PolynomialTowerControls
@[expose] public section
open Komorebi.PolynomialTowerControls MvPolynomial

-- Invalid: surjectivity for the one-by-two projection Jacobian does not eliminate its free coordinate.
example : ∀ a b : Fin 2 → ℤ_[2],
    (∀ i, eval₂ (Int.castRingHom ℤ_[2]) a (projectionSystem i) = 0) →
    (∀ i, eval₂ (Int.castRingHom ℤ_[2]) b (projectionSystem i) = 0) →
    (∀ i, (2 : ℤ_[2]) ∣ b i - a i) → a = b := by
  exact projection_two_padic_roots
