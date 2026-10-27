import Komorebi.Multiverse.AmalgamationNerve
import Mathlib.Data.Finset.Image

/-!
# Maps between world networks and amalgamation patterns

A world morphism preserves reachability.  A pattern embedding is stronger: it
preserves and reflects which finite families admit common upper worlds.  This is
the precise interface needed to compare an abstract obstruction pattern with a
concrete generic multiverse construction.
-/

universe u v

namespace Komorebi.Multiverse

structure WorldMorphism (N : WorldNetwork.{u}) (M : WorldNetwork.{v}) where
  toFun : N.World → M.World
  map_reach : ∀ {a b}, N.reach a b → M.reach (toFun a) (toFun b)

namespace WorldMorphism

variable {N : WorldNetwork.{u}} {M : WorldNetwork.{v}}
    (f : WorldMorphism N M)

/-- Reachability-preserving maps send a chosen amalgamation witness to an
amalgamation witness for the image family. -/
theorem maps_commonUpper [DecidableEq M.World]
    {s : Finset N.World} {apex : N.World} (h : N.CommonUpper s apex) :
    M.CommonUpper (s.image f.toFun) (f.toFun apex) := by
  intro w hw
  obtain ⟨a, ha, rfl⟩ := Finset.mem_image.mp hw
  exact f.map_reach (h a ha)

/-- Hence world morphisms preserve finite joint amalgamability. -/
theorem maps_joint [DecidableEq M.World]
    {s : Finset N.World} (h : N.JointAmalgamable s) :
    M.JointAmalgamable (s.image f.toFun) := by
  obtain ⟨apex, h⟩ := h
  exact ⟨f.toFun apex, f.maps_commonUpper h⟩

end WorldMorphism

/-- Exact realization of a finite face complex inside a world network.  This is
an abstract contract only; constructing such an embedding for forcing models is
a separate forcing theorem. -/
structure PatternEmbedding {V : Type u} [DecidableEq V]
    (C : FiniteFaceComplex V) (N : WorldNetwork.{v}) [DecidableEq N.World] where
  toWorld : V → N.World
  injective : Function.Injective toWorld
  face_iff : ∀ s : Finset V,
    C.Face s ↔ N.JointAmalgamable (s.image toWorld)

/-- Every amalgamation nerve realizes itself exactly. -/
def identityPatternEmbedding (N : WorldNetwork.{u}) [DecidableEq N.World] :
    PatternEmbedding (amalgamationNerve N) N where
  toWorld := id
  injective := Function.injective_id
  face_iff := by
    intro s
    change N.JointAmalgamable s ↔ N.JointAmalgamable (s.image id)
    simp

end Komorebi.Multiverse
