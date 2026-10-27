import Komorebi.PacketCoarsening
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases

noncomputable section
set_option autoImplicit false
namespace Komorebi.PacketEnergy
open Matrix SelfAdjointPackets

/-- A one-packet resolution is complete in every finite dimension. -/
def identityPackets (ι : Type*) [Fintype ι] [DecidableEq ι] : SelfAdjointPackets ι Unit where
  proj _ := 1
  symmetric _ := Matrix.transpose_one
  idempotent _ := Matrix.one_mul 1
  disjoint a b hab := by
    cases a
    cases b
    exact (hab rfl).elim

theorem identityPackets_complete (ι : Type*) [Fintype ι] [DecidableEq ι] :
    (identityPackets ι).Complete := by
  simp [Complete, sumOn, identityPackets]

/-- Rotated real projections, not coordinate selectors. -/
def rotatedProj (a : Fin 2) : Matrix (Fin 2) (Fin 2) ℝ :=
  if a = 0 then !![1/2,1/2;1/2,1/2] else !![1/2,-1/2;-1/2,1/2]

def rotatedPackets : SelfAdjointPackets (Fin 2) (Fin 2) where
  proj := rotatedProj
  symmetric a := by
    ext i j
    fin_cases a <;> fin_cases i <;> fin_cases j <;> norm_num [rotatedProj]
  idempotent a := by
    ext i j
    fin_cases a <;> fin_cases i <;> fin_cases j <;>
      norm_num [rotatedProj, Matrix.mul_apply, Fin.sum_univ_two]
  disjoint a b hab := by
    ext i j
    fin_cases a <;> fin_cases b <;> fin_cases i <;> fin_cases j <;>
      norm_num [rotatedProj, Matrix.mul_apply, Fin.sum_univ_two] at *

theorem rotatedPackets_complete : rotatedPackets.Complete := by
  unfold Complete sumOn
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [rotatedPackets, rotatedProj, Fin.sum_univ_two]

/-- Universal rectangular regression for a non-coordinate output resolution. -/
theorem rotated_rectangular_energy {κ : Type*} [Fintype κ] [DecidableEq κ]
    (A : Matrix (Fin 2) κ ℝ) :
    matrixEnergy A = ∑ a, matrixEnergy (rotatedProj a*A) := by
  have h := matrixEnergy_eq_sum_blocks rotatedPackets (identityPackets κ)
    rotatedPackets_complete (identityPackets_complete κ) A
  simpa [identityPackets, rotatedPackets] using h

def obliqueP : Matrix (Fin 2) (Fin 2) ℝ := !![1,1;0,0]
def obliqueQ : Matrix (Fin 2) (Fin 2) ℝ := !![0,-1;0,1]

/-- Algebraic annihilation and completeness alone do not imply energy additivity. -/
theorem oblique_algebraic_partition :
    obliqueP*obliqueP = obliqueP ∧ obliqueQ*obliqueQ = obliqueQ ∧
    obliqueP*obliqueQ = 0 ∧ obliqueQ*obliqueP = 0 ∧
    obliqueP+obliqueQ = 1 := by
  refine ⟨?_, ?_, ?_, ?_, ?_⟩ <;>
    ext i j <;> fin_cases i <;> fin_cases j <;>
      norm_num [obliqueP, obliqueQ, Matrix.mul_apply, Fin.sum_univ_two]

theorem oblique_energy_not_additive :
    matrixEnergy obliqueP + matrixEnergy obliqueQ = 4 ∧
      matrixEnergy (1 : Matrix (Fin 2) (Fin 2) ℝ) = 2 := by
  norm_num [matrixEnergy, obliqueP, obliqueQ, Fin.sum_univ_two]

/-- Every zero residual has zero energy in every projected corner. -/
theorem zero_residual_packet_energy {ι κ α β : Type*} [Fintype ι] [Fintype κ]
    (E : SelfAdjointPackets ι α) (D : SelfAdjointPackets κ β) (a : α) (b : β) :
    matrixEnergy (E.proj a*(0 : Matrix ι κ ℝ)*D.proj b) = 0 := by
  simp

end Komorebi.PacketEnergy
