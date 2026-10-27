import Komorebi.PrecisionModel
import Komorebi.PrecisionScoreAlgebra
import Komorebi.RoundedCandidate

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq κ]

def residualRoundCoeff (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) : ℚ :=
  ∑ a, ∑ b, matrixEnergyCoeff (packetBudget M B (Q a) (D b))
def residualEnergyMagnitude (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) : ℚ :=
  ∑ a, ∑ b, matrixEnergyMag (packetBudget M B (Q a) (D b))

/-- A precision-independent, directly computable upper-inflation coefficient. -/
def scoreRoundCoeff (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) : ℚ :=
  let a := residualRoundCoeff M Q D B
  let b := vectorEnergyCoeff (innovationVectorBudget M)
  let m := residualEnergyMagnitude M Q D B
  let n := vectorEnergyMag (innovationVectorBudget M)
  (a*(M.noiseFloor+n)+m*b+a*b)/M.noiseFloor^2

theorem residualRoundCoeff_nonneg (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) :
    0 ≤ residualRoundCoeff M Q D B :=
  Finset.sum_nonneg fun a _ => Finset.sum_nonneg fun b _ => matrixEnergyCoeff_nonneg (packetBudget M B (Q a) (D b))

theorem residualEnergyMagnitude_nonneg (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) :
    0 ≤ residualEnergyMagnitude M Q D B :=
  Finset.sum_nonneg fun a _ => Finset.sum_nonneg fun b _ => matrixEnergyMag_nonneg (packetBudget M B (Q a) (D b))

theorem scoreRoundCoeff_nonneg (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 ≤ M.noiseFloor) : 0 ≤ scoreRoundCoeff M Q D B := by
  have ha := residualRoundCoeff_nonneg M Q D B
  have hb := vectorEnergyCoeff_nonneg (innovationVectorBudget M)
  have hm := residualEnergyMagnitude_nonneg M Q D B
  have hn := vectorEnergyMag_nonneg (innovationVectorBudget M)
  dsimp only [scoreRoundCoeff]
  positivity

/-- Summed endpoint-energy inflation for the actual rounded packet graph. -/
theorem rounded_total_inflation (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) :
    totalUpper (roundedCandidate p M Q D B) ≤ totalUpper (exactCandidate M Q D B) +
      residualRoundCoeff M Q D B*mesh p := by
  have hh := Finset.sum_le_sum fun a (_ : a ∈ Finset.univ) =>
    Finset.sum_le_sum fun b (_ : b ∈ Finset.univ) =>
      matrixEnergy_inflation (packetBudget_bounds p M B (Q a) (D b))
  simpa only [totalUpper,roundedCandidate,exactCandidate,residualRoundCoeff,
    Finset.sum_add_distrib,Finset.sum_mul] using hh

theorem exact_total_le_magnitude (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ) :
    totalUpper (exactCandidate M Q D B) ≤ residualEnergyMagnitude M Q D B :=
  Finset.sum_le_sum fun a _ => Finset.sum_le_sum fun b _ =>
    matrixExactEnergy_le_mag (packetBudget_bounds 0 M B (Q a) (D b))

/-- Quantitative sufficiency: the entire score inflation is bounded by C*2^(-p).
The exact geometry is not needed for this arithmetic estimate. -/
theorem rounded_score_inflation (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) :
    candidateScore M (roundedCandidate p M Q D B) ≤
      candidateScore M (exactCandidate M Q D B) + scoreRoundCoeff M Q D B*mesh p := by
  apply score_inflation_algebra M.noiseFloor
    (totalUpper (exactCandidate M Q D B)) (rationalVectorEnergy M.innovationVector)
    (totalUpper (roundedCandidate p M Q D B)) (vectorEnergyUpper (innovationVectorBall p M))
    (residualRoundCoeff M Q D B) (vectorEnergyCoeff (innovationVectorBudget M))
    (residualEnergyMagnitude M Q D B) (vectorEnergyMag (innovationVectorBudget M)) (mesh p)
    hs
  · exact Finset.sum_nonneg fun a _ => Finset.sum_nonneg fun b _ => rationalEnergy_nonneg (Q a * M.residual B * D b)
  · exact (rationalVectorEnergy_nonneg _).trans
      (vectorEnergyUpper_sound (innovationVectorBall_encloses p M))
  · exact residualRoundCoeff_nonneg M Q D B
  · exact vectorEnergyCoeff_nonneg (innovationVectorBudget M)
  · exact exact_total_le_magnitude M Q D B
  · exact vectorExactEnergy_le_mag (innovationVectorBudget_bounds p M)
  · exact (mesh_pos p).le
  · exact mesh_le_one p
  · exact rounded_total_inflation p M Q D B
  · exact vectorEnergy_inflation (innovationVectorBudget_bounds p M)

end Komorebi.RoundedPosterior
