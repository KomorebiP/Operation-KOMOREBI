import AVOC.AffineReuseCodec
import AVOC.MultiLevelEconomics

namespace Komorebi.AVOC.Affine.Terminal

open Factorization Reuse SearchGuard MultiLevelEconomics
open ReuseCodec

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5

inductive Kind where
  | warm
  | cold
  deriving Repr, DecidableEq

/-- A terminal implementation result carries the semantic proof needed to deploy it.
`setup` is the incremental setup charge from the current decision point. -/
structure Deployment (n m : Nat) where
  kind : Kind
  source : DenseProgram F n m
  selected : DenseProgram F n m
  setup : Nat
  correct : ∀ x, execute selected x = execute source x
  noWorse : executionCost selected ≤ executionCost source

namespace Deployment

variable {n m : Nat}

@[simp] theorem source_correct (d : Deployment n m) (x : Fin n → F) :
    execute d.selected x = execute d.source x := d.correct x

@[simp] theorem selected_cost_le (d : Deployment n m) :
    executionCost d.selected ≤ executionCost d.source := d.noWorse

/-- Incremental net value relative to executing the source for every declared call. -/
def payoff (d : Deployment n m) (calls : Nat) : ℚ :=
  netGain calls (executionCost d.source) d.setup (executionCost d.selected)

@[simp] theorem payoff_formula (d : Deployment n m) (calls : Nat) :
    d.payoff calls =
      (calls : ℚ) * ((executionCost d.source : ℚ) -
        (executionCost d.selected : ℚ)) - (d.setup : ℚ) := rfl

theorem payoff_le_gross_saving (d : Deployment n m) (calls : Nat) :
    d.payoff calls ≤
      (calls : ℚ) * ((executionCost d.source : ℚ) -
        (executionCost d.selected : ℚ)) := by
  unfold payoff netGain
  have hs : (0 : ℚ) ≤ d.setup := by positivity
  linarith

theorem nonpositive_when_no_strict_saving (d : Deployment n m) (calls : Nat)
    (h : executionCost d.source ≤ executionCost d.selected) :
    d.payoff calls ≤ 0 :=
  netGain_nonpositive_of_no_saving calls _ _ _ h

theorem source_and_selected_observationally_equal (d : Deployment n m) :
    ∀ x, execute d.selected x = execute d.source x := d.correct

end Deployment

/-- Construct a proof-carrying warm-cache result after revalidation and retargeting. -/
def warmFrom {n m : Nat} (p : DenseProgram F n m) (r : Record F n m)
    (paid credit : Nat) : Option (Deployment n m) :=
  match imported p r paid credit with
  | none => none
  | some c => some {
      kind := .warm
      source := p
      selected := choose p c
      setup := normalizationCost p + reuseCharge n m r.candidate.width
      correct := choose_correct p c
      noWorse := choose_le_original p c }

/-- Construct a proof-carrying cold-generation result after checking the candidate. -/
def coldFrom {n m : Nat} (p : DenseProgram F n m) (c : Candidate F n m)
    (generation credit : Nat) : Option (Deployment n m) :=
  match admit p c generation credit with
  | none => none
  | some checked => some {
      kind := .cold
      source := p
      selected := choose p checked
      setup := upfront p c.width generation
      correct := choose_correct p checked
      noWorse := choose_le_original p checked }

variable {n m : Nat}

theorem warmFrom_kind {p : DenseProgram F n m} {r : Record F n m}
    {paid credit : Nat} {d : Deployment n m} (h : warmFrom p r paid credit = some d) :
    d.kind = .warm := by
  cases hi : imported p r paid credit with
  | none => simp [warmFrom, hi] at h
  | some c =>
      simp [warmFrom, hi] at h
      subst d
      rfl

theorem warmFrom_source {p : DenseProgram F n m} {r : Record F n m}
    {paid credit : Nat} {d : Deployment n m} (h : warmFrom p r paid credit = some d) :
    d.source = p := by
  cases hi : imported p r paid credit with
  | none => simp [warmFrom, hi] at h
  | some c =>
      simp [warmFrom, hi] at h
      subst d
      rfl

theorem warmFrom_setup {p : DenseProgram F n m} {r : Record F n m}
    {paid credit : Nat} {d : Deployment n m} (h : warmFrom p r paid credit = some d) :
    d.setup = normalizationCost p + reuseCharge n m r.candidate.width := by
  cases hi : imported p r paid credit with
  | none => simp [warmFrom, hi] at h
  | some c =>
      simp [warmFrom, hi] at h
      subst d
      rfl

theorem warmFrom_budget {p : DenseProgram F n m} {r : Record F n m}
    {paid credit : Nat} {d : Deployment n m} (h : warmFrom p r paid credit = some d) :
    paid + d.setup ≤ credit := by
  cases hi : imported p r paid credit with
  | none => simp [warmFrom, hi] at h
  | some c =>
      simp [warmFrom, hi] at h
      subst d
      simpa [Nat.add_assoc] using import_budget p r paid credit c hi

theorem warmFrom_sound {p : DenseProgram F n m} {r : Record F n m}
    {paid credit : Nat} {d : Deployment n m} (h : warmFrom p r paid credit = some d) :
    (∀ x, execute d.selected x = execute p x) ∧
      executionCost d.selected ≤ executionCost p := by
  constructor
  · intro x
    rw [← warmFrom_source h]
    exact d.correct x
  · rw [← warmFrom_source h]
    exact d.noWorse

theorem coldFrom_kind {p : DenseProgram F n m} {c : Candidate F n m}
    {generation credit : Nat} {d : Deployment n m} (h : coldFrom p c generation credit = some d) :
    d.kind = .cold := by
  cases hi : admit p c generation credit with
  | none => simp [coldFrom, hi] at h
  | some checked =>
      simp [coldFrom, hi] at h
      subst d
      rfl

theorem coldFrom_source {p : DenseProgram F n m} {c : Candidate F n m}
    {generation credit : Nat} {d : Deployment n m} (h : coldFrom p c generation credit = some d) :
    d.source = p := by
  cases hi : admit p c generation credit with
  | none => simp [coldFrom, hi] at h
  | some checked =>
      simp [coldFrom, hi] at h
      subst d
      rfl

theorem coldFrom_setup {p : DenseProgram F n m} {c : Candidate F n m}
    {generation credit : Nat} {d : Deployment n m} (h : coldFrom p c generation credit = some d) :
    d.setup = upfront p c.width generation := by
  cases hi : admit p c generation credit with
  | none => simp [coldFrom, hi] at h
  | some checked =>
      simp [coldFrom, hi] at h
      subst d
      rfl

theorem coldFrom_budget {p : DenseProgram F n m} {c : Candidate F n m}
    {generation credit : Nat} {d : Deployment n m} (h : coldFrom p c generation credit = some d) :
    d.setup ≤ credit := by
  cases hi : admit p c generation credit with
  | none => simp [coldFrom, hi] at h
  | some checked =>
      simp [coldFrom, hi] at h
      subst d
      exact ((admission_iff p c generation credit).1 ⟨checked,hi⟩).1

theorem coldFrom_sound {p : DenseProgram F n m} {c : Candidate F n m}
    {generation credit : Nat} {d : Deployment n m} (h : coldFrom p c generation credit = some d) :
    (∀ x, execute d.selected x = execute p x) ∧
      executionCost d.selected ≤ executionCost p := by
  constructor
  · intro x
    rw [← coldFrom_source h]
    exact d.correct x
  · rw [← coldFrom_source h]
    exact d.noWorse

/-- A successful terminal result can be compared directly with the planner's declared payoff. -/
def payoffError {n m : Nat} (estimate : ℚ) (d : Deployment n m) (calls : Nat) : ℚ :=
  |estimate - d.payoff calls|

theorem payoff_within {n m : Nat} (estimate eta : ℚ) (d : Deployment n m)
    (calls : Nat) (h : payoffError estimate d calls ≤ eta) :
    |estimate - d.payoff calls| ≤ eta := h

end Komorebi.AVOC.Affine.Terminal
