import KomorebiLSM.MemoryApproximation
import KomorebiLSM.StrongRefinement
import Mathlib.Tactic.NormNum

/-! Exact examples for the distinction between local residuals, propagated
error, finite memory and switching. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM.Block8Examples
open Komorebi.LSM.Stability

noncomputable def scale (r : ℝ) : ℝ →L[ℝ] ℝ := r • ContinuousLinearMap.id ℝ ℝ

@[simp] theorem scale_apply (r x : ℝ) : scale r x = r*x := rfl

theorem scale_norm (r : ℝ) : ‖scale r‖=|r| := by simp only [scale,norm_smul,ContinuousLinearMap.norm_id,Real.norm_eq_abs,mul_one]

/-- An actual predicted trajectory with local error one and gain two. -/
def expandingPrediction (t : ℕ) : ℝ := 2^t-1

theorem expandingPrediction_step (t : ℕ) :
    expandingPrediction (t+1)=2*expandingPrediction t+1 := by
  simp only [expandingPrediction,pow_succ]
  ring

theorem expanding_lipschitz : LipschitzWith (2 : NNReal) (fun x : ℝ => 2*x+1) := by
  apply LipschitzWith.of_dist_le_mul
  intro x y
  simp only [dist_eq_norm,Real.norm_eq_abs,NNReal.coe_ofNat]
  rw [show (2*x+1)-(2*y+1)=2*(x-y) by ring,abs_mul]
  norm_num

theorem expanding_prediction_general_bound (T : ℕ) :
    ‖(0 : ℝ)-expandingPrediction T‖ ≤ errorEnvelope (fun _ => 2) (fun _ => 1) 0 T := by
  have h := compositional_defect_propagation
    (X:=ℝ) (Z:=fun _ => ℝ) (fun _ x => x) (fun _ _ => 0)
    (fun _ x => 2*x+1) (fun _ => 0) expandingPrediction
    (fun _ => Set.univ) (fun _ => (2 : NNReal)) (fun _ => 1)
    (fun _ => rfl) expandingPrediction_step
    (fun _ => Set.mem_univ _) (fun _ => Set.mem_univ _)
    (fun _ => expanding_lipschitz.lipschitzOnWith) (fun _ => by norm_num) T
  simpa only [expandingPrediction,Nat.cast_zero,pow_zero,sub_self,norm_zero,NNReal.coe_ofNat] using h

theorem expanding_envelope_exact (T : ℕ) :
    errorEnvelope (fun _ => 2) (fun _ => 1) 0 T=2^T-1 := by
  induction T with
  | zero => simp
  | succ T ih => rw [errorEnvelope_succ,ih,pow_succ]; ring

theorem local_error_not_whole_trajectory_error :
    ‖(0 : ℝ)-expandingPrediction 3‖=7 := by norm_num [expandingPrediction]

/-- A stable length-one memory prediction, stored as current/previous values. -/
noncomputable def memoryPair : ℕ → ℝ×ℝ
  | 0 => (0,0)
  | t+1 => ((memoryPair t).1/2+(memoryPair t).2/4+1/8,(memoryPair t).1)

noncomputable def memoryPrediction (s : ℤ) : ℝ :=
  if 0 ≤ s then (memoryPair s.toNat).1 else 0

@[simp] theorem memoryPrediction_nat (t : ℕ) : memoryPrediction (t:ℤ)=(memoryPair t).1 := by
  simp [memoryPrediction]

theorem memoryPrediction_previous (t : ℕ) :
    memoryPrediction ((t:ℤ)-1)=(memoryPair t).2 := by
  cases t with
  | zero => norm_num [memoryPrediction,memoryPair]
  | succ t =>
    have h : ((t+1:ℕ):ℤ)-1=(t:ℤ) := by omega
    rw [h,memoryPrediction_nat]
    rfl

theorem memoryPrediction_initial (s : ℤ) (hs : s ≤ 0) : memoryPrediction s=0 := by
  rcases eq_or_lt_of_le hs with h|h
  · subst s; norm_num [memoryPrediction,memoryPair]
  · simp [memoryPrediction,not_le.mpr h]

theorem memoryPrediction_step (t : ℕ) :
    memoryPrediction ((t:ℤ)+1)=
      finiteMemory (scale (1/2)) (fun _ => scale (1/4)) 1 memoryPrediction t+1/8 := by
  rw [show (t:ℤ)+1=((t+1:ℕ):ℤ) by omega,memoryPrediction_nat]
  rw [finiteMemory,Finset.sum_range_one]
  simp only [Nat.cast_zero,sub_zero]
  change (memoryPair (t+1)).1 =
    (1/2)*memoryPrediction (t:ℤ)+(1/4)*memoryPrediction ((t:ℤ)-1)+1/8
  rw [memoryPrediction_nat,memoryPrediction_previous]
  simp only [memoryPair]
  ring

theorem stable_memory_gain : memoryGain (scale (1/2)) (fun _ => scale (1/4)) 1=3/4 := by
  norm_num [memoryGain,scale_norm]

/-- This invokes the general theorem on a predicted trajectory's own history. -/
theorem recursive_memory_uniform_bound :
    sSup (Set.range (fun t : ℕ => ‖(0 : ℝ)-memoryPrediction t‖)) ≤ 1/2 := by
  have h := finite_memory_uniform_prediction_bound
    (scale (1/2)) (fun _ => scale (1/4)) 1 (fun _ => (0:ℝ)) memoryPrediction (fun _ => 1/8)
    (D:=1/8) (E0:=0) (by rw [stable_memory_gain]; norm_num) (by norm_num)
    (fun s _ hs => by rw [memoryPrediction_initial s hs]; norm_num)
    memoryPrediction_step (fun _ => by norm_num [finiteMemory])
  rw [stable_memory_gain] at h
  norm_num at h ⊢
  exact h

theorem memoryPrediction_first_three :
    memoryPrediction 1=1/8 ∧ memoryPrediction 2=3/16 ∧ memoryPrediction 3=1/4 := by
  have h1 := memoryPrediction_nat 1
  have h2 := memoryPrediction_nat 2
  have h3 := memoryPrediction_nat 3
  norm_num [memoryPair] at h1 h2 h3
  exact ⟨h1,h2,h3⟩

/-- The zero-memory-length case still has a well-defined transition. -/
theorem zero_memory_length (A : ℝ →L[ℝ] ℝ) (K : ℕ → ℝ →L[ℝ] ℝ) (z : ℤ → ℝ) (t : ℤ) :
    finiteMemory A K 0 z t=A (z t) := by simp [finiteMemory]

/-- Gain one and a persistent local residual can have arbitrarily large error. -/
theorem gain_one_drift (t : ℕ) :
    ((t+1:ℕ):ℝ)=finiteMemory (scale 1) (fun _ => scale 0) 0 (fun s : ℤ => (s:ℝ)) t+1 := by
  simp [finiteMemory]

theorem gain_one_unbounded : ∀ E : ℝ, ∃ t : ℕ, E < ‖(0 : ℝ)-(t:ℝ)‖ := by
  intro E
  obtain ⟨t, ht⟩ := exists_nat_gt E
  exact ⟨t,by simpa using ht⟩

/-- Each map squares to zero; their alternating product amplifies a state. -/
def switchA : (ℝ×ℝ) →ₗ[ℝ] (ℝ×ℝ) where
  toFun x := (2*x.2,0)
  map_add' := by intro x y; ext <;> simp [mul_add]
  map_smul' := by intro r x; ext <;> simp [mul_left_comm]

def switchB : (ℝ×ℝ) →ₗ[ℝ] (ℝ×ℝ) where
  toFun x := (0,2*x.1)
  map_add' := by intro x y; ext <;> simp [mul_add]
  map_smul' := by intro r x; ext <;> simp [mul_left_comm]

theorem individually_nilpotent : switchA.comp switchA=0 ∧ switchB.comp switchB=0 := by
  constructor
  · apply LinearMap.ext
    intro x
    simp [switchA]
  · apply LinearMap.ext
    intro x
    simp [switchB]

theorem alternating_amplification (n : ℕ) :
    ((switchB.comp switchA)^n) (0,1)=(0,4^n) := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ',Module.End.mul_apply,ih]
    simp [switchA,switchB,pow_succ']
    ring

theorem alternating_three_pairs : ‖((switchB.comp switchA)^3) (0,1)‖=64 := by
  rw [alternating_amplification]
  norm_num

end Komorebi.LSM.Block8Examples
