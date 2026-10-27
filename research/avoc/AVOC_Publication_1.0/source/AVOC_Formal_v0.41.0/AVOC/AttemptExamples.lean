import AVOC.AttemptAccounting

namespace Komorebi.AVOC.AttemptExamples
open Attempts

def lim : Limits := ⟨4,4⟩
def first : Ledger := ⟨1,0,1,some ⟨0,0,1⟩,false,false⟩
def second : Ledger := ⟨2,0,2,some ⟨0,1,1⟩,false,false⟩
def committed : Ledger := ⟨2,0,2,some ⟨0,1,1⟩,true,false⟩
def confirmed : Ledger := ⟨2,1,2,none,false,false⟩

theorem fresh_attempt : reserve lim initial 0 1 = .ok first := by rfl

theorem retry_charged_twice : renew lim first ⟨0,0,1⟩ = .ok second := by rfl

theorem old_attempt_cannot_publish : publish second ⟨0,0,1⟩ = .error "publication refused" := by rfl

theorem new_attempt_can_publish : publish second ⟨0,1,1⟩ = .ok committed := by rfl

theorem successful_retry_only_one_logical_fee : settle committed ⟨0,1,1⟩ = .ok confirmed := by rfl

theorem failed_cost_retained : confirmed.charged = 2 ∧ confirmed.confirmed = 1 := by decide

theorem no_refund_on_terminal_cancel :
    abandon first ⟨0,0,1⟩ = .ok ⟨1,0,1,none,false,true⟩ := by rfl

theorem count_cap_stops_free_retries :
    renew ⟨10,1⟩ ⟨0,0,1,some ⟨0,0,0⟩,false,false⟩ ⟨0,0,0⟩ = .error "retry refused" := by rfl

theorem budget_cap_stops_retry : renew ⟨1,100⟩ first ⟨0,0,1⟩ = .error "retry refused" := by rfl

end Komorebi.AVOC.AttemptExamples
