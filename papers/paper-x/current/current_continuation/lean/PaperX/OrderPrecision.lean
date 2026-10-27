import PaperX.PrecisionAveraging
import Mathlib.RingTheory.DiscreteValuationRing.Basic

set_option autoImplicit false
namespace PaperX.OrderPrecision
open PaperX.RepresentationLimits PaperX.RepresentationClasses

variable {R Γ : Type*} [CommRing R] [IsDomain R]
  [IsDiscreteValuationRing R] [Group Γ] [Fintype Γ]

omit [Group Γ] in
/-- A nonzero group order has a finite uniformizer exponent.  The exponent is
chosen from the coefficient ring and group before any representations. -/
theorem exists_order_exponent (π : R) (hπ : Irreducible π)
    (hΓ : (Fintype.card Γ : R) ≠ 0) :
    ∃ e : ℕ, IsDiscreteValuationRing.addVal R (Fintype.card Γ : R) = e ∧
      (Fintype.card Γ : R) ∣ π^e := by
  obtain ⟨e, u, hu⟩ := IsDiscreteValuationRing.eq_unit_mul_pow_irreducible hΓ hπ
  refine ⟨e, ?_, ?_⟩
  · rw [hu, IsDiscreteValuationRing.addVal_def' u hπ]
  · refine ⟨(↑(u⁻¹) : R), ?_⟩
    rw [hu]
    rw [mul_right_comm, Units.mul_inv, one_mul]

omit [IsDomain R] [IsDiscreteValuationRing R] in
/-- Characteristic zero ensures that every finite group has a nonzero order
in the coefficient ring. -/
theorem order_ne_zero [CharZero R] : (Fintype.card Γ : R) ≠ 0 := by
  exact_mod_cast Fintype.card_ne_zero (α := Γ)

/-- One precision detects integral isomorphism in every rank.  Its value is
exactly one more than the valuation of the group order. -/
theorem uniform_detection_precision (π : R) (hπ : Irreducible π)
    (hΓ : (Fintype.card Γ : R) ≠ 0) :
    ∃ e : ℕ, IsDiscreteValuationRing.addVal R (Fintype.card Γ : R) = e ∧
      ∀ (n : ℕ) (ρ τ : MatrixRep R Γ (Fin n)),
        Conjugate (reduce (Ideal.span {π}) τ (e+1))
          (reduce (Ideal.span {π}) ρ (e+1)) ↔ Conjugate τ ρ := by
  obtain ⟨e, he, hdiv⟩ := exists_order_exponent π hπ hΓ
  exact ⟨e, he, fun _ ρ τ => PrecisionAveraging.conjugacy_iff_reduction
    π e 1 ρ τ hΓ hdiv hπ.not_isUnit (by decide)⟩

section Classes
variable {ι : Type*} [Fintype ι] [DecidableEq ι]

/-- Reduction at the group-order precision is injective on actual integral
isomorphism classes.  Surjectivity onto arbitrary quotient representations is
not asserted. -/
theorem reduceClass_injective (π : R) (hπ : Irreducible π) (e : ℕ)
    (hΓ : (Fintype.card Γ : R) ≠ 0) (hdiv : (Fintype.card Γ : R) ∣ π^e) :
    Function.Injective (fun c : ClassRep R Γ ι => reduceClass (Ideal.span {π}) c (e+1)) := by
  intro x y h
  obtain ⟨τ, rfl⟩ := classOf_surjective x
  obtain ⟨ρ, rfl⟩ := classOf_surjective y
  apply classOf_eq.mpr
  exact (PrecisionAveraging.conjugacy_iff_reduction π e 1 ρ τ hΓ hdiv
    hπ.not_isUnit (by decide)).mp (classOf_eq.mp h)

omit [IsDomain R] [IsDiscreteValuationRing R] in
/-- Finite coefficients and a finite source yield finitely many actual
representation classes at that coefficient level. -/
theorem finite_classes_of_finite_coefficients [Finite R] : Finite (ClassRep R Γ ι) := by
  let : Finite (MatrixRep R Γ ι) := Finite.of_injective
    (fun ρ : MatrixRep R Γ ι => (ρ : Γ → Matrix ι ι R))
    (fun _ _ h => MonoidHom.ext (congrFun h))
  exact Finite.of_surjective classOf classOf_surjective

/-- For a fixed finite group and rank, finite coefficient quotients imply
finitely many integral isomorphism classes.  Completeness is unnecessary. -/
theorem finite_integral_classes (π : R) (hπ : Irreducible π)
    (hΓ : (Fintype.card Γ : R) ≠ 0)
    (finiteR : ∀ k, Finite (R ⧸ (Ideal.span {π})^k)) :
    Finite (ClassRep R Γ ι) := by
  obtain ⟨e, _, hdiv⟩ := exists_order_exponent π hπ hΓ
  let : Finite (R ⧸ (Ideal.span {π})^(e+1)) := finiteR (e+1)
  let : Finite (ClassRep (R ⧸ (Ideal.span {π})^(e+1)) Γ ι) :=
    finite_classes_of_finite_coefficients
  exact Finite.of_injective _ (reduceClass_injective π hπ e hΓ hdiv)

end Classes
end PaperX.OrderPrecision
