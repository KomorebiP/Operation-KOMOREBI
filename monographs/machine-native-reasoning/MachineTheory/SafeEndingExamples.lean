import MachineTheory.SafeEndingPolicies
import Mathlib.Tactic.FinCases

/-! Exact, kernel-checked examples and boundary controls for Core 8.3. -/
namespace Komorebi.MachineTheory.SafeEnding.Examples

/-- 0 is a goal, 1 can stop now but loses that option when running,
and 2 can run safely forever without an ending. -/
def threeState : Model (Fin 3) Bool where
  safe := Finset.univ
  goal := {0}
  goal_safe := Finset.subset_univ _
  run := fun _ => {false}
  finish := fun x => if x = 2 then ∅ else {true}
  post := fun x a => if a then {0} else if x = 0 then {0} else {2}
  post_nonempty := by
    intro x a _
    cases a with
    | false => by_cases hx : x = 0 <;> simp [hx]
    | true => simp

theorem three_end_stage : endStage threeState 1 = {0, 1} := by
  ext x
  fin_cases x <;> simp [endStage_succ, endStage_zero, endStep, threeState]

theorem three_end_fixed : endStep threeState (endStage threeState 1) = endStage threeState 1 := by
  rw [three_end_stage]
  ext x
  fin_cases x <;> simp [endStep, threeState]

theorem three_ending : endingRegion threeState = {0, 1} :=
  (endingRegion_eq_of_stage_fixed threeState 1 three_end_fixed).trans three_end_stage

theorem three_run_stage : runStage threeState 1 = {0} := by
  rw [runStage_succ, runStage_zero, three_ending]
  ext x
  fin_cases x <;> simp [runStep, threeState]

theorem three_run_fixed : runStep threeState (runStage threeState 1) = runStage threeState 1 := by
  rw [three_run_stage]
  ext x
  fin_cases x <;> simp [runStep, threeState]

theorem three_running : runningRegion threeState = {0} :=
  (runningRegion_eq_of_stage_fixed threeState 1 three_run_fixed).trans three_run_stage

theorem ready_rank : endRank threeState 1 = 1 := by
  have hx : (1 : Fin 3) ∈ endingRegion threeState := by simp [three_ending]
  have hle : endRank threeState 1 ≤ 1 := endRank_min threeState (n := 1) (by rw [three_end_stage]; simp)
  have hn : endRank threeState 1 ≠ 0 := by
    intro h
    have hg := (endRank_zero_iff threeState hx).mp h
    simp [threeState] at hg
  omega

theorem ready_can_stop : ∃ σ, EndingGuarantee threeState σ 1 :=
  (ending_region_iff threeState 1).mp (by simp [three_ending])

theorem ready_cannot_preserve_ending : ¬ ∃ P, SwitchingGuarantee threeState P 1 := by
  rw [← safe_continuation_iff, three_running]
  simp

theorem trap_can_run : RunningGuarantee threeState (fun _ => some false) 2 := by
  intro c _
  exact ⟨Finset.mem_univ _, false, rfl, by simp [threeState]⟩

theorem trap_cannot_end : ¬ ∃ σ, EndingGuarantee threeState σ 2 := by
  rw [← ending_region_iff, three_ending]
  simp

/-- Empty catalogues are permitted, but are not winning policies. -/
def deadlock : Model Unit Unit where
  safe := Finset.univ
  goal := ∅
  goal_safe := Finset.empty_subset _
  run := fun _ => ∅
  finish := fun _ => ∅
  post := fun _ _ => ∅
  post_nonempty := by simp

theorem deadlock_no_running (σ : Strategy Unit Unit) : ¬ RunningGuarantee deadlock σ () := by
  intro h
  obtain ⟨a, _, ha⟩ := (h (start ()) Reach.refl).2
  simp [deadlock] at ha

theorem deadlock_no_ending (σ : Strategy Unit Unit) : ¬ EndingGuarantee deadlock σ () := by
  intro h
  obtain ⟨a, _, ha⟩ := (h.total (start ()) Reach.refl).2 (by simp [deadlock, start])
  simp [deadlock] at ha

/-- Swapping action and successor quantifiers would allow hindsight. -/
theorem hindsight_is_stronger :
    (∀ y : Bool, ∃ a : Bool, a = y) ∧ ¬ (∃ a : Bool, ∀ y : Bool, a = y) := by decide

/-- A winning history-dependent ending may wait longer than the minimal rank.
Only the constructed rank strategy receives the first-entry-rank time bound. -/
def waitModel : Model Bool Bool where
  safe := Finset.univ
  goal := {false}
  goal_safe := Finset.subset_univ _
  run := fun _ => {false}
  finish := fun _ => Finset.univ
  post := fun x a => {if a then false else x}
  post_nonempty := by intro x a _; exact Finset.singleton_nonempty _

def delayStrategy : Strategy Bool Bool := fun c => some (if c.1 = [] then false else true)

theorem wait_end_stage : endStage waitModel 1 = Finset.univ := by
  ext x
  cases x <;> simp [endStage_succ, endStage_zero, endStep, waitModel]

theorem wait_ending : endingRegion waitModel = Finset.univ := by
  have hf : endStep waitModel (endStage waitModel 1) = endStage waitModel 1 := by
    rw [wait_end_stage]
    ext x
    simp [endStep]
  exact (endingRegion_eq_of_stage_fixed waitModel 1 hf).trans wait_end_stage

theorem wait_rank : endRank waitModel true = 1 := by
  have hx : true ∈ endingRegion waitModel := by simp [wait_ending]
  have hle : endRank waitModel true ≤ 1 := endRank_min waitModel (n := 1) (by rw [wait_end_stage]; simp)
  have hn : endRank waitModel true ≠ 0 := by
    intro h
    have hg := (endRank_zero_iff waitModel hx).mp h
    simp [waitModel] at hg
  omega

theorem delay_guarantee : EndingGuarantee waitModel delayStrategy true := by
  refine ⟨?_, ?_⟩
  · intro c _
    refine ⟨Finset.mem_univ _, ?_⟩
    intro _
    exact ⟨if c.1 = [] then false else true, rfl, Finset.mem_univ _⟩
  · intro p _ hp
    obtain ⟨_, a, _, _, hh, _⟩ := hp 0
    have hn : (p 1).1 ≠ [] := by rw [hh]; simp
    obtain ⟨_, b, hb, _, _, hy⟩ := hp 1
    have hb' : b = true := by
      simpa [delayStrategy, hn] using hb.symm
    subst b
    have hgoal : (p 2).2 ∈ waitModel.goal := by simpa [waitModel] using hy
    exact (hp 2).1 hgoal

def delayFirst : Config Bool Bool := ([(true, false)], true)
def delayLast : Config Bool Bool := ([(true, true), (true, false)], false)

theorem delay_first_step : endEdge waitModel delayStrategy (start true) delayFirst := by
  exact ⟨by decide, false, rfl, by decide, rfl, by decide⟩

theorem delay_second_step : endEdge waitModel delayStrategy delayFirst delayLast := by
  exact ⟨by decide, true, rfl, by decide, rfl, by decide⟩

theorem winning_policy_need_not_take_minimal_time :
    EndingGuarantee waitModel delayStrategy true ∧
    endEdge waitModel delayStrategy (start true) delayFirst ∧
    endEdge waitModel delayStrategy delayFirst delayLast ∧
    2 > endRank waitModel true := by
  exact ⟨delay_guarantee, delay_first_step, delay_second_step, by rw [wait_rank]; decide⟩

end Komorebi.MachineTheory.SafeEnding.Examples
