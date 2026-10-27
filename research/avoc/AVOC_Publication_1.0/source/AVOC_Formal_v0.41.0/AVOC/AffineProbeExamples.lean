import AVOC.AffineProbeCodec

namespace Komorebi.AVOC.Affine.ProbeExamples

open RankProbe SearchGuard Factorization
abbrev F := ZMod 5
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

def corner : MinorTwo 4 4 := ⟨0,1,0,1⟩
def diagonal : Signature F 4 4 := ⟨1, 0⟩
def rankOne : Signature F 4 4 := ⟨fun _ _ => 1, ![1,2,3,4]⟩
def hiddenTwo : Signature F 4 4 :=
  ⟨fun i j => if i=j ∧ (i=1 ∨ i=2) then 1 else 0, 0⟩

theorem diagonal_probe_passes : check2 diagonal.linear corner = true := by decide

theorem diagonal_floor_two :
    (scan diagonal.linear 1 8 [corner]).lower = 2 := by decide

theorem diagonal_probe_cost :
    (scan diagonal.linear 1 8 [corner]).tested = 1 ∧
    (scan diagonal.linear 1 8 [corner]).remaining = 0 := by decide

theorem diagonal_initial_search_passes :
    ProbeCodec.permitted (.atom diagonal) 1000 1 = true := by decide

theorem diagonal_refined_search_denied :
    ProbeCodec.permitted (.atom diagonal) 1000 2 = false := by decide

theorem diagonal_baseline_globally_two_stage_minimal {k : Nat}
    (a : Signature F 4 k) (b : Signature F k 4) (h : compose b a = diagonal) :
    36 ≤ factorCost 4 4 k := by
  have hr := check2_rank_lower diagonal.linear corner diagonal_probe_passes
  exact baseline_le_every_factor (.atom diagonal) 2 hr (by decide) a b h

theorem rank_one_inconclusive_paid :
    (scan rankOne.linear 1 8 [corner]).lower = 1 ∧
    (scan rankOne.linear 1 8 [corner]).tested = 1 ∧
    (scan rankOne.linear 1 8 [corner]).remaining = 0 ∧
    (scan rankOne.linear 1 8 [corner]).witness = none := by decide

theorem rank_one_still_may_pay : ProbeCodec.permitted (.atom rankOne) 1000 1 = true := by decide

theorem insufficient_probe_credit_keeps_floor :
    scan diagonal.linear 1 7 [corner] = ⟨1,0,7,none⟩ := by decide

/-- A zero tested minor does not imply rank <= 1. -/
theorem missed_minor_no_upper_bound :
    check2 hiddenTwo.linear corner = false ∧ 2 ≤ hiddenTwo.linear.rank := by
  constructor
  · decide
  · exact check2_rank_lower hiddenTwo.linear ⟨1,2,1,2⟩ (by decide)

theorem second_probe_finds_hidden_witness :
    (scan hiddenTwo.linear 1 16 [corner,⟨1,2,1,2⟩]).lower = 2 ∧
    (scan hiddenTwo.linear 1 16 [corner,⟨1,2,1,2⟩]).tested = 2 := by decide

theorem duplicated_probe_is_charged :
    (scan rankOne.linear 1 16 [corner,corner]).tested = 2 ∧
    (scan rankOne.linear 1 16 [corner,corner]).remaining = 0 := by decide

/-- Two successful rank-two witnesses do not add to a rank-four certificate. -/
theorem witnesses_combine_by_max_not_sum :
    (scan hiddenTwo.linear 1 16 [⟨1,2,1,2⟩,⟨2,1,1,2⟩]).lower = 2 ∧
    (scan hiddenTwo.linear 1 16 [⟨1,2,1,2⟩,⟨2,1,1,2⟩]).tested = 1 := by decide

end Komorebi.AVOC.Affine.ProbeExamples
