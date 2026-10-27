import Komorebi.Multiverse.TransportResidual

/-!
# Abstract world-residual descent and a nontriviality audit

A bare obstruction tower is too weak as a foundational notion: every failure can
be packed into degree zero.  This module formalizes that fact.  Any future
Komorebi multiverse axiom therefore has to constrain how the obstruction tower
is produced (for example by locality, naturality, or a derived construction).
-/

universe u v

namespace Komorebi.Multiverse
namespace TransportSystem

variable {N : WorldNetwork.{u}} (F : TransportSystem.{u,v} N)

/-- A graded family of obstruction predicates, required only to be sound: a
jointly glued datum cannot carry an obstruction. -/
structure ObstructionTheory where
  Obstruction : ∀ {s : Finset N.World}, Nat → F.LocalFamily s → Prop
  sound : ∀ {s : Finset N.World} (x : F.LocalFamily s) (q : Nat),
    F.JointCompatible x → ¬ Obstruction q x

namespace ObstructionTheory

variable {F : TransportSystem.{u,v} N} (R : F.ObstructionTheory)

/-- All graded residual obstructions vanish on this local datum. -/
def AllVanish {s : Finset N.World} (x : F.LocalFamily s) : Prop :=
  ∀ q : Nat, ¬ R.Obstruction q x

/-- Completeness means every failure of joint gluing is detected at some degree. -/
def Complete : Prop :=
  ∀ {s : Finset N.World} (x : F.LocalFamily s),
    ¬ F.JointCompatible x → ∃ q : Nat, R.Obstruction q x

/-- Soundness alone gives the easy direction of residual descent. -/
theorem allVanish_of_joint {s : Finset N.World} {x : F.LocalFamily s}
    (h : F.JointCompatible x) : R.AllVanish x := by
  intro q hq
  exact R.sound x q h hq

/-- Soundness plus completeness gives the exact descent criterion. -/
theorem joint_iff_allVanish (hcomplete : R.Complete)
    {s : Finset N.World} (x : F.LocalFamily s) :
    F.JointCompatible x ↔ R.AllVanish x := by
  constructor
  · exact R.allVanish_of_joint
  · intro hv
    by_contra hn
    obtain ⟨q, hq⟩ := hcomplete x hn
    exact hv q hq

end ObstructionTheory

/-- The degenerate degree-zero theory.  It proves that existence of some complete
obstruction tower is not by itself a substantive axiom. -/
def packedFailureTheory : F.ObstructionTheory where
  Obstruction := fun q x => q = 0 ∧ ¬ F.JointCompatible x
  sound := by
    intro s x q hj hq
    exact hq.2 hj

/-- The packed degree-zero theory is always complete. -/
theorem packedFailureTheory_complete : F.packedFailureTheory.Complete := by
  intro s x hn
  exact ⟨0, rfl, hn⟩

/-- A genuinely higher, but generally incomplete, detector: degree one records
pairwise-compatible failure of global gluing. -/
def pairwiseBoundaryTheory : F.ObstructionTheory where
  Obstruction := fun q x => q = 1 ∧ F.HigherDataObstruction x
  sound := by
    intro s x q hj hq
    exact hq.2.2 hj

/-- Degree-one detection is exactly the previously defined higher data obstruction. -/
theorem pairwiseBoundaryTheory_degree_one {s : Finset N.World} (x : F.LocalFamily s) :
    F.pairwiseBoundaryTheory.Obstruction 1 x ↔ F.HigherDataObstruction x := by
  simp [pairwiseBoundaryTheory]

end TransportSystem
end Komorebi.Multiverse
