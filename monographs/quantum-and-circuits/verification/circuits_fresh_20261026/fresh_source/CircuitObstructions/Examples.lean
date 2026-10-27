import CircuitObstructions.CutComparison

/-! Constructive witnesses and a refuted target-only shortcut. -/
namespace CircuitObstructions.Examples

inductive WorkWire where
  | left | right | scratch | target
  deriving DecidableEq, Repr

def andBoundary : Boundary (Bool × Bool) WorkWire where
  encode x y
    | .left => x.1
    | .right => x.2
    | .scratch => false
    | .target => y
  target := .target
  target_eq := by intros; rfl

def andCompute : Circuit WorkWire :=
  [.toffoli .left .right .scratch (by decide) (by decide) (by decide)]

def andCopy : Circuit WorkWire := [.cnot .scratch .target (by decide)]

def andOracle : Circuit WorkWire := andCompute ++ andCopy ++ andCompute

/-- Explicit dirty-workspace compute/copy/uncompute oracle for conjunction. -/
theorem andOracle_restores :
    Restores andBoundary andOracle (fun x => x.1 && x.2) := by
  intro x y
  rcases x with ⟨a, b⟩
  cases a <;> cases b <;> cases y <;> funext i <;> cases i <;> rfl

theorem andOracle_toffoli_count : toffoliCount andOracle = 2 := rfl

/-- The scratch bit need not be zero between the endpoints. -/
theorem and_scratch_can_be_dirty :
    run andCompute (andBoundary.encode (true, true) false) .scratch = true := rfl

/-- Every cut of this explicit circuit is an instance of the universal C01 theorem. -/
theorem andOracle_every_cut (k : Nat) (x : Bool × Bool) :
    (x.1 && x.2) = true ↔
      ∃ i, packet andBoundary (andOracle.take k) (andOracle.drop k) x i = true :=
  every_index_cut andBoundary andOracle (fun x => x.1 && x.2) andOracle_restores k x

inductive SwapWire where
  | data | target
  deriving DecidableEq, Repr

def swapBoundary : Boundary Bool SwapWire where
  encode x y
    | .data => x
    | .target => y
  target := .target
  target_eq := by intros; rfl

def swapCircuit : Circuit SwapWire :=
  [.cnot .data .target (by decide),
   .cnot .target .data (by decide),
   .cnot .data .target (by decide)]

def swapSuffix : Circuit SwapWire := [.not .data] ++ swapCircuit

def outputActiveOracle : Circuit SwapWire := swapCircuit ++ swapSuffix

/-- The target is genuinely used as a control in a restored oracle. -/
theorem outputActiveOracle_restores :
    Restores swapBoundary outputActiveOracle (fun _ => true) := by
  intro x y
  cases x <;> cases y <;> funext i <;> cases i <;> rfl

theorem outputActiveOracle_length : outputActiveOracle.length = 7 := rfl

theorem outputActiveOracle_toffoli_count : toffoliCount outputActiveOracle = 0 := rfl

/-- At this cut the discrepancy is in the data wire, not in the named target. -/
theorem moved_discrepancy_data (x : Bool) :
    packet swapBoundary swapCircuit swapSuffix x .data = true := by
  cases x <;> rfl

theorem moved_discrepancy_target (x : Bool) :
    packet swapBoundary swapCircuit swapSuffix x .target = false := by
  cases x <;> rfl

/-- A concrete refutation of replacing the complete register comparison by target-only comparison. -/
theorem target_only_reconstruction_is_false :
    ¬ (∀ x : Bool, packet swapBoundary swapCircuit swapSuffix x .target = true) := by
  intro h
  have hh := h false
  rw [moved_discrepancy_target] at hh
  contradiction

/-- Dropping target separation permits a vacuous endpoint equation for the wrong function. -/
theorem degenerate_encoding_control :
    let bad : Bool → State SwapWire := fun _ _ => false
    (∀ y, run ([] : Circuit SwapWire) (bad y) = bad (Bool.xor y true)) ∧
    (∀ i, Bool.xor (bad false i) (bad false i) = false) := by
  constructor <;> intros <;> rfl

end CircuitObstructions.Examples
