import PrimaryBoundaryConsumers
open Polynomial Komorebi.SeedRankBasics PaperIBlock03Tests
example : IsLeast {r : ℕ | ∃ s : Fin r → ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}),
    FamilyGenerates ℚ[X] ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}) s} 4 :=
  nonlinear_repeated_primary_minimum_two
