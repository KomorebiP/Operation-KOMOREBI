import AVOC.AdaptiveProbeControl

namespace Komorebi.AVOC.AdaptiveProbe.Examples

abbrev World := Fin 4
abbrev Probe := Fin 3

def detects (p : Probe) (w : World) : Bool :=
  if p = 0 then decide (w = 0 ∨ w = 1)
  else if p = 1 then decide (w = 2)
  else decide (w = 3)

def equalFeeModel : Model World Probe where
  detects := detects
  fee _ := 8
  fee_nonneg _ := by norm_num
  benefit := 40
  benefit_nonneg := by norm_num

def initial : State World Probe where
  worlds := Finset.univ
  worlds_nonempty := ⟨0,Finset.mem_univ _⟩
  remaining := [0,1,2]
  remaining_nodup := by decide
  done := false

def afterBroadFailure : State World Probe := afterFailure equalFeeModel initial 0

def afterBroadLeftFailure : State World Probe :=
  afterFailure equalFeeModel afterBroadFailure 1

/-- The broad probe covers two of the four uniform catalogue worlds. -/
theorem initial_broad_probability : successProb equalFeeModel initial 0 = 1/2 := by
  change (2 : ℚ) / 4 = 1 / 2
  norm_num

/-- Each singleton probe covers one initial world. -/
theorem initial_singleton_probability : successProb equalFeeModel initial 1 = 1/4 := by
  change (1 : ℚ) / 4 = 1 / 4
  norm_num

/-- After the broad failure, two worlds remain and the first singleton covers one. -/
theorem failure_singleton_probability :
    successProb equalFeeModel afterBroadFailure 1 = 1/2 := by
  change (1 : ℚ) / 2 = 1 / 2
  norm_num

/-- After the broad and first-singleton failures, the last probe is certain. -/
theorem final_probe_certain :
    successProb equalFeeModel afterBroadLeftFailure 2 = 1 := by
  change (1 : ℚ) / 1 = 1
  norm_num

/-- Probability alone is not enough: the same catalogue can have unequal probe fees. -/
def unequalFeeModel : Model World Probe where
  detects := detects
  fee p := if p = 0 then 25 else 1
  fee_nonneg p := by split <;> norm_num
  benefit := 40
  benefit_nonneg := by norm_num

/-- The broad probe has positive immediate net value under the equal-fee model. -/
theorem broad_immediate_positive : 0 < reward equalFeeModel initial (.probe 0) := by
  change 0 < successProb equalFeeModel initial 0 * equalFeeModel.benefit - equalFeeModel.fee 0
  rw [initial_broad_probability]
  norm_num [equalFeeModel]

/-- The same catalogue probabilities hold when only the fees change. -/
theorem unequal_broad_probability : successProb unequalFeeModel initial 0 = 1/2 := by
  change (2 : ℚ) / 4 = 1 / 2
  norm_num

theorem unequal_singleton_probability : successProb unequalFeeModel initial 1 = 1/4 := by
  change (1 : ℚ) / 4 = 1 / 4
  norm_num

/-- The same broad probe has negative immediate net value when its fee is raised. -/
theorem expensive_broad_immediate_negative : reward unequalFeeModel initial (.probe 0) < 0 := by
  change successProb unequalFeeModel initial 0 * unequalFeeModel.benefit - unequalFeeModel.fee 0 < 0
  rw [unequal_broad_probability]
  norm_num [unequalFeeModel]

/-- A singleton remains profitable in the unequal-fee model. -/
theorem cheap_singleton_immediate_positive : 0 < reward unequalFeeModel initial (.probe 1) := by
  change 0 < successProb unequalFeeModel initial 1 * unequalFeeModel.benefit - unequalFeeModel.fee 1
  rw [unequal_singleton_probability]
  norm_num [unequalFeeModel]

/-- Every executed positive-depth choice is feasible and Bellman-optimal; exact
numeric choices for this catalogue are additionally checked by the executable regression. -/
theorem example_selected_is_optimal (n : Nat) :
    let a := selected equalFeeModel n initial
    a ∈ (system equalFeeModel).actions initial ∧
      Guarded.qValue (system equalFeeModel) n initial a =
        Guarded.value (system equalFeeModel) (n + 1) initial := by
  exact ⟨selected_allowed equalFeeModel n initial,
    selected_realizes_value equalFeeModel n initial⟩

end Komorebi.AVOC.AdaptiveProbe.Examples
