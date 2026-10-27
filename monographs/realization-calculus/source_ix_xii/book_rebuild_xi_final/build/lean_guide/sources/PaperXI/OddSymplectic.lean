import Mathlib.LinearAlgebra.Matrix.BilinearForm
import Mathlib.LinearAlgebra.FiniteDimensional.Defs
import Mathlib.Algebra.Ring.Parity
import Mathlib.Algebra.Field.ZMod

/-! Even dimension of the actual alternating nondegenerate form in odd
characteristic. The determinant argument uses its matrix in a constructed
finite basis and does not assume symplectic coordinates or evenness. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.OddSymplectic

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable [FiniteDimensional K V]

/-- The actual form matrix is skew under transposition. -/
theorem transpose_toMatrix (b : LinearMap.BilinForm K V) (ha : b.IsAlt) :
    (LinearMap.BilinForm.toMatrix (Module.finBasis K V) b).transpose =
      -LinearMap.BilinForm.toMatrix (Module.finBasis K V) b := by
  ext i j
  simpa only [Matrix.transpose_apply, Matrix.neg_apply, LinearMap.BilinForm.toMatrix_apply]
    using (ha.neg_eq (Module.finBasis K V i) (Module.finBasis K V j)).symm

/-- A finite-dimensional nondegenerate alternating form over a field of
characteristic different from two has even dimension. -/
theorem even_finrank (b : LinearMap.BilinForm K V) (ha : b.IsAlt)
    (hn : b.Nondegenerate) (h2 : (2 : K) ≠ 0) : Even (Module.finrank K V) := by
  let M := LinearMap.BilinForm.toMatrix (Module.finBasis K V) b
  have hd0 : M.det ≠ 0 :=
    (LinearMap.BilinForm.nondegenerate_iff_det_ne_zero (Module.finBasis K V)).mp hn
  have hd := congrArg Matrix.det (transpose_toMatrix b ha)
  change M.transpose.det = (-M).det at hd
  rw [Matrix.det_transpose, Matrix.det_neg, Fintype.card_fin] at hd
  have hp : (-1 : K) ^ Module.finrank K V = 1 := by
    apply mul_right_cancel₀ hd0
    simpa only [one_mul] using hd.symm
  apply (neg_one_pow_eq_one_iff_even ?_).mp hp
  intro h
  apply h2
  have hh := congrArg (fun x : K => x + 1) h
  simpa only [neg_add_cancel, ← one_add_one_eq_two] using hh.symm

/-- The half-dimension is an exact integer, proved from the form hypotheses. -/
theorem finrank_eq_two_mul_half (b : LinearMap.BilinForm K V) (ha : b.IsAlt)
    (hn : b.Nondegenerate) (h2 : (2 : K) ≠ 0) :
    Module.finrank K V = 2 * (Module.finrank K V / 2) := by
  obtain ⟨n, hn⟩ := even_finrank b ha hn h2
  omega

/-- The odd-prime source hypothesis gives the needed nonzero scalar two. -/
theorem two_ne_zero {p : ℕ} [Fact p.Prime] (hp : p ≠ 2) : (2 : ZMod p) ≠ 0 := by
  intro h
  have hd : p ∣ 2 := (ZMod.natCast_eq_zero_iff 2 p).mp h
  rcases (Nat.dvd_prime Nat.prime_two).mp hd with h1 | htwo
  · exact (Nat.Prime.ne_one (Fact.out : p.Prime)) h1
  · exact hp htwo

/-- Source specialization with actual odd-prime and symplectic-form hypotheses. -/
theorem even_finrank_zmod {p : ℕ} [Fact p.Prime] (hp : p ≠ 2)
    {W : Type*} [AddCommGroup W] [Module (ZMod p) W] [FiniteDimensional (ZMod p) W]
    (b : LinearMap.BilinForm (ZMod p) W) (ha : b.IsAlt) (hn : b.Nondegenerate) :
    Even (Module.finrank (ZMod p) W) := even_finrank b ha hn (two_ne_zero hp)

theorem finrank_eq_two_mul_half_zmod {p : ℕ} [Fact p.Prime] (hp : p ≠ 2)
    {W : Type*} [AddCommGroup W] [Module (ZMod p) W] [FiniteDimensional (ZMod p) W]
    (b : LinearMap.BilinForm (ZMod p) W) (ha : b.IsAlt) (hn : b.Nondegenerate) :
    Module.finrank (ZMod p) W = 2 * (Module.finrank (ZMod p) W / 2) :=
  finrank_eq_two_mul_half b ha hn (two_ne_zero hp)

end PaperXI.OddSymplectic
