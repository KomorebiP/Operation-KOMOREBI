import MachineTheory.PrefixSemantics
import MachineTheory.BinaryCertificate

/-!
# An explicit admission boundary for capacity-pruned search

The outer `none` rejects the scope certificate. A completed inner `none` means
finite-depth infeasibility ONLY after all scope, menu and row conditions pass.
The exhaustive finite guard is itself preparation, not an uncharged cheap test.
-/
namespace Komorebi.MachineTheory.OrderedCompiler
open HardInquiry BinaryDiagnosis
variable {X E C : Type} [Fintype X] [DecidableEq X]
  [Fintype E] [DecidableEq E] [Fintype C] [DecidableEq C]

def guard (M : Model X E Bool C Unit) (es : List E) (cs : List C) (xs : List X) : Bool :=
  checkScope M && decide (xs.Nodup ∧ (∀ e,e∈es) ∧ ∀ c,c∈cs)

theorem guard_iff (M : Model X E Bool C Unit) (es : List E) (cs : List C) (xs : List X) :
    guard M es cs xs=true ↔ Scope M ∧ xs.Nodup ∧ (∀ e,e∈es) ∧ ∀ c,c∈cs := by
  simp only [guard,Bool.and_eq_true_iff,checkScope_iff,decide_eq_true_eq]

def checkedSearch (M : Model X E Bool C Unit) (es : List E) (cs : List C)
    (h : ℕ) (xs : List X) : Option (Run (Tree E Bool C h)) :=
  if guard M es cs xs then some (search streamScanner M es cs h xs) else none

theorem admitted_contract (M : Model X E Bool C Unit) (es : List E) (cs : List C)
    (h : ℕ) (xs : List X) (r : Run (Tree E Bool C h))
    (hr : checkedSearch M es cs h xs=some r) :
    Scope M ∧ xs.Nodup ∧ (∀ e,e∈es) ∧ (∀ c,c∈cs) ∧ r=search streamScanner M es cs h xs := by
  unfold checkedSearch at hr
  split at hr
  · have hg := (guard_iff M es cs xs).mp ‹guard M es cs xs=true›
    exact ⟨hg.1,hg.2.1,hg.2.2.1,hg.2.2.2,(Option.some.inj hr).symm⟩
  · cases hr

/-- This is about a completed admitted search, not a timeout or a rejected model. -/
theorem admitted_search_sound_complete (M : Model X E Bool C Unit) (es : List E) (cs : List C)
    (h : ℕ) (xs : List X) (r : Run (Tree E Bool C h))
    (hr : checkedSearch M es cs h xs=some r) :
    (∀ t,r.answer=some t → M.Valid h xs.toFinset t) ∧
    (r.answer=none ↔ ¬ ∃ t : Tree E Bool C h,M.Valid h xs.toFinset t) := by
  obtain ⟨hs,hn,he,hc,hh⟩ := admitted_contract M es cs h xs r hr
  rw [hh]
  exact streaming_sound_complete M hs es cs he hc h xs hn

theorem admitted_search_preserves_reference (M : Model X E Bool C Unit) (es : List E) (cs : List C)
    (h : ℕ) (xs : List X) (r : Run (Tree E Bool C h))
    (hr : checkedSearch M es cs h xs=some r) :
    r.answer=(search fullScanner M es cs h xs).answer ∧
    r.reads≤(search fullScanner M es cs h xs).reads := by
  obtain ⟨_,_,_,_,hh⟩ := admitted_contract M es cs h xs r hr
  rw [hh]
  exact streaming_preserves_search M es cs h xs


/-- The new ordered compiler and the unchanged Pareto synthesizer agree on finite feasibility. -/
theorem admitted_failure_iff_empty_frontier (M : Model X E Bool C Unit) (es : List E) (cs : List C)
    (h : ℕ) (xs : List X) (r : Run (Tree E Bool C h))
    (hr : checkedSearch M es cs h xs=some r) :
    r.answer=none ↔ M.compute h xs.toFinset=∅ := by
  rw [M.compute_eq_solve]
  exact (admitted_search_sound_complete M es cs h xs r hr).2.trans
    (M.no_tree_iff_empty h xs.toFinset)

end Komorebi.MachineTheory.OrderedCompiler

