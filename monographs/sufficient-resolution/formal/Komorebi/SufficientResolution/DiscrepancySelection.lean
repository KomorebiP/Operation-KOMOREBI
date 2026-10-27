import Komorebi.SufficientResolution.DiscrepancyResidual

/-!
# Existence and uniqueness of an actual discrepancy parameter

A target strictly between a feasible residual and the norm of the data is attained
at exactly one positive parameter. The large-data clause is essential.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.DiscrepancySelection

open TikhonovConstruction TikhonovOptimality TikhonovBounds DiscrepancyResidual

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

 theorem small_parameter_below_target (v : V) (rho : ℝ) (g : G)
    (hfit : ‖A g-v‖ < rho) :
    ∃ lam : ℝ, 0 < lam ∧ residual A v lam < rho := by
  have hr : 0 < rho := (norm_nonneg _).trans_lt hfit
  have hd : 0 < rho^2-‖A g-v‖^2 := by nlinarith [norm_nonneg (A g-v)]
  let lam := (rho^2-‖A g-v‖^2)/(2*(‖g‖^2+1))
  have hl : 0 < lam := by dsimp [lam]; positivity
  have he : lam*(2*(‖g‖^2+1)) = rho^2-‖A g-v‖^2 := by
    dsimp [lam]; field_simp
  refine ⟨lam, hl, ?_⟩
  have hm := minimizes A lam hl v g
  unfold objective at hm
  rw [DiscrepancyResidual.residual, recoveryAt_pos A lam hl]
  have hn := mul_nonneg hl.le (sq_nonneg ‖regularized A lam hl v‖)
  have hg := mul_nonneg hl.le (sq_nonneg ‖g‖)
  have hs : ‖A (regularized A lam hl v)-v‖^2 < rho^2 := by nlinarith
  nlinarith [norm_nonneg (A (regularized A lam hl v)-v)]

 theorem fitted_data_inverse_parameter_bound (v : V) (lam : ℝ) (hl : 0 < lam) :
    ‖A (regularized A lam hl v)‖ ≤ (‖A‖*‖A.adjoint v‖)/lam := by
  calc
    _ ≤ ‖A‖*‖regularized A lam hl v‖ := A.le_opNorm _
    _ ≤ ‖A‖*(‖A.adjoint v‖/lam) :=
      mul_le_mul_of_nonneg_left (resolvent_bound A lam hl (A.adjoint v)) (norm_nonneg _)
    _ = _ := by ring

 theorem large_parameter_above_target (v : V) (rho a : ℝ)
    (ha : 0 < a) (hu : rho < ‖v‖) :
    ∃ mu : ℝ, a ≤ mu ∧ rho < residual A v mu := by
  let k := ‖A‖*‖A.adjoint v‖
  let d := ‖v‖-rho
  have hk : 0 ≤ k := mul_nonneg (norm_nonneg _) (norm_nonneg _)
  have hd : 0 < d := sub_pos.mpr hu
  let mu := a+1+k/d
  have hma : a ≤ mu := by dsimp [mu]; linarith [div_nonneg hk hd.le]
  have hm : 0 < mu := ha.trans_le hma
  have hprod : mu*d = (a+1)*d+k := by dsimp [mu]; field_simp
  have hsmall : k/mu < d := (div_lt_iff₀ hm).mpr (by nlinarith)
  refine ⟨mu, hma, ?_⟩
  have hb := fitted_data_inverse_parameter_bound A v mu hm
  have ht : ‖v‖ ≤ ‖A (regularized A mu hm v)-v‖+‖A (regularized A mu hm v)‖ := by
    have h := norm_sub_le (A (regularized A mu hm v)) (A (regularized A mu hm v)-v)
    simpa only [sub_sub_cancel, norm_sub_rev, add_comm] using h
  rw [DiscrepancyResidual.residual, recoveryAt_pos A mu hm]
  dsimp [k, d] at hsmall
  linarith

 theorem exists_parameter (v : V) (rho : ℝ)
    (hfeas : ∃ g : G, ‖A g-v‖ < rho) (hu : rho < ‖v‖) :
    ∃ lam : ℝ, 0 < lam ∧ residual A v lam = rho := by
  obtain ⟨g, hg⟩ := hfeas
  obtain ⟨a, ha, hlo⟩ := small_parameter_below_target A v rho g hg
  obtain ⟨b, hab, hhi⟩ := large_parameter_above_target A v rho a ha hu
  obtain ⟨lam, hlam, he⟩ := intermediate_value_Icc hab
    (residual_continuousOn_interval A v ha) ⟨hlo.le, hhi.le⟩
  exact ⟨lam, ha.trans_le hlam.1, he⟩

 theorem parameter_unique (v : V) (rho : ℝ) (hu : rho < ‖v‖)
    {lam mu : ℝ} (hl : 0 < lam) (hm : 0 < mu)
    (hel : residual A v lam = rho) (hem : residual A v mu = rho) : lam = mu := by
  have hv : A.adjoint v ≠ 0 := by
    intro hz
    have h := residual_constant_of_adjoint_zero A v hz lam hl
    rw [hel] at h
    linarith
  rcases lt_trichotomy lam mu with hlt | he | hgt
  · have h := residual_strictMono A v hv hl hm hlt; rw [hel, hem] at h; exact False.elim (lt_irrefl _ h)
  · exact he
  · have h := residual_strictMono A v hv hm hl hgt; rw [hel, hem] at h; exact False.elim (lt_irrefl _ h)

 theorem exists_unique_parameter (v : V) (rho : ℝ)
    (hfeas : ∃ g : G, ‖A g-v‖ < rho) (hu : rho < ‖v‖) :
    ∃! lam : ℝ, 0 < lam ∧ residual A v lam = rho := by
  obtain ⟨lam, hl, he⟩ := exists_parameter A v rho hfeas hu
  exact ⟨lam, ⟨hl, he⟩, fun mu hm => parameter_unique A v rho hu hm.1 hl hm.2 he⟩

 theorem residual_floor_le (v : V) (lam : ℝ) :
    Metric.infDist v (A.range : Set V) ≤ residual A v lam := by
  have h := Metric.infDist_le_dist_of_mem (x := v) (A.mem_range_self (recoveryAt A lam v))
  simpa only [dist_eq_norm, norm_sub_rev, DiscrepancyResidual.residual, ContinuousLinearMap.coe_coe] using h

 theorem exists_unique_parameter_of_distance (v : V) (rho : ℝ)
    (hf : Metric.infDist v (A.range : Set V) < rho) (hu : rho < ‖v‖) :
    ∃! lam : ℝ, 0 < lam ∧ residual A v lam = rho := by
  have hn : (A.range : Set V).Nonempty := ⟨0, A.range.zero_mem⟩
  obtain ⟨y, hy, hd⟩ := (Metric.infDist_lt_iff hn).mp hf
  obtain ⟨g, rfl⟩ := hy
  apply exists_unique_parameter A v rho _ hu
  exact ⟨g, by simpa only [dist_eq_norm, norm_sub_rev, ContinuousLinearMap.coe_coe] using hd⟩

 theorem root_in_bracket (v : V) (rho : ℝ) (hu : rho < ‖v‖)
    (a b lam : ℝ) (ha : 0 < a) (hb : 0 < b) (hl : 0 < lam)
    (hlo : residual A v a ≤ rho) (hhi : rho ≤ residual A v b)
    (he : residual A v lam = rho) : a ≤ lam ∧ lam ≤ b := by
  have hv : A.adjoint v ≠ 0 := by
    intro hz
    have hc := residual_constant_of_adjoint_zero A v hz lam hl
    rw [he] at hc; linarith
  constructor
  · by_contra h
    have hs := residual_strictMono A v hv hl ha (lt_of_not_ge h)
    rw [he] at hs; linarith
  · by_contra h
    have hs := residual_strictMono A v hv hb hl (lt_of_not_ge h)
    rw [he] at hs; linarith

/-- Positive exact root, selected from the proved existence theorem. -/
def parameter (v : V) (rho : ℝ)
    (hfeas : ∃ g : G, ‖A g-v‖ < rho) (hu : rho < ‖v‖) : ℝ :=
  Classical.choose (exists_parameter A v rho hfeas hu)

 theorem parameter_pos (v : V) (rho : ℝ)
    (hfeas : ∃ g : G, ‖A g-v‖ < rho) (hu : rho < ‖v‖) :
    0 < parameter A v rho hfeas hu :=
  (Classical.choose_spec (exists_parameter A v rho hfeas hu)).1

 theorem parameter_hits_target (v : V) (rho : ℝ)
    (hfeas : ∃ g : G, ‖A g-v‖ < rho) (hu : rho < ‖v‖) :
    residual A v (parameter A v rho hfeas hu) = rho :=
  (Classical.choose_spec (exists_parameter A v rho hfeas hu)).2

 theorem noisy_parameter_exists (g : G) (v : V) (eta tau : ℝ)
    (heta : 0 < eta) (htau : 1 < tau) (hnoise : ‖A g-v‖ ≤ eta)
    (hlarge : tau*eta < ‖v‖) :
    ∃! lam : ℝ, 0 < lam ∧ residual A v lam = tau*eta := by
  apply exists_unique_parameter A v (tau*eta) _ hlarge
  exact ⟨g, hnoise.trans_lt (by nlinarith)⟩

end Komorebi.SufficientResolution.DiscrepancySelection
