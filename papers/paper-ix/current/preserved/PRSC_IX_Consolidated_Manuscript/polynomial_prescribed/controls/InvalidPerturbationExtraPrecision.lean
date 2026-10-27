module
public import PolynomialDeformationControls
@[expose] public section
open Komorebi.PolynomialDeformationControls MvPolynomial

-- Invalid: G=X−2 is an integral coefficient perturbation of F=X of precision one.
-- Its actual p-adic root has displacement two, which does not have precision two.
example : ∃ b : Fin 1 → ℤ_[2],
    eval₂ (Int.castRingHom ℤ_[2]) b (Komorebi.PolynomialTowerControls.linearMinusTwo 0) = 0 ∧
    (2 : ℤ_[2]) ^ 2 ∣ b 0 := by
  exact linear_shift_no_extra_padic_precision
