import KomorebiPadic.ResidualMinimalityExamples
open KomorebiPadic KomorebiPadic.ResidualRealization
noncomputable section

example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [] [] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [] [0] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [] [1] = 1 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [] [0,0] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [] [0,1] = 2 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [] [1,0] = 1 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [] [1,1] = 3 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0] [] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0] [0] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0] [1] = 2 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0] [0,0] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0] [0,1] = 4 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0] [1,0] = 2 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0] [1,1] = 6 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1] [] = 1 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1] [0] = 1 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1] [1] = 3 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1] [0,0] = 1 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1] [0,1] = 5 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1] [1,0] = 3 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1] [1,1] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,0] [] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,0] [0] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,0] [1] = 4 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,0] [0,0] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,0] [0,1] = 1 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,0] [1,0] = 4 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,0] [1,1] = 5 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,1] [] = 2 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,1] [0] = 2 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,1] [1] = 6 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,1] [0,0] = 2 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,1] [0,1] = 3 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,1] [1,0] = 6 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [0,1] [1,1] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,0] [] = 1 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,0] [0] = 1 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,0] [1] = 5 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,0] [0,0] = 1 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,0] [0,1] = 2 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,0] [1,0] = 5 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,0] [1,1] = 6 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,1] [] = 3 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,1] [0] = 3 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,1] [1] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,1] [0,0] = 3 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,1] [0,1] = 4 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,1] [1,0] = 0 := by decide +kernel
example : residual (fun ds : List ℕ => (cartierWordValue 2 ds : ZMod 7)) [1,1] [1,1] = 1 := by decide +kernel
example : behavior constantOne [] = 1 := constantOne_observation [] 1
example : behavior constantOne [(),(),()] = 1 := constantOne_observation _ 1
example : behavior scaledConstant [] = 1 := by rw [scaledConstant_same_behavior]; exact constantOne_observation [] 1
example : behavior trailingZero [] = 0 := trailingZero_empty
example : behavior trailingZero [0] = 1 := trailingZero_single_zero
example : behavior trailingZero [0,1] = 0 := trailingZero_ends_one [0]
example : behavior trailingZero [1,0,1] = 0 := trailingZero_ends_one [1,0]
example : LinearObservability.State LinearObservability.twiceIdentity ≃ₗ[ZMod 4] ResidualState (behavior LinearObservability.twiceIdentity) := quotientEquivResidual _ LinearObservability.twiceIdentity_reachable
example : Simulation constantOne scaledConstant doubleMap := doubleMap_simulation
end
