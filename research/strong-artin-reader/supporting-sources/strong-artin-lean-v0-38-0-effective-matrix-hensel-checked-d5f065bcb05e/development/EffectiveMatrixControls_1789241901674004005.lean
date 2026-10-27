import EffectiveMatrixRoot

namespace Komorebi.StrongArtin.MatrixHensel.Controls
noncomputable section
open scoped Matrix.Norms.Elementwise
attribute [local instance] padicMatrixNormedRing padicMatrixUltra

abbrev M2 (R : Type*) := Matrix (Fin 2) (Fin 2) R

def center : M2 (PadicInt 2) := !![1, 1; 0, 1]

def inverseCoefficients : Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) (PadicInt 2) :=
  fun ij kl =>
    (![ ![ !![2, 0; -1, 0], !![-1, 2; 1, -1] ],
        ![ !![0, 0; 2, 0], !![0, 0; -1, 2] ] ] ij.1 ij.2) kl.1 kl.2

theorem square_inverse_certificate :
    InverseCertificate (integralMatrix center) 2 2 inverseCoefficients := by
  intro i j
  constructor <;> ext k l <;> fin_cases i <;> fin_cases j <;> fin_cases k <;> fin_cases l <;>
    norm_num [inverseLinear, coefficientAction, tangent, integralMatrix, center,
      inverseCoefficients, Matrix.mul_apply, Fin.sum_univ_two, Fintype.sum_prod_type,
      Matrix.single_apply] <;> ring

/-- An exact finite test for arbitrary targets, in a genuinely noncommutative residue ball. -/
theorem unipotent_square_iff (U : M2 (PadicInt 2)) :
    (∃! F : M2 (PadicInt 2), F^2 = U ∧
      (PadicInt.toZModPow 3).mapMatrix F = (PadicInt.toZModPow 3).mapMatrix center) ↔
    (PadicInt.toZModPow 5).mapMatrix (integralAction inverseCoefficients (U-center^2)) = 0 :=
  matrix_power_unique_iff center U 2 2 3 (by decide) inverseCoefficients square_inverse_certificate

def noncommutingRoot : M2 (PadicInt 2) := !![1, 1; 8, 1]

theorem root_noncommutes : center * noncommutingRoot ≠ noncommutingRoot * center := by
  intro h
  have hh := congrArg (fun X : M2 (PadicInt 2) => X 0 0) h
  norm_num [center, noncommutingRoot, Matrix.mul_apply, Fin.sum_univ_two] at hh

theorem noncommuting_positive :
    noncommutingRoot^2 = (!![9, 2; 16, 9] : M2 (PadicInt 2)) ∧
    (PadicInt.toZModPow 3).mapMatrix noncommutingRoot =
      (PadicInt.toZModPow 3).mapMatrix center := by
  constructor
  · ext i j
    fin_cases i <;> fin_cases j <;>
      norm_num [noncommutingRoot, pow_two, Matrix.mul_apply, Fin.sum_univ_two]
  · ext i j
    fin_cases i <;> fin_cases j <;>
      norm_num [noncommutingRoot, center, RingHom.mapMatrix_apply, map_ofNat]

end
end Komorebi.StrongArtin.MatrixHensel.Controls
