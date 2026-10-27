module
public import KomorebiPhysics.InfiniteCellCurrents
public import KomorebiPhysics.CycleGauge

/-! Countably many disjoint finite cycles. Every row is absolutely summable;
both iterated sums exist and vanish, but the joint double array is not summable.
This is an abstract array counterexample, not a claimed Hamiltonian realization. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace CurrentSummationExamples
open Classical
open scoped BigOperators

abbrev Label := ℕ × Fin 3

def cycles (i j : Label) : ℝ :=
  if j.1 = i.1 then CycleGauge.triangle i.2 j.2 else 0

theorem cycles_antisymm (i j : Label) : cycles i j = -cycles j i := by
  by_cases h : j.1 = i.1
  · simp only [cycles, h, ite_true]
    rw [CycleGauge.triangle_isCycle.1]
  · simp [cycles, h, Ne.symm h]

theorem row_summable (i : Label) : Summable (cycles i) := by
  apply summable_of_ne_finset_zero (s := Finset.univ.image (fun a : Fin 3 => (i.1, a)))
  intro j hj
  have hn : j.1 ≠ i.1 := by
    intro h
    apply hj
    apply Finset.mem_image.mpr
    exact ⟨j.2, Finset.mem_univ _, Prod.ext h.symm rfl⟩
  exact ite_eq_right hn

theorem row_abs_summable (i : Label) : Summable (fun j => |cycles i j|) :=
  (row_summable i).abs

theorem row_sum_zero (i : Label) : (∑' j, cycles i j) = 0 := by
  rw [(row_summable i).tsum_prod]
  have he : ∀ n : ℕ, (∑' a : Fin 3, cycles i (n,a)) =
      if n = i.1 then (∑ a, CycleGauge.triangle i.2 a) else 0 := by
    intro n
    by_cases h : n = i.1 <;> simp [cycles, h, tsum_fintype]
  simp only [he, CycleGauge.triangle_isCycle.2, ite_self, tsum_zero]

theorem column_summable (j : Label) : Summable (fun i => cycles i j) := by
  have h := (row_summable j).neg
  exact h.congr (fun i => (cycles_antisymm i j).symm)

theorem column_sum_zero (j : Label) : (∑' i, cycles i j) = 0 := by
  calc
    _ = ∑' i, -cycles j i := tsum_congr (fun i => cycles_antisymm i j)
    _ = 0 := by rw [tsum_neg, row_sum_zero, neg_zero]

theorem row_hasSum_zero (i : Label) : HasSum (cycles i) 0 := by
  simpa only [row_sum_zero] using (row_summable i).hasSum

theorem both_iterated_hasSum :
    HasSum (fun i => ∑' j, cycles i j) 0 ∧
    HasSum (fun j => ∑' i, cycles i j) 0 := by
  simp only [row_sum_zero, column_sum_zero]
  exact ⟨hasSum_zero, hasSum_zero⟩

theorem unit_edges (n : ℕ) : cycles (n,0) (n,1) = 1 := by
  norm_num [cycles, CycleGauge.triangle]

theorem not_joint_summable : ¬ Summable (fun ij : Label × Label => cycles ij.1 ij.2) := by
  intro h
  have hi : Function.Injective (fun n : ℕ => ((n, (0 : Fin 3)), (n, (1 : Fin 3)))) := by
    intro m n hmn
    exact congrArg (fun ij : Label × Label => ij.1.1) hmn
  have hs := h.comp_injective hi
  change Summable (fun n : ℕ => cycles (n,0) (n,1)) at hs
  have hc : Summable (fun _ : ℕ => (1 : ℝ)) := by
    simpa only [unit_edges] using hs
  exact one_ne_zero ((summable_const_iff (1 : ℝ)).mp hc)

theorem not_joint_absolute : ¬ Summable (fun ij : Label × Label => |cycles ij.1 ij.2|) := by
  intro h
  apply not_joint_summable
  exact (summable_norm_iff).mp h

end CurrentSummationExamples
end KomorebiPhysics
