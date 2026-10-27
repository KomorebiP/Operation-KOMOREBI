import AVOC.StateDependentControl

namespace Komorebi.AVOC

universe u v w

/-- Behavioral equivalence up to a finite decision horizon.  At horizon zero no
future reward is observed.  At horizon `n+1`, equivalent states must expose the
same feasible actions, agree on immediate reward, and send every feasible action
to states equivalent for the remaining `n` steps. -/
def HorizonEquivalent
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) : ℕ → S → S → Prop
  | 0, _, _ => True
  | n + 1, s, t =>
      sys.actions s = sys.actions t ∧
      ∀ a ∈ sys.actions s,
        sys.reward s a = sys.reward t a ∧
        HorizonEquivalent sys n (sys.transition s a) (sys.transition t a)

/-- Horizon equivalence is reflexive. -/
theorem horizonEquivalent_refl
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) (s : S) :
    HorizonEquivalent sys n s s := by
  induction n generalizing s with
  | zero => trivial
  | succ n ih =>
      refine ⟨rfl, ?_⟩
      intro a ha
      exact ⟨rfl, ih (sys.transition s a)⟩

/-- Horizon equivalence is symmetric. -/
theorem horizonEquivalent_symm
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) {s t : S}
    (h : HorizonEquivalent sys n s t) : HorizonEquivalent sys n t s := by
  induction n generalizing s t with
  | zero => trivial
  | succ n ih =>
      rcases h with ⟨hactions, hlocal⟩
      refine ⟨hactions.symm, ?_⟩
      intro a hat
      have has : a ∈ sys.actions s := by simpa [hactions] using hat
      rcases hlocal a has with ⟨hr, hnext⟩
      exact ⟨hr.symm, ih hnext⟩

/-- Horizon equivalence is transitive. -/
theorem horizonEquivalent_trans
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) {s t r : S}
    (hst : HorizonEquivalent sys n s t)
    (htr : HorizonEquivalent sys n t r) :
    HorizonEquivalent sys n s r := by
  induction n generalizing s t r with
  | zero => trivial
  | succ n ih =>
      rcases hst with ⟨hactST, hlocalST⟩
      rcases htr with ⟨hactTR, hlocalTR⟩
      refine ⟨hactST.trans hactTR, ?_⟩
      intro a has
      have hat : a ∈ sys.actions t := by simpa [hactST] using has
      rcases hlocalST a has with ⟨hrST, hnST⟩
      rcases hlocalTR a hat with ⟨hrTR, hnTR⟩
      exact ⟨hrST.trans hrTR, ih hnST hnTR⟩

/-- Hence finite-horizon behavioral equivalence defines a setoid. -/
def horizonSetoid
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) : Setoid S where
  r := HorizonEquivalent sys n
  iseqv := ⟨horizonEquivalent_refl sys n,
    horizonEquivalent_symm sys n,
    horizonEquivalent_trans sys n⟩

/-- Longer-horizon behavioral equivalence implies shorter-horizon equivalence. -/
theorem horizonEquivalent_of_succ
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) {s t : S}
    (h : HorizonEquivalent sys (n + 1) s t) :
    HorizonEquivalent sys n s t := by
  induction n generalizing s t with
  | zero => trivial
  | succ n ih =>
      rcases h with ⟨hactions, hlocal⟩
      refine ⟨hactions, ?_⟩
      intro a ha
      rcases hlocal a ha with ⟨hr, hn⟩
      exact ⟨hr, ih hn⟩

/-- If two states are behaviorally equivalent for horizon `n`, they have exactly
the same optimal finite-horizon value for those `n` decisions. -/
theorem horizonEquivalent_preserves_value
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) {s t : S}
    (h : HorizonEquivalent sys n s t) :
    stateHorizonValue sys n s = stateHorizonValue sys n t := by
  induction n generalizing s t with
  | zero => rfl
  | succ n ih =>
      rcases h with ⟨hactions, hlocal⟩
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

/-- A representation is sufficient for exactly `n` future decisions when every
representation fiber lies inside one `n`-horizon behavioral equivalence class. -/
def HorizonControlSufficient
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) (φ : S → Z) (n : ℕ) : Prop :=
  ∀ ⦃s t : S⦄, φ s = φ t → HorizonEquivalent sys n s t

/-- Horizon-control sufficiency weakens monotonically when the requested horizon
shrinks. -/
theorem horizonControlSufficient_of_succ
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) {φ : S → Z} (n : ℕ)
    (h : HorizonControlSufficient sys φ (n + 1)) :
    HorizonControlSufficient sys φ n := by
  intro s t hst
  exact horizonEquivalent_of_succ sys n (h hst)

/-- Any horizon-control-sufficient representation preserves value on its fibers. -/
theorem horizonControlSufficient_preserves_value
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) {φ : S → Z} (n : ℕ)
    (h : HorizonControlSufficient sys φ n)
    {s t : S} (hst : φ s = φ t) :
    stateHorizonValue sys n s = stateHorizonValue sys n t := by
  exact horizonEquivalent_preserves_value sys n (h hst)

/-- Full state-control sufficiency implies sufficiency for every finite horizon. -/
theorem stateControlSufficient_implies_all_horizons
    {S : Type u} {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) {φ : S → Z}
    (hctrl : StateControlSufficient sys φ) :
    ∀ n, HorizonControlSufficient sys φ n := by
  intro n
  induction n with
  | zero =>
      intro s t hst
      trivial
  | succ n ih =>
      intro s t hst
      rcases hctrl hst with ⟨hactions, hlocal⟩
      refine ⟨hactions, ?_⟩
      intro a ha
      rcases hlocal a ha with ⟨hr, hnext⟩
      exact ⟨hr, ih hnext⟩

/-- Canonical quotient map by `n`-horizon behavioral equivalence. -/
def horizonQuotientMap
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) :
    S → Quotient (horizonSetoid sys n) :=
  fun s => Quotient.mk _ s

/-- The canonical behavioral quotient is itself sufficient for horizon `n`. -/
theorem horizonQuotient_is_sufficient
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) :
    HorizonControlSufficient sys (horizonQuotientMap sys n) n := by
  intro s t hst
  exact Quotient.exact hst

/-- Forget one step of behavioral resolution: an `(n+1)`-horizon class maps
canonically to its `n`-horizon class.  Well-definedness is exactly the theorem
that longer-horizon equivalence implies shorter-horizon equivalence. -/
def horizonForget
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) :
    Quotient (horizonSetoid sys (n + 1)) → Quotient (horizonSetoid sys n) :=
  Quotient.lift (horizonQuotientMap sys n) (by
    intro s t hst
    exact Quotient.sound (horizonEquivalent_of_succ sys n hst))

/-- The forgetful map commutes with the canonical quotient maps. -/
theorem horizonForget_comp_quotientMap
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) (s : S) :
    horizonForget sys n (horizonQuotientMap sys (n + 1) s) =
      horizonQuotientMap sys n s := by
  rfl

/-- The canonical `(n+1)`-horizon quotient refines the canonical `n`-horizon
quotient.  Longer planning horizons can therefore require distinctions that are
provably unnecessary at shorter horizons, but never the reverse. -/
theorem horizonQuotient_refines_previous
    {S : Type u} {A : Type v} [DecidableEq A]
    (sys : StateControlSystem S A) (n : ℕ) :
    Refines (horizonQuotientMap sys (n + 1)) (horizonQuotientMap sys n) := by
  refine ⟨horizonForget sys n, ?_⟩
  intro s
  rfl


/-- Canonical minimality theorem: every `n`-horizon sufficient encoding refines
the behavioral quotient.  Thus the quotient is the coarsest exact finite-horizon
control representation, up to encoding equivalence. -/
theorem horizonQuotient_is_coarsest
    {S : Type u} [Nonempty S] {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) (n : ℕ) {φ : S → Z}
    (h : HorizonControlSufficient sys φ n) :
    Refines φ (horizonQuotientMap sys n) := by
  classical
  let s₀ : S := Classical.choice (inferInstance : Nonempty S)
  let decode : Z → Quotient (horizonSetoid sys n) := fun z =>
    if hz : ∃ s : S, φ s = z then
      Quotient.mk _ (Classical.choose hz)
    else Quotient.mk _ s₀
  refine ⟨decode, ?_⟩
  intro s
  have hz : ∃ t : S, φ t = φ s := ⟨s, rfl⟩
  simp only [decode, dite_eq_left hz, horizonQuotientMap]
  exact Quotient.sound (h (Classical.choose_spec hz))

/-- The canonical quotient is horizon-control-minimal: it is sufficient and is
refined by every other sufficient representation. -/
theorem horizonQuotient_minimal_characterization
    {S : Type u} [Nonempty S] {A : Type v} [DecidableEq A] {Z : Type w}
    (sys : StateControlSystem S A) (n : ℕ) {φ : S → Z}
    (hφ : HorizonControlSufficient sys φ n) :
    Refines φ (horizonQuotientMap sys n) :=
  horizonQuotient_is_coarsest sys n hφ

end Komorebi.AVOC
