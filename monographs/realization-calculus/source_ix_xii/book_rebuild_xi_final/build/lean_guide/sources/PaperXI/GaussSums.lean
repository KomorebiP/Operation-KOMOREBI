import Mathlib.NumberTheory.GaussSum
import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Tactic

/-! Finite-field Gauss sums with the manuscript's sum over the unit group.
The additive character is explicitly required to be nontrivial. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.GaussSums
open scoped Classical

variable {k : Type*} [Field k] [Fintype k]

/-- The literal sum over nonzero field elements, represented by units. -/
def unitSum (χ : MulChar k ℂ) (ψ : AddChar k ℂ) : ℂ :=
  ∑ x : kˣ, χ x * ψ x

/-- Mathlib's sum includes zero, where the extended multiplicative character vanishes. -/
theorem unitSum_eq_gaussSum (χ : MulChar k ℂ) (ψ : AddChar k ℂ) :
    unitSum χ ψ = gaussSum χ ψ := by
  classical
  rw [gaussSum, Fintype.sum_eq_add_sum_subtype_ne _ 0]
  simp only [MulChar.map_zero, zero_mul, zero_add]
  exact Fintype.sum_equiv (unitsEquivNeZero (G₀ := k)) _ _ (fun _ => rfl)

/-- The product with both characters inverted is the field cardinality. -/
theorem sum_mul_inverse {χ : MulChar k ℂ} {ψ : AddChar k ℂ}
    (hχ : χ ≠ 1) (hψ : ψ ≠ 1) :
    unitSum χ ψ * unitSum χ⁻¹ ψ⁻¹ = Fintype.card k := by
  simpa only [unitSum_eq_gaussSum] using
    gaussSum_mul_gaussSum_eq_card hχ (AddChar.IsPrimitive.of_ne_one hψ)

/-- Complex conjugation inverts both characters. -/
theorem conjugate_sum (χ : MulChar k ℂ) (ψ : AddChar k ℂ) :
    star (unitSum χ ψ) = unitSum χ⁻¹ ψ⁻¹ := by
  simpa only [unitSum_eq_gaussSum] using star_gaussSum_eq χ ψ

/-- The squared norm is the cardinality, before taking the positive square root. -/
theorem norm_sq {χ : MulChar k ℂ} {ψ : AddChar k ℂ}
    (hχ : χ ≠ 1) (hψ : ψ ≠ 1) :
    ‖unitSum χ ψ‖ ^ 2 = (Fintype.card k : ℝ) := by
  have h := sum_mul_inverse hχ hψ
  rw [← conjugate_sum] at h
  have he : ((‖unitSum χ ψ‖ ^ 2 : ℝ) : ℂ) = Fintype.card k := by
    simpa only [Complex.star_def, Complex.mul_conj', Complex.ofReal_pow] using h
  exact_mod_cast he

/-- Proposition 6.1: the magnitude of a nontrivial Gauss sum. -/
theorem magnitude {χ : MulChar k ℂ} {ψ : AddChar k ℂ}
    (hχ : χ ≠ 1) (hψ : ψ ≠ 1) :
    ‖unitSum χ ψ‖ = Real.sqrt (Fintype.card k) := by
  rw [← norm_sq hχ hψ, Real.sqrt_sq (norm_nonneg _)]

/-- The product identity with the same additive character on both factors. -/
theorem sum_duality {χ : MulChar k ℂ} {ψ : AddChar k ℂ}
    (hχ : χ ≠ 1) (hψ : ψ ≠ 1) :
    unitSum χ ψ * unitSum χ⁻¹ ψ = χ (-1) * Fintype.card k := by
  simp only [unitSum_eq_gaussSum]
  rw [← mul_gaussSum_inv_eq_gaussSum χ⁻¹, mul_left_comm,
    gaussSum_mul_gaussSum_eq_card hχ (AddChar.IsPrimitive.of_ne_one hψ),
    MulChar.inv_apply', inv_neg_one]

/-- Definition 6.2: positive real square-root normalization. -/
def phase (χ : MulChar k ℂ) (ψ : AddChar k ℂ) : ℂ :=
  unitSum χ ψ / (Real.sqrt (Fintype.card k) : ℂ)

/-- The normalization is defined using a strictly positive real denominator. -/
theorem sqrt_card_pos : 0 < Real.sqrt (Fintype.card k : ℝ) := by
  exact Real.sqrt_pos.2 (by exact_mod_cast Fintype.card_pos)

/-- The asserted unit-circle property in Definition 6.2. -/
theorem phase_norm {χ : MulChar k ℂ} {ψ : AddChar k ℂ}
    (hχ : χ ≠ 1) (hψ : ψ ≠ 1) : ‖phase χ ψ‖ = 1 := by
  rw [phase, norm_div, magnitude hχ hψ, Complex.norm_real,
    Real.norm_eq_abs, abs_of_pos (sqrt_card_pos (k := k))]
  exact div_self (ne_of_gt (sqrt_card_pos (k := k)))

/-- Proposition 6.3: normalized Gauss phases are dual with sign χ(-1). -/
theorem phase_duality {χ : MulChar k ℂ} {ψ : AddChar k ℂ}
    (hχ : χ ≠ 1) (hψ : ψ ≠ 1) :
    phase χ ψ * phase χ⁻¹ ψ = χ (-1) := by
  have hq : (Fintype.card k : ℂ) ≠ 0 := by
    exact_mod_cast (ne_of_gt (Fintype.card_pos : 0 < Fintype.card k))
  have hs : (Real.sqrt (Fintype.card k) : ℂ) ^ 2 = Fintype.card k := by
    exact_mod_cast Real.sq_sqrt (show (0 : ℝ) ≤ Fintype.card k by positivity)
  rw [phase, phase, div_mul_div_comm, ← pow_two, hs, sum_duality hχ hψ,
    mul_div_cancel_right₀ _ hq]

end PaperXI.GaussSums
