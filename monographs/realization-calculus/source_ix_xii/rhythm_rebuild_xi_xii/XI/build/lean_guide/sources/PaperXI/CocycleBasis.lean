import PaperXI.CocycleCommutator
import Mathlib.LinearAlgebra.Basis.SMul
import Mathlib.Algebra.Algebra.Basic

/-! Paper XI, Proposition 8.1: the coefficient change in an actual algebra basis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CocycleCommutator
open Module

variable {A K B : Type*} [CommGroup A] [CommRing K] [Ring B] [Algebra K B]

/-- Rescaling the actual basis, not merely a coefficient function, gives the
coboundary formula for its multiplication table. -/
theorem rescaled_basis_mul (c : Cocycle A Kˣ) (u : Basis A K B)
    (hu : ∀ a b, u a * u b = (c.coeff a b : K) • u (a * b))
    (s : A → Kˣ) (a b : A) :
    u.unitsSMul s a * u.unitsSMul s b =
      ((rescale c s).coeff a b : K) • u.unitsSMul s (a * b) := by
  simp only [Basis.unitsSMul_apply, Units.smul_def, smul_mul_assoc, mul_smul_comm,
    hu, smul_smul, rescale, div_eq_mul_inv, Units.val_mul]
  congr 1
  exact congrArg (fun t : Kˣ => (t : K)) (show
    s b * (s a * c.coeff a b) =
      (s a * s b * (s (a * b))⁻¹ * c.coeff a b) * s (a * b) by
    simp [mul_assoc, mul_comm, mul_left_comm])

/-- After the actual basis change, the scalar commutator is unchanged. -/
theorem rescaled_basis_commutator (c : Cocycle A Kˣ) (s : A → Kˣ) (a b : A) :
    (rescale c s).coeff a b / (rescale c s).coeff b a =
      c.coeff a b / c.coeff b a := commutator_rescale c s a b

end PaperXI.CocycleCommutator
