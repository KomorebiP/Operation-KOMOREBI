import AVOC.ControlSufficiency
import Mathlib.Data.Finset.Max

namespace Komorebi.AVOC

universe u v w

/-- Deterministic finite-horizon control with state-dependent feasible actions. -/
structure StateControlSystem (S : Type u) (A : Type v) [DecidableEq A] where
  actions : S → Finset A
  actions_nonempty : ∀ s, (actions s).Nonempty
  transition : S → A → S
  reward : S → A → ℝ

/-- State-dependent finite-horizon value. -/
noncomputable def stateHorizonValue
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) : ℕ → S → ℝ
  | 0, _ => 0
  | n + 1, s =>
      let values := (sys.actions s).image
        (fun a => sys.reward s a + stateHorizonValue sys n (sys.transition s a))
      values.max' ((sys.actions_nonempty s).image _)

/-- Bellman action value in a state-dependent control system. -/
noncomputable def stateQValue
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) (s : S) (a : A) : ℝ :=
  sys.reward s a + stateHorizonValue sys n (sys.transition s a)

/-- State-dependent Bellman equation. -/
theorem stateHorizonValue_succ_eq_max
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) (s : S) :
    stateHorizonValue sys (n + 1) s =
      ((sys.actions s).image (stateQValue sys n s)).max'
        ((sys.actions_nonempty s).image _) := by
  rfl

/-- A maximizing feasible action exists at every state and finite horizon. -/
theorem state_bellman_action_exists
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) (s : S) :
    ∃ a ∈ sys.actions s, ∀ b ∈ sys.actions s,
      stateQValue sys n s b ≤ stateQValue sys n s a := by
  exact Finset.exists_max_image (sys.actions s) (stateQValue sys n s)
    (sys.actions_nonempty s)

/-- A maximizing state-dependent action realizes the horizon value. -/
theorem stateHorizonValue_eq_qValue_of_optimal
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) (s : S) (a : A)
    (ha : a ∈ sys.actions s)
    (hmax : ∀ b ∈ sys.actions s,
      stateQValue sys n s b ≤ stateQValue sys n s a) :
    stateHorizonValue sys (n + 1) s = stateQValue sys n s a := by
  rw [stateHorizonValue_succ_eq_max]
  apply (Finset.max'_eq_iff _ _ _).2
  constructor
  · exact Finset.mem_image.mpr ⟨a, ha, rfl⟩
  · intro y hy
    rcases Finset.mem_image.mp hy with ⟨b, hb, rfl⟩
    exact hmax b hb

/-- Every feasible action value lies below the next state-dependent horizon. -/
theorem stateQValue_le_horizonValue_succ
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) (s : S) (a : A)
    (ha : a ∈ sys.actions s) :
    stateQValue sys n s a ≤ stateHorizonValue sys (n + 1) s := by
  rw [stateHorizonValue_succ_eq_max]
  exact Finset.le_max' _ _ (Finset.mem_image.mpr ⟨a, ha, rfl⟩)

/-- Control sufficiency with state-dependent feasibility.  Two merged states
must expose exactly the same feasible actions; each such action must preserve
reward and projected transition behavior. -/
def StateControlSufficient
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) (φ : S → Z) : Prop :=
  ∀ ⦃s t : S⦄, φ s = φ t →
    sys.actions s = sys.actions t ∧
    ∀ a ∈ sys.actions s,
      sys.reward s a = sys.reward t a ∧
      φ (sys.transition s a) = φ (sys.transition t a)

/-- The identity representation is state-control-sufficient. -/
theorem stateControlSufficient_id
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) : StateControlSufficient sys id := by
  intro s t hst
  change s = t at hst
  subst t
  exact ⟨rfl, by intro a ha; exact ⟨rfl, rfl⟩⟩

/-- Feasible-action mismatch is itself a certificate of control insufficiency. -/
theorem action_mismatch_obstructs_stateControlSufficiency
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) {φ : S → Z}
    {s t : S} (hst : φ s = φ t)
    (hactions : sys.actions s ≠ sys.actions t) :
    ¬ StateControlSufficient sys φ := by
  intro h
  exact hactions (h hst).1

/-- Main state-dependent fiber theorem: preserving feasible actions, reward,
and projected transitions is sufficient to preserve exact finite-horizon value
inside each representation fiber. -/
theorem stateHorizonValue_eq_of_stateControlSufficient
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) {φ : S → Z}
    (hctrl : StateControlSufficient sys φ) (n : ℕ)
    {s t : S} (hst : φ s = φ t) :
    stateHorizonValue sys n s = stateHorizonValue sys n t := by
  induction n generalizing s t with
  | zero => rfl
  | succ n ih =>
      rcases hctrl hst with ⟨hactions, hlocal⟩
      have hq : ∀ a ∈ sys.actions s,
          stateQValue sys n s a = stateQValue sys n t a := by
        intro a ha
        rcases hlocal a ha with ⟨hr, hnext⟩
        unfold stateQValue
        rw [hr, ih hnext]
      apply le_antisymm
      · obtain ⟨a, ha, hmax⟩ := state_bellman_action_exists sys n s
        have hat : a ∈ sys.actions t := by simpa [hactions] using ha
        rw [stateHorizonValue_eq_qValue_of_optimal sys n s a ha hmax,
            hq a ha]
        exact stateQValue_le_horizonValue_succ sys n t a hat
      · obtain ⟨a, hat, hmax⟩ := state_bellman_action_exists sys n t
        have ha : a ∈ sys.actions s := by simpa [hactions] using hat
        rw [stateHorizonValue_eq_qValue_of_optimal sys n t a hat hmax,
            ← hq a ha]
        exact stateQValue_le_horizonValue_succ sys n s a ha

/-- State-dependent Bellman action optimality. -/
def StateBellmanOptimalAt
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) (s : S) (a : A) : Prop :=
  a ∈ sys.actions s ∧
    ∀ b ∈ sys.actions s, stateQValue sys n s b ≤ stateQValue sys n s a

/-- Optimal action sets are identical within every state-control-sufficient
fiber. -/
theorem stateBellmanOptimalAt_iff_of_stateControlSufficient
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) {φ : S → Z}
    (hctrl : StateControlSufficient sys φ) (n : ℕ)
    {s t : S} (hst : φ s = φ t) (a : A) :
    StateBellmanOptimalAt sys n s a ↔ StateBellmanOptimalAt sys n t a := by
  rcases hctrl hst with ⟨hactions, hlocal⟩
  have hq : ∀ b ∈ sys.actions s,
      stateQValue sys n s b = stateQValue sys n t b := by
    intro b hb
    rcases hlocal b hb with ⟨hr, hnext⟩
    unfold stateQValue
    rw [hr, stateHorizonValue_eq_of_stateControlSufficient sys hctrl n hnext]
  constructor
  · rintro ⟨ha, hmax⟩
    have hat : a ∈ sys.actions t := by simpa [hactions] using ha
    refine ⟨hat, ?_⟩
    intro b hbt
    have hb : b ∈ sys.actions s := by simpa [hactions] using hbt
    rw [← hq b hb, ← hq a ha]
    exact hmax b hb
  · rintro ⟨hat, hmax⟩
    have ha : a ∈ sys.actions s := by simpa [hactions] using hat
    refine ⟨ha, ?_⟩
    intro b hb
    have hbt : b ∈ sys.actions t := by simpa [hactions] using hb
    rw [hq b hb, hq a ha]
    exact hmax b hbt

/-- Quotient state-dependent control system induced by a surjective
state-control-sufficient representation. -/
noncomputable def quotientStateControlSystem
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) (φ : S → Z)
    (hsurj : Function.Surjective φ) : StateControlSystem Z A where
  actions z := sys.actions (controlSection φ hsurj z)
  actions_nonempty z := sys.actions_nonempty (controlSection φ hsurj z)
  transition z a := φ (sys.transition (controlSection φ hsurj z) a)
  reward z a := sys.reward (controlSection φ hsurj z) a

/-- Feasible actions of the quotient agree exactly with feasible raw actions
at every reachable quotient state. -/
theorem quotientStateControlSystem_actions_eq
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) (φ : S → Z)
    (hctrl : StateControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (s : S) :
    (quotientStateControlSystem sys φ hsurj).actions (φ s) = sys.actions s := by
  change sys.actions (controlSection φ hsurj (φ s)) = sys.actions s
  exact (hctrl (controlSection_spec φ hsurj (φ s))).1

/-- Quotient reward agrees with raw reward for every feasible raw action. -/
theorem quotientStateControlSystem_reward_eq
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) (φ : S → Z)
    (hctrl : StateControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (s : S) (a : A) (ha : a ∈ sys.actions s) :
    (quotientStateControlSystem sys φ hsurj).reward (φ s) a = sys.reward s a := by
  change sys.reward (controlSection φ hsurj (φ s)) a = sys.reward s a
  have hrep := hctrl (controlSection_spec φ hsurj (φ s))
  have haRep : a ∈ sys.actions (controlSection φ hsurj (φ s)) := by
    rw [hrep.1]
    exact ha
  exact (hrep.2 a haRep).1

/-- Quotient transition agrees with projection of the raw transition for every
feasible action. -/
theorem quotientStateControlSystem_transition_eq
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) (φ : S → Z)
    (hctrl : StateControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (s : S) (a : A) (ha : a ∈ sys.actions s) :
    (quotientStateControlSystem sys φ hsurj).transition (φ s) a =
      φ (sys.transition s a) := by
  change φ (sys.transition (controlSection φ hsurj (φ s)) a) =
    φ (sys.transition s a)
  have hrep := hctrl (controlSection_spec φ hsurj (φ s))
  have haRep : a ∈ sys.actions (controlSection φ hsurj (φ s)) := by
    rw [hrep.1]
    exact ha
  exact (hrep.2 a haRep).2

/-- Strong state-dependent quotient theorem: exact feasibility-preserving
control compression preserves finite-horizon optimal value. -/
theorem quotientStateControlSystem_horizonValue_eq
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) (φ : S → Z)
    (hctrl : StateControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (n : ℕ) (s : S) :
    stateHorizonValue (quotientStateControlSystem sys φ hsurj) n (φ s) =
      stateHorizonValue sys n s := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
      let qsys := quotientStateControlSystem sys φ hsurj
      have hactions : qsys.actions (φ s) = sys.actions s :=
        quotientStateControlSystem_actions_eq sys φ hctrl hsurj s
      have hq : ∀ a ∈ sys.actions s,
          stateQValue qsys n (φ s) a = stateQValue sys n s a := by
        intro a ha
        unfold stateQValue
        rw [quotientStateControlSystem_reward_eq sys φ hctrl hsurj s a ha,
            quotientStateControlSystem_transition_eq sys φ hctrl hsurj s a ha,
            ih (sys.transition s a)]
      apply le_antisymm
      · obtain ⟨a, haQ, hmax⟩ := state_bellman_action_exists qsys n (φ s)
        have ha : a ∈ sys.actions s := by simpa [hactions] using haQ
        rw [stateHorizonValue_eq_qValue_of_optimal qsys n (φ s) a haQ hmax,
            hq a ha]
        exact stateQValue_le_horizonValue_succ sys n s a ha
      · obtain ⟨a, ha, hmax⟩ := state_bellman_action_exists sys n s
        have haQ : a ∈ qsys.actions (φ s) := by simpa [hactions] using ha
        rw [stateHorizonValue_eq_qValue_of_optimal sys n s a ha hmax,
            ← hq a ha]
        exact stateQValue_le_horizonValue_succ qsys n (φ s) a haQ

end Komorebi.AVOC
