import MachineTheory.PriceExamples
import MachineTheory.RevisionAdmission

/-! # Repricing preserves a controller but not its old benefit certificate

This instance uses Block 11's actual invalidation and replay. The program and
event semantics are fixed. Artifact false is an integer read price; artifact true
is a recorded integer saving, with test price fixed at one. A correct calculation
and a nonnegative advantage are deliberately different dependent claims.
-/
namespace Komorebi.MachineTheory.PriceRevision
open Dependency PriceExamples ResourcePrices Finset

abbrev Node := Fin 3
abbrev Data := Bool → ℤ

/-- Calculated directly from the inherited compiled event counters. -/
def actualSaving (r : ℤ) : ℤ :=
  r*(fullCounts false : ℤ)+(fullCounts true : ℤ) -
    (r*(streamCounts false : ℤ)+(streamCounts true : ℤ))

theorem actualSaving_eq (r : ℤ) : actualSaving r=31*r-153 := by
  rcases counter_binding with ⟨h0,h1,h2,h3⟩
  simp only [actualSaving,h0,h1,h2,h3]
  ring

/-- The exact integer quote agrees with the general real-price theorem. -/
theorem actualSaving_real (r : ℤ) :
    (actualSaving r : ℝ) = saving perUse (prices (r : ℝ) 1) := by
  rw [actualSaving_eq,priced_scan]
  push_cast
  ring

/-- Node 0: execution; node 1: correct quote; node 2: nonnegative advantage. -/
def graph : Graph Node Bool where
  parents := fun v => if v=2 then {1} else ∅
  direct := fun v => if v=0 then ∅ else if v=1 then univ else {true}

def rank (v : Node) : ℕ := v.val

theorem rank_checked : graph.Ranked rank := by
  unfold Graph.Ranked
  decide

def meaning (a : Data) (v : Node) : Prop :=
  if v=0 then
    PrefixExamples.streamEight.answer=PrefixExamples.fullEight.answer ∧
      ∀ t, PrefixExamples.streamEight.answer=some t → BinaryExamples.eight.Valid 3 univ t
  else if v=1 then a true=actualSaving (a false)
  else a true=actualSaving (a false) ∧ 0 ≤ a true

/-- The checker sees exactly the declared local view. -/
def localCheck : (v : Node) → ({i // i∈graph.direct v} → ℤ) → Bool → Bool
  | ⟨0,_⟩, _, w => w
  | ⟨1,_⟩, a, w => w && decide (a ⟨true,by change true ∈ graph.direct (1 : Node); decide⟩=actualSaving (a ⟨false,by change false ∈ graph.direct (1 : Node); decide⟩))
  | ⟨2,_⟩, a, w => w && decide (0 ≤ a ⟨true,by change true ∈ graph.direct (2 : Node); decide⟩)
  | ⟨n+3,h⟩, _, _ => False.elim (by omega)

def system : System graph (fun _ => ℤ) (fun _ => Bool) where
  claim := meaning
  external := fun _ _ => True
  check := localCheck
  sound := by
    intro a v w hc _ hp
    fin_cases v
    · exact same_valid_controller
    · change (w && decide (a true=actualSaving (a false)))=true at hc
      change a true=actualSaving (a false)
      exact of_decide_eq_true (Bool.and_eq_true_iff.mp hc).2
    · have hv : a true=actualSaving (a false) := hp 1 (by decide)
      change (w && decide (0 ≤ a true))=true at hc
      exact ⟨hv,of_decide_eq_true (Bool.and_eq_true_iff.mp hc).2⟩

/-- Semantic completeness is proved for this quote family, including invalid quotes. -/
theorem meanings_complete : system.Complete := by
  intro a b v hview hp _
  fin_cases v
  · rfl
  · have h0 : a false=b false := congrFun hview ⟨false,by decide⟩
    have h1 : a true=b true := congrFun hview ⟨true,by decide⟩
    change (a true=actualSaving (a false)) ↔ (b true=actualSaving (b false))
    rw [h0,h1]
  · have h1 : a true=b true := congrFun hview ⟨true,by decide⟩
    have hv := hp 1 (by decide)
    change (a true=actualSaving (a false)) ↔ (b true=actualSaving (b false)) at hv
    change (a true=actualSaving (a false) ∧ 0 ≤ a true) ↔
      (b true=actualSaving (b false) ∧ 0 ≤ b true)
    apply and_congr hv
    rw [h1]

def before : Data := fun i => if i then 2 else 5

def staleQuote : Data := fun i => if i then 2 else 1

def correctedQuote : Data := fun i => if i then -122 else 1

def oldWitness : Node → Bool := fun _ => true

def allFresh : Node → Option Bool := fun _ => some true

def externalOK : Node → Bool := fun _ => true

theorem old_checks : ∀ v, system.check v (graph.view before v) (oldWitness v)=true := by
  decide

/-- Every old certificate is established before any reuse is attempted. -/
theorem old_established : ∀ v,system.Established before v (oldWitness v) :=
  system.established_from_checks rank rank_checked before oldWitness old_checks (fun _ => trivial)

theorem reprice_propagates :
    graph.changedRoots before staleQuote={1} ∧ graph.stale before staleQuote={1,2} ∧
    graph.stale before correctedQuote={1,2} := by
  decide

def staleResult := system.finish before staleQuote oldWitness allFresh externalOK rank

def correctedResult := system.finish before correctedQuote oldWitness allFresh externalOK rank

/-- A still-positive old quote is rejected, and its apparent benefit cannot be used. -/
theorem stale_quote_outcomes :
    staleResult 0=.reused true ∧ staleResult 1=.rejected ∧ staleResult 2=.blockedParents := by
  decide

/-- A valid negative quote is re-established without inventing a benefit certificate. -/
theorem corrected_quote_outcomes :
    correctedResult 0=.reused true ∧ correctedResult 1=.rechecked true ∧ correctedResult 2=.rejected := by
  decide

/-- Soundness is inherited from the same generic replay, including all partial stages. -/
theorem every_stage_sound (a : Data) (n : ℕ) :
    system.SoundState a (system.replay before a oldWitness allFresh externalOK rank n) :=
  system.replay_sound meanings_complete rank rank_checked before a oldWitness allFresh externalOK
    old_established (fun _ _ => trivial) (fun _ _ => trivial) n

theorem restored_calculation : system.Established correctedQuote 1 true := by
  have hs := every_stage_sound correctedQuote (finishAt rank)
  apply hs 1 true
  change (correctedResult 1).witness?=some true
  rw [corrected_quote_outcomes.2.1]
  rfl

theorem benefit_now_false : ¬ system.claim correctedQuote 2 := by
  change ¬ (correctedQuote true=actualSaving (correctedQuote false) ∧ 0 ≤ correctedQuote true)
  norm_num [correctedQuote]

/-- Repricing has not changed the actual program returned by either compiler. -/
theorem execution_certificate_reused : system.Established correctedQuote 0 true := by
  have hs := every_stage_sound correctedQuote (finishAt rank)
  apply hs 0 true
  change (correctedResult 0).witness?=some true
  rw [corrected_quote_outcomes.1]
  rfl

/-- The restored quote is the actual real saving, including its negative sign. -/
theorem restored_negative_real_saving :
    saving perUse (prices (correctedQuote false : ℝ) 1)= (correctedQuote true : ℝ) ∧
      saving perUse (prices (correctedQuote false : ℝ) 1) < 0 := by
  have hq : correctedQuote true=actualSaving (correctedQuote false) := restored_calculation.2.2
  constructor
  · rw [← actualSaving_real,← hq]
  · rw [priced_scan]
    norm_num [correctedQuote]

end Komorebi.MachineTheory.PriceRevision
