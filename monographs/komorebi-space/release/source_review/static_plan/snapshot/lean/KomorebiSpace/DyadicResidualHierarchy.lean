import KomorebiSpace.DyadicResidualSplit
import KomorebiSpace.CoarseningCascade

set_option autoImplicit false

/-!
# Actual iterated dyadic residual reconstruction

The target splitting is constructed at each coarser resolution by composition.
Consequently every finite depth has a lossless residual hierarchy. There is
no assertion of uniform bounds or convergence at infinite depth.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace DyadicResidual
open BanachTower
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (Y : BanachTower.{u,v} 𝕜) (hY : ∀ n, ‖Y.down n‖ ≤ 1) (L : Splitting Y)

/-- Target sections remain available after pairing, by composing adjacent sections. -/
def sampledSplitting : Splitting (sampled Y hY) where
  up n := (L.up (2*n+1)).comp (L.up (2*n))
  down_up n := by
    change (restriction Y (show 2*n ≤ 2*(n+1) from schedule_monotone (Nat.le_succ n))).comp
      ((L.up (2*n+1)).comp (L.up (2*n))) = ContinuousLinearMap.id 𝕜 (Y.Obj (2*n))
    rw [restriction_succ Y (show 2*n ≤ 2*n+1 by omega), restriction_adjacent]
    ext y
    change Y.down (2*n) (Y.down (2*n+1) (L.up (2*n+1) (L.up (2*n) y))) = y
    rw [L.down_up_apply, L.down_up_apply]
  bound := L.bound * L.bound
  up_bound n := by
    exact ((L.up (2*n+1)).opNorm_comp_le (L.up (2*n))).trans
      (mul_le_mul (L.up_bound _) (L.up_bound _) (norm_nonneg _) (NNReal.coe_nonneg _))

/-- The full input to one genuine dyadic residual map. -/
structure System (𝕜 : Type u) [NontriviallyNormedField 𝕜] where
  source : BanachTower.{u,v} 𝕜
  target : BanachTower.{u,v} 𝕜
  source_contractive : ∀ n, ‖source.down n‖ ≤ 1
  target_contractive : ∀ n, ‖target.down n‖ ≤ 1
  target_splitting : Splitting target

namespace System
variable (T : System.{u,v} 𝕜)

/-- Coarsen both actual towers on the same paired schedule. -/
def next : System.{u,v} 𝕜 where
  source := sampled T.source T.source_contractive
  target := sampled T.target T.target_contractive
  source_contractive n := restriction_contractive T.source T.source_contractive
    (schedule_monotone (Nat.le_succ n))
  target_contractive n := restriction_contractive T.target T.target_contractive
    (schedule_monotone (Nat.le_succ n))
  target_splitting := sampledSplitting T.target T.target_contractive T.target_splitting

def stage : ℕ → System.{u,v} 𝕜
  | 0 => T
  | n+1 => (stage n).next

/-- This cascade uses the actual residual accumulation at every depth. -/
def cascade : CoarseningCascade.{u,v} 𝕜 where
  Obj n := Residuals (T.stage n).source (T.stage n).target
  down n := coarsen (T.stage n).source (T.stage n).target
    (T.stage n).source_contractive (T.stage n).target_contractive
  splitting n := sectionC (T.stage n).source (T.stage n).target
    (T.stage n).source_contractive (T.stage n).target_contractive (T.stage n).target_splitting

/-- No scalar-model substitution: reconstruction is on the original residual space. -/
theorem residual_reconstruction (r : Residuals T.source T.target) (N : ℕ) :
    r = (∑ n ∈ Finset.range N, T.cascade.detailTerm r n) +
      T.cascade.restore N (T.cascade.level r N) := T.cascade.reconstruction r N

/-- Retained details plus the final coarse datum detect exactness at every finite depth. -/
theorem exactness_iff_hierarchy (f : Candidates T.source T.target) (N : ℕ) :
    Exact T.source T.target f ↔
      (∀ n < N, T.cascade.detail (differential T.source T.target f) n = 0) ∧
      T.cascade.level (differential T.source T.target f) N = 0 := by
  rw [exact_iff_differential_zero]
  exact T.cascade.zero_iff _ N

end System
end DyadicResidual
end KomorebiSpace
end
