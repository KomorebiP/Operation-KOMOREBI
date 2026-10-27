module
public import PolynomialPrescribedControls
@[expose] public section
open Komorebi.PolynomialPrescribedControls

-- Invalid: F=T has surjective full Jacobian, but the solved block is zero.
-- At x=0 modulo 2, prescribing parameter digit 1 gives no root modulo 4.
example : Nonempty (Komorebi.PolynomialPrescribedLifts.PrescribedLifts
    2 1 parameterOnly (fun _ => 0) (fun _ => 1)) := by
  exact prescribed_one_no_actual_lift
