import PolynomialSystemTaylor
import Mathlib.LinearAlgebra.Matrix.ToLin
import Mathlib.Tactic.Abel

/-!
# Finite-coordinate polynomial Hensel lifting from a residual matrix right inverse

For a finite polynomial system, the Jacobian matrix varies polynomially with
its base point.  Hence points in one residual fibre have congruent Jacobians.
An entrywise right inverse modulo `pi` therefore remains an approximate right
inverse throughout that fibre.  The v0.19 nonlinear Hensel theorem then gives
an exact solution over a nilpotent thickening.
-/

namespace Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.ScalarPowerDivisibility
open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.VariableJacobianHensel

noncomputable section

variable {R ι κ : Type*} [CommRing R]
  [Fintype ι] [DecidableEq ι]
  [Fintype κ] [DecidableEq κ]

/-- A matrix is entrywise divisible by `pi^n`. -/
def EntrywisePowDivisible (pi : R) (n : ℕ) {m l : Type*}
    (M : Matrix m l R) : Prop :=
  ∀ i j, PowDivisible pi n (M i j)

/-- Finite sums of scalars of one filtration depth remain at that depth. -/
theorem powDivisible_finset_sum {α : Type*} (pi : R) (n : ℕ)
    (s : Finset α) (f : α → R)
    (hf : ∀ a ∈ s, PowDivisible pi n (f a)) :
    PowDivisible pi n (∑ a ∈ s, f a) := by
  classical
  induction s using Finset.induction_on with
  | empty => simp
  | @insert a s ha ih =>
      rw [Finset.sum_insert ha]
      exact (hf a (by simp)).add (ih (fun b hb => hf b (by simp [hb])))

/-- Entrywise divisibility is closed under addition. -/
theorem EntrywisePowDivisible.add {m l : Type*} {pi : R} {n : ℕ}
    {A B : Matrix m l R}
    (hA : EntrywisePowDivisible pi n A)
    (hB : EntrywisePowDivisible pi n B) :
    EntrywisePowDivisible pi n (A + B) := by
  intro i j
  simpa using (hA i j).add (hB i j)

/-- Entrywise divisibility is closed under subtraction. -/
theorem EntrywisePowDivisible.sub {m l : Type*} {pi : R} {n : ℕ}
    {A B : Matrix m l R}
    (hA : EntrywisePowDivisible pi n A)
    (hB : EntrywisePowDivisible pi n B) :
    EntrywisePowDivisible pi n (A - B) := by
  intro i j
  simpa using (hA i j).sub (hB i j)

/-- Multiplication on the right by an arbitrary finite matrix preserves
entrywise filtration depth. -/
theorem EntrywisePowDivisible.mul_right {m l t : Type*} [Fintype l]
    {pi : R} {n : ℕ} {A : Matrix m l R}
    (hA : EntrywisePowDivisible pi n A) (B : Matrix l t R) :
    EntrywisePowDivisible pi n (A * B) := by
  intro i j
  rw [Matrix.mul_apply]
  apply powDivisible_finset_sum pi n Finset.univ
  intro a ha
  exact powDivisible_mul_right (hA i a) (B a j)

/-- Multiplication on the left by an arbitrary finite matrix preserves
entrywise filtration depth on the right factor. -/
theorem EntrywisePowDivisible.mul_left {m l t : Type*} [Fintype l]
    {pi : R} {n : ℕ} (A : Matrix m l R) {B : Matrix l t R}
    (hB : EntrywisePowDivisible pi n B) :
    EntrywisePowDivisible pi n (A * B) := by
  intro i j
  rw [Matrix.mul_apply]
  apply powDivisible_finset_sum pi n Finset.univ
  intro a ha
  exact powDivisible_mul_left (A i a) (hB a j)

/-- Entrywise divisibility of a matrix difference is equivalent to an explicit
`pi`-multiple error matrix at depth one. -/
theorem exists_error_matrix_of_entrywise_depth_one {m l : Type*}
    (pi : R) (A B : Matrix m l R)
    (h : EntrywisePowDivisible pi 1 (A - B)) :
    ∃ E : Matrix m l R, A = B + pi • E := by
  classical
  choose E hE using h
  refine ⟨E, ?_⟩
  ext i j
  have hij : pi * E i j = A i j - B i j := by
    simpa [pow_one, smul_eq_mul, Matrix.sub_apply] using hE i j
  change A i j = B i j + pi * E i j
  rw [hij]
  ring

/-- The Jacobian matrix in the standard coordinate bases. -/
def jacobianMatrix (system : System ι κ R) (x : ι → R) : Matrix κ ι R :=
  (LinearMap.toMatrix (Pi.basisFun R ι) (Pi.basisFun R κ))
    (systemDerivative system x)

omit [DecidableEq κ] in
@[simp] theorem jacobianMatrix_apply
    (system : System ι κ R) (x : ι → R) (j : κ) (i : ι) :
    jacobianMatrix system x j i =
      Expr.deriv (system j) x (Pi.single i 1) := by
  simp [jacobianMatrix, LinearMap.toMatrix_apply, systemDerivative]

/- Polynomial Jacobian matrices at points congruent modulo `pi^n` are
entrywise congruent modulo the same power. -/
omit [DecidableEq κ] in
theorem jacobianMatrix_sub_powDivisible
    (system : System ι κ R) (pi : R) {n : ℕ}
    (x y : ι → R) (hxy : PowDivisible pi n (x - y)) :
    EntrywisePowDivisible pi n
      (jacobianMatrix system x - jacobianMatrix system y) := by
  intro j i
  simp only [Matrix.sub_apply, jacobianMatrix_apply]
  exact Expr.deriv_sub_deriv_powDivisible
    (system j) pi x y (Pi.single i 1) hxy

/-- Convert a coordinate matrix into its standard-basis linear map. -/
def matrixLinear {m l : Type*}
    [Fintype l] [DecidableEq l] [Fintype m] [DecidableEq m]
    (M : Matrix m l R) : (l → R) →ₗ[R] (m → R) :=
  (Matrix.toLin (Pi.basisFun R l) (Pi.basisFun R m)) M

@[simp] theorem toMatrix_matrixLinear {m l : Type*}
    [Fintype l] [DecidableEq l] [Fintype m] [DecidableEq m]
    (M : Matrix m l R) :
    (LinearMap.toMatrix (Pi.basisFun R l) (Pi.basisFun R m))
      (matrixLinear M) = M :=
  LinearMap.toMatrix_toLin _ _ M

@[simp] theorem matrixLinear_toMatrix {m l : Type*}
    [Fintype l] [DecidableEq l] [Fintype m] [DecidableEq m]
    (f : (l → R) →ₗ[R] (m → R)) :
    matrixLinear
      ((LinearMap.toMatrix (Pi.basisFun R l) (Pi.basisFun R m)) f) = f :=
  Matrix.toLin_toMatrix _ _ f

/-- Matrix multiplication agrees with composition in standard coordinates. -/
theorem matrixLinear_mul {l m n : Type*}
    [Fintype n] [DecidableEq n]
    [Fintype m] [DecidableEq m]
    [Fintype l] [DecidableEq l]
    (A : Matrix l m R) (B : Matrix m n R) :
    (matrixLinear A).comp (matrixLinear B) = matrixLinear (A * B) := by
  symm
  exact Matrix.toLin_mul (Pi.basisFun R n) (Pi.basisFun R m)
    (Pi.basisFun R l) A B

@[simp] theorem matrixLinear_one {m : Type*}
    [Fintype m] [DecidableEq m] :
    matrixLinear (1 : Matrix m m R) = LinearMap.id :=
  Matrix.toLin_one (Pi.basisFun R m)

@[simp] theorem matrixLinear_add {m l : Type*}
    [Fintype l] [DecidableEq l] [Fintype m] [DecidableEq m]
    (A B : Matrix m l R) :
    matrixLinear (A + B) = matrixLinear A + matrixLinear B := by
  exact map_add _ A B

@[simp] theorem matrixLinear_smul {m l : Type*}
    [Fintype l] [DecidableEq l] [Fintype m] [DecidableEq m]
    (a : R) (A : Matrix m l R) :
    matrixLinear (a • A) = a • matrixLinear A := by
  exact map_smul _ a A

/-- A base-point right-inverse congruence remains valid throughout the whole
residual fibre of a polynomial system. -/
theorem exists_residualFiber_error_endomorphism
    (pi : R) (system : System ι κ R) (x₀ : ι → R)
    (rightInvMatrix : Matrix ι κ R)
    (hbase : EntrywisePowDivisible pi 1
      (jacobianMatrix system x₀ * rightInvMatrix - 1)) :
    ∃ E : (ι → R) → Module.End R (κ → R),
      ∀ x : ι → R, SameResidual pi x₀ x →
        (systemDerivative system x).comp (matrixLinear rightInvMatrix) =
          LinearMap.id + pi • E x := by
  classical
  have hex : ∀ x : ι → R,
      ∃ Ex : Module.End R (κ → R), SameResidual pi x₀ x →
        (systemDerivative system x).comp (matrixLinear rightInvMatrix) =
          LinearMap.id + pi • Ex := by
    intro x
    by_cases hx : SameResidual pi x₀ x
    · have hJdiff := jacobianMatrix_sub_powDivisible system pi x x₀ hx
      have hprod := hJdiff.mul_right rightInvMatrix
      have htotal : EntrywisePowDivisible pi 1
          (jacobianMatrix system x * rightInvMatrix - 1) := by
        have heq :
            jacobianMatrix system x * rightInvMatrix - 1 =
              (jacobianMatrix system x - jacobianMatrix system x₀) * rightInvMatrix +
                (jacobianMatrix system x₀ * rightInvMatrix - 1) := by
          ext i j
          simp only [Matrix.sub_apply, Matrix.add_apply, Matrix.mul_apply]
          have hsum :
              (∑ a, (jacobianMatrix system x i a -
                    jacobianMatrix system x₀ i a) * rightInvMatrix a j) =
                (∑ a, jacobianMatrix system x i a * rightInvMatrix a j) -
                  (∑ a, jacobianMatrix system x₀ i a * rightInvMatrix a j) := by
            rw [← Finset.sum_sub_distrib]
            apply Finset.sum_congr rfl
            intro a ha
            ring
          rw [hsum]
          ring
        rw [heq]
        exact hprod.add hbase
      obtain ⟨Emat, hEmat⟩ :=
        exists_error_matrix_of_entrywise_depth_one pi
          (jacobianMatrix system x * rightInvMatrix) 1 htotal
      refine ⟨matrixLinear Emat, fun _ => ?_⟩
      calc
        (systemDerivative system x).comp (matrixLinear rightInvMatrix) =
            matrixLinear (jacobianMatrix system x * rightInvMatrix) := by
              rw [← matrixLinear_toMatrix (systemDerivative system x)]
              exact matrixLinear_mul _ _
        _ = matrixLinear (1 + pi • Emat) := by rw [hEmat]
        _ = LinearMap.id + pi • matrixLinear Emat := by simp
    · exact ⟨0, fun hres => (hx hres).elim⟩
  choose E hE using hex
  exact ⟨E, hE⟩

/--
**Finite-coordinate polynomial Hensel theorem.** A polynomial system over a
nilpotent thickening has an exact solution as soon as its residual Jacobian has
an entrywise lifted right inverse modulo `pi` and the base point solves the
system modulo `pi`.
-/
theorem exists_exact_solution_of_residual_matrix_rightInverse
    (pi : R) (system : System ι κ R) (x₀ : ι → R)
    (rightInvMatrix : Matrix ι κ R)
    (hbase : EntrywisePowDivisible pi 1
      (jacobianMatrix system x₀ * rightInvMatrix - 1))
    (hpi : IsNilpotent pi)
    (hx₀ : PowDivisible pi 1 (evalSystem system x₀)) :
    ∃ x : ι → R, SameResidual pi x₀ x ∧ evalSystem system x = 0 := by
  obtain ⟨E, hE⟩ :=
    exists_residualFiber_error_endomorphism pi system x₀ rightInvMatrix hbase
  exact exists_exact_polynomial_system_solution
    pi system (matrixLinear rightInvMatrix) E x₀ hE hpi hx₀

end

end Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel

#print axioms Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel.jacobianMatrix_sub_powDivisible
#print axioms Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel.exists_residualFiber_error_endomorphism
#print axioms Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel.exists_exact_solution_of_residual_matrix_rightInverse
