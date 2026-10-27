import PaperIRelease.GraphSources
set_option autoImplicit false
namespace Komorebi.PaperIRelease
open Komorebi.Foundation
open Komorebi.PacketNaturalityCompletion.Reachability
open Komorebi.PacketNaturalityCompletion.StrictNaturality
open FiniteDigraph
universe u v w
variable {K : Type u} [Field K] {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w} [Fintype I] [DecidableEq I]
theorem generatedAlgebra_source_obstruction
    (P : LinearProjectorFamily K X I) (ops : Set (Module.End K X))
    (C : Sources (TransferEdge P ops)) (seeds : Set X)
    (hseeds : ∀ s ∈ seeds, VectorSupported P {a | component (TransferEdge P ops) a ≠ C.val} s)
    {x : X} (hx : x ≠ 0)
    (hxC : VectorSupported P {a | component (TransferEdge P ops) a = C.val} x) :
    x ∉ AlgebraGeneratedHull (packetGeneratedAlgebra P ops) seeds := by
  classical
  have hcoord : ∃ b, P.proj b x ≠ 0 := by
    by_contra h
    apply hx
    calc
      x = ∑ b, P.proj b x := (P.complete x).symm
      _ = 0 := Finset.sum_eq_zero (fun b _ => by simpa using not_exists.mp h b)
  obtain ⟨b, hb⟩ := hcoord
  have hbC : component (TransferEdge P ops) b = C.val := by
    by_contra h
    exact hb (hxC b h)
  apply generatedAlgebra_unreachable_obstruction P ops _ seeds hseeds ?_ hb
  rintro ⟨a, ha, hab⟩
  exact ha (no_reach_into_source (TransferEdge P ops) C hbC hab)
end Komorebi.PaperIRelease
#print axioms Komorebi.PaperIRelease.generatedAlgebra_source_obstruction
