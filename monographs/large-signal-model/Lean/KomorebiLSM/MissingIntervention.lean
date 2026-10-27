import KomorebiLSM.BehaviorProbability
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Algebra.BigOperators.Fin

/-! P31: actual one-state stochastic instruments agree on every passive record
and disagree under an unobserved intervention. False is action a, true is b.
The model tag specifies the deterministic observation under action b. -/
set_option autoImplicit false
namespace Komorebi.LSM.MissingIntervention
open scoped BigOperators
open FiniteInstruments

/-- One hidden state, two actions and two observations. -/
noncomputable def model (tag : Bool) : Instrument (Fin 1) Bool Bool where
  matrix a o _ _ := if a then (if o = tag then 1 else 0) else 1/2
  nonneg := by
    intro a o j i
    cases a <;> cases o <;> cases tag <;> norm_num
  mass_one := by
    intro a i
    cases a <;> cases tag <;> norm_num [Fin.sum_univ_succ, Fintype.sum_bool]

/-- The unique hidden state has probability one. -/
def initial : Fin 1 → ℝ := fun _ => 1

theorem initial_valid : FiniteBayes.IsPrior initial := by
  constructor
  · intro i; norm_num [initial]
  · norm_num [initial, Fin.sum_univ_succ]

/-- Chronological word probabilities of the actual instruments. -/
noncomputable def process (tag : Bool) (w : List (Bool × Bool)) : ℝ :=
  mass (wordAction (model tag).branch w initial)

theorem process_causal (tag : Bool) : Behavior.CausalLaw (process tag) :=
  Behavior.instrument_causal (model tag) initial initial_valid

theorem process_bounds (tag : Bool) (w : List (Bool × Bool)) :
    0 ≤ process tag w ∧ process tag w ≤ 1 :=
  (process_causal tag).word_bounds w

/-- Each a-branch multiplies every unnormalized state by one half. -/
theorem branch_a (tag o : Bool) (p : Fin 1 → ℝ) :
    (model tag).branch (false, o) p = (1/2 : ℝ) • p := by
  funext j
  fin_cases j
  simp [Instrument.branch_apply, model]

/-- All lengths and all observation records, not a finite test fixture. -/
theorem passive_word_state (tag : Bool) (os : List Bool) (p : Fin 1 → ℝ) :
    wordAction (model tag).branch (os.map (fun o => (false, o))) p =
      ((1/2 : ℝ) ^ os.length) • p := by
  induction os with
  | nil => simp
  | cons o os ih =>
    simp only [List.map_cons, List.length_cons, wordAction_cons, LinearMap.comp_apply]
    rw [branch_a, map_smul, ih]
    simp [smul_smul, pow_succ, mul_comm]

/-- Every length-k a-only record has probability 2^(-k). -/
theorem passive_word_probability (tag : Bool) (os : List Bool) :
    process tag (os.map (fun o => (false, o))) = (1/2 : ℝ) ^ os.length := by
  unfold process
  rw [passive_word_state, map_smul, mass_prior initial initial_valid]
  simp

theorem passive_agreement (os : List Bool) :
    process false (os.map (fun o => (false, o))) =
      process true (os.map (fun o => (false, o))) := by
  rw [passive_word_probability, passive_word_probability]

/-- One unseen intervention distinguishes the two models with certainty. -/
theorem intervention_disagreement :
    process false [(true, false)] = 1 ∧ process true [(true, false)] = 0 := by
  norm_num [process, wordAction, Instrument.branch_apply, model, initial,
    mass_apply, Fin.sum_univ_succ]

theorem full_laws_distinct : process false ≠ process true := by
  intro h
  have hw := congrFun h [(true, false)]
  rw [intervention_disagreement.1, intervention_disagreement.2] at hw
  norm_num at hw

/-- P31's existential form, with validity supplied by the Instrument type. -/
theorem missing_intervention_nonidentifiability :
    ∃ T₀ T₁ : Instrument (Fin 1) Bool Bool,
      (∀ os : List Bool,
        mass (wordAction T₀.branch (os.map (fun o => (false, o))) initial) =
        mass (wordAction T₁.branch (os.map (fun o => (false, o))) initial)) ∧
      mass (wordAction T₀.branch [(true, false)] initial) = 1 ∧
      mass (wordAction T₁.branch [(true, false)] initial) = 0 := by
  exact ⟨model false, model true, passive_agreement,
    intervention_disagreement.1, intervention_disagreement.2⟩

/-- Even the complete exact passive probability law cannot determine the
unrestricted controlled law for both models. This is not a sample-size bound. -/
theorem no_passive_identification
    (learn : (List Bool → ℝ) → List (Bool × Bool) → ℝ) :
    ¬ ((learn (fun os : List Bool => process false (os.map (fun o => (false, o)))) = process false) ∧
       (learn (fun os : List Bool => process true (os.map (fun o => (false, o)))) = process true)) := by
  rintro ⟨h₀, h₁⟩
  have hp : (fun os : List Bool => process false (os.map (fun o => (false, o)))) =
      (fun os : List Bool => process true (os.map (fun o => (false, o)))) :=
    funext passive_agreement
  exact full_laws_distinct (h₀.symm.trans ((congrArg learn hp).trans h₁))

end Komorebi.LSM.MissingIntervention
