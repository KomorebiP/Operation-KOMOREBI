import AVOC.DurableUpgradeRuntime

namespace Komorebi.AVOC.DurableUpgradeExamples

open UpgradeCatalogue DurableUpgrade

def start : Journal Version := DurableUpgrade.initial .dynamic

def bad : Ticket Version := ⟨"bad-001", start.current, badTrial⟩
def afterReserve : Journal Version := ⟨charged (authority 100) bad, some bad, []⟩
def afterBad : Journal Version :=
  ⟨beforeUpgrade, none, [⟨bad, .evaluated .rejected⟩]⟩
def good : Ticket Version := ⟨"good-001", afterBad.current, goodTrial⟩
def final : Journal Version :=
  ⟨afterUpgrade, none,
    [⟨bad, .evaluated .rejected⟩, ⟨good, .evaluated .promoted⟩]⟩

def campaign : List (Command Version) :=
  [.begin bad, .finish bad.key, .begin good, .finish good.key]

theorem reserve_is_paid_not_promoted :
    afterReserve.current.evaluationSpent = 3 ∧
    afterReserve.current.active = .dynamic ∧ afterReserve.current.revision = 0 := by decide

theorem bad_trial_completed :
    (finish (authority 100) afterReserve bad.key).map Reply.journal = .ok afterBad := by decide

theorem full_campaign_replays : replay (authority 100) start campaign = .ok final := by decide

theorem persisted_net_gain : Upgrade.campaignNet (authority 100) final.current = 56 :=
  after_upgrade_net_gain

theorem duplicate_promotion_has_no_debit :
    finish (authority 100) final good.key = .ok (unchanged final) := by decide

theorem exact_request_replay_is_free :
    begin (authority 100) final good = .ok (unchanged final) := by decide

theorem interrupted_evaluation_abandonment_retains_charge :
    let cancelled := ⟨afterReserve.current, none, [⟨bad, .abandoned⟩]⟩
    abandon afterReserve bad.key = .ok ⟨cancelled, true, 0, 0⟩ ∧
    cancelled.current.evaluationSpent = 3 ∧ cancelled.current.active = .dynamic := by decide

theorem omitted_failed_trial_is_rejected :
    replay (authority 100) start [.begin good, .finish good.key] =
      .error "stale complete parent state" := by decide

theorem unchanged_version_does_not_erase_cost :
    afterBad.current.active = start.current.active ∧
    afterBad.current.revision = start.current.revision ∧
    afterBad.current ≠ start.current := by decide

theorem forged_active_checkpoint_rejected :
    restore (authority 100) .dynamic [] final = .error "log/checkpoint mismatch" := by decide

theorem abandoned_result_cannot_promote :
    finish (authority 100)
      ⟨afterReserve.current, none, [⟨bad, .abandoned⟩]⟩ bad.key =
      .ok (unchanged ⟨afterReserve.current, none, [⟨bad, .abandoned⟩]⟩) := by decide

end Komorebi.AVOC.DurableUpgradeExamples
