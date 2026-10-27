import MachineTheory.Revision
import Mathlib.Data.Finset.Lattice.Fold

/-! # Finite selective rechecking

One fixed revised artifact snapshot is used for an entire replay. Unaffected witnesses
are copied. Affected vertices are checked in certified rank layers. Missing evidence,
failed local checks and unavailable parents/external premises are not falsehood proofs.
-/
namespace Komorebi.MachineTheory.Dependency
open Finset

inductive Verdict (W : Type*) where
  | pending
  | missing
  | rejected
  | blockedParents
  | blockedExternal
  | reused (w : W)
  | rechecked (w : W)
  deriving DecidableEq, Repr

def Verdict.witness? {W : Type*} : Verdict W → Option W
  | .reused w | .rechecked w => some w
  | _ => none

def Verdict.ready {W : Type*} (s : Verdict W) : Bool := s.witness?.isSome

theorem Verdict.ready_iff {W : Type*} (s : Verdict W) :
    s.ready = true ↔ ∃ w, s.witness? = some w := by
  cases s <;> simp [ready,witness?]

variable {V I : Type*} [Fintype V] [DecidableEq V]
variable {A : I → Type*} [∀ i, DecidableEq (A i)] {W : V → Type*}
variable {G : Graph V I} (S : System G A W)

def System.SoundState (a : ∀ i, A i) (s : ∀ v, Verdict (W v)) : Prop :=
  ∀ v w, (s v).witness? = some w → S.Established a v w

def initialState (G : Graph V I) (a b : ∀ i, A i) (old : ∀ v, W v) :
    ∀ v, Verdict (W v) := fun v =>
  if v ∈ G.stale a b then .pending else .reused (old v)

/-- No evaluator or premise is silently supplied by the witness under test. -/
def System.evaluate (b : ∀ i, A i) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (s : ∀ v, Verdict (W v)) (v : V) : Verdict (W v) :=
  if (∀ u ∈ G.parents v, (s u).ready = true) then
    if external v then
      match fresh v with
      | none => .missing
      | some w => if S.check v (G.view b v) w then .rechecked w else .rejected
    else .blockedExternal
  else .blockedParents

/-- Only affected vertices in the current rank layer incur a new local check. -/
def System.layer (a b : ∀ i, A i) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (rank : V → ℕ) (k : ℕ)
    (s : ∀ v, Verdict (W v)) : ∀ v, Verdict (W v) := fun v =>
  if rank v = k ∧ v ∈ G.stale a b then S.evaluate b fresh external s v else s v

def System.replay (S : System G A W) (a b : ∀ i, A i) (old : ∀ v, W v) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (rank : V → ℕ) : ℕ → (∀ v, Verdict (W v))
  | 0 => initialState G a b old
  | k+1 => S.layer a b fresh external rank k (S.replay a b old fresh external rank k)

def finishAt (rank : V → ℕ) : ℕ := univ.sup rank + 1

def System.finish (a b : ∀ i, A i) (old : ∀ v, W v) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (rank : V → ℕ) : ∀ v, Verdict (W v) :=
  S.replay a b old fresh external rank (finishAt rank)

omit [Fintype V] [DecidableEq V] [∀ i, DecidableEq (A i)] in
/-- A sound ready entry provides the premise to its dependents. -/
theorem System.claim_of_ready (b : ∀ i, A i) (s : ∀ v, Verdict (W v))
    (hs : S.SoundState b s) {v : V} (hv : (s v).ready = true) : S.claim b v := by
  obtain ⟨w,hw⟩ := (Verdict.ready_iff (s v)).mp hv
  exact (hs v w hw).2.2

omit [∀ i, DecidableEq (A i)] in
theorem System.evaluate_sound (b : ∀ i, A i) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (s : ∀ v, Verdict (W v))
    (hs : S.SoundState b s) (he : ∀ v, external v = true → S.external b v) :
    ∀ v w, (S.evaluate b fresh external s v).witness? = some w → S.Established b v w := by
  intro v w hw
  unfold evaluate at hw
  split at hw
  next hp =>
    split at hw
    next hex =>
      cases hf : fresh v with
      | none => simp [hf,Verdict.witness?] at hw
      | some w' =>
        simp only [hf] at hw
        split at hw
        next hc =>
          have heq : w'=w := Option.some.inj hw
          subst w'
          apply S.restore b v w hc (he v hex)
          intro u hu
          exact S.claim_of_ready b s hs (hp u hu)
        next => simp [Verdict.witness?] at hw
    next => simp [Verdict.witness?] at hw
  next => simp [Verdict.witness?] at hw

omit [∀ i, DecidableEq (A i)] in
/-- Failed availability tests cannot create certificates. -/
theorem System.evaluate_ready_iff (b : ∀ i, A i) (fresh : ∀ v, Option (W v))
    (external : V → Bool) (s : ∀ v, Verdict (W v)) (v : V) :
    (S.evaluate b fresh external s v).ready = true ↔
      (∀ u ∈ G.parents v, (s u).ready = true) ∧ external v = true ∧
        ∃ w, fresh v = some w ∧ S.check v (G.view b v) w = true := by
  constructor
  · intro hr
    unfold evaluate at hr
    split at hr
    next hp =>
      split at hr
      next he =>
        cases hf : fresh v with
        | none => simp [hf,Verdict.ready,Verdict.witness?] at hr
        | some w =>
          simp only [hf] at hr
          split at hr
          next hc => exact ⟨hp,he,⟨w,rfl,hc⟩⟩
          next => simp [Verdict.ready,Verdict.witness?] at hr
      next => simp [Verdict.ready,Verdict.witness?] at hr
    next => simp [Verdict.ready,Verdict.witness?] at hr
  · rintro ⟨hp,he,w,hf,hc⟩
    unfold evaluate
    rw [ite_eq_left hp,ite_eq_left he,hf]
    change (if S.check v (G.view b v) w = true then Verdict.rechecked w else Verdict.rejected).ready = true
    rw [ite_eq_left hc]
    rfl

/-- The original witness is copied literally outside the affected closure. -/
theorem System.replay_unaffected (a b : ∀ i, A i) (old : ∀ v, W v)
    (fresh : ∀ v, Option (W v)) (external : V → Bool) (rank : V → ℕ)
    (n : ℕ) (v : V) (hv : v ∉ G.stale a b) :
    S.replay a b old fresh external rank n v = .reused (old v) := by
  induction n with
  | zero => simp [replay,initialState,hv]
  | succ n ih => simp [replay,layer,hv,ih]

/-- Soundness holds at every intermediate replay state, including partial failures. -/
theorem System.replay_sound (complete : S.Complete) (rank : V → ℕ) (ordered : G.Ranked rank)
    (a b : ∀ i, A i) (old : ∀ v, W v) (fresh : ∀ v, Option (W v)) (external : V → Bool)
    (hold : ∀ v, S.Established a v (old v))
    (hclean : ∀ v, v ∉ G.stale a b → S.external b v)
    (he : ∀ v, external v = true → S.external b v) (n : ℕ) :
    S.SoundState b (S.replay a b old fresh external rank n) := by
  induction n with
  | zero =>
    intro v w hw
    change (initialState G a b old v).witness? = some w at hw
    by_cases hv : v ∈ G.stale a b
    · simp [initialState,hv,Verdict.witness?] at hw
    · have heq : old v = w := by simpa [initialState,hv,Verdict.witness?] using hw
      subst w
      exact S.selective_reuse complete rank ordered a b old hold hclean v hv
  | succ n ih =>
    intro v w hw
    change (S.layer a b fresh external rank n (S.replay a b old fresh external rank n) v).witness? = some w at hw
    unfold layer at hw
    split at hw
    · exact S.evaluate_sound b fresh external _ ih he v w hw
    · exact ih v w hw

/-- No local checker is rerun on unaffected vertices; only the rank-layer entries change. -/
theorem System.replay_after_rank (a b : ∀ i, A i) (old : ∀ v, W v)
    (fresh : ∀ v, Option (W v)) (external : V → Bool) (rank : V → ℕ)
    {n : ℕ} {v : V} (hv : rank v < n) :
    S.replay a b old fresh external rank (n+1) v = S.replay a b old fresh external rank n v := by
  simp [replay,layer,Nat.ne_of_lt hv]

/-- If revised local evidence is available and passes, topological replay restores it.
This is conditional completeness of this procedure, not completeness of proof search. -/
theorem System.replay_complete (rank : V → ℕ) (ordered : G.Ranked rank)
    (a b : ∀ i, A i) (old : ∀ v, W v) (fresh : ∀ v, Option (W v)) (external : V → Bool)
    (he : ∀ v ∈ G.stale a b, external v = true)
    (hf : ∀ v ∈ G.stale a b, ∃ w, fresh v = some w ∧ S.check v (G.view b v) w = true)
    (n : ℕ) : ∀ v, rank v < n → (S.replay a b old fresh external rank n v).ready = true := by
  induction n with
  | zero => intro v hv; omega
  | succ n ih =>
    intro v hv
    by_cases hn : rank v < n
    · rw [S.replay_after_rank a b old fresh external rank hn]
      exact ih v hn
    · have hvn : rank v = n := by omega
      by_cases hstale : v ∈ G.stale a b
      · change (S.layer a b fresh external rank n (S.replay a b old fresh external rank n) v).ready = true
        simp only [layer,hvn,hstale,and_self,ite_true]
        apply (S.evaluate_ready_iff b fresh external _ v).mpr
        refine ⟨?_,he v hstale,hf v hstale⟩
        intro u hu
        apply ih u
        rw [← hvn]
        exact ordered v u hu
      · rw [S.replay_unaffected a b old fresh external rank (n+1) v hstale]
        rfl

/-- The finite completed replay supplies every revised claim when its actual inputs pass. -/
theorem System.restoration (complete : S.Complete) (rank : V → ℕ) (ordered : G.Ranked rank)
    (a b : ∀ i, A i) (old : ∀ v, W v) (fresh : ∀ v, Option (W v)) (external : V → Bool)
    (hold : ∀ v, S.Established a v (old v))
    (hclean : ∀ v, v ∉ G.stale a b → S.external b v)
    (he : ∀ v, external v = true → S.external b v)
    (havailable : ∀ v ∈ G.stale a b, external v = true)
    (hchecks : ∀ v ∈ G.stale a b, ∃ w, fresh v = some w ∧ S.check v (G.view b v) w = true) :
    ∀ v, ∃ w, (S.finish a b old fresh external rank v).witness? = some w ∧ S.Established b v w := by
  intro v
  have hr : rank v < finishAt rank := by
    have h := Finset.le_sup (f := rank) (Finset.mem_univ v)
    unfold finishAt
    omega
  have ready := S.replay_complete rank ordered a b old fresh external havailable hchecks (finishAt rank) v hr
  obtain ⟨w,hw⟩ := (Verdict.ready_iff _).mp ready
  refine ⟨w,hw,?_⟩
  exact S.replay_sound complete rank ordered a b old fresh external hold hclean he _ v w hw

/-- Partial replay certifies only the entries whose witnesses it actually returns. -/
theorem System.finish_sound (complete : S.Complete) (rank : V → ℕ) (ordered : G.Ranked rank)
    (a b : ∀ i, A i) (old : ∀ v, W v) (fresh : ∀ v, Option (W v)) (external : V → Bool)
    (hold : ∀ v, S.Established a v (old v))
    (hclean : ∀ v, v ∉ G.stale a b → S.external b v)
    (he : ∀ v, external v = true → S.external b v) :
    S.SoundState b (S.finish a b old fresh external rank) :=
  S.replay_sound complete rank ordered a b old fresh external hold hclean he _

end Komorebi.MachineTheory.Dependency
