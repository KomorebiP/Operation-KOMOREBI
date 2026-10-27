import Mathlib

/-!
Elementary algebraic certificates for the ABC jet-determinant block.
STATUS: NOT COMPILER-VERIFIED IN THE AUTHORING RUNTIME.
This file does not formalize the infinite polylogarithm series, p-adic convergence,
Cauchy--Binet limit, ABC, or any IUT-specific arithmetic object.
There are no custom axioms or placeholder proofs.
-/

set_option autoImplicit false

namespace Komorebi.ABCJet

/-- The omitted factor `a*b` in the old all-sector target is load-bearing. -/
theorem balanced_ratio (a b c R : ℚ)
    (ha : a ≠ 0) (hb : b ≠ 0) (hR : R ≠ 0) :
    (a * b * c / R) / (a * b) = c / R := by
  field_simp [ha, hb, hR]; ring

/-- Two-node Gram determinant: an explicit nonvanishing mechanism. -/
theorem two_node_gram (w₁ w₂ x₁ x₂ : ℚ) :
    (w₁ + w₂) * (w₁ * x₁ ^ 2 + w₂ * x₂ ^ 2)
      - (w₁ * x₁ + w₂ * x₂) ^ 2 =
      w₁ * w₂ * (x₁ - x₂) ^ 2 := by
  ring

/-- Three-node Cauchy--Binet identity, finite and purely algebraic. -/
theorem three_node_gram (w₁ w₂ w₃ x₁ x₂ x₃ : ℚ) :
    (w₁ + w₂ + w₃) * (w₁ * x₁ ^ 2 + w₂ * x₂ ^ 2 + w₃ * x₃ ^ 2)
      - (w₁ * x₁ + w₂ * x₂ + w₃ * x₃) ^ 2 =
      w₁ * w₂ * (x₁ - x₂) ^ 2 +
      w₁ * w₃ * (x₁ - x₃) ^ 2 +
      w₂ * w₃ * (x₂ - x₃) ^ 2 := by
  ring

/-- The first three spectral moments, truncated at k=3. -/
def truncatedH2 (t : ℚ) : ℚ :=
  (t + t ^ 2 / 2 + t ^ 3 / 3) *
      (t + t ^ 2 / 8 + t ^ 3 / 27) -
      (t + t ^ 2 / 4 + t ^ 3 / 9) ^ 2

theorem truncatedH2_formula (t : ℚ) :
    truncatedH2 t = t ^ 3 * (27 + 32 * t + t ^ 2) / 216 := by
  unfold truncatedH2
  ring

/-- Clearing this explicit truncation does not provide output-prime contact. -/
theorem cleared_truncation (a c : ℚ) (hc : c ≠ 0) :
    216 * c ^ 5 * truncatedH2 (a / c) =
      a ^ 3 * (27 * c ^ 2 + 32 * a * c + a ^ 2) := by
  rw [truncatedH2_formula]
  field_simp [hc]; ring

/-- Its remainder modulo c is a^5, stated as an exact integer identity. -/
theorem cleared_truncation_remainder (a c : ℤ) :
    a ^ 3 * (27 * c ^ 2 + 32 * a * c + a ^ 2) =
      a ^ 5 + c * (27 * a ^ 3 * c + 32 * a ^ 4) := by
  ring

/-- Relation between the determinant and the first three positive jet filters. -/
theorem determinant_in_jet_coordinates (L₁ L₂ L₃ : ℚ) :
    L₁ * L₃ - L₂ ^ 2 =
      L₁ * ((L₁ - L₂) / 2) +
      3 * L₁ * ((L₁ - 3 * L₂ + 2 * L₃) / 6) -
      4 * ((L₁ - L₂) / 2) ^ 2 := by
  ring

end Komorebi.ABCJet
