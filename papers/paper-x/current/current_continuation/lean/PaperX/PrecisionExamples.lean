import PaperX.ArithmeticCertificateExample
import PaperX.AveragingBoundary
import PaperX.PrecisionCompletion

/-! Sharp finite precision examples over the actual ring Z_2. -/
set_option autoImplicit false
namespace PaperX.PrecisionExamples
open scoped Matrix
open PaperX.CompletionExamples PaperX.RepresentationLimits
open PaperX.RepresentationTopology PaperX.RepresentationClasses
open PaperX.RepresentationForests

instance twoPrime : Fact (Nat.Prime 2) := ⟨by norm_num⟩

def integerRho : MatrixRep ℤ C2 (Fin 2) where
  toFun g := if g.toAdd = 0 then 1 else !![1, 2; 0, -1]
  map_one' := by decide +kernel
  map_mul' := by decide +kernel

def integerLift : Matrix (Fin 2) (Fin 2) ℤ := !![1, 1; 0, 1]
def integerComparison : Matrix (Fin 2) (Fin 2) ℤ := !![1, -1; 0, 1]

noncomputable def rho : MatrixRep ℤ_[2] C2 (Fin 2) :=
  changeCoefficients (Int.castRingHom ℤ_[2]) integerRho
noncomputable def tau : MatrixRep ℤ_[2] C2 (Fin 2) :=
  changeCoefficients (Int.castRingHom ℤ_[2]) signRep
noncomputable def initialLift : Matrix (Fin 2) (Fin 2) ℤ_[2] :=
  integerLift.map (Int.castRingHom ℤ_[2])
noncomputable def comparison : Matrix (Fin 2) (Fin 2) ℤ_[2] :=
  integerComparison.map (Int.castRingHom ℤ_[2])

noncomputable abbrev modTwo : ℤ_[2] →+* ZMod 2 := PadicInt.toZMod
noncomputable abbrev modFour : ℤ_[2] →+* ZMod 4 := PadicInt.toZModPow 2
noncomputable abbrev twoIdeal : Ideal ℤ_[2] := Ideal.span {(2 : ℤ_[2])}

/-- The actual p-adic quotient comparison agrees with reduction to Z/2^n. -/
theorem quotient_eq_iff (n : ℕ) (x y : ℤ_[2]) :
    Ideal.Quotient.mk (twoIdeal^n) x = Ideal.Quotient.mk (twoIdeal^n) y ↔
      PadicInt.toZModPow n x = PadicInt.toZModPow n y := by
  rw [Ideal.Quotient.mk_eq_mk_iff_sub_mem, ← sub_eq_zero, ← map_sub,
    ← RingHom.mem_ker, PadicInt.ker_toZModPow]
  norm_num [twoIdeal, Ideal.span_singleton_pow]

theorem quotient_matrices_eq_iff (n : ℕ) (A B : Matrix (Fin 2) (Fin 2) ℤ_[2]) :
    A.map (Ideal.Quotient.mk (twoIdeal^n)) = B.map (Ideal.Quotient.mk (twoIdeal^n)) ↔
      A.map (PadicInt.toZModPow n) = B.map (PadicInt.toZModPow n) := by
  constructor
  · intro h
    ext i j
    exact (quotient_eq_iff n _ _).mp (congrArg (fun M => M i j) h)
  · intro h
    ext i j
    exact (quotient_eq_iff n _ _).mpr (congrArg (fun M => M i j) h)

theorem group_order_nonzero : (Fintype.card C2 : ℤ_[2]) ≠ 0 := by
  norm_num [show Fintype.card C2 = 2 from rfl]

theorem group_order_not_unit : ¬ IsUnit (Fintype.card C2 : ℤ_[2]) := by
  change ¬ IsUnit (2 : ℤ_[2])
  exact PadicInt.irreducible_p.not_isUnit

theorem group_order_divides_two : (Fintype.card C2 : ℤ_[2]) ∣ (2 : ℤ_[2])^1 := by
  norm_num [show Fintype.card C2 = 2 from rfl]

/-- The chosen lift is an exact intertwiner modulo four. -/
theorem initial_lift_intertwines_mod_four (g : C2) :
    (rho g).map modFour * initialLift.map modFour =
      initialLift.map modFour * (tau g).map modFour := by
  have hi : ∀ g : C2,
      (integerRho g).map (Int.castRingHom (ZMod 4)) *
        integerLift.map (Int.castRingHom (ZMod 4)) =
      integerLift.map (Int.castRingHom (ZMod 4)) *
        (signRep g).map (Int.castRingHom (ZMod 4)) := by decide +kernel
  simpa [rho, tau, initialLift, changeCoefficients, Matrix.map_map,
    Function.comp_def] using hi g

theorem initial_lift_intertwines_quotient (g : C2) :
    (rho g).map (Ideal.Quotient.mk (twoIdeal^2)) *
        initialLift.map (Ideal.Quotient.mk (twoIdeal^2)) =
      initialLift.map (Ideal.Quotient.mk (twoIdeal^2)) *
        (tau g).map (Ideal.Quotient.mk (twoIdeal^2)) := by
  rw [← Matrix.map_mul, ← Matrix.map_mul]
  apply (quotient_matrices_eq_iff 2 _ _).mpr
  simpa only [Matrix.map_mul] using initial_lift_intertwines_mod_four g

theorem initial_lift_not_intertwiner :
    rho generator * initialLift ≠ initialLift * tau generator := by
  intro h
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℤ_[2] => M 0 1) h
  norm_num [rho, tau, initialLift, integerLift, integerRho, signRep, signValue,
    generator, changeCoefficients, Matrix.mul_apply, Fin.sum_univ_succ] at h01

/-- Clearing the averaging denominator gives twice the displayed comparison. -/
theorem integer_averaging_sum :
    (∑ g : C2, integerRho g * integerLift * signRep g⁻¹) =
      (2 : ℤ) • integerComparison := by decide +kernel

/-- The field-valued average is computed explicitly and is integral. -/
theorem rational_average_formula :
    (2 : ℚ_[2])⁻¹ • (∑ g : C2,
      (integerRho g).map (Int.castRingHom ℚ_[2]) *
        integerLift.map (Int.castRingHom ℚ_[2]) *
        (signRep g⁻¹).map (Int.castRingHom ℚ_[2])) =
      integerComparison.map (Int.castRingHom ℚ_[2]) := by
  have hs : (∑ g : C2,
      (integerRho g).map (Int.castRingHom ℚ_[2]) *
        integerLift.map (Int.castRingHom ℚ_[2]) *
        (signRep g⁻¹).map (Int.castRingHom ℚ_[2])) =
      !![(2 : ℚ_[2]), -2; 0, 2] := by
    have h := congrArg (fun M => (Int.castRingHom ℚ_[2]).mapMatrix M) integer_averaging_sum
    rw [map_sum] at h
    simp only [map_mul, RingHom.mapMatrix_apply] at h
    convert h using 1
    ext i j
    fin_cases i <;> fin_cases j <;> norm_num [integerComparison]
  rw [hs]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [integerComparison]

theorem comparison_intertwines (g : C2) :
    rho g * comparison = comparison * tau g := by
  have hi : ∀ g : C2, integerRho g * integerComparison =
      integerComparison * signRep g := by decide +kernel
  have h := congrArg (fun M => (Int.castRingHom ℤ_[2]).mapMatrix M) (hi g)
  change (integerRho g).map (Int.castRingHom ℤ_[2]) *
    integerComparison.map (Int.castRingHom ℤ_[2]) =
    integerComparison.map (Int.castRingHom ℤ_[2]) *
      (signRep g).map (Int.castRingHom ℤ_[2])
  simpa only [map_mul, RingHom.mapMatrix_apply] using h

theorem comparison_det : comparison.det = 1 := by
  norm_num [comparison, integerComparison, Matrix.det_fin_two]

theorem comparison_isUnit : IsUnit comparison := by
  apply (Matrix.isUnit_iff_isUnit_det _).mpr
  rw [comparison_det]
  exact isUnit_one

theorem initial_lift_isUnit : IsUnit initialLift := by
  apply (Matrix.isUnit_iff_isUnit_det _).mpr
  have hd : initialLift.det = 1 := by
    norm_num [initialLift, integerLift, Matrix.det_fin_two]
  rw [hd]
  exact isUnit_one

theorem comparison_preserves_mod_two : comparison.map modTwo = initialLift.map modTwo := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [comparison, initialLift, integerComparison, integerLift, Matrix.map_map]

theorem comparison_changes_mod_four : comparison.map modFour ≠ initialLift.map modFour := by
  intro h
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) (ZMod 4) => M 0 1) h
  norm_num [comparison, initialLift, integerComparison, integerLift, Matrix.map_map] at h01
  exact (by decide : (-1 : ZMod 4) ≠ 1) h01

/-- No exact intertwiner, even a singular one, preserves this full mod-four lift.
The loss of one digit is forced by the example. -/
theorem no_exact_intertwiner_preserves_mod_four :
    ¬ ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[2],
      P.map modFour = initialLift.map modFour ∧
      ∀ g, rho g * P = P * tau g := by
  rintro ⟨P, hred, hP⟩
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℤ_[2] => M 0 1) (hP generator)
  norm_num [rho, tau, integerRho, signRep, signValue, generator,
    changeCoefficients, Matrix.mul_apply, Fin.sum_univ_succ] at h01
  have heq : 2 * (P 0 1 + P 1 1) = 0 := by linear_combination h01
  have hsum : P 0 1 + P 1 1 = 0 := (mul_eq_zero.mp heq).resolve_left (by norm_num)
  have hmod := congrArg modFour hsum
  have hb := congrArg (fun M : Matrix (Fin 2) (Fin 2) (ZMod 4) => M 0 1) hred
  have hd := congrArg (fun M : Matrix (Fin 2) (Fin 2) (ZMod 4) => M 1 1) hred
  norm_num [initialLift, integerLift, Matrix.map_map] at hb hd
  rw [map_add, map_zero, hb, hd] at hmod
  norm_num at hmod
  exact (by decide : (2 : ZMod 4) ≠ 0) hmod

/-- The new precision theorem is instantiated on the prescribed mod-four matrix.
It retains exactly the guaranteed mod-two reduction. -/
theorem actual_two_adic_precision_lift :
    ∃ P : (Matrix (Fin 2) (Fin 2) ℤ_[2])ˣ,
      (P : Matrix (Fin 2) (Fin 2) ℤ_[2]).map (Ideal.Quotient.mk (twoIdeal^1)) =
        initialLift.map (Ideal.Quotient.mk (twoIdeal^1)) ∧
      ∀ g, rho g * (P : Matrix (Fin 2) (Fin 2) ℤ_[2]) =
        (P : Matrix (Fin 2) (Fin 2) ℤ_[2]) * tau g := by
  let f := Ideal.Quotient.mk (twoIdeal^2)
  let B := Units.map f.mapMatrix.toMonoidHom initial_lift_isUnit.unit
  have hBu : (B : Matrix (Fin 2) (Fin 2) (ℤ_[2] ⧸ twoIdeal^2)) = initialLift.map f := by
    change (initial_lift_isUnit.unit : Matrix (Fin 2) (Fin 2) ℤ_[2]).map f = _
    rw [initial_lift_isUnit.unit_spec]
  obtain ⟨P, hP, hi⟩ := PrecisionAveraging.exists_isomorphism_lift (2 : ℤ_[2]) 1 1
    rho tau group_order_nonzero group_order_divides_two
    (by exact group_order_not_unit) (by decide) B (by
      intro g
      rw [hBu]
      exact initial_lift_intertwines_quotient g)
  refine ⟨P, ?_, hi⟩
  rw [hP]
  ext i j
  simp [B, f]

/-- For every pair of these rank-two C2 representations, mod four detects
integral isomorphism. No completeness or finite search is used in this application. -/
theorem two_adic_isomorphism_detected_mod_four
    (σ υ : MatrixRep ℤ_[2] C2 (Fin 2)) :
    Conjugate (reduce twoIdeal υ 2) (reduce twoIdeal σ 2) ↔ Conjugate υ σ := by
  exact PrecisionAveraging.conjugacy_iff_reduction (2 : ℤ_[2]) 1 1 σ υ
    group_order_nonzero group_order_divides_two (by exact group_order_not_unit) (by decide)

theorem twoIdeal_eq_maximal : twoIdeal = IsLocalRing.maximalIdeal ℤ_[2] := by
  exact PadicInt.maximalIdeal_eq_span_p.symm

instance twoAdicComplete : IsAdicComplete twoIdeal ℤ_[2] := by
  rw [twoIdeal_eq_maximal]
  infer_instance

instance twoResidueFinite : Finite (ℤ_[2] ⧸ twoIdeal) := by
  rw [twoIdeal_eq_maximal]
  exact Finite.of_equiv (ZMod 2) (PadicInt.residueField (p := 2)).symm.toEquiv

/-- Concrete framed conditions populated by the displayed integral rho. -/
noncomputable def fixedConditions : Conditions (G := C2) (ι := Fin 2) twoIdeal where
  allowed k σ := σ = reduce twoIdeal rho k
  downward := by
    intro j k hjk σ hσ
    rw [hσ]
    exact transition_reduce twoIdeal rho hjk

/-- The type hypothesis is certified by the approximate lift A modulo four,
without using an already constructed exact comparison. -/
theorem fixed_finite_type : PrecisionCompletion.FiniteType (2 : ℤ_[2])
    fixedConditions 1 tau := by
  intro σ hσ
  change σ = reduce twoIdeal rho 2 at hσ
  subst σ
  let f := Ideal.Quotient.mk (twoIdeal^2)
  let B := Units.map f.mapMatrix.toMonoidHom initial_lift_isUnit.unit
  refine ⟨B, ?_⟩
  intro g
  change (rho g).map f * (initial_lift_isUnit.unit : Matrix (Fin 2) (Fin 2) ℤ_[2]).map f =
    (initial_lift_isUnit.unit : Matrix (Fin 2) (Fin 2) ℤ_[2]).map f * (tau g).map f
  rw [initial_lift_isUnit.unit_spec]
  exact initial_lift_intertwines_quotient g

/-- The new completion theorem constructs a continuous integral realization
with the required integral type. The explicit rho supplies every-level occupancy. -/
theorem actual_two_adic_precision_completion :
    ∃ (σ : MatrixRep ℤ_[2] C2 (Fin 2)) (P : (Matrix (Fin 2) (Fin 2) ℤ_[2])ˣ),
      Realizes twoIdeal fixedConditions σ ∧ AdicRepContinuous twoIdeal σ ∧
      (∀ g, σ g * (P : Matrix (Fin 2) (Fin 2) ℤ_[2]) =
        (P : Matrix (Fin 2) (Fin 2) ℤ_[2]) * tau g) ∧
      Ideal.Quotient.mk (twoIdeal^1) (P : Matrix (Fin 2) (Fin 2) ℤ_[2]).det ≠ 0 := by
  apply PrecisionCompletion.continuous_finite_group_completion (2 : ℤ_[2]) fixedConditions
    1 tau group_order_nonzero group_order_divides_two
    (by exact group_order_not_unit) fixed_finite_type
  · intro k
    exact Ideal.finite_quotient_pow (IsNoetherian.noetherian twoIdeal) k
  · intro k
    exact ⟨reduce twoIdeal rho k, rfl⟩

end PaperX.PrecisionExamples
