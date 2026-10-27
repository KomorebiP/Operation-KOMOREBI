import MachineTheory.SafeEndingExamples
open Komorebi.MachineTheory.SafeEnding
variable {Z A : Type*} [Fintype Z]
example (M : Model Z A) (x : Z) :
    x ∈ runningRegion M ↔ ∃ P : Policy Z A, SwitchingGuarantee M P x := safe_continuation_iff M x
example (M : Model Z A) (x : Z) :
    x ∈ endingRegion M ↔ ∃ σ : Strategy Z A, EndingGuarantee M σ x := ending_region_iff M x
example (M : Model Z A) {P : Policy Z A} {x : Z}
    (h : SwitchingGuarantee M P x) : x ∈ runningRegion M := switching_mem_running M h
example (M : Model Z A) {x : Z} (hx : x ∈ endingRegion M) :
    endRank M x ≤ Fintype.card Z - M.goal.card := endRank_bound M hx
#check source_core83
#check command_rank_bound
#check command_rank_arrival
#check running_has_infinite_path
#check ending_prefix_extends
#check Examples.winning_policy_need_not_take_minimal_time
