import Komorebi.SufficientResolution.TikhonovPerturbation
import Mathlib.Topology.Order.IntermediateValue

/-!
# The actual Tikhonov discrepancy curve

The total extension below is used only to express continuity on positive intervals.
All mathematical selection theorems restrict the parameter to strictly positive values.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.DiscrepancyResidual

open TikhonovConstruction TikhonovOptimality TikhonovBounds TikhonovPerturbation

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

/-- Total extension of the constructed recovery. Nonpositive parameters are not admissible. -/
def recoveryAt (lam : ℝ) : V →L[ℝ] G :=
  if h : 0 < lam then regularized A lam h else 0

 theorem recoveryAt_pos (lam : ℝ) (h : 0 < lam) :
    recoveryAt A lam = regularized A lam h := by simp [recoveryAt, h]

/-- The actual data residual, not a surrogate objective. -/
def residual (v : V) (lam : ℝ) : ℝ := ‖A (recoveryAt A lam v)-v‖

 theorem residual_nonneg (v : V) (lam : ℝ) : 0 ≤ residual A v lam := norm_nonneg _

 theorem residual_le_data (v : V) (lam : ℝ) (h : 0 < lam) :
    residual A v lam ≤ ‖v‖ := by
  rw [residual, recoveryAt_pos A lam h]
  exact residual_data_bound A lam h v

 theorem source_norm_antitone (v : V) {lam mu : ℝ}
    (hlam : 0 < lam) (hmu : 0 < mu) (hle : lam ≤ mu) :
    ‖regularized A mu hmu v‖ ≤ ‖regularized A lam hlam v‖ := by
  rcases hle.eq_or_lt with he | hlt
  · subst mu; rfl
  have h1 := minimizes A lam hlam v (regularized A mu hmu v)
  have h2 := minimizes A mu hmu v (regularized A lam hlam v)
  unfold objective at h1 h2
  apply (sq_le_sq₀ (norm_nonneg _) (norm_nonneg _)).mp
  nlinarith

 theorem residual_monotone (v : V) {lam mu : ℝ}
    (hlam : 0 < lam) (hmu : 0 < mu) (hle : lam ≤ mu) :
    residual A v lam ≤ residual A v mu := by
  have hn := source_norm_antitone A v hlam hmu hle
  have hs := (sq_le_sq₀ (norm_nonneg _) (norm_nonneg _)).mpr hn
  have h := minimizes A lam hlam v (regularized A mu hmu v)
  unfold objective at h
  rw [residual, residual, recoveryAt_pos A lam hlam, recoveryAt_pos A mu hmu]
  apply (sq_le_sq₀ (norm_nonneg _) (norm_nonneg _)).mp
  nlinarith

 theorem equal_residual_forces_zero (v : V) {lam mu : ℝ}
    (hlam : 0 < lam) (hmu : 0 < mu) (hlt : lam < mu)
    (he : residual A v lam = residual A v mu) : A.adjoint v = 0 := by
  have h1 := minimizes A lam hlam v (regularized A mu hmu v)
  have h2 := minimizes A mu hmu v (regularized A lam hlam v)
  have he' : ‖A (regularized A lam hlam v)-v‖ =
      ‖A (regularized A mu hmu v)-v‖ := by
    simpa only [residual, recoveryAt_pos A lam hlam, recoveryAt_pos A mu hmu] using he
  have hn : ‖regularized A lam hlam v‖^2 = ‖regularized A mu hmu v‖^2 := by
    unfold objective at h1 h2
    rw [he'] at h1 h2
    nlinarith
  have hx : regularized A mu hmu v = regularized A lam hlam v := by
    apply (objective_equal_iff A lam hlam v _).mp
    unfold objective
    rw [he', hn]
  have e1 := solution_energy A lam hlam v
  have e2 := solution_energy A mu hmu v
  rw [hx] at e2
  have hz : ‖regularized A lam hlam v‖^2 = 0 := by nlinarith
  have hx0 := norm_eq_zero.mp (sq_eq_zero_iff.mp hz)
  have h := normal_equation A lam hlam v
  rw [hx0, map_zero] at h
  exact h.symm

 theorem residual_strictMono (v : V) (hv : A.adjoint v ≠ 0) {lam mu : ℝ}
    (hlam : 0 < lam) (hmu : 0 < mu) (hlt : lam < mu) :
    residual A v lam < residual A v mu := by
  exact (residual_monotone A v hlam hmu hlt.le).lt_of_ne
    (fun he => hv (equal_residual_forces_zero A v hlam hmu hlt he))

 theorem residual_constant_of_adjoint_zero (v : V) (hv : A.adjoint v = 0)
    (lam : ℝ) (hlam : 0 < lam) : residual A v lam = ‖v‖ := by
  simp [residual, recoveryAt_pos A lam hlam, regularized, hv]

 theorem residual_difference_bound (v : V) {a lam mu : ℝ}
    (ha : 0 < a) (hlam : a ≤ lam) (hmu : a ≤ mu) :
    |residual A v lam-residual A v mu| ≤
      (‖A‖*‖A.adjoint v‖/(a*a))*|lam-mu| := by
  have hl : 0 < lam := ha.trans_le hlam
  have hm : 0 < mu := ha.trans_le hmu
  calc
    _ ≤ ‖(A (regularized A lam hl v)-v)-(A (regularized A mu hm v)-v)‖ := by
      simpa only [residual, recoveryAt_pos A lam hl, recoveryAt_pos A mu hm] using
        abs_norm_sub_norm_le (A (regularized A lam hl v)-v) (A (regularized A mu hm v)-v)
    _ = ‖A (regularized A lam hl v-regularized A mu hm v)‖ := by
      rw [map_sub]; congr 1; abel
    _ ≤ ‖A‖*‖regularized A lam hl v-regularized A mu hm v‖ := A.le_opNorm _
    _ ≤ ‖A‖*(|mu-lam|/(lam*mu)*‖A.adjoint v‖) := by
      apply mul_le_mul_of_nonneg_left _ (norm_nonneg A)
      exact parameter_difference_bound A lam mu hl hm (A.adjoint v)
    _ ≤ ‖A‖*(|mu-lam|/(a*a)*‖A.adjoint v‖) := by
      gcongr
    _ = _ := by rw [abs_sub_comm mu lam]; ring

 theorem residual_continuousOn_interval (v : V) {a b : ℝ} (ha : 0 < a) :
    ContinuousOn (residual A v) (Set.Icc a b) := by
  apply Metric.continuousOn_iff.mpr
  intro x hx eps heps
  let c := ‖A‖*‖A.adjoint v‖/(a*a)
  have hc : 0 ≤ c := by dsimp [c]; positivity
  refine ⟨eps/(c+1), by positivity, ?_⟩
  intro y hy hxy
  rw [Real.dist_eq] at hxy ⊢
  have hb := residual_difference_bound A v ha hy.1 hx.1
  have hp : 0 < c+1 := by positivity
  have hm : |y-x| * (c+1) < eps := (lt_div_iff₀ hp).mp hxy
  change |residual A v y-residual A v x| < eps
  change |residual A v y-residual A v x| ≤ c*|y-x| at hb
  nlinarith [abs_nonneg (y-x)]

end Komorebi.SufficientResolution.DiscrepancyResidual
