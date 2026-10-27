import Mathlib.Data.Set.Lattice.Bounded
import Mathlib.Data.Finset.Basic

/-!
Generic interfaces for a lane-refined exclusion certificate.

There are no number-theoretic assumptions, external theorem axioms, or Beal
nonexistence claims here. In an application, `Candidate` must contain every
globally fixed choice, including the modular form and a prime above seven.
-/

namespace KomorebiBeal.Block47

variable {Lane Candidate Test State FineLane : Type*}

/-- Candidates satisfying every selected test in a single arithmetic lane. -/
def survivors (compatible : Lane → Candidate → Test → Prop)
    (tests : Set Test) (lane : Lane) : Set Candidate :=
  {candidate | ∀ test ∈ tests, compatible lane candidate test}

theorem survivors_mono_tests
    (compatible : Lane → Candidate → Test → Prop) (lane : Lane)
    {small large : Set Test} (h : small ⊆ large) :
    survivors compatible large lane ⊆ survivors compatible small lane := by
  intro candidate hc test ht
  exact hc test (h ht)

theorem survivors_union
    (compatible : Lane → Candidate → Test → Prop) (lane : Lane)
    (first second : Set Test) :
    survivors compatible (first ∪ second) lane =
      survivors compatible first lane ∩ survivors compatible second lane := by
  ext candidate
  constructor
  · intro h
    exact ⟨fun test ht => h test (Or.inl ht),
      fun test ht => h test (Or.inr ht)⟩
  · intro h test ht
    cases ht with
    | inl hfirst => exact h.1 test hfirst
    | inr hsecond => exact h.2 test hsecond

theorem survivors_refinement
    (fine : FineLane → Candidate → Test → Prop)
    (coarse : Lane → Candidate → Test → Prop)
    (parent : FineLane → Lane) (tests : Set Test)
    (transfer : ∀ lane candidate test,
      fine lane candidate test → coarse (parent lane) candidate test)
    (lane : FineLane) :
    survivors fine tests lane ⊆ survivors coarse tests (parent lane) := by
  intro candidate hc test ht
  exact transfer lane candidate test (hc test ht)

/-- A contradiction certificate may depend on the arithmetic lane, but its
candidate is held fixed throughout all selected tests in that lane. -/
theorem exclusion_from_empty_survivors
    (solution : State → Prop) (phase : State → Lane → Prop)
    (label : State → Candidate → Prop)
    (compatible : Lane → Candidate → Test → Prop)
    (tests : Lane → Set Test)
    (cover : ∀ state, solution state → ∃ lane, phase state lane)
    (attachment : ∀ state, solution state → ∃ candidate, label state candidate)
    (sound : ∀ state, solution state → ∀ lane, phase state lane →
      ∀ candidate, label state candidate →
        candidate ∈ survivors compatible (tests lane) lane)
    (empty : ∀ lane, survivors compatible (tests lane) lane = ∅) :
    ∀ state, ¬solution state := by
  intro state hs
  obtain ⟨lane, hl⟩ := cover state hs
  obtain ⟨candidate, hc⟩ := attachment state hs
  have hmem := sound state hs lane hl candidate hc
  rw [empty lane] at hmem
  exact hmem

/-- Explicit finite exclusion witnesses supply the empty-survivor hypothesis. -/
theorem finite_certificate_empty
    (compatible : Lane → Candidate → Test → Prop)
    (tests : Lane → Finset Test)
    (reject : ∀ lane candidate,
      ∃ test ∈ tests lane, ¬compatible lane candidate test) :
    ∀ lane, survivors compatible (↑(tests lane)) lane = ∅ := by
  intro lane
  apply Set.eq_empty_iff_forall_notMem.mpr
  intro candidate hc
  obtain ⟨test, ht, hbad⟩ := reject lane candidate
  exact hbad (hc test ht)

/-- Refining a covering family remains exhaustive only with a proved lift. -/
theorem refinement_preserves_cover
    (solution : State → Prop) (phase : State → Lane → Prop)
    (finePhase : State → FineLane → Prop)
    (cover : ∀ state, solution state → ∃ lane, phase state lane)
    (lift : ∀ state, solution state → ∀ lane, phase state lane →
      ∃ fineLane, finePhase state fineLane) :
    ∀ state, solution state → ∃ fineLane, finePhase state fineLane := by
  intro state hs
  obtain ⟨lane, hl⟩ := cover state hs
  exact lift state hs lane hl

/-- Saturated tests cannot produce an exclusion certificate. This is a
statement about a fixed candidate satisfying all tests, not separate choices. -/
theorem fixed_witness_prevents_empty
    (compatible : Lane → Candidate → Test → Prop)
    (tests : Set Test) (lane : Lane) (candidate : Candidate)
    (witness : ∀ test ∈ tests, compatible lane candidate test) :
    survivors compatible tests lane ≠ ∅ := by
  intro empty
  have hmem : candidate ∈ survivors compatible tests lane := witness
  rw [empty] at hmem
  exact hmem

end KomorebiBeal.Block47
