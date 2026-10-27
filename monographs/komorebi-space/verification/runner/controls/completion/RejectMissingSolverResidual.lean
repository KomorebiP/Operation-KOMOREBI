import KomorebiSpace.DiagonalInexactRate

open KomorebiSpace.DiagonalRegularization

-- Deliberate mutation: the scalar tolerance budget cannot replace the bound
-- on the measured normal residual. All other theorem hypotheses are retained.
example (s a : H) {δ κ ε : ℝ}
    (hδ : 0 < δ) (hδ₁ : δ ≤ 1) (hκ : 0 ≤ κ)
    (hdata : ‖s - b‖ ≤ δ)
    (hε : ε ≤ κ * alpha (Nat.ceil (δ ^ (-(2 : ℝ) / 3))) *
      δ ^ ((1 : ℝ) / 3)) :
    ‖a - w‖ ≤ (Real.sqrt 2 + 1 + κ) * δ ^ ((1 : ℝ) / 3) := by
  exact diagonal_inexact_rounded_rate s a hδ hδ₁ hκ hdata hε hε
