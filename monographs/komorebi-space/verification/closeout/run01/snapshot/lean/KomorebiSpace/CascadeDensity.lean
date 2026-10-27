import KomorebiSpace.CascadeLimits

set_option autoImplicit false

/-!
# A checkable density criterion for infinite reconstruction

Under a uniform remainder bound, recoverable data are exactly the norm closure
of data killed at some finite coarse level. This is a criterion, not a blanket
density assertion. Uniform boundedness is not inferred from split surjectivity.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace CoarseningCascade
open Filter Set
open scoped Topology
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (T : CoarseningCascade.{u,v} 𝕜)

/-- Data whose retained hierarchy terminates at a finite level. -/
def finiteCore : Set (T.Obj 0) := {x | ∃ N, T.remainder N x = 0}

@[simp] theorem mem_finiteCore (x : T.Obj 0) :
    x ∈ T.finiteCore ↔ ∃ N, T.remainder N x = 0 := Iff.rfl

/-- A remainder that is zero stays zero under further coarsening. -/
theorem remainder_zero_after (x : T.Obj 0) (N : ℕ) (hN : T.remainder N x = 0)
    (n : ℕ) (hn : N ≤ n) : T.remainder n x = 0 := by
  rw [← T.remainder_nested_right N n hn x, hN, map_zero]

theorem finiteCore_recoverable (x : T.Obj 0) (hx : x ∈ T.finiteCore) :
    x ∈ T.recoverable := by
  obtain ⟨N, hN⟩ := hx
  apply tendsto_const_nhds.congr'
  filter_upwards [eventually_ge_atTop N] with n hn
  exact (T.remainder_zero_after x N hN n hn).symm

/-- The finite reconstructed approximants always lie in the finite core. -/
theorem partial_mem_finiteCore (x : T.Obj 0) (N : ℕ) :
    T.reconstructed N x ∈ T.finiteCore := ⟨N, T.remainder_partial x N⟩

/-- Recovery forces approximation by data killed at a finite level. -/
theorem recoverable_mem_closure_finiteCore (x : T.Obj 0) (hx : x ∈ T.recoverable) :
    x ∈ closure T.finiteCore := by
  have ht := (T.partial_tendsto_iff x).2 hx
  exact isClosed_closure.mem_of_tendsto ht
    (Filter.Eventually.of_forall (fun N => subset_closure (T.partial_mem_finiteCore x N)))

/-- A uniform operator bound promotes finite-core approximation to recovery. -/
theorem recoverable_of_mem_closure (K : ℝ) (hK : 0 ≤ K)
    (hQ : ∀ N, ‖T.remainder N‖ ≤ K) (x : T.Obj 0)
    (hx : x ∈ closure T.finiteCore) : x ∈ T.recoverable := by
  apply tendsto_zero_iff_norm_tendsto_zero.mpr
  apply Metric.tendsto_atTop.mpr
  intro ε hε
  have hK1 : 0 < K+1 := by linarith
  obtain ⟨y, ⟨N, hN⟩, hxy⟩ := Metric.mem_closure_iff.1 hx
    (ε/(K+1)) (div_pos hε hK1)
  refine ⟨N, fun n hn => ?_⟩
  have hy : T.remainder n y = 0 := T.remainder_zero_after y N hN n hn
  have hd : T.remainder n x = T.remainder n (x-y) := by rw [map_sub, hy, sub_zero]
  have hnlt : ‖T.remainder n x‖ < ε := by
    calc
      _ = ‖T.remainder n (x-y)‖ := congrArg norm hd
      _ ≤ ‖T.remainder n‖ * ‖x-y‖ := (T.remainder n).le_opNorm _
      _ ≤ K * ‖x-y‖ := mul_le_mul_of_nonneg_right (hQ n) (norm_nonneg _)
      _ ≤ (K+1) * ‖x-y‖ := by nlinarith [norm_nonneg (x-y)]
      _ < (K+1) * (ε/(K+1)) :=
        mul_lt_mul_of_pos_left (by simpa only [dist_eq_norm] using hxy) hK1
      _ = ε := by field_simp
  simpa only [Real.dist_eq, sub_zero, abs_of_nonneg (norm_nonneg _)] using hnlt

/-- Exact description of the infinite reconstruction domain under uniform bounds. -/
theorem recoverable_iff_closure_finiteCore (K : ℝ) (hK : 0 ≤ K)
    (hQ : ∀ N, ‖T.remainder N‖ ≤ K) (x : T.Obj 0) :
    x ∈ T.recoverable ↔ x ∈ closure T.finiteCore :=
  ⟨T.recoverable_mem_closure_finiteCore x, T.recoverable_of_mem_closure K hK hQ x⟩

/-- Universal reconstruction is equivalent to density, not assumed from the outset. -/
theorem all_recoverable_iff_dense (K : ℝ) (hK : 0 ≤ K)
    (hQ : ∀ N, ‖T.remainder N‖ ≤ K) :
    (∀ x, x ∈ T.recoverable) ↔ Dense T.finiteCore := by
  constructor
  · intro h x
    exact T.recoverable_mem_closure_finiteCore x (h x)
  · intro h x
    exact T.recoverable_of_mem_closure K hK hQ x (h x)

/-- A directly usable infinite reconstruction theorem from stability and density. -/
theorem ordered_reconstruction_of_dense (K : ℝ) (hK : 0 ≤ K)
    (hQ : ∀ N, ‖T.remainder N‖ ≤ K) (hdense : Dense T.finiteCore)
    (x : T.Obj 0) :
    Tendsto (fun N => ∑ n ∈ Finset.range N, T.detailTerm x n) atTop (𝓝 x) := by
  apply (T.ordered_reconstruction_iff x).2
  exact T.recoverable_of_mem_closure K hK hQ x (hdense x)

/-- Density plus stability excludes all nonzero persistent coarse information. -/
theorem persistent_eq_bot_of_dense (K : ℝ) (hK : 0 ≤ K)
    (hQ : ∀ N, ‖T.remainder N‖ ≤ K) (hdense : Dense T.finiteCore) :
    T.persistent = ⊥ := by
  apply le_antisymm _ bot_le
  intro x hx
  rw [Submodule.mem_bot]
  exact T.persistent_recoverable_zero x hx
    (T.recoverable_of_mem_closure K hK hQ x (hdense x))

end CoarseningCascade
end KomorebiSpace
end
