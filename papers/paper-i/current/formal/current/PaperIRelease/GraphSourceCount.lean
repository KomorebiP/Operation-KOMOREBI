import PaperIRelease.PacketLocalRank
import PaperIRelease.GraphSourceProjection

set_option autoImplicit false
set_option linter.unnecessarySimpa false
set_option maxHeartbeats 3000000
noncomputable section

namespace Komorebi.PaperIRelease
open Cardinal Set Komorebi.Foundation Komorebi.SeedRankBasics
open Komorebi.PacketNaturalityCompletion.Reachability
open FiniteDigraph PacketAggregation

universe u
variable {K X I : Type u} [Field K] [AddCommGroup X] [Module K X] [Fintype I]

/-- Cyclicity is under the actual diagonal corner of the generated operator algebra. -/
def PacketCornerCyclic (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) : Prop :=
  ∀ i, Cyclic (packetCornerAlgebra (packetGeneratedAlgebra P ops) (P.proj i)
    (projector_mem_generatedAlgebra P ops i) (P.idempotent i)) (LinearMap.range (P.proj i))

/-- Literal packet propagation combines actual edge surjections and actual corner cyclicity. -/
def PacketPropagating (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) : Prop := EdgeSurjective P ops ∧ PacketCornerCyclic P ops

/-- One cyclic seed at one vertex per source component supplies the global upper bound. -/
theorem packetPureSeedRank_le_source_count (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (hedges : EdgeSurjective P ops)
    (hcyclic : PacketCornerCyclic P ops) :
    packetPureSeedRank (packetGeneratedAlgebra P ops) P ≤ #(Sources (TransferEdge P ops)) := by
  classical
  let A := packetGeneratedAlgebra P ops
  let edge := TransferEdge P ops
  choose s hs using hcyclic
  choose vertex hv using (fun C : Sources edge => component_surjective edge C.val)
  let seed : Sources edge → X := fun C => (s (vertex C) : X)
  let H : Submodule A X := Submodule.span A (Set.range seed)
  have hpacket (C : Sources edge) : LinearMap.range (P.proj (vertex C)) ≤ H.restrictScalars K := by
    intro x hx
    have hgen := hs (vertex C)
    have hxs : (⟨x,hx⟩ : LinearMap.range (P.proj (vertex C))) ∈
        Submodule.span (packetCornerAlgebra A (P.proj (vertex C))
          (projector_mem_generatedAlgebra P ops (vertex C)) (P.idempotent (vertex C)))
            {s (vertex C)} := by
      rw [hgen]
      trivial
    refine Submodule.span_induction
      (p := fun (y : LinearMap.range (P.proj (vertex C))) _ => (y : X) ∈ H) ?_ ?_ ?_ ?_ hxs
    · intro y hy
      have hy' : y = s (vertex C) := Set.mem_singleton_iff.mp hy
      subst y
      exact Submodule.subset_span ⟨C, rfl⟩
    · exact H.zero_mem
    · intro y z _ _ hy hz
      exact H.add_mem hy hz
    · intro a y _ hy
      obtain ⟨b,hb⟩ := corner_action_ambient A (P.proj (vertex C))
        (projector_mem_generatedAlgebra P ops (vertex C)) (P.idempotent (vertex C)) a
      rw [hb y]
      exact H.smul_mem b hy
  have hinvariant : AlgebraInvariant A (H.restrictScalars K) := by
    intro T hT x hx
    exact H.smul_mem (⟨T,hT⟩ : A) hx
  have htop : H.restrictScalars K = ⊤ := by
    apply submodule_eq_top_of_sources P ops hedges _ hinvariant
    intro C a ha
    have hreach : Reach edge (vertex C) a :=
      ((component_eq_iff edge (vertex C) a).mp ((hv C).trans ha.symm)).1
    exact reachable_range_le P ops hedges _ hinvariant hreach (hpacket C)
  have hgen : PureGenerates A P (Set.range seed) := by
    constructor
    · apply top_unique
      intro x _
      have hx : x ∈ H.restrictScalars K := by rw [htop]; trivial
      exact hx
    · rintro x ⟨C,rfl⟩
      exact packetPure_of_mem_range P (s (vertex C)).property
  exact (packetPureSeedRank_le_card hgen).trans Cardinal.mk_range_le

/-- Every source class contains an original packet, so nonzero packets give a nonzero local rank. -/
theorem one_le_source_localPureSeedRank (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) [∀ i, Nontrivial (LinearMap.range (P.proj i))]
    (C : Sources (TransferEdge P ops)) :
    1 ≤ localPureSeedRank (packetGeneratedAlgebra P ops) P
      (projector_mem_generatedAlgebra P ops) (component (TransferEdge P ops)) C.val := by
  classical
  let A := packetGeneratedAlgebra P ops
  let σ := component (TransferEdge P ops)
  let V := LinearMap.range ((groupedFamily P σ).proj C.val)
  obtain ⟨i, hi⟩ := component_surjective (TransferEdge P ops) C.val
  obtain ⟨x,hx⟩ := exists_ne (0 : LinearMap.range (P.proj i))
  have hmem : (x : X) ∈ V := by
    have h := original_mem_grouped P σ i x
    simpa only [σ, V, hi] using h
  have hnonzero : (⟨x,hmem⟩ : V) ≠ 0 := by
    intro h
    apply hx
    exact Subtype.ext (congrArg (fun y : V => (y : X)) h)
  apply Cardinal.one_le_iff_ne_zero.mpr
  intro hzero
  have hle := seedRank_le_packetPureSeedRank
    (localCornerAlgebra A P (projector_mem_generatedAlgebra P ops) σ C.val)
    (localPacketFamily P σ C.val)
  have hs : seedRank (localCornerAlgebra A P (projector_mem_generatedAlgebra P ops) σ C.val) V = 0 :=
    le_antisymm (hzero ▸ hle) bot_le
  have hsub := (seedRank_eq_zero_iff _ V).mp hs
  exact hnonzero (@Subsingleton.elim V hsub _ _)

/-- Every generating set must meet each nonzero source component. -/
theorem generating_set_meets_source (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) [∀ i, Nontrivial (LinearMap.range (P.proj i))]
    (S : Set X) (hS : Generates (packetGeneratedAlgebra P ops) X S)
    (C : Sources (TransferEdge P ops)) :
    ∃ x ∈ S, componentProjection P ops C.val x ≠ 0 := by
  classical
  by_contra h
  have hseed : ∀ x ∈ S, componentProjection P ops C.val x = 0 := by
    intro x hx
    by_contra hne
    exact h ⟨x,hx,hne⟩
  have hspan : ∀ x ∈ Submodule.span (packetGeneratedAlgebra P ops) S,
      componentProjection P ops C.val x = 0 := by
    intro x hx
    induction hx using Submodule.span_induction with
    | mem x hx => exact hseed x hx
    | zero => exact map_zero _
    | add x y _ _ hx hy => rw [map_add, hx, hy, add_zero]
    | smul T x _ hx =>
      change componentProjection P ops C.val (T.val x) = 0
      rw [sourceProjection_compression P ops C T.property x, hx, map_zero, map_zero]
  obtain ⟨i,hi⟩ := component_surjective (TransferEdge P ops) C.val
  obtain ⟨x,hx⟩ := exists_ne (0 : LinearMap.range (P.proj i))
  have hxs : (x : X) ∈ Submodule.span (packetGeneratedAlgebra P ops) S := by rw [hS]; trivial
  have hz := hspan x hxs
  rw [componentProjection_packet P ops C.val hi x.property] at hz
  exact hx (Subtype.ext hz)

/-- Different source components require different pure seeds, even without edge surjectivity. -/
theorem source_count_le_packetPureSeedRank (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) [∀ i, Nontrivial (LinearMap.range (P.proj i))] :
    #(Sources (TransferEdge P ops)) ≤ packetPureSeedRank (packetGeneratedAlgebra P ops) P := by
  classical
  obtain ⟨S,hS,hcard⟩ := exists_pure_generating_set_card_eq (packetGeneratedAlgebra P ops) P
  rw [← hcard]
  choose x hx hnonzero using (fun C : Sources (TransferEdge P ops) =>
    generating_set_meets_source P ops S hS.1 C)
  let f : Sources (TransferEdge P ops) → S := fun C => ⟨x C, hx C⟩
  apply Cardinal.mk_le_of_injective (f := f)
  intro C D hCD
  by_contra hne
  have hval : x C = x D := congrArg Subtype.val hCD
  let σ := component (TransferEdge P ops)
  let Q := groupedFamily P σ
  have hC : Q.proj C.val (x C) = x C :=
    (pure_grouped_fixed_or_zero P σ C.val (hS.2 (x C) (hx C))).resolve_right (hnonzero C)
  have hD : Q.proj D.val (x C) = x C := by
    rw [hval]
    exact (pure_grouped_fixed_or_zero P σ D.val (hS.2 (x D) (hx D))).resolve_right (hnonzero D)
  have hindex : C.val ≠ D.val := fun h => hne (Subtype.ext h)
  have hzero := Q.orthogonal hindex (x C)
  rw [hD, hC] at hzero
  exact hnonzero C (hC.trans hzero)

/-- Unweighted source-component count for a packet-propagating system. -/
theorem packetPureSeedRank_eq_source_count (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) [∀ i, Nontrivial (LinearMap.range (P.proj i))]
    (hpropagating : PacketPropagating P ops) :
    packetPureSeedRank (packetGeneratedAlgebra P ops) P =
      #(Sources (TransferEdge P ops)) :=
  le_antisymm (packetPureSeedRank_le_source_count P ops hpropagating.1 hpropagating.2)
    (source_count_le_packetPureSeedRank P ops)

/-- Natural-number cardinality form of the finite source count. -/
theorem packetPureSeedRank_eq_source_card (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) [∀ i, Nontrivial (LinearMap.range (P.proj i))]
    (hpropagating : PacketPropagating P ops) :
    packetPureSeedRank (packetGeneratedAlgebra P ops) P =
      (Fintype.card (Sources (TransferEdge P ops)) : Cardinal) := by
  simpa only [Cardinal.mk_fintype] using packetPureSeedRank_eq_source_count P ops hpropagating

end Komorebi.PaperIRelease
