module
public import KomorebiPhysics.SpectralTimeContinuity

/-! Actual l2 Schrödinger differentiation by dominated slopes on the maximal
weighted domain, and the converse characterization of differentiable states. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace SpectralEvolution
open Filter BoundedSpectral HarmonicSurrogates
open scoped Topology BigOperators lp
variable (eig : ℕ → ℝ)

/-- Pointwise difference quotients are bounded by the square-summable generator
image. The bound is uniform in time and coordinate. -/
theorem slope_coordinate_bound (x : (DiagonalDomain.operator eig).domain)
    (s t : ℝ) (n : ℕ) :
    ‖slope (fun u => evolution eig u (x : Space)) t s n‖ ≤
      ‖DiagonalDomain.operator eig x n‖ := by
  by_cases h : s = t
  · subst s
    simp only [slope_same, lp.coeFn_zero, Pi.zero_apply, norm_zero]
    exact norm_nonneg _
  · have hab : |s-t| ≠ 0 := abs_ne_zero.mpr (sub_ne_zero.mpr h)
    simp only [slope_def_module, lp.coeFn_smul, lp.coeFn_sub, Pi.smul_apply,
      Pi.sub_apply, norm_smul, Real.norm_eq_abs, abs_inv]
    calc
      _ ≤ |s-t|⁻¹ * (|s-t| * (|eig n| * ‖(x : Space) n‖)) :=
        mul_le_mul_of_nonneg_left (coordinate_increment_bound eig s t x n)
          (inv_nonneg.mpr (abs_nonneg _))
      _ = ‖DiagonalDomain.operator eig x n‖ := by
        rw [← mul_assoc, inv_mul_cancel₀ hab, one_mul, DiagonalDomain.operator_apply,
          norm_mul, Complex.norm_real, Real.norm_eq_abs]

/-- The desired velocity has exactly the same coordinate norm as H x. -/
theorem velocity_coordinate_norm (x : (DiagonalDomain.operator eig).domain) (t : ℝ) (n : ℕ) :
    ‖((-Complex.I) • DiagonalDomain.operator eig (domainEvolution eig t x)) n‖ =
      ‖DiagonalDomain.operator eig x n‖ := by
  rw [operator_commutes]
  simp only [lp.coeFn_smul, Pi.smul_apply, norm_smul, norm_neg, Complex.norm_I,
    one_mul, coordinate_norm]

/-- The actual ambient l2 derivative. No trajectory or scalar balance law
is supplied as a hypothesis. -/
theorem orbit_hasDerivAt (x : (DiagonalDomain.operator eig).domain) (t : ℝ) :
    HasDerivAt (fun s => evolution eig s (x : Space))
      ((-Complex.I) • DiagonalDomain.operator eig (domainEvolution eig t x)) t := by
  let v : Space := (2 : ℂ) • DiagonalDomain.operator eig x
  apply L2DominatedLimits.hasDerivAt_of_dominated_slope (bound := fun n => ‖v n‖)
  · simpa using (lp.memℓp v).summable (by norm_num : 0 < (2 : ENNReal).toReal)
  · intro n
    simpa only [lp.coeFn_smul, Pi.smul_apply, smul_eq_mul, DiagonalDomain.operator_apply,
      domainEvolution_coe, mul_assoc] using coordinate_hasDerivAt eig (x : Space) t n
  · apply Filter.Eventually.of_forall
    intro s n
    calc
      _ ≤ ‖slope (fun u => evolution eig u (x : Space)) t s n‖ +
          ‖((-Complex.I) • DiagonalDomain.operator eig (domainEvolution eig t x)) n‖ := norm_sub_le _ _
      _ ≤ ‖DiagonalDomain.operator eig x n‖ + ‖DiagonalDomain.operator eig x n‖ :=
        add_le_add (slope_coordinate_bound eig x s t n) (le_of_eq (velocity_coordinate_norm eig x t n))
      _ = ‖v n‖ := by
        simp only [v, lp.coeFn_smul, Pi.smul_apply, norm_smul]
        norm_num
        ring

theorem orbit_hasDerivAt_zero (x : (DiagonalDomain.operator eig).domain) :
    HasDerivAt (fun s => evolution eig s (x : Space)) ((-Complex.I) • DiagonalDomain.operator eig x) 0 := by
  simpa only [domainEvolution_zero] using orbit_hasDerivAt eig x 0

theorem differentiable_orbit (x : (DiagonalDomain.operator eig).domain) :
    Differentiable ℝ (fun s => evolution eig s (x : Space)) :=
  fun t => (orbit_hasDerivAt eig x t).differentiableAt

theorem deriv_orbit (x : (DiagonalDomain.operator eig).domain) (t : ℝ) :
    deriv (fun s => evolution eig s (x : Space)) t =
      (-Complex.I) • DiagonalDomain.operator eig (domainEvolution eig t x) :=
  (orbit_hasDerivAt eig x t).deriv

theorem norm_deriv (x : (DiagonalDomain.operator eig).domain) (t : ℝ) :
    ‖deriv (fun s => evolution eig s (x : Space)) t‖ = ‖DiagonalDomain.operator eig x‖ := by
  rw [deriv_orbit, norm_smul, norm_neg, Complex.norm_I, one_mul,
    operator_commutes, norm_preserved]

/-- Continuous velocity on the ambient Hilbert space; no H^2 assumption. -/
theorem continuous_velocity (x : (DiagonalDomain.operator eig).domain) :
    Continuous (fun t => deriv (fun s => evolution eig s (x : Space)) t) := by
  simp only [deriv_orbit, operator_commutes]
  exact (continuous_orbit eig (DiagonalDomain.operator eig x)).const_smul (-Complex.I)

/-- Quantitative time regularity for each domain state. The constant depends
on H x, not on a nonexistent bounded operator norm for H. -/
theorem domain_increment_bound (x : (DiagonalDomain.operator eig).domain) (s t : ℝ) :
    ‖evolution eig s (x : Space) - evolution eig t (x : Space)‖ ≤
      |s-t| * ‖DiagonalDomain.operator eig x‖ := by
  have h : ‖evolution eig s (x : Space) - evolution eig t (x : Space)‖ ≤
      ‖(s-t) • DiagonalDomain.operator eig x‖ := by
    apply lp.norm_mono (by norm_num : (2 : ENNReal) ≠ 0)
    intro n
    simpa only [lp.coeFn_sub, Pi.sub_apply, lp.coeFn_smul, Pi.smul_apply,
      norm_smul, Real.norm_eq_abs, DiagonalDomain.operator_apply, norm_mul, Complex.norm_real]
      using coordinate_increment_bound eig s t x n
  simpa only [norm_smul, Real.norm_eq_abs] using h

/-- An ambient derivative forces its actual coordinate values. -/
theorem derivative_coordinates {x y : Space} {t : ℝ}
    (h : HasDerivAt (fun s => evolution eig s x) y t) (n : ℕ) :
    y n = (-Complex.I) * (eig n : ℂ) * evolution eig t x n := by
  have he := ((lp.evalCLM ℂ (fun _ : ℕ => ℂ) 2 n).restrictScalars ℝ).hasFDerivAt.comp_hasDerivAt t h
  exact he.unique (coordinate_hasDerivAt eig x t n)

/-- Converse: existence of an l2 derivative forces maximal-domain membership. -/
theorem mem_domain_of_hasDerivAt {x y : Space} {t : ℝ}
    (h : HasDerivAt (fun s => evolution eig s x) y t) : x ∈ DiagonalDomain.domain eig := by
  apply (domain_iff eig t x).mp
  change Memℓp (fun n => (eig n : ℂ) * evolution eig t x n) 2
  convert lp.memℓp (Complex.I • y) using 1
  funext n
  simp only [lp.coeFn_smul, Pi.smul_apply, smul_eq_mul, derivative_coordinates eig h n]
  simp [← mul_assoc]

/-- Sharp domain characterization: continuity is universal, differentiation is not. -/
theorem differentiableAt_iff_mem_domain (x : Space) (t : ℝ) :
    DifferentiableAt ℝ (fun s => evolution eig s x) t ↔ x ∈ DiagonalDomain.domain eig := by
  constructor
  · intro h
    exact mem_domain_of_hasDerivAt eig h.hasDerivAt
  · intro hx
    exact (orbit_hasDerivAt eig ⟨x, hx⟩ t).differentiableAt

theorem not_differentiable_outside {x : Space} (hx : x ∉ DiagonalDomain.domain eig) (t : ℝ) :
    ¬ DifferentiableAt ℝ (fun s => evolution eig s x) t := by
  exact fun h => hx ((differentiableAt_iff_mem_domain eig x t).mp h)

end SpectralEvolution
end KomorebiPhysics
