import PaperXI.GeneralChain
import PaperXI.ChainSharpness
import PaperXI.ScalarCovariance
import PaperXI.FourierCovariance
import PaperXI.HolonomyResidual

set_option autoImplicit false
namespace PaperXI.BoundaryExamples
open PaperXI.MonodromyChain

theorem empty_chain : (shift (K := ℚ) (W := ℚ) (m := 0) (fun _ => 1)) ^ 0 = 0 :=
  nilpotent_bound _

theorem singleton_chain : (shift (K := ℚ) (W := ℚ) (m := 1) (fun _ => 1)) ^ 1 = 0 :=
  nilpotent_bound _

theorem length_three_square_nonzero :
    (shift (K := ℚ) (W := ℚ) (m := 3) (fun _ => 1)) ^ 2 ≠ 0 :=
  identity_shift_power_ne_zero (by decide)

theorem length_three_cube_zero :
    (shift (K := ℚ) (W := ℚ) (m := 3) (fun _ => 1)) ^ 3 = 0 := nilpotent_bound _

theorem inverse_two_mod_five : (2 : ZMod 5)⁻¹ = 3 := by
  exact ZMod.inv_eq_of_mul_eq_one 5 2 3 (by decide)
theorem inverse_label_differs : (2 : ZMod 5)⁻¹ ≠ 2 := by
  rw [inverse_two_mod_five]
  decide

end PaperXI.BoundaryExamples
