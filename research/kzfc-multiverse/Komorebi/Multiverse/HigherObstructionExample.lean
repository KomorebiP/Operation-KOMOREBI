import Komorebi.Multiverse.AmalgamationNerve

/-!
# A finite higher-amalgamation obstruction

The six worlds represent the nonempty proper faces of a three-point simplex:
three vertices and three edges.  Reachability is inclusion of supports.  The
three vertex worlds amalgamate pairwise in edge worlds, but no world in the
network contains all three vertices.
-/

namespace Komorebi.Multiverse

inductive TriangleWorld where
  | a | b | c | ab | ac | bc
  deriving DecidableEq

namespace TriangleWorld

/-- Finite support represented by each world. -/
def support : TriangleWorld → Finset (Fin 3)
  | a  => {0}
  | b  => {1}
  | c  => {2}
  | ab => {0, 1}
  | ac => {0, 2}
  | bc => {1, 2}

end TriangleWorld

/-- The finite world network ordered by inclusion of supports. -/
def triangleNetwork : WorldNetwork where
  World := TriangleWorld
  reach := fun x y => x.support ⊆ y.support
  refl := fun _ => Finset.Subset.rfl
  trans := fun hxy hyz => hxy.trans hyz

abbrev TN := triangleNetwork

def boundaryTriple : Finset TriangleWorld := {.a, .b, .c}

/-- Membership in the boundary has exactly the three vertex cases. -/
theorem mem_boundaryTriple_iff (x : TriangleWorld) :
    x ∈ boundaryTriple ↔ x = .a ∨ x = .b ∨ x = .c := by
  constructor
  · intro h
    unfold boundaryTriple at h
    rcases Finset.mem_insert.mp h with h | h
    · exact Or.inl h
    rcases Finset.mem_insert.mp h with h | h
    · exact Or.inr (Or.inl h)
    · exact Or.inr (Or.inr (Finset.mem_singleton.mp h))
  · rintro (rfl | rfl | rfl)
    · unfold boundaryTriple
      exact Finset.mem_insert_self _ _
    · unfold boundaryTriple
      exact Finset.mem_insert_of_mem (Finset.mem_insert_self _ _)
    · unfold boundaryTriple
      exact Finset.mem_insert_of_mem (Finset.mem_insert_of_mem (Finset.mem_singleton_self _))

/-- Every pair of vertex worlds has a common upper edge world. -/
theorem boundaryTriple_pairwise : TN.PairwiseAmalgamable boundaryTriple := by
  change ∀ x ∈ boundaryTriple, ∀ y ∈ boundaryTriple,
    ∃ u : TriangleWorld, x.support ⊆ u.support ∧ y.support ⊆ u.support
  intro x hx y hy
  rcases (mem_boundaryTriple_iff x).mp hx with rfl | rfl | rfl <;>
    rcases (mem_boundaryTriple_iff y).mp hy with rfl | rfl | rfl
  · exact ⟨.a, by simp [TriangleWorld.support]⟩
  · exact ⟨.ab, by simp [TriangleWorld.support]⟩
  · exact ⟨.ac, by simp [TriangleWorld.support]⟩
  · exact ⟨.ab, by simp [TriangleWorld.support]⟩
  · exact ⟨.b, by simp [TriangleWorld.support]⟩
  · exact ⟨.bc, by simp [TriangleWorld.support]⟩
  · exact ⟨.ac, by simp [TriangleWorld.support]⟩
  · exact ⟨.bc, by simp [TriangleWorld.support]⟩
  · exact ⟨.c, by simp [TriangleWorld.support]⟩

/-- There is no world above all three vertices. -/
theorem boundaryTriple_not_joint : ¬ TN.JointAmalgamable boundaryTriple := by
  change ¬ ∃ u : TriangleWorld, ∀ w ∈ boundaryTriple, w.support ⊆ u.support
  rintro ⟨u, hu⟩
  have ha := hu .a ((mem_boundaryTriple_iff .a).mpr (Or.inl rfl))
  have hb := hu .b ((mem_boundaryTriple_iff .b).mpr (Or.inr (Or.inl rfl)))
  have hc := hu .c ((mem_boundaryTriple_iff .c).mpr (Or.inr (Or.inr rfl)))
  cases u <;> simp [TriangleWorld.support] at ha hb hc

/-- The boundary triangle therefore carries a genuine higher obstruction. -/
theorem boundaryTriple_higherObstruction : TN.HigherObstruction boundaryTriple :=
  ⟨boundaryTriple_pairwise, boundaryTriple_not_joint⟩

end Komorebi.Multiverse
