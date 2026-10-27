import AVOC.AffineReuseCodec
import AVOC.AffineFactorExamples

namespace Komorebi.AVOC.Affine.ReuseExamples

open Factorization FactorExamples Reuse SearchGuard ReuseCodec
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

def saved : Record K 4 4 := ⟨rankOne,rankOneCandidate⟩
def shifted : Signature K 4 4 := {rankOne with offset := ![4,3,2,1]}

theorem unchanged_factors_fail_new_bias : Factorization.check shifted rankOneCandidate = false := by
  decide

theorem retargeted_factors_accept :
    Factorization.check shifted (retarget shifted rankOneCandidate) = true := by decide

theorem shifted_import_exists : ∃ c, importFor shifted saved = some c := by
  apply (importFor_iff _ _).2
  exact ⟨rankOne_valid,rfl⟩

/-- Nonzero FIRST bias must be subtracted; blindly replacing SECOND bias is wrong. -/
def shiftedFirst : Candidate K 4 4 :=
  ⟨1,⟨fun _ _ => 1, ![2]⟩,⟨fun _ _ => 1, ![4,0,1,2]⟩,
    rankOneCandidate.left,rankOneCandidate.right⟩

theorem shifted_first_valid : Factorization.check rankOne shiftedFirst = true := by decide

theorem shifted_first_retarget :
    Factorization.check shifted (retarget shifted shiftedFirst) = true ∧
    (retarget shifted shiftedFirst).second.offset = ![2,1,0,4] := by decide

def changedLinear : Signature K 4 4 := {rankOne with linear := 0}

theorem wrong_linear_cannot_reuse : importFor changedLinear saved = none := by
  apply import_wrong_linear_rejected
  intro h
  have h00 := congrFun (congrFun h (0:Fin 4)) (0:Fin 4)
  norm_num [changedLinear,saved,rankOne] at h00

theorem rank_one_preflight_tariffs :
    preflightCharge rankOneProgram = 16 ∧
    coldMinimum rankOneProgram 1 = 154 ∧ warmMinimum rankOneProgram 1 = 133 := by decide

theorem cheap_cold_skip : worthExploring 10 36 21 154 = false := by decide

theorem same_calls_warm_admissible : worthExploring 10 36 21 133 = true := by decide

/-- A successful optimistic preflight is not a certificate that actual search pays. -/
theorem preflight_does_not_guarantee_profit :
    worthExploring 11 36 21 154 = true ∧
    11*36 < 240 + 11*21 := by decide

theorem rank_one_cold_lifecycle (calls : Nat) :
    240 + calls*21 ≤ calls*36 ↔ 16 ≤ calls := by omega

theorem rank_one_warm_lifecycle (calls : Nat) :
    149 + calls*21 ≤ calls*36 ↔ 10 ≤ calls := by omega

theorem reuse_is_not_free : reuseCharge 4 4 1 = 133 ∧ 0 < reuseCharge 4 4 1 := by decide

theorem identical_linear_does_not_imply_identical_bias : rankOne.linear = shifted.linear ∧
    rankOne.offset ≠ shifted.offset := by decide

end Komorebi.AVOC.Affine.ReuseExamples
