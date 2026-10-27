import PaperX.PrecisionExamples
import PaperX.PrecisionBoundary
import PaperX.OrderPrecision

open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.CompletionExamples PaperX.PrecisionExamples

-- The detecting precision is independent of matrix rank.
example (n : ℕ) (ρ τ : MatrixRep ℤ_[2] C2 (Fin n)) :
    Conjugate (reduce twoIdeal τ 2) (reduce twoIdeal ρ 2) ↔ Conjugate τ ρ :=
  PaperX.PrecisionAveraging.conjugacy_iff_reduction (2 : ℤ_[2]) 1 1 ρ τ
    group_order_nonzero group_order_divides_two group_order_not_unit (by decide)

-- The DVR exponent is obtained from the actual valuation of the group order.
example : ∃ e : ℕ,
    IsDiscreteValuationRing.addVal ℤ_[2] (Fintype.card C2 : ℤ_[2]) = e ∧
    ∀ (n : ℕ) (ρ τ : MatrixRep ℤ_[2] C2 (Fin n)),
      Conjugate (reduce twoIdeal τ (e+1)) (reduce twoIdeal ρ (e+1)) ↔
        Conjugate τ ρ :=
  PaperX.OrderPrecision.uniform_detection_precision (2 : ℤ_[2])
    PadicInt.irreducible_p group_order_nonzero

example : ∃ P : (Matrix (Fin 2) (Fin 2) ℤ_[2])ˣ,
    (P : Matrix (Fin 2) (Fin 2) ℤ_[2]).map (Ideal.Quotient.mk (twoIdeal^1)) =
      initialLift.map (Ideal.Quotient.mk (twoIdeal^1)) ∧
    ∀ g, rho g * (P : Matrix (Fin 2) (Fin 2) ℤ_[2]) =
      (P : Matrix (Fin 2) (Fin 2) ℤ_[2]) * tau g :=
  actual_two_adic_precision_lift

example : ¬ Conjugate PaperX.PrecisionBoundary.trivial tau :=
  PaperX.PrecisionBoundary.sign_not_integrally_conjugate_trivial

#check PaperX.PrecisionExamples.actual_two_adic_precision_completion
#check PaperX.OrderPrecision.finite_integral_classes
