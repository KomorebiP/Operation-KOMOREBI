import KomorebiSpace.SplitDefectCharts
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

set_option autoImplicit false

/-!
# Finite, lossless hierarchies of split coarsenings

Every discarded layer is retained in the kernel of its own coarsening map.
The reconstruction is finite and exact. No infinite-series convergence,
uniform multiscale bound, or computational compression is asserted.
-/
universe u v
noncomputable section
namespace KomorebiSpace

structure CoarseningCascade (𝕜 : Type u) [NontriviallyNormedField 𝕜] where
  Obj : ℕ → Type v
  [normed : ∀ n, NormedAddCommGroup (Obj n)]
  [space : ∀ n, NormedSpace 𝕜 (Obj n)]
  down : ∀ n, Obj n →L[𝕜] Obj (n+1)
  splitting : ∀ n, SplitDefect.Section (down n)

attribute [instance] CoarseningCascade.normed CoarseningCascade.space

namespace CoarseningCascade
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (T : CoarseningCascade.{u,v} 𝕜)

/-- Repeated coarse observation, with the original datum at level zero. -/
def level (x : T.Obj 0) : ∀ n, T.Obj n
  | 0 => x
  | n+1 => T.down n (level x n)

/-- Lift a coarse datum back to the original space using the selected sections. -/
def restore : ∀ n, T.Obj n →L[𝕜] T.Obj 0
  | 0 => ContinuousLinearMap.id 𝕜 (T.Obj 0)
  | n+1 => (restore n).comp (T.splitting n).lift

@[simp] theorem level_zero (x : T.Obj 0) : T.level x 0 = x := rfl
@[simp] theorem level_succ (x : T.Obj 0) (n : ℕ) :
    T.level x (n+1) = T.down n (T.level x n) := rfl
@[simp] theorem restore_zero (x : T.Obj 0) : T.restore 0 x = x := rfl
@[simp] theorem restore_succ (n : ℕ) (y : T.Obj (n+1)) :
    T.restore (n+1) y = T.restore n ((T.splitting n).lift y) := rfl

@[simp] theorem level_of_zero (n : ℕ) : T.level 0 n = 0 := by
  induction n with
  | zero => rfl
  | succ n ih => rw [level_succ, ih, map_zero]

/-- The hidden residual at its own scale. -/
def detail (x : T.Obj 0) (n : ℕ) : T.Obj n :=
  (T.splitting n).project (T.level x n)

@[simp] theorem detail_hidden (x : T.Obj 0) (n : ℕ) : T.down n (T.detail x n) = 0 :=
  (T.splitting n).project_exact _

@[simp] theorem detail_zero (n : ℕ) : T.detail 0 n = 0 := by
  unfold detail
  rw [level_of_zero, map_zero]

/-- The same detail transported into the original space. -/
def detailTerm (x : T.Obj 0) (n : ℕ) : T.Obj 0 := T.restore n (T.detail x n)

theorem one_layer (x : T.Obj 0) (n : ℕ) :
    T.restore n (T.level x n) = T.detailTerm x n + T.restore (n+1) (T.level x (n+1)) := by
  unfold detailTerm detail
  rw [SplitDefect.Section.project_apply, map_sub, restore_succ, level_succ]
  abel

/-- Exact finite multiscale reconstruction, for every depth N. -/
theorem reconstruction (x : T.Obj 0) (N : ℕ) :
    x = (∑ n ∈ Finset.range N, T.detailTerm x n) + T.restore N (T.level x N) := by
  induction N with
  | zero => simp
  | succ N ih =>
    calc
      x = (∑ n ∈ Finset.range N, T.detailTerm x n) + T.restore N (T.level x N) := ih
      _ = (∑ n ∈ Finset.range N, T.detailTerm x n) +
          (T.detailTerm x N + T.restore (N+1) (T.level x (N+1))) := by rw [one_layer]
      _ = _ := by rw [Finset.sum_range_succ]; abel

/-- The entire retained hierarchy detects equality, including the depth-zero case. -/
theorem equal_iff (x y : T.Obj 0) (N : ℕ) : x = y ↔
    (∀ n < N, T.detail x n = T.detail y n) ∧ T.level x N = T.level y N := by
  constructor
  · rintro rfl; exact ⟨fun _ _ => rfl, rfl⟩
  · rintro ⟨hd, hc⟩
    have hs : (∑ n ∈ Finset.range N, T.detailTerm x n) =
        ∑ n ∈ Finset.range N, T.detailTerm y n := by
      apply Finset.sum_congr rfl
      intro n hn
      unfold detailTerm
      rw [hd n (Finset.mem_range.mp hn)]
    calc
      x = (∑ n ∈ Finset.range N, T.detailTerm x n) + T.restore N (T.level x N) := T.reconstruction x N
      _ = (∑ n ∈ Finset.range N, T.detailTerm y n) + T.restore N (T.level y N) := by rw [hs, hc]
      _ = y := (T.reconstruction y N).symm

theorem zero_iff (x : T.Obj 0) (N : ℕ) : x = 0 ↔
    (∀ n < N, T.detail x n = 0) ∧ T.level x N = 0 := by
  simpa only [detail_zero, level_of_zero] using T.equal_iff x 0 N

end CoarseningCascade
end KomorebiSpace
end
