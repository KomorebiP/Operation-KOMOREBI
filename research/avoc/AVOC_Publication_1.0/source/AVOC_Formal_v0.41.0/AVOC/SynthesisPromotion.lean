import AVOC.BoundedSynthesis
import AVOC.DurableUpgradeLaws

namespace Komorebi.AVOC.Synthesis

/-- Fixed semantic target and protected node-visit utility. The replication count
is a declared workload, not an observed speedup or forecast proved by Lean. -/
def authority (reference : Program) (calls credits : Nat) : Upgrade.Authority Program where
  core := "avoc-pure-boolean-synthesis-v1"
  objective := "exact-bool3/eager-nodes;target-and-calls-frozen-in-authority"
  Contract := fun p => Equivalent p reference
  check := fun p => check p reference
  check_sound := fun p h => check_sound p reference h
  utility := fun p => -((calls * nodes p : Nat) : Int)
  lower := fun p => -((calls * nodes p : Nat) : Int)
  upper := fun p => -((calls * nodes p : Nat) : Int)
  bounds_sound := fun _ => ⟨Int.le_refl _, Int.le_refl _⟩
  evaluationCost := fun p => 8 * (nodes reference + nodes p + 1)
  switchCost := fun _ _ => 1
  credits := credits
  margin := 1
  margin_pos := by decide

structure Submission (reference : Program) (calls credits : Nat) where
  journal : DurableUpgrade.Journal Program
  commands : List (DurableUpgrade.Command Program)
  safe : DurableUpgrade.Safe (authority reference calls credits) journal
  replayed : DurableUpgrade.replay (authority reference calls credits)
    (DurableUpgrade.initial reference) commands = .ok journal

/-- Submit a generated program to the EXISTING prepaid durable upgrade gate.
An unfunded submission retains the original component. -/
def submit (r : Program) (calls credit : Nat) (candidate : Program) : Submission r calls credit :=
  let a := authority r calls credit
  let base := DurableUpgrade.initial r
  let hb : DurableUpgrade.Safe a base := DurableUpgrade.initial_safe a r (equivalent_refl r)
  let t : DurableUpgrade.Ticket Program :=
    ⟨"generated-candidate-0", base.current,
      ⟨r, 0, candidate, a.core, a.objective⟩⟩
  match he : DurableUpgrade.begin a base t with
  | .error _ => ⟨base, [], hb, rfl⟩
  | .ok started =>
    let hs := DurableUpgrade.begin_safe a base t started hb he
    match hf : DurableUpgrade.finish a started.journal t.key with
    | .error _ => ⟨started.journal, [.begin t], hs, by
        simp [DurableUpgrade.replay, DurableUpgrade.apply,
          show DurableUpgrade.begin (authority r calls credit) (DurableUpgrade.initial r) t = .ok started from he]⟩
    | .ok finished =>
      ⟨finished.journal, [.begin t, .finish t.key],
        DurableUpgrade.finish_safe a started.journal t.key finished hs hf, by
          simp [DurableUpgrade.replay, DurableUpgrade.apply,
            show DurableUpgrade.begin (authority r calls credit) (DurableUpgrade.initial r) t = .ok started from he,
            show DurableUpgrade.finish (authority r calls credit) started.journal t.key = .ok finished from hf]⟩

theorem submission_contract (r : Program) (calls credit : Nat) (p : Program) :
    Equivalent (submit r calls credit p).journal.current.active r :=
  (submit r calls credit p).safe.1.1

theorem submission_budget (r : Program) (calls credit : Nat) (p : Program) :
    (submit r calls credit p).journal.current.evaluationSpent +
    (submit r calls credit p).journal.current.switchSpent ≤ credit :=
  (submit r calls credit p).safe.1.2.1

theorem submission_replays (r : Program) (calls credit : Nat) (p : Program) :
    DurableUpgrade.replay (authority r calls credit) (DurableUpgrade.initial r)
      (submit r calls credit p).commands = .ok (submit r calls credit p).journal :=
  (submit r calls credit p).replayed

structure Campaign (reference : Program) (calls total : Nat) where
  proposal : SearchResult
  proposal_sound : Equivalent proposal.candidate reference
  search_budget : proposal.generation + proposal.evaluation ≤ total
  accepted : Submission reference calls (total - (proposal.generation + proposal.evaluation))

def campaign (r : Program) (calls total depth limit searchCredit : Nat) : Campaign r calls total :=
  let b := min searchCredit total
  let out := search r depth limit b
  let hb : out.generation + out.evaluation ≤ total :=
    Nat.le_trans (search_safe r depth limit b).2 (Nat.min_le_right _ _)
  ⟨out, (search_safe r depth limit b).1, hb,
    submit r calls (total - (out.generation + out.evaluation)) out.candidate⟩

def Campaign.totalCharge {r : Program} {calls total : Nat} (c : Campaign r calls total) : Nat :=
  c.proposal.generation + c.proposal.evaluation +
  c.accepted.journal.current.evaluationSpent + c.accepted.journal.current.switchSpent

def Campaign.net {r : Program} {calls total : Nat} (c : Campaign r calls total) : Int :=
  (authority r calls total).utility c.accepted.journal.current.active -
  (authority r calls total).utility r - (c.totalCharge : Int)

theorem campaign_total_budget {r : Program} {calls total : Nat} (c : Campaign r calls total) :
    c.totalCharge ≤ total := by
  have hb := c.accepted.safe.1.2.1
  have hg := c.search_budget
  unfold Campaign.totalCharge
  change c.accepted.journal.current.evaluationSpent +
    c.accepted.journal.current.switchSpent ≤ total -
      (c.proposal.generation + c.proposal.evaluation) at hb
  omega

theorem campaign_active_sound {r : Program} {calls total : Nat} (c : Campaign r calls total) :
    Equivalent c.accepted.journal.current.active r := c.accepted.safe.1.1

theorem campaign_net_bound {r : Program} {calls total : Nat} (c : Campaign r calls total)
    (hi : c.accepted.journal.current.initial = r) :
    (c.accepted.journal.current.guaranteedGain : Int) -
      (c.proposal.generation + c.proposal.evaluation +
        c.accepted.journal.current.evaluationSpent : Nat) ≤ c.net := by
  have h := Upgrade.campaign_net_lower_bound _ _ c.accepted.safe.1
  simp only [Upgrade.campaignNet, authority, hi] at h
  simp only [Campaign.net, Campaign.totalCharge, authority, Int.natCast_add]
  omega

/-- Restore a persisted GENERATED-program journal through the same exact replay gate. -/
def restoreGenerated (r : Program) (calls credit : Nat)
    (cmds : List (DurableUpgrade.Command Program)) (actual : DurableUpgrade.Journal Program) :
    Except String (Submission r calls credit) :=
  match h : DurableUpgrade.restore (authority r calls credit) r cmds actual with
  | .error e => .error e
  | .ok out =>
    .ok ⟨out, cmds, DurableUpgrade.restored_certificate _ r (equivalent_refl r) cmds actual out h, by
      unfold DurableUpgrade.restore at h
      split at h
      · cases h
      next j hj =>
        split at h
        · cases h; exact hj
        · cases h⟩

theorem restored_generated_sound (r : Program) (calls credit : Nat)
    (j : Submission r calls credit) (s : Input) :
    (runCount j.journal.current.active s).1 = run r s := by
  rw [runCount_value]
  exact j.safe.1.1 s

end Komorebi.AVOC.Synthesis
