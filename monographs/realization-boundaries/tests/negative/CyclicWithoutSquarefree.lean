import tests.Contracts

set_option autoImplicit false
noncomputable section
open RealizationBoundaries RealizationBoundariesRootTests

example (W : Submodule ℚ TailSpace) : ∃ f : preimage W →+ ZMod 4, Function.Surjective f := by
  apply (finite_quotient_exists_iff W (ZMod 4)).mpr
  refine ⟨inferInstance, ?_⟩
  have hcard : Nat.card (ZMod 4) = 4 := by simp
  rw [hcard]
  exact Nat.prime_two.prime.squarefree
