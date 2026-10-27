import Mathlib.Data.Set.Lattice.Indexed

namespace ProofPath
universe u

/-- A declared graph of views. Edges induce restrictions in the opposite direction. -/
structure ViewDiagram (V E : Type*) where
  fiber : V → Type u
  source : E → V
  target : E → V
  restriction : (e : E) → fiber (target e) → fiber (source e)

namespace ViewDiagram
variable {V E I : Type*} (F : ViewDiagram V E)

def Coherent (x : (v : V) → F.fiber v) : Prop :=
  ∀ e, F.restriction e (x (F.target e)) = x (F.source e)

theorem arrow_cover_gluing (U : I → Set V)
    (s : (i : I) → (v : V) → v ∈ U i → F.fiber v)
    (cover : ∀ v, ∃ i, v ∈ U i)
    (edgeCover : ∀ e, ∃ i, F.source e ∈ U i ∧ F.target e ∈ U i)
    (matching : ∀ i j v (hi : v ∈ U i) (hj : v ∈ U j), s i v hi = s j v hj)
    (localCoherence : ∀ i e (hs : F.source e ∈ U i) (ht : F.target e ∈ U i),
      F.restriction e (s i (F.target e) ht) = s i (F.source e) hs) :
    ∃! x : (v : V) → F.fiber v,
      F.Coherent x ∧ ∀ i v (h : v ∈ U i), x v = s i v h := by
  classical
  let x : (v : V) → F.fiber v := fun v =>
    s (Classical.choose (cover v)) v (Classical.choose_spec (cover v))
  have agree : ∀ i v (h : v ∈ U i), x v = s i v h := by
    intro i v h
    exact matching _ i v _ h
  refine ⟨x, ⟨?_, agree⟩, ?_⟩
  · intro e
    obtain ⟨i, hs, ht⟩ := edgeCover e
    rw [agree i (F.target e) ht, agree i (F.source e) hs]
    exact localCoherence i e hs ht
  · intro y hy
    funext v
    obtain ⟨i, hi⟩ := cover v
    exact (hy.2 i v hi).trans (agree i v hi).symm

end ViewDiagram
end ProofPath
