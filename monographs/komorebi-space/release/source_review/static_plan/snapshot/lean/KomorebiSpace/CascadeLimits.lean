import KomorebiSpace.CascadeProjections
import Mathlib.Analysis.Normed.Group.InfiniteSum
import Mathlib.Analysis.SpecificLimits.Basic

set_option autoImplicit false

/-!
# Infinite reconstruction and the persistent coarse component

Natural-order partial sums are used unless absolute summability is explicitly
assumed. No unconditional `HasSum` claim is inferred merely from ordered
convergence. Coarse data must be lifted before their size is tested.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace CoarseningCascade
open Filter
open scoped Topology
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (T : CoarseningCascade.{u,v} 𝕜)

@[simp] theorem partial_error (x : T.Obj 0) (N : ℕ) :
    ‖x - T.reconstructed N x‖ = ‖T.remainder N x‖ := by
  rw [partial_apply, sub_sub_cancel]

/-- The exact convergence criterion, with no summability assumption. -/
theorem partial_tendsto_iff (x : T.Obj 0) :
    Tendsto (fun N => T.reconstructed N x) atTop (𝓝 x) ↔
    Tendsto (fun N => T.remainder N x) atTop (𝓝 0) := by
  constructor
  · intro h
    have hh := (tendsto_const_nhds (x := x)).sub h
    simpa only [partial_apply, sub_sub_cancel, sub_self] using hh
  · intro h
    have hh := (tendsto_const_nhds (x := x)).sub h
    simpa only [partial_apply, sub_zero] using hh

/-- The finite theorem upgrades to ordered infinite reconstruction precisely
when its actual lifted remainder vanishes. -/
theorem ordered_reconstruction_iff (x : T.Obj 0) :
    Tendsto (fun N => ∑ n ∈ Finset.range N, T.detailTerm x n) atTop (𝓝 x) ↔
    Tendsto (fun N => T.remainder N x) atTop (𝓝 0) := by
  simpa only [partial_eq_sum] using T.partial_tendsto_iff x

/-- Recoverable data form a linear subspace, not necessarily the entire space. -/
def recoverable : Submodule 𝕜 (T.Obj 0) where
  carrier := {x | Tendsto (fun N => T.remainder N x) atTop (𝓝 0)}
  zero_mem' := by simpa only [Set.mem_ofPred_eq, map_zero] using (tendsto_const_nhds (x := (0 : T.Obj 0)))
  add_mem' := by
    intro x y hx hy
    simpa only [Set.mem_ofPred_eq, map_add, zero_add] using hx.add hy
  smul_mem' := by
    intro c x hx
    simpa only [Set.mem_ofPred_eq, map_smul, smul_zero] using (tendsto_const_nhds (x := c)).smul hx

@[simp] theorem mem_recoverable (x : T.Obj 0) :
    x ∈ T.recoverable ↔ Tendsto (fun N => T.remainder N x) atTop (𝓝 0) := Iff.rfl

/-- The persistent and recoverable subspaces intersect only at zero. -/
theorem persistent_recoverable_zero (x : T.Obj 0)
    (hp : x ∈ T.persistent) (hr : x ∈ T.recoverable) : x = 0 := by
  change ∀ n, T.remainder n x = x at hp
  have h : Tendsto (fun _ : ℕ => x) atTop (𝓝 0) := by
    change Tendsto (fun N => T.remainder N x) atTop (𝓝 0) at hr
    simpa only [hp] using hr
  exact tendsto_nhds_unique tendsto_const_nhds h

theorem zero_iff_details_on_recoverable (x : T.Obj 0) (hx : x ∈ T.recoverable) :
    x = 0 ↔ ∀ n, T.detail x n = 0 := by
  constructor
  · rintro rfl; exact T.detail_zero
  · intro h
    exact T.persistent_recoverable_zero x ((T.persistent_iff_details_zero x).2 h) hx

/-- All detail coordinates are injective on the recoverable subspace. -/
theorem details_injective_on_recoverable (x y : T.Obj 0)
    (hx : x ∈ T.recoverable) (hy : y ∈ T.recoverable)
    (hd : ∀ n, T.detail x n = T.detail y n) : x = y := by
  apply sub_eq_zero.mp
  exact T.persistent_recoverable_zero (x-y)
    ((T.equal_details_iff_persistent_difference x y).1 hd)
    (T.recoverable.sub_mem hx hy)

/-- Every convergent remainder lands in the persistent coarse subspace. -/
theorem remainder_limit_persistent (x z : T.Obj 0)
    (hz : Tendsto (fun N => T.remainder N x) atTop (𝓝 z)) : z ∈ T.persistent := by
  intro m
  have h1 : Tendsto (fun N => T.remainder m (T.remainder N x)) atTop
      (𝓝 (T.remainder m z)) := (T.remainder m).continuous.continuousAt.tendsto.comp hz
  have h2 : Tendsto (fun N => T.remainder m (T.remainder N x)) atTop (𝓝 z) := by
    apply hz.congr'
    filter_upwards [eventually_ge_atTop m] with N hN
    exact (T.remainder_nested_left m N hN x).symm
  exact tendsto_nhds_unique h1 h2

/-- A convergent remainder is an explicit boundary term in infinite reconstruction. -/
theorem reconstruction_with_boundary (x z : T.Obj 0)
    (hz : Tendsto (fun N => T.remainder N x) atTop (𝓝 z)) :
    Tendsto (fun N => ∑ n ∈ Finset.range N, T.detailTerm x n) atTop (𝓝 (x-z)) ∧
    z ∈ T.persistent := by
  constructor
  · have hh := (tendsto_const_nhds (x := x)).sub hz
    simpa only [← partial_apply, partial_eq_sum] using hh
  · exact T.remainder_limit_persistent x z hz

/-- Absolute summability yields a boundary term; it does not by itself kill it. -/
theorem absolutely_summable_boundary [CompleteSpace (T.Obj 0)] (x : T.Obj 0)
    (hs : Summable (fun n => ‖T.detailTerm x n‖)) :
    x - ∑' n, T.detailTerm x n ∈ T.persistent := by
  have hsum := hs.of_norm.tendsto_sum_tsum_nat
  have hz : Tendsto (fun N => T.remainder N x) atTop
      (𝓝 (x - ∑' n, T.detailTerm x n)) := by
    have hh := (tendsto_const_nhds (x := x)).sub hsum
    simpa only [← partial_eq_sum, partial_apply, sub_sub_cancel] using hh
  exact T.remainder_limit_persistent x _ hz

/-- Absolute reconstruction is valid once the residual boundary is excluded. -/
theorem tsum_reconstruction [CompleteSpace (T.Obj 0)] (x : T.Obj 0)
    (hs : Summable (fun n => ‖T.detailTerm x n‖))
    (hp : T.persistent = ⊥) : (∑' n, T.detailTerm x n) = x := by
  have h := T.absolutely_summable_boundary x hs
  rw [hp, Submodule.mem_bot] at h
  exact (sub_eq_zero.mp h).symm

/-- Product gain for restoration, retaining possible amplification at each level. -/
def liftGain (N : ℕ) : ℝ := ∏ n ∈ Finset.range N, ‖(T.splitting n).lift‖

@[simp] theorem liftGain_zero : T.liftGain 0 = 1 := by simp [liftGain]
@[simp] theorem liftGain_succ (N : ℕ) :
    T.liftGain (N+1) = T.liftGain N * ‖(T.splitting N).lift‖ := by
  simp [liftGain, Finset.prod_range_succ]

theorem liftGain_nonneg (N : ℕ) : 0 ≤ T.liftGain N := by
  unfold liftGain
  exact Finset.prod_nonneg (fun n _ => norm_nonneg _)

theorem restore_gain_bound (N : ℕ) (y : T.Obj N) :
    ‖T.restore N y‖ ≤ T.liftGain N * ‖y‖ := by
  induction N with
  | zero => simp
  | succ N ih =>
    rw [restore_succ, liftGain_succ]
    calc
      _ ≤ T.liftGain N * ‖(T.splitting N).lift y‖ := ih _
      _ ≤ T.liftGain N * (‖(T.splitting N).lift‖ * ‖y‖) :=
        mul_le_mul_of_nonneg_left ((T.splitting N).lift.le_opNorm y) (T.liftGain_nonneg N)
      _ = _ := (mul_assoc _ _ _).symm

theorem reconstruction_error_bound (x : T.Obj 0) (N : ℕ) :
    ‖x-T.reconstructed N x‖ ≤ T.liftGain N * ‖T.level x N‖ := by
  rw [partial_error, remainder_apply]
  exact T.restore_gain_bound _ _

/-- Coarse decay after multiplication by the full restoration gain is sufficient. -/
theorem recoverable_of_weighted_coarse_decay (x : T.Obj 0)
    (h : Tendsto (fun N => T.liftGain N * ‖T.level x N‖) atTop (𝓝 0)) :
    x ∈ T.recoverable := by
  apply tendsto_zero_iff_norm_tendsto_zero.mpr
  apply squeeze_zero (fun _ => norm_nonneg _) _ h
  intro N
  rw [remainder_apply]
  exact T.restore_gain_bound _ _

/-- Quantitative geometric criterion allowing amplification and decay together. -/
theorem recoverable_of_geometric_bounds (x : T.Obj 0) (B C a b : ℝ)
    (hB : 0 ≤ B) (_hC : 0 ≤ C) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (hgap : a*b < 1)
    (hgain : ∀ N, T.liftGain N ≤ B*a^N)
    (hcoarse : ∀ N, ‖T.level x N‖ ≤ C*b^N) :
    x ∈ T.recoverable ∧
    ∀ N, ‖x-T.reconstructed N x‖ ≤ (B*C)*(a*b)^N := by
  have hbound (N : ℕ) : T.liftGain N * ‖T.level x N‖ ≤ (B*C)*(a*b)^N := by
    calc
      _ ≤ (B*a^N)*(C*b^N) := mul_le_mul (hgain N) (hcoarse N)
        (norm_nonneg _) (mul_nonneg hB (pow_nonneg ha N))
      _ = _ := by rw [mul_pow]; ring
  constructor
  · apply T.recoverable_of_weighted_coarse_decay
    apply squeeze_zero (fun N => mul_nonneg (T.liftGain_nonneg N) (norm_nonneg _)) hbound
    simpa only [mul_zero] using
      (tendsto_pow_atTop_nhds_zero_of_lt_one (mul_nonneg ha hb) hgap).const_mul (B*C)
  · intro N
    exact (T.reconstruction_error_bound x N).trans (hbound N)

/-- Contractive lifts cannot amplify the remaining coarse term. -/
theorem liftGain_le_one (hJ : ∀ n, ‖(T.splitting n).lift‖ ≤ 1) (N : ℕ) :
    T.liftGain N ≤ 1 := by
  induction N with
  | zero => simp
  | succ N ih =>
    rw [liftGain_succ]
    exact (mul_le_mul ih (hJ N) (norm_nonneg _) (by norm_num)).trans (by norm_num)

theorem recoverable_of_coarse_decay (hJ : ∀ n, ‖(T.splitting n).lift‖ ≤ 1)
    (x : T.Obj 0) (h : Tendsto (fun N => ‖T.level x N‖) atTop (𝓝 0)) :
    x ∈ T.recoverable := by
  apply T.recoverable_of_weighted_coarse_decay
  apply squeeze_zero (fun N => mul_nonneg (T.liftGain_nonneg N) (norm_nonneg _)) _ h
  intro N
  simpa only [one_mul] using
    mul_le_mul_of_nonneg_right (T.liftGain_le_one hJ N) (norm_nonneg (T.level x N))


end CoarseningCascade
end KomorebiSpace
end
