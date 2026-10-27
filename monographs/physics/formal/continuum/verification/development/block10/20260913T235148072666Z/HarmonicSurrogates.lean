module
public import KomorebiPhysics.SpectralTruncation
public import KomorebiPhysics.UnboundedExamples

/-! Bounded resolvent, heat and phase multipliers for the constructed harmonic
spectrum. The resolvent has proved domain range and two inverse identities.
Heat convergence explicitly requires positive time. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace HarmonicSurrogates
open BoundedSpectral SpectralTruncation UnboundedExamples Filter
open scoped Topology BigOperators lp

/-- The positive spectral gap makes every imaginary-axis parameter safe here,
including eta=0. This is not asserted for arbitrary self-adjoint operators. -/
def denominator (η : ℝ) (n : ℕ) : ℂ := (harmonicEigenvalue n : ℂ) - (η : ℂ) * Complex.I

theorem eigenvalue_mono {m n : ℕ} (h : m ≤ n) : harmonicEigenvalue m ≤ harmonicEigenvalue n := by
  unfold harmonicEigenvalue
  exact add_le_add (by exact_mod_cast h) le_rfl

theorem eigenvalue_half_le (n : ℕ) : (1 : ℝ) / 2 ≤ harmonicEigenvalue n := by
  unfold harmonicEigenvalue
  positivity

theorem denominator_re (η : ℝ) (n : ℕ) : (denominator η n).re = harmonicEigenvalue n := by
  simp [denominator]

theorem denominator_ne_zero (η : ℝ) (n : ℕ) : denominator η n ≠ 0 := by
  intro h
  have hh := congrArg Complex.re h
  rw [denominator_re] at hh
  exact (ne_of_gt (eigenvalue_pos n)) hh

theorem denominator_norm_lower (η : ℝ) (n : ℕ) : harmonicEigenvalue n ≤ ‖denominator η n‖ := by
  simpa only [denominator_re] using Complex.re_le_norm (denominator η n)

theorem denominator_norm (η : ℝ) (n : ℕ) :
    ‖denominator η n‖ = Real.sqrt (harmonicEigenvalue n ^ 2 + η ^ 2) := by
  rw [Complex.norm_def]
  congr 1
  simp [denominator, Complex.normSq_apply, pow_two]

theorem resolvent_coefficient_bound (η : ℝ) (n : ℕ) :
    ‖(denominator η n)⁻¹‖ ≤ (harmonicEigenvalue n)⁻¹ := by
  rw [norm_inv]
  exact inv_anti₀ (eigenvalue_pos n) (denominator_norm_lower η n)

def resolventSymbol (η : ℝ) : Symbol := ofBound (fun n => (denominator η n)⁻¹) 2 (fun n => by
  apply (resolvent_coefficient_bound η n).trans
  have h := inv_anti₀ (by norm_num : (0 : ℝ) < 1 / 2) (eigenvalue_half_le n)
  norm_num at h ⊢
  exact h)

theorem resolventSymbol_apply (η : ℝ) (n : ℕ) :
    resolventSymbol η n = (denominator η n)⁻¹ := rfl

theorem resolventSymbol_norm (η : ℝ) (n : ℕ) :
    ‖resolventSymbol η n‖ = (Real.sqrt (harmonicEigenvalue n ^ 2 + η ^ 2))⁻¹ := by
  rw [resolventSymbol_apply, norm_inv, denominator_norm]

theorem resolvent_tail (η : ℝ) : Tendsto (fun n => resolventSymbol η n) atTop (𝓝 0) := by
  rw [tendsto_iff_norm_sub_tendsto_zero]
  simp only [sub_zero]
  exact squeeze_zero (fun _ => norm_nonneg _)
    (resolvent_coefficient_bound η) (tendsto_inv_atTop_zero.comp eigenvalue_tendsto)

theorem resolvent_truncation_norm (η : ℝ) (M : ℕ) :
    ‖diagonal (resolventSymbol η) - diagonal (truncate (resolventSymbol η) M)‖ =
      ⨆ k : ℕ, (Real.sqrt (harmonicEigenvalue (k + M) ^ 2 + η ^ 2))⁻¹ := by
  simpa only [anchored_zero, sub_zero, resolventSymbol_norm] using
    error_norm_eq_sup (resolventSymbol η) 0 M

theorem resolvent_truncation_tendsto (η : ℝ) :
    Tendsto (fun M => ‖diagonal (resolventSymbol η) -
      diagonal (truncate (resolventSymbol η) M)‖) atTop (𝓝 0) := by
  simpa only [anchored_zero] using anchored_norm_tendsto (resolventSymbol η) 0 (resolvent_tail η)

/-- Applying the bounded resolvent actually lands in the maximal unbounded domain. -/
theorem resolvent_mem_domain (η : ℝ) (x : Space) :
    diagonal (resolventSymbol η) x ∈ harmonic.domain := by
  change Memℓp (fun n => (harmonicEigenvalue n : ℂ) * diagonal (resolventSymbol η) x n) 2
  apply (lp.memℓp x).mono'
  intro n
  rw [diagonal_apply, resolventSymbol_apply, norm_mul, norm_mul, Complex.norm_real,
    Real.norm_eq_abs, abs_of_pos (eigenvalue_pos n)]
  have h := resolvent_coefficient_bound η n
  have h1 : harmonicEigenvalue n * ‖(denominator η n)⁻¹‖ ≤ 1 := by
    calc
      _ ≤ harmonicEigenvalue n * (harmonicEigenvalue n)⁻¹ :=
        mul_le_mul_of_nonneg_left h (le_of_lt (eigenvalue_pos n))
      _ = 1 := mul_inv_cancel₀ (ne_of_gt (eigenvalue_pos n))
  calc
    _ = (harmonicEigenvalue n * ‖(denominator η n)⁻¹‖) * ‖x n‖ := by ring
    _ ≤ 1 * ‖x n‖ := mul_le_mul_of_nonneg_right h1 (norm_nonneg _)
    _ = ‖x n‖ := one_mul _

def resolventDomain (η : ℝ) (x : Space) : harmonic.domain :=
  ⟨diagonal (resolventSymbol η) x, resolvent_mem_domain η x⟩

theorem resolvent_right_inverse (η : ℝ) (x : Space) :
    harmonic (resolventDomain η x) - ((η : ℂ) * Complex.I) •
      (resolventDomain η x : Space) = x := by
  apply lp.ext
  funext n
  change (harmonicEigenvalue n : ℂ) * ((denominator η n)⁻¹ * x n) -
    ((η : ℂ) * Complex.I) * ((denominator η n)⁻¹ * x n) = x n
  rw [← sub_mul, ← mul_assoc]
  change denominator η n * (denominator η n)⁻¹ * x n = x n
  rw [mul_inv_cancel₀ (denominator_ne_zero η n), one_mul]

theorem resolvent_left_inverse (η : ℝ) (x : harmonic.domain) :
    diagonal (resolventSymbol η) (harmonic x - ((η : ℂ) * Complex.I) • (x : Space)) = x := by
  apply lp.ext
  funext n
  change (denominator η n)⁻¹ * ((harmonicEigenvalue n : ℂ) * (x : Space) n -
    ((η : ℂ) * Complex.I) * (x : Space) n) = (x : Space) n
  rw [← sub_mul, ← mul_assoc]
  change (denominator η n)⁻¹ * denominator η n * (x : Space) n = (x : Space) n
  rw [inv_mul_cancel₀ (denominator_ne_zero η n), one_mul]

/-- Positive-time heat multiplier. Time zero is admitted only as a bounded
identity operator; decay in the spectral tail needs t>0. -/
def heatSymbol (t : ℝ) (ht : 0 ≤ t) : Symbol :=
  ofBound (fun n => (Real.exp (-t * harmonicEigenvalue n) : ℂ)) 1 (fun n => by
    rw [Complex.norm_real, Real.norm_eq_abs, abs_of_pos (Real.exp_pos _)]
    apply Real.exp_le_one_iff.mpr
    exact mul_nonpos_of_nonpos_of_nonneg (neg_nonpos.mpr ht) (le_of_lt (eigenvalue_pos n)))

theorem heatSymbol_apply (t : ℝ) (ht : 0 ≤ t) (n : ℕ) :
    heatSymbol t ht n = (Real.exp (-t * harmonicEigenvalue n) : ℂ) := rfl

theorem heatSymbol_norm (t : ℝ) (ht : 0 ≤ t) (n : ℕ) :
    ‖heatSymbol t ht n‖ = Real.exp (-t * harmonicEigenvalue n) := by
  simp only [heatSymbol_apply, Complex.norm_real, Real.norm_eq_abs, abs_of_pos (Real.exp_pos _)]

theorem heat_zero : heatSymbol 0 le_rfl = 1 := by
  apply lp.ext
  funext n
  simp [heatSymbol_apply]

theorem heat_add (s t : ℝ) (hs : 0 ≤ s) (ht : 0 ≤ t) :
    diagonal (heatSymbol (s+t) (add_nonneg hs ht)) =
      (diagonal (heatSymbol s hs)).comp (diagonal (heatSymbol t ht)) := by
  rw [← diagonal_mul]
  apply diagonal_congr
  intro n
  change (Real.exp (-(s+t) * harmonicEigenvalue n) : ℂ) =
    (Real.exp (-s * harmonicEigenvalue n) : ℂ) * (Real.exp (-t * harmonicEigenvalue n) : ℂ)
  rw [← Complex.ofReal_mul, ← Real.exp_add]
  congr 2
  ring

theorem heat_truncation_exact (t : ℝ) (ht : 0 ≤ t) (M : ℕ) :
    ‖diagonal (heatSymbol t ht) - diagonal (truncate (heatSymbol t ht) M)‖ =
      Real.exp (-t * harmonicEigenvalue M) := by
  rw [← anchored_zero]
  apply le_antisymm
  · apply error_norm_le _ _ _ (le_of_lt (Real.exp_pos _))
    intro n hn
    rw [sub_zero, heatSymbol_norm]
    exact Real.exp_le_exp.mpr (mul_le_mul_of_nonpos_left (eigenvalue_mono hn) (neg_nonpos.mpr ht))
  · simpa only [sub_zero, heatSymbol_norm] using tail_le_error_norm (heatSymbol t ht) 0 M M le_rfl

theorem heat_truncation_tendsto (t : ℝ) (ht : 0 < t) :
    Tendsto (fun M => ‖diagonal (heatSymbol t ht.le) -
      diagonal (truncate (heatSymbol t ht.le) M)‖) atTop (𝓝 0) := by
  simp only [heat_truncation_exact]
  have h : Tendsto (fun n => t * harmonicEigenvalue n) atTop atTop :=
    eigenvalue_tendsto.const_mul_atTop ht
  simpa only [neg_mul] using Real.tendsto_exp_neg_atTop_nhds_zero.comp h

/-- Actual complex phase coefficients, not a postulated abstract unitary. -/
def phaseSymbol (eig : ℕ → ℝ) (t : ℝ) : Symbol :=
  ofBound (fun n => Complex.exp ((-t * eig n : ℝ) * Complex.I)) 1 (fun n => by
    exact le_of_eq (Complex.norm_exp_ofReal_mul_I _))

theorem phaseSymbol_apply (eig : ℕ → ℝ) (t : ℝ) (n : ℕ) :
    phaseSymbol eig t n = Complex.exp ((-t * eig n : ℝ) * Complex.I) := rfl

theorem phaseSymbol_norm (eig : ℕ → ℝ) (t : ℝ) (n : ℕ) :
    ‖phaseSymbol eig t n‖ = 1 := Complex.norm_exp_ofReal_mul_I _

theorem phase_zero (eig : ℕ → ℝ) : diagonal (phaseSymbol eig 0) = ContinuousLinearMap.id ℂ Space := by
  rw [← diagonal_one]
  apply diagonal_congr
  intro n
  simp [phaseSymbol_apply]

theorem phase_add (eig : ℕ → ℝ) (s t : ℝ) :
    diagonal (phaseSymbol eig (s+t)) =
      (diagonal (phaseSymbol eig s)).comp (diagonal (phaseSymbol eig t)) := by
  rw [← diagonal_mul]
  apply diagonal_congr
  intro n
  change Complex.exp ((-((s+t)) * eig n : ℝ) * Complex.I) =
    Complex.exp ((-s * eig n : ℝ) * Complex.I) * Complex.exp ((-t * eig n : ℝ) * Complex.I)
  rw [← Complex.exp_add]
  congr 1
  push_cast
  ring

theorem phase_inverse (eig : ℕ → ℝ) (t : ℝ) :
    (diagonal (phaseSymbol eig (-t))).comp (diagonal (phaseSymbol eig t)) =
      ContinuousLinearMap.id ℂ Space := by
  rw [← phase_add, neg_add_cancel, phase_zero]

theorem phase_preserves_norm (eig : ℕ → ℝ) (t : ℝ) (x : Space) :
    ‖diagonal (phaseSymbol eig t) x‖ = ‖x‖ := by
  apply le_antisymm
  · apply lp.norm_mono (by norm_num : (2 : ENNReal) ≠ 0)
    intro n
    simp only [diagonal_apply, norm_mul, phaseSymbol_norm, one_mul, le_refl]
  · apply lp.norm_mono (by norm_num : (2 : ENNReal) ≠ 0)
    intro n
    simp only [diagonal_apply, norm_mul, phaseSymbol_norm, one_mul, le_refl]

theorem phase_truncation_exact (eig : ℕ → ℝ) (t : ℝ) (M : ℕ) :
    ‖diagonal (phaseSymbol eig t) - diagonal (truncate (phaseSymbol eig t) M)‖ = 1 :=
  unit_modulus_error _ (phaseSymbol_norm eig t) M

theorem phase_truncation_not_norm (eig : ℕ → ℝ) (t : ℝ) :
    ¬ Tendsto (fun M => ‖diagonal (phaseSymbol eig t) -
      diagonal (truncate (phaseSymbol eig t) M)‖) atTop (𝓝 0) :=
  unit_modulus_not_norm _ (phaseSymbol_norm eig t)

theorem phase_truncation_strong (eig : ℕ → ℝ) (t : ℝ) (x : Space) :
    Tendsto (fun M => diagonal (truncate (phaseSymbol eig t) M) x) atTop
      (𝓝 (diagonal (phaseSymbol eig t) x)) := truncate_strong _ x

theorem cutoff_eq_old_partial (M : ℕ) (x : Space) :
    cutoff M x = DiagonalDomain.coordinateAtlas.partialSum (Finset.range M) x := by
  simpa only [diagonal_one, ContinuousLinearMap.id_apply, StrongAtlas.partialSum,
    DiagonalDomain.coordinateAtlas, DiagonalDomain.coordinate_apply] using truncate_vector_sum 1 M x

end HarmonicSurrogates
end KomorebiPhysics
