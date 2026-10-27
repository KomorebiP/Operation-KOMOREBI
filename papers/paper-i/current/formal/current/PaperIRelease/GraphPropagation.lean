import PaperIRelease.GraphSources

/-! Surjective transfer blocks propagate entire actual packet ranges.
The graph is the declared generator TransferEdge graph, and the available
blocks are operators in its actual generated algebra. -/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 2000000

namespace Komorebi.PaperIRelease
open Komorebi.Foundation
open Komorebi.PacketNaturalityCompletion.Reachability
open Komorebi.PacketNaturalityCompletion.FullBlocks
open Komorebi.PacketNaturalityCompletion.StrictNaturality
open FiniteDigraph

universe u v w
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w} [Fintype I]

/-- Literal edge-surjectivity: for every actual generator edge, some operator
in the generated algebra has a surjective source-to-target restricted block. -/
def EdgeSurjective (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) : Prop :=
  ∀ ⦃a b : I⦄, TransferEdge P ops a b →
    ∃ T : packetGeneratedAlgebra P ops, Function.Surjective (restrictBlocks P T.val b a)

def AlgebraInvariant (A : Subalgebra K (Module.End K X)) (H : Submodule K X) : Prop :=
  ∀ T ∈ A, ∀ x ∈ H, T x ∈ H

theorem projector_mem_generatedAlgebra (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (a : I) : P.proj a ∈ packetGeneratedAlgebra P ops :=
  Algebra.subset_adjoin (Or.inl ⟨a, rfl⟩)

theorem algebraGeneratedHull_invariant (A : Subalgebra K (Module.End K X))
    (S : Set X) : AlgebraInvariant A (AlgebraGeneratedHull A S) := by
  intro T hT x hx
  induction hx using Submodule.span_induction with
  | mem x hx =>
    obtain ⟨U, s, hs, rfl⟩ := hx
    exact Submodule.subset_span ⟨⟨T * U.val, A.mul_mem hT U.property⟩, s, hs, rfl⟩
  | zero => simpa only [map_zero] using (AlgebraGeneratedHull A S).zero_mem
  | add x y hx hy ihx ihy =>
    simpa only [map_add] using (AlgebraGeneratedHull A S).add_mem ihx ihy
  | smul c x hx ih =>
    simpa only [map_smul] using (AlgebraGeneratedHull A S).smul_mem c ih

theorem transferBlock_preserves_invariant (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (H : Submodule K X)
    (hH : AlgebraInvariant (packetGeneratedAlgebra P ops) H)
    {T : Module.End K X} (hT : T ∈ packetGeneratedAlgebra P ops) (b a : I)
    {x : X} (hx : x ∈ H) : transferBlock P P T b a x ∈ H := by
  exact hH _ (projector_mem_generatedAlgebra P ops b) _
    (hH T hT _ (hH _ (projector_mem_generatedAlgebra P ops a) x hx))

/-- Surjectivity of the literal restricted block transfers range containment. -/
theorem range_le_of_surjective_block (P : LinearProjectorFamily K X I)
    (H : Submodule K X) (T : Module.End K X) (a b : I)
    (hsurj : Function.Surjective (restrictBlocks P T b a))
    (hstable : ∀ x ∈ H, transferBlock P P T b a x ∈ H)
    (ha : LinearMap.range (P.proj a) ≤ H) : LinearMap.range (P.proj b) ≤ H := by
  intro y hy
  obtain ⟨x, hx⟩ := hsurj ⟨y, hy⟩
  have hxself : P.proj a (x : X) = x := by
    obtain ⟨z, hz⟩ := x.property
    rw [← hz]
    exact P.idempotent a z
  have heq : transferBlock P P T b a (x : X) = y := by
    have heq := congrArg Subtype.val hx
    change P.proj b (T (x : X)) = y at heq
    simpa only [transferBlock, LinearMap.comp_apply, hxself] using heq
  rw [← heq]
  exact hstable x (ha x.property)

theorem edge_range_le (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (hedges : EdgeSurjective P ops)
    (H : Submodule K X) (hH : AlgebraInvariant (packetGeneratedAlgebra P ops) H)
    {a b : I} (hab : TransferEdge P ops a b)
    (ha : LinearMap.range (P.proj a) ≤ H) : LinearMap.range (P.proj b) ≤ H := by
  obtain ⟨T, hT⟩ := hedges hab
  exact range_le_of_surjective_block P H T.val a b hT
    (fun _ hx => transferBlock_preserves_invariant P ops H hH T.property b a hx) ha

/-- Surjective edges propagate a full packet along every finite directed path. -/
theorem reachable_range_le (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (hedges : EdgeSurjective P ops)
    (H : Submodule K X) (hH : AlgebraInvariant (packetGeneratedAlgebra P ops) H)
    {a b : I} (hab : Reach (TransferEdge P ops) a b)
    (ha : LinearMap.range (P.proj a) ≤ H) : LinearMap.range (P.proj b) ≤ H := by
  induction hab with
  | refl => exact ha
  | tail hab hbc ih => exact edge_range_le P ops hedges H hH hbc ih

/-- A variant for a subspace invariant only under blocks internal to one SCC.
This is the propagation needed for local corner-algebra cyclicity. -/
theorem reachable_range_le_in_component (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (hedges : EdgeSurjective P ops)
    (C : SCC (TransferEdge P ops)) (H : Submodule K X)
    (hH : ∀ a b, component (TransferEdge P ops) a = C →
      component (TransferEdge P ops) b = C → ∀ T ∈ packetGeneratedAlgebra P ops,
      ∀ x ∈ H, transferBlock P P T b a x ∈ H)
    {a b : I} (hab : Reach (TransferEdge P ops) a b) :
    component (TransferEdge P ops) a = C → component (TransferEdge P ops) b = C →
      LinearMap.range (P.proj a) ≤ H → LinearMap.range (P.proj b) ≤ H := by
  induction hab using Relation.ReflTransGen.head_induction_on with
  | refl => intro _ _ ha; exact ha
  | @head a c hac hcb ih =>
    intro ha hb hrange
    have hc : component (TransferEdge P ops) c = C := by
      exact (intermediate_same_component (TransferEdge P ops) (ha.trans hb.symm)
        (.single hac) hcb).trans ha
    apply ih hc hb
    obtain ⟨T, hT⟩ := hedges hac
    exact range_le_of_surjective_block P H T.val a c hT (hH a c ha hc T.val T.property) hrange

/-- Whole source components generate the ambient space: finite source existence
and graph reachability are conclusions of the previous graph theorem. -/
theorem submodule_eq_top_of_sources (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (hedges : EdgeSurjective P ops)
    (H : Submodule K X) (hH : AlgebraInvariant (packetGeneratedAlgebra P ops) H)
    (hsources : ∀ C : Sources (TransferEdge P ops), ∀ a,
      component (TransferEdge P ops) a = C.val → LinearMap.range (P.proj a) ≤ H) :
    H = ⊤ := by
  apply top_unique
  intro x _
  rw [← P.complete x]
  apply H.sum_mem
  intro b _
  obtain ⟨C, a, ha, hab⟩ := exists_source_reaching (TransferEdge P ops) b
  exact reachable_range_le P ops hedges H hH hab (hsources C a ha) ⟨x, rfl⟩

variable [DecidableEq I]

/-- The generated algebra has zero blocks from outside into a source SCC. -/
theorem source_block_zero (P : LinearProjectorFamily K X I)
    (ops : Set (Module.End K X)) (C : Sources (TransferEdge P ops))
    {a b : I} (ha : component (TransferEdge P ops) a ≠ C.val)
    (hb : component (TransferEdge P ops) b = C.val)
    {T : Module.End K X} (hT : T ∈ packetGeneratedAlgebra P ops) :
    transferBlock P P T b a = 0 := by
  apply generatedAlgebra_block_zero P ops hT
  intro hab
  exact ha (no_reach_into_source (TransferEdge P ops) C hb hab)

end Komorebi.PaperIRelease
