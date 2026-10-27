import Komorebi.SufficientResolution.ChangingDiscrepancy

/-!
# Candidate-dependent discrepancy without a prior source norm bound

The acceptance rule inflates the noise allowance by the norm of the candidate itself.
The lower discrepancy inequality then forces norm domination by any true feasible
identifiable source. This removes a supplied source-norm cap from the certificate.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.GeneralizedDiscrepancy

open TikhonovConstruction TikhonovOptimality DiscrepancyResidual
open OperatorUncertainty MinimumNormReconstruction DiscrepancyConvergence
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]

/-- Candidate-dependent effective noise. -/
def candidateNoise (eta delta : ℝ) (x : G) : ℝ := eta + delta * ‖x‖

omit [InnerProductSpace ℝ G] [CompleteSpace G] in
 theorem candidateNoise_nonneg (eta delta : ℝ) (x : G)
    (he : 0 ≤ eta) (hd : 0 ≤ delta) : 0 ≤ candidateNoise eta delta x := by
  exact add_nonneg he (mul_nonneg hd (norm_nonneg x))

omit [InnerProductSpace ℝ G] [CompleteSpace G] in
 theorem candidateNoise_mono_norm (eta delta : ℝ) {x y : G}
    (hd : 0 ≤ delta) (hxy : ‖x‖ ≤ ‖y‖) :
    candidateNoise eta delta x ≤ candidateNoise eta delta y := by
  simp only [candidateNoise]
  gcongr

/-- A generalized accepted source. The positive branch is an actual Tikhonov source
whose residual lies between one and `tau` times its candidate-dependent allowance. -/
def Accepted (C : G →L[ℝ] V) (v : V) (eta delta tau : ℝ) (x : G) : Prop :=
  (‖v‖ ≤ tau * eta ∧ x = 0) ∨
  ∃ (lam : ℝ) (hl : 0 < lam), x = regularized C lam hl v ∧
    candidateNoise eta delta x ≤ residual C v lam ∧
    residual C v lam ≤ tau * candidateNoise eta delta x

 theorem accepted_fit (C : G →L[ℝ] V) (v : V) (eta delta tau : ℝ) (x : G)
    (hx : Accepted C v eta delta tau x) :
    ‖C x-v‖ ≤ tau * candidateNoise eta delta x := by
  rcases hx with ⟨hs, rfl⟩ | ⟨lam, hl, rfl, _, hhi⟩
  · simp only [map_zero, zero_sub, norm_neg, candidateNoise, norm_zero, mul_zero, add_zero]
    exact hs
  · simpa only [DiscrepancyResidual.residual, DiscrepancyResidual.recoveryAt_pos C lam hl] using hhi

 theorem accepted_lower (C : G →L[ℝ] V) (v : V) (eta delta tau : ℝ) (x : G)
    (hx : Accepted C v eta delta tau x) (hn : tau * eta < ‖v‖) :
    candidateNoise eta delta x ≤ ‖C x-v‖ := by
  rcases hx with ⟨hs, _⟩ | ⟨lam, hl, rfl, hlo, _⟩
  · exact False.elim ((not_lt_of_ge hs) hn)
  · simpa only [DiscrepancyResidual.residual, DiscrepancyResidual.recoveryAt_pos C lam hl] using hlo

/-- Core self-bounding lemma: if the candidate-dependent lower discrepancy holds,
then the regularized candidate cannot have larger norm than a feasible comparison source. -/
 theorem regularized_norm_domination (C : G →L[ℝ] V) (v : V)
    (eta delta lam : ℝ) (hl : 0 < lam) (p : G)
    (hd : 0 ≤ delta)
    (hp : ‖C p-v‖ ≤ candidateNoise eta delta p)
    (hlo : candidateNoise eta delta (regularized C lam hl v) ≤
      ‖C (regularized C lam hl v)-v‖) :
    ‖regularized C lam hl v‖ ≤ ‖p‖ := by
  have hmin := minimizes C lam hl v p
  unfold objective at hmin
  by_contra h
  have hnorm : ‖p‖ < ‖regularized C lam hl v‖ := lt_of_not_ge h
  have hpn : candidateNoise eta delta p ≤
      candidateNoise eta delta (regularized C lam hl v) :=
    candidateNoise_mono_norm eta delta hd hnorm.le
  have hfit : ‖C p-v‖ ≤ ‖C (regularized C lam hl v)-v‖ :=
    hp.trans (hpn.trans hlo)
  have hfitsq : ‖C p-v‖^2 ≤ ‖C (regularized C lam hl v)-v‖^2 :=
    (sq_le_sq₀ (norm_nonneg _) (norm_nonneg _)).mpr hfit
  have hnormsq : ‖p‖^2 < ‖regularized C lam hl v‖^2 :=
    (sq_lt_sq₀ (norm_nonneg p) (norm_nonneg _)).mpr hnorm
  have hweighted : lam*‖p‖^2 < lam*‖regularized C lam hl v‖^2 :=
    mul_lt_mul_of_pos_left hnormsq hl
  nlinarith

 theorem accepted_norm_control (A C : G →L[ℝ] V) (p x : G) (v : V)
    (eta delta tau : ℝ)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hx : Accepted C v eta delta tau x) : ‖x‖ ≤ ‖p‖ := by
  have hdelta : 0 ≤ delta := operator_allowance_nonneg A C delta hd
  rcases hx with ⟨_, rfl⟩ | ⟨lam, hl, rfl, hlo, _⟩
  · simpa only [norm_zero] using norm_nonneg p
  · apply regularized_norm_domination C v eta delta lam hl p hdelta
    · exact effective_data_noise A C p v eta delta ‖p‖ hd le_rfl he
    · simpa only [DiscrepancyResidual.residual, DiscrepancyResidual.recoveryAt_pos C lam hl] using hlo

 theorem accepted_true_residual (A C : G →L[ℝ] V) (p x : G) (v : V)
    (eta delta tau : ℝ) (ht : 0 ≤ tau)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hx : Accepted C v eta delta tau x) :
    ‖A x-A p‖ ≤ (tau+1) * candidateNoise eta delta p := by
  have hdelta : 0 ≤ delta := operator_allowance_nonneg A C delta hd
  have hn := accepted_norm_control A C p x v eta delta tau hd he hx
  have hcand : candidateNoise eta delta x ≤ candidateNoise eta delta p :=
    candidateNoise_mono_norm eta delta hdelta hn
  have hfit := accepted_fit C v eta delta tau x hx
  have hfit' : ‖C x-v‖ ≤ tau*candidateNoise eta delta p :=
    hfit.trans (mul_le_mul_of_nonneg_left hcand ht)
  calc
    _ ≤ ‖A x-C x‖ + ‖C x-v‖ + ‖v-A p‖ := by
      have h1 := norm_sub_le_norm_sub_add_norm_sub (A x) (C x) (A p)
      have h2 := norm_sub_le_norm_sub_add_norm_sub (C x) v (A p)
      linarith [h1, h2]
    _ ≤ delta*‖x‖ + tau*candidateNoise eta delta p + eta := by
      gcongr
      · exact reverse_action_error A C delta hd x
      · simpa only [norm_sub_rev] using he
    _ ≤ delta*‖p‖ + tau*candidateNoise eta delta p + eta := by
      gcongr
    _ = (tau+1) * candidateNoise eta delta p := by
      simp only [candidateNoise]
      ring

 theorem accepted_consistent {ι : Type*} (f : Filter ι) (A : G →L[ℝ] V)
    (C : ι → G →L[ℝ] V) (v : ι → V) (eta delta : ι → ℝ)
    (x : ι → G) (p : G) (tau : ℝ)
    (hp : p ∈ A.kerᗮ) (ht : 0 ≤ tau)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i)
    (he : ∀ i, ‖A p-v i‖ ≤ eta i)
    (hx : ∀ i, Accepted (C i) (v i) (eta i) (delta i) tau (x i))
    (heta0 : Tendsto eta f (𝓝 0)) (hdelta0 : Tendsto delta f (𝓝 0)) :
    Tendsto x f (𝓝 p) := by
  apply norm_control_residual_tendsto A f x p hp
  · intro i
    exact accepted_norm_control A (C i) p (x i) (v i) (eta i) (delta i) tau
      (hd i) (he i) (hx i)
  · have hub : ∀ i, ‖A (x i)-A p‖ ≤
        (tau+1) * candidateNoise (eta i) (delta i) p := by
      intro i
      exact accepted_true_residual A (C i) p (x i) (v i) (eta i) (delta i) tau ht
        (hd i) (he i) (hx i)
    have hcand : Tendsto (fun i => candidateNoise (eta i) (delta i) p) f (𝓝 0) := by
      simpa only [candidateNoise, zero_mul, zero_add] using
        heta0.add (hdelta0.mul (tendsto_const_nhds (x := ‖p‖)))
    have hu : Tendsto (fun i => (tau+1) * candidateNoise (eta i) (delta i) p) f (𝓝 0) := by
      simpa only [mul_zero] using (tendsto_const_nhds (x := tau+1)).mul hcand
    exact squeeze_zero (fun i => norm_nonneg _) hub hu

end Komorebi.SufficientResolution.GeneralizedDiscrepancy
