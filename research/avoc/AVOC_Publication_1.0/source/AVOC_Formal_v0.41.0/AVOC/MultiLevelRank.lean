import AVOC.MultiLevelInformation
import AVOC.AffineRankProbe

namespace Komorebi.AVOC.Affine.MultiLevelRank

set_option linter.unusedSectionVars false

open Factorization RankProbe

variable {R : Type} [Field R] [DecidableEq R] {n m : Nat}

/-- Exact algebraic tests with different certificate strengths. -/
inductive Probe (m n : Nat) where
  | entry (row : Fin m) (col : Fin n)
  | minor2 (p : MinorTwo m n)
  deriving Repr, DecidableEq


def level : Probe m n → Nat
  | .entry _ _ => 1
  | .minor2 _ => 2


def detects (A : Matrix (Fin m) (Fin n) R) : Probe m n → Bool
  | .entry i j => decide (A i j ≠ 0)
  | .minor2 p => check2 A p

@[simp] theorem detects_entry_iff (A : Matrix (Fin m) (Fin n) R) (i : Fin m) (j : Fin n) :
    detects A (.entry i j) = true ↔ A i j ≠ 0 := by simp [detects]

@[simp] theorem detects_minor2 (A : Matrix (Fin m) (Fin n) R) (p : MinorTwo m n) :
    detects A (.minor2 p) = check2 A p := rfl

/-- Every positive report has the rank-lower-bound meaning encoded by `level`. -/
theorem detects_rank_lower (A : Matrix (Fin m) (Fin n) R) (p : Probe m n)
    (h : detects A p = true) : level p ≤ A.rank := by
  cases p with
  | entry i j =>
      apply nonzero_minor_rank_lower A 1 (fun _ => i) (fun _ => j)
      simpa [detects, Matrix.det_fin_one, Matrix.submatrix] using h
  | minor2 q =>
      exact check2_rank_lower A q h

variable {Ω P : Type*} [Fintype Ω] [DecidableEq Ω] [Fintype P] [DecidableEq P]

/-- Concrete affine specialization. Terminal payoffs are declared net values in
one common rational objective. The checker proves probe meaning, not payoff calibration. -/
structure Catalogue (R : Type) [Field R] (Ω P : Type*) (n m : Nat) where
  matrix : Ω → Matrix (Fin m) (Fin n) R
  probe : P → Probe m n
  fee : P → ℚ
  fee_nonneg : ∀ p, 0 ≤ fee p
  reuseAvailable : Bool
  reusePayoff : Ω → ℚ
  coldPayoff : Ω → ℚ


def model (c : Catalogue R Ω P n m) : MultiLevel.Model Ω P where
  detects p w := detects (c.matrix w) (c.probe p)
  level p := level (c.probe p)
  fee := c.fee
  fee_nonneg := c.fee_nonneg
  reuseAvailable := c.reuseAvailable
  reusePayoff := c.reusePayoff
  coldPayoff := c.coldPayoff

@[simp] theorem model_detects (c : Catalogue R Ω P n m) (p : P) (w : Ω) :
    (model c).detects p w = detects (c.matrix w) (c.probe p) := rfl

@[simp] theorem model_level (c : Catalogue R Ω P n m) (p : P) :
    (model c).level p = level (c.probe p) := rfl


/-- The algebraic invariant attached to a computational controller state. -/
def RankSound (c : Catalogue R Ω P n m) (s : MultiLevel.State (model c)) : Prop :=
  ∀ w ∈ s.worlds, s.lower ≤ (c.matrix w).rank


theorem rankSound_zero (c : Catalogue R Ω P n m) (s : MultiLevel.State (model c))
    (hzero : s.lower = 0) : RankSound c s := by
  intro w hw
  rw [hzero]
  exact Nat.zero_le _


theorem rankSound_afterSuccess (c : Catalogue R Ω P n m)
    (s : MultiLevel.State (model c)) (p : P) (hs : RankSound c s) :
    RankSound c (MultiLevel.afterSuccess (model c) s p) := by
  intro w hw
  by_cases hnonempty : (MultiLevel.successWorlds (model c) s p).Nonempty
  · have hm : w ∈ MultiLevel.successWorlds (model c) s p := by
      simpa [MultiLevel.afterSuccess, hnonempty] using hw
    have hparent : w ∈ s.worlds := MultiLevel.successWorlds_subset (model c) s p hm
    have hdet : detects (c.matrix w) (c.probe p) = true :=
      (Finset.mem_filter.mp hm).2
    have hb := max_le (hs w hparent) (detects_rank_lower (c.matrix w) (c.probe p) hdet)
    simpa [MultiLevel.afterSuccess, hnonempty] using hb
  · have hm : w ∈ s.worlds := by
      simpa [MultiLevel.afterSuccess, hnonempty] using hw
    simpa [MultiLevel.afterSuccess, hnonempty] using hs w hm


theorem rankSound_afterFailure (c : Catalogue R Ω P n m)
    (s : MultiLevel.State (model c)) (p : P) (hs : RankSound c s) :
    RankSound c (MultiLevel.afterFailure (model c) s p) := by
  intro w hw
  by_cases hnonempty : (MultiLevel.failureWorlds (model c) s p).Nonempty
  · have hm : w ∈ MultiLevel.failureWorlds (model c) s p := by
      simpa [MultiLevel.afterFailure, hnonempty] using hw
    have hp : w ∈ s.worlds := MultiLevel.failureWorlds_subset (model c) s p hm
    simpa [MultiLevel.afterFailure, hnonempty] using hs w hp
  · have hm : w ∈ s.worlds := by
      simpa [MultiLevel.afterFailure, hnonempty] using hw
    simpa [MultiLevel.afterFailure, hnonempty] using hs w hm


theorem rankSound_terminal (c : Catalogue R Ω P n m)
    (s : MultiLevel.State (model c)) (hs : RankSound c s) :
    RankSound c (MultiLevel.terminal s) := hs


theorem rankSound_step (c : Catalogue R Ω P n m)
    (s : MultiLevel.State (model c)) (a : MultiLevel.Action P) (o : Bool)
    (hs : RankSound c s) : RankSound c (MultiLevel.step (model c) s a o) := by
  cases a with
  | stop => exact rankSound_terminal c s hs
  | reuse => exact rankSound_terminal c s hs
  | cold => exact rankSound_terminal c s hs
  | probe p => cases o <;> simp only [MultiLevel.step] <;>
      first | exact rankSound_afterFailure c s p hs | exact rankSound_afterSuccess c s p hs

theorem rankSound_preserves (c : Catalogue R Ω P n m) :
    Guarded.Preserves (MultiLevel.system (model c)) (RankSound c) := by
  intro s hs a ha o
  exact rankSound_step c s a o hs


theorem selectedPlan_rankSound (c : Catalogue R Ω P n m)
    (steps : Nat) (s : MultiLevel.State (model c)) (hs : RankSound c s) :
    Guarded.TreeSafe (MultiLevel.system (model c)) (RankSound c) s
      (MultiLevel.selectedPlan (model c) steps s) :=
  Guarded.legal_plan_safe (MultiLevel.system (model c)) (RankSound c)
    (rankSound_preserves c) s _ hs (MultiLevel.selectedPlan_legal (model c) steps s)

/-- There exists an optimal finite-horizon adaptive plan whose every branch
retains a sound rank floor. -/
theorem rankSound_optimal_plan_exists (c : Catalogue R Ω P n m)
    (steps : Nat) (s : MultiLevel.State (model c)) (hs : RankSound c s) :
    ∃ p : Guarded.Plan (MultiLevel.Action P) Bool steps,
      Guarded.Legal (MultiLevel.system (model c)) s p ∧
      Guarded.TreeSafe (MultiLevel.system (model c)) (RankSound c) s p ∧
      Guarded.planValue (MultiLevel.system (model c)) s p =
        Guarded.value (MultiLevel.system (model c)) steps s ∧
      ∀ q : Guarded.Plan (MultiLevel.Action P) Bool steps,
        Guarded.Legal (MultiLevel.system (model c)) s q →
        Guarded.planValue (MultiLevel.system (model c)) s q ≤
          Guarded.planValue (MultiLevel.system (model c)) s p :=
  Guarded.safe_optimal_plan_exists (MultiLevel.system (model c)) (RankSound c)
    (rankSound_preserves c) steps s hs

/-- The state's retained floor is a genuine rank lower bound for every retained
catalogue matrix, independent of catalogue probabilities. -/
theorem state_lower_rank (c : Catalogue R Ω P n m) (s : MultiLevel.State (model c))
    (hs : RankSound c s) (w : Ω) (hw : w ∈ s.worlds) :
    s.lower ≤ (c.matrix w).rank := hs w hw

/-- The same state floor bounds every exact two-stage factorization of every
retained world. -/
theorem state_lower_bounds_every_factor
    (c : Catalogue R Ω P n m) (s : MultiLevel.State (model c)) (hs : RankSound c s)
    (w : Ω) (hw : w ∈ s.worlds) (f : Signature R n m)
    (hm : f.linear = c.matrix w) {k : Nat}
    (a : Signature R n k) (b : Signature R k m)
    (he : compose b a = f) : s.lower ≤ k := by
  have hl : s.lower ≤ f.linear.rank := by simpa [hm] using state_lower_rank c s hs w hw
  have hu := any_factor_rank_upper a b
  rw [he] at hu
  exact hl.trans hu

/-- A positive report at a possible branch upgrades the explicit floor to at
least the probe's certified level. -/
theorem positive_branch_certifies_level
    (c : Catalogue R Ω P n m) (s : MultiLevel.State (model c)) (p : P)
    (h : (MultiLevel.successWorlds (model c) s p).Nonempty) :
    level (c.probe p) ≤ (MultiLevel.afterSuccess (model c) s p).lower :=
  MultiLevel.positive_report_level_le (model c) s p h

/-- Only the linear component is tested; changed affine offsets preserve every
entry/minor report. -/
theorem probe_offset_invariant (f g : Signature R n m) (p : Probe m n)
    (h : f.linear = g.linear) : detects f.linear p = detects g.linear p := by rw [h]

/-- A positive report directly bounds any exact factorization of the observed
map, without using catalogue frequencies. -/
theorem positive_report_bounds_factor (A : Matrix (Fin m) (Fin n) R)
    (p : Probe m n) (h : detects A p = true) (f : Signature R n m)
    (hm : f.linear = A) {k : Nat} (a : Signature R n k) (b : Signature R k m)
    (he : compose b a = f) : level p ≤ k := by
  have hl : level p ≤ f.linear.rank := by simpa [hm] using detects_rank_lower A p h
  have hu := any_factor_rank_upper a b
  rw [he] at hu
  exact hl.trans hu

end Komorebi.AVOC.Affine.MultiLevelRank
