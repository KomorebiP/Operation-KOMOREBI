import Komorebi.HybridPosteriorGuarantee
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
namespace Komorebi.RoundedPosterior
open Matrix Komorebi.ExactPosterior

/-- Zero rounding coefficient is handled by the executable bit predictor. -/
theorem zero_coefficient_precision (δ : ℚ) : precisionFor 0 δ = 1 := by
  simp [precisionFor]

/-- A fixed equality-boundary test cannot replace the strict-slack hypothesis. -/
theorem boundary_source_inflates : (1/3 : ℚ)^2 < energyUpper (rExact 4 (1/3)) := by
  decide +kernel

/-- Negative inputs obey the same magnitude enclosure conventions. -/
theorem negative_source_checked :
    Encloses (rExact 3 (-7/3)) (-7/3) ∧
      (rExact 3 (-7/3)).radius ≤ 2*mesh 3 := by
  exact ⟨rExact_encloses _ _,(Budget.input_bounds _ _).2.2⟩

/-- Empty finite summation has a valid quantified enclosure. -/
theorem empty_sum_checked (p : ℕ) :
    Budget.Bounds p (rSum p (∅ : Finset ℕ) (fun _ => exact 0)) 0
      (Budget.total (∅ : Finset ℕ) (fun _ => Budget.input 0)) := by
  simpa using Budget.total_bounds p (∅ : Finset ℕ) (fun _ => exact 0)
    (fun _ => (0 : ℚ)) (fun _ => Budget.input 0) (by simp)

section
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

/-- The positive-tolerance termination theorem does not silently include zero tolerance. -/
theorem hybrid_rejects_nonpositive_tolerance (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ) (hε : ε ≤ 0)
    (B : Matrix ι κ ℚ) : hybridSolve M Q D ε B = none := by
  simp only [hybridSolve,ite_eq_right (not_lt.mpr hε)]

/-- Successful certification cannot bypass the positive model-floor requirement. -/
theorem hybrid_rejects_nonpositive_floor (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (ε : ℚ) (hs : M.noiseFloor ≤ 0)
    (B : Matrix ι κ ℚ) : hybridSolve M Q D ε B = none := by
  cases hr : hybridSolve M Q D ε B with
  | none => rfl
  | some pair =>
    rcases pair with ⟨p,c⟩
    have hv := (checkCandidate_eq_true M Q D c).mp (hybridSolve_sound M Q D ε B p c hr).1
    exact False.elim ((not_lt.mpr hs) hv.1)

omit [DecidableEq α] [DecidableEq β] in
/-- The quantitative inflation theorem bounds an actual outward score from both sides. -/
theorem rounded_score_sandwich (p : ℕ) (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (B : Matrix ι κ ℚ)
    (hs : 0 < M.noiseFloor) (hQ : RationalPacketsValid Q) (hD : RationalPacketsValid D) :
    candidateScore M (exactCandidate M Q D B) ≤ candidateScore M (roundedCandidate p M Q D B) ∧
    candidateScore M (roundedCandidate p M Q D B) ≤ candidateScore M (exactCandidate M Q D B)+
      scoreRoundCoeff M Q D B*mesh p := by
  constructor
  · have h := exactCandidate_score_le_valid M Q D (roundedCandidate p M Q D B)
      (roundedCandidate_valid p M Q D B hs hQ hD)
    simpa only [roundedCandidate_gain] using h
  · exact rounded_score_inflation p M Q D B hs
end
end Komorebi.RoundedPosterior
