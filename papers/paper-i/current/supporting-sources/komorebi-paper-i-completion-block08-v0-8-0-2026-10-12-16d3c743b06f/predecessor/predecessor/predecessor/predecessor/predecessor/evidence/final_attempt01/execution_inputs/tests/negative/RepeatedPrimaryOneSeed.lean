import PrimaryBoundaryConsumers
open Polynomial Komorebi.SeedRankBasics PaperIBlock03Tests
example : ∃ s : Fin 1 → ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}),
    FamilyGenerates ℚ[X] ((i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}) s :=
  nonlinear_repeated_primary_minimum_two.1
