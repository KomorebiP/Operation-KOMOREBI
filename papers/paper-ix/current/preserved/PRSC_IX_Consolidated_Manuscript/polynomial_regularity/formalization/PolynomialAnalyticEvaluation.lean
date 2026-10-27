module
public import PolynomialWeightedInverse
public import Mathlib.Analysis.Analytic.Polynomial
public import Mathlib.Analysis.Analytic.Constructions
public import Mathlib.Analysis.Calculus.FDeriv.Mul
public import Mathlib.Analysis.Calculus.FDeriv.Prod
public import Mathlib.Analysis.Normed.Module.FiniteDimension

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialAnalyticEvaluation
open Matrix
variable {𝕜 : Type*} [NontriviallyNormedField 𝕜] [CompleteSpace 𝕜]
variable {n m : ℕ}

/-- The continuous linear map represented by a finite matrix. -/
def matrixCLM (A : Matrix (Fin m) (Fin n) 𝕜) :
    (Fin n → 𝕜) →L[𝕜] (Fin m → 𝕜) := A.mulVecLin.toContinuousLinearMap

@[simp] theorem matrixCLM_apply (A : Matrix (Fin m) (Fin n) 𝕜) (v : Fin n → 𝕜) :
    matrixCLM A v = A.mulVec v := rfl

/-- Actual evaluation of each polynomial in a system. -/
def evalSystem (F : Fin m → MvPolynomial (Fin n) 𝕜) (a : Fin n → 𝕜) : Fin m → 𝕜 :=
  fun i => MvPolynomial.eval a (F i)

/-- The formal partial derivatives give a continuous linear functional. -/
def polynomialDeriv (P : MvPolynomial (Fin n) 𝕜) (a : Fin n → 𝕜) :
    (Fin n → 𝕜) →L[𝕜] 𝕜 :=
  ∑ j, MvPolynomial.eval a (MvPolynomial.pderiv j P) • ContinuousLinearMap.proj j

omit [CompleteSpace 𝕜] in
@[simp] theorem polynomialDeriv_apply (P : MvPolynomial (Fin n) 𝕜)
    (a v : Fin n → 𝕜) :
    polynomialDeriv P a v = ∑ j, MvPolynomial.eval a (MvPolynomial.pderiv j P) * v j := by
  simp [polynomialDeriv]

omit [CompleteSpace 𝕜] in
/-- Polynomial evaluation has strict derivative equal to its actual formal gradient. -/
theorem hasStrictFDerivAt_eval (P : MvPolynomial (Fin n) 𝕜) (a : Fin n → 𝕜) :
    HasStrictFDerivAt (fun x => MvPolynomial.eval x P) (polynomialDeriv P a) a := by
  induction P using MvPolynomial.induction_on with
  | C c =>
      have hder : polynomialDeriv (MvPolynomial.C c) a = 0 := by
        ext v
        simp
      rw [hder]
      convert! (hasStrictFDerivAt_const (𝕜 := 𝕜) c a) using 1; ext x; simp
  | add P Q hP hQ =>
      have hder : polynomialDeriv (P + Q) a = polynomialDeriv P a + polynomialDeriv Q a := by
        ext v
        simp [Finset.sum_add_distrib, add_mul]
      rw [hder]
      convert! hP.add hQ using 1; ext x; simp
  | mul_X P j hP =>
      have hder : polynomialDeriv (P * MvPolynomial.X j) a =
          MvPolynomial.eval a P • ContinuousLinearMap.proj j + a j • polynomialDeriv P a := by
        ext v
        simp [MvPolynomial.pderiv_X, Pi.single_apply, apply_ite, Finset.sum_add_distrib,
          mul_add, Finset.mul_sum, mul_left_comm, mul_comm]
      rw [hder]
      convert! hP.mul (hasStrictFDerivAt_apply j a) using 1; ext x; simp

/-- Actual finite polynomial systems are analytic at every point. -/
theorem analyticAt_evalSystem (F : Fin m → MvPolynomial (Fin n) 𝕜) (a : Fin n → 𝕜) :
    AnalyticAt 𝕜 (evalSystem F) a := by
  exact AnalyticAt.pi fun i => AnalyticOnNhd.eval_mvPolynomial (F i) a (Set.mem_univ a)

/-- Actual finite polynomial systems are analytic on the whole ambient space. -/
theorem analyticOnNhd_evalSystem (F : Fin m → MvPolynomial (Fin n) 𝕜) :
    AnalyticOnNhd 𝕜 (evalSystem F) Set.univ := fun a _ => analyticAt_evalSystem F a

/-- The derivative matrix is exactly the evaluated formal Jacobian, with no derivative hypothesis. -/
theorem hasStrictFDerivAt_evalSystem (F : Fin m → MvPolynomial (Fin n) 𝕜)
    (a : Fin n → 𝕜) :
    HasStrictFDerivAt (evalSystem F) (matrixCLM (PolynomialWeightedInverse.jacobian F a)) a := by
  have h := hasStrictFDerivAt_pi.mpr (fun i => hasStrictFDerivAt_eval (F i) a)
  have hder : ContinuousLinearMap.pi (fun i => polynomialDeriv (F i) a) =
      matrixCLM (PolynomialWeightedInverse.jacobian F a) := by
    ext v i
    simp [PolynomialWeightedInverse.jacobian, Matrix.mulVec, dotProduct]
  rw [← hder]
  convert! h using 1

end Komorebi.PolynomialAnalyticEvaluation
