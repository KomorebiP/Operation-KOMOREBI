import KomorebiSpace.BanachTowers
import KomorebiSpace.AdjacentResolution
import Mathlib.Algebra.BigOperators.Intervals
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Ring

set_option autoImplicit false

/-!
# Actual block restrictions and accumulated tower residuals

All maps below use the existing Banach tower bonding maps. A block residual is
not a subsample of adjacent residuals: it is their transported accumulation.
Contractivity is an explicit extra hypothesis for the norm estimates.
-/

universe u v
noncomputable section
namespace KomorebiSpace
namespace BanachTower
open scoped NNReal ENNReal
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X Y : BanachTower.{u,v} 𝕜)

/-- The actual continuous linear restriction between any ordered pair of stages. -/
def restriction {i j : ℕ} (h : i ≤ j) : X.Obj j →L[𝕜] X.Obj i :=
  Nat.leRecOn (C := fun n => X.Obj n →L[𝕜] X.Obj i) h
    (fun {n} a => a.comp (X.down n)) (ContinuousLinearMap.id 𝕜 (X.Obj i))

@[simp] theorem restriction_refl (i : ℕ) :
    restriction X (Nat.le_refl i) = ContinuousLinearMap.id 𝕜 (X.Obj i) := by
  simp [restriction, Nat.leRecOn_self]

theorem restriction_succ {i j : ℕ} (h : i ≤ j) (h' : i ≤ j+1) :
    restriction X h' = (restriction X h).comp (X.down j) := by
  simp only [restriction, Nat.leRecOn_succ h]

@[simp] theorem restriction_adjacent (i : ℕ) :
    restriction X (Nat.le_succ i) = X.down i := by
  rw [restriction_succ X (Nat.le_refl i), restriction_refl]
  ext x
  rfl

theorem restriction_trans {i j k : ℕ} (hij : i ≤ j) (hjk : j ≤ k) :
    (restriction X hij).comp (restriction X hjk) =
      restriction X (hij.trans hjk) := by
  induction k, hjk using Nat.le_induction with
  | base => simp
  | succ k hk ih =>
    rw [restriction_succ X hk, restriction_succ X (hij.trans hk)]
    rw [← ContinuousLinearMap.comp_assoc, ih]

/-- Agreement with the finite-stage functions in the previous eventual category. -/
theorem restriction_underlying {i j : ℕ} (h : i ≤ j) (x : X.Obj j) :
    restriction X h x = (Resolution.Adjacent.resolution X.Obj (fun n => X.down n)).restrict h x := by
  induction j, h using Nat.le_induction with
  | base => simp [Resolution.Adjacent.resolution]
  | succ j hj ih =>
    rw [restriction_succ X hj]
    change restriction X hj (X.down j x) =
      Resolution.Adjacent.restrict X.Obj (fun n => X.down n) _ x
    rw [Resolution.Adjacent.restrict_succ X.Obj (fun n => X.down n) hj]
    exact ih (X.down j x)

/-- All-pairs restrictions are contractive when adjacent bonds are. -/
theorem restriction_contractive (hX : ∀ n, ‖X.down n‖ ≤ 1)
    {i j : ℕ} (h : i ≤ j) : ‖restriction X h‖ ≤ 1 := by
  induction j, h using Nat.le_induction with
  | base => simpa using (ContinuousLinearMap.norm_id_le (𝕜 := 𝕜) (E := X.Obj i))
  | succ j hj ih =>
    rw [restriction_succ X hj]
    exact ((restriction X hj).opNorm_comp_le (X.down j)).trans
      ((mul_le_mul ih (hX j) (norm_nonneg _) (by norm_num)).trans (by norm_num))

/-- Noncommuting comparison for an entire block. -/
def blockDefect (f : Candidates X Y) {i j : ℕ} (h : i ≤ j) :
    X.Obj j →L[𝕜] Y.Obj i :=
  (restriction Y h).comp (f j) - (f i).comp (restriction X h)

@[simp] theorem blockDefect_refl (f : Candidates X Y) (i : ℕ) :
    blockDefect X Y f (Nat.le_refl i) = 0 := by
  ext x
  simp [blockDefect]

@[simp] theorem blockDefect_adjacent (f : Candidates X Y) (i : ℕ) :
    blockDefect X Y f (Nat.le_succ i) = rawDefect X Y f i := by
  simp [blockDefect, rawDefect]

/-- Exact concatenation law, with the two defects in the correct common Hom space. -/
theorem blockDefect_concat (f : Candidates X Y) {i j k : ℕ}
    (hij : i ≤ j) (hjk : j ≤ k) :
    blockDefect X Y f (hij.trans hjk) =
      (restriction Y hij).comp (blockDefect X Y f hjk) +
      (blockDefect X Y f hij).comp (restriction X hjk) := by
  unfold blockDefect
  rw [← restriction_trans X hij hjk, ← restriction_trans Y hij hjk]
  ext x
  simp only [ContinuousLinearMap.comp_apply, sub_apply,
    add_apply, map_sub]
  abel

theorem blockDefect_succ (f : Candidates X Y) {i j : ℕ} (h : i ≤ j) :
    blockDefect X Y f (h.trans (Nat.le_succ j)) =
      (restriction Y h).comp (rawDefect X Y f j) +
      (blockDefect X Y f h).comp (X.down j) := by
  rw [blockDefect_concat X Y f h (Nat.le_succ j)]
  simp

/-- Transported accumulation of any family of adjacent residuals. -/
def blockSum (r : ∀ n, X.Obj (n+1) →L[𝕜] Y.Obj n) {i j : ℕ} (h : i ≤ j) :
    X.Obj j →L[𝕜] Y.Obj i :=
  Nat.leRecOn (C := fun n => X.Obj n →L[𝕜] Y.Obj i) h
    (fun {n} a => if hn : i ≤ n then
      (restriction Y hn).comp (r n) + a.comp (X.down n) else 0) 0

@[simp] theorem blockSum_refl (r : ∀ n, X.Obj (n+1) →L[𝕜] Y.Obj n) (i : ℕ) :
    blockSum X Y r (Nat.le_refl i) = 0 := by
  simp [blockSum, Nat.leRecOn_self]

theorem blockSum_succ (r : ∀ n, X.Obj (n+1) →L[𝕜] Y.Obj n)
    {i j : ℕ} (h : i ≤ j) (h' : i ≤ j+1) :
    blockSum X Y r h' =
      (restriction Y h).comp (r j) + (blockSum X Y r h).comp (X.down j) := by
  simp only [blockSum, Nat.leRecOn_succ h, dite_eq_left h]

@[simp] theorem blockSum_adjacent (r : ∀ n, X.Obj (n+1) →L[𝕜] Y.Obj n) (i : ℕ) :
    blockSum X Y r (Nat.le_succ i) = r i := by
  rw [blockSum_succ X Y r (Nat.le_refl i)]
  simp

/-- Fundamental telescoping identity, on the actual tower differential. -/
theorem blockSum_differential (f : Candidates X Y) {i j : ℕ} (h : i ≤ j) :
    blockSum X Y (differential X Y f) h = blockDefect X Y f h := by
  induction j, h using Nat.le_induction with
  | base => simp
  | succ j hj ih =>
    rw [blockSum_succ X Y _ hj, blockDefect_succ, ih]
    rfl

theorem blockSum_add (r s : ∀ n, X.Obj (n+1) →L[𝕜] Y.Obj n)
    {i j : ℕ} (h : i ≤ j) :
    blockSum X Y (r+s) h = blockSum X Y r h + blockSum X Y s h := by
  induction j, h using Nat.le_induction with
  | base => simp
  | succ j hj ih =>
    rw [blockSum_succ X Y _ hj, blockSum_succ X Y r hj,
      blockSum_succ X Y s hj, ih]
    ext x
    simp only [Pi.add_apply, ContinuousLinearMap.comp_apply,
      add_apply, map_add]
    abel

theorem blockSum_smul (c : 𝕜) (r : ∀ n, X.Obj (n+1) →L[𝕜] Y.Obj n)
    {i j : ℕ} (h : i ≤ j) :
    blockSum X Y (c • r) h = c • blockSum X Y r h := by
  induction j, h using Nat.le_induction with
  | base => simp
  | succ j hj ih =>
    rw [blockSum_succ X Y _ hj, blockSum_succ X Y r hj, ih]
    ext x
    simp [smul_add]

/-- A local sum budget, without cancellation being discarded from the residual itself. -/
theorem blockSum_norm (hX : ∀ n, ‖X.down n‖ ≤ 1) (hY : ∀ n, ‖Y.down n‖ ≤ 1)
    (r : ∀ n, X.Obj (n+1) →L[𝕜] Y.Obj n) {i j : ℕ} (h : i ≤ j) :
    ‖blockSum X Y r h‖ ≤ ∑ k ∈ Finset.Ico i j, ‖r k‖ := by
  induction j, h using Nat.le_induction with
  | base => simp
  | succ j hj ih =>
    rw [blockSum_succ X Y r hj, Finset.sum_Ico_succ_top hj]
    have h1 : ‖(restriction Y hj).comp (r j)‖ ≤ ‖r j‖ :=
      ((restriction Y hj).opNorm_comp_le (r j)).trans
        (by simpa using (mul_le_mul_of_nonneg_right (restriction_contractive Y hY hj)
          (norm_nonneg (r j))))
    have h2 : ‖(blockSum X Y r hj).comp (X.down j)‖ ≤ ‖blockSum X Y r hj‖ :=
      ((blockSum X Y r hj).opNorm_comp_le (X.down j)).trans
        (by simpa using (mul_le_mul_of_nonneg_left (hX j) (norm_nonneg (blockSum X Y r hj))))
    exact (norm_add_le _ _).trans ((add_le_add h1 (h2.trans ih)).trans (by rw [add_comm]))

theorem blockSum_uniform_bound (hX : ∀ n, ‖X.down n‖ ≤ 1)
    (hY : ∀ n, ‖Y.down n‖ ≤ 1) (r : Residuals X Y) {i j : ℕ} (h : i ≤ j) :
    ‖blockSum X Y r h‖ ≤ (j-i : ℕ) * ‖r‖ := by
  apply (blockSum_norm X Y hX hY r h).trans
  calc
    (∑ k ∈ Finset.Ico i j, ‖r k‖) ≤ ∑ _k ∈ Finset.Ico i j, ‖r‖ :=
      Finset.sum_le_sum (fun k _ => lp.norm_apply_le_norm ENNReal.top_ne_zero r k)
    _ = (j-i : ℕ) * ‖r‖ := by simp

theorem blockDefect_uniform_bound (hX : ∀ n, ‖X.down n‖ ≤ 1)
    (hY : ∀ n, ‖Y.down n‖ ≤ 1) (f : Candidates X Y) {i j : ℕ} (h : i ≤ j) :
    ‖blockDefect X Y f h‖ ≤ (j-i : ℕ) * ‖differential X Y f‖ := by
  rw [← blockSum_differential X Y f h]
  exact blockSum_uniform_bound X Y hX hY _ h

end BanachTower
end KomorebiSpace
end
