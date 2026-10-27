module
public import QuantumArithmeticSpecification

@[expose] public section
set_option autoImplicit false
namespace Komorebi.QuantumArithmetic.VerificationControls
open Komorebi.QuantumArithmetic

theorem wrong_energy_is_false : sqEnergy ramanujan12 ≠ 49 := by
  rw [ramanujan12_energy]
  norm_num

theorem wrong_root_order_is_false : cPow zeta12 6 ≠ cOne := by
  simpa using zeta12_no_smaller_positive_power (⟨5, by decide⟩ : Fin 11)

theorem retaining_noise_is_false : matVec projector12 noise12 ≠ noise12 := by
  rw [projector12_kills_noise]
  intro h
  have h0 := congrArg (fun xs : QVector => xs.getD 0 0) h
  norm_num [noise12] at h0

theorem invented_phase_mode_is_false :
    (List.range 12).map (dft12 absRamanujanCVector) ≠
      [cRat 16, cRat 1, cRat 4, cRat 0, cRat 4, cRat 0,
       cRat 16, cRat 0, cRat 4, cRat 0, cRat 4, cRat 0] := by
  rw [abs_ramanujan_dft_table]
  intro h
  have h1 := congrArg (fun xs : List Cyclo12 => (xs.getD 1 cZero).a) h
  change (0 : ℚ) = 1 at h1
  norm_num at h1

#print axioms wrong_energy_is_false
#print axioms wrong_root_order_is_false
#print axioms retaining_noise_is_false
#print axioms invented_phase_mode_is_false

end Komorebi.QuantumArithmetic.VerificationControls
