import PaperX.PrecisionBoundary

/-! Boundaries for lifting prescribed equivariant projectors.  The first two
examples use the actual continuous sign representation of C2 over Z_2.  The
last example shows why Reynolds averaging alone does not construct a summand. -/
set_option autoImplicit false
namespace PaperX.SummandBoundary
open scoped Matrix BigOperators
open PaperX.RepresentationLimits PaperX.CompletionExamples
open PaperX.PrecisionExamples

private theorem modTwo_two : modTwo (2 : ℤ_[2]) = 0 := by
  rw [show (2 : ℤ_[2]) = 1 + 1 by norm_num, map_add, map_one]
  decide +kernel

private theorem modFour_two : modFour (2 : ℤ_[2]) = 2 := by
  rw [show (2 : ℤ_[2]) = 1 + 1 by norm_num, map_add, map_one]
  decide +kernel

/-- An integral projector whose off-diagonal entry records prescribed precision. -/
noncomputable def skewProjector (b : ℤ_[2]) : Matrix (Fin 2) (Fin 2) ℤ_[2] := !![1, b; 0, 0]

theorem skewProjector_idempotent (b : ℤ_[2]) :
    skewProjector b * skewProjector b = skewProjector b := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [skewProjector, Matrix.mul_apply, Fin.sum_univ_succ]

/-- Any exact endomorphism of the sign carrier has zero upper-right entry. -/
theorem commuting_upper_right_zero (P : Matrix (Fin 2) (Fin 2) ℤ_[2])
    (hP : ∀ g : C2, tau g * P = P * tau g) : P 0 1 = 0 := by
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℤ_[2] => M 0 1)
    (hP generator)
  norm_num [tau, changeCoefficients, signRep, signValue, generator,
    Matrix.mul_apply, Fin.sum_univ_succ] at h01
  have heq : 2 * P 0 1 = 0 := by linear_combination h01
  exact (mul_eq_zero.mp heq).resolve_left (by norm_num)

theorem skew_one_commutes_mod_two (g : C2) :
    (tau g).map modTwo * (skewProjector 1).map modTwo =
      (skewProjector 1).map modTwo * (tau g).map modTwo := by
  have hi : ∀ g : C2,
      (signRep g).map (Int.castRingHom (ZMod 2)) * !![1, 1; 0, 0] =
        !![1, 1; 0, 0] * (signRep g).map (Int.castRingHom (ZMod 2)) := by
    decide +kernel
  have hp : (skewProjector 1).map modTwo = !![(1 : ZMod 2), 1; 0, 0] := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [skewProjector, Matrix.map_apply]
  rw [hp]
  simpa [tau, changeCoefficients, Matrix.map_map, Function.comp_def] using hi g

/-- A residual equivariant projector need not lift, even though the carrier is
an actual continuous representation on a finite free p-adic module. -/
theorem no_exact_endomorphism_retains_skew_one :
    ¬ ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[2],
      P.map modTwo = (skewProjector 1).map modTwo ∧
      ∀ g : C2, tau g * P = P * tau g := by
  rintro ⟨P, hred, hP⟩
  have hz := commuting_upper_right_zero P hP
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) (ZMod 2) => M 0 1) hred
  simp [Matrix.map_apply, skewProjector, hz] at h01

theorem skew_two_commutes_mod_four (g : C2) :
    (tau g).map modFour * (skewProjector 2).map modFour =
      (skewProjector 2).map modFour * (tau g).map modFour := by
  have hi : ∀ g : C2,
      (signRep g).map (Int.castRingHom (ZMod 4)) * !![1, 2; 0, 0] =
        !![1, 2; 0, 0] * (signRep g).map (Int.castRingHom (ZMod 4)) := by
    decide +kernel
  have hp : (skewProjector 2).map modFour = !![(1 : ZMod 4), 2; 0, 0] := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [skewProjector, Matrix.map_apply, modFour_two]
  rw [hp]
  simpa [tau, changeCoefficients, Matrix.map_map, Function.comp_def] using hi g

/-- The one-digit loss is necessary for a prescribed projector, not merely for
a prescribed isomorphism matrix. No exact endomorphism retains this mod-four
matrix, even without imposing idempotence. -/
theorem no_exact_endomorphism_retains_skew_two_mod_four :
    ¬ ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[2],
      P.map modFour = (skewProjector 2).map modFour ∧
      ∀ g : C2, tau g * P = P * tau g := by
  rintro ⟨P, hred, hP⟩
  have hz := commuting_upper_right_zero P hP
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) (ZMod 4) => M 0 1) hred
  norm_num [Matrix.map_apply, skewProjector, hz, modFour_two] at h01
  exact (by decide : (0 : ZMod 4) ≠ 2) h01

theorem diagonal_projector_commutes (g : C2) :
    tau g * skewProjector 0 = skewProjector 0 * tau g := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [tau, changeCoefficients, signRep, skewProjector,
      Matrix.mul_apply, Fin.sum_univ_succ]

/-- The guaranteed lower precision is attainable, by a nonzero proper summand. -/
theorem skew_two_has_exact_projector_mod_two :
    ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[2], P * P = P ∧
      P.map modTwo = (skewProjector 2).map modTwo ∧
      (∀ g : C2, tau g * P = P * tau g) ∧ P ≠ 0 ∧ P ≠ 1 := by
  refine ⟨skewProjector 0, skewProjector_idempotent 0, ?_,
    diagonal_projector_commutes, ?_, ?_⟩
  · ext i j
    fin_cases i <;> fin_cases j <;> norm_num [skewProjector, modTwo_two]
  · intro h
    have h00 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℤ_[2] => M 0 0) h
    norm_num [skewProjector] at h00
  · intro h
    have h11 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℤ_[2] => M 1 1) h
    norm_num [skewProjector] at h11

noncomputable def rationalSign : MatrixRep ℚ C2 (Fin 2) :=
  changeCoefficients (Int.castRingHom ℚ) signRep

def rationalProjector : Matrix (Fin 2) (Fin 2) ℚ := !![1/2, 1/2; 1/2, 1/2]

theorem rational_projector_idempotent :
    rationalProjector * rationalProjector = rationalProjector := by decide +kernel

/-- The Reynolds average is equivariant, but is no longer idempotent. -/
noncomputable def rationalAverage : Matrix (Fin 2) (Fin 2) ℚ :=
  (Fintype.card C2 : ℚ)⁻¹ •
    ∑ g : C2, rationalSign g * rationalProjector * rationalSign g⁻¹

theorem rational_average_formula : rationalAverage = !![1/2, 0; 0, 1/2] := by
  decide +kernel

theorem rational_average_commutes (g : C2) :
    rationalSign g * rationalAverage = rationalAverage * rationalSign g := by
  rw [rational_average_formula]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [rationalSign, changeCoefficients, signRep, Matrix.mul_apply,
      Fin.sum_univ_succ, mul_comm]

theorem rational_average_not_idempotent :
    rationalAverage * rationalAverage ≠ rationalAverage := by
  rw [rational_average_formula]
  decide +kernel

end PaperX.SummandBoundary
