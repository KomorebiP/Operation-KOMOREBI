import Komorebi.PrecisionMatrix
import Komorebi.RoundedModel

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior
variable {ι κ υ ω : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
variable [DecidableEq κ]

def priorBudget (M : RationalModel ι κ υ ω) : BudgetMatrix ι ι :=
  budgetMul (budgetInput M.priorFactor) (budgetTranspose (budgetInput M.priorFactor))
def noiseBudget (M : RationalModel ι κ υ ω) : BudgetMatrix κ κ :=
  budgetAdd
    (budgetMul (budgetInput M.noiseFactor) (budgetTranspose (budgetInput M.noiseFactor)))
    (budgetInput (M.noiseFloor • (1 : Matrix κ κ ℚ)))
def innovationBudget (M : RationalModel ι κ υ ω) : BudgetMatrix κ κ :=
  budgetAdd
    (budgetMul (budgetMul (budgetInput M.observationMatrix) (priorBudget M))
      (budgetTranspose (budgetInput M.observationMatrix))) (noiseBudget M)
def residualBudget (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : BudgetMatrix ι κ :=
  budgetAdd (budgetMul (priorBudget M) (budgetTranspose (budgetInput M.observationMatrix)))
    (budgetMul (budgetInput B) (innovationBudget M))
def innovationVectorBudget (M : RationalModel ι κ υ ω) : κ → Budget :=
  budgetVectorSub (budgetVectorInput M.observation)
    (budgetVector (budgetInput M.observationMatrix) (budgetVectorInput M.mean))

def packetBudget (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ)
    (Q : Matrix ι ι ℚ) (D : Matrix κ κ ℚ) : BudgetMatrix ι κ :=
  budgetMul (budgetMul (budgetInput Q) (residualBudget M B)) (budgetInput D)

omit [Fintype ι] [Fintype κ] [Fintype ω] [DecidableEq κ] in
theorem priorBudget_bounds (p : ℕ) (M : RationalModel ι κ υ ω) :
    MatrixBudgetBounds p (priorBall p M) M.prior (priorBudget M) :=
  budgetMul_bounds p (budgetInput_bounds p _) (budgetTranspose_bounds (budgetInput_bounds p _))
omit [Fintype ι] [Fintype κ] [Fintype υ] in
theorem noiseBudget_bounds (p : ℕ) (M : RationalModel ι κ υ ω) :
    MatrixBudgetBounds p (noiseBall p M) M.noise (noiseBudget M) :=
  budgetAdd_bounds p
    (budgetMul_bounds p (budgetInput_bounds p _) (budgetTranspose_bounds (budgetInput_bounds p _)))
    (budgetInput_bounds p _)
omit [Fintype κ] in
theorem innovationBudget_bounds (p : ℕ) (M : RationalModel ι κ υ ω) :
    MatrixBudgetBounds p (innovationBall p M) M.innovation (innovationBudget M) :=
  budgetAdd_bounds p
    (budgetMul_bounds p (budgetMul_bounds p (budgetInput_bounds p _) (priorBudget_bounds p M))
      (budgetTranspose_bounds (budgetInput_bounds p _))) (noiseBudget_bounds p M)
theorem residualBudget_bounds (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    MatrixBudgetBounds p (residualBall p M B) (M.residual B) (residualBudget M B) :=
  budgetSub_bounds p
    (budgetMul_bounds p (priorBudget_bounds p M) (budgetTranspose_bounds (budgetInput_bounds p _)))
    (budgetMul_bounds p (budgetInput_bounds p _) (innovationBudget_bounds p M))
omit [Fintype κ] [Fintype υ] [Fintype ω] [DecidableEq κ] in
theorem innovationVectorBudget_bounds (p : ℕ) (M : RationalModel ι κ υ ω) :
    VectorBudgetBounds p (innovationVectorBall p M) M.innovationVector (innovationVectorBudget M) :=
  budgetVectorSub_bounds p (budgetVectorInput_bounds p _)
    (budgetVector_bounds p (budgetInput_bounds p _) (budgetVectorInput_bounds p _))

theorem packetBudget_bounds (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ)
    (Q : Matrix ι ι ℚ) (D : Matrix κ κ ℚ) :
    MatrixBudgetBounds p (packetBall p M B Q D) (Q*M.residual B*D) (packetBudget M B Q D) :=
  budgetMul_bounds p
    (budgetMul_bounds p (budgetInput_bounds p _) (residualBudget_bounds p M B))
    (budgetInput_bounds p _)

end Komorebi.RoundedPosterior
