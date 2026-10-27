import PaperX.OrthogonalLifting
import PaperX.SummandExamples

/-! A three-summand example with a nonunit finite-group order.  The actual
carrier is diag(1,sign,1) over Z_2. An integral shear produces a complete
orthogonal family which is equivariant modulo four, but cannot be retained
modulo four by any exact equivariant lift. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.FamilyExamples
open scoped Matrix BigOperators
open PaperX.RepresentationLimits PaperX.CompletionExamples
open PaperX.PrecisionExamples PaperX.OrthogonalProjectors

private theorem modFour_two : modFour (2 : ℤ_[2]) = 2 := by
  rw [show (2 : ℤ_[2]) = 1 + 1 by norm_num, map_add, map_one]
  decide +kernel

def integerCarrier : MatrixRep ℤ C2 (Fin 3) where
  toFun g := !![1, 0, 0; 0, signValue g, 0; 0, 0, 1]
  map_one' := by decide +kernel
  map_mul' := by decide +kernel

def tau3 : MatrixRep ℤ_[2] C2 (Fin 3) :=
  changeCoefficients (Int.castRingHom ℤ_[2]) integerCarrier

theorem tau3_continuous :
    PaperX.RepresentationTopology.AdicRepContinuous twoIdeal tau3 := by
  let : TopologicalSpace ℤ_[2] := twoIdeal.adicTopology
  exact continuous_of_discreteTopology

def integerProjectors (i : Fin 3) : Matrix (Fin 3) (Fin 3) ℤ :=
  ![!![1, -2, 0; 0, 0, 0; 0, 0, 0],
    !![0, 2, 0; 0, 1, 0; 0, 0, 0],
    !![0, 0, 0; 0, 0, 0; 0, 0, 1]] i

def pAdicProjectors (i : Fin 3) : Matrix (Fin 3) (Fin 3) ℤ_[2] :=
  (integerProjectors i).map (Int.castRingHom ℤ_[2])

theorem integer_idempotent : ∀ i : Fin 3,
    integerProjectors i * integerProjectors i = integerProjectors i := by
  decide +kernel

theorem integer_orthogonal : ∀ i j : Fin 3, i ≠ j →
    integerProjectors i * integerProjectors j = 0 := by decide +kernel

theorem integer_total : ∑ i : Fin 3, integerProjectors i = 1 := by decide +kernel

theorem integer_diagonal : ∀ i : Fin 3, integerProjectors i i i = 1 := by decide +kernel

theorem integer_commutes_mod_four : ∀ (g : C2) (i : Fin 3),
    (integerCarrier g).map (Int.castRingHom (ZMod 4)) *
        (integerProjectors i).map (Int.castRingHom (ZMod 4)) =
      (integerProjectors i).map (Int.castRingHom (ZMod 4)) *
        (integerCarrier g).map (Int.castRingHom (ZMod 4)) := by decide +kernel

theorem pAdic_idempotent (i : Fin 3) :
    pAdicProjectors i * pAdicProjectors i = pAdicProjectors i := by
  unfold pAdicProjectors
  rw [← Matrix.map_mul, integer_idempotent]

theorem pAdic_orthogonal (i j : Fin 3) (h : i ≠ j) :
    pAdicProjectors i * pAdicProjectors j = 0 := by
  unfold pAdicProjectors
  rw [← Matrix.map_mul, integer_orthogonal i j h]
  ext a b
  simp only [Matrix.map_apply, Matrix.zero_apply, map_zero]

theorem pAdic_total : ∑ i : Fin 3, pAdicProjectors i = 1 := by
  change ∑ i : Fin 3, (Int.castRingHom ℤ_[2]).mapMatrix (integerProjectors i) = 1
  rw [← map_sum, integer_total, map_one]

theorem pAdic_diagonal (i : Fin 3) : pAdicProjectors i i i = 1 := by
  simp only [pAdicProjectors, Matrix.map_apply, integer_diagonal, map_one]

theorem pAdic_commutes_mod_four (g : C2) (i : Fin 3) :
    (tau3 g).map modFour * (pAdicProjectors i).map modFour =
      (pAdicProjectors i).map modFour * (tau3 g).map modFour := by
  simpa [tau3, pAdicProjectors, changeCoefficients, Matrix.map_map,
    Function.comp_def] using integer_commutes_mod_four g i

/-- The quotient comparison is independent of the matrix rank. -/
theorem quotient_matrices_eq_iff_three (n : ℕ)
    (A B : Matrix (Fin 3) (Fin 3) ℤ_[2]) :
    A.map (Ideal.Quotient.mk (twoIdeal^n)) = B.map (Ideal.Quotient.mk (twoIdeal^n)) ↔
      A.map (PadicInt.toZModPow n) = B.map (PadicInt.toZModPow n) := by
  constructor
  · intro h
    ext i j
    exact (quotient_eq_iff n _ _).mp (congrArg (fun M => M i j) h)
  · intro h
    ext i j
    exact (quotient_eq_iff n _ _).mpr (congrArg (fun M => M i j) h)

theorem pAdic_commutes_quotient (g : C2) (i : Fin 3) :
    (tau3 g).map (Ideal.Quotient.mk (twoIdeal^2)) *
        (pAdicProjectors i).map (Ideal.Quotient.mk (twoIdeal^2)) =
      (pAdicProjectors i).map (Ideal.Quotient.mk (twoIdeal^2)) *
        (tau3 g).map (Ideal.Quotient.mk (twoIdeal^2)) := by
  rw [← Matrix.map_mul, ← Matrix.map_mul]
  apply (quotient_matrices_eq_iff_three 2 _ _).mpr
  simpa only [Matrix.map_mul] using pAdic_commutes_mod_four g i

/-- Three nonzero prescribed orthogonal quotient projectors. -/
def inputFamily : Family (reduce twoIdeal tau3 2) (Fin 3) where
  projector i := {
    matrix := (pAdicProjectors i).map (Ideal.Quotient.mk (twoIdeal^2))
    idempotent := by rw [← Matrix.map_mul, pAdic_idempotent]
    commutes := by intro g; exact pAdic_commutes_quotient g i }
  orthogonal i j hij := by
    change (pAdicProjectors i).map _ * (pAdicProjectors j).map _ = 0
    rw [← Matrix.map_mul, pAdic_orthogonal i j hij]
    ext a b
    simp only [Matrix.map_apply, Matrix.zero_apply, map_zero]
  total := by
    change ∑ i : Fin 3, (Ideal.Quotient.mk (twoIdeal^2)).mapMatrix (pAdicProjectors i) = 1
    rw [← map_sum, pAdic_total, map_one]

/-- Exact equivariance forces the mixed-sign entry to vanish. -/
theorem commuting_upper_right_zero (P : Matrix (Fin 3) (Fin 3) ℤ_[2])
    (hP : ∀ g : C2, tau3 g * P = P * tau3 g) : P 0 1 = 0 := by
  have h01 := congrArg (fun M : Matrix (Fin 3) (Fin 3) ℤ_[2] => M 0 1)
    (hP generator)
  norm_num [tau3, changeCoefficients, integerCarrier, signValue, generator,
    Matrix.mul_apply, Fin.sum_univ_succ] at h01
  have heq : 2 * P 0 1 = 0 := by linear_combination h01
  exact (mul_eq_zero.mp heq).resolve_left (by norm_num)

theorem pAdic_family_not_equivariant :
    ¬ ∀ (g : C2) (i : Fin 3), tau3 g * pAdicProjectors i =
      pAdicProjectors i * tau3 g := by
  intro h
  have hz := commuting_upper_right_zero (pAdicProjectors 1) (fun g => h g 1)
  norm_num [pAdicProjectors, integerProjectors] at hz

/-- Even one of the three prescribed projectors cannot be retained modulo four.
The failure concerns exact equivariance, before asking for orthogonality. -/
theorem no_exact_family_retains_mod_four :
    ¬ ∃ E : Family tau3 (Fin 3), ∀ i : Fin 3,
      (E.projector i).matrix.map modFour = (pAdicProjectors i).map modFour := by
  rintro ⟨E, hE⟩
  have hz := commuting_upper_right_zero (E.projector 1).matrix
    (E.projector 1).commutes
  have h01 := congrArg (fun M : Matrix (Fin 3) (Fin 3) (ZMod 4) => M 0 1) (hE 1)
  norm_num [Matrix.map_apply, pAdicProjectors, integerProjectors, hz, modFour_two] at h01
  exact (by decide : (0 : ZMod 4) ≠ 2) h01

/-- The preserved diagonal witnesses that every output summand is nonzero. -/
theorem nonzero_of_reduction (i : Fin 3) (P : Matrix (Fin 3) (Fin 3) ℤ_[2])
    (hP : P.map (Ideal.Quotient.mk (twoIdeal^1)) =
      (pAdicProjectors i).map (Ideal.Quotient.mk (twoIdeal^1))) : P ≠ 0 := by
  intro hz
  have h := (quotient_matrices_eq_iff_three 1 _ _).mp hP
  have hii := congrArg (fun M : Matrix (Fin 3) (Fin 3) (ZMod (2^1)) => M i i) h
  simp only [Matrix.map_apply, pAdic_diagonal, hz, Matrix.zero_apply, map_zero,
    map_one] at hii
  exact (by decide : (0 : ZMod (2^1)) ≠ 1) hii

/-- The general simultaneous theorem constructs three nonzero exact summands
from this mod-four family while retaining its prescribed mod-two reduction.
The group order is two, so this tests the nonunit-order case and a family with
more than a projector and its complement. -/
theorem actual_three_summand_lift :
    ∃ E : Family tau3 (Fin 3),
      (∀ i : Fin 3, (E.projector i).matrix.map
          (Ideal.Quotient.mk (twoIdeal^1)) =
        (pAdicProjectors i).map (Ideal.Quotient.mk (twoIdeal^1))) ∧
      ∀ i : Fin 3, (E.projector i).matrix ≠ 0 := by
  obtain ⟨E, hE⟩ := OrthogonalLifting.exists_family_lift (2 : ℤ_[2]) 1 1
    (by decide) tau3 group_order_nonzero group_order_divides_two inputFamily
  have hred (i : Fin 3) : (E.projector i).matrix.map
        (Ideal.Quotient.mk (twoIdeal^1)) =
      (pAdicProjectors i).map (Ideal.Quotient.mk (twoIdeal^1)) := by
    rw [hE]
    ext a b
    simp [inputFamily]
  exact ⟨E, hred, fun i => nonzero_of_reduction i _ (hred i)⟩

end PaperX.FamilyExamples
