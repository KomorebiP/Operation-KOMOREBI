import MachineTheory.Variation

/-! # Exact finite boundary examples for adaptive-lineage error control

These examples use the inherited finite real-valued distribution interface.
They illustrate the hypotheses and limits of Core 7.4. They are not a proof
of its countably infinite probability-space theorem. Every probability is an
exact sum over a declared finite world space, not an empirical estimate.
-/
namespace Komorebi.MachineTheory.LineageExamples
open Instrument Variation Finset
open scoped BigOperators
noncomputable section

/-- Probability of a finite event under the supplied finite distribution. -/
def prob {Ω : Type*} [Fintype Ω] [DecidableEq Ω]
    (p : Ω → ℝ) (E : Finset Ω) : ℝ := mass (Variation.restrict E p)

theorem prob_mono {Ω : Type*} [Fintype Ω] [DecidableEq Ω]
    (p : Ω → ℝ) (hp : ∀ w, 0 ≤ p w) {E F : Finset Ω} (h : E ⊆ F) :
    prob p E ≤ prob p F := by
  apply Finset.sum_le_sum
  intro w _
  by_cases he : w ∈ E
  · simp only [Variation.restrict, he, h he, ↓reduceIte, le_refl]
  · by_cases hf : w ∈ F
    · simpa only [Variation.restrict, he, hf, ↓reduceIte] using hp w
    · simp only [Variation.restrict, he, hf, ↓reduceIte, le_refl]

def fair (_w : Bool) : ℝ := 1/2

theorem fair_dist : IsDist fair := by
  constructor
  · intro w; norm_num [fair]
  · norm_num [mass, fair, Fintype.sum_bool]

/-- Both candidates make false claims; each accepts on its own labeled world. -/
def claimTrue (_candidate : Bool) : Prop := False

def accepts (candidate world : Bool) : Prop := world = candidate

def fixedBad (candidate : Bool) : Finset Bool := by
  classical
  exact univ.filter fun world => accepts candidate world ∧ ¬ claimTrue candidate

/-- Selection observes the world, then chooses the candidate that accepts there. -/
def selectedCandidate (world : Bool) : Bool := world

def selectedBad : Finset Bool := by
  classical
  exact univ.filter fun world =>
    accepts (selectedCandidate world) world ∧ ¬ claimTrue (selectedCandidate world)

theorem fixed_candidate_half (candidate : Bool) : prob fair (fixedBad candidate) = 1/2 := by
  cases candidate <;>
    norm_num [prob, mass, Variation.restrict, fair, fixedBad, accepts, claimTrue, Fintype.sum_bool]

theorem selected_candidate_certain : prob fair selectedBad = 1 := by
  norm_num [prob, mass, Variation.restrict, fair, selectedBad, selectedCandidate,
    accepts, claimTrue, Fintype.sum_bool]

/-- Pointwise nominal validity before selection does not imply validity afterward. -/
theorem selection_invalidates_nominal_bound :
    (∀ candidate, prob fair (fixedBad candidate) ≤ 1/2) ∧
    ¬ prob fair selectedBad ≤ 1/2 := by
  constructor
  · intro candidate; rw [fixed_candidate_half]
  · rw [selected_candidate_certain]; norm_num

/-- Conditional on the revealed world, its selected false acceptance has probability one. -/
theorem revealed_history_error (world : Bool) :
    prob fair (selectedBad ∩ {world}) / prob fair {world} = 1 := by
  cases world <;>
    norm_num [prob, mass, Variation.restrict, fair, selectedBad, selectedCandidate,
      accepts, claimTrue, Fintype.sum_bool]

/-- Disjoint false-acceptance events attain the union bound exactly. -/
theorem disjoint_union_sharp :
    Disjoint (fixedBad false) (fixedBad true) ∧
    prob fair (fixedBad false ∪ fixedBad true) =
      prob fair (fixedBad false) + prob fair (fixedBad true) ∧
    prob fair (fixedBad false ∪ fixedBad true) = 1 := by
  constructor
  · apply Finset.disjoint_left.mpr
    intro world hf ht
    simp only [fixedBad, mem_filter, mem_univ, true_and, accepts, claimTrue,
      not_false_eq_true, and_true] at hf ht
    exact Bool.false_ne_true (hf.symm.trans ht)
  · norm_num [prob, mass, Variation.restrict, fair, fixedBad, accepts,
      claimTrue, Fintype.sum_bool]

/-- Repeating one event is perfectly dependent: the union bound is strict,
and the product formula for independence is false. This concerns the union
step alone, not conditional validity after observing an earlier outcome. -/
theorem dependent_repetition :
    prob fair (fixedBad true ∪ fixedBad true) = 1/2 ∧
    prob fair (fixedBad true ∪ fixedBad true) <
      prob fair (fixedBad true) + prob fair (fixedBad true) ∧
    prob fair (fixedBad true ∩ fixedBad true) ≠
      prob fair (fixedBad true) * prob fair (fixedBad true) := by
  simp only [union_self, inter_self, fixed_candidate_half]
  norm_num

/-- A gate can depend arbitrarily on the same world. Retained bad events
are still contained in the ungated lineage's bad events. -/
theorem gated_union_containment {Ω : Type*} [DecidableEq Ω]
    (stages : Finset ℕ) (bad gate : ℕ → Finset Ω) :
    stages.biUnion (fun i => bad i ∩ gate i) ⊆ stages.biUnion bad := by
  intro w hw
  obtain ⟨i, hi, hwi⟩ := mem_biUnion.mp hw
  exact mem_biUnion.mpr ⟨i, hi, (mem_inter.mp hwi).1⟩

theorem gated_union_probability {Ω : Type*} [Fintype Ω] [DecidableEq Ω]
    (p : Ω → ℝ) (hp : IsDist p) (stages : Finset ℕ) (bad gate : ℕ → Finset Ω) :
    prob p (stages.biUnion (fun i => bad i ∩ gate i)) ≤
      prob p (stages.biUnion bad) :=
  prob_mono p hp.1 (gated_union_containment stages bad gate)

/-- Gating preserves an unconditional bound; it does not bound error
conditional on the decision to retain. The retained mass here is positive. -/
theorem retention_can_condition_to_certain_error :
    0 < prob fair (fixedBad true) ∧
    prob fair (fixedBad true ∩ fixedBad true) ≤ 1/2 ∧
    prob fair (fixedBad true ∩ fixedBad true) / prob fair (fixedBad true) = 1 := by
  simp only [inter_self, fixed_candidate_half]
  norm_num

/-- Zero probability is weaker than event emptiness under a law with zero-mass worlds. -/
theorem null_event_is_nonempty :
    IsDist (basis false : Bool → ℝ) ∧
    ({true} : Finset Bool).Nonempty ∧ prob (basis false) {true} = 0 := by
  refine ⟨basis_dist false, by simp, ?_⟩
  norm_num [prob, mass, Variation.restrict, basis, Fintype.sum_bool]

/-- An arbitrary finite prefix can be error-free while a later stage is certain to fail. -/
def lateBad (cutoff stage : ℕ) : Finset Bool := if stage = cutoff then univ else ∅

theorem late_failure (cutoff : ℕ) :
    (∀ stage < cutoff, prob fair (lateBad cutoff stage) = 0) ∧
    prob fair (lateBad cutoff cutoff) = 1 := by
  constructor
  · intro stage hstage
    have hne : stage ≠ cutoff := Nat.ne_of_lt hstage
    simp [prob, mass, Variation.restrict, lateBad, hne]
  · norm_num [prob, mass, Variation.restrict, lateBad, fair, Fintype.sum_bool]

/-- A sum of declared numbers alone has no connection to the event probabilities. -/
theorem numeric_budget_without_validity :
    (∑ _stage : Bool, (0 : ℝ)) ≤ 1/10 ∧ ¬ prob fair selectedBad ≤ 1/10 := by
  rw [selected_candidate_certain]
  norm_num

end
end Komorebi.MachineTheory.LineageExamples
