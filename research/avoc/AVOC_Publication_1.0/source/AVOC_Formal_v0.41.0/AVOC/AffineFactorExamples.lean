import AVOC.AffineFactorCodec
import Mathlib.LinearAlgebra.Matrix.Notation

namespace Komorebi.AVOC.Affine.FactorExamples

open Factorization
abbrev K := ZMod 5
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

def rankOne : Signature K 4 4 := ⟨fun _ _ => 1, ![1,2,3,4]⟩
def rankOneCandidate : Candidate K 4 4 :=
  ⟨1, ⟨fun _ _ => 1, 0⟩, ⟨fun _ _ => 1, ![1,2,3,4]⟩,
    fun _ j => if j = 0 then 1 else 0,
    fun i _ => if i = 0 then 1 else 0⟩

theorem rankOne_check : Factorization.check rankOne rankOneCandidate = true := by decide

theorem rankOne_valid : Valid rankOne rankOneCandidate := (Factorization.check_iff _ _).1 rankOne_check

theorem rankOne_rank : rankOne.linear.rank = 1 := valid_rank_exact rankOne_valid

theorem rankOne_minimum_width {k : Nat} (a : Signature K 4 k) (b : Signature K k 4)
    (h : ∀ x, eval b (eval a x) = eval rankOne x) : 1 ≤ k :=
  width_minimal rankOne_valid a b h

def rankOneProgram : DenseProgram K 4 4 := .atom rankOne
def rankOneChecked : Checked (coefficients rankOneProgram) := ⟨rankOneCandidate,rankOne_valid⟩

theorem rankOne_execution_costs : executionCost rankOneProgram = 36 ∧
    executionCost (plan rankOneCandidate) = 21 ∧
    executionCost (choose rankOneProgram rankOneChecked) = 21 := by decide

theorem rankOne_checker_charge : checkingCharge 4 4 1 = 105 := by decide

theorem rankOne_amortization (calls generation : Nat) :
    campaignCost rankOneProgram rankOneChecked calls generation ≤ 36*calls ↔
    105+generation ≤ 15*calls := by
  have h := amortization_iff rankOneProgram rankOneChecked calls generation
  have hu : upfront rankOneProgram rankOneChecked.candidate.width generation = generation+105 := by
    simp [upfront, rankOneChecked, rankOneCandidate, rankOneProgram,
      normalizationCost, checkingCharge, composeCost, denseCost]
  have hs : costSaving rankOneProgram rankOneChecked = 15 := by
    simp only [costSaving, rankOne_execution_costs.1, rankOne_execution_costs.2.2]
  rw [rankOne_execution_costs.1, hu, hs] at h
  simpa only [Nat.mul_comm, Nat.add_comm] using h

/-- Exact factorization alone does not certify that its width is minimal. -/
def redundantCandidate : Candidate K 4 4 :=
  ⟨2, ⟨fun i _ => if i = 0 then 1 else 0, 0⟩,
    ⟨fun _ j => if j = 0 then 1 else 0, ![1,2,3,4]⟩, 0,0⟩

theorem redundant_is_exact :
    Affine.check (compose redundantCandidate.second redundantCandidate.first) rankOne = true := by
  decide

theorem redundant_lower_rejected : Factorization.check rankOne redundantCandidate = false := by decide

/-- A wrong bias is rejected even when the linear product and rank witness are right. -/
def wrongBias : Candidate K 4 4 :=
  { rankOneCandidate with second := ⟨fun _ _ => 1, 0⟩ }

theorem wrong_bias_rejected : Factorization.check rankOne wrongBias = false := by decide

def idCandidate : Candidate K 2 2 := ⟨2,identity 2,identity 2,1,1⟩
theorem identity_check : Factorization.check (identity (R:=K) 2) idCandidate = true := by decide

def idChecked : Checked (coefficients (Program.ident : DenseProgram K 2 2)) :=
  ⟨idCandidate,(Factorization.check_iff _ _).1 identity_check⟩

theorem identity_keeps_zero_cost :
    executionCost (choose (.ident : DenseProgram K 2 2) idChecked) = 0 := by decide

theorem full_rank_factor_can_lose : factorCost 2 2 2 = 20 ∧ denseCost 2 2 = 10 := by decide

def constant : Signature K 2 3 := ⟨0,![1,2,3]⟩
def constantCandidate : Candidate K 2 3 := ⟨0,⟨0,0⟩,⟨0,![1,2,3]⟩,0,0⟩

theorem constant_check : Factorization.check constant constantCandidate = true := by decide

theorem constant_zero_width : constant.linear.rank = 0 :=
  valid_rank_exact ((Factorization.check_iff _ _).1 constant_check)

theorem constant_costs : factorCost 2 3 0 = 3 ∧ denseCost 2 3 = 15 := by decide

end Komorebi.AVOC.Affine.FactorExamples
