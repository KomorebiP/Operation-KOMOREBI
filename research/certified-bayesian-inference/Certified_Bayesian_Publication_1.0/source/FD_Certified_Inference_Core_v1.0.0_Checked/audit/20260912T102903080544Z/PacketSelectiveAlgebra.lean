import Komorebi.RationalRichardsonGeometry
import Komorebi.PacketEnergyDecomposition

set_option autoImplicit false
namespace Komorebi.AdaptivePosterior
open Matrix Komorebi.ExactPosterior Komorebi.PacketEnergy
variable {ι κ υ ω α : Type*}
variable [Fintype ι] [Fintype κ] [Fintype υ] [Fintype ω] [Fintype α]
variable [DecidableEq ι] [DecidableEq κ] [DecidableEq α]

omit [Fintype υ] [Fintype ω] [DecidableEq κ] in
/-- Complete output packets account for the entire rational residual energy. -/
theorem sum_left_energy (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (F : Matrix ι κ ℚ) : (∑ a, rationalEnergy (Q a * F)) = rationalEnergy F := by
  have h := matrixEnergy_sumOn_left (realPackets Q hQ) Finset.univ (realMatrix F)
  have hc := realPackets_complete Q hQ
  unfold SelfAdjointPackets.Complete at hc
  rw [hc, Matrix.one_mul] at h
  have hh : (rationalEnergy F : ℝ) = ∑ a, (rationalEnergy (Q a * F) : ℝ) := by
    simpa only [realPackets_proj, ← realMatrix_mul, ← rationalEnergy_cast] using h
  exact_mod_cast hh.symm

omit [Fintype α] [DecidableEq ι] [DecidableEq α] in
/-- A single exact-rational output-packet update. -/
def packetStep (M : RationalModel ι κ υ ω) (Q : Matrix ι ι ℚ)
    (B : Matrix ι κ ℚ) : Matrix ι κ ℚ := B + M.solverStep • (Q * M.residual B)

omit [Fintype α] [DecidableEq ι] [DecidableEq α] in
theorem packetStep_residual (M : RationalModel ι κ υ ω) (Q : Matrix ι ι ℚ)
    (B : Matrix ι κ ℚ) :
    M.residual (packetStep M Q B) = M.residual B - M.solverStep • (Q * M.residual B * M.innovation) := by
  simp only [packetStep, RationalModel.residual, Matrix.add_mul, Matrix.smul_mul]
  abel

/-- Unselected output residuals are unchanged, including all their input subpackets. -/
theorem unselected_residual (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (a b : α) (hba : b ≠ a) (B : Matrix ι κ ℚ) :
    Q b * M.residual (packetStep M (Q a) B) = Q b * M.residual B := by
  rw [packetStep_residual]
  simp only [Matrix.mul_sub, Matrix.mul_smul, ← Matrix.mul_assoc,
    hQ.2.2.1 b a hba, Matrix.zero_mul, smul_zero, sub_zero]

/-- The selected residual is the full innovation transition of its previous value. -/
theorem selected_residual (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (a : α) (B : Matrix ι κ ℚ) :
    Q a * M.residual (packetStep M (Q a) B) =
      (Q a * M.residual B) * (1 - M.solverStep • M.innovation) := by
  rw [packetStep_residual]
  simp only [Matrix.mul_sub, Matrix.mul_one, Matrix.mul_smul, ← Matrix.mul_assoc, hQ.2.1 a]

/-- The gain itself changes only in the selected output packet. -/
theorem unselected_gain (M : RationalModel ι κ υ ω)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (a b : α) (hba : b ≠ a) (B : Matrix ι κ ℚ) :
    Q b * packetStep M (Q a) B = Q b * B := by
  simp only [packetStep, Matrix.mul_add, Matrix.mul_smul, ← Matrix.mul_assoc,
    hQ.2.2.1 b a hba, Matrix.zero_mul, smul_zero, add_zero]

omit [Fintype α] [DecidableEq ι] [DecidableEq α] in
/-- Input effects include S*D; no input-block locality is silently assumed. -/
theorem input_packet_effect (M : RationalModel ι κ υ ω)
    (Q : Matrix ι ι ℚ) (D : Matrix κ κ ℚ) (B : Matrix ι κ ℚ) :
    M.residual (packetStep M Q B) * D =
      M.residual B * D - M.solverStep • (Q * M.residual B * M.innovation * D) := by
  rw [packetStep_residual, Matrix.sub_mul, Matrix.smul_mul]

/-- Local contraction yields exact global descent weighted by the chosen packet energy. -/
theorem packetStep_energy_descent (M : RationalModel ι κ υ ω) (hs : 0 < M.noiseFloor)
    (Q : α → Matrix ι ι ℚ) (hQ : RationalPacketsValid Q)
    (a : α) (B : Matrix ι κ ℚ) :
    rationalEnergy (M.residual (packetStep M (Q a) B)) ≤
      rationalEnergy (M.residual B) - (1-M.solverRate)*rationalEnergy (Q a*M.residual B) := by
  let e := fun b => rationalEnergy (Q b * M.residual B)
  have hsel : rationalEnergy (Q a * M.residual (packetStep M (Q a) B)) ≤ M.solverRate * e a := by
    rw [selected_residual M Q hQ]
    exact M.residual_energy_transition hs _
  have hsum : (∑ b, rationalEnergy (Q b*M.residual (packetStep M (Q a) B))) ≤
      ∑ b, (if b = a then M.solverRate*e a else e b) := by
    apply Finset.sum_le_sum
    intro b _
    by_cases hb : b = a
    · subst b; simpa only [ite_true] using hsel
    · rw [ite_eq_right hb, unselected_residual M Q hQ a b hb]
  have hid : (∑ b, (if b = a then M.solverRate*e a else e b)) =
      (∑ b, e b) - (1-M.solverRate)*e a := by
    have hi : (fun b => if b = a then M.solverRate*e a else e b) =
        (fun b => e b + if b = a then (M.solverRate-1)*e a else 0) := by
      funext b
      split_ifs with hb
      · subst b; ring
      · ring
    rw [hi, Finset.sum_add_distrib]
    simp only [Finset.sum_ite_eq', Finset.mem_univ, ite_true]
    ring
  rw [hid, sum_left_energy Q hQ] at hsum
  simpa only [sum_left_energy Q hQ] using hsum

end Komorebi.AdaptivePosterior
