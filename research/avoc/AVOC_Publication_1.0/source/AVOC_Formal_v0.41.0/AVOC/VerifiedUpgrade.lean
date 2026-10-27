import Std

namespace Komorebi.AVOC.Upgrade

/-- Protected evaluation authority. Utility, bounds and prices refer to one fixed
workload, objective and unit convention. Bounds and check soundness are obligations,
not consequences of receiving a JSON score or an approval flag. -/
structure Authority (V : Type) where
  core : String
  objective : String
  Contract : V → Prop
  check : V → Bool
  check_sound : ∀ v, check v = true → Contract v
  utility : V → Int
  lower : V → Int
  upper : V → Int
  bounds_sound : ∀ v, lower v ≤ utility v ∧ utility v ≤ upper v
  evaluationCost : V → Nat
  switchCost : V → V → Nat
  credits : Nat
  margin : Nat
  margin_pos : 0 < margin

structure State (V : Type) where
  initial : V
  active : V
  revision : Nat
  trials : Nat
  evaluationSpent : Nat
  switchSpent : Nat
  guaranteedGain : Nat
  deriving Repr, DecidableEq

structure Proposal (V : Type) where
  parent : V
  revision : Nat
  candidate : V
  core : String
  objective : String
  deriving Repr, DecidableEq

inductive Outcome where
  | unfunded | rejected | promoted
  deriving Repr, DecidableEq

structure Result (V : Type) where
  next : State V
  outcome : Outcome
  evaluationDebit : Nat
  switchDebit : Nat
  deriving Repr, DecidableEq

def initial (v : V) : State V := ⟨v, v, 0, 0, 0, 0, 0⟩

def Safe (a : Authority V) (s : State V) : Prop :=
  a.Contract s.active ∧
  s.evaluationSpent + s.switchSpent ≤ a.credits ∧
  a.utility s.initial + (s.switchSpent : Int) + (s.guaranteedGain : Int) ≤
    a.utility s.active ∧
  s.guaranteedGain = s.revision * a.margin ∧
  s.revision ≤ s.trials

def Funded (a : Authority V) (s : State V) (p : Proposal V) : Prop :=
  s.evaluationSpent + a.evaluationCost p.candidate + s.switchSpent ≤ a.credits

instance (a : Authority V) (s : State V) (p : Proposal V) :
    Decidable (Funded a s p) := inferInstanceAs (Decidable (_ ≤ _))

def Eligible [DecidableEq V] (a : Authority V) (s : State V) (p : Proposal V) : Prop :=
  p.parent = s.active ∧ p.revision = s.revision ∧ p.core = a.core ∧
  p.objective = a.objective ∧ a.check p.candidate = true ∧
  a.upper s.active + (a.switchCost s.active p.candidate : Int) + (a.margin : Int) ≤
    a.lower p.candidate ∧
  s.evaluationSpent + a.evaluationCost p.candidate + s.switchSpent +
    a.switchCost s.active p.candidate ≤ a.credits

instance [DecidableEq V] (a : Authority V) (s : State V) (p : Proposal V) :
    Decidable (Eligible a s p) := by unfold Eligible; infer_instance

/-- Every funded trial is charged, including stale, uncertified and unprofitable
proposals. No cost or checker/objective override is accepted from a proposal. -/
def step [DecidableEq V] (a : Authority V) (s : State V) (p : Proposal V) : Result V :=
  if Funded a s p then
    if Eligible a s p then
      ⟨{s with
          active := p.candidate
          revision := s.revision + 1
          trials := s.trials + 1
          evaluationSpent := s.evaluationSpent + a.evaluationCost p.candidate
          switchSpent := s.switchSpent + a.switchCost s.active p.candidate
          guaranteedGain := s.guaranteedGain + a.margin},
        .promoted, a.evaluationCost p.candidate, a.switchCost s.active p.candidate⟩
    else
      ⟨{s with
          trials := s.trials + 1
          evaluationSpent := s.evaluationSpent + a.evaluationCost p.candidate},
        .rejected, a.evaluationCost p.candidate, 0⟩
  else ⟨s, .unfunded, 0, 0⟩

theorem initial_safe (a : Authority V) (v : V) (hc : a.Contract v) :
    Safe a (initial v) := by simp [Safe, initial, hc]

theorem eligible_gain [DecidableEq V] (a : Authority V) (s : State V) (p : Proposal V)
    (h : Eligible a s p) :
    a.utility s.active + (a.switchCost s.active p.candidate : Int) + (a.margin : Int) ≤
      a.utility p.candidate := by
  have hb := (a.bounds_sound s.active).2
  have hc := (a.bounds_sound p.candidate).1
  have hg := h.2.2.2.2.2.1
  omega

theorem eligible_strict_improvement [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) (h : Eligible a s p) :
    a.utility s.active < a.utility p.candidate := by
  have hg := eligible_gain a s p h
  have hm := a.margin_pos
  omega

theorem promoted_iff [DecidableEq V] (a : Authority V) (s : State V) (p : Proposal V) :
    (step a s p).outcome = .promoted ↔ Funded a s p ∧ Eligible a s p := by
  by_cases hf : Funded a s p <;> by_cases he : Eligible a s p <;> simp [step, hf, he]

theorem promotion_bound_to_request [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) (h : (step a s p).outcome = .promoted) :
    p.parent = s.active ∧ p.revision = s.revision ∧ p.core = a.core ∧
    p.objective = a.objective ∧ a.check p.candidate = true := by
  have he := ((promoted_iff a s p).mp h).2
  exact ⟨he.1, he.2.1, he.2.2.1, he.2.2.2.1, he.2.2.2.2.1⟩

theorem rejection_keeps_active [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) (h : (step a s p).outcome ≠ .promoted) :
    (step a s p).next.active = s.active := by
  by_cases hf : Funded a s p <;> by_cases he : Eligible a s p <;>
    simp_all [step]

theorem funded_trial_is_charged [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) (hf : Funded a s p) :
    (step a s p).next.evaluationSpent = s.evaluationSpent + a.evaluationCost p.candidate := by
  by_cases he : Eligible a s p <;> simp [step, hf, he]

theorem unfunded_unchanged [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) (hf : ¬ Funded a s p) :
    (step a s p).next = s ∧ (step a s p).evaluationDebit = 0 := by simp [step, hf]

theorem step_initial_unchanged [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) : (step a s p).next.initial = s.initial := by
  by_cases hf : Funded a s p <;> by_cases he : Eligible a s p <;> simp [step, hf, he]

theorem step_accounting [DecidableEq V] (a : Authority V) (s : State V) (p : Proposal V) :
    (step a s p).next.evaluationSpent = s.evaluationSpent + (step a s p).evaluationDebit ∧
    (step a s p).next.switchSpent = s.switchSpent + (step a s p).switchDebit := by
  by_cases hf : Funded a s p <;> by_cases he : Eligible a s p <;> simp [step, hf, he]

theorem step_safe [DecidableEq V] (a : Authority V) (s : State V) (p : Proposal V)
    (hs : Safe a s) : Safe a (step a s p).next := by
  by_cases hf : Funded a s p
  · by_cases he : Eligible a s p
    · have hc := a.check_sound p.candidate he.2.2.2.2.1
      have hg := eligible_gain a s p he
      have hb := he.2.2.2.2.2.2
      rcases hs with ⟨_, _, hquality, hgain, hrev⟩
      simp only [step, hf, he, ↓reduceIte, Safe]
      refine ⟨hc, by omega, ?_, ?_, by omega⟩
      · simp only [Int.natCast_add]
        omega
      · simpa only [Nat.add_mul, Nat.one_mul] using congrArg (fun x => x + a.margin) hgain
    · rcases hs with ⟨hc, _, hquality, hgain, hrev⟩
      simp only [step, hf, he, ↓reduceIte, Safe]
      exact ⟨hc, hf, hquality, hgain, by omega⟩
  · simpa [step, hf] using hs

theorem step_utility_nondecreasing [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) : a.utility s.active ≤ a.utility (step a s p).next.active := by
  by_cases hf : Funded a s p
  · by_cases he : Eligible a s p
    · have h := eligible_strict_improvement a s p he
      simpa [step, hf, he] using Int.le_of_lt h
    · simp [step, hf, he]
  · simp [step, hf]

/-- Replaying a promoted proposal cannot promote it again: its parent revision is stale.
A fresh evaluation of that stale proposal can still be charged. This is NOT an
idempotent payment API or a crash recovery protocol. -/
theorem promoted_proposal_stale [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) (h : (step a s p).outcome = .promoted) :
    (step a (step a s p).next p).outcome ≠ .promoted := by
  obtain ⟨hf, he⟩ := (promoted_iff a s p).mp h
  intro hh
  have hr := ((promoted_iff a _ p).mp hh).2.2.1
  have hp := he.2.1
  simp only [step, hf, he, ↓reduceIte] at hr
  omega

def run [DecidableEq V] (a : Authority V) : State V → List (Proposal V) → State V
  | s, [] => s
  | s, p :: ps => run a (step a s p).next ps

def trialCharges [DecidableEq V] (a : Authority V) : State V → List (Proposal V) → Nat
  | _, [] => 0
  | s, p :: ps => (step a s p).evaluationDebit + trialCharges a (step a s p).next ps

def switchCharges [DecidableEq V] (a : Authority V) : State V → List (Proposal V) → Nat
  | _, [] => 0
  | s, p :: ps => (step a s p).switchDebit + switchCharges a (step a s p).next ps

theorem run_safe [DecidableEq V] (a : Authority V) (s : State V) (ps : List (Proposal V))
    (hs : Safe a s) : Safe a (run a s ps) := by
  induction ps generalizing s with
  | nil => exact hs
  | cons p ps ih => exact ih _ (step_safe a s p hs)

theorem run_initial [DecidableEq V] (a : Authority V) (s : State V) (ps : List (Proposal V)) :
    (run a s ps).initial = s.initial := by
  induction ps generalizing s with
  | nil => rfl
  | cons p ps ih => simp only [run, ih, step_initial_unchanged]

theorem run_evaluation_accounting [DecidableEq V] (a : Authority V)
    (s : State V) (ps : List (Proposal V)) :
    (run a s ps).evaluationSpent = s.evaluationSpent + trialCharges a s ps := by
  induction ps generalizing s with
  | nil => simp [run, trialCharges]
  | cons p ps ih =>
    simp only [run, trialCharges, ih, (step_accounting a s p).1]
    omega

theorem run_switch_accounting [DecidableEq V] (a : Authority V)
    (s : State V) (ps : List (Proposal V)) :
    (run a s ps).switchSpent = s.switchSpent + switchCharges a s ps := by
  induction ps generalizing s with
  | nil => simp [run, switchCharges]
  | cons p ps ih =>
    simp only [run, switchCharges, ih, (step_accounting a s p).2]
    omega

/-- Net endpoint gain pays ALL search trials, including rejected candidates. -/
def campaignNet (a : Authority V) (s : State V) : Int :=
  a.utility s.active - a.utility s.initial - (s.evaluationSpent : Int) - (s.switchSpent : Int)

theorem campaign_net_lower_bound (a : Authority V) (s : State V) (hs : Safe a s) :
    (s.guaranteedGain : Int) - (s.evaluationSpent : Int) ≤ campaignNet a s := by
  have h := hs.2.2.1
  unfold campaignNet
  omega

theorem campaign_profitable_of_paid_search (a : Authority V) (s : State V)
    (hs : Safe a s) (h : s.evaluationSpent < s.guaranteedGain) :
    0 < campaignNet a s := by
  have hb := campaign_net_lower_bound a s hs
  omega

theorem no_overspend [DecidableEq V] (a : Authority V) (v : V)
    (hc : a.Contract v) (ps : List (Proposal V)) :
    (run a (initial v) ps).evaluationSpent + (run a (initial v) ps).switchSpent ≤ a.credits :=
  (run_safe a (initial v) ps (initial_safe a v hc)).2.1

/-- Central theorem: a fixed protected authority supports arbitrary proposed
sequences without silently weakening its contract, changing objective, or hiding
failed-trial charges. Evidence-bound soundness remains an explicit input. -/
theorem certified_upgrade_campaign [DecidableEq V] (a : Authority V) (v : V)
    (hc : a.Contract v) (ps : List (Proposal V)) :
    let s := run a (initial v) ps
    a.Contract s.active ∧
    s.evaluationSpent + s.switchSpent ≤ a.credits ∧
    (s.guaranteedGain : Int) - (s.evaluationSpent : Int) ≤ campaignNet a s := by
  dsimp only
  have hs := run_safe a (initial v) ps (initial_safe a v hc)
  exact ⟨hs.1, hs.2.1, campaign_net_lower_bound a _ hs⟩

/-- The proposer sees the current accepted version and the accumulated ledger.
It may be learned, adversarial, or itself version-dependent. The theorem does not
assume or establish that it finds useful candidates. -/
def iterate [DecidableEq V] (a : Authority V)
    (propose : Nat → State V → Proposal V) : Nat → State V → State V
  | 0, s => s
  | n + 1, s => iterate a propose n (step a s (propose n s)).next

theorem adaptive_campaign_safe [DecidableEq V] (a : Authority V)
    (propose : Nat → State V → Proposal V) (n : Nat) (s : State V) (hs : Safe a s) :
    Safe a (iterate a propose n s) := by
  induction n generalizing s with
  | zero => exact hs
  | succ n ih => exact ih _ (step_safe a s (propose n s) hs)

theorem adaptive_utility_nondecreasing [DecidableEq V] (a : Authority V)
    (propose : Nat → State V → Proposal V) (n : Nat) (s : State V) :
    a.utility s.active ≤ a.utility (iterate a propose n s).active := by
  induction n generalizing s with
  | zero => exact Int.le_refl _
  | succ n ih =>
    have hstep := step_utility_nondecreasing a s (propose n s)
    have htail := ih (step a s (propose n s)).next
    exact Int.le_trans hstep htail

theorem adaptive_campaign_net_bound [DecidableEq V] (a : Authority V)
    (propose : Nat → State V → Proposal V) (n : Nat) (s : State V) (hs : Safe a s) :
    let final := iterate a propose n s
    (final.guaranteedGain : Int) - (final.evaluationSpent : Int) ≤ campaignNet a final :=
  campaign_net_lower_bound a _ (adaptive_campaign_safe a propose n s hs)

theorem changed_objective_never_promotes [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) (h : p.objective ≠ a.objective) :
    (step a s p).outcome ≠ .promoted := by
  intro hp
  exact h (promotion_bound_to_request a s p hp).2.2.2.1

theorem changed_core_never_promotes [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) (h : p.core ≠ a.core) :
    (step a s p).outcome ≠ .promoted := by
  intro hp
  exact h (promotion_bound_to_request a s p hp).2.2.1

theorem rejected_check_never_promotes [DecidableEq V] (a : Authority V)
    (s : State V) (p : Proposal V) (h : a.check p.candidate = false) :
    (step a s p).outcome ≠ .promoted := by
  intro hp
  have hc := (promotion_bound_to_request a s p hp).2.2.2.2
  rw [h] at hc
  contradiction

end Komorebi.AVOC.Upgrade
