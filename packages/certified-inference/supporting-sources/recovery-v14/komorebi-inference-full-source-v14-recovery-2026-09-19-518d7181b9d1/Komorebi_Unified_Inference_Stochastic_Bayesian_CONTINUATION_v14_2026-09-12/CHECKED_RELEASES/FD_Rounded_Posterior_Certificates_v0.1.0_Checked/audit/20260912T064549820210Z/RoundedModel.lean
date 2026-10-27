import Komorebi.RoundedMatrix
import Komorebi.RationalCertificateChecker

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior
variable {ι κ υ ω : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω]
variable [DecidableEq ι] [DecidableEq κ]

def priorBall (p : ℕ) (M : RationalModel ι κ υ ω) : BallMatrix ι ι :=
  matrixMul p (matrixInput p M.priorFactor) (matrixTranspose (matrixInput p M.priorFactor))
def noiseBall (p : ℕ) (M : RationalModel ι κ υ ω) : BallMatrix κ κ :=
  matrixAdd p
    (matrixMul p (matrixInput p M.noiseFactor) (matrixTranspose (matrixInput p M.noiseFactor)))
    (matrixInput p (M.noiseFloor • (1 : Matrix κ κ ℚ)))
def innovationBall (p : ℕ) (M : RationalModel ι κ υ ω) : BallMatrix κ κ :=
  matrixAdd p
    (matrixMul p (matrixMul p (matrixInput p M.observationMatrix) (priorBall p M))
      (matrixTranspose (matrixInput p M.observationMatrix))) (noiseBall p M)
def residualBall (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) : BallMatrix ι κ :=
  matrixSub p (matrixMul p (priorBall p M) (matrixTranspose (matrixInput p M.observationMatrix)))
    (matrixMul p (matrixInput p B) (innovationBall p M))
def innovationVectorBall (p : ℕ) (M : RationalModel ι κ υ ω) : κ → Ball :=
  vectorSub p (vectorInput p M.observation)
    (matrixVector p (matrixInput p M.observationMatrix) (vectorInput p M.mean))

omit [Fintype ι] [Fintype κ] [Fintype ω] [DecidableEq ι] [DecidableEq κ] in
theorem priorBall_encloses (p : ℕ) (M : RationalModel ι κ υ ω) :
    MatrixEncloses (priorBall p M) M.prior :=
  matrixMul_encloses p (matrixInput_encloses p _) (matrixTranspose_encloses (matrixInput_encloses p _))
omit [Fintype ι] [Fintype κ] [Fintype υ] [DecidableEq ι] in
theorem noiseBall_encloses (p : ℕ) (M : RationalModel ι κ υ ω) :
    MatrixEncloses (noiseBall p M) M.noise :=
  matrixAdd_encloses p
    (matrixMul_encloses p (matrixInput_encloses p _) (matrixTranspose_encloses (matrixInput_encloses p _)))
    (matrixInput_encloses p _)
theorem innovationBall_encloses (p : ℕ) (M : RationalModel ι κ υ ω) :
    MatrixEncloses (innovationBall p M) M.innovation :=
  matrixAdd_encloses p
    (matrixMul_encloses p (matrixMul_encloses p (matrixInput_encloses p _) (priorBall_encloses p M))
      (matrixTranspose_encloses (matrixInput_encloses p _))) (noiseBall_encloses p M)
theorem residualBall_encloses (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ) :
    MatrixEncloses (residualBall p M B) (M.residual B) :=
  matrixSub_encloses p
    (matrixMul_encloses p (priorBall_encloses p M) (matrixTranspose_encloses (matrixInput_encloses p _)))
    (matrixMul_encloses p (matrixInput_encloses p _) (innovationBall_encloses p M))
omit [Fintype κ] [Fintype υ] [Fintype ω] [DecidableEq ι] [DecidableEq κ] in
theorem innovationVectorBall_encloses (p : ℕ) (M : RationalModel ι κ υ ω) :
    VectorEncloses (innovationVectorBall p M) M.innovationVector :=
  vectorSub_encloses p (vectorInput_encloses p _)
    (matrixVector_encloses p (matrixInput_encloses p _) (vectorInput_encloses p _))

def packetBall (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ)
    (Q : Matrix ι ι ℚ) (D : Matrix κ κ ℚ) : BallMatrix ι κ :=
  matrixMul p (matrixMul p (matrixInput p Q) (residualBall p M B)) (matrixInput p D)

theorem packetBall_encloses (p : ℕ) (M : RationalModel ι κ υ ω) (B : Matrix ι κ ℚ)
    (Q : Matrix ι ι ℚ) (D : Matrix κ κ ℚ) :
    MatrixEncloses (packetBall p M B Q D) (Q * M.residual B * D) :=
  matrixMul_encloses p
    (matrixMul_encloses p (matrixInput_encloses p _) (residualBall_encloses p M B))
    (matrixInput_encloses p _)

end Komorebi.RoundedPosterior
