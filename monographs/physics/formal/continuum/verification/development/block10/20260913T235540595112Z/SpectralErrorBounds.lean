module
public import KomorebiPhysics.AnchoredSurrogates

/-! Quantified endpoint errors and hypothesis-sensitive checks. Every cutoff
is arbitrary; these are not finite numerical benchmark assertions. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace SpectralErrorBounds
open BoundedSpectral SpectralTruncation HarmonicSurrogates AnchoredSurrogates UnboundedExamples Filter
open scoped Topology BigOperators lp

theorem denominator_norm_mono (η : ℝ) {m n : ℕ} (h : m ≤ n) :
    ‖denominator η m‖ ≤ ‖denominator η n‖ := by
  rw [denominator_norm, denominator_norm]
  apply Real.sqrt_le_sqrt
  have hm := eigenvalue_pos m
  have hn := eigenvalue_mono h
  nlinarith

/-- The harmonic resolvent tail supremum is attained at the first omitted index. -/
theorem resolvent_error_endpoint (η : ℝ) (M : ℕ) :
    ‖diagonal (resolventSymbol η) - diagonal (truncate (resolventSymbol η) M)‖ =
      (Real.sqrt (harmonicEigenvalue M ^ 2 + η ^ 2))⁻¹ := by
  rw [← anchored_zero]
  apply le_antisymm
  · apply error_norm_le _ _ _ (by positivity)
    intro n hn
    rw [sub_zero, resolventSymbol_apply, norm_inv, ← denominator_norm]
    exact inv_anti₀ (norm_pos_iff.mpr (denominator_ne_zero η M)) (denominator_norm_mono η hn)
  · simpa only [sub_zero, resolventSymbol_norm] using
      tail_le_error_norm (resolventSymbol η) 0 M M le_rfl

/-- Uniform in eta, with an explicit spectral-gap rate. -/
theorem resolvent_error_bound (η : ℝ) (M : ℕ) :
    ‖diagonal (resolventSymbol η) - diagonal (truncate (resolventSymbol η) M)‖ ≤
      (harmonicEigenvalue M)⁻¹ := by
  rw [resolvent_error_endpoint, ← denominator_norm, ← norm_inv]
  exact resolvent_coefficient_bound η M

theorem bounded_coefficient_mono {m n : ℕ} (h : m ≤ n) :
    harmonicEigenvalue m / root m ≤ harmonicEigenvalue n / root n := by
  rw [bounded_normalized, bounded_normalized]
  apply inv_anti₀ (Real.sqrt_pos.mpr (by positivity))
  apply Real.sqrt_le_sqrt
  have hi := inv_anti₀ (eigenvalue_pos m) (eigenvalue_mono h)
  have hm := inv_pos.mpr (eigenvalue_pos m)
  have hn := inv_pos.mpr (eigenvalue_pos n)
  nlinarith

theorem bounded_error_endpoint (M : ℕ) :
    ‖diagonal boundedSymbol - diagonal (anchored boundedSymbol 1 M)‖ =
      1 - harmonicEigenvalue M / root M := by
  have hb : ∀ n, harmonicEigenvalue n / root n ≤ 1 := fun n =>
    (div_le_one (root_pos n)).mpr (root_ge_eigenvalue n)
  have he : ∀ n, ‖boundedSymbol n - 1‖ = 1 - harmonicEigenvalue n / root n := by
    intro n
    rw [boundedSymbol_apply, ← Complex.ofReal_one, ← Complex.ofReal_sub,
      Complex.norm_real, Real.norm_eq_abs, abs_of_nonpos (sub_nonpos.mpr (hb n))]
    ring
  apply le_antisymm
  · apply error_norm_le _ _ _ (sub_nonneg.mpr (hb M))
    intro n hn
    rw [he]
    linarith [bounded_coefficient_mono hn]
  · rw [← he]
    exact tail_le_error_norm boundedSymbol 1 M M le_rfl

/-- Rationalized exact error: no cancellation of nearly equal floating values
is used in this mathematical identity. -/
theorem bounded_error_rationalized (M : ℕ) :
    ‖diagonal boundedSymbol - diagonal (anchored boundedSymbol 1 M)‖ =
      (root M * (root M + harmonicEigenvalue M))⁻¹ := by
  rw [bounded_error_endpoint]
  have hs := root_sq M
  have hp := root_pos M
  have he := eigenvalue_pos M
  field_simp
  nlinarith

/-- An explicit quadratic tail bound for the bounded transform. -/
theorem bounded_error_bound (M : ℕ) :
    ‖diagonal boundedSymbol - diagonal (anchored boundedSymbol 1 M)‖ ≤
      ((harmonicEigenvalue M)^2)⁻¹ := by
  rw [bounded_error_rationalized]
  apply inv_anti₀ (sq_pos_of_pos (eigenvalue_pos M))
  have he := eigenvalue_pos M
  have hr := root_ge_eigenvalue M
  nlinarith

theorem cayley_error_endpoint (M : ℕ) :
    ‖diagonal cayleySymbol - diagonal (anchored cayleySymbol 1 M)‖ = 2 / root M := by
  have he : ‖denominator (-1) M‖ = root M := by
    rw [denominator_norm, root]
    congr 1
    norm_num
    ring
  apply le_antisymm
  · apply error_norm_le _ _ _ (by positivity [root_pos M])
    intro n hn
    rw [cayley_difference_norm, ← he]
    exact div_le_div_of_nonneg_left (by norm_num) (norm_pos_iff.mpr (denominator_ne_zero (-1) M))
      (denominator_norm_mono (-1) hn)
  · rw [← he, ← cayley_difference_norm]
    exact tail_le_error_norm cayleySymbol 1 M M le_rfl

theorem cayley_error_bound (M : ℕ) :
    ‖diagonal cayleySymbol - diagonal (anchored cayleySymbol 1 M)‖ ≤
      2 * (harmonicEigenvalue M)⁻¹ := by
  rw [cayley_error_endpoint, div_eq_mul_inv]
  exact mul_le_mul_of_nonneg_left (inv_anti₀ (eigenvalue_pos M) (root_ge_eigenvalue M)) (by norm_num)

/-- A correct scalar spectral limit rejects every wrong constant tail anchor. -/
theorem wrong_anchor_not_norm (a : Symbol) (c d : ℂ)
    (ha : Tendsto (fun n => a n) atTop (𝓝 d)) (hcd : c ≠ d) :
    ¬ Tendsto (fun M => ‖diagonal a - diagonal (anchored a c M)‖) atTop (𝓝 0) := by
  intro h
  exact hcd (tendsto_nhds_unique ((anchored_norm_iff a c).mp h) ha)

theorem bounded_wrong_anchor (c : ℂ) (hc : c ≠ 1) :
    ¬ Tendsto (fun M => ‖diagonal boundedSymbol - diagonal (anchored boundedSymbol c M)‖)
      atTop (𝓝 0) := wrong_anchor_not_norm boundedSymbol c 1 bounded_tail hc

theorem cayley_wrong_anchor (c : ℂ) (hc : c ≠ 1) :
    ¬ Tendsto (fun M => ‖diagonal cayleySymbol - diagonal (anchored cayleySymbol c M)‖)
      atTop (𝓝 0) := wrong_anchor_not_norm cayleySymbol c 1 cayley_tail hc

theorem heat_zero_error (M : ℕ) :
    ‖diagonal (heatSymbol 0 le_rfl) - diagonal (truncate (heatSymbol 0 le_rfl) M)‖ = 1 := by
  rw [heat_truncation_exact]
  simp

theorem heat_zero_not_norm :
    ¬ Tendsto (fun M => ‖diagonal (heatSymbol 0 le_rfl) -
      diagonal (truncate (heatSymbol 0 le_rfl) M)‖) atTop (𝓝 0) := by
  intro h
  have hz : Tendsto (fun _ : ℕ => (1 : ℝ)) atTop (𝓝 0) := by simpa only [heat_zero_error] using h
  have : (1 : ℝ) = 0 := tendsto_nhds_unique tendsto_const_nhds hz
  norm_num at this

/-- Negative heat time yields an unbounded sequence of spectral coefficients. -/
theorem backward_heat_unbounded (t : ℝ) (ht : t < 0) :
    ¬ ∃ C : ℝ, ∀ n, Real.exp (-t * harmonicEigenvalue n) ≤ C := by
  rintro ⟨C, hC⟩
  have h : Tendsto (fun n => Real.exp (-t * harmonicEigenvalue n)) atTop atTop :=
    Real.tendsto_exp_atTop.comp (eigenvalue_tendsto.const_mul_atTop (neg_pos.mpr ht))
  obtain ⟨n, hn⟩ := (h.eventually (eventually_gt_atTop C)).exists
  exact (not_lt_of_ge (hC n)) hn

/-- Exact nonzero cutoff example with no floating-point approximation. -/
theorem zero_parameter_resolvent_error (M : ℕ) :
    ‖diagonal (resolventSymbol 0) - diagonal (truncate (resolventSymbol 0) M)‖ =
      (harmonicEigenvalue M)⁻¹ := by
  rw [resolvent_error_endpoint]
  simp only [zero_pow (by decide : 2 ≠ 0), add_zero, Real.sqrt_sq (eigenvalue_pos M).le]

theorem resolvent_error_at_ten :
    ‖diagonal (resolventSymbol 0) - diagonal (truncate (resolventSymbol 0) 10)‖ = 2/21 := by
  rw [zero_parameter_resolvent_error]
  norm_num [harmonicEigenvalue]

theorem phase_tail_eigenvector (eig : ℕ → ℝ) (t : ℝ) (M n : ℕ) (hn : M ≤ n) :
    (diagonal (phaseSymbol eig t) - diagonal (truncate (phaseSymbol eig t) M))
      (lp.single 2 n (1 : ℂ)) = lp.single 2 n (phaseSymbol eig t n) := by
  rw [← diagonal_sub, diagonal_single]
  simp only [lp.coeFn_sub, Pi.sub_apply, truncate_apply, ite_eq_right (Nat.not_lt.mpr hn), sub_zero, mul_one]

theorem identity_cutoff_strong : ∀ x : Space,
    Tendsto (fun M => cutoff M x) atTop (𝓝 x) := cutoff_strong

theorem identity_cutoff_norm_error (M : ℕ) :
    ‖ContinuousLinearMap.id ℂ Space - cutoff M‖ = 1 := by
  simpa only [diagonal_one, cutoff] using unit_modulus_error (1 : Symbol) (fun _ => by simp) M

end SpectralErrorBounds
end KomorebiPhysics
