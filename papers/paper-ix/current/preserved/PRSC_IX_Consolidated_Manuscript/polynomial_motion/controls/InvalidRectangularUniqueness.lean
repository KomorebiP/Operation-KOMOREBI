module
public import PolynomialTowerControls
@[expose] public section
open Komorebi.PolynomialTowerControls MvPolynomial

-- Invalid: a surjective rectangular Jacobian permits free coordinates inside one residue ball.
example : ∀ a b : Fin 2 → ℤ_[2],
    (∀ i, eval₂ (Int.castRingHom ℤ_[2]) a (projectionSystem i) = 0) →
    (∀ i, eval₂ (Int.castRingHom ℤ_[2]) b (projectionSystem i) = 0) →
    (∀ i, (2 : ℤ_[2]) ∣ b i - a i) → a = b := by
  exact projection_two_padic_roots
