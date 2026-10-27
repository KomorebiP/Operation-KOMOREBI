import PrimaryBoundaryConsumers
open Polynomial Komorebi.SeedRankBasics
open Komorebi.PaperICompletion3.PrimarySeedFormula PaperIBlock03Tests
-- A zero exponent gives the zero module, not a nonzero primary block.
example : IsLeast {r : ℕ | ∃ s : Fin r → ((i : Fin 1) → ℚ[X] ⧸ Ideal.span {quadratic ^ 0}),
    FamilyGenerates ℚ[X] ((i : Fin 1) → ℚ[X] ⧸ Ideal.span {quadratic ^ 0}) s} 1 := by
  simpa [maxMultiplicity, fiberMultiplicity] using
    primePowerProduct_seedNumber_isLeast (fun _ : Fin 1 ↦ quadratic)
      (fun _ ↦ quadratic_irreducible) (fun _ : Fin 1 ↦ 0) (fun _ ↦ by decide)
