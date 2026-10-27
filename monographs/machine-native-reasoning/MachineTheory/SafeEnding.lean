import MachineTheory.FiniteFixedPoints

/-! Core 8.3: the two actual finite fixed points and their policy witnesses.
The post sets of enabled actions are nonempty. An empty action catalogue is
permitted and represents a deadlock, not a vacuous successful transition.
The goal is reached at first arrival; no post-goal execution obligation is added.
-/
namespace Komorebi.MachineTheory.SafeEnding

open FiniteFixedPoints

universe u v

structure Model (Z : Type u) (A : Type v) where
  safe : Finset Z
  goal : Finset Z
  goal_safe : goal ⊆ safe
  run : Z → Finset A
  finish : Z → Finset A
  post : Z → A → Finset Z
  post_nonempty : ∀ x a, a ∈ run x ∨ a ∈ finish x → (post x a).Nonempty

variable {Z : Type u} {A : Type v}
noncomputable section

/-- An ending predecessor must select its action before its adversarial successor. -/
def endStep (M : Model Z A) (U : Finset Z) : Finset Z := by
  classical
  exact U ∪ M.safe.filter (fun x => ∃ a ∈ M.finish x, M.post x a ⊆ U)

theorem mem_endStep (M : Model Z A) (U : Finset Z) (x : Z) :
    x ∈ endStep M U ↔ x ∈ U ∨
      (x ∈ M.safe ∧ ∃ a ∈ M.finish x, M.post x a ⊆ U) := by
  classical
  simp only [endStep, Finset.mem_union, Finset.mem_filter]

theorem endStep_increasing (M : Model Z A) (U : Finset Z) : U ⊆ endStep M U :=
  fun x hx => (mem_endStep M U x).mpr (Or.inl hx)

def endStage (M : Model Z A) : ℕ → Finset Z := sequence (endStep M) M.goal

@[simp] theorem endStage_zero (M : Model Z A) : endStage M 0 = M.goal := rfl
@[simp] theorem endStage_succ (M : Model Z A) (n : ℕ) :
    endStage M (n + 1) = endStep M (endStage M n) := rfl

theorem endStage_safe (M : Model Z A) (n : ℕ) : endStage M n ⊆ M.safe := by
  induction n with
  | zero => exact M.goal_safe
  | succ n ih =>
    intro x hx
    rcases (mem_endStep M _ x).mp hx with old | new
    · exact ih old
    · exact new.1

theorem ending_stabilizes [Fintype Z] (M : Model Z A) :
    ∃ n ≤ Fintype.card Z - M.goal.card,
      endStep M (endStage M n) = endStage M n :=
  increasing_stabilization (endStep M) M.goal (endStep_increasing M)

def endIndex [Fintype Z] (M : Model Z A) : ℕ := by
  classical
  exact Nat.find (ending_stabilizes M)

def endingRegion [Fintype Z] (M : Model Z A) : Finset Z := endStage M (endIndex M)

theorem endIndex_bound [Fintype Z] (M : Model Z A) :
    endIndex M ≤ Fintype.card Z - M.goal.card := by
  classical
  exact (Nat.find_spec (ending_stabilizes M)).1

theorem endingRegion_fixed [Fintype Z] (M : Model Z A) :
    endStep M (endingRegion M) = endingRegion M := by
  classical
  exact (Nat.find_spec (ending_stabilizes M)).2

theorem endingRegion_safe [Fintype Z] (M : Model Z A) : endingRegion M ⊆ M.safe :=
  endStage_safe M (endIndex M)

theorem endStage_subset_region [Fintype Z] (M : Model Z A) (n : ℕ) :
    endStage M n ⊆ endingRegion M := by
  induction n with
  | zero =>
    have hs : ∀ k, M.goal ⊆ endStage M k := by
      intro k
      induction k with
      | zero => exact Finset.Subset.refl _
      | succ k ih => exact Finset.Subset.trans ih (endStep_increasing M _)
    exact hs (endIndex M)
  | succ n ih =>
    intro x hx
    rcases (mem_endStep M _ x).mp hx with old | new
    · exact ih old
    · have h : x ∈ endStep M (endingRegion M) := by
        apply (mem_endStep M _ x).mpr
        right
        obtain ⟨hs, a, ha, hp⟩ := new
        exact ⟨hs, a, ha, Finset.Subset.trans hp ih⟩
      rwa [endingRegion_fixed] at h

theorem goal_subset_region [Fintype Z] (M : Model Z A) : M.goal ⊆ endingRegion M :=
  endStage_subset_region M 0

theorem endingRegion_of_pre [Fintype Z] (M : Model Z A) {x : Z} {a : A}
    (hs : x ∈ M.safe) (ha : a ∈ M.finish x) (hp : M.post x a ⊆ endingRegion M) :
    x ∈ endingRegion M := by
  have h := (mem_endStep M (endingRegion M) x).mpr (Or.inr ⟨hs, a, ha, hp⟩)
  rwa [endingRegion_fixed] at h

/-- Every chosen ending action at a safe state outside the attractor has a real
successor outside it. No successor is selected before the action is known. -/
theorem outside_successor [Fintype Z] (M : Model Z A) {x : Z} {a : A}
    (hs : x ∈ M.safe) (hx : x ∉ endingRegion M) (ha : a ∈ M.finish x) :
    ∃ y ∈ M.post x a, y ∉ endingRegion M := by
  classical
  by_contra h
  apply hx
  apply endingRegion_of_pre M hs ha
  intro y hy
  by_contra hn
  exact h ⟨y, hy, hn⟩

/-- First-entry rank is defined on all states, with the unused outside value zero. -/
def endRank [Fintype Z] (M : Model Z A) (x : Z) : ℕ := by
  classical
  exact if hx : x ∈ endingRegion M then
    Nat.find (show ∃ n, x ∈ endStage M n from ⟨endIndex M, hx⟩)
  else 0

theorem endRank_spec [Fintype Z] (M : Model Z A) {x : Z} (hx : x ∈ endingRegion M) :
    x ∈ endStage M (endRank M x) := by
  classical
  simp only [endRank, dite_eq_left hx]
  exact Nat.find_spec (show ∃ n, x ∈ endStage M n from ⟨endIndex M, hx⟩)

theorem endRank_min [Fintype Z] (M : Model Z A) {x : Z} {n : ℕ}
    (hn : x ∈ endStage M n) : endRank M x ≤ n := by
  classical
  have hx := endStage_subset_region M n hn
  simp only [endRank, dite_eq_left hx]
  exact Nat.find_min' _ hn

theorem endRank_bound [Fintype Z] (M : Model Z A) {x : Z} (hx : x ∈ endingRegion M) :
    endRank M x ≤ Fintype.card Z - M.goal.card :=
  le_trans (endRank_min M hx) (endIndex_bound M)

theorem endRank_zero_iff [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ endingRegion M) : endRank M x = 0 ↔ x ∈ M.goal := by
  constructor
  · intro hz
    have hs := endRank_spec M hx
    rwa [hz, endStage_zero] at hs
  · intro hg
    exact Nat.eq_zero_of_le_zero (endRank_min M (n := 0) hg)

/-- A single action lowers rank for every successor, not one action per successor. -/
theorem rank_action [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ endingRegion M) (hg : x ∉ M.goal) :
    ∃ a ∈ M.finish x, ∀ y ∈ M.post x a,
      y ∈ endingRegion M ∧ endRank M y < endRank M x := by
  cases hr : endRank M x with
  | zero => exact False.elim (hg ((endRank_zero_iff M hx).mp hr))
  | succ n =>
    have hm := endRank_spec M hx
    rw [hr, endStage_succ] at hm
    rcases (mem_endStep M _ x).mp hm with old | new
    · have hle := endRank_min M old
      omega
    · obtain ⟨_, a, ha, hp⟩ := new
      refine ⟨a, ha, ?_⟩
      intro y hy
      have hs := hp hy
      refine ⟨endStage_subset_region M n hs, ?_⟩
      have hle := endRank_min M hs
      omega

def endingAction [Fintype Z] (M : Model Z A) (x : Z) : Option A := by
  classical
  exact if hx : x ∈ endingRegion M then
    if hg : x ∈ M.goal then none else some (Classical.choose (rank_action M hx hg))
  else none

theorem endingAction_spec [Fintype Z] (M : Model Z A) {x : Z}
    (hx : x ∈ endingRegion M) (hg : x ∉ M.goal) :
    ∃ a, endingAction M x = some a ∧ a ∈ M.finish x ∧
      ∀ y ∈ M.post x a, y ∈ endingRegion M ∧ endRank M y < endRank M x := by
  classical
  refine ⟨Classical.choose (rank_action M hx hg), ?_, ?_⟩
  · simp only [endingAction, dite_eq_left hx, dite_eq_right hg]
  · exact Classical.choose_spec (rank_action M hx hg)

/-- Running removes states that cannot keep every successor in the current region. -/
def runStep (M : Model Z A) (U : Finset Z) : Finset Z := by
  classical
  exact U.filter (fun x => ∃ a ∈ M.run x, M.post x a ⊆ U)

theorem mem_runStep (M : Model Z A) (U : Finset Z) (x : Z) :
    x ∈ runStep M U ↔ x ∈ U ∧ ∃ a ∈ M.run x, M.post x a ⊆ U := by
  classical
  simp only [runStep, Finset.mem_filter]

theorem runStep_decreasing (M : Model Z A) (U : Finset Z) : runStep M U ⊆ U :=
  fun x hx => ((mem_runStep M U x).mp hx).1

def runStage [Fintype Z] (M : Model Z A) : ℕ → Finset Z :=
  sequence (runStep M) (endingRegion M)

@[simp] theorem runStage_zero [Fintype Z] (M : Model Z A) : runStage M 0 = endingRegion M := rfl
@[simp] theorem runStage_succ [Fintype Z] (M : Model Z A) (n : ℕ) :
    runStage M (n + 1) = runStep M (runStage M n) := rfl

theorem running_stabilizes [Fintype Z] (M : Model Z A) :
    ∃ n ≤ (endingRegion M).card, runStep M (runStage M n) = runStage M n :=
  decreasing_stabilization (runStep M) (endingRegion M) (runStep_decreasing M)

def runIndex [Fintype Z] (M : Model Z A) : ℕ := by
  classical
  exact Nat.find (running_stabilizes M)

def runningRegion [Fintype Z] (M : Model Z A) : Finset Z := runStage M (runIndex M)

theorem runIndex_bound [Fintype Z] (M : Model Z A) :
    runIndex M ≤ (endingRegion M).card := by
  classical
  exact (Nat.find_spec (running_stabilizes M)).1

theorem runningRegion_fixed [Fintype Z] (M : Model Z A) :
    runStep M (runningRegion M) = runningRegion M := by
  classical
  exact (Nat.find_spec (running_stabilizes M)).2

theorem runStage_subset_ending [Fintype Z] (M : Model Z A) (n : ℕ) :
    runStage M n ⊆ endingRegion M := by
  induction n with
  | zero => exact Finset.Subset.refl _
  | succ n ih => exact Finset.Subset.trans (runStep_decreasing M _) ih

theorem runningRegion_subset_ending [Fintype Z] (M : Model Z A) :
    runningRegion M ⊆ endingRegion M := runStage_subset_ending M _

theorem runningRegion_safe [Fintype Z] (M : Model Z A) :
    runningRegion M ⊆ M.safe := Finset.Subset.trans (runningRegion_subset_ending M) (endingRegion_safe M)

theorem running_action [Fintype Z] (M : Model Z A) {x : Z} (hx : x ∈ runningRegion M) :
    ∃ a ∈ M.run x, M.post x a ⊆ runningRegion M := by
  have hh : x ∈ runStep M (runningRegion M) := by rwa [runningRegion_fixed]
  exact ((mem_runStep M _ x).mp hh).2

def runningAction [Fintype Z] (M : Model Z A) (x : Z) : Option A := by
  classical
  exact if hx : x ∈ runningRegion M then some (Classical.choose (running_action M hx)) else none

theorem runningAction_spec [Fintype Z] (M : Model Z A) {x : Z} (hx : x ∈ runningRegion M) :
    ∃ a, runningAction M x = some a ∧ a ∈ M.run x ∧ M.post x a ⊆ runningRegion M := by
  classical
  refine ⟨Classical.choose (running_action M hx), ?_, ?_⟩
  · simp only [runningAction, dite_eq_left hx]
  · exact Classical.choose_spec (running_action M hx)

/-- Any set of histories whose current states stay in the ending region and
admit safe continuation is contained in the computed running region. -/
theorem running_maximal [Fintype Z] (M : Model Z A) (R : Z → Prop)
    (hEnd : ∀ x, R x → x ∈ endingRegion M)
    (hRun : ∀ x, R x → ∃ a ∈ M.run x, ∀ y ∈ M.post x a, R y) :
    ∀ x, R x → x ∈ runningRegion M := by
  have hstage : ∀ n x, R x → x ∈ runStage M n := by
    intro n
    induction n with
    | zero => exact hEnd
    | succ n ih =>
      intro x hx
      apply (mem_runStep M _ x).mpr
      obtain ⟨a, ha, hp⟩ := hRun x hx
      exact ⟨ih x hx, a, ha, fun y hy => ih y (hp y hy)⟩
  exact hstage (runIndex M)


/-- The ending update is monotone in the target set. -/
theorem endStep_mono (M : Model Z A) {U V : Finset Z} (h : U ⊆ V) :
    endStep M U ⊆ endStep M V := by
  intro x hx
  rcases (mem_endStep M U x).mp hx with old | new
  · exact (mem_endStep M V x).mpr (Or.inl (h old))
  · obtain ⟨hs, a, ha, hp⟩ := new
    exact (mem_endStep M V x).mpr (Or.inr ⟨hs, a, ha, Finset.Subset.trans hp h⟩)

theorem goal_subset_stage (M : Model Z A) (n : ℕ) : M.goal ⊆ endStage M n := by
  induction n with
  | zero => exact Finset.Subset.refl _
  | succ n ih => exact Finset.Subset.trans ih (endStep_increasing M _)

/-- An explicit finite fixed-point certificate identifies the actual attractor. -/
theorem endingRegion_eq_of_stage_fixed [Fintype Z] (M : Model Z A) (n : ℕ)
    (hn : endStep M (endStage M n) = endStage M n) : endingRegion M = endStage M n := by
  apply Finset.Subset.antisymm
  · have inv : ∀ k, endStage M k ⊆ endStage M n := by
      intro k
      induction k with
      | zero => exact goal_subset_stage M n
      | succ k ih =>
        have hs := endStep_mono M ih
        rwa [hn] at hs
    exact inv (endIndex M)
  · exact endStage_subset_region M n

theorem runStep_mono (M : Model Z A) {U V : Finset Z} (h : U ⊆ V) :
    runStep M U ⊆ runStep M V := by
  intro x hx
  obtain ⟨hx, a, ha, hp⟩ := (mem_runStep M U x).mp hx
  exact (mem_runStep M V x).mpr ⟨h hx, a, ha, Finset.Subset.trans hp h⟩

theorem runningRegion_subset_stage [Fintype Z] (M : Model Z A) (n : ℕ) :
    runningRegion M ⊆ runStage M n := by
  induction n with
  | zero => exact runningRegion_subset_ending M
  | succ n ih =>
    have hs := runStep_mono M ih
    rwa [runningRegion_fixed] at hs

/-- An explicit finite viability fixed point identifies the actual running region. -/
theorem runningRegion_eq_of_stage_fixed [Fintype Z] (M : Model Z A) (n : ℕ)
    (hn : runStep M (runStage M n) = runStage M n) : runningRegion M = runStage M n := by
  apply Finset.Subset.antisymm (runningRegion_subset_stage M n)
  apply running_maximal M (fun x => x ∈ runStage M n)
  · intro x hx
    exact runStage_subset_ending M n hx
  · intro x hx
    have h : x ∈ runStep M (runStage M n) := by rwa [hn]
    exact ((mem_runStep M _ x).mp h).2

end
end Komorebi.MachineTheory.SafeEnding
