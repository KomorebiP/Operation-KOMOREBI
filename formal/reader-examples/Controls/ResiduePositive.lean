import KomorebiReader.ResiduePackets
import Mathlib.Tactic.NormNum

set_option autoImplicit false

open scoped BigOperators
open Komorebi.Reader.ResiduePackets

namespace Komorebi.Reader.Controls.Residue

/-- The reader's exact two-child refinement, for an arbitrary sequence. -/
theorem ten_to_twenty (a : ℕ → ℤ) :
    project 10 4 a = project 20 4 a + project 20 14 a := by
  have h := refinement (by decide : 0 < 20) (by decide : 10 ∣ 20) 4 a
  norm_num [Finset.sum_range_succ] at h
  exact h

/-- A missing odd packet loses a nonzero coefficient. -/
theorem omitted_packet_witness :
    project 2 0 (fun _ : ℕ => (1 : ℤ)) 1 = 0 := by decide

/-- The fine residue zero modulo three crosses the coarse parity boundary. -/
theorem nondividing_moduli_witness :
    project 2 0 (project 3 0 (fun _ : ℕ => (1 : ℤ))) 3 = 0 ∧
      project 3 0 (fun _ : ℕ => (1 : ℤ)) 3 = 1 := by decide

/-- A concrete invertible change of coordinates on a finite carrier. -/
def shear : (ℤ × ℤ) ≃+ (ℤ × ℤ) where
  toFun v := (v.1 + v.2, v.2)
  invFun v := (v.1 - v.2, v.2)
  left_inv v := by
    apply Prod.ext
    · exact add_sub_cancel_right v.1 v.2
    · rfl
  right_inv v := by
    apply Prod.ext
    · exact sub_add_cancel v.1 v.2
    · rfl
  map_add' v w := by
    apply Prod.ext
    · change v.1 + w.1 + (v.2 + w.2) = (v.1 + v.2) + (w.1 + w.2)
      ac_rfl
    · rfl

/-- The first coordinate projector before the coordinate change. -/
def firstCoordinate : (ℤ × ℤ) →+ (ℤ × ℤ) where
  toFun v := (v.1, 0)
  map_zero' := rfl
  map_add' _ _ := rfl

/-- Reusing the old projector after a genuine coordinate change gives a
different answer from the correctly transported projector. -/
theorem shear_requires_transport :
    coordinateTransfer shear firstCoordinate (0, 1) = (-1, 0) ∧
      firstCoordinate (0, 1) = (0, 0) := by decide

end Komorebi.Reader.Controls.Residue
