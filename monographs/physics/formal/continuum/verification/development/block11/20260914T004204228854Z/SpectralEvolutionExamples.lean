module
public import KomorebiPhysics.SpectralTimeApproximation
public import Mathlib.Analysis.PSeries

/-! Exact infinite-dimensional controls: a continuous nowhere-differentiable
orbit outside the maximal domain, operator-norm discontinuity in time, and
nonzero evolution of a normalized coherent finite-support state. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace SpectralEvolutionExamples
open Filter BoundedSpectral HarmonicSurrogates SpectralEvolution UnboundedExamples
open scoped Topology BigOperators lp

/-- A square-summable harmonic reciprocal vector with a nonsummable H-image. -/
def roughState : Space :=
  ⟨fun n => ((harmonicEigenvalue n)⁻¹ : ℝ), by
    rw [memℓp_gen_iff (by norm_num : 0 < (2 : ENNReal).toReal)]
    have h := (Real.summable_one_div_nat_add_rpow (1/2) 2).mpr (by norm_num)
    simpa only [ENNReal.toReal_ofNat, Real.rpow_two, harmonicEigenvalue,
      Complex.norm_real, Real.norm_eq_abs, abs_inv, inv_pow, one_div] using h⟩

theorem roughState_apply (n : ℕ) : roughState n = ((harmonicEigenvalue n)⁻¹ : ℝ) := rfl

theorem roughState_weighted (n : ℕ) : (harmonicEigenvalue n : ℂ) * roughState n = 1 := by
  rw [roughState_apply, ← Complex.ofReal_mul, mul_inv_cancel₀ (ne_of_gt (eigenvalue_pos n)), Complex.ofReal_one]

theorem roughState_not_domain : roughState ∉ DiagonalDomain.domain harmonicEigenvalue := by
  intro h
  change Memℓp (fun n => (harmonicEigenvalue n : ℂ) * roughState n) 2 at h
  rw [memℓp_gen_iff (by norm_num)] at h
  simp only [roughState_weighted, norm_one, Real.one_rpow] at h
  simpa only [summable_const_iff] using h

theorem roughState_nonzero : roughState ≠ 0 := by
  intro h
  have hz := congrArg (fun x : Space => x 0) h
  norm_num [roughState_apply, harmonicEigenvalue] at hz

theorem rough_orbit_continuous : Continuous (fun t => evolution harmonicEigenvalue t roughState) :=
  continuous_orbit harmonicEigenvalue roughState

theorem rough_orbit_not_differentiable (t : ℝ) :
    ¬ DifferentiableAt ℝ (fun s => evolution harmonicEigenvalue s roughState) t :=
  not_differentiable_outside harmonicEigenvalue roughState_not_domain t

/-- Arbitrarily small times carry one spectral coordinate through half a turn. -/
def halfTurnTime (n : ℕ) : ℝ := Real.pi / harmonicEigenvalue n

theorem halfTurnTime_tendsto : Tendsto halfTurnTime atTop (𝓝 0) := by
  simpa only [halfTurnTime, div_eq_mul_inv, mul_zero] using
    (tendsto_inv_atTop_zero.comp eigenvalue_tendsto).const_mul Real.pi

theorem phase_halfTurn (n : ℕ) : phaseSymbol harmonicEigenvalue (halfTurnTime n) n = -1 := by
  rw [phaseSymbol_apply]
  have he : -(halfTurnTime n) * harmonicEigenvalue n = -Real.pi := by
    rw [halfTurnTime, neg_mul, div_mul_cancel₀ _ (ne_of_gt (eigenvalue_pos n))]
  rw [he, Complex.ofReal_neg, neg_mul, Complex.exp_neg_pi_mul_I]

/-- Universal upper bound for the norm-distance of a phase operator from I. -/
theorem operator_distance_le_two (eig : ℕ → ℝ) (t : ℝ) :
    ‖evolution eig t - ContinuousLinearMap.id ℂ Space‖ ≤ 2 := by
  rw [evolution, ← diagonal_one, diagonal_norm_sub]
  apply lp.norm_le_of_forall_le (by norm_num)
  intro n
  change ‖phaseSymbol eig t n - 1‖ ≤ 2
  calc
    _ ≤ ‖phaseSymbol eig t n‖ + ‖(1 : ℂ)‖ := norm_sub_le _ _
    _ = 2 := by rw [phaseSymbol_norm, norm_one]; norm_num

/-- Exact norm error two at times tending to zero. -/
theorem halfTurn_operator_distance (n : ℕ) :
    ‖evolution harmonicEigenvalue (halfTurnTime n) - ContinuousLinearMap.id ℂ Space‖ = 2 := by
  apply le_antisymm (operator_distance_le_two _ _)
  have h := symbol_le_norm (phaseSymbol harmonicEigenvalue (halfTurnTime n) - 1) n
  simpa only [lp.coeFn_sub, Pi.sub_apply, lp.coeFn_one, Pi.one_apply,
    phase_halfTurn, diagonal_sub, diagonal_one, ← evolution] using h

/-- Strong time continuity does not imply continuity in operator norm. -/
theorem not_operator_norm_continuous :
    ¬ ContinuousAt (fun t => evolution harmonicEigenvalue t) 0 := by
  intro h
  have ht := ((h.tendsto.comp halfTurnTime_tendsto).sub_const
    (ContinuousLinearMap.id ℂ Space)).norm
  have hz : evolution harmonicEigenvalue 0 = ContinuousLinearMap.id ℂ Space := phase_zero _
  simp only [hz, sub_self, norm_zero, halfTurn_operator_distance] at ht
  have he : (2 : ℝ) = 0 := tendsto_nhds_unique tendsto_const_nhds ht
  norm_num at he

/-- A normalized two-mode state embedded in the genuine infinite space. -/
def coherentState : (DiagonalDomain.operator harmonicEigenvalue).domain :=
  DiagonalDomain.single harmonicEigenvalue 0 (3/5) +
    DiagonalDomain.single harmonicEigenvalue 1 ((4/5) * Complex.I)

theorem coherentState_coe : (coherentState : Space) =
    lp.single 2 0 (3/5) + lp.single 2 1 ((4/5) * Complex.I) := rfl

theorem coherentState_norm : ‖(coherentState : Space)‖ = 1 := by
  rw [coherentState_coe]
  have hi : inner ℂ (lp.single 2 0 (3/5) : Space) (lp.single 2 1 ((4/5) * Complex.I)) = 0 := by
    simp
  have hn := norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero _ _ hi
  simp only [lp.norm_single (by norm_num : (0 : ENNReal) < 2), norm_mul, Complex.norm_I, mul_one] at hn
  norm_num at hn
  nlinarith [norm_nonneg ((lp.single 2 0 (3/5) : Space) + lp.single 2 1 ((4/5) * Complex.I))]

theorem coherentState_zero : (coherentState : Space) 0 = 3/5 := by
  simp [coherentState_coe]

theorem coherentState_one : (coherentState : Space) 1 = (4/5) * Complex.I := by
  simp [coherentState_coe]

theorem coherent_orbit_normalized (t : ℝ) :
    ‖evolution harmonicEigenvalue t (coherentState : Space)‖ = 1 := by
  rw [norm_preserved, coherentState_norm]

theorem coherent_orbit_hasDerivAt (t : ℝ) :
    HasDerivAt (fun s => evolution harmonicEigenvalue s (coherentState : Space))
      ((-Complex.I) • DiagonalDomain.operator harmonicEigenvalue
        (domainEvolution harmonicEigenvalue t coherentState)) t :=
  orbit_hasDerivAt harmonicEigenvalue coherentState t

/-- Coherent coordinate amplitude, not a spectral population. -/
def coherentAmplitude (t : ℝ) : ℂ :=
  evolution harmonicEigenvalue t (coherentState : Space) 0 +
    evolution harmonicEigenvalue t (coherentState : Space) 1

theorem coherentAmplitude_zero : coherentAmplitude 0 = (3/5) + (4/5) * Complex.I := by
  simp only [coherentAmplitude, evolution_zero, coherentState_zero, coherentState_one]

theorem coherentAmplitude_hasDerivAt :
    HasDerivAt coherentAmplitude ((6/5) - (3/10) * Complex.I) 0 := by
  have h := (coordinate_hasDerivAt harmonicEigenvalue (coherentState : Space) 0 0).add
    (coordinate_hasDerivAt harmonicEigenvalue (coherentState : Space) 0 1)
  convert h using 1
  · rfl
  · simp only [evolution_zero, coherentState_zero, coherentState_one, harmonicEigenvalue]
    norm_num
    ring_nf
    simp

/-- An exact nonzero rate of the coherent quadratic observable. -/
theorem coherent_observable_hasDerivAt :
    HasDerivAt (fun t => ‖coherentAmplitude t‖ ^ 2 / 2) (12/25) 0 := by
  have h := (KomorebiPhysics.hasDerivAt_norm_sq coherentAmplitude_hasDerivAt).div_const 2
  convert h using 1
  rw [coherentAmplitude_zero]
  simp only [RCLike.inner_apply, map_add, map_mul, map_div₀, map_ofNat, Complex.conj_I]
  norm_num [Complex.mul_re, Complex.mul_im]

theorem coherent_observable_rate_nonzero :
    deriv (fun t => ‖coherentAmplitude t‖ ^ 2 / 2) 0 ≠ 0 := by
  rw [coherent_observable_hasDerivAt.deriv]
  norm_num

end SpectralEvolutionExamples
end KomorebiPhysics
