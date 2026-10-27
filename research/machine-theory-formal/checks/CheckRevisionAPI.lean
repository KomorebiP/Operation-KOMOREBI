import MachineTheory
open Komorebi.MachineTheory Dependency

variable {V I : Type*} [Fintype V] [DecidableEq V]
variable {A : I → Type*} [∀ i, DecidableEq (A i)] {W : V → Type*}

/-- The changed set is actual finite reachability, not an unverified supplied superset. -/
example (G : Graph V I) (a b : ∀ i, A i) (v : V) :
    v ∈ G.stale a b ↔ Reach G.parents (G.changedRoots a b) v := G.stale_iff a b v

/-- Source 7.1. The old witness and external-premise assumptions are not omitted. -/
example (G : Graph V I) (S : System G A W) (complete : S.Complete)
    (rank : V → ℕ) (ordered : G.Ranked rank) (a b : ∀ i, A i) (old : ∀ v, W v)
    (hold : ∀ v, S.Established a v (old v))
    (hex : ∀ v, v ∉ G.stale a b → S.external b v) :
    ∀ v, v ∉ G.stale a b → S.Established b v (old v) :=
  S.selective_reuse complete rank ordered a b old hold hex

/-- Every intermediate status that exports a witness has its revised semantics. -/
example (G : Graph V I) (S : System G A W) (complete : S.Complete)
    (rank : V → ℕ) (ordered : G.Ranked rank) (a b : ∀ i, A i)
    (old : ∀ v, W v) (fresh : ∀ v, Option (W v)) (ext : V → Bool)
    (hold : ∀ v, S.Established a v (old v))
    (hclean : ∀ v, v ∉ G.stale a b → S.external b v)
    (he : ∀ v, ext v = true → S.external b v) (n : ℕ) :
    ∀ v w, (S.replay a b old fresh ext rank n v).witness? = some w →
      S.check v (G.view b v) w = true ∧ S.external b v ∧ S.claim b v :=
  S.replay_sound complete rank ordered a b old fresh ext hold hclean he n

/-- Revised parent establishment and actual new checks suffice for completed restoration. -/
example (G : Graph V I) (S : System G A W) (complete : S.Complete)
    (rank : V → ℕ) (ordered : G.Ranked rank) (a b : ∀ i, A i)
    (old : ∀ v, W v) (fresh : ∀ v, Option (W v)) (ext : V → Bool)
    (hold : ∀ v, S.Established a v (old v))
    (hclean : ∀ v, v ∉ G.stale a b → S.external b v)
    (he : ∀ v, ext v = true → S.external b v)
    (hex : ∀ v ∈ G.stale a b, ext v = true)
    (hc : ∀ v ∈ G.stale a b, ∃ w, fresh v=some w ∧ S.check v (G.view b v) w=true) :
    ∀ v, ∃ w, (S.finish a b old fresh ext rank v).witness?=some w ∧ S.Established b v w :=
  S.restoration complete rank ordered a b old fresh ext hold hclean he hex hc

/-- Actual inherited controller semantics are an instance of the revision theorem. -/
example :
    (RevisionExamples.selectedModel (RevisionExamples.replaced 0)).Valid 3 Finset.univ
      (RevisionExamples.selectedTree (RevisionExamples.replaced 1)) ∧
    (RevisionExamples.selectedModel (RevisionExamples.replaced 0)).profile 3 Finset.univ
      (RevisionExamples.selectedTree (RevisionExamples.replaced 1)) = (fun _ => 1,1) :=
  RevisionExamples.replacement_actual_controller
