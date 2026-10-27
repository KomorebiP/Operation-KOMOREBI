import Komorebi.PrecisionModel

set_option autoImplicit false
namespace Komorebi.PosteriorOutput
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior

variable {ι κ υ ω : Type*}

structure Arrays (ι : Type*) where
  mean : ι → Ball
  covariance : BallMatrix ι ι

def outputMean [Fintype κ] [Fintype ι]
    (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : ι → ℚ :=
  M.mean + B *ᵥ M.innovationVector

def outputOperator [Fintype κ] [DecidableEq ι]
    (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : Matrix ι ι ℚ :=
  1 - B * M.observationMatrix

def outputCovariance [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
    [DecidableEq ι] [DecidableEq κ]
    (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : Matrix ι ι ℚ :=
  outputOperator M B * M.prior * (outputOperator M B).transpose +
    B * M.noise * B.transpose

def operatorBall [Fintype κ] [DecidableEq ι]
    (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : BallMatrix ι ι :=
  matrixSub p (matrixInput p 1)
    (matrixMul p (matrixInput p B) (matrixInput p M.observationMatrix))

def operatorBudget [Fintype κ] [DecidableEq ι]
    (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : BudgetMatrix ι ι :=
  budgetAdd (budgetInput 1) (budgetMul (budgetInput B) (budgetInput M.observationMatrix))

theorem operator_bounds [Fintype κ] [DecidableEq ι]
    (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    MatrixBudgetBounds p (operatorBall p M B) (outputOperator M B) (operatorBudget M B) :=
  budgetSub_bounds p (budgetInput_bounds p _)
    (budgetMul_bounds p (budgetInput_bounds p _) (budgetInput_bounds p _))

def meanBall [Fintype ι] [Fintype κ]
    (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : ι → Ball :=
  fun i => rAdd p (rExact p (M.mean i))
    (matrixVector p (matrixInput p B) (innovationVectorBall p M) i)

def meanBudget [Fintype ι] [Fintype κ]
    (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : ι → Budget :=
  fun i => Budget.plus (Budget.input (M.mean i))
    (budgetVector (budgetInput B) (innovationVectorBudget M) i)

theorem mean_bounds [Fintype ι] [Fintype κ]
    (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    VectorBudgetBounds p (meanBall p M B) (outputMean M B) (meanBudget M B) :=
  fun i => Budget.plus_bounds p (Budget.input_bounds p _)
    (budgetVector_bounds p (budgetInput_bounds p _) (innovationVectorBudget_bounds p M) i)

def covarianceBall [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
    [DecidableEq ι] [DecidableEq κ]
    (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : BallMatrix ι ι :=
  matrixAdd p
    (matrixMul p (matrixMul p (operatorBall p M B) (priorBall p M))
      (matrixTranspose (operatorBall p M B)))
    (matrixMul p (matrixMul p (matrixInput p B) (noiseBall p M))
      (matrixTranspose (matrixInput p B)))

def covarianceBudget [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
    [DecidableEq ι] [DecidableEq κ]
    (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : BudgetMatrix ι ι :=
  budgetAdd
    (budgetMul (budgetMul (operatorBudget M B) (priorBudget M))
      (budgetTranspose (operatorBudget M B)))
    (budgetMul (budgetMul (budgetInput B) (noiseBudget M))
      (budgetTranspose (budgetInput B)))

theorem covariance_bounds [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
    [DecidableEq ι] [DecidableEq κ]
    (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    MatrixBudgetBounds p (covarianceBall p M B) (outputCovariance M B)
      (covarianceBudget M B) :=
  budgetAdd_bounds p
    (budgetMul_bounds p (budgetMul_bounds p (operator_bounds p M B) (priorBudget_bounds p M))
      (budgetTranspose_bounds (operator_bounds p M B)))
    (budgetMul_bounds p (budgetMul_bounds p (budgetInput_bounds p _) (noiseBudget_bounds p M))
      (budgetTranspose_bounds (budgetInput_bounds p _)))

def evaluate [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
    [DecidableEq ι] [DecidableEq κ]
    (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : Arrays ι :=
  ⟨meanBall p M B, covarianceBall p M B⟩

def EnclosesParameters [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
    [DecidableEq ι] [DecidableEq κ]
    (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (a : Arrays ι) : Prop :=
  VectorEncloses a.mean (outputMean M B) ∧
    MatrixEncloses a.covariance (outputCovariance M B)

theorem evaluate_encloses [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
    [DecidableEq ι] [DecidableEq κ]
    (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    EnclosesParameters M B (evaluate p M B) :=
  ⟨fun i => (mean_bounds p M B i).2.1,
    fun i j => (covariance_bounds p M B i j).2.1⟩

def OnGrid (a : Arrays ι) (p : ℕ) : Prop :=
  (∀ i, (∃ z : ℤ, (a.mean i).center = (z : ℚ) / scale p) ∧
    (∃ z : ℤ, (a.mean i).radius = (z : ℚ) / scale p)) ∧
  (∀ i j, (∃ z : ℤ, (a.covariance i j).center = (z : ℚ) / scale p) ∧
    (∃ z : ℤ, (a.covariance i j).radius = (z : ℚ) / scale p))

theorem evaluate_grid [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
    [DecidableEq ι] [DecidableEq κ]
    (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    OnGrid (evaluate p M B) p :=
  ⟨fun _ => round_grid p _, fun _ _ => round_grid p _⟩

end Komorebi.PosteriorOutput
