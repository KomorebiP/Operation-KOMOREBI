module
public import KomorebiPhysics.HarmonicSurrogates

/-! Bounded and Cayley transforms with the correct nonzero tail anchors.
These are actual infinite-dimensional diagonal operators. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace AnchoredSurrogates
open BoundedSpectral SpectralTruncation HarmonicSurrogates UnboundedExamples Filter
open scoped Topology BigOperators lp

def root (n : ℕ) : ℝ := Real.sqrt (1 + harmonicEigenvalue n ^ 2)

theorem root_pos (n : ℕ) : 0 < root n := Real.sqrt_pos.mpr (by positivity)

theorem root_sq (n : ℕ) : root n ^ 2 = 1 + harmonicEigenvalue n ^ 2 :=
  Real.sq_sqrt (by positivity)

theorem root_ge_eigenvalue (n : ℕ) : harmonicEigenvalue n ≤ root n := by
  have h := root_sq n
  have hp := root_pos n
  nlinarith

theorem root_ge_one (n : ℕ) : 1 ≤ root n := by
  have h := root_sq n
  have hp := root_pos n
  nlinarith [sq_nonneg (harmonicEigenvalue n)]

def boundedSymbol : Symbol := ofBound (fun n => (harmonicEigenvalue n / root n : ℝ)) 1 (fun n => by
  rw [Complex.norm_real, Real.norm_eq_abs, abs_of_pos (div_pos (eigenvalue_pos n) (root_pos n))]
  exact (div_le_one (root_pos n)).mpr (root_ge_eigenvalue n))

theorem boundedSymbol_apply (n : ℕ) : boundedSymbol n = (harmonicEigenvalue n / root n : ℝ) := rfl

theorem boundedSymbol_norm_le (n : ℕ) : ‖boundedSymbol n‖ ≤ 1 := by
  rw [boundedSymbol_apply, Complex.norm_real, Real.norm_eq_abs,
    abs_of_pos (div_pos (eigenvalue_pos n) (root_pos n))]
  exact (div_le_one (root_pos n)).mpr (root_ge_eigenvalue n)

/-- Normalize at infinity without ever dividing by a zero eigenvalue. -/
theorem root_normalized (n : ℕ) :
    root n = harmonicEigenvalue n * Real.sqrt (1 + (harmonicEigenvalue n)⁻¹ ^ 2) := by
  have heig := eigenvalue_pos n
  have heig0 := ne_of_gt heig
  have hs := Real.sq_sqrt (by positivity : 0 ≤ 1 + (harmonicEigenvalue n)⁻¹ ^ 2)
  have heq : (harmonicEigenvalue n * Real.sqrt (1 + (harmonicEigenvalue n)⁻¹ ^ 2)) ^ 2 =
      root n ^ 2 := by
    rw [mul_pow, hs, root_sq]
    field_simp [heig0]
    ring
  have hpos : 0 ≤ harmonicEigenvalue n * Real.sqrt (1 + (harmonicEigenvalue n)⁻¹ ^ 2) := by positivity
  nlinarith [root_pos n]

theorem bounded_normalized (n : ℕ) :
    harmonicEigenvalue n / root n = (Real.sqrt (1 + (harmonicEigenvalue n)⁻¹ ^ 2))⁻¹ := by
  rw [root_normalized]
  field_simp [ne_of_gt (eigenvalue_pos n)]

theorem bounded_tail : Tendsto (fun n => boundedSymbol n) atTop (𝓝 1) := by
  have hi : Tendsto (fun n => (harmonicEigenvalue n)⁻¹) atTop (𝓝 (0 : ℝ)) :=
    tendsto_inv_atTop_zero.comp eigenvalue_tendsto
  have hs := (tendsto_const_nhds.add (hi.pow 2) :
    Tendsto (fun n => 1 + (harmonicEigenvalue n)⁻¹ ^ 2) atTop (𝓝 (1 + 0 ^ 2 : ℝ))).sqrt
  have hh := hs.inv₀ (by norm_num : Real.sqrt (1 + 0 ^ 2 : ℝ) ≠ 0)
  have hc := hh.ofReal
  simpa only [boundedSymbol_apply, bounded_normalized, zero_pow (by decide : 2 ≠ 0),
    add_zero, Real.sqrt_one, inv_one, Complex.ofReal_one] using hc

theorem bounded_anchored_exact (M : ℕ) :
    ‖diagonal boundedSymbol - diagonal (anchored boundedSymbol 1 M)‖ =
      ⨆ k : ℕ, |harmonicEigenvalue (k+M) / root (k+M) - 1| := by
  rw [error_norm_eq_sup]
  congr 1
  funext k
  rw [boundedSymbol_apply, ← Complex.ofReal_one, ← Complex.ofReal_sub, Complex.norm_real,
    Real.norm_eq_abs]

theorem bounded_anchored_tendsto :
    Tendsto (fun M => ‖diagonal boundedSymbol - diagonal (anchored boundedSymbol 1 M)‖)
      atTop (𝓝 0) := anchored_norm_tendsto boundedSymbol 1 bounded_tail

/-- Zero padding is still maximally wrong in operator norm for this symbol. -/
theorem bounded_zero_padded_exact (M : ℕ) :
    ‖diagonal boundedSymbol - diagonal (truncate boundedSymbol M)‖ = 1 := by
  rw [← anchored_zero]
  apply le_antisymm
  · apply error_norm_le _ _ _ (by norm_num)
    intro n _
    simpa only [sub_zero] using boundedSymbol_norm_le n
  · have hn := bounded_tail.norm
    simp only [norm_one] at hn
    apply le_of_tendsto hn
    filter_upwards [eventually_ge_atTop M] with n hn
    simpa only [sub_zero] using tail_le_error_norm boundedSymbol 0 M n hn

/-- The bounded square-root regularizer, with genuine domain range below. -/
def regularizerSymbol : Symbol := ofBound (fun n => ((root n)⁻¹ : ℝ)) 1 (fun n => by
  rw [Complex.norm_real, Real.norm_eq_abs, abs_of_pos (inv_pos.mpr (root_pos n))]
  simpa using inv_anti₀ (by norm_num : (0 : ℝ) < 1) (root_ge_one n))

theorem regularizer_apply (n : ℕ) : regularizerSymbol n = ((root n)⁻¹ : ℝ) := rfl

theorem regularizer_mem_domain (x : Space) : diagonal regularizerSymbol x ∈ harmonic.domain := by
  change Memℓp (fun n => (harmonicEigenvalue n : ℂ) * diagonal regularizerSymbol x n) 2
  apply (lp.memℓp x).mono'
  intro n
  have heq : (harmonicEigenvalue n : ℂ) * diagonal regularizerSymbol x n = boundedSymbol n * x n := by
    simp only [diagonal_apply, regularizer_apply, boundedSymbol_apply]
    push_cast
    ring
  rw [heq, norm_mul]
  calc
    _ ≤ 1 * ‖x n‖ := mul_le_mul_of_nonneg_right (boundedSymbol_norm_le n) (norm_nonneg _)
    _ = ‖x n‖ := one_mul _

def regularizerDomain (x : Space) : harmonic.domain :=
  ⟨diagonal regularizerSymbol x, regularizer_mem_domain x⟩

theorem bounded_transform_action (x : Space) : harmonic (regularizerDomain x) = diagonal boundedSymbol x := by
  apply lp.ext
  funext n
  change (harmonicEigenvalue n : ℂ) * (((root n)⁻¹ : ℝ) * x n) =
    (harmonicEigenvalue n / root n : ℝ) * x n
  push_cast
  ring

/-- Cayley coefficients are calculated from the same true resolvents. -/
def cayleyCoeff (n : ℕ) : ℂ := denominator 1 n / denominator (-1) n

theorem denominator_norm_pm (n : ℕ) : ‖denominator 1 n‖ = ‖denominator (-1) n‖ := by
  simp only [denominator_norm]
  norm_num

theorem cayleyCoeff_norm (n : ℕ) : ‖cayleyCoeff n‖ = 1 := by
  rw [cayleyCoeff, norm_div, denominator_norm_pm]
  exact div_self (norm_ne_zero_iff.mpr (denominator_ne_zero (-1) n))

def cayleySymbol : Symbol := ofBound cayleyCoeff 1 (fun n => (cayleyCoeff_norm n).le)

theorem cayleySymbol_apply (n : ℕ) : cayleySymbol n = cayleyCoeff n := rfl

theorem cayley_difference (n : ℕ) : cayleySymbol n - 1 = (-2 * Complex.I) / denominator (-1) n := by
  rw [cayleySymbol_apply, cayleyCoeff]
  field_simp [denominator_ne_zero (-1) n]
  simp [denominator]
  ring

theorem cayley_difference_norm (n : ℕ) :
    ‖cayleySymbol n - 1‖ = 2 / ‖denominator (-1) n‖ := by
  rw [cayley_difference, norm_div, norm_mul]
  norm_num

theorem cayley_tail : Tendsto (fun n => cayleySymbol n) atTop (𝓝 1) := by
  rw [tendsto_iff_norm_sub_tendsto_zero]
  have h := (tendsto_inv_atTop_zero.comp eigenvalue_tendsto).const_mul 2
  apply squeeze_zero (g := fun n => 2 * (harmonicEigenvalue n)⁻¹) (fun _ => norm_nonneg _)
  · intro n
    rw [cayley_difference_norm, div_eq_mul_inv]
    exact mul_le_mul_of_nonneg_left (inv_anti₀ (eigenvalue_pos n)
      (denominator_norm_lower (-1) n)) (by norm_num)
  · simpa only [mul_zero, Function.comp_def] using h

theorem cayley_anchored_exact (M : ℕ) :
    ‖diagonal cayleySymbol - diagonal (anchored cayleySymbol 1 M)‖ =
      ⨆ k : ℕ, 2 / ‖denominator (-1) (k + M)‖ := by
  simpa only [cayley_difference_norm] using error_norm_eq_sup cayleySymbol 1 M

theorem cayley_anchored_tendsto :
    Tendsto (fun M => ‖diagonal cayleySymbol - diagonal (anchored cayleySymbol 1 M)‖)
      atTop (𝓝 0) := anchored_norm_tendsto cayleySymbol 1 cayley_tail

theorem cayley_zero_padded_exact (M : ℕ) :
    ‖diagonal cayleySymbol - diagonal (truncate cayleySymbol M)‖ = 1 :=
  unit_modulus_error cayleySymbol cayleyCoeff_norm M

/-- The formula is an actual composition with the unbounded operator on the
proved resolvent range, not a purely suggestive fraction of operators. -/
theorem cayley_transform_action (x : Space) :
    diagonal cayleySymbol x = harmonic (resolventDomain (-1) x) -
      Complex.I • (resolventDomain (-1) x : Space) := by
  apply lp.ext
  funext n
  change (denominator 1 n / denominator (-1) n) * x n =
    (harmonicEigenvalue n : ℂ) * ((denominator (-1) n)⁻¹ * x n) -
      Complex.I * ((denominator (-1) n)⁻¹ * x n)
  simp only [div_eq_mul_inv, denominator]
  push_cast
  ring

theorem cayley_preserves_norm (x : Space) : ‖diagonal cayleySymbol x‖ = ‖x‖ := by
  apply le_antisymm
  · apply lp.norm_mono (by norm_num : (2 : ENNReal) ≠ 0)
    intro n
    simp only [diagonal_apply, norm_mul, cayleySymbol_apply, cayleyCoeff_norm, one_mul, le_refl]
  · apply lp.norm_mono (by norm_num : (2 : ENNReal) ≠ 0)
    intro n
    simp only [diagonal_apply, norm_mul, cayleySymbol_apply, cayleyCoeff_norm, one_mul, le_refl]

end AnchoredSurrogates
end KomorebiPhysics
