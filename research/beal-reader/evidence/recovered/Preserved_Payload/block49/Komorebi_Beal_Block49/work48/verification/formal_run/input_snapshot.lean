import Mathlib

/-!+# Block 48: exact local algebra

This file checks only the displayed characteristic-seven polynomial exclusions
and the finite Fontaine–Laffaille determinant-weight calculation. The curve's
Frobenius polynomials, the LMFDB eigenvalues, modular attachment, finite-flatness,
and the determinant/inertia dictionary are external arithmetic inputs.
-/

namespace KomorebiBeal.Block48

section Frobenius

variable {F : Type*} [Field F] [CharP F 7]

private theorem nat_cast_nonzero (n : ℕ) (hn : ¬7 ∣ n) : (n : F) ≠ 0 := by
  exact fun h => hn ((CharP.cast_eq_zero_iff F 7 n).mp h)

/-- Value of the norm-four Hecke polynomial at a potential eigenvalue. -/
def heckeValue (a t : F) : F := t ^ 2 - a * t + 4

/-- Distinct traces in this family have no common eigenvalue, over any
characteristic-seven field, not just over the prime field. -/
theorem common_root_forces_trace_eq (a b t : F)
    (ha : heckeValue a t = 0) (hb : heckeValue b t = 0) : a = b := by
  have ht : t ≠ 0 := by
    intro ht
    subst t
    norm_num [heckeValue] at ha
    exact nat_cast_nonzero 4 (by norm_num) ha
  have hab : (a - b) * t = 0 := by
    unfold heckeValue at ha hb
    linear_combination hb - ha
  exact sub_eq_zero.mp ((mul_eq_zero.mp hab).resolve_right ht)

/-- The three rational traces 4, -4, 1 cannot occur in either odd-C
Frobenius polynomial, whose quadratic trace is 0 or -1. -/
theorem oddC_three_traces_excluded (a b t : F)
    (ha : a = 4 ∨ a = -4 ∨ a = 1) (hb : b = 0 ∨ b = -1)
    (hroot : heckeValue a t = 0) : heckeValue b t ≠ 0 := by
  intro hbroot
  have hab := common_root_forces_trace_eq a b t hroot hbroot
  have hab0 : a - b = 0 := sub_eq_zero.mpr hab
  rcases ha with rfl | rfl | rfl <;>
    rcases hb with rfl | rfl <;> norm_num at hab0
  · exact nat_cast_nonzero 4 (by norm_num) hab0
  · exact nat_cast_nonzero 5 (by norm_num) hab0
  · exact nat_cast_nonzero 4 (by norm_num) hab0
  · exact nat_cast_nonzero 3 (by norm_num) hab0
  · exact nat_cast_nonzero 2 (by norm_num) hab0

/-- A trace-zero candidate cannot use the odd-C quadratic of trace -1. -/
theorem oddC_zero_trace_forces_zero_branch (b t : F)
    (hroot : heckeValue (0 : F) t = 0)
    (hbroot : heckeValue b t = 0) : b = 0 := by
  exact (common_root_forces_trace_eq 0 b t hroot hbroot).symm

/-- None of the four actual candidate trace values vanishes at -1. -/
theorem evenC_candidate_nonzero_at_neg_one (a : F)
    (ha : a = 4 ∨ a = -4 ∨ a = 1 ∨ a = 0) :
    heckeValue a (-1) ≠ 0 := by
  rcases ha with rfl | rfl | rfl | rfl <;> norm_num [heckeValue]
  · exact nat_cast_nonzero 9 (by norm_num)
  · exact nat_cast_nonzero 6 (by norm_num)
  · exact nat_cast_nonzero 5 (by norm_num)

/-- None of the four actual candidate trace values vanishes at -4. -/
theorem evenC_candidate_nonzero_at_neg_four (a : F)
    (ha : a = 4 ∨ a = -4 ∨ a = 1 ∨ a = 0) :
    heckeValue a (-4) ≠ 0 := by
  rcases ha with rfl | rfl | rfl | rfl <;> norm_num [heckeValue]
  · exact nat_cast_nonzero 36 (by norm_num)
  · exact nat_cast_nonzero 4 (by norm_num)
  · exact nat_cast_nonzero 24 (by norm_num)
  · exact nat_cast_nonzero 20 (by norm_num)

/-- No candidate eigenvalue is a root of the full even-C polynomial.
The squares retain the actual multiplicities in the four-dimensional input. -/
theorem evenC_full_polynomial_excluded (a t : F)
    (ha : a = 4 ∨ a = -4 ∨ a = 1 ∨ a = 0)
    (hroot : heckeValue a t = 0) :
    (t + 1) ^ 2 * (t + 4) ^ 2 ≠ 0 := by
  intro hfull
  rcases mul_eq_zero.mp hfull with h | h
  · have ht : t = -1 := by
      exact eq_neg_of_add_eq_zero_left (eq_zero_of_pow_eq_zero h)
    subst t
    exact evenC_candidate_nonzero_at_neg_one a ha hroot
  · have ht : t = -4 := by
      exact eq_neg_of_add_eq_zero_left (eq_zero_of_pow_eq_zero h)
    subst t
    exact evenC_candidate_nonzero_at_neg_four a ha hroot

/-- The odd-C obstruction also covers the squared full polynomial. -/
theorem oddC_full_polynomial_excluded (a b t : F)
    (ha : a = 4 ∨ a = -4 ∨ a = 1) (hb : b = 0 ∨ b = -1)
    (hroot : heckeValue a t = 0) : heckeValue b t ^ 2 ≠ 0 := by
  exact pow_ne_zero 2 (oddC_three_traces_excluded a b t ha hb hroot)

end Frobenius

/-- With two rank-two filtration components, the determinant exponent 8
modulo 48 forces filtration-one dimension one at each component. -/
theorem determinant_weight_uniqueness (d₀ d₁ : ℕ)
    (h₀ : d₀ ≤ 2) (h₁ : d₁ ≤ 2)
    (hdet : (d₀ + 7 * d₁) % 48 = 8) : d₀ = 1 ∧ d₁ = 1 := by
  omega

end KomorebiBeal.Block48

#print axioms KomorebiBeal.Block48.common_root_forces_trace_eq
#print axioms KomorebiBeal.Block48.oddC_three_traces_excluded
#print axioms KomorebiBeal.Block48.oddC_zero_trace_forces_zero_branch
#print axioms KomorebiBeal.Block48.evenC_candidate_nonzero_at_neg_one
#print axioms KomorebiBeal.Block48.evenC_candidate_nonzero_at_neg_four
#print axioms KomorebiBeal.Block48.evenC_full_polynomial_excluded
#print axioms KomorebiBeal.Block48.oddC_full_polynomial_excluded
#print axioms KomorebiBeal.Block48.determinant_weight_uniqueness
