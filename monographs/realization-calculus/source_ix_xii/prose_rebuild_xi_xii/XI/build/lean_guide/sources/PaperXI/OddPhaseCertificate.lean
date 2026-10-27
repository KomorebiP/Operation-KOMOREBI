import PaperXI.OddPhase
import PaperXI.OddSymplectic

/-! The actual characteristic-polynomial certificate for the determinant phase.
The source specialization derives even dimension from the supplied form. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OddPhase

variable {p : ℕ} [Fact p.Prime]
variable {V : Type*} [AddCommGroup V] [Module (ZMod p) V]
variable [FiniteDimensional (ZMod p) V]

/-- The actual characteristic polynomial at one is the determinant of the
negative difference. No parity hypothesis is needed for this identity. -/
theorem charpoly_eval_one (g : V ≃ₗ[ZMod p] V) :
    g.toLinearMap.charpoly.eval 1 = LinearMap.det (-difference g) := by
  rw [LinearMap.eval_charpoly]
  congr 1
  ext v
  simp [difference, sub_eq_add_neg]

/-- In even dimension the two difference conventions have the same determinant. -/
theorem determinant_neg_difference (g : V ≃ₗ[ZMod p] V)
    (heven : Even (Module.finrank (ZMod p) V)) :
    LinearMap.det (-difference g) = LinearMap.det (difference g) := by
  rw [← neg_one_smul (ZMod p) (difference g), LinearMap.det_smul,
    heven.neg_one_pow, one_mul]

theorem characteristic_determinant (g : V ≃ₗ[ZMod p] V)
    (heven : Even (Module.finrank (ZMod p) V)) :
    g.toLinearMap.charpoly.eval 1 = LinearMap.det (difference g) := by
  rw [charpoly_eval_one, determinant_neg_difference g heven]

/-- The phase certificate for a supplied even-dimensional space. -/
theorem characteristic_certificate_of_even (g : V ≃ₗ[ZMod p] V)
    (heven : Even (Module.finrank (ZMod p) V)) :
    phase g = quadraticChar (ZMod p) (-1) ^ (Module.finrank (ZMod p) V / 2) *
      quadraticChar (ZMod p) (g.toLinearMap.charpoly.eval 1) := by
  rw [characteristic_determinant g heven]
  rfl

/-- Source 12.5: the actual nondegenerate alternating form in odd
characteristic supplies the parity needed for the characteristic certificate.
The formula also remains valid when the action has fixed vectors. -/
theorem characteristic_certificate (hp : p ≠ 2)
    (b : LinearMap.BilinForm (ZMod p) V) (hb : b.IsAlt) (hbn : b.Nondegenerate)
    (g : V ≃ₗ[ZMod p] V) :
    phase g = quadraticChar (ZMod p) (-1) ^ (Module.finrank (ZMod p) V / 2) *
      quadraticChar (ZMod p) (g.toLinearMap.charpoly.eval 1) :=
  characteristic_certificate_of_even g (OddSymplectic.even_finrank_zmod hp b hb hbn)

/-- Fixed-point-free source data make the characteristic-polynomial value at
one nonzero; it is the actual determinant used in the phase. -/
theorem characteristic_eval_one_ne_zero (hp : p ≠ 2)
    (b : LinearMap.BilinForm (ZMod p) V) (hb : b.IsAlt) (hbn : b.Nondegenerate)
    (g : V ≃ₗ[ZMod p] V) (hg : FixedPointFree g) : g.toLinearMap.charpoly.eval 1 ≠ 0 := by
  rw [characteristic_determinant g (OddSymplectic.even_finrank_zmod hp b hb hbn)]
  exact (fixedPointFree_iff_det_ne_zero g).mp hg

end PaperXI.OddPhase
