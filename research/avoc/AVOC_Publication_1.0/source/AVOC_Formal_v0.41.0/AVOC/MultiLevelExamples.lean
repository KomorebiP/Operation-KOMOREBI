import AVOC.MultiLevelInformation

namespace Komorebi.AVOC.MultiLevel.Examples

abbrev World := Fin 4
abbrev Probe := Fin 2


def detects (p : Probe) (w : World) : Bool :=
  if p = 0 then decide (w ≠ 0)
  else decide (w = 2 ∨ w = 3)


def rank : World → Nat
  | 0 => 0
  | 1 => 1
  | 2 => 2
  | 3 => 2


def coldPayoff : World → ℚ
  | 0 => 20
  | 1 => 12
  | 2 => -3
  | 3 => -10


def model : Model World Probe where
  detects := detects
  level p := if p = 0 then 1 else 2
  fee _ := 1
  fee_nonneg _ := by norm_num
  reuseAvailable := true
  reusePayoff _ := 4
  coldPayoff := coldPayoff


def initial : State model where
  worlds := Finset.univ
  worlds_nonempty := ⟨0,Finset.mem_univ _⟩
  remaining := [0,1]
  remaining_nodup := by decide
  lower := 0
  done := false


def afterEntrySuccess : State model := afterSuccess model initial 0

def afterMinorSuccess : State model := afterSuccess model initial 1

def afterMinorFailure : State model := afterFailure model initial 1


theorem initial_entry_probability : successProb model initial 0 = 3/4 := by
  change (3 : ℚ) / 4 = 3 / 4
  rfl


theorem initial_minor_probability : successProb model initial 1 = 1/2 := by
  change (2 : ℚ) / 4 = 1 / 2
  norm_num


theorem initial_reuse_value : reward model initial .reuse = 4 := by
  change average model initial (fun _ => (4 : ℚ)) = 4
  exact average_const model initial 4


theorem entry_success_floor : afterEntrySuccess.lower = 1 := by
  rfl


theorem minor_success_floor : afterMinorSuccess.lower = 2 := by
  rfl


theorem minor_failure_floor : afterMinorFailure.lower = 0 := by
  rfl

/-- The executable planner's chosen action is always feasible and realizes the
finite-horizon Bellman value. Exact numeric choices are additionally checked by
the runtime regression. -/
theorem selected_is_optimal (n : Nat) :
    let a := selected model n initial
    a ∈ (system model).actions initial ∧
      Guarded.qValue (system model) n initial a = Guarded.value (system model) (n+1) initial := by
  exact ⟨selected_allowed model n initial, selected_realizes_value model n initial⟩

end Komorebi.AVOC.MultiLevel.Examples
