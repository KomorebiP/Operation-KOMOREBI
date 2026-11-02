import CoupledLowerGrowth
open Komorebi.SpecialFunctions.Coupled.Scales
example : ∀ R : ℝ, 2 ≤ R → R ≤ 2 := by
  exact real_radius_descent_induction (P := fun R => R ≤ 2) (B := 2) (d := 0)
    (by norm_num) (fun _ _ hB => hB)
    (fun R hR _ hIH => hIH R hR (by simp))
