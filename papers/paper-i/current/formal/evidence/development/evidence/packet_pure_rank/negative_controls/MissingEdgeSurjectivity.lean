import PaperIRelease.PacketSourceRank
open Komorebi.PaperIRelease Komorebi.Foundation
open Komorebi.PaperIRelease.FiniteDigraph
open Komorebi.PacketNaturalityCompletion.Reachability
variable {K X I : Type} [Field K] [AddCommGroup X] [Module K X] [Fintype I] [DecidableEq I]
example (P : LinearProjectorFamily K X I) (ops : Set (Module.End K X)) :
    packetPureSeedRank (packetGeneratedAlgebra P ops) P =
      Cardinal.sum (fun C : Sources (TransferEdge P ops) =>
        localPureSeedRank (packetGeneratedAlgebra P ops) P
          (projector_mem_generatedAlgebra P ops)
          (component (TransferEdge P ops)) C.val) := by
  exact source_component_pureSeedRank P ops
