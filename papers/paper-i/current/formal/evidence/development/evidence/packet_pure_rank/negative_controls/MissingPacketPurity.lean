import PaperIRelease.PacketSourceLower
open Komorebi.PaperIRelease Komorebi.Foundation Komorebi.SeedRankBasics
open Komorebi.PaperIRelease.PacketAggregation
variable {K X I J : Type} [Field K] [AddCommGroup X] [Module K X]
variable [Fintype I] [Fintype J] [DecidableEq J]
example (A : Subalgebra K (Module.End K X)) (P : LinearProjectorFamily K X I)
    (hPA : ∀ i, P.proj i ∈ A) (σ : I → J) (C : J)
    (hcomp : ∀ a ∈ A, ∀ x, (groupedFamily P σ).proj C (a x) =
      (groupedFamily P σ).proj C (a ((groupedFamily P σ).proj C x)))
    (S : Set X) (hS : Generates A X S) :
    PureGenerates (localCornerAlgebra A P hPA σ C) (localPacketFamily P σ C)
      (localNonzeroSeeds P σ C S) := by
  exact localNonzeroSeeds_generate_of_compression A P hPA σ C hcomp hS
