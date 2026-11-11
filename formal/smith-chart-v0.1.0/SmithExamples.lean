import SmithResults
import SmithFourier
import SmithAlgebra

/-! Kernel-checked boundary examples that exercise the stated hypotheses. -/

namespace SmithExamples

theorem pole_is_totalized_in_lean : SmithGeometry.impedance 1 = 0 := by
  norm_num [SmithGeometry.impedance]

theorem omitted_denominator_can_fake_passivity :
    SmithGeometry.reflection (-1) = 0 ∧ ((-1 : ℂ).re < 0) := by
  norm_num [SmithGeometry.reflection]

theorem odd_order_is_not_even_duality :
    SmithChart.admittancePacket 3 1 (1 / 2 : ℂ) ≠
      (-1 : ℂ) ^ 1 * SmithChart.impedancePacket 3 1 (1 / 2 : ℂ) := by
  have ht : ‖(1 / 2 : ℂ)‖ < 1 := by norm_num
  rw [SmithChart.odd_admittance_nonzero ht (by decide) (by decide) (by decide),
    SmithChart.packet_nonzero ht (by decide) (by decide)]
  norm_num

theorem order_one_root_does_not_filter_mod_two :
    (2 : ℂ)⁻¹ * (∑ k ∈ Finset.range 2, (((1 : ℂ) ^ 0) / ((1 : ℂ) ^ 1)) ^ k) = 1 := by
  norm_num [Finset.sum_range_succ]

def linearFixture (n : ℕ) : ℂ := if n < 2 then 1 else 0

/-- The degree-two term of (1+t)^2 comes from the two odd lanes. -/
theorem off_diagonal_terms_are_necessary :
    SmithAlgebra.project 2 0 (SmithAlgebra.convolution linearFixture linearFixture) 2 = 1 ∧
      SmithAlgebra.convolution (SmithAlgebra.project 2 0 linearFixture)
        (SmithAlgebra.project 2 0 linearFixture) 2 = 0 := by
  norm_num [SmithAlgebra.project, SmithAlgebra.convolution, linearFixture,
    Finset.sum_range_succ]

end SmithExamples
