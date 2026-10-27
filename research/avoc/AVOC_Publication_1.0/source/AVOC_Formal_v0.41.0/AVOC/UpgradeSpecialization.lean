import AVOC.VerifiedUpgrade
import AVOC.RetryEvaluation

namespace Komorebi.AVOC.UpgradeCatalogue

/-- Immutable compiled candidates, NOT arbitrary source supplied by an LLM.
The editable component's contract returns only the retry decision. It does not
replace the v0.22 report that also promises an exact lookahead value. -/
inductive Version where
  | dynamic | threshold | alwaysRetry
  deriving Repr, DecidableEq

structure Decision where
  retry : Bool
  visits : Nat
  deriving Repr, DecidableEq

def execute {S : Type} (v : Version) (m : Retry.Model S) (n : Nat) (s : S) : Decision :=
  match v with
  | .dynamic => let r := Retry.evaluate m n s; ⟨r.retry, r.visits⟩
  | .threshold => ⟨match n with
      | 0 => false
      | _ + 1 => m.enabled s && decide (0 < Retry.immediate m s), 1⟩
  | .alwaysRetry => ⟨true, 1⟩

def Contract (v : Version) : Prop :=
  ∀ (S : Type) (m : Retry.Model S), Retry.NoRevival m →
  ∀ (n : Nat) (s : S), (execute v m n s).retry = Retry.choose m n s

def check : Version → Bool
  | .dynamic => true
  | .threshold => true
  | .alwaysRetry => false

theorem dynamic_contract : Contract .dynamic := by
  intro S m _ n s
  exact Retry.evaluate_choice m n s

theorem threshold_contract : Contract .threshold := by
  intro S m h n s
  cases n with
  | zero => rfl
  | succ n => exact (Retry.choose_threshold m h n s).symm

theorem check_sound (v : Version) (h : check v = true) : Contract v := by
  cases v with
  | dynamic => exact dynamic_contract
  | threshold => exact threshold_contract
  | alwaysRetry => simp [check] at h

theorem evaluate_visits_positive {S : Type} (m : Retry.Model S) (n : Nat) (s : S) :
    1 ≤ (Retry.evaluate m n s).visits := by
  cases n with
  | zero => exact le_rfl
  | succ n => unfold Retry.evaluate; split <;> simp_all

/-- The replacement has no worse STATE-VISIT cost for every input. Arithmetic,
proof checking, compilation, wall time and allocation are outside this meter. -/
theorem threshold_work_nondegrading {S : Type} (m : Retry.Model S) (n : Nat) (s : S) :
    (execute .threshold m n s).visits ≤ (execute .dynamic m n s).visits :=
  evaluate_visits_positive m n s

theorem threshold_observational_equivalence {S : Type} (m : Retry.Model S)
    (h : Retry.NoRevival m) (n : Nat) (s : S) :
    (execute .threshold m n s).retry = (execute .dynamic m n s).retry := by
  rw [threshold_contract S m h n s, dynamic_contract S m h n s]

/-- A simple protected workload. The general contract and work domination above
are not inferred from these finite benchmark cases. -/
def exampleModel : Retry.Model Unit where
  enabled _ := true
  resolve _ := 1/2
  resolve_nonneg _ := by norm_num
  resolve_le_one _ := by norm_num
  cost _ := 1
  gain _ := 4
  afterFault _ := ()

theorem example_no_revival : Retry.NoRevival exampleModel := by
  intro s h
  cases s
  exact h

theorem uncertified_version_fails : ¬ Contract .alwaysRetry := by
  intro h
  have hh := h Unit exampleModel example_no_revival 0 ()
  change true = false at hh
  contradiction

def horizons : List Nat := [0, 1, 2, 4, 8, 16, 32]

def workScore (v : Version) : Nat :=
  (horizons.map (fun n => (execute v exampleModel n ()).visits)).sum

def utility (v : Version) : Int := -(workScore v : Int)

theorem example_dynamic_visits (n : Nat) :
    (Retry.evaluate exampleModel n ()).visits = n + 1 := by
  induction n with
  | zero => rfl
  | succ n ih =>
    change (Retry.evaluate exampleModel n ()).visits + 1 = (n + 1) + 1
    omega

theorem dynamic_work : workScore .dynamic = 70 := by
  unfold workScore
  simp only [execute, example_dynamic_visits]
  decide

theorem threshold_work : workScore .threshold = 7 := by decide

theorem alwaysRetry_work : workScore .alwaysRetry = 7 := by decide

/-- Evaluation cost and switching cost are protected illustrative accounting
units in the SAME nominal utility scale. They are not runtime measurements. -/
def authority (credits : Nat) : Upgrade.Authority Version where
  core := "AVOC-upgrade-checker-v1"
  objective := "retry-action-NoRevival;visits-horizons-0-1-2-4-8-16-32;v1"
  Contract := Contract
  check := check
  check_sound := check_sound
  utility := utility
  lower := utility
  upper := utility
  bounds_sound _ := ⟨le_rfl, le_rfl⟩
  evaluationCost _ := 3
  switchCost _ _ := 1
  credits := credits
  margin := 8
  margin_pos := by decide

def proposal (parent candidate : Version) (revision : Nat) : Upgrade.Proposal Version :=
  ⟨parent, revision, candidate, (authority 0).core, (authority 0).objective⟩

def initial : Upgrade.State Version := Upgrade.initial .dynamic

def badTrial : Upgrade.Proposal Version := proposal .dynamic .alwaysRetry 0

def goodTrial : Upgrade.Proposal Version := proposal .dynamic .threshold 0

def beforeUpgrade : Upgrade.State Version :=
  (Upgrade.step (authority 100) initial badTrial).next

def afterUpgrade : Upgrade.State Version :=
  (Upgrade.step (authority 100) beforeUpgrade goodTrial).next

theorem initial_safe (credits : Nat) : Upgrade.Safe (authority credits) initial :=
  Upgrade.initial_safe _ _ dynamic_contract

theorem rejected_bad_candidate :
    (Upgrade.step (authority 100) initial badTrial).outcome = .rejected := by
  simp [Upgrade.step, Upgrade.Funded, Upgrade.Eligible, authority, initial,
    Upgrade.initial, badTrial, proposal, check]

theorem bad_trial_cost_retained : beforeUpgrade.evaluationSpent = 3 := by
  simp [beforeUpgrade, Upgrade.step, Upgrade.Funded, Upgrade.Eligible, authority,
    initial, Upgrade.initial, badTrial, proposal, check]

theorem approved_good_candidate :
    (Upgrade.step (authority 100) beforeUpgrade goodTrial).outcome = .promoted := by
  simp [beforeUpgrade, Upgrade.step, Upgrade.Funded, Upgrade.Eligible, authority,
    initial, Upgrade.initial, badTrial, goodTrial, proposal, check,
    utility, dynamic_work, threshold_work]

theorem after_upgrade_net_gain : Upgrade.campaignNet (authority 100) afterUpgrade = 56 := by
  simp [Upgrade.campaignNet, afterUpgrade, beforeUpgrade, Upgrade.step,
    Upgrade.Funded, Upgrade.Eligible, authority, initial, Upgrade.initial,
    badTrial, goodTrial, proposal, check, utility, dynamic_work, threshold_work]

theorem after_upgrade_safe : Upgrade.Safe (authority 100) afterUpgrade :=
  Upgrade.step_safe _ _ _ (Upgrade.step_safe _ _ _ (initial_safe 100))

/-- An accepted version can be cheaper while its improvement campaign loses money.
The state represents 24 already-paid rejected trials, then one paid promotion. -/
def expensiveSearch : Upgrade.State Version :=
  {initial with trials := 24, evaluationSpent := 72}

set_option maxRecDepth 10000 in
theorem expensive_search_reachable :
    Upgrade.run (authority 100) initial (List.replicate 24 badTrial) = expensiveSearch := by
  decide

theorem expensive_search_safe : Upgrade.Safe (authority 100) expensiveSearch := by
  simp [Upgrade.Safe, expensiveSearch, initial, Upgrade.initial, authority, dynamic_contract]

theorem improved_version_unprofitable_campaign :
    let r := Upgrade.step (authority 100) expensiveSearch goodTrial
    r.outcome = .promoted ∧ Upgrade.campaignNet (authority 100) r.next = -13 := by
  simp [Upgrade.step, Upgrade.Funded, Upgrade.Eligible, expensiveSearch,
    authority, initial, Upgrade.initial, goodTrial, proposal, check,
    utility, dynamic_work, threshold_work, Upgrade.campaignNet]

end Komorebi.AVOC.UpgradeCatalogue
