import Komorebi.RationalCandidateAcceptance

set_option autoImplicit false
namespace Komorebi.ExactPosterior
open Matrix
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

omit [DecidableEq α] [DecidableEq β] in
/-- Replacing conservative energy majorants by exact energies cannot increase the score. -/
theorem exactCandidate_score_le_valid (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ) (c : RationalCandidate ι κ α β)
    (h : ValidCandidate M Q D c) :
    candidateScore M (exactCandidate M Q D c.gain) ≤ candidateScore M c := by
  have hu : totalUpper (exactCandidate M Q D c.gain) ≤ totalUpper c :=
    Finset.sum_le_sum fun a _ => Finset.sum_le_sum fun b _ => h.2.2.2.1 a b
  have hv : M.noiseFloor+rationalVectorEnergy M.innovationVector ≤
      M.noiseFloor+c.innovationUpper := add_le_add le_rfl h.2.2.2.2
  apply div_le_div_of_nonneg_right _ (sq_nonneg M.noiseFloor)
  exact mul_le_mul hu hv
    (add_nonneg h.1.le (rationalVectorEnergy_nonneg _))
    (valid_totalUpper_nonneg M Q D c h)

end Komorebi.ExactPosterior
