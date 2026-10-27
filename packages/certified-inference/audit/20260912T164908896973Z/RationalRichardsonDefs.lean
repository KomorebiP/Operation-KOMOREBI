import Komorebi.RationalCertificateChecker
import Komorebi.RichardsonIteration
import Komorebi.GeometricFuel

set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix Komorebi.GainSolver
variable {ι κ υ ω : Type*} [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
variable [DecidableEq κ]
namespace RationalModel

/-- Rational trace cap avoids a numerical eigenvalue computation and covers empty spaces. -/
def spectralCap (M : RationalModel ι κ υ ω) : ℚ := M.noiseFloor + M.innovation.trace

def solverStep (M : RationalModel ι κ υ ω) : ℚ := M.spectralCap⁻¹

/-- Contraction factor for the Frobenius norm. Its square bounds energy. -/
def solverRho (M : RationalModel ι κ υ ω) : ℚ := 1-M.noiseFloor/M.spectralCap

def solverRate (M : RationalModel ι κ υ ω) : ℚ := M.solverRho^2

/-- Fully executable exact-rational solver from any initial gain. -/
def solverGain (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (n : ℕ) : Matrix ι κ ℚ :=
  gainIter (M.prior*M.observationMatrix.transpose) M.innovation M.solverStep B n

/-- Resolution-independent score when all packet energies are computed exactly. -/
def residualScore (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : ℚ :=
  rationalEnergy (M.residual B) * (M.noiseFloor+rationalVectorEnergy M.innovationVector) /
    M.noiseFloor^2

/-- Explicit conservative iteration budget. Positive tolerance is required by its theorem. -/
def solverFuel (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (ε : ℚ) : ℕ :=
  toleranceFuel M.solverRate (M.residualScore B) ε

@[simp] theorem solverGain_zero (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    M.solverGain B 0 = B := rfl

@[simp] theorem solverGain_succ (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (n : ℕ) :
    M.solverGain B (n+1) = M.solverGain B n + M.solverStep • M.residual (M.solverGain B n) := rfl

/-- The exact recurrence is now attached to the represented Gaussian model. -/
theorem solver_residual_succ (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (n : ℕ) :
    M.residual (M.solverGain B (n+1)) =
      M.residual (M.solverGain B n) * (1-M.solverStep • M.innovation) := by
  exact residual_gainStep _ _ _ _

/-- Fixed points are preserved, rather than requiring a positive tolerance to recognize them. -/
theorem solverGain_of_residual_zero (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ)
    (h : M.residual B = 0) (n : ℕ) : M.solverGain B n = B :=
  gainIter_of_zero_residual _ _ _ _ h n
theorem solverGain_shift (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) (n : ℕ) :
    M.solverGain (B+M.solverStep • M.residual B) n = M.solverGain B (n+1) :=
  gainIter_shift _ _ _ _ n
end RationalModel
end Komorebi.ExactPosterior
