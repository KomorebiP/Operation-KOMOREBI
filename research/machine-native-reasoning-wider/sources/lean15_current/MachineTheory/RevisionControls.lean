import MachineTheory.RevisionExamples
import MachineTheory.PrefixExamples

/-! # Boundaries of selective certificate reuse

Staleness is an exact syntactic dependency-closure result, not a semantic refutation.
The false registry and cyclic example are intentionally not admitted as sound old proofs.
-/
namespace Komorebi.MachineTheory.RevisionControls
open Dependency RevisionExamples HardInquiry BinaryDiagnosis BinaryExamples Finset

/-- The omitted second input is a real value, not an unresolved hash collision. -/
def omitted : Graph Unit Bool where
  parents := fun _ => ∅
  direct := fun _ => {false}

def zeroState : Bool → Bool := fun _ => false

def changedSecond : Bool → Bool := id

theorem omitted_dependency :
    omitted.view zeroState () = omitted.view changedSecond () ∧
    omitted.stale zeroState changedSecond = ∅ ∧
    zeroState false = zeroState true ∧ changedSecond false ≠ changedSecond true := by
  refine ⟨?_,by decide,rfl,by decide⟩
  funext i
  have hi : i.val=false := by simpa [omitted] using i.property
  simp [Graph.view,zeroState,changedSecond,hi]

/-- No semantically complete declaration can justify the missing-dependency claim. -/
theorem omitted_not_complete :
    ¬ (∀ a b : Bool → Bool, omitted.view a () = omitted.view b () →
      (a false=a true ↔ b false=b true)) := by
  intro hc
  have hh := (hc zeroState changedSecond omitted_dependency.1).mp rfl
  exact omitted_dependency.2.2.2 hh

/-- A local-only unchecked test can pass even while the intended equality is false. -/
def incompleteCheck (a : {i // i ∈ omitted.direct ()} → Bool) : Bool := !a ⟨false,by decide⟩

theorem flawless_local_replay_can_be_wrong :
    incompleteCheck (omitted.view zeroState ()) = true ∧
    incompleteCheck (omitted.view changedSecond ()) = true ∧
    changedSecond false ≠ changedSecond true := by decide

/-- Exact copies of printed names carry no implication of value equality. -/
theorem same_name_not_same_artifact :
    ("repair" : String) = "repair" ∧
    ¬ Scope universalRepair ∧ Scope eight :=
  ⟨rfl,universal_not_scope,eight_scope⟩

/-- A cyclic pair of implications does not establish either false premise. -/
def cyclic : Graph Bool Unit where
  parents := fun v => {!v}
  direct := fun _ => ∅

def cyclicSystem : System cyclic (fun _ => Bool) (fun _ => Bool) where
  claim := fun _ _ => False
  external := fun _ _ => True
  check := fun _ _ w => w
  sound := by
    intro a v _ _ _ hp
    exact hp (!v) (by simp [cyclic])

theorem cycle_has_no_rank : ¬ ∃ r : Bool → ℕ, cyclic.Ranked r := by
  rintro ⟨r,hr⟩
  have h0 := hr false true (by simp [cyclic])
  have h1 := hr true false (by simp [cyclic])
  omega

theorem cyclic_flags_are_not_proofs :
    (∀ v, cyclicSystem.check v (cyclic.view (fun _ => false) v) true = true) ∧
    ¬ (∀ v, cyclicSystem.Established (fun _ => false) v true) := by
  refine ⟨fun _ => rfl,?_⟩
  intro h
  exact (h false).2.2

theorem cycle_guard_rejects (r : Bool → ℕ) :
    replayGuard cyclic (fun _ => false) (fun _ => false) (fun _ => true) r = false := by
  apply Bool.eq_false_iff.mpr
  intro h
  exact cycle_has_no_rank ⟨r,((replayGuard_iff _ _ _ _ _).mp h).1⟩

/-- Guard refusal is not a proof that a sound independent arithmetic fact is false. -/
theorem bad_order_rejected :
    replayGuard graph before repairAdded externalOK (fun _ => 0) = false ∧
    system.claim repairAdded 0 := by
  refine ⟨by decide,?_⟩
  intro n
  simp

/-- Unchanged claims with unavailable external assurance cannot be admitted for copying. -/
theorem external_guard_rejects :
    system.checkedFinish before before oldWitness allFresh (fun _ => false) rank = none := by
  unfold System.checkedFinish
  have hg : replayGuard graph before before (fun _ => false) rank = false := by decide
  rw [hg]
  rfl

/-- A false submitted witness is rejected even when the mathematical claim happens to be true. -/
def badFresh : Node → Option Bool := fun v => if v=3 then some false else some true

def rejectedRun := system.finish before repairAdded oldWitness badFresh externalOK rank

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
theorem rejection_not_false : rejectedRun 3 = .rejected ∧ system.claim repairAdded 3 := by
  exact ⟨by decide,by change universalRepair.Valid 3 univ balanced; decide⟩

set_option maxRecDepth 8192 in
set_option maxHeartbeats 2000000 in
theorem unchecked_parent_blocks_true_child :
    rejectedRun 4 = .blockedParents ∧ system.claim repairAdded 4 := by
  exact ⟨by decide,missing_is_not_false.2⟩

/-- Stale is not false: the controller remains valid while its justification is re-established. -/
theorem stale_can_remain_true : (3 : Node) ∈ graph.stale before repairAdded ∧
    system.claim repairAdded 3 :=
  ⟨by decide,rejection_not_false.2⟩

/-- Direct-only invalidation misses the unmodified-profile descendant. -/
theorem closure_is_necessary : (4 : Node) ∉ graph.changedRoots before repairAdded ∧
    (4 : Node) ∈ graph.stale before repairAdded := by decide

/-- A supplied local flag cannot bypass unavailable parent evidence. -/
theorem parent_required_for_local_return :
    system.evaluate repairAdded allFresh externalOK (fun _ => .pending) 2 = .blockedParents ∧
    system.check 2 (graph.view repairAdded 2) true = true := by decide

/-- Changing a query order has an actual literal-controller consequence in Block10. -/
theorem query_order_is_semantic_input :
    (OrderedCompiler.search OrderedCompiler.streamScanner three [0,1,2] [0,1,2] 2 [0,1,2]).answer ≠
    (OrderedCompiler.search OrderedCompiler.streamScanner three [1,0,2] [0,1,2] 2 [0,1,2]).answer :=
  PrefixExamples.query_order_changes_tree

/-- A fingerprint not proved injective cannot replace equality of declared values. -/
theorem constant_digest_not_identity :
    (fun _ : Bool => (0 : ℕ)) false = (fun _ : Bool => (0 : ℕ)) true ∧
    false ≠ true := by decide

end Komorebi.MachineTheory.RevisionControls
