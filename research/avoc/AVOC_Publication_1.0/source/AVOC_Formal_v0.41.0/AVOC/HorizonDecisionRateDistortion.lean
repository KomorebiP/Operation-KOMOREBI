import AVOC.QRateDistortionFinite

namespace Komorebi.AVOC

universe u v w

/-- Admissible actions of a finite stochastic control system as a finite type. -/
abbrev AdmissibleStochasticAction
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) :=
  {a : A // a ∈ sys.actions}

/-- Complete admissible Bellman Q-signature at a state and continuation horizon. -/
noncomputable def horizonDecisionSignature
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) (n : ℕ) :
    S → AdmissibleStochasticAction sys → ℚ :=
  fun s a => stochasticQValue sys n s a.1

/-- A compressed context reconstructs the full admissible Bellman decision
signature to tolerance `η`. -/
def HorizonDecisionSignatureApproximation
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    {Z : Type w}
    (sys : FiniteStochasticControlSystem S A) (n : ℕ)
    (φ : S → Z) (Qbar : Z → AdmissibleStochasticAction sys → ℚ)
    (η : ℚ) : Prop :=
  QSignatureApproximation φ (horizonDecisionSignature sys n) Qbar η

/-- Exact minimum finite context cardinality required to preserve all
admissible Bellman action values at horizon `n` to tolerance `η`. -/
noncomputable def exactHorizonDecisionCodeNumber
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) (n : ℕ)
    (η : ℚ) (hη : 0 ≤ η) : ℕ :=
  exactQCodeNumber (horizonDecisionSignature sys n) η hη

/-- Every finite context preserving all admissible Bellman Q-values needs at
least the exact horizon decision-code number of symbols. -/
theorem exactHorizonDecisionCodeNumber_le_finite_code_card
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    {Z : Type w} [Fintype Z] [DecidableEq Z]
    (sys : FiniteStochasticControlSystem S A) (n : ℕ)
    (φ : S → Z) (Qbar : Z → AdmissibleStochasticAction sys → ℚ)
    (η : ℚ) (hη : 0 ≤ η)
    (h : HorizonDecisionSignatureApproximation sys n φ Qbar η) :
    exactHorizonDecisionCodeNumber sys n η hη ≤ Fintype.card Z := by
  exact exactQCodeNumber_le_finite_code_card φ
    (horizonDecisionSignature sys n) Qbar η hη h

/-- The exact horizon decision-code minimum is attained by a finite context. -/
theorem exactHorizonDecisionCodeNumber_attained
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) (n : ℕ)
    (η : ℚ) (hη : 0 ≤ η) :
    ∃ C : Finset (AdmissibleStochasticAction sys → ℚ),
      C.card = exactHorizonDecisionCodeNumber sys n η hη ∧
      ∃ φ : S → {c // c ∈ C},
        HorizonDecisionSignatureApproximation sys n φ
          (fun z : {c // c ∈ C} =>
            (z : AdmissibleStochasticAction sys → ℚ)) η := by
  exact exactQCodeNumber_attained_by_context
    (horizonDecisionSignature sys n) η hη

/-- At zero distortion, exact context cardinality equals the number of distinct
admissible Bellman Q-signatures. -/
theorem exactHorizonDecisionCodeNumber_zero_eq_distinct_signature_card
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    (sys : FiniteStochasticControlSystem S A) (n : ℕ) :
    exactHorizonDecisionCodeNumber sys n 0 (by norm_num) =
      (Finset.univ.image (horizonDecisionSignature sys n)).card := by
  exact exactQCodeNumber_zero_eq_distinct_signature_card
    (horizonDecisionSignature sys n)

/-- Optimality among decoded admissible Bellman actions. -/
def DecodedBellmanOptimalAt
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    {Z : Type w}
    (sys : FiniteStochasticControlSystem S A)
    (Qbar : Z → AdmissibleStochasticAction sys → ℚ)
    (z : Z) (a : AdmissibleStochasticAction sys) : Prop :=
  ∀ b, Qbar z b ≤ Qbar z a

/-- Choosing an action optimal in an `η`-accurate decoded Bellman signature
incurs at most `2η` raw Bellman regret against every admissible action. -/
theorem decoded_bellman_optimal_raw_regret_bound
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    {Z : Type w}
    (sys : FiniteStochasticControlSystem S A) (n : ℕ)
    (φ : S → Z) (Qbar : Z → AdmissibleStochasticAction sys → ℚ)
    (η : ℚ)
    (happrox : HorizonDecisionSignatureApproximation sys n φ Qbar η)
    {s : S} {aStar : AdmissibleStochasticAction sys}
    (hopt : DecodedBellmanOptimalAt sys Qbar (φ s) aStar) :
    ∀ a : AdmissibleStochasticAction sys,
      stochasticQValue sys n s a.1 - stochasticQValue sys n s aStar.1 ≤ 2 * η := by
  exact abstract_q_optimal_raw_regret_bound φ
    (horizonDecisionSignature sys n) Qbar η happrox hopt

/-- A raw admissible action with Bellman margin above `2η` remains strictly
optimal in every `η`-accurate decoded signature. -/
theorem bellman_margin_preserves_decoded_unique_optimum
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    {Z : Type w}
    (sys : FiniteStochasticControlSystem S A) (n : ℕ)
    (φ : S → Z) (Qbar : Z → AdmissibleStochasticAction sys → ℚ)
    (η : ℚ)
    (happrox : HorizonDecisionSignatureApproximation sys n φ Qbar η)
    {s : S} {aStar : AdmissibleStochasticAction sys}
    (hmargin : ∀ a : AdmissibleStochasticAction sys, a ≠ aStar →
      2 * η < stochasticQValue sys n s aStar.1 - stochasticQValue sys n s a.1) :
    ∀ a : AdmissibleStochasticAction sys, a ≠ aStar →
      Qbar (φ s) a < Qbar (φ s) aStar := by
  exact q_margin_preserves_unique_optimum φ
    (horizonDecisionSignature sys n) Qbar η happrox hmargin

/-- At zero signature distortion, decoded and raw optimal-action sets coincide
on the admissible stochastic action type. -/
theorem exact_horizon_decision_signature_optimality_iff
    {S : Type u} {A : Type v} [Fintype S] [DecidableEq A]
    {Z : Type w}
    (sys : FiniteStochasticControlSystem S A) (n : ℕ)
    (φ : S → Z) (Qbar : Z → AdmissibleStochasticAction sys → ℚ)
    (happrox : HorizonDecisionSignatureApproximation sys n φ Qbar 0)
    (s : S) (a : AdmissibleStochasticAction sys) :
    DecodedBellmanOptimalAt sys Qbar (φ s) a ↔
      (∀ b : AdmissibleStochasticAction sys,
        stochasticQValue sys n s b.1 ≤ stochasticQValue sys n s a.1) := by
  exact exact_q_signature_optimality_iff φ
    (horizonDecisionSignature sys n) Qbar happrox s a

end Komorebi.AVOC
