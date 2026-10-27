import Mathlib.Data.Finset.Basic

/-!
# Abstract world networks and amalgamation

This module deliberately does not identify worlds with forcing extensions yet.
A `WorldNetwork` is the minimal reflexive/transitive accessibility structure needed
for the Komorebi multiverse residual program.  Concrete set-theoretic multiverses
can later instantiate `extends` by forcing reachability, ground reachability, or
another explicitly chosen notion.
-/

universe u

namespace Komorebi.Multiverse

/-- A class-sized idea is represented locally by a type of worlds together with an
admissible extension/reachability relation.  Reflexivity and transitivity are the
only laws assumed at this layer. -/
structure WorldNetwork where
  World : Type u
  reach : World → World → Prop
  refl : ∀ w, reach w w
  trans : ∀ {a b c}, reach a b → reach b c → reach a c

namespace WorldNetwork

variable (N : WorldNetwork.{u})

/-- `u` is a common upper world for all worlds in the finite family `s`. -/
def CommonUpper (s : Finset N.World) (u : N.World) : Prop :=
  ∀ w ∈ s, N.reach w u

/-- A finite family of worlds is jointly amalgamable if it has a common upper world. -/
def JointAmalgamable (s : Finset N.World) : Prop :=
  ∃ u, N.CommonUpper s u

/-- Two worlds are compatible upward when they possess a common upper world. -/
def PairAmalgamable (a b : N.World) : Prop :=
  ∃ u, N.reach a u ∧ N.reach b u

/-- Every pair drawn from `s` is upward-compatible. -/
def PairwiseAmalgamable (s : Finset N.World) : Prop :=
  ∀ a ∈ s, ∀ b ∈ s, N.PairAmalgamable a b

/-- Degree-zero amalgamation obstruction. -/
def Obstructed (s : Finset N.World) : Prop :=
  ¬ N.JointAmalgamable s

/-- A first higher obstruction: all pairwise tests vanish but the whole finite
family does not admit a common upper world. -/
def HigherObstruction (s : Finset N.World) : Prop :=
  N.PairwiseAmalgamable s ∧ N.Obstructed s

/-- The amalgamation nerve: finite simplices are exactly jointly amalgamable families. -/
def Simplex (s : Finset N.World) : Prop := N.JointAmalgamable s

/-- Amalgamability is downward closed, hence `Simplex` really is an abstract
simplicial-complex predicate on finite world sets. -/
theorem simplex_downward {s t : Finset N.World} (hst : s ⊆ t)
    (ht : N.Simplex t) : N.Simplex s := by
  obtain ⟨u, hu⟩ := ht
  exact ⟨u, fun w hw => hu w (hst hw)⟩

/-- Joint amalgamability kills every pairwise obstruction. -/
theorem pairwise_of_joint {s : Finset N.World} (h : N.JointAmalgamable s) :
    N.PairwiseAmalgamable s := by
  obtain ⟨u, hu⟩ := h
  intro a ha b hb
  exact ⟨u, hu a ha, hu b hb⟩

/-- The empty family is always amalgamable once a world is supplied. -/
theorem empty_joint (w : N.World) : N.JointAmalgamable ∅ := by
  exact ⟨w, by simp [CommonUpper]⟩

/-- Every singleton is amalgamable by reflexivity. -/
theorem singleton_joint (w : N.World) : N.JointAmalgamable {w} := by
  refine ⟨w, ?_⟩
  intro x hx
  have hxw : x = w := by simpa using hx
  subst x
  exact N.refl w

/-- Higher obstruction implies genuine global obstruction. -/
theorem higherObstruction_obstructed {s : Finset N.World}
    (h : N.HigherObstruction s) : N.Obstructed s := h.2

/-- A jointly amalgamable family can never carry the first higher obstruction. -/
theorem not_higherObstruction_of_joint {s : Finset N.World}
    (h : N.JointAmalgamable s) : ¬ N.HigherObstruction s := by
  intro hh
  exact hh.2 h

end WorldNetwork

end Komorebi.Multiverse
