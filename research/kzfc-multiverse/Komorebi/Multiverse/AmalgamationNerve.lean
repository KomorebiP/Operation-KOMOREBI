import Komorebi.Multiverse.WorldNetwork
import Mathlib.Data.Finset.Card

/-!
# The finite amalgamation nerve

The nerve records only which finite world families possess a common upper world.
It is deliberately representation-free: forcing, grounds, inner-model maps, or
other world notions enter only through the chosen `WorldNetwork.reach` relation.
-/

universe u

namespace Komorebi.Multiverse

/-- A downward-closed predicate on finite vertex sets.  We use this minimal
interface rather than importing topological machinery that the current proof
obligations do not need. -/
structure FiniteFaceComplex (V : Type u) where
  Face : Finset V → Prop
  downward : ∀ {s t : Finset V}, s ⊆ t → Face t → Face s

/-- The amalgamation nerve of a world network. -/
def amalgamationNerve (N : WorldNetwork.{u}) : FiniteFaceComplex N.World where
  Face := N.JointAmalgamable
  downward := fun hst ht => N.simplex_downward hst ht

namespace FiniteFaceComplex

variable {V : Type u} (C : FiniteFaceComplex V)

/-- A finite family is a minimal obstruction when it is not a face but every
proper subfamily is a face. -/
def MinimalNonface (s : Finset V) : Prop :=
  ¬ C.Face s ∧ ∀ t : Finset V, t ⊂ s → C.Face t

end FiniteFaceComplex


namespace WorldNetwork

variable (N : WorldNetwork.{u})

/-- On a nonempty world network, pairwise amalgamability already gives joint
amalgamability for families of cardinality at most two.  Thus the first genuinely
higher obstruction can only occur at three or more worlds. -/
theorem joint_of_pairwise_card_le_two [DecidableEq N.World]
    (base : N.World) {s : Finset N.World} (hp : N.PairwiseAmalgamable s) (hc : s.card ≤ 2) :
    N.JointAmalgamable s := by
  classical
  induction s using Finset.induction_on with
  | empty =>
      exact N.empty_joint base
  | @insert a s ha ih =>
      by_cases hs : s = ∅
      · subst s
        simpa using N.singleton_joint a
      · have hsne : s.Nonempty := Finset.nonempty_iff_ne_empty.mpr hs
        obtain ⟨b, hb⟩ := hsne
        have hcard_s : s.card ≤ 1 := by
          simpa [Finset.card_insert_of_notMem ha] using hc
        obtain ⟨apex, haa, hbb⟩ := hp a (Finset.mem_insert_self a s)
          b (Finset.mem_insert_of_mem hb)
        refine ⟨apex, ?_⟩
        intro w hw
        rcases Finset.mem_insert.mp hw with rfl | hw
        · exact haa
        · have hwb : w = b := (Finset.card_le_one.mp hcard_s) w hw b hb
          subst w
          exact hbb

end WorldNetwork

/-- In the amalgamation nerve, nonfaces are exactly world-amalgamation obstructions. -/
theorem not_face_iff_obstructed (N : WorldNetwork.{u}) (s : Finset N.World) :
    ¬ (amalgamationNerve N).Face s ↔ N.Obstructed s := Iff.rfl

end Komorebi.Multiverse
