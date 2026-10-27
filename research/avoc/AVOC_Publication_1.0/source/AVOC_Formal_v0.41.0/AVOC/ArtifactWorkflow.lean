import AVOC.CertificateResearch
import AVOC.FilteredObservation

namespace Komorebi.AVOC.ArtifactWorkflow

open Certificate Binding Scheduling

/-- One protected in-flight slot, matching the serial local-store workflow.
The verified receipt is separate from pending and from completed claims. -/
structure State (Ω P : Type*) [Fintype Ω] where
  belief : RationalBelief Ω
  completed : Finset P
  slot : Slot
  owner : Option P
  checked : Option Receipt
  budget : Nat
  spent : Nat
  halted : Bool

inductive Action (P C : Type*) where
  | register (task : P) (candidate : C)
  | verify
  | admit
  | stop
  deriving DecidableEq, Repr

/-- A finite declared catalogue; raw reports remain internal to the verifier.
Only the validated/rejected Boolean report is exposed to this controller. -/
structure Protocol (Ω P C O : Type*) [Fintype Ω] [Fintype O] [PartialOrder P] where
  formula : P → Formula
  valuation : Nat → Prop
  spec : P → Identity
  describes : ∀ x, BoundResearch.Describes formula x (spec x)
  candidate : P → C → Artifact
  registerFee : P → C → Nat
  verifyFee : P → Nat
  admitFee : P → Nat
  admissionValue : P → ℚ
  rawChannel : State Ω P → RationalChannel Ω O
  rawReceipt : State Ω P → O → Option Receipt

variable {Ω P C O : Type*} [Fintype Ω] [Fintype O] [PartialOrder P] [DecidableEq P]

def claim (p : Protocol Ω P C O) (x : P) : Prop := Denote p.valuation (p.formula x)

/-- The checker publishes only its exact current-ticket acceptance bit. -/
def report (p : Protocol Ω P C O) (s : State Ω P) (o : O) : Bool :=
  match s.owner, s.slot.pending, p.rawReceipt s o with
  | some x, some t, some r => validate (p.spec x) t r
  | _, _, _ => false

/-- Reconstruct the unique canonical passing receipt only after rechecking the
current pending artifact.  Impossible `true` report branches cannot forge it. -/
def currentReceipt (p : Protocol Ω P C O) (s : State Ω P) : Option Receipt :=
  match s.owner, s.slot.pending with
  | some x, some t =>
      let r : Receipt := ⟨t, true⟩
      if validate (p.spec x) t r then some r else none
  | _, _ => none

def fee (p : Protocol Ω P C O) (s : State Ω P) : Action P C → Nat
  | .register x c => p.registerFee x c
  | .verify => s.owner.elim 0 p.verifyFee
  | .admit => s.owner.elim 0 p.admitFee
  | .stop => 0

def Precondition (p : Protocol Ω P C O) (s : State Ω P) : Action P C → Prop
  | .register x _ => Ready s.completed x
  | .verify => ∃ x t, s.owner = some x ∧ s.slot.pending = some t
  | .admit => ∃ x t r, s.owner = some x ∧ s.slot.pending = some t ∧
      s.checked = some r ∧ validate (p.spec x) t r = true
  | .stop => True

def Allowed (p : Protocol Ω P C O) (s : State Ω P) (a : Action P C) : Prop :=
  a = .stop ∨ (s.halted = false ∧ fee p s a ≤ s.budget ∧ Precondition p s a)

/-- Belief and receipt correctness are orthogonal: proof evidence is carried by
checked receipts and certified completed propositions, not posterior magnitude. -/
structure Safe (p : Protocol Ω P C O) (s : State Ω P) : Prop where
  ideal : IsIdeal s.completed
  certified : Certified (claim p) s.completed
  generation : WellFormed s.slot
  paired : s.owner = none ↔ s.slot.pending = none
  ready : ∀ x, s.owner = some x → Ready s.completed x
  receipt : ∀ r, s.checked = some r → ∃ x t,
    s.owner = some x ∧ s.slot.pending = some t ∧ validate (p.spec x) t r = true

def BudgetSafe (p : Protocol Ω P C O) (B : Nat) (s : State Ω P) : Prop :=
  Safe p s ∧ s.budget + s.spent = B

def charge (p : Protocol Ω P C O) (s : State Ω P) (a : Action P C) : State Ω P :=
  { s with budget := s.budget - fee p s a, spent := s.spent + fee p s a }

def registerStep (p : Protocol Ω P C O) (s : State Ω P) (x : P) (c : C) : State Ω P :=
  { charge p s (.register x c) with
    slot := Binding.register s.slot (p.candidate x c), owner := some x, checked := none }

noncomputable def verifyStep (p : Protocol Ω P C O) (s : State Ω P) (d : Bool) : State Ω P :=
  { charge p s .verify with
    belief := bayesUpdateTotal s.belief (Filtered.reportChannel (p.rawChannel s) (report p s)) d
    checked := if d then currentReceipt p s else none }

/-- Admission re-executes the existing consume gate. Rejected consumption keeps
the pending candidate; successful consumption clears ownership and the receipt. -/
def admitStep (p : Protocol Ω P C O) (s : State Ω P) : State Ω P :=
  match s.owner, s.checked with
  | some x, some r =>
      match Binding.consume s.slot (p.spec x) r with
      | (slot, some _) =>
          { charge p s .admit with
            completed := insert x s.completed
            slot := slot
            owner := none
            checked := none }
      | (_, none) => charge p s .admit
  | _, _ => charge p s .admit

noncomputable def step (p : Protocol Ω P C O) (s : State Ω P)
    (a : Action P C) (d : Bool) : State Ω P :=
  match a with
  | .register x c => registerStep p s x c
  | .verify => verifyStep p s d
  | .admit => admitStep p s
  | .stop => { s with halted := true }

/-- The law of the report actually visible to the controller. All rejection
preimages are retained. No renormalization to successful receipts occurs. -/
def channel (p : Protocol Ω P C O) (s : State Ω P) : Action P C → RationalChannel Ω Bool
  | .verify => Filtered.reportChannel (p.rawChannel s) (report p s)
  | _ => Filtered.silentChannel false

/-- Stage fees are charged separately; value is obtained only by actual admission.
The constants are declared costs, not measured machine/LLM costs. -/
def reward (p : Protocol Ω P C O) (s : State Ω P) (a : Action P C) : ℚ :=
  (match a, s.owner, s.checked with
   | .admit, some x, some r =>
       match (Binding.consume s.slot (p.spec x) r).2 with
       | some _ => p.admissionValue x
       | none => 0
   | _, _, _ => 0) - (fee p s a : ℚ)

omit [DecidableEq P] in
theorem stop_allowed (p : Protocol Ω P C O) (s : State Ω P) : Allowed p s .stop :=
  Or.inl rfl

omit [DecidableEq P] in
theorem allowed_fee (p : Protocol Ω P C O) (s : State Ω P)
    (a : Action P C) (h : Allowed p s a) : fee p s a ≤ s.budget := by
  rcases h with rfl | h
  · exact Nat.zero_le _
  · exact h.2.1

omit [DecidableEq P] in
theorem halted_only_stop (p : Protocol Ω P C O) (s : State Ω P)
    (hh : s.halted = true) (a : Action P C) (ha : Allowed p s a) : a = .stop := by
  rcases ha with h | h
  · exact h
  · simp [hh] at h

omit [DecidableEq P] in
theorem currentReceipt_bound (p : Protocol Ω P C O) (s : State Ω P) (r : Receipt)
    (h : currentReceipt p s = some r) : ∃ x t,
    s.owner = some x ∧ s.slot.pending = some t ∧ validate (p.spec x) t r = true := by
  cases hx : s.owner with
  | none => simp [currentReceipt, hx] at h
  | some x =>
    cases ht : s.slot.pending with
    | none => simp [currentReceipt, hx, ht] at h
    | some t =>
      by_cases hv : validate (p.spec x) t ⟨t, true⟩ = true
      · have he : (⟨t, true⟩ : Receipt) = r := by simpa [currentReceipt, hx, ht, hv] using h
        subst r
        exact ⟨x, t, rfl, rfl, hv⟩
      · simp [currentReceipt, hx, ht, hv] at h

omit [DecidableEq P] in
theorem report_true_bound (p : Protocol Ω P C O) (s : State Ω P) (o : O)
    (h : report p s o = true) : ∃ x t r,
    s.owner = some x ∧ s.slot.pending = some t ∧ p.rawReceipt s o = some r ∧
      r.subject = t ∧ t.artifact.identity = p.spec x ∧ Valid t.artifact := by
  cases hx : s.owner with
  | none => simp [report, hx] at h
  | some x =>
    cases ht : s.slot.pending with
    | none => simp [report, hx, ht] at h
    | some t =>
      cases hr : p.rawReceipt s o with
      | none => simp [report, hx, ht, hr] at h
      | some r =>
        have hv : validate (p.spec x) t r = true := by simpa [report, hx, ht, hr] using h
        exact ⟨x, t, r, rfl, rfl, rfl, validated_receipt _ _ _ hv,
          validated_identity _ _ _ hv, validated_artifact_valid _ _ _ hv⟩

omit [DecidableEq P] in
theorem register_safe (p : Protocol Ω P C O) (s : State Ω P) (hs : Safe p s)
    (x : P) (c : C) (hr : Ready s.completed x) : Safe p (registerStep p s x c) := by
  refine ⟨hs.ideal, hs.certified, register_wellFormed _ _, ?_, ?_, ?_⟩
  · simp [registerStep, Binding.register]
  · intro y hy
    have he : x = y := Option.some.inj hy
    change Ready s.completed y
    simpa [he] using hr
  · intro r h
    simp [registerStep] at h

omit [DecidableEq P] in
theorem verify_safe (p : Protocol Ω P C O) (s : State Ω P) (hs : Safe p s)
    (d : Bool) : Safe p (verifyStep p s d) := by
  refine ⟨hs.ideal, hs.certified, hs.generation, hs.paired, hs.ready, ?_⟩
  intro r hr
  cases d with
  | false => simp [verifyStep] at hr
  | true =>
    have hc : currentReceipt p s = some r := by simpa [verifyStep] using hr
    exact currentReceipt_bound p s r hc

theorem admitStep_of_pass (p : Protocol Ω P C O) (s : State Ω P)
    (x : P) (t : Ticket) (r : Receipt)
    (hx : s.owner = some x) (ht : s.slot.pending = some t)
    (hr : s.checked = some r) (hv : validate (p.spec x) t r = true) :
    admitStep p s = { charge p s .admit with
      completed := insert x s.completed
      slot := ⟨s.slot.nextGeneration, none⟩
      owner := none
      checked := none } := by
  simp [admitStep, hx, hr, Binding.consume, ht, hv]

theorem admit_safe (p : Protocol Ω P C O) (s : State Ω P) (hs : Safe p s)
    (ha : Precondition p s .admit) : Safe p (admitStep p s) := by
  obtain ⟨x, t, r, hx, ht, hr, hv⟩ := ha
  have hlocal := BoundResearch.bound_receipt_local_rule p.formula p.valuation
    x (p.spec x) t r (p.describes x) hv
  have hcert := checked_step_preserves hs.ideal hs.certified (hs.ready x hx) hlocal
  rw [admitStep_of_pass p s x t r hx ht hr hv]
  refine ⟨hcert.1, hcert.2, ?_, ?_, ?_, ?_⟩
  · intro u hu
    simp at hu
  · simp
  · intro y hy
    simp at hy
  · intro u hu
    simp at hu

theorem step_safe (p : Protocol Ω P C O) (s : State Ω P) (hs : Safe p s)
    (a : Action P C) (ha : Allowed p s a) (d : Bool) : Safe p (step p s a d) := by
  cases a with
  | register x c =>
    have hpre : Ready s.completed x := (ha.resolve_left (by intro h; cases h)).2.2
    exact register_safe p s hs x c hpre
  | verify => exact verify_safe p s hs d
  | admit => exact admit_safe p s hs ((ha.resolve_left (by intro h; cases h)).2.2)
  | stop => exact ⟨hs.ideal, hs.certified, hs.generation, hs.paired, hs.ready, hs.receipt⟩

omit [DecidableEq P] in
/-- Verification rejection keeps the exact ticket and ownership for an explicitly
costed retry, while the belief is still updated on the rejection report. -/
theorem rejection_retains_candidate (p : Protocol Ω P C O) (s : State Ω P) :
    (verifyStep p s false).slot = s.slot ∧
    (verifyStep p s false).owner = s.owner ∧
    (verifyStep p s false).completed = s.completed ∧
    (verifyStep p s false).checked = none := ⟨rfl, rfl, rfl, rfl⟩

omit [DecidableEq P] in
theorem verify_never_admits (p : Protocol Ω P C O) (s : State Ω P) (d : Bool) :
    (verifyStep p s d).completed = s.completed := rfl

omit [DecidableEq P] in
theorem register_never_admits (p : Protocol Ω P C O) (s : State Ω P) (x : P) (c : C) :
    (registerStep p s x c).completed = s.completed := rfl

theorem admit_consumes (p : Protocol Ω P C O) (s : State Ω P)
    (ha : Precondition p s .admit) :
    (admitStep p s).slot.pending = none ∧ (admitStep p s).checked = none ∧
    (admitStep p s).owner = none := by
  obtain ⟨x, t, r, hx, ht, hr, hv⟩ := ha
  rw [admitStep_of_pass p s x t r hx ht hr hv]
  exact ⟨rfl, rfl, rfl⟩

omit [DecidableEq P] in
theorem admission_has_exact_ticket (p : Protocol Ω P C O) (s : State Ω P)
    (ha : Precondition p s .admit) : ∃ x t r,
    s.owner = some x ∧ s.slot.pending = some t ∧ s.checked = some r ∧
    r.subject = t ∧ t.artifact.identity = p.spec x ∧ Valid t.artifact := by
  obtain ⟨x, t, r, hx, ht, hr, hv⟩ := ha
  exact ⟨x, t, r, hx, ht, hr, validated_receipt _ _ _ hv,
    validated_identity _ _ _ hv, validated_artifact_valid _ _ _ hv⟩

theorem replay_admission_not_allowed (p : Protocol Ω P C O) (s : State Ω P)
    (ha : Precondition p s .admit) : ¬ Allowed p (admitStep p s) .admit := by
  intro h
  have hp := (h.resolve_left (by intro he; cases he)).2.2
  obtain ⟨x, t, r, hx, ht, hr, hv⟩ := hp
  rw [(admit_consumes p s ha).2.2] at hx
  cases hx

end Komorebi.AVOC.ArtifactWorkflow
