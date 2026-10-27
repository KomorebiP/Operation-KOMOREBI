import KomorebiVerification.PaperII.ReleaseTransferMultigradedRational
import Mathlib.FieldTheory.RatFunc.Basic

/-! Consequences of the semantic transfer identities. Coefficient recurrences
use the actual vanishing coefficient, so the zero numerator at index zero is
included. Over a field the reduced rational-function denominator divides the
transfer determinant. -/
set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PaperII.ReleaseTransferConsequences
universe u v w z

section Recurrence
variable {R : Type u} [CommRing R]

theorem recurrence_of_coefficient_zero (P Q : Polynomial R) (Z : PowerSeries R)
    (h : (Q : PowerSeries R) * Z = (P : PowerSeries R)) (n : ℕ)
    (hn : P.coeff n = 0) :
    ∑ k ∈ Finset.range (n + 1), Q.coeff k * PowerSeries.coeff (n - k) Z = 0 := by
  have hc := congrArg (PowerSeries.coeff n) h
  rw [PowerSeries.coeff_mul, Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at hc
  simpa [hn] using hc

theorem recurrence_of_degree_lt (P Q : Polynomial R) (Z : PowerSeries R)
    (h : (Q : PowerSeries R) * Z = (P : PowerSeries R)) (n : ℕ)
    (hn : P.degree < (n : WithBot ℕ)) :
    ∑ k ∈ Finset.range (n + 1), Q.coeff k * PowerSeries.coeff (n - k) Z = 0 :=
  recurrence_of_coefficient_zero P Q Z h n (Polynomial.coeff_eq_zero_of_degree_lt hn)

theorem zero_numerator_recurrence (Q : Polynomial R) (Z : PowerSeries R)
    (h : (Q : PowerSeries R) * Z = 0) (n : ℕ) :
    ∑ k ∈ Finset.range (n + 1), Q.coeff k * PowerSeries.coeff (n - k) Z = 0 := by
  exact recurrence_of_coefficient_zero 0 Q Z (by simpa using h) n (by simp)

end Recurrence

section Scalar
open TransferZeta
variable {V : Type u} {E : Type v} {R : Type w}
variable [Fintype V] [Fintype E] [DecidableEq V] [CommRing R]
variable (G : PositiveWeightedMultigraph V E) (m : E → R)

 theorem scalar_denominator_ne_zero [Nontrivial R] :
    ReleaseTransferScalar.denominator G m ≠ 0 := by
  intro h
  have hc := ReleaseTransferScalar.denominator_coeff_zero G m
  rw [h, Polynomial.coeff_zero] at hc
  exact zero_ne_one hc

 theorem scalar_endpoint_unique (u v : V → R) (Z : PowerSeries R)
    (h : (ReleaseTransferScalar.denominator G m : PowerSeries R) * Z =
      (ReleaseTransferScalar.endpointNumerator G m u v : PowerSeries R)) :
    Z = ReleaseTransferScalar.endpointSeries G m u v := by
  calc
    Z = 1 * Z := (one_mul _).symm
    _ = (ReleaseTransferScalar.denominatorInverse G m *
      (ReleaseTransferScalar.denominator G m : PowerSeries R)) * Z := by
        rw [ReleaseTransferScalar.denominator_inverse_mul]
    _ = ReleaseTransferScalar.denominatorInverse G m *
      ((ReleaseTransferScalar.denominator G m : PowerSeries R) * Z) := mul_assoc _ _ _
    _ = ReleaseTransferScalar.denominatorInverse G m *
      ((ReleaseTransferScalar.denominator G m : PowerSeries R) *
        ReleaseTransferScalar.endpointSeries G m u v) := by
          rw [h, ReleaseTransferScalar.endpoint_rationality]
    _ = ReleaseTransferScalar.endpointSeries G m u v := by
      rw [← mul_assoc, ReleaseTransferScalar.denominator_inverse_mul, one_mul]

end Scalar

section RationalFunction
open TransferZeta
variable {V : Type u} {E : Type v} {K : Type w}
variable [Fintype V] [Fintype E] [DecidableEq V] [Field K]
variable (G : PositiveWeightedMultigraph V E) (m : E → K)

noncomputable def endpointRationalFunction (u v : V → K) : RatFunc K :=
  algebraMap (Polynomial K) (RatFunc K) (ReleaseTransferScalar.endpointNumerator G m u v) /
    algebraMap (Polynomial K) (RatFunc K) (ReleaseTransferScalar.denominator G m)

theorem reduced_denominator_dvd (u v : V → K) :
    RatFunc.denom (endpointRationalFunction G m u v) ∣ ReleaseTransferScalar.denominator G m :=
  RatFunc.denom_div_dvd _ _

end RationalFunction

section Multigraded
variable {V : Type u} {E : Type v} {σ : Type w} {R : Type z}
variable [Fintype V] [Fintype E] [DecidableEq V] [DecidableEq σ] [CommRing R]
variable (G : ReleaseTransferMultigraded.Graph V E σ) (m : E → R)

theorem multigraded_denominator_ne_zero [Nontrivial R] :
    ReleaseTransferMultigraded.denominator G m ≠ 0 := by
  intro h
  have hc := ReleaseTransferMultigraded.denominator_constantCoeff G m
  rw [h, map_zero] at hc
  exact zero_ne_one hc

theorem multigraded_endpoint_unique (u v : V → R) (Z : MvPowerSeries σ R)
    (h : (ReleaseTransferMultigraded.denominator G m : MvPowerSeries σ R) * Z =
      (ReleaseTransferMultigraded.endpointNumerator G m u v : MvPowerSeries σ R)) :
    Z = ReleaseTransferMultigraded.endpointSeries G m u v := by
  calc
    Z = 1 * Z := (one_mul _).symm
    _ = (ReleaseTransferMultigraded.denominatorInverse G m *
      (ReleaseTransferMultigraded.denominator G m : MvPowerSeries σ R)) * Z := by
        rw [ReleaseTransferMultigraded.denominator_inverse_mul]
    _ = ReleaseTransferMultigraded.denominatorInverse G m *
      ((ReleaseTransferMultigraded.denominator G m : MvPowerSeries σ R) * Z) := mul_assoc _ _ _
    _ = ReleaseTransferMultigraded.denominatorInverse G m *
      ((ReleaseTransferMultigraded.denominator G m : MvPowerSeries σ R) *
        ReleaseTransferMultigraded.endpointSeries G m u v) := by
          rw [h, ReleaseTransferMultigraded.endpoint_rationality]
    _ = ReleaseTransferMultigraded.endpointSeries G m u v := by
      rw [← mul_assoc, ReleaseTransferMultigraded.denominator_inverse_mul, one_mul]

end Multigraded
end Komorebi.PaperII.ReleaseTransferConsequences
