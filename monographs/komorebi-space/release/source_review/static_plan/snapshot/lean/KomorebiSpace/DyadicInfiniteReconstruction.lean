import KomorebiSpace.DyadicResidualHierarchy
import KomorebiSpace.CascadeDensity

set_option autoImplicit false

/-!
# Infinite retained-detail reconstruction for the actual dyadic tower residual

All-level detail injectivity is proved from the actual parity lift, without a
convergence assumption. Norm reconstruction requires a separate analytic
condition. No arbitrary replacement of the tower coarsening by a scalar model
is used in these theorems.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace DyadicResidual
namespace System
open BanachTower Filter
open scoped Topology
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (T : System.{u,v} 𝕜)

/-- An explicitly typed view of the actual residual at coarsening depth j. -/
def residualLevel (r : Residuals T.source T.target) (j : ℕ) :
    Residuals (T.stage j).source (T.stage j).target := T.cascade.level r j

/-- All details determine every fine coordinate, via strong induction on its index. -/
theorem all_details_zero_implies_zero (r : Residuals T.source T.target)
    (hd : ∀ j, T.cascade.detail r j = 0) : r = 0 := by
  have hcoord : ∀ k j, T.residualLevel r j k = 0 := by
    intro k
    induction k using Nat.strong_induction_on with
    | h k ih =>
      intro j
      let U := T.stage j
      have hh : hidden U.source U.target U.source_contractive U.target_contractive
          U.target_splitting (T.residualLevel r j) = 0 := hd j
      have hpar : k = 2*(k/2) ∨ k = 2*(k/2)+1 := by omega
      rcases hpar with he | ho
      · have hv := congrArg (fun f : Residuals U.source U.target => f (2*(k/2))) hh
        rw [hidden_even] at hv
        rw [he]
        exact hv
      · have hv := congrArg (fun f : Residuals U.source U.target => f (2*(k/2)+1)) hh
        rw [hidden_odd] at hv
        have hk : k/2 < k := by omega
        have hc : coarsen U.source U.target U.source_contractive U.target_contractive
            (T.residualLevel r j) (k/2) = 0 := ih (k/2) hk (j+1)
        change T.residualLevel r j (2*(k/2)+1) -
          (U.target_splitting.up (2*(k/2))).comp
            (coarsen U.source U.target U.source_contractive U.target_contractive
              (T.residualLevel r j) (k/2)) = 0 at hv
        rw [hc, ContinuousLinearMap.comp_zero, sub_zero] at hv
        rw [ho]
        exact hv
  apply lp.ext
  funext k
  exact hcoord k 0

/-- Unlike arbitrary split cascades, this actual dyadic cascade has no invisible
nonzero persistent residual. -/
theorem persistent_residual_eq_bot : T.cascade.persistent = ⊥ := by
  apply le_antisymm _ bot_le
  intro r hr
  rw [Submodule.mem_bot]
  exact T.all_details_zero_implies_zero r
    ((T.cascade.persistent_iff_details_zero r).1 hr)

/-- All detail coordinates are lossless at infinite depth, without norm convergence. -/
theorem infinite_details_injective (r s : Residuals T.source T.target)
    (h : ∀ j, T.cascade.detail r j = T.cascade.detail s j) : r = s := by
  have hm := (T.cascade.equal_details_iff_persistent_difference r s).1 h
  rw [T.persistent_residual_eq_bot, Submodule.mem_bot] at hm
  exact sub_eq_zero.mp hm

/-- Every-scale detail vanishing detects actual fine compatibility. -/
theorem exactness_iff_all_details (f : Candidates T.source T.target) :
    Exact T.source T.target f ↔
    ∀ j, T.cascade.detail (differential T.source T.target f) j = 0 := by
  rw [exact_iff_differential_zero]
  constructor
  · intro h j; rw [h]; exact T.cascade.detail_zero j
  · exact T.all_details_zero_implies_zero _

/-- Norm reconstruction has its own, strictly analytic, criterion. -/
theorem ordered_residual_reconstruction_iff (r : Residuals T.source T.target) :
    Tendsto (fun N => ∑ n ∈ Finset.range N, T.cascade.detailTerm r n) atTop (𝓝 r) ↔
    Tendsto (fun N => T.cascade.remainder N r) atTop (𝓝 0) :=
  T.cascade.ordered_reconstruction_iff r

theorem cascade_zero_complete : CompleteSpace (T.cascade.Obj 0) := by
  change CompleteSpace (Residuals T.source T.target)
  infer_instance

/-- Absolute summability is now enough because the dyadic persistent space was
proved trivial, rather than assumed so. -/
theorem absolute_residual_reconstruction (r : Residuals T.source T.target)
    (hs : Summable (fun n => ‖T.cascade.detailTerm r n‖)) :
    (∑' n, T.cascade.detailTerm r n) = r := by
  let : CompleteSpace (T.cascade.Obj 0) := T.cascade_zero_complete
  exact T.cascade.tsum_reconstruction r hs T.persistent_residual_eq_bot

/-- Any convergent dyadic remainder must converge to zero. -/
theorem convergent_remainder_zero (r z : Residuals T.source T.target)
    (hz : Tendsto (fun N => T.cascade.remainder N r) atTop (𝓝 z)) : z = 0 := by
  have hp := T.cascade.remainder_limit_persistent r z hz
  rw [T.persistent_residual_eq_bot] at hp
  change z = 0 at hp
  exact hp

/-- The section bound stays at most one under actual dyadic composition. -/
theorem stage_section_bound_le_one (hL : T.target_splitting.bound ≤ 1) (n : ℕ) :
    (T.stage n).target_splitting.bound ≤ 1 := by
  induction n with
  | zero => exact hL
  | succ n ih =>
    change (T.stage n).target_splitting.bound * (T.stage n).target_splitting.bound ≤ 1
    exact (mul_le_mul ih ih (by positivity) (by positivity)).trans (by norm_num)

theorem cascade_lifts_contractive (hL : T.target_splitting.bound ≤ 1) (n : ℕ) :
    ‖(T.cascade.splitting n).lift‖ ≤ 1 := by
  let U := T.stage n
  change ‖lift U.source U.target U.source_contractive U.target_contractive U.target_splitting‖ ≤ 1
  exact (lift_opNorm U.source U.target U.source_contractive U.target_contractive
    U.target_splitting).trans (by exact_mod_cast T.stage_section_bound_le_one hL n)

/-- When section norms are at most one, no amplification factor is required. -/
theorem residual_reconstruction_of_coarse_decay (hL : T.target_splitting.bound ≤ 1)
    (r : Residuals T.source T.target)
    (hr : Tendsto (fun N => ‖T.cascade.level r N‖) atTop (𝓝 0)) :
    Tendsto (fun N => ∑ n ∈ Finset.range N, T.cascade.detailTerm r n) atTop (𝓝 r) := by
  apply (T.cascade.ordered_reconstruction_iff r).2
  exact T.cascade.recoverable_of_coarse_decay (T.cascade_lifts_contractive hL) r hr

/-- Typed finite reconstruction on the original residual space. -/
def reconstructedResidual (N : ℕ) :
    Residuals T.source T.target →L[𝕜] Residuals T.source T.target :=
  T.cascade.reconstructed N

/-- Finite error estimate in the same contractive-section case. -/
theorem residual_error_le_coarse (hL : T.target_splitting.bound ≤ 1)
    (r : Residuals T.source T.target) (N : ℕ) :
    ‖r - T.reconstructedResidual N r‖ ≤ ‖T.cascade.level r N‖ := by
  apply (T.cascade.reconstruction_error_bound r N).trans
  simpa only [one_mul] using mul_le_mul_of_nonneg_right
    (T.cascade.liftGain_le_one (T.cascade_lifts_contractive hL) N) (norm_nonneg _)

/-- Vanishing N successive details determines the first 2^N-1 coordinates
at the starting scale. The target/source operator fibers remain the actual ones. -/
theorem finite_details_zero_coordinate (r : Residuals T.source T.target)
    (N j k : ℕ)
    (hd : ∀ i < N, T.cascade.detail r (j+i) = 0)
    (hk : k+1 < 2^N) : T.residualLevel r j k = 0 := by
  induction N generalizing j k with
  | zero => simp only [pow_zero] at hk; omega
  | succ N ih =>
    let U := T.stage j
    have hh : hidden U.source U.target U.source_contractive U.target_contractive
        U.target_splitting (T.residualLevel r j) = 0 := by
      have h := hd 0 (Nat.zero_lt_succ N)
      rw [Nat.add_zero] at h
      exact h
    have hpar : k = 2*(k/2) ∨ k = 2*(k/2)+1 := by omega
    rcases hpar with he | ho
    · have hv := congrArg (fun f : Residuals U.source U.target => f (2*(k/2))) hh
      rw [hidden_even] at hv
      rw [he]
      exact hv
    · have hv := congrArg (fun f : Residuals U.source U.target => f (2*(k/2)+1)) hh
      rw [hidden_odd] at hv
      have hk' : k/2+1 < 2^N := by rw [pow_succ] at hk; omega
      have hd' : ∀ i < N, T.cascade.detail r ((j+1)+i) = 0 := by
        intro i hi
        rw [show j+1+i = j+(i+1) by omega]
        exact hd (i+1) (by omega)
      have hc : coarsen U.source U.target U.source_contractive U.target_contractive
          (T.residualLevel r j) (k/2) = 0 := ih (j+1) (k/2) hd' hk'
      change T.residualLevel r j (2*(k/2)+1) -
        (U.target_splitting.up (2*(k/2))).comp
          (coarsen U.source U.target U.source_contractive U.target_contractive
            (T.residualLevel r j) (k/2)) = 0 at hv
      rw [hc, ContinuousLinearMap.comp_zero, sub_zero] at hv
      rw [ho]
      exact hv

/-- An explicitly typed original-space remainder. -/
def residualRemainder (N : ℕ) :
    Residuals T.source T.target →L[𝕜] Residuals T.source T.target := T.cascade.remainder N

/-- Restored dyadic remainders are supported beyond the first 2^N-1 coordinates. -/
theorem remainder_coordinate_zero (r : Residuals T.source T.target) (N k : ℕ)
    (hk : k+1 < 2^N) : T.residualRemainder N r k = 0 := by
  have hd : ∀ i < N, T.cascade.detail (T.residualRemainder N r) (0+i) = 0 := by
    intro i hi
    rw [Nat.zero_add]
    exact T.cascade.remainder_details_below r N i hi
  exact T.finite_details_zero_coordinate (T.residualRemainder N r) N 0 k hd hk

/-- Every fixed coordinate is reconstructed exactly after a finite depth. -/
theorem reconstruction_coordinate (r : Residuals T.source T.target) (N k : ℕ)
    (hk : k+1 < 2^N) : T.reconstructedResidual N r k = r k := by
  change r k - T.residualRemainder N r k = r k
  rw [T.remainder_coordinate_zero r N k hk, sub_zero]

/-- Coordinatewise operator-norm reconstruction holds for every bounded residual,
even when reconstruction in the uniform residual norm fails. -/
theorem coordinatewise_reconstruction (r : Residuals T.source T.target) (k : ℕ) :
    Tendsto (fun N => T.reconstructedResidual N r k) atTop (𝓝 (r k)) := by
  apply tendsto_const_nhds.congr'
  filter_upwards [eventually_ge_atTop (k+1)] with N hN
  exact (T.reconstruction_coordinate r N k (hN.trans_lt N.lt_two_pow_self)).symm


end System
end DyadicResidual
end KomorebiSpace
end
