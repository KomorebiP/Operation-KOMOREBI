import ProofPath.Binary

namespace ProofPath.Generated
open Matrix

def one_bit_M : Matrix (Fin 2) (Fin 3) (ZMod 2) := ![![1, 1, 1], ![1, 0, 0]]
def one_bit_b : Fin 2 → ZMod 2 := ![0, 0]
theorem one_bit_positive : ∃ y, one_bit_M.mulVec y = one_bit_b := by
  exact ⟨![0, 0, 0], by decide⟩
theorem one_bit_count : (Finset.univ.filter (fun y : Fin 3 → ZMod 2 =>
    one_bit_M.mulVec y = one_bit_b)).card = 2 := by decide
def one_bit_Q : Matrix (Fin 1) (Fin 3) (ZMod 2) := ![![0, 1, 0]]
theorem one_bit_observations : ((Finset.univ.filter (fun y : Fin 3 → ZMod 2 =>
    one_bit_M.mulVec y = one_bit_b)).image one_bit_Q.mulVec).card = 2 := by decide

def incompatible_M : Matrix (Fin 3) (Fin 3) (ZMod 2) := ![![1, 1, 0], ![1, 0, 0], ![0, 1, 0]]
def incompatible_b : Fin 3 → ZMod 2 := ![0, 0, 1]
def incompatible_w : Fin 3 → ZMod 2 := ![1, 1, 1]
theorem incompatible_negative : ¬ ∃ y, incompatible_M.mulVec y = incompatible_b := by
  exact row_witness_sound incompatible_M incompatible_b incompatible_w (by decide) (by decide)

def redundant_M : Matrix (Fin 2) (Fin 3) (ZMod 2) := ![![1, 1, 0], ![0, 0, 0]]
def redundant_b : Fin 2 → ZMod 2 := ![0, 0]
theorem redundant_positive : ∃ y, redundant_M.mulVec y = redundant_b := by
  exact ⟨![0, 0, 0], by decide⟩
theorem redundant_count : (Finset.univ.filter (fun y : Fin 3 → ZMod 2 =>
    redundant_M.mulVec y = redundant_b)).card = 4 := by decide
def redundant_Q : Matrix (Fin 2) (Fin 3) (ZMod 2) := ![![0, 0, 1], ![0, 0, 1]]
theorem redundant_observations : ((Finset.univ.filter (fun y : Fin 3 → ZMod 2 =>
    redundant_M.mulVec y = redundant_b)).image redundant_Q.mulVec).card = 2 := by decide

def unique_M : Matrix (Fin 4) (Fin 3) (ZMod 2) := ![![1, 0, 0], ![0, 1, 0], ![0, 0, 1], ![0, 0, 0]]
def unique_b : Fin 4 → ZMod 2 := ![0, 0, 0, 0]
theorem unique_positive : ∃ y, unique_M.mulVec y = unique_b := by
  exact ⟨![0, 0, 0], by decide⟩
theorem unique_count : (Finset.univ.filter (fun y : Fin 3 → ZMod 2 =>
    unique_M.mulVec y = unique_b)).card = 1 := by decide
def unique_Q : Matrix (Fin 1) (Fin 3) (ZMod 2) := ![![1, 1, 1]]
theorem unique_observations : ((Finset.univ.filter (fun y : Fin 3 → ZMod 2 =>
    unique_M.mulVec y = unique_b)).image unique_Q.mulVec).card = 1 := by decide

end ProofPath.Generated
