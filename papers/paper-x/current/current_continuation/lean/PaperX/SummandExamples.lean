import PaperX.PrecisionIdempotent
import PaperX.SummandBoundary

/-! A concrete application of precision idempotent lifting to an actual
continuous C2 carrier over Z_2.  The supplied projector lives modulo four;
the theorem constructs an exact nonzero proper equivariant projector. -/
set_option autoImplicit false
namespace PaperX.SummandExamples
open scoped Matrix
open PaperX.RepresentationLimits PaperX.CompletionExamples
open PaperX.PrecisionExamples PaperX.SummandBoundary

/-- The prescribed mod-four projector is idempotent. -/
theorem skew_two_quotient_idempotent :
    (skewProjector 2).map (Ideal.Quotient.mk (twoIdeal^2)) *
        (skewProjector 2).map (Ideal.Quotient.mk (twoIdeal^2)) =
      (skewProjector 2).map (Ideal.Quotient.mk (twoIdeal^2)) := by
  rw [← Matrix.map_mul, skewProjector_idempotent]

theorem skew_two_commutes_quotient (g : C2) :
    (tau g).map (Ideal.Quotient.mk (twoIdeal^2)) *
        (skewProjector 2).map (Ideal.Quotient.mk (twoIdeal^2)) =
      (skewProjector 2).map (Ideal.Quotient.mk (twoIdeal^2)) *
        (tau g).map (Ideal.Quotient.mk (twoIdeal^2)) := by
  rw [← Matrix.map_mul, ← Matrix.map_mul]
  apply (quotient_matrices_eq_iff 2 _ _).mpr
  simpa only [Matrix.map_mul] using skew_two_commutes_mod_four g

/-- This uses the general lifting theorem on finite quotient input.  An exact
projector is obtained as a conclusion, not supplied as an input. -/
theorem actual_two_adic_projector_lift :
    ∃ E : Matrix (Fin 2) (Fin 2) ℤ_[2], E * E = E ∧
      E.map (Ideal.Quotient.mk (twoIdeal^1)) =
        (skewProjector 2).map (Ideal.Quotient.mk (twoIdeal^1)) ∧
      (∀ g : C2, tau g * E = E * tau g) ∧ E ≠ 0 ∧ E ≠ 1 := by
  let B := (skewProjector 2).map (Ideal.Quotient.mk (twoIdeal^2))
  obtain ⟨E, hid, hred, hcomm⟩ := PrecisionIdempotent.exists_idempotent_lift
    (2 : ℤ_[2]) 1 1 tau group_order_nonzero group_order_divides_two (by decide)
    B skew_two_quotient_idempotent skew_two_commutes_quotient
  have hE : E.map (Ideal.Quotient.mk (twoIdeal^1)) =
      (skewProjector 2).map (Ideal.Quotient.mk (twoIdeal^1)) := by
    rw [hred]
    ext i j
    simp [B]
  refine ⟨E, hid, hE, hcomm, ?_, ?_⟩
  · intro hz
    have h := (quotient_matrices_eq_iff 1 E (skewProjector 2)).mp hE
    have h00 := congrArg (fun M : Matrix (Fin 2) (Fin 2) (ZMod (2^1)) => M 0 0) h
    norm_num [hz, skewProjector] at h00
    exact (by decide : (0 : ZMod (2^1)) ≠ 1) h00
  · intro hi
    have h := (quotient_matrices_eq_iff 1 E (skewProjector 2)).mp hE
    have h11 := congrArg (fun M : Matrix (Fin 2) (Fin 2) (ZMod (2^1)) => M 1 1) h
    norm_num [hi, skewProjector] at h11
    exact (by decide : (1 : ZMod (2^1)) ≠ 0) h11

end PaperX.SummandExamples
