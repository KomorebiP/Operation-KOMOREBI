import PaperIRelease.GraphPropagation
import PaperIRelease.PacketAggregation

/-! Actual grouped source projections eliminate all incoming contributions
from outside the source SCC. This supplies the source-corner lower bound. -/

noncomputable section
set_option autoImplicit false

namespace Komorebi.PaperIRelease
open Komorebi.Foundation
open Komorebi.PacketNaturalityCompletion.Reachability
open FiniteDigraph PacketAggregation

universe u v w
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w} [Fintype I] [DecidableEq I]

/-- The actual grouped projector onto a strongly connected component. -/
abbrev componentProjection (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (C : SCC (TransferEdge P ops)) : Module.End K X :=
  (groupedFamily P (component (TransferEdge P ops))).proj C

omit [DecidableEq I] in
theorem componentProjection_mem (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (C : SCC (TransferEdge P ops)) :
    componentProjection P ops C ∈ packetGeneratedAlgebra P ops := by
  apply (packetGeneratedAlgebra P ops).sum_mem
  intro a _
  exact projector_mem_generatedAlgebra P ops a

/-- The source projection of an operator depends only on the source projection
of its input. The operator is an element of the actual generated algebra. -/
theorem sourceProjection_compression (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (C : Sources (TransferEdge P ops))
    {T : Module.End K X} (hT : T ∈ packetGeneratedAlgebra P ops) (x : X) :
    componentProjection P ops C.val (T x) =
      componentProjection P ops C.val (T (componentProjection P ops C.val x)) := by
  change groupedProjection P (component (TransferEdge P ops)) C.val (T x) =
    groupedProjection P (component (TransferEdge P ops)) C.val
      (T (groupedProjection P (component (TransferEdge P ops)) C.val x))
  simp only [groupedProjection, LinearMap.sum_apply]
  apply Finset.sum_congr rfl
  intro b hb
  have hbC := (Finset.mem_filter.mp hb).2
  conv_lhs => rw [← P.complete x]
  simp only [map_sum]
  symm
  apply Finset.sum_subset (Finset.filter_subset _ _)
  intro a _ ha
  have haC : component (TransferEdge P ops) a ≠ C.val := by
    intro haC
    exact ha (Finset.mem_filter.mpr ⟨Finset.mem_univ _, haC⟩)
  exact LinearMap.congr_fun (source_block_zero P ops C haC hbC hT) x

/-- Operator form of the same source-corner identity. -/
theorem sourceProjection_comp_eq (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (C : Sources (TransferEdge P ops))
    {T : Module.End K X} (hT : T ∈ packetGeneratedAlgebra P ops) :
    (componentProjection P ops C.val).comp T =
      ((componentProjection P ops C.val).comp T).comp (componentProjection P ops C.val) := by
  ext x
  exact sourceProjection_compression P ops C hT x

omit [DecidableEq I] in
/-- A vector in a packet outside a component has zero component projection. -/
theorem componentProjection_other_packet (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (C : SCC (TransferEdge P ops))
    {a : I} (ha : component (TransferEdge P ops) a ≠ C) {x : X}
    (hx : x ∈ LinearMap.range (P.proj a)) : componentProjection P ops C x = 0 := by
  obtain ⟨y, rfl⟩ := hx
  change (∑ i with component (TransferEdge P ops) i = C, P.proj i) (P.proj a y) = 0
  rw [LinearMap.sum_apply]
  apply Finset.sum_eq_zero
  intro b hb
  apply P.orthogonal
  intro hba
  exact ha (hba ▸ (Finset.mem_filter.mp hb).2)

omit [DecidableEq I] in
/-- A vector in a packet of the component is fixed by its grouped projection. -/
theorem componentProjection_packet (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (C : SCC (TransferEdge P ops))
    {a : I} (ha : component (TransferEdge P ops) a = C) {x : X}
    (hx : x ∈ LinearMap.range (P.proj a)) : componentProjection P ops C x = x := by
  have hxC := original_mem_grouped P (component (TransferEdge P ops)) a ⟨x, hx⟩
  rw [ha] at hxC
  obtain ⟨y, hy⟩ := hxC
  change componentProjection P ops C y = x at hy
  rw [← hy]
  exact (groupedFamily P (component (TransferEdge P ops))).idempotent C y

end Komorebi.PaperIRelease
