import Komorebi.RationalMatrixCertificates
import Komorebi.SelfAdjointPackets
import Mathlib.Data.Rat.Cast.Order

set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix Komorebi.PacketEnergy

variable {ι κ α β : Type*} [Fintype ι] [Fintype κ] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- Four finite exact-rational obligations, including complete coverage. -/
abbrev RationalPacketsValid (Q : α → Matrix ι ι ℚ) : Prop :=
  (∀ a, (Q a).transpose = Q a) ∧
  (∀ a, Q a * Q a = Q a) ∧
  (∀ a b, a ≠ b → Q a * Q b = 0) ∧
  (∑ a, Q a) = 1

def checkRationalPackets (Q : α → Matrix ι ι ℚ) : Bool :=
  decide (RationalPacketsValid Q)

@[simp] theorem checkRationalPackets_eq_true (Q : α → Matrix ι ι ℚ) :
    checkRationalPackets Q = true ↔ RationalPacketsValid Q := by
  simp [checkRationalPackets]

/-- Rational structural checks construct the stronger real projector geometry. -/
noncomputable def realPackets (Q : α → Matrix ι ι ℚ) (h : RationalPacketsValid Q) :
    SelfAdjointPackets ι α where
  proj a := realMatrix (Q a)
  symmetric a := by rw [← realMatrix_transpose, h.1 a]
  idempotent a := by rw [← realMatrix_mul, h.2.1 a]
  disjoint a b hab := by rw [← realMatrix_mul, h.2.2.1 a b hab, realMatrix_zero]

omit [DecidableEq α] in
@[simp] theorem realPackets_proj (Q : α → Matrix ι ι ℚ)
    (h : RationalPacketsValid Q) (a : α) :
    (realPackets Q h).proj a = realMatrix (Q a) := rfl

omit [DecidableEq α] in
theorem realPackets_complete (Q : α → Matrix ι ι ℚ) (h : RationalPacketsValid Q) :
    (realPackets Q h).Complete := by
  change (∑ a, realMatrix (Q a)) = 1
  rw [← realMatrix_sum, h.2.2.2, realMatrix_one]

omit [DecidableEq ι] [DecidableEq κ] in
/-- Every exact rational energy is interpreted as the real squared Frobenius energy. -/
theorem rationalEnergy_cast (A : Matrix ι κ ℚ) :
    (rationalEnergy A : ℝ) = matrixEnergy (realMatrix A) := by
  simp [rationalEnergy, matrixEnergy, realMatrix, pow_two]

/-- Rational upper bounds give real local enclosures for arbitrary rectangular packets. -/
theorem rational_packet_majorant (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D)
    (A : Matrix ι κ ℚ) (b : α → β → ℚ)
    (hb : ∀ a c, rationalEnergy (Q a * A * D c) ≤ b a c) (a : α) (c : β) :
    matrixEnergy ((realPackets Q hQ).proj a * realMatrix A * (realPackets D hD).proj c)
      ≤ (b a c : ℝ) := by
  rw [realPackets_proj, realPackets_proj, ← realMatrix_mul, ← realMatrix_mul,
    ← rationalEnergy_cast]
  exact_mod_cast hb a c

end Komorebi.ExactPosterior
