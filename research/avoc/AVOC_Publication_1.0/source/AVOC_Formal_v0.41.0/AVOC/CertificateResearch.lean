import AVOC.ArtifactBinding
import AVOC.ResearchPolicy

namespace Komorebi.AVOC.BoundResearch

open Certificate Binding

variable {P : Type*} [PartialOrder P]

/-- Explicit semantic adapter: the requested target is the task formula, and
all supplied premise formulas correspond to strict prerequisite tasks. -/
def Describes (formula : P → Formula) (x : P) (i : Identity) : Prop :=
  i.statement = formula x ∧
    ∀ f ∈ context i, ∃ y, y < x ∧ f = formula y

/-- Here checker soundness is derived from executable proof checking; it is not
another assumed Boolean-to-truth axiom. -/
theorem bound_receipt_local_rule (formula : P → Formula) (v : Nat → Prop)
    (x : P) (i : Identity) (t : Ticket) (r : Receipt)
    (hd : Describes formula x i) (hv : validate i t r = true) :
    Scheduling.LocalRule (fun y => Denote v (formula y)) x := by
  intro hprev
  have hc : Satisfies v (context i) := by
    intro f hf
    obtain ⟨y, hy, he⟩ := hd.2 f hf
    rw [he]
    exact hprev y hy
  simpa only [hd.1] using validated_sound i t r hv v hc

variable {C : Type*}

def boundGate (spec : P → Identity) (registry : C → Ticket) (x : P) (c : C) : Bool :=
  validate (spec x) (registry c) ⟨registry c, true⟩

theorem boundGate_sound (formula : P → Formula) (v : Nat → Prop)
    (spec : P → Identity) (registry : C → Ticket)
    (hd : ∀ x, Describes formula x (spec x)) (x : P) (c : C)
    (h : boundGate spec registry x c = true) :
    Scheduling.LocalRule (fun y => Denote v (formula y)) x :=
  bound_receipt_local_rule formula v x (spec x) (registry c) ⟨registry c, true⟩ (hd x) h

/-- A concrete receipt gate for any finite registered candidate catalogue.
Other fields remain declared stochastic/resource data. -/
def protocol {Ω : Type*} [Fintype Ω] [Fintype C]
    (formula : P → Formula) (v : Nat → Prop)
    (spec : P → Identity) (registry : C → Ticket)
    (hd : ∀ x, Describes formula x (spec x))
    (attemptFee verifyFee : P → Nat)
    (experiment : Research.State Ω P → Research.Action P → RationalChannel Ω (Option C))
    (admissionValue : P → ℚ) (congestion : Nat → ℚ) :
    Research.Protocol Ω P C (fun y => Denote v (formula y)) where
  attemptFee := attemptFee
  verifyFee := verifyFee
  check := boundGate spec registry
  check_sound := boundGate_sound formula v spec registry hd
  experiment := experiment
  admissionValue := admissionValue
  congestion := congestion

/-- Filter against the actual pending artifact and its current identity. -/
def filterReceipt (i : Identity) (slot : Slot) (registry : C → Ticket) : Option C → Option C
  | none => none
  | some c => match slot.pending with
      | none => none
      | some t => if validate i t ⟨registry c, true⟩ then some c else none

theorem passing_filter_bound (i : Identity) (slot : Slot) (registry : C → Ticket)
    (o : Option C) (c : C) (h : filterReceipt i slot registry o = some c) :
    o = some c ∧ ∃ t, slot.pending = some t ∧ registry c = t ∧
      t.artifact.identity = i ∧ Valid t.artifact := by
  cases o with
  | none => simp [filterReceipt] at h
  | some d =>
      cases hp : slot.pending with
      | none => simp [filterReceipt, hp] at h
      | some t =>
          by_cases hv : validate i t ⟨registry d, true⟩ = true
          · have hdc : d = c := by simpa [filterReceipt, hp, hv] using h
            subst d
            exact ⟨rfl, t, rfl, validated_receipt i t _ hv,
              validated_identity i t _ hv, validated_artifact_valid i t _ hv⟩
          · simp [filterReceipt, hp, hv] at h

theorem empty_slot_blocks (i : Identity) (slot : Slot) (registry : C → Ticket)
    (h : slot.pending = none) (o : Option C) : filterReceipt i slot registry o = none := by
  cases o <;> simp [filterReceipt, h]

variable {Ω : Type*} [Fintype Ω] [Fintype C] [DecidableEq P] {claim : P → Prop}

/-- Deterministic safe admission adapter. It consumes the pending slot. This is
not a claim of unchanged observation likelihoods or Bellman values after filtering. -/
noncomputable def verifyBound (p : Research.Protocol Ω P C claim)
    (i : Identity) (slot : Slot) (registry : C → Ticket)
    (s : Research.State Ω P) (x : P) (o : Option C) : Research.State Ω P × Slot :=
  (Research.step p s (.verify x) (filterReceipt i slot registry o),
    ⟨slot.nextGeneration, none⟩)

theorem bound_verification_budgetSafe (p : Research.Protocol Ω P C claim)
    (i : Identity) (slot : Slot) (registry : C → Ticket)
    (s : Research.State Ω P) (x : P) (o : Option C) (B : Nat)
    (hs : Research.BudgetSafe claim B s) (ha : Research.Allowed p s (.verify x)) :
    Research.BudgetSafe claim B (verifyBound p i slot registry s x o).1 :=
  Research.step_budgetSafe p B s hs (.verify x) ha (filterReceipt i slot registry o)

theorem bound_verification_consumes (p : Research.Protocol Ω P C claim)
    (i : Identity) (slot : Slot) (registry : C → Ticket)
    (s : Research.State Ω P) (x : P) (o : Option C) :
    (verifyBound p i slot registry s x o).2.pending = none := rfl

theorem new_bound_completion_has_exact_artifact (p : Research.Protocol Ω P C claim)
    (i : Identity) (slot : Slot) (registry : C → Ticket)
    (s : Research.State Ω P) (x y : P) (o : Option C)
    (hn : y ∈ (verifyBound p i slot registry s x o).1.completed)
    (hf : y ∉ s.completed) :
    y = x ∧ ∃ c t, o = some c ∧ slot.pending = some t ∧ registry c = t ∧
      t.artifact.identity = i ∧ Valid t.artifact := by
  have h := Research.new_completion_requires_verification p s (.verify x)
    (filterReceipt i slot registry o) y hn hf
  have he : x = y := Research.Action.verify.inj h.1
  subst y
  cases ho : filterReceipt i slot registry o with
  | none => simp [Research.accepted, ho] at h
  | some c =>
      obtain ⟨he, t, hp, hr, hi, hv⟩ := passing_filter_bound i slot registry o c ho
      exact ⟨rfl, c, t, he, hp, hr, hi, hv⟩

theorem rejected_bound_completion_unchanged (p : Research.Protocol Ω P C claim)
    (i : Identity) (slot : Slot) (registry : C → Ticket)
    (s : Research.State Ω P) (x : P) (o : Option C)
    (h : filterReceipt i slot registry o = none) :
    (verifyBound p i slot registry s x o).1.completed = s.completed := by
  exact Research.rejected_completed_unchanged p s x _ (by simp [h, Research.accepted])

theorem replay_cannot_admit_new (p : Research.Protocol Ω P C claim)
    (i : Identity) (slot : Slot) (registry : C → Ticket)
    (s : Research.State Ω P) (x : P) (o : Option C) :
    let result := verifyBound p i slot registry s x o
    (verifyBound p i result.2 registry result.1 x o).1.completed = result.1.completed := by
  dsimp only
  apply rejected_bound_completion_unchanged
  exact empty_slot_blocks i _ registry rfl o

end Komorebi.AVOC.BoundResearch
