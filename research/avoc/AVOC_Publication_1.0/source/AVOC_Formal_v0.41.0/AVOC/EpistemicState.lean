import AVOC.State
import Mathlib.Data.Finset.Union

namespace Komorebi.AVOC

universe u

/-- A minimal epistemic ledger separates the proposal pool from the evidence
status function.  Proposal generation may enlarge `candidates`; it cannot edit
`status` by construction. -/
structure EpistemicLedger (Claim : Type u) [DecidableEq Claim] where
  candidates : Finset Claim
  status : Claim → ClaimStatus

/-- Proposal-only transition: add candidates while preserving all evidence
statuses. -/
def propose
    {Claim : Type u} [DecidableEq Claim]
    (s : EpistemicLedger Claim) (newCandidates : Finset Claim) : EpistemicLedger Claim :=
  { candidates := s.candidates ∪ newCandidates
    status := s.status }

/-- A proposal-only transition leaves every claim's evidence status unchanged. -/
theorem propose_status_eq
    {Claim : Type u} [DecidableEq Claim]
    (s : EpistemicLedger Claim) (newCandidates : Finset Claim) (c : Claim) :
    (propose s newCandidates).status c = s.status c := by
  rfl

/-- Proposal generation is monotone on the candidate pool. -/
theorem candidates_subset_propose
    {Claim : Type u} [DecidableEq Claim]
    (s : EpistemicLedger Claim) (newCandidates : Finset Claim) :
    s.candidates ⊆ (propose s newCandidates).candidates := by
  intro c hc
  simp [propose, hc]

/-- Apply a finite sequence of proposal batches. -/
def proposeMany
    {Claim : Type u} [DecidableEq Claim] :
    EpistemicLedger Claim → List (Finset Claim) → EpistemicLedger Claim
  | s, [] => s
  | s, batch :: rest => proposeMany (propose s batch) rest

/-- No-silent-promotion invariant: arbitrarily many proposal-only steps leave
all evidence statuses exactly unchanged. -/
theorem proposeMany_status_eq
    {Claim : Type u} [DecidableEq Claim]
    (s : EpistemicLedger Claim) (batches : List (Finset Claim)) (c : Claim) :
    (proposeMany s batches).status c = s.status c := by
  induction batches generalizing s with
  | nil => rfl
  | cons batch rest ih =>
      simpa [proposeMany, propose] using ih (propose s batch)

/-- Consequently proposal-only transitions cannot make a claim cross any
fixed evidence threshold. -/
theorem proposeMany_preserves_threshold
    {Claim : Type u} [DecidableEq Claim]
    (s : EpistemicLedger Claim) (batches : List (Finset Claim))
    (c : Claim) (threshold : ClaimStatus) :
    ((proposeMany s batches).status c).AtLeast threshold ↔
      (s.status c).AtLeast threshold := by
  rw [proposeMany_status_eq]

/-- If proposal-only work begins below an evidence threshold, it remains below
that threshold after any number of proposal batches. -/
theorem proposal_only_cannot_upgrade_to_threshold
    {Claim : Type u} [DecidableEq Claim]
    (s : EpistemicLedger Claim) (batches : List (Finset Claim))
    (c : Claim) (threshold : ClaimStatus)
    (hbelow : ¬ (s.status c).AtLeast threshold) :
    ¬ ((proposeMany s batches).status c).AtLeast threshold := by
  intro h
  exact hbelow ((proposeMany_preserves_threshold s batches c threshold).1 h)

end Komorebi.AVOC
