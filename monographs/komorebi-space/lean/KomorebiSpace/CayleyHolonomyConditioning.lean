import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.Normed.Operator.LinearIsometry
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

set_option autoImplicit false

/-!
# A two-real-dimensional family with unbounded holonomy correction gains

Multiplication by (t+i)/(t-i) is a real linear isometry of C with no nonzero
fixed vector, for every real t. Its exact correction gain is |t-i|/2. Thus
finite dimensionality supplies a finite gain for each system, not a common
gain for all isometric loop operators. All statements are universal in t.
-/
noncomputable section
namespace KomorebiSpace
namespace CayleyHolonomy

@[simp] theorem denominator_ne_zero (t : ℝ) : (t : ℂ)-Complex.I ≠ 0 := by
  intro h
  have hi := congrArg Complex.im h
  norm_num at hi

@[simp] theorem numerator_ne_zero (t : ℝ) : (t : ℂ)+Complex.I ≠ 0 := by
  intro h
  have hi := congrArg Complex.im h
  norm_num at hi

def phase (t : ℝ) : ℂ := ((t : ℂ)+Complex.I)/((t : ℂ)-Complex.I)

theorem phase_ne_zero (t : ℝ) : phase t ≠ 0 :=
  div_ne_zero (numerator_ne_zero t) (denominator_ne_zero t)

theorem phase_norm (t : ℝ) : ‖phase t‖ = 1 := by
  have hc : (t : ℂ)+Complex.I = star ((t : ℂ)-Complex.I) := by
    apply Complex.ext <;> simp
  unfold phase
  rw [norm_div, hc, norm_star, div_self (norm_ne_zero_iff.mpr (denominator_ne_zero t))]

theorem phase_ne_one (t : ℝ) : phase t ≠ 1 := by
  intro h
  have he : (t : ℂ)+Complex.I = (t : ℂ)-Complex.I :=
    (div_eq_one_iff_eq (denominator_ne_zero t)).mp h
  have hi := congrArg Complex.im he
  norm_num at hi

/-- A genuine real linear isometry, not an arbitrary small residual operator. -/
def rotation (t : ℝ) : ℂ ≃ₗᵢ[ℝ] ℂ where
  toFun z := phase t * z
  invFun z := (phase t)⁻¹ * z
  left_inv z := by dsimp only; rw [← mul_assoc, inv_mul_cancel₀ (phase_ne_zero t), one_mul]
  right_inv z := by dsimp only; rw [← mul_assoc, mul_inv_cancel₀ (phase_ne_zero t), one_mul]
  map_add' z w := mul_add _ _ _
  map_smul' c z := by
    change phase t * ((c : ℂ)*z) = (c : ℂ)*(phase t*z)
    ring
  norm_map' z := by
    change ‖phase t * z‖ = ‖z‖
    rw [norm_mul, phase_norm, one_mul]

@[simp] theorem rotation_apply (t : ℝ) (z : ℂ) : rotation t z = phase t * z := rfl

theorem fixed_iff_zero (t : ℝ) (z : ℂ) : rotation t z = z ↔ z = 0 := by
  rw [rotation_apply]
  constructor
  · intro h
    have hp : (phase t-1)*z = 0 := by rw [sub_mul, one_mul, h, sub_self]
    exact (mul_eq_zero.mp hp).resolve_left (sub_ne_zero.mpr (phase_ne_one t))
  · intro h; simp [h]

theorem phase_sub_one (t : ℝ) :
    phase t-1 = (2:ℂ)*Complex.I/((t:ℂ)-Complex.I) := by
  unfold phase
  field_simp
  ring

theorem phase_displacement_norm (t : ℝ) :
    ‖phase t-1‖ = 2/‖(t:ℂ)-Complex.I‖ := by
  rw [phase_sub_one, norm_div, norm_mul]
  norm_num

def sharpGain (t : ℝ) : ℝ := ‖(t:ℂ)-Complex.I‖/2

theorem sharpGain_pos (t : ℝ) : 0 < sharpGain t := by
  unfold sharpGain
  exact div_pos (norm_pos_iff.mpr (denominator_ne_zero t)) (by norm_num)

/-- Equality for all inputs gives the exact, rather than only sufficient, gain. -/
theorem sharp_gain_identity (t : ℝ) (z : ℂ) :
    sharpGain t * ‖rotation t z-z‖ = ‖z‖ := by
  have hf : rotation t z-z = (phase t-1)*z := by rw [rotation_apply]; ring
  rw [hf, norm_mul, phase_displacement_norm]
  unfold sharpGain
  field_simp [norm_ne_zero_iff.mpr (denominator_ne_zero t)]

/-- Any claimed stability bound must be at least the displayed gain. -/
theorem necessary_gain (t C : ℝ)
    (h : ∀ z : ℂ, ‖z‖ ≤ C * ‖rotation t z-z‖) : sharpGain t ≤ C := by
  have he := sharp_gain_identity t (1:ℂ)
  have hb := mul_le_mul_of_nonneg_left (h 1) (le_of_lt (sharpGain_pos t))
  norm_num only [norm_one] at he hb
  calc
    sharpGain t = sharpGain t * 1 := by ring
    _ ≤ sharpGain t * (C * ‖rotation t 1-1‖) := hb
    _ = C * (sharpGain t * ‖rotation t 1-1‖) := by ring
    _ = C := by rw [he, mul_one]

theorem gain_unbounded (C : ℝ) : ∃ t : ℝ, C < sharpGain t := by
  let t := 2*|C|+1
  have ht : 0 ≤ t := by dsimp [t]; positivity
  have hn := Complex.abs_re_le_norm ((t:ℂ)-Complex.I)
  have hn' : t ≤ ‖(t:ℂ)-Complex.I‖ := by
    simpa only [Complex.sub_re, Complex.ofReal_re, Complex.I_re,
      sub_zero, abs_of_nonneg ht] using hn
  refine ⟨t, ?_⟩
  unfold sharpGain
  have hc := le_abs_self C
  dsimp [t] at hn' ⊢
  linarith

theorem no_uniform_holonomy_gain :
    ¬ ∃ C : ℝ, ∀ t : ℝ, ∀ z : ℂ, ‖z‖ ≤ C * ‖rotation t z-z‖ := by
  rintro ⟨C,hC⟩
  obtain ⟨t,ht⟩ := gain_unbounded C
  exact (not_le_of_gt ht) (necessary_gain t C (hC t))

end CayleyHolonomy
end KomorebiSpace
end
