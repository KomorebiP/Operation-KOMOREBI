import MachineTheory.RevisionReplay

/-! # Admission and the initial certificate boundary

A positive local verdict without established parents does not constitute an old proof.
The constructor below derives old establishment in topological order. The finite gate
also checks every unchanged external premise before copying old certificates.
-/
namespace Komorebi.MachineTheory.Dependency
open Finset
variable {V I : Type*} [Fintype V] [DecidableEq V]
variable {A : I → Type*} [∀ i, DecidableEq (A i)] {W : V → Type*}
variable {G : Graph V I} (S : System G A W)

omit [Fintype V] [DecidableEq V] [∀ i, DecidableEq (A i)] in
/-- Establishing an initial snapshot requires sound local rules and grounded parents. -/
theorem System.established_from_checks (rank : V → ℕ) (ordered : G.Ranked rank)
    (a : ∀ i, A i) (old : ∀ v, W v)
    (hc : ∀ v, S.check v (G.view a v) (old v) = true)
    (he : ∀ v, S.external a v) : ∀ v, S.Established a v (old v) := by
  have go : ∀ n v, rank v=n → S.claim a v := by
    intro n
    induction n using Nat.strong_induction_on with
    | h n ih =>
      intro v hn
      apply S.sound a v (old v) (hc v) (he v)
      intro u hu
      exact ih (rank u) (by rw [← hn]; exact ordered v u hu) u rfl
  intro v
  exact ⟨hc v,he v,go (rank v) v rfl⟩

def replayGuard (G : Graph V I) (a b : ∀ i, A i) (external : V → Bool) (rank : V → ℕ) : Bool :=
  decide ((∀ v u, u ∈ G.parents v → rank u < rank v) ∧
    (∀ v, v ∉ G.stale a b → external v = true))

theorem replayGuard_iff (G : Graph V I) (a b : ∀ i, A i) (external : V → Bool) (rank : V → ℕ) :
    replayGuard G a b external rank = true ↔
      G.Ranked rank ∧ (∀ v, v ∉ G.stale a b → external v = true) := by
  simp [replayGuard,Graph.Ranked]

/-- An outer rejection is neither a false-claim verdict nor a completed proof search. -/
def System.checkedFinish (a b : ∀ i, A i) (old : ∀ v, W v)
    (fresh : ∀ v, Option (W v)) (external : V → Bool) (rank : V → ℕ) :
    Option (∀ v, Verdict (W v)) :=
  if replayGuard G a b external rank then some (S.finish a b old fresh external rank) else none

/-- Every certificate returned by an admitted partial replay has its revised meaning. -/
theorem System.admitted_reuse_and_restoration (complete : S.Complete)
    (a b : ∀ i, A i) (old : ∀ v, W v) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (rank : V → ℕ)
    (hold : ∀ v, S.Established a v (old v))
    (he : ∀ v, external v = true → S.external b v)
    (result : ∀ v, Verdict (W v))
    (accepted : S.checkedFinish a b old fresh external rank = some result) :
    S.SoundState b result := by
  unfold checkedFinish at accepted
  split at accepted
  next hg =>
    have heq := Option.some.inj accepted
    subst result
    obtain ⟨hr,hclean⟩ := (replayGuard_iff G a b external rank).mp hg
    exact S.finish_sound complete rank hr a b old fresh external hold
      (fun v hv => he v (hclean v hv)) he
  next => contradiction

omit [∀ i, DecidableEq (A i)] in
/-- A missing parent yields no local certificate even when the local check could pass. -/
theorem System.blocked_parent (b : ∀ i, A i) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (s : ∀ v, Verdict (W v)) (v u : V)
    (hu : u ∈ G.parents v) (hm : (s u).ready = false) :
    S.evaluate b fresh external s v = .blockedParents := by
  have hn : ¬ ∀ z ∈ G.parents v, (s z).ready = true := by
    intro h
    have hh := h u hu
    rw [hm] at hh
    contradiction
  exact ite_eq_right hn

omit [∀ i, DecidableEq (A i)] in
/-- Failure to find a witness is recorded separately from rejection of a supplied witness. -/
theorem System.missing_evidence (b : ∀ i, A i) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (s : ∀ v, Verdict (W v)) (v : V)
    (hp : ∀ u ∈ G.parents v, (s u).ready = true) (he : external v=true)
    (hf : fresh v=none) : S.evaluate b fresh external s v = .missing := by
  unfold evaluate
  rw [ite_eq_left hp,ite_eq_left he,hf]

omit [∀ i, DecidableEq (A i)] in
/-- A rejected local witness supplies no theorem that its intended claim is false. -/
theorem System.rejected_evidence (b : ∀ i, A i) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (s : ∀ v, Verdict (W v)) (v : V) (w : W v)
    (hp : ∀ u ∈ G.parents v, (s u).ready = true) (he : external v=true)
    (hf : fresh v=some w) (hc : S.check v (G.view b v) w = false) :
    S.evaluate b fresh external s v = .rejected := by
  unfold evaluate
  rw [ite_eq_left hp,ite_eq_left he,hf]
  simp only [hc,Bool.false_eq_true,ite_false]

end Komorebi.MachineTheory.Dependency
