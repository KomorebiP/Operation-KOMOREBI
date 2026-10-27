import DyadicSharpTower
open KomorebiPaperIX.DyadicSharpTower
example : padicValRat 2 (kappa 1) = 4 := by
  have h := kappa_valuation 1 (by decide)
  norm_num at h ⊢
  exact h
