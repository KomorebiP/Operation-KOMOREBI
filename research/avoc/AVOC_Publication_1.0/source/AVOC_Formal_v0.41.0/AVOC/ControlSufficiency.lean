import AVOC.Dynamic

namespace Komorebi.AVOC

universe u v w

/-- A representation is control-sufficient for a deterministic finite control
system when states merged by the representation have identical one-step reward
and transition to states that remain merged, for every admissible action.  Since
`FiniteControlSystem` has one global finite action set, action feasibility is
already identical on every state. -/
def ControlSufficient
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z) : Prop :=
  ∀ ⦃s t : S⦄, φ s = φ t → ∀ a ∈ sys.actions,
    sys.reward s a = sys.reward t a ∧
      φ (sys.transition s a) = φ (sys.transition t a)

/-- The identity representation is control-sufficient. -/
theorem controlSufficient_id
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : FiniteControlSystem S A) :
    ControlSufficient sys id := by
  intro s t hst a ha
  change s = t at hst
  subst t
  exact ⟨rfl, rfl⟩

/-- Reward consistency is inherited by a finer representation, but projected
transition consistency need not be.  This helper isolates the inherited half
of control sufficiency and makes the non-monotonicity boundary explicit. -/
theorem reward_eq_of_refines_controlSufficient
    {S : Type u} {A : Type v} [DecidableEq A]
    {Fine : Type w} {Coarse : Type*}
    (sys : FiniteControlSystem S A)
    {fine : S → Fine} {coarse : S → Coarse}
    (href : Refines fine coarse)
    (hcoarse : ControlSufficient sys coarse)
    {s t : S} (hst : fine s = fine t) (a : A) (ha : a ∈ sys.actions) :
    sys.reward s a = sys.reward t a := by
  rcases href with ⟨decode, hdecode⟩
  have hcoarseFiber : coarse s = coarse t := by
    calc
      coarse s = decode (fine s) := (hdecode s).symm
      _ = decode (fine t) := congrArg decode hst
      _ = coarse t := hdecode t
  exact (hcoarse hcoarseFiber a ha).1


/-- Reward stability on representation fibers. -/
def RewardStable
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z) : Prop :=
  ∀ ⦃s t : S⦄, φ s = φ t → ∀ a ∈ sys.actions,
    sys.reward s a = sys.reward t a

/-- Dynamic closure of a representation under the controlled transition map. -/
def TransitionClosed
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z) : Prop :=
  ∀ ⦃s t : S⦄, φ s = φ t → ∀ a ∈ sys.actions,
    φ (sys.transition s a) = φ (sys.transition t a)

/-- Control sufficiency decomposes exactly into reward stability and transition
closure. -/
theorem controlSufficient_iff_rewardStable_and_transitionClosed
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z) :
    ControlSufficient sys φ ↔ RewardStable sys φ ∧ TransitionClosed sys φ := by
  constructor
  · intro h
    refine ⟨?_, ?_⟩
    · intro s t hst a ha
      exact (h hst a ha).1
    · intro s t hst a ha
      exact (h hst a ha).2
  · rintro ⟨hr, ht⟩ s t hst a ha
    exact ⟨hr hst a ha, ht hst a ha⟩

/-- Exact repair of the false refinement-monotonicity claim: a refinement of a
control-sufficient representation remains control-sufficient whenever the finer
representation is dynamically closed. Reward stability is inherited from the
coarser sufficient representation. -/
theorem controlSufficient_of_refines_and_transitionClosed
    {S : Type u} {A : Type v} [DecidableEq A]
    {Fine : Type w} {Coarse : Type*}
    (sys : FiniteControlSystem S A)
    {fine : S → Fine} {coarse : S → Coarse}
    (href : Refines fine coarse)
    (hcoarse : ControlSufficient sys coarse)
    (hclosed : TransitionClosed sys fine) :
    ControlSufficient sys fine := by
  rw [controlSufficient_iff_rewardStable_and_transitionClosed]
  refine ⟨?_, hclosed⟩
  intro s t hst a ha
  exact reward_eq_of_refines_controlSufficient sys href hcoarse hst a ha

/-- A reward mismatch inside one representation fiber is a certificate that the
representation is not control-sufficient. -/
theorem reward_mismatch_obstructs_controlSufficiency
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) {φ : S → Z}
    {s t : S} (hst : φ s = φ t) {a : A} (ha : a ∈ sys.actions)
    (hr : sys.reward s a ≠ sys.reward t a) :
    ¬ ControlSufficient sys φ := by
  intro h
  exact hr (h hst a ha).1

/-- A projected-transition mismatch inside one representation fiber is likewise
a certificate of control insufficiency. -/
theorem transition_mismatch_obstructs_controlSufficiency
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) {φ : S → Z}
    {s t : S} (hst : φ s = φ t) {a : A} (ha : a ∈ sys.actions)
    (hnext : φ (sys.transition s a) ≠ φ (sys.transition t a)) :
    ¬ ControlSufficient sys φ := by
  intro h
  exact hnext (h hst a ha).2

/-- Bellman action optimality at a state with `n` continuation steps. -/
def BellmanOptimalAt
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) (a : A) : Prop :=
  a ∈ sys.actions ∧ ∀ b ∈ sys.actions, qValue sys n s b ≤ qValue sys n s a

/-- A fixed Bellman-optimal action exists at every finite-horizon state. -/
theorem bellmanOptimalAt_exists
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) :
    ∃ a, BellmanOptimalAt sys n s a := by
  obtain ⟨a, ha, hmax⟩ := bellman_action_exists sys n s
  exact ⟨a, ha, hmax⟩

/-- Every admissible Bellman action value lies below the next-horizon value. -/
theorem qValue_le_horizonValue_succ
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) (a : A)
    (ha : a ∈ sys.actions) :
    qValue sys n s a ≤ horizonValue sys (n + 1) s := by
  rw [horizonValue_succ_eq_max]
  exact Finset.le_max' _ _ (Finset.mem_image.mpr ⟨a, ha, rfl⟩)

/-- Main intrinsic control-sufficiency theorem: finite-horizon optimal value is
constant on every fiber of a control-sufficient representation. -/
theorem horizonValue_eq_of_controlSufficient
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) {φ : S → Z}
    (hctrl : ControlSufficient sys φ) (n : ℕ)
    {s t : S} (hst : φ s = φ t) :
    horizonValue sys n s = horizonValue sys n t := by
  induction n generalizing s t with
  | zero => rfl
  | succ n ih =>
      have hq : ∀ a ∈ sys.actions, qValue sys n s a = qValue sys n t a := by
        intro a ha
        rcases hctrl hst a ha with ⟨hr, hnext⟩
        unfold qValue
        rw [hr, ih hnext]
      apply le_antisymm
      · obtain ⟨a, ha, hmax⟩ := bellman_action_exists sys n s
        rw [horizonValue_eq_qValue_of_optimal sys n s a ha hmax, hq a ha]
        exact qValue_le_horizonValue_succ sys n t a ha
      · obtain ⟨a, ha, hmax⟩ := bellman_action_exists sys n t
        rw [horizonValue_eq_qValue_of_optimal sys n t a ha hmax, ← hq a ha]
        exact qValue_le_horizonValue_succ sys n s a ha

/-- Bellman action values are also constant on control-sufficient fibers. -/
theorem qValue_eq_of_controlSufficient
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) {φ : S → Z}
    (hctrl : ControlSufficient sys φ) (n : ℕ)
    {s t : S} (hst : φ s = φ t) (a : A) (ha : a ∈ sys.actions) :
    qValue sys n s a = qValue sys n t a := by
  rcases hctrl hst a ha with ⟨hr, hnext⟩
  unfold qValue
  rw [hr, horizonValue_eq_of_controlSufficient sys hctrl n hnext]

/-- Optimal action sets are identical within every control-sufficient fiber. -/
theorem bellmanOptimalAt_iff_of_controlSufficient
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) {φ : S → Z}
    (hctrl : ControlSufficient sys φ) (n : ℕ)
    {s t : S} (hst : φ s = φ t) (a : A) :
    BellmanOptimalAt sys n s a ↔ BellmanOptimalAt sys n t a := by
  constructor
  · rintro ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro b hb
    rw [← qValue_eq_of_controlSufficient sys hctrl n hst b hb,
        ← qValue_eq_of_controlSufficient sys hctrl n hst a ha]
    exact hmax b hb
  · rintro ⟨ha, hmax⟩
    refine ⟨ha, ?_⟩
    intro b hb
    rw [qValue_eq_of_controlSufficient sys hctrl n hst b hb,
        qValue_eq_of_controlSufficient sys hctrl n hst a ha]
    exact hmax b hb

/-- A canonical noncomputable Bellman choice, used only to prove existence of a
policy that factors through a sufficient representation. -/
noncomputable def bellmanChoice
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) : A :=
  Classical.choose (bellmanOptimalAt_exists sys n s)

/-- The canonical Bellman choice is optimal. -/
theorem bellmanChoice_optimal
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : FiniteControlSystem S A) (n : ℕ) (s : S) :
    BellmanOptimalAt sys n s (bellmanChoice sys n s) := by
  exact Classical.choose_spec (bellmanOptimalAt_exists sys n s)

/-- Control sufficiency implies existence of an optimal finite-horizon policy
that depends only on the compressed representation.  Unreachable representation
values may be assigned arbitrarily; every reachable value receives an action
optimal for every raw state in that fiber. -/
theorem quotient_factored_optimal_policy_exists
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z)
    (hctrl : ControlSufficient sys φ) (n : ℕ) :
    ∃ policy : Z → A, ∀ s : S,
      BellmanOptimalAt sys n s (policy (φ s)) := by
  classical
  let default : A := Classical.choose sys.actions_nonempty
  let policy : Z → A := fun z =>
    if hz : ∃ s : S, φ s = z then
      bellmanChoice sys n (Classical.choose hz)
    else default
  refine ⟨policy, ?_⟩
  intro s
  have hz : ∃ t : S, φ t = φ s := ⟨s, rfl⟩
  have hrep : φ (Classical.choose hz) = φ s := Classical.choose_spec hz
  have hopt : BellmanOptimalAt sys n (Classical.choose hz)
      (bellmanChoice sys n (Classical.choose hz)) :=
    bellmanChoice_optimal sys n (Classical.choose hz)
  have htransport : BellmanOptimalAt sys n s
      (bellmanChoice sys n (Classical.choose hz)) :=
    (bellmanOptimalAt_iff_of_controlSufficient sys hctrl n hrep
      (bellmanChoice sys n (Classical.choose hz))).1 hopt
  simpa only [policy, dite_eq_left hz] using htransport

/-- Choose one raw representative for every quotient state of a surjective
representation. -/
noncomputable def controlSection
    {S : Type u} {Z : Type w} (φ : S → Z) (hsurj : Function.Surjective φ) : Z → S :=
  fun z => Classical.choose (hsurj z)

/-- The chosen representative maps back to its quotient state. -/
theorem controlSection_spec
    {S : Type u} {Z : Type w} (φ : S → Z) (hsurj : Function.Surjective φ) (z : Z) :
    φ (controlSection φ hsurj z) = z := by
  exact Classical.choose_spec (hsurj z)

/-- Quotient control system induced by a surjective control-sufficient
representation.  Reward and transition are read from an arbitrary representative;
control sufficiency guarantees that this choice is behaviorally sound. -/
noncomputable def quotientControlSystem
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z)
    (hsurj : Function.Surjective φ) : FiniteControlSystem Z A where
  actions := sys.actions
  actions_nonempty := sys.actions_nonempty
  transition z a := φ (sys.transition (controlSection φ hsurj z) a)
  reward z a := sys.reward (controlSection φ hsurj z) a

/-- Quotient reward agrees with raw reward on every reachable quotient state. -/
theorem quotientControlSystem_reward_eq
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z)
    (hctrl : ControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (s : S) (a : A) (ha : a ∈ sys.actions) :
    (quotientControlSystem sys φ hsurj).reward (φ s) a = sys.reward s a := by
  change sys.reward (controlSection φ hsurj (φ s)) a = sys.reward s a
  exact (hctrl (controlSection_spec φ hsurj (φ s)) a ha).1

/-- Quotient transition agrees with projection of the raw transition. -/
theorem quotientControlSystem_transition_eq
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z)
    (hctrl : ControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (s : S) (a : A) (ha : a ∈ sys.actions) :
    (quotientControlSystem sys φ hsurj).transition (φ s) a =
      φ (sys.transition s a) := by
  change φ (sys.transition (controlSection φ hsurj (φ s)) a) =
    φ (sys.transition s a)
  exact (hctrl (controlSection_spec φ hsurj (φ s)) a ha).2

/-- Quotient Bellman action value agrees with the raw action value. -/
theorem quotientControlSystem_qValue_eq
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z)
    (hctrl : ControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (n : ℕ) (s : S) (a : A) (ha : a ∈ sys.actions)
    (ih : horizonValue (quotientControlSystem sys φ hsurj) n
            (φ (sys.transition s a)) =
          horizonValue sys n (sys.transition s a)) :
    qValue (quotientControlSystem sys φ hsurj) n (φ s) a =
      qValue sys n s a := by
  unfold qValue
  rw [quotientControlSystem_reward_eq sys φ hctrl hsurj s a ha,
      quotientControlSystem_transition_eq sys φ hctrl hsurj s a ha,
      ih]

/-- Strong quotient theorem: a surjective control-sufficient compression
preserves the exact finite-horizon optimal value. -/
theorem quotientControlSystem_horizonValue_eq
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z)
    (hctrl : ControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (n : ℕ) (s : S) :
    horizonValue (quotientControlSystem sys φ hsurj) n (φ s) =
      horizonValue sys n s := by
  induction n generalizing s with
  | zero => rfl
  | succ n ih =>
      let qsys := quotientControlSystem sys φ hsurj
      have hq : ∀ a ∈ sys.actions,
          qValue qsys n (φ s) a = qValue sys n s a := by
        intro a ha
        exact quotientControlSystem_qValue_eq sys φ hctrl hsurj n s a ha
          (ih (sys.transition s a))
      apply le_antisymm
      · obtain ⟨a, ha, hmax⟩ := bellman_action_exists qsys n (φ s)
        have haRaw : a ∈ sys.actions := by
          change a ∈ sys.actions at ha
          exact ha
        rw [horizonValue_eq_qValue_of_optimal qsys n (φ s) a ha hmax,
            hq a haRaw]
        exact qValue_le_horizonValue_succ sys n s a haRaw
      · obtain ⟨a, ha, hmax⟩ := bellman_action_exists sys n s
        have haQ : a ∈ qsys.actions := by
          change a ∈ sys.actions
          exact ha
        rw [horizonValue_eq_qValue_of_optimal sys n s a ha hmax,
            ← hq a ha]
        exact qValue_le_horizonValue_succ qsys n (φ s) a haQ

/-- A Bellman-optimal quotient action is Bellman-optimal in every raw state
that projects to the quotient state. -/
theorem quotient_optimal_action_lifts
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z)
    (hctrl : ControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (n : ℕ) (s : S) (a : A)
    (hopt : BellmanOptimalAt (quotientControlSystem sys φ hsurj) n (φ s) a) :
    BellmanOptimalAt sys n s a := by
  rcases hopt with ⟨haQ, hmax⟩
  let qsys := quotientControlSystem sys φ hsurj
  have ha : a ∈ sys.actions := by
    change a ∈ sys.actions at haQ
    exact haQ
  refine ⟨ha, ?_⟩
  intro b hb
  have hbQ : b ∈ qsys.actions := by
    change b ∈ sys.actions
    exact hb
  have hqa := quotientControlSystem_qValue_eq sys φ hctrl hsurj n s a ha
    (quotientControlSystem_horizonValue_eq sys φ hctrl hsurj n (sys.transition s a))
  have hqb := quotientControlSystem_qValue_eq sys φ hctrl hsurj n s b hb
    (quotientControlSystem_horizonValue_eq sys φ hctrl hsurj n (sys.transition s b))
  rw [← hqb, ← hqa]
  exact hmax b hbQ


/-- Exact action-level quotient theorem: an action is Bellman-optimal at a
reachable quotient state iff it is Bellman-optimal at the corresponding raw
state. -/
theorem quotient_bellmanOptimalAt_iff
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : FiniteControlSystem S A) (φ : S → Z)
    (hctrl : ControlSufficient sys φ) (hsurj : Function.Surjective φ)
    (n : ℕ) (s : S) (a : A) :
    BellmanOptimalAt (quotientControlSystem sys φ hsurj) n (φ s) a ↔
      BellmanOptimalAt sys n s a := by
  constructor
  · exact quotient_optimal_action_lifts sys φ hctrl hsurj n s a
  · intro hopt
    rcases hopt with ⟨ha, hmax⟩
    let qsys := quotientControlSystem sys φ hsurj
    have haQ : a ∈ qsys.actions := by
      change a ∈ sys.actions
      exact ha
    refine ⟨haQ, ?_⟩
    intro b hbQ
    have hb : b ∈ sys.actions := by
      change b ∈ sys.actions at hbQ
      exact hbQ
    have hqa := quotientControlSystem_qValue_eq sys φ hctrl hsurj n s a ha
      (quotientControlSystem_horizonValue_eq sys φ hctrl hsurj n (sys.transition s a))
    have hqb := quotientControlSystem_qValue_eq sys φ hctrl hsurj n s b hb
      (quotientControlSystem_horizonValue_eq sys φ hctrl hsurj n (sys.transition s b))
    rw [hqb, hqa]
    exact hmax b hb

end Komorebi.AVOC
