import Mathlib.LinearAlgebra.Matrix.PosDef
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse

noncomputable section
set_option autoImplicit false

namespace Komorebi.FiniteDimensionalGaussianKalman

open Matrix

variable {ι κ : Type*} [Fintype ι] [Fintype κ]

def innovationMatrix (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) : Matrix κ κ ℝ :=
  H * P * H.transpose + R

def gainMatrix [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) : Matrix ι κ ℝ :=
  P * H.transpose * (innovationMatrix H P R)⁻¹

def posteriorCovMatrix [DecidableEq κ]
    (H : Matrix κ ι ℝ) (P : Matrix ι ι ℝ) (R : Matrix κ κ ℝ) : Matrix ι ι ℝ :=
  P - gainMatrix H P R * H * P

end Komorebi.FiniteDimensionalGaussianKalman
