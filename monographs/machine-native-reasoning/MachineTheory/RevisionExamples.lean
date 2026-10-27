import MachineTheory.RevisionAdmission
import MachineTheory.BinaryExamples

/-! # Actual controller-scope revision

The artifacts select the inherited eight-case repair language, an installed controller,
and the exact expected profile attached to its record. Claim 2 is the general lower
bound for the actual model, not a supplied Boolean named "lower bound".
-/
namespace Komorebi.MachineTheory.RevisionExamples
open Dependency HardInquiry BinaryDiagnosis BinaryExamples Finset

abbrev Node := Fin 5
abbrev Input := Fin 3
abbrev Data := Input → Bool

/-- 0 equation; 1 counting scope; 2 leaf bound; 3 controller validity; 4 bound profile. -/
def graph : Graph Node Input where
  parents := fun v => if v=2 then {1} else if v=4 then {3} else ∅
  direct := fun v => if v=1 then {0} else if v=3 then {0,1} else if v=4 then {1,2} else ∅

def rank (v : Node) : ℕ := if v=2 ∨ v=4 then 1 else 0

theorem rank_checked : graph.Ranked rank := by
  unfold Graph.Ranked
  decide

/-- Only the success predicate differs between these already formalized models. -/
def selectedModel (u : Bool) : Model World Query Bool World Unit :=
  if u then universalRepair else eight

def selectedTree (small : Bool) : Tree Query Bool World 3 :=
  if small then .inl (false,false,false) else balanced

def expectedProfile (small : Bool) : Profile Unit :=
  if small then (fun _ => 1,1) else (fun _ => 4,15)

def actualProfile (small : Bool) : Profile Unit := eight.profile 3 univ (selectedTree small)

theorem profile_independent_of_repair_scope (u small : Bool) :
    (selectedModel u).profile 3 univ (selectedTree small) = actualProfile small := by
  cases u <;> cases small <;> rfl

/-- The actual source bound quantifies over arbitrary supports and finite horizons. -/
def Lower (u : Bool) : Prop :=
  ∀ h V (t : Tree Query Bool World h), (selectedModel u).Valid h V t →
    lowerProfile V.card ≤ (selectedModel u).profile h V t

theorem lower_from_scope (u : Bool) (hs : Scope (selectedModel u)) : Lower u := by
  intro h V t ht
  exact lowerProfile_le _ hs h V t ht

theorem universal_breaks_old_bound : ¬ Lower true := by
  intro h
  have hh := h 0 univ (false,false,false) universal_repair_small.1
  have no : ¬ lowerProfile (univ : Finset World).card ≤
      universalRepair.profile 0 univ (false,false,false) := by decide
  exact no hh

theorem lower_iff_scope (u : Bool) : Lower u ↔ Scope (selectedModel u) := by
  constructor
  · intro h
    cases u with
    | false => exact eight_scope
    | true => exact False.elim (universal_breaks_old_bound h)
  · exact lower_from_scope u

def meaning (a : Data) (v : Node) : Prop :=
  if v=0 then (∀ n : ℕ, max n 0 = n)
  else if v=1 then Scope (selectedModel (a 0))
  else if v=2 then Lower (a 0)
  else if v=3 then (selectedModel (a 0)).Valid 3 univ (selectedTree (a 1))
  else (selectedModel (a 0)).Valid 3 univ (selectedTree (a 1)) ∧
    (selectedModel (a 0)).profile 3 univ (selectedTree (a 1)) = expectedProfile (a 2)

/-- Witness true asks the actual checker to validate this instance; false is malformed. -/
def localCheck : (v : Node) → ({i // i ∈ graph.direct v} → Bool) → Bool → Bool
  | ⟨0,_⟩, _, w => w
  | ⟨1,_⟩, a, w => w && checkScope (selectedModel (a ⟨0,by simp [graph,Fin.ext_iff]⟩))
  | ⟨2,_⟩, _, w => w
  | ⟨3,_⟩, a, w => w && decide ((selectedModel (a ⟨0,by simp [graph,Fin.ext_iff]⟩)).Valid 3 univ
      (selectedTree (a ⟨1,by simp [graph,Fin.ext_iff]⟩)))
  | ⟨4,_⟩, a, w => w && decide (actualProfile (a ⟨1,by simp [graph,Fin.ext_iff]⟩) = expectedProfile (a ⟨2,by simp [graph,Fin.ext_iff]⟩))
  | ⟨n+5,h⟩, _, _ => False.elim (by omega)

def system : System graph (fun _ => Bool) (fun _ => Bool) where
  claim := meaning
  external := fun _ _ => True
  check := localCheck
  sound := by
    intro a v w hc _ hp
    fin_cases v
    · intro n
      simp
    · change (w && checkScope (selectedModel (a 0))) = true at hc
      exact (checkScope_iff _).mp (Bool.and_eq_true_iff.mp hc).2
    · have hs : Scope (selectedModel (a 0)) := hp 1 (by decide)
      exact lower_from_scope (a 0) hs
    · change (w && decide ((selectedModel (a 0)).Valid 3 univ (selectedTree (a 1)))) = true at hc
      have hv : (selectedModel (a 0)).Valid 3 univ (selectedTree (a 1)) :=
        of_decide_eq_true (Bool.and_eq_true_iff.mp hc).2
      exact hv
    · have hv : (selectedModel (a 0)).Valid 3 univ (selectedTree (a 1)) := hp 3 (by decide)
      change (w && decide (actualProfile (a 1) = expectedProfile (a 2))) = true at hc
      exact ⟨hv,(profile_independent_of_repair_scope (a 0) (a 1)).trans
        (of_decide_eq_true (Bool.and_eq_true_iff.mp hc).2)⟩

/-- The supplied registry is proved complete for these actual five claim meanings. -/
theorem meanings_complete : system.Complete := by
  intro a b v hview hp _
  fin_cases v
  · rfl
  · have h0 : a 0=b 0 := congrFun hview ⟨0,by decide⟩
    change Scope (selectedModel (a 0)) ↔ Scope (selectedModel (b 0))
    rw [h0]
  · change Lower (a 0) ↔ Lower (b 0)
    rw [lower_iff_scope,lower_iff_scope]
    exact hp 1 (by decide)
  · have h0 : a 0=b 0 := congrFun hview ⟨0,by decide⟩
    have h1 : a 1=b 1 := congrFun hview ⟨1,by decide⟩
    change (selectedModel (a 0)).Valid 3 univ (selectedTree (a 1)) ↔
      (selectedModel (b 0)).Valid 3 univ (selectedTree (b 1))
    rw [h0,h1]
  · have h1 : a 1=b 1 := congrFun hview ⟨1,by decide⟩
    have h2 : a 2=b 2 := congrFun hview ⟨2,by decide⟩
    have hvalid := hp 3 (by decide)
    change (selectedModel (a 0)).Valid 3 univ (selectedTree (a 1)) ↔
      (selectedModel (b 0)).Valid 3 univ (selectedTree (b 1)) at hvalid
    change ((selectedModel (a 0)).Valid 3 univ (selectedTree (a 1)) ∧
        (selectedModel (a 0)).profile 3 univ (selectedTree (a 1)) = expectedProfile (a 2)) ↔
      ((selectedModel (b 0)).Valid 3 univ (selectedTree (b 1)) ∧
        (selectedModel (b 0)).profile 3 univ (selectedTree (b 1)) = expectedProfile (b 2))
    rw [profile_independent_of_repair_scope,profile_independent_of_repair_scope]
    apply and_congr hvalid
    rw [h1,h2]

def before : Data := fun _ => false

def repairAdded : Data := fun i => decide (i=0)

def replaced : Data := fun _ => true

def oldWitness : Node → Bool := fun _ => true

def allFresh : Node → Option Bool := fun _ => some true

def missingProfile : Node → Option Bool := fun v => if v=4 then none else some true

def externalOK : Node → Bool := fun _ => true

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
theorem old_checks : ∀ v, system.check v (graph.view before v) (oldWitness v)=true := by decide

/-- The pre-revision claims are established by sound rules, not by a stored PASS flag. -/
theorem old_established : ∀ v, system.Established before v (oldWitness v) :=
  system.established_from_checks rank rank_checked before oldWitness old_checks (fun _ => trivial)

theorem exact_changed_roots : graph.changedRoots before repairAdded = {1,3} ∧
    graph.stale before repairAdded = {1,2,3,4} := by decide

theorem exact_replacement_stale : graph.changedRoots before replaced = {1,3,4} ∧
    graph.stale before replaced = {1,2,3,4} := by decide

def afterAddition := system.finish before repairAdded oldWitness missingProfile externalOK rank

def afterReplacement := system.finish before replaced oldWitness allFresh externalOK rank

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
/-- Stale and false are distinct: the old balanced controller is still valid. -/
theorem addition_verdicts : afterAddition 0 = .reused true ∧
    afterAddition 1 = .rejected ∧ afterAddition 2 = .blockedParents ∧
    afterAddition 3 = .rechecked true ∧ afterAddition 4 = .missing := by decide

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
theorem replacement_verdicts : afterReplacement 0 = .reused true ∧
    afterReplacement 1 = .rejected ∧ afterReplacement 2 = .blockedParents ∧
    afterReplacement 3 = .rechecked true ∧ afterReplacement 4 = .rechecked true := by decide

theorem addition_sound : system.SoundState repairAdded afterAddition :=
  system.finish_sound meanings_complete rank rank_checked before repairAdded oldWitness missingProfile
    externalOK old_established (fun _ _ => trivial) (fun _ _ => trivial)

theorem replacement_sound : system.SoundState replaced afterReplacement :=
  system.finish_sound meanings_complete rank rank_checked before replaced oldWitness allFresh
    externalOK old_established (fun _ _ => trivial) (fun _ _ => trivial)

/-- The still-true profile is missing evidence, not refuted by that procedural outcome. -/
theorem missing_is_not_false : afterAddition 4 = .missing ∧ system.claim repairAdded 4 := by
  refine ⟨addition_verdicts.2.2.2.2,?_⟩
  change universalRepair.Valid 3 univ balanced ∧ universalRepair.profile 3 univ balanced = (fun _ => 4,15)
  decide

/-- A new valid one-record controller gets a new actual profile, not the old (4,15). -/
theorem replacement_actual_controller :
    (selectedModel (replaced 0)).Valid 3 univ (selectedTree (replaced 1)) ∧
    (selectedModel (replaced 0)).profile 3 univ (selectedTree (replaced 1)) = (fun _ => 1,1) := by
  have h := (replacement_sound 4 true (by rw [replacement_verdicts.2.2.2.2]; rfl)).2.2
  exact h

/-- A stored old performance target is not repaired just by installing a valid controller. -/
def oldProfileTarget : Data := fun i => decide (i≠2)

def afterOldProfile := system.finish before oldProfileTarget oldWitness allFresh externalOK rank

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
theorem obsolete_profile_rejected : afterOldProfile 3 = .rechecked true ∧
    afterOldProfile 4 = .rejected ∧ ¬ system.claim oldProfileTarget 4 := by
  refine ⟨by decide,by decide,?_⟩
  intro h
  have falseProfile := h.2
  have no : ¬ universalRepair.profile 3 univ (.inl (false,false,false)) =
      (show Profile Unit from (fun _ => 4,15)) := by decide
  exact no falseProfile

/-- The unchanged equation survives the actual scope change through the generic theorem. -/
theorem equation_reused : system.Established replaced 0 true := by
  exact system.selective_reuse meanings_complete rank rank_checked before replaced oldWitness
    old_established (fun _ _ => trivial) 0 (by decide)

/-- No scope flag licenses the old lower bound after the success predicate changes. -/
theorem old_bound_now_false : ¬ system.claim repairAdded 2 := universal_breaks_old_bound

end Komorebi.MachineTheory.RevisionExamples
