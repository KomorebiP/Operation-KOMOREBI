import Komorebi.AdaptivePacketSolver

set_option autoImplicit false
namespace Komorebi.AdaptivePosterior
open Matrix Komorebi.ExactPosterior
variable {ι κ υ ω α β : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α] [Fintype β]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α] [DecidableEq β]

omit [Fintype β] [DecidableEq β] in
/-- A resolved output packet stays resolved throughout selective iteration. -/
theorem zero_packet_invariant (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (seed : α) (scan : List α) (B : Matrix ι κ ℚ) (a : α)
    (ha : Q a * M.residual B = 0) (n : ℕ) :
    Q a * M.residual (greedyGain M Q seed scan B n) = 0 := by
  induction n with
  | zero => exact ha
  | succ n ih =>
    change Q a * M.residual (packetStep M (Q (selectPacket M Q seed scan (greedyGain M Q seed scan B n))) _) = 0
    by_cases he : a = selectPacket M Q seed scan (greedyGain M Q seed scan B n)
    · rw [← he, selected_residual M Q hQ, ih, Matrix.zero_mul]
    · rw [unselected_residual M Q hQ _ a he, ih]

/-- The executable coverage guard rejects omitted packet labels. -/
theorem solveAdaptive_rejects_incomplete_scan (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (D : β → Matrix κ κ ℚ)
    (seed : α) (scan : List α) (hscan : ¬ ∀ a, a ∈ scan)
    (ε : ℚ) (probes : List ℕ) (B : Matrix ι κ ℚ) :
    solveAdaptive M Q D seed scan ε probes B = none := by
  rw [solveAdaptive, ite_eq_right (fun h => hscan h.2.2)]

end Komorebi.AdaptivePosterior
